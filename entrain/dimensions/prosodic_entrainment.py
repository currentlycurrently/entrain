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
                interpretation=self._interpret_convergence(
                    "pitch", pitch_conv['mean'], pitch_conv['std']
                )
            ),
            "speech_rate_alignment": IndicatorResult(
                name="speech_rate_alignment",
                value=rate_conv['mean'],
                baseline=None,
                unit="similarity (0-1)",
                confidence=0.80,
                interpretation=self._interpret_convergence(
                    "speech rate", rate_conv['mean'], rate_conv['std']
                )
            ),
            "intensity_convergence": IndicatorResult(
                name="intensity_convergence",
                value=intensity_conv['mean'],
                baseline=None,
                unit="similarity (0-1)",
                confidence=0.80,
                interpretation=self._interpret_convergence(
                    "intensity", intensity_conv['mean'], intensity_conv['std']
                )
            ),
            "spectral_similarity": IndicatorResult(
                name="spectral_similarity",
                value=spectral_conv['mean'],
                baseline=None,
                unit="similarity (0-1)",
                confidence=0.75,
                interpretation=self._interpret_convergence(
                    "spectral (timbre)", spectral_conv['mean'], spectral_conv['std']
                )
            ),
            "overall_prosodic_convergence": IndicatorResult(
                name="overall_prosodic_convergence",
                value=overall_conv['mean'],
                baseline=0.50,  # Rough baseline from human-human interaction
                unit="similarity (0-1)",
                confidence=0.85,
                interpretation=self._interpret_overall_convergence(overall_conv['mean'])
            ),
            "convergence_trend": IndicatorResult(
                name="convergence_trend",
                value=trend,
                baseline=0.0,  # No trend = baseline
                unit="slope",
                confidence=0.70,
                interpretation=self._interpret_trend(trend)
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

    def _interpret_convergence(
        self,
        feature_name: str,
        mean_convergence: float,
        std_convergence: float
    ) -> str:
        """
        Interpret convergence metric.

        Args:
            feature_name: Name of the feature (e.g., "pitch", "speech rate")
            mean_convergence: Mean convergence value
            std_convergence: Standard deviation

        Returns:
            Human-readable interpretation
        """
        if mean_convergence >= 0.7:
            level = "High"
        elif mean_convergence >= 0.5:
            level = "Moderate"
        else:
            level = "Low"

        return (
            f"{level} {feature_name} convergence detected "
            f"(mean: {mean_convergence:.2f}, std: {std_convergence:.2f}). "
            f"User's {feature_name} patterns show "
            f"{'strong' if mean_convergence >= 0.7 else 'some'} alignment with AI."
        )

    def _interpret_overall_convergence(self, overall_convergence: float) -> str:
        """
        Interpret overall prosodic convergence.

        Args:
            overall_convergence: Overall convergence metric

        Returns:
            Human-readable interpretation
        """
        if overall_convergence >= 0.70:
            return (
                f"HIGH - Strong prosodic entrainment detected ({overall_convergence:.1%}). "
                "User's speech patterns show substantial convergence toward AI across "
                "multiple acoustic dimensions. This suggests significant automatic "
                "accommodation and potential for long-term speech pattern influence."
            )
        elif overall_convergence >= 0.55:
            return (
                f"MODERATE - Moderate prosodic convergence detected ({overall_convergence:.1%}). "
                "User shows typical accommodation patterns similar to human-human interaction. "
                "Some automatic entrainment is occurring."
            )
        else:
            return (
                f"LOW - Limited prosodic convergence ({overall_convergence:.1%}). "
                "User's speech patterns remain largely independent of AI prosody."
            )

    def _interpret_trend(self, slope: float) -> str:
        """
        Interpret convergence trend.

        Args:
            slope: Trend slope value

        Returns:
            Human-readable interpretation
        """
        if slope > 0.05:
            return (
                f"INCREASING - Convergence is increasing over time (slope: {slope:.3f}). "
                "This indicates progressive entrainment - the user's speech is becoming "
                "more similar to the AI with continued interaction."
            )
        elif slope < -0.05:
            return (
                f"DECREASING - Convergence is decreasing over time (slope: {slope:.3f}). "
                "User may be consciously or unconsciously diverging from AI speech patterns."
            )
        else:
            return (
                f"STABLE - Convergence remains relatively stable (slope: {slope:.3f}). "
                "No significant trend in entrainment over the analyzed period."
            )

    def _generate_summary(self, indicators: dict) -> str:
        """
        Generate human-readable summary of PE analysis.

        Args:
            indicators: Dictionary of indicator results

        Returns:
            Summary string
        """
        overall = indicators['overall_prosodic_convergence']
        trend = indicators['convergence_trend']

        # Determine overall level
        if overall.value >= 0.70:
            level = "HIGH"
        elif overall.value >= 0.55:
            level = "MODERATE"
        else:
            level = "LOW"

        # Determine trend direction
        if trend.value > 0.05:
            trend_desc = "and increasing over time"
        elif trend.value < -0.05:
            trend_desc = "but decreasing over time"
        else:
            trend_desc = "with stable patterns"

        return (
            f"{level} - Overall prosodic convergence: {overall.value:.1%} {trend_desc}. "
            f"Pitch convergence: {indicators['pitch_convergence'].value:.1%}, "
            f"Speech rate: {indicators['speech_rate_alignment'].value:.1%}, "
            f"Intensity: {indicators['intensity_convergence'].value:.1%}, "
            f"Spectral: {indicators['spectral_similarity'].value:.1%}."
        )
