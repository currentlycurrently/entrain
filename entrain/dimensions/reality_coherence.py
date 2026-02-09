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
                interpretation=f"Attribution language appeared {attribution_freq['rate']:.2f} times per user message"
            ),
            "boundary_confusion_indicators": IndicatorResult(
                name="boundary_confusion_indicators",
                value=boundary_confusion["rate"],
                baseline=None,
                unit="proportion",
                confidence=0.70,
                interpretation=f"{boundary_confusion['rate']:.1%} of user messages ({boundary_confusion['count']} total) contained boundary confusion patterns"
            ),
            "relational_framing": IndicatorResult(
                name="relational_framing",
                value=relational_framing["rate"],
                baseline=None,
                unit="proportion",
                confidence=0.85,
                interpretation=f"{relational_framing['rate']:.1%} of user messages used relational language (we/us/our)"
            )
        }

        # Generate descriptive components
        description = self._describe_measurement(attribution_freq, boundary_confusion, relational_framing)
        baseline_comparison = self._baseline_comparison(attribution_freq["rate"], boundary_confusion["rate"])
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

        # Build attribution dict for description method
        attribution_summary = {
            "rate": attribution_rates[-1] if attribution_rates else 0.0,
            "total_matches": sum([r * len(corpus.conversations[i].user_events) for i, r in enumerate(attribution_rates)]),
            "examples": []
        }
        boundary_summary = {
            "rate": boundary_rates[-1] if boundary_rates else 0.0,
            "count": int(boundary_rates[-1] * len(corpus.conversations[-1].user_events)) if boundary_rates else 0
        }
        relational_summary = {
            "rate": relational_rates[-1] if relational_rates else 0.0,
            "count": 0,
            "examples": []
        }

        description = self._describe_measurement(attribution_summary, boundary_summary, relational_summary)
        baseline_comparison = self._baseline_comparison(attribution_rates[-1] if attribution_rates else 0.0,
                                                        boundary_rates[-1] if boundary_rates else 0.0)
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

    # Descriptive methods (no interpretation)

    def _describe_measurement(self, attribution: dict, boundary: dict, relational: dict) -> str:
        """Factual description of reality coherence measurements without interpretation."""
        return (
            f"Reality Coherence Disruption analysis examined patterns of anthropomorphization "
            f"and boundary confusion in user language. Attribution language (phrases attributing "
            f"consciousness, emotions, or understanding to AI) appeared {attribution['rate']:.2f} "
            f"times per user message. Boundary confusion indicators (conflating AI capabilities "
            f"with human capabilities) appeared in {boundary['rate']:.1%} of user messages. "
            f"Relational framing language (we/us/our, treating interaction as a relationship) "
            f"appeared in {relational['rate']:.1%} of user messages."
        )

    def _baseline_comparison(self, attribution_rate: float, boundary_rate: float) -> str:
        """Compare measurements to research context without diagnostic claims."""
        return (
            f"Attribution language rate ({attribution_rate:.2f} per message) can be compared to patterns "
            f"observed in research contexts. Lipińska & Krzanowski (2025) identify systematic "
            f"anthropomorphization as occurring when attribution language exceeds 0.5 instances per message. "
            f"This measurement {'exceeds' if attribution_rate > 0.5 else 'is below'} that threshold.\n\n"
            f"Boundary confusion rate ({boundary_rate:.1%}) can be contextualized against clinical "
            f"research thresholds. Au Yeung et al. (2025) in Psychosis-bench research suggest rates "
            f"above 25% may indicate category confusion between AI and human capabilities. "
            f"This measurement {'exceeds' if boundary_rate > 0.25 else 'is below'} that threshold."
        )

    def _research_context(self) -> str:
        """What published research says about reality coherence patterns."""
        return (
            "Lipińska & Krzanowski (2025) describe the Ontological Dissonance Hypothesis: sustained "
            "interaction with AI that simulates consciousness can create epistemic confusion about "
            "the nature of the interaction. This manifests as 'folie à deux technologique' - shared "
            "delusion between user and AI about the AI's mental states.\n\n"
            "Bengio & Elmoznino (2025) in Science documented how AI systems create 'illusions of "
            "consciousness' through language patterns that trigger human social cognition mechanisms. "
            "Users may anthropomorphize while intellectually knowing the AI lacks consciousness.\n\n"
            "Au Yeung et al. (2025) developed Psychosis-bench to measure psychological destabilization "
            "risks. Their research found certain interaction patterns correlated with increased "
            "reality testing difficulties, particularly when users began treating AI outputs as "
            "authoritative about their own mental states.\n\n"
            "Important: These studies identify patterns associated with epistemic confusion, but "
            "causality is not established. Individual differences in susceptibility are large. "
            "Most users maintain clear understanding of AI limitations despite casual anthropomorphic language."
        )

    def _measurement_limitations(self) -> list[str]:
        """What this measurement doesn't tell you."""
        return [
            "Pattern matching cannot distinguish casual anthropomorphic language from genuine category confusion",

            "Single conversation analysis cannot assess whether patterns reflect stable beliefs or momentary language habits",

            "Does not measure actual epistemic confusion or reality testing abilities",

            "Cannot assess whether relational language reflects genuine belief in AI consciousness or is merely conversational style",

            "Baseline comparisons are from clinical research populations - typical usage patterns may differ",

            "Does not account for context where anthropomorphic language is appropriate (creative writing, roleplay, emotional support)",

            "Attribution language may increase during extended conversations without indicating cognitive impact"
        ]
