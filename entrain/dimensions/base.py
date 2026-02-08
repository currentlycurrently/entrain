"""
Abstract base class for dimension analyzers.

All Entrain Framework dimension analyzers implement this interface.

See ARCHITECTURE.md Section 5.1 for specification.
"""

from abc import ABC, abstractmethod
from typing import Literal

from entrain.models import Conversation, Corpus, DimensionReport, ENTRAIN_VERSION


class DimensionAnalyzer(ABC):
    """
    Abstract base for dimension analyzers.

    Each dimension (SR, PE, LC, AE, RCD, DF) has an analyzer that implements
    this interface. Analyzers compute dimension-specific indicators from
    conversations or corpora.
    """

    @property
    @abstractmethod
    def dimension_code(self) -> str:
        """
        Dimension code (e.g., 'SR', 'PE', 'LC', 'AE', 'RCD', 'DF').

        Returns:
            Two or three letter dimension code
        """
        pass

    @property
    @abstractmethod
    def dimension_name(self) -> str:
        """
        Full dimension name.

        Returns:
            Human-readable dimension name
        """
        pass

    @property
    @abstractmethod
    def required_modality(self) -> Literal["text", "audio", "both"]:
        """
        What input modality this analyzer requires.

        Returns:
            Required modality ("text", "audio", or "both")
        """
        pass

    @abstractmethod
    def analyze_conversation(self, conversation: Conversation) -> DimensionReport:
        """
        Analyze a single conversation.

        Args:
            conversation: Conversation to analyze

        Returns:
            DimensionReport with computed indicators

        Raises:
            ValueError: If conversation lacks required modality
        """
        pass

    def analyze_corpus(self, corpus: Corpus) -> DimensionReport:
        """
        Analyze a corpus (default: aggregate conversation-level results).

        This default implementation computes per-conversation reports and
        aggregates them. Individual analyzers can override this for more
        sophisticated longitudinal analysis.

        Args:
            corpus: Corpus to analyze

        Returns:
            Aggregated DimensionReport
        """
        if not corpus.conversations:
            raise ValueError("Cannot analyze empty corpus")

        # Analyze each conversation
        reports = []
        for conv in corpus.conversations:
            try:
                report = self.analyze_conversation(conv)
                reports.append(report)
            except Exception as e:
                print(f"Warning: Failed to analyze conversation {conv.id}: {e}")
                continue

        if not reports:
            raise ValueError("No conversations could be analyzed")

        # Aggregate indicators across conversations
        return self._aggregate(reports)

    def _aggregate(self, reports: list[DimensionReport]) -> DimensionReport:
        """
        Aggregate multiple conversation-level reports into corpus report.

        Default aggregation: compute mean for each indicator.

        Args:
            reports: List of conversation-level reports

        Returns:
            Aggregated report
        """
        if not reports:
            raise ValueError("Cannot aggregate empty report list")

        # Get all indicator names from first report
        indicator_names = set(reports[0].indicators.keys())

        # Aggregate each indicator
        from entrain.models import IndicatorResult

        aggregated_indicators = {}

        for name in indicator_names:
            # Collect values for this indicator across all reports
            values = []
            for report in reports:
                if name in report.indicators:
                    values.append(report.indicators[name].value)

            if values:
                mean_value = sum(values) / len(values)

                # Use first report's indicator as template
                template = reports[0].indicators[name]

                aggregated_indicators[name] = IndicatorResult(
                    name=name,
                    value=mean_value,
                    baseline=template.baseline,
                    unit=template.unit,
                    confidence=template.confidence,
                    interpretation=f"Mean across {len(reports)} conversations: {mean_value:.3f}"
                )

        # Create aggregated report
        return DimensionReport(
            dimension=self.dimension_code,
            version=ENTRAIN_VERSION,
            indicators=aggregated_indicators,
            summary=f"Aggregated {self.dimension_name} analysis across {len(reports)} conversations",
            methodology_notes=f"Computed per-conversation and aggregated (mean). Based on {self.dimension_code} analyzer v{ENTRAIN_VERSION}",
            citations=reports[0].citations if reports else []
        )

    def _validate_conversation(self, conversation: Conversation) -> None:
        """
        Validate that conversation has required modality.

        Args:
            conversation: Conversation to validate

        Raises:
            ValueError: If required modality is missing
        """
        if self.required_modality == "text":
            if not any(e.text_content for e in conversation.events):
                raise ValueError(
                    f"{self.dimension_code} analyzer requires text content, "
                    "but conversation has no text"
                )

        elif self.required_modality == "audio":
            if not any(e.audio_features for e in conversation.events):
                raise ValueError(
                    f"{self.dimension_code} analyzer requires audio features, "
                    "but conversation has no audio"
                )

        elif self.required_modality == "both":
            has_text = any(e.text_content for e in conversation.events)
            has_audio = any(e.audio_features for e in conversation.events)

            if not (has_text and has_audio):
                raise ValueError(
                    f"{self.dimension_code} analyzer requires both text and audio, "
                    "but conversation is missing one or both"
                )
