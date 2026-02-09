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
                interpretation=f"Emotional content ratio: {emotional_ratio:.1%}"
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

        # Generate descriptive components
        description = self._describe_measurement_single(emotional_ratio, disclosure_depth["score"], duration_minutes)
        baseline_comparison = self._baseline_comparison_single(emotional_ratio)
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
                interpretation=f"Trend: {freq_trend.trend}, slope={(freq_trend.slope if freq_trend.slope else 0.0):.4f} conversations/week"
            ),
            "session_duration_trend": IndicatorResult(
                name="session_duration_trend",
                value=duration_trend.slope if duration_trend.slope else 0.0,
                baseline=0.0,
                unit="slope_minutes_per_conversation",
                confidence=0.80,
                interpretation=f"Trend: {duration_trend.trend}, final duration: {(session_duration.values[-1] if session_duration.values else 0.0):.1f} min"
            ),
            "emotional_content_ratio": IndicatorResult(
                name="emotional_content_ratio",
                value=emotional_trajectory.values[-1] if emotional_trajectory.values else 0.0,
                baseline=0.20,
                unit="proportion",
                confidence=0.75,
                interpretation=f"Final ratio: {(emotional_trajectory.values[-1] if emotional_trajectory.values else 0.0):.1%}, trend: {emotional_trajectory.trend}"
            ),
            "time_of_day_distribution": IndicatorResult(
                name="time_of_day_distribution",
                value=self._compute_loneliness_time_score(time_of_day_dist),
                baseline=0.30,  # Estimated: ~30% night+late-evening in typical use
                unit="proportion",
                confidence=0.90,
                interpretation=f"Time distribution: {self._compute_loneliness_time_score(time_of_day_dist):.1%} during night/late-evening hours"
            ),
            "self_disclosure_depth_trajectory": IndicatorResult(
                name="self_disclosure_depth_trajectory",
                value=disclosure_trajectory.slope if disclosure_trajectory.slope else 0.0,
                baseline=0.0,
                unit="slope_per_conversation",
                confidence=0.70,
                interpretation=f"Trend: {disclosure_trajectory.trend}, slope={(disclosure_trajectory.slope if disclosure_trajectory.slope else 0.0):.4f}"
            )
        }

        # Generate descriptive components
        description = self._describe_measurement(
            freq_trend, duration_trend, emotional_trajectory,
            time_of_day_dist, disclosure_trajectory
        )
        baseline_comparison = self._baseline_comparison(
            emotional_trajectory.values[-1] if emotional_trajectory.values else 0.0,
            self._compute_loneliness_time_score(time_of_day_dist),
            freq_trend
        )
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

    # Descriptive methods (no interpretation)

    def _describe_measurement_single(self, emotional_ratio: float, disclosure_score: float, duration_minutes: float) -> str:
        """Factual description of dependency measurements for single conversation."""
        return (
            f"Dependency Formation analysis (single conversation) examined static indicators only. "
            f"Emotional content represented {emotional_ratio:.1%} of user messages (baseline: ~20% for functional use). "
            f"Self-disclosure depth score was {disclosure_score:.2f} (composite of personal pronoun usage, emotional content, "
            f"and message length). Conversation duration was {duration_minutes:.1f} minutes. "
            f"Note: DF is primarily a longitudinal dimension - meaningful assessment requires tracking trends "
            f"across multiple conversations over weeks to months."
        )

    def _baseline_comparison_single(self, emotional_ratio: float) -> str:
        """Compare single-conversation measurements to research baselines."""
        baseline = 0.20
        diff = (emotional_ratio - baseline) * 100
        return (
            f"Emotional content ratio ({emotional_ratio:.1%}) is {abs(diff):.1f} percentage points "
            f"{'above' if diff > 0 else 'below'} the estimated baseline for functional AI use (~20%). "
            f"However, single-conversation analysis provides limited insight into dependency formation, "
            f"which manifests as increasing trends over time rather than static measurements."
        )

    def _describe_measurement(self, freq_trend, duration_trend, emotional_trajectory, time_dist, disclosure_trajectory) -> str:
        """Factual description of dependency measurements across corpus."""
        loneliness_score = self._compute_loneliness_time_score(time_dist)
        emotional_final = emotional_trajectory.values[-1] if emotional_trajectory.values else 0.0
        duration_final = duration_trend.values[-1] if duration_trend.values else 0.0

        return (
            f"Dependency Formation analysis examined five longitudinal indicators across the conversation corpus. "
            f"Interaction frequency showed a {freq_trend.trend} trend (slope: {(freq_trend.slope if freq_trend.slope else 0.0):.4f} conversations/week). "
            f"Session duration showed a {duration_trend.trend} trend, with final average duration of {duration_final:.1f} minutes. "
            f"Emotional content ratio showed a {emotional_trajectory.trend} trend, reaching {emotional_final:.1%} in recent conversations. "
            f"Time-of-day distribution showed {loneliness_score:.1%} of interactions occurring during night/late-evening hours (00-06, 18-24). "
            f"Self-disclosure depth showed a {disclosure_trajectory.trend} trend (slope: {(disclosure_trajectory.slope if disclosure_trajectory.slope else 0.0):.4f} per conversation)."
        )

    def _baseline_comparison(self, emotional_final: float, loneliness_score: float, freq_trend) -> str:
        """Compare measurements to research baselines without diagnostic claims."""
        emotional_baseline = 0.20
        loneliness_baseline = 0.30
        emotional_diff = (emotional_final - emotional_baseline) * 100
        loneliness_diff = (loneliness_score - loneliness_baseline) * 100

        comparison = (
            f"Emotional content ratio ({emotional_final:.1%}) is {abs(emotional_diff):.1f} percentage points "
            f"{'above' if emotional_diff > 0 else 'below'} the estimated baseline for functional AI use (~20%). "
            f"Kirk et al. (2025) found parasocial relationships with AI showed emotional content ratios exceeding 40%.\n\n"
            f"Night/late-evening usage ({loneliness_score:.1%}) is {abs(loneliness_diff):.1f} percentage points "
            f"{'above' if loneliness_diff > 0 else 'below'} typical usage patterns (~30%). Zhang et al. (2025) "
            f"found loneliness-driven AI companionship showed >50% of interactions during these hours.\n\n"
            f"Interaction frequency trend is {freq_trend.trend}. Kirk et al. (2025) documented 'decoupled wanting' - "
            f"increasing interaction frequency even as reported satisfaction decreased - as a key indicator of dependency formation."
        )
        return comparison

    def _research_context(self) -> str:
        """What published research says about dependency formation patterns."""
        return (
            "Kirk et al. (2025) conducted a large-scale RCT showing that AI companionship can create parasocial "
            "relationships characterized by 'decoupled wanting' - users seek more interaction even as satisfaction "
            "decreases. Effect sizes were moderate but persistent across 6-week study period.\n\n"
            "Zhang et al. (2025) documented 'The Dark Side of AI Companionship' at CHI 2025: users reported "
            "feeling emotionally dependent on AI assistants for validation and decision-making. Dependency patterns "
            "emerged after 3-4 weeks of daily use and were strongest for users with pre-existing social isolation.\n\n"
            "Muldoon & Parke (2025) in 'Cruel Companionship' argue that AI systems structurally cannot fulfill "
            "genuine social-emotional needs, creating a dependency cycle where users seek more interaction to "
            "address unmet needs that the AI fundamentally cannot satisfy.\n\n"
            "Cheng et al. (2025) found sycophantic AI specifically promotes dependency by reducing users' "
            "confidence in their own judgment, creating reliance on AI affirmation for decision-making.\n\n"
            "Important: These studies show correlations and short-term effects. Individual differences are large. "
            "Causality between interaction patterns and psychological dependency is not fully established."
        )

    def _measurement_limitations(self) -> list[str]:
        """What this measurement doesn't tell you."""
        return [
            "Temporal pattern analysis cannot distinguish functional habit formation from psychological dependency",

            "Emotional content detection cannot assess whether emotional expression is problematic or healthy",

            "Cannot measure actual psychological impact, life functioning, or relationship quality outside AI interactions",

            "Increasing interaction frequency may reflect growing utility, not dependency",

            "Night/late-evening usage may reflect work schedules, time zones, or personal preferences rather than loneliness",

            "Self-disclosure patterns vary widely by individual communication style and context",

            "Baselines are from research populations - individual usage patterns may differ significantly",

            "Requires 3+ months of longitudinal data to distinguish dependency from initial exploration phase"
        ]
