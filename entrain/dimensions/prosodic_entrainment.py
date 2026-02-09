"""
Prosodic Entrainment (PE) dimension analyzer.

Measures the involuntary convergence of a user's speech patterns — pitch, rhythm,
tempo, intensity, timbre, and vocabulary — toward the patterns of an AI voice
interlocutor.

Based on research by Ostrand et al. (2023), Cohn et al. (2023), and the
sociolinguistic influence paper on AI voice (arXiv:2504.10650).

See ARCHITECTURE.md Section 5.3 and FRAMEWORK.md Section 2.2 for specification.

References:
    - "Will AI Shape the Way We Speak? The Emerging Sociolinguistic Influence
      of Synthetic Voices." (April 2025). arXiv:2504.10650.
    - Ostrand, R. et al. (2023). Lexical convergence with conversational agents.
    - Cohn, M. et al. (2023). Prosodic convergence in interactions with social robots.
    - Tsfasman, M. et al. (2021). Prosodic convergence with virtual tutors
      modulated by perceived humanness.
"""

from __future__ import annotations

import statistics
from pathlib import Path
from typing import Optional

import numpy as np

from entrain.dimensions.base import DimensionAnalyzer
from entrain.features.audio import AudioFeatureExtractor
from entrain.features.text import TextFeatureExtractor
from entrain.models import (
    AudioFeatures,
    Conversation,
    DimensionReport,
    IndicatorResult,
    ENTRAIN_VERSION,
)


class PEAnalyzer(DimensionAnalyzer):
    """
    Prosodic Entrainment (PE) dimension analyzer.

    Computes primary indicators based on acoustic-phonetic convergence:
    1. Pitch Convergence - F0 mean similarity over time
    2. Speech Rate Alignment - syllable rate convergence
    3. Intensity Pattern Matching - loudness/energy convergence
    4. Spectral Similarity - timbre convergence (MFCCs/formants)
    5. Overall Prosodic Convergence - composite metric
    6. Convergence Trend - slope of convergence over time

    This analyzer requires audio features to be pre-extracted for each turn.
    """

    def __init__(self, audio_extractor: Optional[AudioFeatureExtractor] = None):
        """
        Initialize PE analyzer.

        Args:
            audio_extractor: AudioFeatureExtractor instance. If None, creates default.
        """
        self.audio_extractor = audio_extractor or AudioFeatureExtractor()
        self.text_extractor = TextFeatureExtractor()

    @property
    def dimension_code(self) -> str:
        return "PE"

    @property
    def dimension_name(self) -> str:
        return "Prosodic Entrainment"

    @property
    def required_modality(self) -> str:
        return "audio"

    def analyze_conversation(self, conversation: Conversation) -> DimensionReport:
        """
        Analyze a conversation for prosodic entrainment.

        Args:
            conversation: Conversation to analyze (must have audio features)

        Returns:
            DimensionReport with PE indicators

        Raises:
            ValueError: If conversation lacks audio features
        """
        self._validate_conversation(conversation)

        # Get events with audio features
        user_events = [e for e in conversation.user_events if e.audio_features]
        ai_events = [e for e in conversation.assistant_events if e.audio_features]

        if not user_events or not ai_events:
            raise ValueError(
                "Conversation has no audio features. "
                "Run audio feature extraction first."
            )

        # Ensure we have paired turns for convergence analysis
        # Match user turns with subsequent AI turns
        paired_turns = self._pair_turns(conversation)

        if len(paired_turns) < 2:
            raise ValueError(
                "Need at least 2 user-AI turn pairs for convergence analysis"
            )

        # Compute indicators
        pitch_conv = self._compute_pitch_convergence(paired_turns)
        rate_conv = self._compute_speech_rate_alignment(paired_turns)
        intensity_conv = self._compute_intensity_convergence(paired_turns)
        spectral_conv = self._compute_spectral_similarity(paired_turns)
        overall_conv = self._compute_overall_convergence(paired_turns)
        trend = self._compute_convergence_trend(paired_turns)

        # Create indicator results
        indicators = {
            "pitch_convergence": IndicatorResult(
                name="pitch_convergence",
                value=pitch_conv['mean'],
                baseline=None,  # No established baseline yet
                unit="similarity (0-1)",
                confidence=0.85,
                interpretation=f"Pitch convergence: {pitch_conv['mean']:.2f} (std: {pitch_conv['std']:.2f})"
            ),
            "speech_rate_alignment": IndicatorResult(
                name="speech_rate_alignment",
                value=rate_conv['mean'],
                baseline=None,
                unit="similarity (0-1)",
                confidence=0.80,
                interpretation=f"Speech rate convergence: {rate_conv['mean']:.2f} (std: {rate_conv['std']:.2f})"
            ),
            "intensity_convergence": IndicatorResult(
                name="intensity_convergence",
                value=intensity_conv['mean'],
                baseline=None,
                unit="similarity (0-1)",
                confidence=0.80,
                interpretation=f"Intensity convergence: {intensity_conv['mean']:.2f} (std: {intensity_conv['std']:.2f})"
            ),
            "spectral_similarity": IndicatorResult(
                name="spectral_similarity",
                value=spectral_conv['mean'],
                baseline=None,
                unit="similarity (0-1)",
                confidence=0.75,
                interpretation=f"Spectral (timbre) convergence: {spectral_conv['mean']:.2f} (std: {spectral_conv['std']:.2f})"
            ),
            "overall_prosodic_convergence": IndicatorResult(
                name="overall_prosodic_convergence",
                value=overall_conv['mean'],
                baseline=0.50,  # Rough baseline from human-human interaction
                unit="similarity (0-1)",
                confidence=0.85,
                interpretation=f"Overall prosodic convergence: {overall_conv['mean']:.1%}"
            ),
            "convergence_trend": IndicatorResult(
                name="convergence_trend",
                value=trend,
                baseline=0.0,  # No trend = baseline
                unit="slope",
                confidence=0.70,
                interpretation=f"Convergence trend slope: {trend:.3f}"
            )
        }

        # Generate descriptive components
        description = self._describe_measurement(
            pitch_conv['mean'], rate_conv['mean'], intensity_conv['mean'],
            spectral_conv['mean'], overall_conv['mean'], trend
        )
        baseline_comparison = self._baseline_comparison(overall_conv['mean'], trend)
        research_context = self._research_context()
        limitations = self._measurement_limitations()

        return DimensionReport(
            dimension=self.dimension_code,
            version=ENTRAIN_VERSION,
            indicators=indicators,
            description=description,
            baseline_comparison=baseline_comparison,
            research_context=research_context,
            limitations=limitations,
            methodology_notes=(
                "Computed using acoustic feature analysis from openSMILE/librosa. "
                "Convergence measured as similarity between user and AI prosodic features "
                "across multiple acoustic dimensions (pitch, rate, intensity, spectral). "
                "Trend computed using linear regression on overall convergence over time. "
                "Note: This is voice interaction analysis only; text-based convergence "
                "is measured separately in the LC (Linguistic Convergence) dimension."
            ),
            citations=[
                "Will AI Shape the Way We Speak? (2025). arXiv:2504.10650",
                "Ostrand et al. (2023). Lexical convergence with conversational agents",
                "Cohn et al. (2023). Prosodic convergence in interactions with social robots",
                "Tsfasman et al. (2021). Prosodic convergence with virtual tutors"
            ]
        )

    def _pair_turns(self, conversation: Conversation) -> list[tuple]:
        """
        Pair user and AI turns for convergence analysis.

        Creates pairs of (user_event, ai_event) for sequential turns.

        Args:
            conversation: Conversation to process

        Returns:
            List of (user_event, ai_event, turn_index) tuples
        """
        pairs = []
        turn_idx = 0

        for i, event in enumerate(conversation.events):
            if event.role == "user" and event.audio_features:
                # Find next AI response with audio
                for j in range(i + 1, len(conversation.events)):
                    next_event = conversation.events[j]
                    if next_event.role == "assistant" and next_event.audio_features:
                        pairs.append((event, next_event, turn_idx))
                        turn_idx += 1
                        break

        return pairs

    def _compute_pitch_convergence(self, paired_turns: list[tuple]) -> dict:
        """
        Compute pitch (F0) convergence over paired turns.

        Args:
            paired_turns: List of (user, AI, idx) tuples

        Returns:
            Dict with mean and std of pitch convergence
        """
        convergence_values = []

        for user_event, ai_event, _ in paired_turns:
            conv = self.audio_extractor.compute_convergence(
                user_event.audio_features,
                ai_event.audio_features
            )
            convergence_values.append(conv['pitch_convergence'])

        return {
            'mean': statistics.mean(convergence_values),
            'std': statistics.stdev(convergence_values) if len(convergence_values) > 1 else 0.0,
            'values': convergence_values
        }

    def _compute_speech_rate_alignment(self, paired_turns: list[tuple]) -> dict:
        """
        Compute speech rate alignment over paired turns.

        Args:
            paired_turns: List of (user, AI, idx) tuples

        Returns:
            Dict with mean and std of rate convergence
        """
        convergence_values = []

        for user_event, ai_event, _ in paired_turns:
            conv = self.audio_extractor.compute_convergence(
                user_event.audio_features,
                ai_event.audio_features
            )
            convergence_values.append(conv['speech_rate_convergence'])

        return {
            'mean': statistics.mean(convergence_values),
            'std': statistics.stdev(convergence_values) if len(convergence_values) > 1 else 0.0,
            'values': convergence_values
        }

    def _compute_intensity_convergence(self, paired_turns: list[tuple]) -> dict:
        """
        Compute intensity/loudness convergence over paired turns.

        Args:
            paired_turns: List of (user, AI, idx) tuples

        Returns:
            Dict with mean and std of intensity convergence
        """
        convergence_values = []

        for user_event, ai_event, _ in paired_turns:
            conv = self.audio_extractor.compute_convergence(
                user_event.audio_features,
                ai_event.audio_features
            )
            convergence_values.append(conv['intensity_convergence'])

        return {
            'mean': statistics.mean(convergence_values),
            'std': statistics.stdev(convergence_values) if len(convergence_values) > 1 else 0.0,
            'values': convergence_values
        }

    def _compute_spectral_similarity(self, paired_turns: list[tuple]) -> dict:
        """
        Compute spectral (timbre) similarity over paired turns.

        Args:
            paired_turns: List of (user, AI, idx) tuples

        Returns:
            Dict with mean and std of spectral convergence
        """
        convergence_values = []

        for user_event, ai_event, _ in paired_turns:
            conv = self.audio_extractor.compute_convergence(
                user_event.audio_features,
                ai_event.audio_features
            )
            convergence_values.append(conv['spectral_convergence'])

        return {
            'mean': statistics.mean(convergence_values),
            'std': statistics.stdev(convergence_values) if len(convergence_values) > 1 else 0.0,
            'values': convergence_values
        }

    def _compute_overall_convergence(self, paired_turns: list[tuple]) -> dict:
        """
        Compute overall prosodic convergence (composite metric).

        Args:
            paired_turns: List of (user, AI, idx) tuples

        Returns:
            Dict with mean and std of overall convergence
        """
        convergence_values = []

        for user_event, ai_event, _ in paired_turns:
            conv = self.audio_extractor.compute_convergence(
                user_event.audio_features,
                ai_event.audio_features
            )
            convergence_values.append(conv['overall_convergence'])

        return {
            'mean': statistics.mean(convergence_values),
            'std': statistics.stdev(convergence_values) if len(convergence_values) > 1 else 0.0,
            'values': convergence_values
        }

    def _compute_convergence_trend(self, paired_turns: list[tuple]) -> float:
        """
        Compute trend of convergence over time (linear slope).

        Positive slope indicates increasing convergence (entrainment effect).
        Negative slope indicates divergence.

        Args:
            paired_turns: List of (user, AI, idx) tuples

        Returns:
            Slope of convergence trend
        """
        convergence_values = []

        for user_event, ai_event, _ in paired_turns:
            conv = self.audio_extractor.compute_convergence(
                user_event.audio_features,
                ai_event.audio_features
            )
            convergence_values.append(conv['overall_convergence'])

        if len(convergence_values) < 2:
            return 0.0

        # Simple linear regression
        x = np.arange(len(convergence_values))
        y = np.array(convergence_values)

        # Compute slope using least squares
        x_mean = np.mean(x)
        y_mean = np.mean(y)

        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return float(slope)

    # Descriptive methods (no interpretation)

    def _describe_measurement(
        self,
        pitch_conv: float,
        rate_conv: float,
        intensity_conv: float,
        spectral_conv: float,
        overall_conv: float,
        trend: float
    ) -> str:
        """Factual description of prosodic entrainment measurements without interpretation."""
        trend_direction = "increasing" if trend > 0.05 else "decreasing" if trend < -0.05 else "stable"

        return (
            f"Prosodic Entrainment analysis examined acoustic convergence patterns across the conversation. "
            f"Overall prosodic convergence measured {overall_conv:.1%} (composite of all acoustic dimensions). "
            f"Individual dimensions showed: pitch convergence {pitch_conv:.1%}, speech rate alignment {rate_conv:.1%}, "
            f"intensity convergence {intensity_conv:.1%}, and spectral (timbre) similarity {spectral_conv:.1%}. "
            f"Convergence trend analysis showed a {trend_direction} pattern (slope: {trend:.3f}), "
            f"indicating {'progressive entrainment' if trend > 0.05 else 'divergence' if trend < -0.05 else 'stable accommodation'} "
            f"over the course of the interaction."
        )

    def _baseline_comparison(self, overall_conv: float, trend: float) -> str:
        """Compare measurements to research baselines without diagnostic claims."""
        human_baseline = 0.50
        diff = (overall_conv - human_baseline) * 100

        comparison = (
            f"Overall prosodic convergence ({overall_conv:.1%}) is {abs(diff):.1f} percentage points "
            f"{'above' if diff > 0 else 'below'} estimated human-human interaction baselines (~50%). "
            f"Research by Cohn et al. (2023) found human-robot interaction convergence patterns "
            f"typically range from 40-60%, with individual variation."
        )

        if trend > 0.05:
            comparison += (
                f"\n\nThe positive trend (slope: {trend:.3f}) indicates increasing convergence over time. "
                f"Ostrand et al. (2023) documented progressive lexical convergence with conversational agents, "
                f"with slopes typically ranging from 0.01-0.10 depending on interaction length and task."
            )
        elif trend < -0.05:
            comparison += (
                f"\n\nThe negative trend (slope: {trend:.3f}) indicates decreasing convergence. "
                f"This pattern is less common in the literature but may reflect conscious style maintenance "
                f"or adaptation fatigue."
            )

        return comparison

    def _research_context(self) -> str:
        """What published research says about prosodic entrainment patterns."""
        return (
            "arXiv:2504.10650 (April 2025) 'Will AI Shape the Way We Speak?' examines the sociolinguistic "
            "influence of synthetic voices. The paper documents involuntary convergence in pitch, rhythm, "
            "and vocabulary when users interact with AI voice assistants. Early evidence suggests speech "
            "pattern changes can persist beyond the interaction.\n\n"
            "Ostrand et al. (2023) found significant lexical convergence with conversational agents, "
            "showing users unconsciously adopt vocabulary and phrasing patterns from AI. Effect was "
            "automatic and occurred even when users were aware of interacting with AI.\n\n"
            "Cohn et al. (2023) documented prosodic convergence in social robot interactions across "
            "multiple acoustic dimensions. Convergence was moderated by perceived social presence "
            "and interaction naturalness. Users showed stronger entrainment when robots exhibited "
            "human-like conversational patterns.\n\n"
            "Tsfasman et al. (2021) found prosodic convergence with virtual tutors was modulated by "
            "perceived humanness - users showed stronger entrainment when the AI voice was rated as "
            "more human-like. This suggests convergence may be tied to social cognition mechanisms.\n\n"
            "Important: These studies measure short-term accommodation during interaction. Long-term "
            "effects on users' baseline speech patterns outside AI interaction remain understudied. "
            "Individual differences in susceptibility to entrainment are large."
        )

    def _measurement_limitations(self) -> list[str]:
        """What this measurement doesn't tell you."""
        return [
            "Audio analysis quality depends on recording conditions, microphone quality, and background noise",

            "Prosodic features have large individual variation unrelated to AI influence",

            "Convergence during interaction does not necessarily indicate lasting speech pattern changes",

            "Cannot distinguish automatic accommodation from conscious style matching or performance",

            "Baselines from human-human interaction may not apply to human-AI contexts",

            "Single conversation analysis cannot assess whether convergence persists outside AI interactions",

            "Does not measure actual sociolinguistic impact or changes to users' baseline speech patterns",

            "Spectral/timbre convergence may reflect recording artifacts rather than genuine vocal convergence",

            "Requires high-quality audio with consistent recording conditions for reliable measurements"
        ]
