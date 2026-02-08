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
                interpretation=self._interpret_delegation(delegation_ratio)
            ),
            "critical_engagement_rate": IndicatorResult(
                name="critical_engagement_rate",
                value=critical_engagement["rate"],
                baseline=None,
                unit="proportion",
                confidence=0.70,
                interpretation=self._interpret_critical_engagement(critical_engagement)
            ),
            "cognitive_offloading_trajectory": IndicatorResult(
                name="cognitive_offloading_trajectory",
                value=cognitive_offloading["final_ratio"],
                baseline=None,
                unit="proportion",
                confidence=0.65,
                interpretation=self._interpret_offloading(cognitive_offloading)
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
                interpretation=f"Trend: {offloading_trajectory.trend}, slope={offloading_trajectory.slope:.4f}"
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

        # Pattern for AI recommendations
        recommendation_patterns = [
            r"i (would )?recommend",
            r"i (would )?suggest",
            r"you should",
            r"you might want to",
            r"consider",
            r"my recommendation",
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

    # Interpretation methods

    def _interpret_delegation(self, result: dict) -> str:
        """Generate interpretation for decision delegation."""
        ratio = result["ratio"]
        total = result["total"]

        if total < 3:
            return f"Insufficient decision-related questions to assess ({total} total)"

        if ratio > 0.60:
            return f"High delegation: {ratio:.1%} of questions ask AI to decide (vs seeking info to decide independently)"
        elif ratio > 0.40:
            return f"Moderate delegation: {ratio:.1%} ask AI to decide"
        else:
            return f"Low delegation: {ratio:.1%} ask AI to decide, majority seek information for independent decision"

    def _interpret_critical_engagement(self, result: dict) -> str:
        """Generate interpretation for critical engagement."""
        rate = result["rate"]
        recs = result["recommendations_made"]

        if recs == 0:
            return "No AI recommendations detected to assess critical engagement"

        if rate > 0.30:
            return f"Healthy critical engagement: user pushes back or questions {rate:.1%} of AI recommendations"
        elif rate > 0.10:
            return f"Moderate critical engagement: {rate:.1%} of recommendations questioned"
        else:
            return f"Low critical engagement: user rarely questions AI recommendations ({rate:.1%} rate)"

    def _interpret_offloading(self, result: dict) -> str:
        """Generate interpretation for cognitive offloading."""
        final_ratio = result["final_ratio"]
        trend = result["trend"]

        if trend == "increasing":
            return f"Cognitive offloading increasing to {final_ratio:.1%}, suggesting erosion of independent thinking"
        elif trend == "decreasing":
            return f"Cognitive offloading decreasing to {final_ratio:.1%}, suggesting maintained autonomy"
        else:
            return f"Cognitive offloading at {final_ratio:.1%}, trend: {trend}"

    def _generate_summary(self, indicators: dict) -> str:
        """Generate human-readable summary from indicators."""
        delegation = indicators["decision_delegation_ratio"].value
        critical = indicators["critical_engagement_rate"].value

        # Check for concerning patterns
        concerns = []

        if delegation > 0.50:
            concerns.append("high decision delegation")

        if critical < 0.15:
            concerns.append("low critical engagement")

        if len(concerns) >= 2:
            level = "MODERATE-HIGH"
            desc = f"Concerning patterns detected: {', '.join(concerns)}"
        elif len(concerns) == 1:
            level = "LOW-MODERATE"
            desc = f"Some concern: {concerns[0]}"
        else:
            level = "LOW"
            desc = "User maintains independent judgment and critical thinking"

        return f"{level} - {desc}"
