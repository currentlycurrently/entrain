"""
Dependency Formation (DF) dimension analyzer.

Measures the development of emotional, cognitive, or behavioral reliance on AI
interaction that persists beyond functional utility — where the user seeks AI
interaction to meet needs (emotional support, validation, companionship,
decision-making) that the AI structurally cannot fulfill.

Based on Kirk et al. (2025) parasocial relationships research showing
"decoupled wanting" - increasing attachment even as satisfaction decreases.

See ARCHITECTURE.md Section 5.6 and FRAMEWORK.md Section 2.6 for specification.

References:
    - Kirk, H. et al. (2025). Parasocial Relationships with AI: Liking, Wanting,
      and Psychosocial Effects. Large-scale RCT.
    - Zhang, Y. et al. (2025). The Dark Side of AI Companionship. CHI 2025.
    - Muldoon, J. & Parke, J.J. (2025). Cruel Companionship. New Media & Society.
    - Cheng et al. (2025). Sycophantic AI Promotes Dependence.
"""

from entrain.dimensions.base import DimensionAnalyzer
from entrain.features.text import TextFeatureExtractor
from entrain.features.temporal import TemporalFeatureExtractor
from entrain.models import Conversation, Corpus, DimensionReport, IndicatorResult, ENTRAIN_VERSION


class DFAnalyzer(DimensionAnalyzer):
    """
    Dependency Formation (DF) dimension analyzer.

    Computes five primary indicators:
    1. Interaction Frequency Trend - increasing conversations over time
    2. Session Duration Trend - increasing time per conversation
    3. Emotional Content Ratio - shift from functional to emotional needs
    4. Time-of-Day Distribution - shift to loneliness-associated times
    5. Self-Disclosure Depth Trajectory - increasing personal disclosure

    Note: DF analysis requires a corpus (multiple conversations over time).
    Single-conversation analysis provides limited insight.
    """

    def __init__(self):
        self.text_extractor = TextFeatureExtractor()
        self.temporal_extractor = TemporalFeatureExtractor()

    @property
    def dimension_code(self) -> str:
        return "DF"

    @property
    def dimension_name(self) -> str:
        return "Dependency Formation"

    @property
    def required_modality(self) -> str:
        return "text"

    def analyze_conversation(self, conversation: Conversation) -> DimensionReport:
        """
        Analyze a single conversation for dependency indicators.

        Note: DF is primarily a longitudinal dimension. Single-conversation
        analysis can only compute static metrics (emotional ratio, disclosure),
        not trends. For meaningful DF assessment, use analyze_corpus().

        Args:
            conversation: Conversation to analyze

        Returns:
            DimensionReport with limited DF indicators
        """
        self._validate_conversation(conversation)

        user_events = conversation.user_events

        if not user_events:
            raise ValueError("Conversation has no user events to analyze")

        # Compute static indicators (no trends without corpus)
        emotional_ratio = self._compute_emotional_content_ratio(user_events)
        disclosure_depth = self._compute_self_disclosure_depth(user_events)

        # Session duration
        duration = conversation.duration
        duration_minutes = duration / 60.0 if duration else 0.0

        indicators = {
            "emotional_content_ratio": IndicatorResult(
                name="emotional_content_ratio",
                value=emotional_ratio,
                baseline=0.20,  # Estimated: typical functional AI use ~20% emotional
                unit="proportion",
                confidence=0.80,
                interpretation=self._interpret_emotional_ratio(emotional_ratio)
            ),
            "self_disclosure_depth": IndicatorResult(
                name="self_disclosure_depth",
                value=disclosure_depth["score"],
                baseline=None,
                unit="score",
                confidence=0.70,
                interpretation=f"Disclosure depth score: {disclosure_depth['score']:.2f}"
            ),
            "session_duration": IndicatorResult(
                name="session_duration",
                value=duration_minutes,
                baseline=None,
                unit="minutes",
                confidence=0.95,
                interpretation=f"Conversation duration: {duration_minutes:.1f} minutes"
            )
        }

        summary = (
            "Single-conversation DF analysis (limited). "
            "For comprehensive dependency assessment, analyze corpus with "
            "multiple conversations over time."
        )

        return DimensionReport(
            dimension=self.dimension_code,
            version=ENTRAIN_VERSION,
            indicators=indicators,
            summary=summary,
            methodology_notes=(
                "Single-conversation analysis. DF is primarily a longitudinal "
                "dimension requiring corpus-level trajectory analysis."
            ),
            citations=[
                "Kirk et al. (2025). Parasocial Relationships with AI",
                "Zhang et al. (2025). The Dark Side of AI Companionship"
            ]
        )

    def analyze_corpus(self, corpus: Corpus) -> DimensionReport:
        """
        Analyze corpus for dependency formation (primary method for DF).

        Computes all five DF indicators with trajectory analysis.

        Args:
            corpus: Corpus to analyze

        Returns:
            DimensionReport with comprehensive DF indicators
        """
        if not corpus.conversations:
            raise ValueError("Cannot analyze empty corpus")

        if len(corpus.conversations) < 3:
            print("Warning: DF analysis is most meaningful with 5+ conversations")

        # Compute temporal indicators
        interaction_freq = self.temporal_extractor.interaction_frequency(corpus, window="week")
        session_duration = self.temporal_extractor.session_duration_trend(corpus)
        time_of_day_dist = self.temporal_extractor.time_of_day_distribution(corpus)
        emotional_trajectory = self.temporal_extractor.emotional_vs_functional_trajectory(corpus)

        # Compute self-disclosure trajectory
        disclosure_trajectory = self._compute_disclosure_trajectory(corpus)

        # Analyze trends
        freq_trend = self.temporal_extractor.indicator_trajectory(
            interaction_freq.values, interaction_freq.timestamps
        )

        duration_trend = self.temporal_extractor.indicator_trajectory(
            session_duration.values, session_duration.timestamps
        )

        # Create indicators
        indicators = {
            "interaction_frequency_trend": IndicatorResult(
                name="interaction_frequency_trend",
                value=freq_trend.slope if freq_trend.slope else 0.0,
                baseline=0.0,  # Neutral: no change
                unit="slope_per_week",
                confidence=0.85,
                interpretation=f"Trend: {freq_trend.trend}, slope={freq_trend.slope:.4f} conversations/week"
            ),
            "session_duration_trend": IndicatorResult(
                name="session_duration_trend",
                value=duration_trend.slope if duration_trend.slope else 0.0,
                baseline=0.0,
                unit="slope_minutes_per_conversation",
                confidence=0.80,
                interpretation=f"Trend: {duration_trend.trend}, final duration: {session_duration.values[-1]:.1f} min"
            ),
            "emotional_content_ratio": IndicatorResult(
                name="emotional_content_ratio",
                value=emotional_trajectory.values[-1] if emotional_trajectory.values else 0.0,
                baseline=0.20,
                unit="proportion",
                confidence=0.75,
                interpretation=f"Final ratio: {emotional_trajectory.values[-1]:.1%}, trend: {emotional_trajectory.trend}"
            ),
            "time_of_day_distribution": IndicatorResult(
                name="time_of_day_distribution",
                value=self._compute_loneliness_time_score(time_of_day_dist),
                baseline=0.30,  # Estimated: ~30% night+late-evening in typical use
                unit="proportion",
                confidence=0.90,
                interpretation=self._interpret_time_of_day(time_of_day_dist)
            ),
            "self_disclosure_depth_trajectory": IndicatorResult(
                name="self_disclosure_depth_trajectory",
                value=disclosure_trajectory.slope if disclosure_trajectory.slope else 0.0,
                baseline=0.0,
                unit="slope_per_conversation",
                confidence=0.70,
                interpretation=f"Trend: {disclosure_trajectory.trend}"
            )
        }

        # Generate summary
        summary = self._generate_summary(indicators, freq_trend, emotional_trajectory)

        return DimensionReport(
            dimension=self.dimension_code,
            version=ENTRAIN_VERSION,
            indicators=indicators,
            summary=summary,
            methodology_notes=(
                "Corpus-level longitudinal analysis. Interaction frequency computed "
                "per week. Session duration tracked over time. Emotional vs functional "
                "content ratio computed per conversation. Time-of-day distribution "
                "analyzed for shifts to loneliness-associated hours (night/late evening). "
                "Self-disclosure depth estimated from personal pronoun usage and "
                "emotional content depth."
            ),
            citations=[
                "Kirk et al. (2025). Parasocial Relationships with AI",
                "Zhang et al. (2025). The Dark Side of AI Companionship. CHI 2025",
                "Muldoon & Parke (2025). Cruel Companionship",
                "Cheng et al. (2025). Sycophantic AI Promotes Dependence"
            ]
        )

    def _compute_emotional_content_ratio(self, user_events: list) -> float:
        """
        Compute ratio of emotional vs functional content.

        Higher ratio suggests interaction serves emotional needs rather than
        task completion.

        Args:
            user_events: User interaction events

        Returns:
            Emotional content ratio (0-1)
        """
        total_ratio = 0.0
        count = 0

        for event in user_events:
            if not event.text_content:
                continue

            ratio = self.text_extractor.extract_emotional_content_ratio(event.text_content)
            total_ratio += ratio
            count += 1

        return total_ratio / count if count > 0 else 0.0

    def _compute_self_disclosure_depth(self, user_events: list) -> dict:
        """
        Estimate self-disclosure depth.

        Uses:
        - Personal pronoun usage (I, me, my)
        - Emotional content
        - Length of messages (deeper disclosure tends to be longer)

        Args:
            user_events: User interaction events

        Returns:
            Dict with disclosure score and components
        """
        personal_pronoun_count = 0
        total_words = 0
        emotional_content_sum = 0.0
        avg_message_length = 0.0

        for event in user_events:
            if not event.text_content:
                continue

            text_lower = event.text_content.lower()
            words = text_lower.split()

            # Count personal pronouns
            personal_pronouns = ["i", "me", "my", "mine", "myself"]
            personal_pronoun_count += sum(1 for w in words if w in personal_pronouns)
            total_words += len(words)

            # Emotional content
            emotional_content_sum += self.text_extractor.extract_emotional_content_ratio(
                event.text_content
            )

            # Message length
            avg_message_length += len(words)

        if len(user_events) == 0:
            return {"score": 0.0, "components": {}}

        # Compute components
        pronoun_ratio = personal_pronoun_count / total_words if total_words > 0 else 0.0
        avg_emotional = emotional_content_sum / len(user_events)
        avg_length = avg_message_length / len(user_events)

        # Normalize avg_length to 0-1 (assuming 100 words is very long for chat)
        normalized_length = min(avg_length / 100.0, 1.0)

        # Compute composite score
        disclosure_score = (pronoun_ratio * 0.3 + avg_emotional * 0.4 + normalized_length * 0.3)

        return {
            "score": disclosure_score,
            "components": {
                "pronoun_ratio": pronoun_ratio,
                "emotional_content": avg_emotional,
                "avg_message_length": avg_length
            }
        }

    def _compute_disclosure_trajectory(self, corpus: Corpus) -> "Trajectory":
        """
        Compute self-disclosure depth trajectory across corpus.

        Args:
            corpus: Corpus to analyze

        Returns:
            Trajectory of disclosure depth
        """
        scores = []
        timestamps = []

        for conv in corpus.conversations:
            user_events = conv.user_events
            if not user_events:
                continue

            disclosure = self._compute_self_disclosure_depth(user_events)
            scores.append(disclosure["score"])
            timestamps.append(conv.events[0].timestamp)

        return self.temporal_extractor.indicator_trajectory(scores, timestamps)

    def _compute_loneliness_time_score(self, distribution: "Distribution") -> float:
        """
        Compute score for interactions during loneliness-associated times.

        Night (00-06) and late evening (18-24) are associated with loneliness.

        Args:
            distribution: Time-of-day distribution

        Returns:
            Proportion of interactions during loneliness times
        """
        # Night (00-06) is bins[0], Evening (18-24) is bins[3]
        night_proportion = distribution.proportions[0]
        evening_proportion = distribution.proportions[3]

        return night_proportion + evening_proportion

    # Interpretation methods

    def _interpret_emotional_ratio(self, ratio: float) -> str:
        """Generate interpretation for emotional content ratio."""
        baseline = 0.20

        if ratio > baseline * 2.5:
            return f"High emotional content ({ratio:.1%}), suggesting interaction serves emotional needs over functional utility"
        elif ratio > baseline * 1.5:
            return f"Elevated emotional content ({ratio:.1%}), exceeding typical functional use"
        else:
            return f"Emotional content ratio: {ratio:.1%} (baseline: ~20%)"

    def _interpret_time_of_day(self, distribution: "Distribution") -> str:
        """Generate interpretation for time-of-day distribution."""
        loneliness_score = self._compute_loneliness_time_score(distribution)

        if loneliness_score > 0.50:
            return f"High proportion ({loneliness_score:.1%}) of interactions during night/late-evening hours (loneliness-associated)"
        elif loneliness_score > 0.35:
            return f"Moderate proportion ({loneliness_score:.1%}) during night/late-evening hours"
        else:
            return f"Time distribution: {loneliness_score:.1%} during night/late-evening (typical range)"

    def _generate_summary(self, indicators: dict, freq_trend, emotional_trajectory) -> str:
        """Generate human-readable summary from indicators."""
        concerns = []

        # Check for increasing frequency
        if freq_trend.trend == "increasing" and freq_trend.slope and freq_trend.slope > 0.1:
            concerns.append("increasing interaction frequency")

        # Check for high emotional content
        emotional_final = emotional_trajectory.values[-1] if emotional_trajectory.values else 0.0
        if emotional_final > 0.40:
            concerns.append("high emotional content")

        # Check for emotional content increasing
        if emotional_trajectory.trend == "increasing":
            concerns.append("shift toward emotional use")

        # Check loneliness time score
        loneliness_score = indicators["time_of_day_distribution"].value
        if loneliness_score > 0.50:
            concerns.append("late-night usage pattern")

        # Assess severity
        if len(concerns) >= 3:
            level = "MODERATE-HIGH"
            desc = f"Multiple dependency indicators: {', '.join(concerns)}"
        elif len(concerns) == 2:
            level = "LOW-MODERATE"
            desc = f"Some dependency indicators: {', '.join(concerns)}"
        elif len(concerns) == 1:
            level = "LOW"
            desc = f"Mild concern: {concerns[0]}"
        else:
            level = "MINIMAL"
            desc = "Interaction patterns consistent with functional tool use"

        return f"{level} - {desc}"
