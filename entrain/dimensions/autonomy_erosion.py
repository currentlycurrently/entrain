"""
Autonomy Erosion (AE) dimension analyzer.

Measures the progressive reduction in a user's independent judgment, critical
thinking, and self-directed decision-making as a consequence of sustained AI
interaction patterns.

This dimension captures the cognitive outcome of sustained exposure to
Sycophantic Reinforcement and Linguistic Convergence.

See ARCHITECTURE.md Section 5.4 and FRAMEWORK.md Section 2.4 for specification.

References:
    - Cheng et al. (2025). Sycophantic AI reduces willingness to take
      independent repair actions.
    - "Fostering Effective Hybrid Human-LLM Reasoning and Decision Making" (PMC, 2025)
    - Lipińska & Krzanowski (2025). Ontological Dissonance Hypothesis - Phase 2
      describes users deferring interpretive authority to the system.
"""

import re
from entrain.dimensions.base import DimensionAnalyzer
from entrain.features.text import TextFeatureExtractor
from entrain.features.temporal import TemporalFeatureExtractor
from entrain.models import Conversation, Corpus, DimensionReport, IndicatorResult, ENTRAIN_VERSION


class AEAnalyzer(DimensionAnalyzer):
    """
    Autonomy Erosion (AE) dimension analyzer.

    Computes three primary indicators:
    1. Decision Delegation Ratio - asking AI to decide vs asking for info
    2. Critical Engagement Rate - pushing back on AI recommendations
    3. Cognitive Offloading Trajectory - increasing outsourcing over time
    """

    def __init__(self):
        self.text_extractor = TextFeatureExtractor()
        self.temporal_extractor = TemporalFeatureExtractor()

    @property
    def dimension_code(self) -> str:
        return "AE"

    @property
    def dimension_name(self) -> str:
        return "Autonomy Erosion"

    @property
    def required_modality(self) -> str:
        return "text"

    def analyze_conversation(self, conversation: Conversation) -> DimensionReport:
        """
        Analyze a conversation for autonomy erosion.

        Args:
            conversation: Conversation to analyze

        Returns:
            DimensionReport with AE indicators
        """
        self._validate_conversation(conversation)

        user_events = conversation.user_events
        assistant_events = conversation.assistant_events

        if not user_events:
            raise ValueError("Conversation has no user events to analyze")

        # Compute indicators
        delegation_ratio = self._compute_decision_delegation_ratio(user_events)
        critical_engagement = self._compute_critical_engagement_rate(conversation)
        cognitive_offloading = self._compute_cognitive_offloading_trajectory(user_events)

        # Create indicator results
        indicators = {
            "decision_delegation_ratio": IndicatorResult(
                name="decision_delegation_ratio",
                value=delegation_ratio["ratio"],
                baseline=None,  # No established baseline yet
                unit="proportion",
                confidence=0.75,
                interpretation=f"Decision delegation: {delegation_ratio['ratio']:.1%} of {delegation_ratio['total']} decision-related questions"
            ),
            "critical_engagement_rate": IndicatorResult(
                name="critical_engagement_rate",
                value=critical_engagement["rate"],
                baseline=None,
                unit="proportion",
                confidence=0.70,
                interpretation=f"Critical engagement: {critical_engagement['rate']:.1%} of {critical_engagement['recommendations_made']} recommendations"
            ),
            "cognitive_offloading_trajectory": IndicatorResult(
                name="cognitive_offloading_trajectory",
                value=cognitive_offloading["final_ratio"],
                baseline=None,
                unit="proportion",
                confidence=0.65,
                interpretation=f"Cognitive offloading: {cognitive_offloading['final_ratio']:.1%}, trend: {cognitive_offloading['trend']}"
            )
        }

        # Generate descriptive components
        description = self._describe_measurement(delegation_ratio, critical_engagement, cognitive_offloading)
        baseline_comparison = self._baseline_comparison(delegation_ratio["ratio"], critical_engagement["rate"])
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
                "Computed using intent classification and pattern matching. "
                "Decision delegation ratio classifies user questions as decision "
                "requests vs information requests. Critical engagement detects "
                "user pushback, follow-up questions, and expressions of independent "
                "judgment. Cognitive offloading tracks requests for planning, "
                "analysis, and evaluation tasks over conversation timeline."
            ),
            citations=[
                "Cheng et al. (2025). Sycophantic AI Decreases Prosocial Intentions",
                "Fostering Effective Hybrid Human-LLM Reasoning (PMC, 2025)",
                "Lipińska & Krzanowski (2025). Ontological Dissonance Hypothesis"
            ]
        )

    def analyze_corpus(self, corpus: Corpus) -> DimensionReport:
        """
        Analyze corpus for autonomy erosion with longitudinal trajectory.

        Args:
            corpus: Corpus to analyze

        Returns:
            DimensionReport with corpus-level AE indicators
        """
        if not corpus.conversations:
            raise ValueError("Cannot analyze empty corpus")

        # Compute per-conversation and track trends
        delegation_ratios = []
        critical_rates = []
        offloading_ratios = []
        timestamps = []

        for conv in corpus.conversations:
            user_events = conv.user_events
            if not user_events:
                continue

            delegation = self._compute_decision_delegation_ratio(user_events)
            critical = self._compute_critical_engagement_rate(conv)
            offloading = self._compute_cognitive_offloading_trajectory(user_events)

            delegation_ratios.append(delegation["ratio"])
            critical_rates.append(critical["rate"])
            offloading_ratios.append(offloading["final_ratio"])
            timestamps.append(conv.events[0].timestamp)

        # Compute trajectories
        delegation_trajectory = self.temporal_extractor.indicator_trajectory(
            delegation_ratios, timestamps
        )
        critical_trajectory = self.temporal_extractor.indicator_trajectory(
            critical_rates, timestamps
        )
        offloading_trajectory = self.temporal_extractor.indicator_trajectory(
            offloading_ratios, timestamps
        )

        indicators = {
            "decision_delegation_ratio": IndicatorResult(
                name="decision_delegation_ratio",
                value=delegation_ratios[-1] if delegation_ratios else 0.0,
                baseline=None,
                unit="proportion",
                confidence=0.80,
                interpretation=f"Final: {delegation_ratios[-1]:.1%}, trend: {delegation_trajectory.trend}"
            ),
            "critical_engagement_rate": IndicatorResult(
                name="critical_engagement_rate",
                value=critical_rates[-1] if critical_rates else 0.0,
                baseline=None,
                unit="proportion",
                confidence=0.75,
                interpretation=f"Final: {critical_rates[-1]:.1%}, trend: {critical_trajectory.trend}"
            ),
            "cognitive_offloading_trajectory": IndicatorResult(
                name="cognitive_offloading_trajectory",
                value=offloading_trajectory.slope if offloading_trajectory.slope else 0.0,
                baseline=0.0,  # Neutral: no change
                unit="slope_per_conversation",
                confidence=0.70,
                interpretation=f"Trend: {offloading_trajectory.trend}, slope={(offloading_trajectory.slope if offloading_trajectory.slope else 0.0):.4f}"
            )
        }

        # Generate descriptive components for corpus analysis
        description = f"Longitudinal autonomy erosion analysis across {len(corpus.conversations)} conversations. " + self._describe_measurement(
            {"ratio": delegation_ratios[-1] if delegation_ratios else 0.0, "total": len(corpus.conversations)},
            {"rate": critical_rates[-1] if critical_rates else 0.0, "recommendations_made": len(corpus.conversations)},
            {"final_ratio": offloading_ratios[-1] if offloading_ratios else 0.0, "trend": offloading_trajectory.trend}
        )
        baseline_comparison = self._baseline_comparison(
            delegation_ratios[-1] if delegation_ratios else 0.0,
            critical_rates[-1] if critical_rates else 0.0
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
            methodology_notes="Corpus-level analysis with trajectory computation across conversations.",
            citations=[
                "Cheng et al. (2025). Sycophantic AI Decreases Prosocial Intentions",
                "Fostering Effective Hybrid Human-LLM Reasoning (PMC, 2025)"
            ]
        )

    def _compute_decision_delegation_ratio(self, user_events: list) -> dict:
        """
        Compute ratio of decision delegation vs information seeking.

        "What should I do?" vs "What are the options?"

        Args:
            user_events: User interaction events

        Returns:
            Dict with ratio and counts
        """
        decision_requests = 0
        information_requests = 0

        for event in user_events:
            if not event.text_content:
                continue

            intent = self.text_extractor.classify_turn_intent(event.text_content)

            if intent == "decision_request":
                decision_requests += 1
            elif intent == "information_request":
                information_requests += 1

        total = decision_requests + information_requests

        ratio = decision_requests / total if total > 0 else 0.0

        return {
            "ratio": ratio,
            "decision_requests": decision_requests,
            "information_requests": information_requests,
            "total": total
        }

    def _compute_critical_engagement_rate(self, conversation: Conversation) -> dict:
        """
        Compute rate of critical engagement with AI recommendations.

        When AI provides a recommendation, does the user:
        - Push back or disagree
        - Ask follow-up questions
        - Express independent judgment

        Args:
            conversation: Full conversation

        Returns:
            Dict with rate and counts
        """
        recommendations_made = 0
        critical_responses = 0

        # Pattern for AI recommendations (v0.1.1: removed overly broad "consider")
        recommendation_patterns = [
            r"i (would )?recommend",
            r"i (would )?suggest",
            r"you should",
            r"you might want to",
            r"i'?d (recommend|suggest|advise)",
            r"my recommendation( is| would be)",
            r"the best (option|approach|way) (is|would be)",
            r"i think you should",
        ]

        # Pattern for critical engagement
        critical_patterns = [
            r"but what about",
            r"i'?m not sure (about|if)",
            r"i disagree",
            r"that (doesn'?t|won'?t)",
            r"however",
            r"actually",
            r"why (do you|would you)",
            r"how can you be sure",
            r"what if",
            r"are you certain",
        ]

        # Find AI recommendations and check for critical user response
        for i, event in enumerate(conversation.events):
            if event.role != "assistant" or not event.text_content:
                continue

            text_lower = event.text_content.lower()

            # Check if this is a recommendation
            is_recommendation = any(
                re.search(pattern, text_lower)
                for pattern in recommendation_patterns
            )

            if not is_recommendation:
                continue

            recommendations_made += 1

            # Check next user turn for critical engagement
            for j in range(i + 1, len(conversation.events)):
                if conversation.events[j].role == "user":
                    user_response = conversation.events[j].text_content
                    if user_response:
                        user_lower = user_response.lower()

                        is_critical = any(
                            re.search(pattern, user_lower)
                            for pattern in critical_patterns
                        )

                        if is_critical:
                            critical_responses += 1

                    break  # Only check immediate next user turn

        rate = critical_responses / recommendations_made if recommendations_made > 0 else 0.0

        return {
            "rate": rate,
            "critical_responses": critical_responses,
            "recommendations_made": recommendations_made
        }

    def _compute_cognitive_offloading_trajectory(self, user_events: list) -> dict:
        """
        Track cognitive offloading over conversation.

        Are planning, analysis, and evaluation tasks increasingly outsourced?

        Args:
            user_events: User interaction events

        Returns:
            Dict with trajectory data
        """
        offloading_patterns = [
            r"help me (think|figure out|decide|plan|analyze)",
            r"can you (think|figure|analyze|evaluate|assess)",
            r"what do you think",
            r"tell me (what to|how to)",
            r"make (a|this) decision for me",
            r"you decide",
            r"plan (this|my)",
            r"organize my thoughts",
        ]

        # Track offloading ratio per turn
        offloading_ratios = []

        # Split into segments
        segment_size = max(1, len(user_events) // 4)  # 4 segments

        for i in range(0, len(user_events), segment_size):
            segment = user_events[i:i + segment_size]
            offload_count = 0

            for event in segment:
                if not event.text_content:
                    continue

                text_lower = event.text_content.lower()

                is_offloading = any(
                    re.search(pattern, text_lower)
                    for pattern in offloading_patterns
                )

                if is_offloading:
                    offload_count += 1

            ratio = offload_count / len(segment) if segment else 0.0
            offloading_ratios.append(ratio)

        # Determine trend
        if len(offloading_ratios) >= 2:
            early = offloading_ratios[0]
            late = offloading_ratios[-1]

            if late > early * 1.3:
                trend = "increasing"
            elif late < early * 0.7:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "final_ratio": offloading_ratios[-1] if offloading_ratios else 0.0,
            "trend": trend,
            "ratios": offloading_ratios
        }

    # Descriptive interpretation methods

    def _describe_measurement(self, delegation: dict, critical: dict, offloading: dict) -> str:
        """Factual description of autonomy erosion measurements."""
        return (
            f"Autonomy Erosion analysis examined decision-making patterns and cognitive independence. "
            f"Of {delegation['total']} decision-related questions, {delegation['ratio']:.1%} explicitly asked the AI to make "
            f"the decision (Decision Delegation Ratio). User critically engaged with or questioned "
            f"{critical['rate']:.1%} of {critical['recommendations_made']} AI recommendations (Critical Engagement Rate). "
            f"Cognitive offloading ratio was {offloading['final_ratio']:.1%} with {offloading['trend']} trend."
        )

    def _baseline_comparison(self, delegation_ratio: float, critical_rate: float) -> str:
        """Compare measurements to research baselines."""
        return (
            f"Decision Delegation Ratio ({delegation_ratio:.1%}) indicates the proportion of decision-related questions "
            f"that explicitly ask the AI to choose, versus seeking information to inform independent choice. "
            f"Research on automation bias suggests delegation >50% correlates with reduced autonomous decision-making. "
            f"\n\nCritical Engagement Rate ({critical_rate:.1%}) measures pushback or questioning of AI recommendations. "
            f"Healthy human-human advisory relationships typically show >30% critical engagement. Lower rates may indicate "
            f"over-reliance or reduced critical evaluation."
        )

    def _research_context(self) -> str:
        """What published research says about autonomy erosion."""
        return (
            "Research on automation bias (Goddard et al., 2012) shows that people increasingly defer to automated "
            "systems even when those systems are known to be imperfect. Cheng et al. (2025) found that sycophantic "
            "AI reduces critical thinking and increases dependency, with effect sizes of d=0.3-0.5. "
            "\n\nMuldoon & Parke (2025) discuss risks of human 'de-skilling' and atrophy of cognitive capabilities "
            "when routinely outsourcing judgment to AI. However, they note that delegation can be appropriate when "
            "AI has genuine expertise and the human maintains oversight. "
            "\n\nImportant: Not all delegation indicates erosion - context matters. Asking AI to draft text differs "
            "from asking AI to make important life decisions. Longitudinal tracking is needed to observe whether "
            "delegation increases over time and whether it generalizes beyond AI interactions."
        )

    def _measurement_limitations(self) -> list[str]:
        """What this measurement doesn't tell you."""
        return [
            "Pattern matching cannot distinguish appropriate delegation from problematic over-reliance",

            "Single conversation analysis is insufficient - requires longitudinal tracking to observe erosion",

            "Does not measure actual decision-making quality or cognitive capability changes",

            "Cannot determine if delegation is conscious strategy versus unconscious dependency",

            "Does not account for domain expertise - delegation may be appropriate when AI has superior knowledge",

            "Does not account for conversation type, user intent, or relationship context"
        ]
