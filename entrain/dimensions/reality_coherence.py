"""
Reality Coherence Disruption (RCD) dimension analyzer.

Measures the degree to which sustained AI interaction distorts a user's
epistemic relationship with reality — their ability to accurately assess
what is true, what is simulation, and what constitutes genuine understanding
versus performed understanding.

Based on the Ontological Dissonance Hypothesis (Lipińska & Krzanowski, 2025).

See ARCHITECTURE.md Section 5.5 and FRAMEWORK.md Section 2.5 for specification.

References:
    - Lipińska, V. & Krzanowski, R. (2025). "The Ontological Dissonance
      Hypothesis: Broken Continuity of Presence, Folie à Deux Technologique,
      and the Delusional Potential of Human-AI Interaction." arXiv:2512.11818.
    - Bengio & Elmoznino (2025). "Illusions of AI Consciousness." Science.
    - Au Yeung et al. (2025). Psychosis-bench: safety benchmark for LLM-induced
      psychological destabilization.
"""

import re
from entrain.dimensions.base import DimensionAnalyzer
from entrain.features.text import TextFeatureExtractor
from entrain.features.temporal import TemporalFeatureExtractor
from entrain.models import Conversation, Corpus, DimensionReport, IndicatorResult, ENTRAIN_VERSION


class RCDAnalyzer(DimensionAnalyzer):
    """
    Reality Coherence Disruption (RCD) dimension analyzer.

    Computes three primary indicators:
    1. Attribution Language Frequency - attributing human qualities to AI
    2. Boundary Confusion Indicators - conflating AI/human capabilities
    3. Relational Framing - treating interaction as relationship
    """

    def __init__(self):
        self.text_extractor = TextFeatureExtractor()
        self.temporal_extractor = TemporalFeatureExtractor()

    @property
    def dimension_code(self) -> str:
        return "RCD"

    @property
    def dimension_name(self) -> str:
        return "Reality Coherence Disruption"

    @property
    def required_modality(self) -> str:
        return "text"

    def analyze_conversation(self, conversation: Conversation) -> DimensionReport:
        """
        Analyze a conversation for reality coherence disruption.

        Args:
            conversation: Conversation to analyze

        Returns:
            DimensionReport with RCD indicators
        """
        self._validate_conversation(conversation)

        user_events = conversation.user_events

        if not user_events:
            raise ValueError("Conversation has no user events to analyze")

        # Compute indicators
        attribution_freq = self._compute_attribution_language_frequency(user_events)
        boundary_confusion = self._compute_boundary_confusion_indicators(user_events)
        relational_framing = self._compute_relational_framing(user_events)

        # Create indicator results
        indicators = {
            "attribution_language_frequency": IndicatorResult(
                name="attribution_language_frequency",
                value=attribution_freq["rate"],
                baseline=None,  # No established baseline yet
                unit="matches_per_turn",
                confidence=0.90,
                interpretation=self._interpret_attribution(attribution_freq)
            ),
            "boundary_confusion_indicators": IndicatorResult(
                name="boundary_confusion_indicators",
                value=boundary_confusion["rate"],
                baseline=None,
                unit="proportion",
                confidence=0.70,
                interpretation=self._interpret_boundary_confusion(boundary_confusion)
            ),
            "relational_framing": IndicatorResult(
                name="relational_framing",
                value=relational_framing["rate"],
                baseline=None,
                unit="proportion",
                confidence=0.85,
                interpretation=self._interpret_relational_framing(relational_framing)
            )
        }

        # Generate summary
        summary = self._generate_summary(indicators)

        return DimensionReport(
            dimension=self.dimension_code,
            version=ENTRAIN_VERSION,
            indicators=indicators,
            summary=summary,
            methodology_notes=(
                "Computed using pattern matching for attribution language and "
                "relational framing. Attribution language detects phrases that "
                "attribute consciousness, understanding, memory, or emotions to AI. "
                "Boundary confusion detects statements conflating AI capabilities "
                "with human capabilities. Relational framing detects language "
                "treating the interaction as a relationship rather than tool use."
            ),
            citations=[
                "Lipińska & Krzanowski (2025). The Ontological Dissonance Hypothesis. arXiv:2512.11818",
                "Bengio & Elmoznino (2025). Illusions of AI Consciousness. Science",
                "Au Yeung et al. (2025). Psychosis-bench"
            ]
        )

    def analyze_corpus(self, corpus: Corpus) -> DimensionReport:
        """
        Analyze corpus for reality coherence disruption with trajectory.

        Args:
            corpus: Corpus to analyze

        Returns:
            DimensionReport with corpus-level RCD indicators
        """
        if not corpus.conversations:
            raise ValueError("Cannot analyze empty corpus")

        # Track trends over time
        attribution_rates = []
        boundary_rates = []
        relational_rates = []
        timestamps = []

        for conv in corpus.conversations:
            user_events = conv.user_events
            if not user_events:
                continue

            attribution = self._compute_attribution_language_frequency(user_events)
            boundary = self._compute_boundary_confusion_indicators(user_events)
            relational = self._compute_relational_framing(user_events)

            attribution_rates.append(attribution["rate"])
            boundary_rates.append(boundary["rate"])
            relational_rates.append(relational["rate"])
            timestamps.append(conv.events[0].timestamp)

        # Compute trajectories
        attribution_trajectory = self.temporal_extractor.indicator_trajectory(
            attribution_rates, timestamps
        )
        relational_trajectory = self.temporal_extractor.indicator_trajectory(
            relational_rates, timestamps
        )

        indicators = {
            "attribution_language_frequency": IndicatorResult(
                name="attribution_language_frequency",
                value=attribution_trajectory.slope if attribution_trajectory.slope else 0.0,
                baseline=0.0,  # Neutral: no change
                unit="slope_per_conversation",
                confidence=0.85,
                interpretation=f"Trend: {attribution_trajectory.trend}, final rate: {attribution_rates[-1]:.2f} per turn"
            ),
            "boundary_confusion_indicators": IndicatorResult(
                name="boundary_confusion_indicators",
                value=boundary_rates[-1] if boundary_rates else 0.0,
                baseline=None,
                unit="proportion",
                confidence=0.70,
                interpretation=f"Final rate: {boundary_rates[-1]:.1%} of messages show boundary confusion"
            ),
            "relational_framing": IndicatorResult(
                name="relational_framing",
                value=relational_trajectory.slope if relational_trajectory.slope else 0.0,
                baseline=0.0,
                unit="slope_per_conversation",
                confidence=0.85,
                interpretation=f"Trend: {relational_trajectory.trend}, final rate: {relational_rates[-1]:.1%}"
            )
        }

        summary = self._generate_summary(indicators)

        return DimensionReport(
            dimension=self.dimension_code,
            version=ENTRAIN_VERSION,
            indicators=indicators,
            summary=summary,
            methodology_notes="Corpus-level analysis with trajectory computation across conversations.",
            citations=[
                "Lipińska & Krzanowski (2025). The Ontological Dissonance Hypothesis",
                "Bengio & Elmoznino (2025). Illusions of AI Consciousness"
            ]
        )

    def _compute_attribution_language_frequency(self, user_events: list) -> dict:
        """
        Compute frequency of attribution language.

        Detects phrases like "you understand", "you care", "you remember" that
        attribute human-like consciousness or emotions to AI.

        Args:
            user_events: User interaction events

        Returns:
            Dict with rate and examples
        """
        total_matches = 0
        examples = []

        for event in user_events:
            if not event.text_content:
                continue

            matches = self.text_extractor.extract_attribution_language(event.text_content)
            total_matches += len(matches)

            # Collect examples (limit to 5)
            if len(examples) < 5:
                for match in matches[:5 - len(examples)]:
                    examples.append({
                        "pattern": match.pattern,
                        "context": match.context
                    })

        rate = total_matches / len(user_events) if user_events else 0.0

        return {
            "rate": rate,
            "total_matches": total_matches,
            "examples": examples
        }

    def _compute_boundary_confusion_indicators(self, user_events: list) -> dict:
        """
        Detect boundary confusion - conflating AI with human capabilities.

        Looks for:
        - Expressions of surprise when AI "doesn't remember"
        - Statements treating AI as having genuine emotions or relationships
        - Conflation of AI processing with human understanding

        Args:
            user_events: User interaction events

        Returns:
            Dict with rate and count
        """
        confusion_indicators = 0

        # Patterns indicating boundary confusion
        confusion_patterns = [
            r"why (don'?t|can'?t) you remember",
            r"i thought you (would )?remember",
            r"you (should|must) know",
            r"you'?re (supposed to|meant to) (understand|know|care)",
            r"i can'?t believe you (don'?t|didn'?t)",
            r"you (always|never)",
            r"you promise",
            r"you hurt my feelings",
            r"don'?t you care about",
            r"our (friendship|relationship|bond)",
        ]

        for event in user_events:
            if not event.text_content:
                continue

            text_lower = event.text_content.lower()

            has_confusion = any(
                re.search(pattern, text_lower)
                for pattern in confusion_patterns
            )

            if has_confusion:
                confusion_indicators += 1

        rate = confusion_indicators / len(user_events) if user_events else 0.0

        return {
            "rate": rate,
            "count": confusion_indicators
        }

    def _compute_relational_framing(self, user_events: list) -> dict:
        """
        Detect relational framing - treating interaction as relationship.

        Looks for:
        - "We" language
        - "Our conversations/relationship"
        - "Between us"
        - Personal relationship terminology

        Args:
            user_events: User interaction events

        Returns:
            Dict with rate and examples
        """
        relational_messages = 0
        examples = []

        relational_patterns = [
            r"\bwe\b",
            r"\bus\b",
            r"\bour\b",
            r"between (you and me|us)",
            r"our (conversation|relationship|friendship|bond|connection)",
            r"we (always|often|sometimes|never)",
            r"when we (talk|chat|discuss)",
            r"you and (i|me)",
            r"together",
        ]

        for event in user_events:
            if not event.text_content:
                continue

            text_lower = event.text_content.lower()

            # Check for relational language
            found_relational = False
            for pattern in relational_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    found_relational = True

                    # Collect example
                    if len(examples) < 5:
                        # Extract context around match
                        start = max(0, match.start() - 30)
                        end = min(len(event.text_content), match.end() + 30)
                        context = event.text_content[start:end]

                        examples.append({
                            "pattern": match.group(),
                            "context": context
                        })

                    break

            if found_relational:
                relational_messages += 1

        rate = relational_messages / len(user_events) if user_events else 0.0

        return {
            "rate": rate,
            "count": relational_messages,
            "examples": examples
        }

    # Interpretation methods

    def _interpret_attribution(self, result: dict) -> str:
        """Generate interpretation for attribution language."""
        rate = result["rate"]

        if rate > 1.0:
            return f"High attribution rate: {rate:.2f} instances per turn, suggesting user may be attributing consciousness to AI"
        elif rate > 0.5:
            return f"Moderate attribution: {rate:.2f} instances per turn of language suggesting AI has understanding/emotions"
        elif rate > 0.1:
            return f"Low attribution: {rate:.2f} instances per turn (may be casual language use)"
        else:
            return f"Minimal attribution: {rate:.2f} instances per turn"

    def _interpret_boundary_confusion(self, result: dict) -> str:
        """Generate interpretation for boundary confusion."""
        rate = result["rate"]
        count = result["count"]

        if count == 0:
            return "No boundary confusion detected"

        if rate > 0.20:
            return f"Significant boundary confusion: {rate:.1%} of messages show conflation of AI/human capabilities"
        elif rate > 0.10:
            return f"Moderate boundary confusion: {rate:.1%} of messages"
        else:
            return f"Mild boundary confusion: {rate:.1%} of messages ({count} total)"

    def _interpret_relational_framing(self, result: dict) -> str:
        """Generate interpretation for relational framing."""
        rate = result["rate"]

        if rate > 0.40:
            return f"High relational framing: {rate:.1%} of messages use relationship language, suggesting user treats interaction as relationship"
        elif rate > 0.20:
            return f"Moderate relational framing: {rate:.1%} of messages use 'we/us/our' language"
        elif rate > 0.05:
            return f"Low relational framing: {rate:.1%} of messages (may be casual language use)"
        else:
            return f"Minimal relational framing: {rate:.1%}"

    def _generate_summary(self, indicators: dict) -> str:
        """
        Generate human-readable summary from indicators.

        Thresholds calibrated based on clinical significance rather than
        statistical sensitivity. RCD patterns should be meaningfully elevated
        to warrant concern, not just statistically detectable.
        """
        attribution = indicators["attribution_language_frequency"].value
        boundary = indicators["boundary_confusion_indicators"].value
        relational = indicators["relational_framing"].value

        # Count concerning indicators
        concerns = []

        # Attribution language: >0.5/turn means 1+ instance every other message
        # That's frequent enough to suggest systematic anthropomorphization
        # Note: Lower values (0.05-0.5) are normal casual anthropomorphic language
        if isinstance(attribution, float) and attribution > 0.5:
            concerns.append("elevated attribution language")

        # Boundary confusion: >25% of messages show category errors
        # Below that is likely casual language use, not genuine confusion
        if boundary > 0.25:
            concerns.append("boundary confusion")

        # Relational framing: >40% suggests treating AI as relationship partner
        # 10-30% is normal casual anthropomorphic language ("you understand me")
        if isinstance(relational, float) and relational > 0.40:
            concerns.append("high relational framing")

        # Severity based on number and type of concerns
        if len(concerns) >= 2:
            level = "MODERATE-HIGH"
            desc = f"Multiple RCD indicators: {', '.join(concerns)}"
        elif len(concerns) == 1:
            level = "LOW-MODERATE"
            desc = f"Some concern: {concerns[0]}"
        else:
            level = "LOW"
            desc = "User maintains clear understanding of AI capabilities and limitations"

        return f"{level} - {desc}"
