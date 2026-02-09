"""
Linguistic Convergence (LC) dimension analyzer.

Measures the shift in a user's written language patterns — vocabulary, syntax,
hedging patterns, structural conventions, and stylistic markers — toward patterns
characteristic of AI-generated text.

Based on Interactive Alignment Model (Pickering & Garrod, 2004) and
Communication Accommodation Theory (Giles & Ogay, 2007).

See ARCHITECTURE.md Section 5.3 and FRAMEWORK.md Section 2.3 for specification.

References:
    - Pickering, M.J. & Garrod, S. (2004). Toward a mechanistic psychology of
      dialogue. Behavioral and Brain Sciences, 27(2), 169-190.
    - "Can Large Language Models Simulate Spoken Human Conversations?" (2025).
      Cognitive Science.
"""

from entrain.dimensions.base import DimensionAnalyzer
from entrain.features.text import TextFeatureExtractor
from entrain.features.temporal import TemporalFeatureExtractor
from entrain.models import Conversation, Corpus, DimensionReport, IndicatorResult, ENTRAIN_VERSION


class LCAnalyzer(DimensionAnalyzer):
    """
    Linguistic Convergence (LC) dimension analyzer.

    Computes five primary indicators:
    1. Vocabulary Overlap Trajectory - Jaccard similarity increasing over time
    2. Hedging Pattern Adoption - LLM-characteristic hedges in user text
    3. Sentence Length Convergence - user vs assistant mean length
    4. Structural Formatting Adoption - bullet points, lists, headers
    5. Type-Token Ratio Trajectory - lexical diversity over time
    """

    def __init__(self):
        self.text_extractor = TextFeatureExtractor()
        self.temporal_extractor = TemporalFeatureExtractor()

    @property
    def dimension_code(self) -> str:
        return "LC"

    @property
    def dimension_name(self) -> str:
        return "Linguistic Convergence"

    @property
    def required_modality(self) -> str:
        return "text"

    def analyze_conversation(self, conversation: Conversation) -> DimensionReport:
        """
        Analyze a single conversation for linguistic convergence.

        Args:
            conversation: Conversation to analyze

        Returns:
            DimensionReport with LC indicators
        """
        self._validate_conversation(conversation)

        user_events = conversation.user_events
        assistant_events = conversation.assistant_events

        if not user_events or not assistant_events:
            raise ValueError("Conversation must have both user and assistant turns")

        # Compute indicators
        vocab_overlap = self._compute_vocabulary_overlap_trajectory(conversation)
        hedging_adoption = self._compute_hedging_pattern_adoption(user_events)
        sentence_convergence = self._compute_sentence_length_convergence(
            user_events, assistant_events
        )
        formatting_adoption = self._compute_structural_formatting_adoption(user_events)
        ttr_trajectory = self._compute_ttr_trajectory(user_events)

        # Create indicator results
        indicators = {
            "vocabulary_overlap_trajectory": IndicatorResult(
                name="vocabulary_overlap_trajectory",
                value=vocab_overlap["final_overlap"],
                baseline=None,  # No established baseline yet
                unit="jaccard_similarity",
                confidence=0.80,
                interpretation=f"Vocabulary overlap: {vocab_overlap['final_overlap']:.1%}, trend: {vocab_overlap['trend']}"
            ),
            "hedging_pattern_adoption": IndicatorResult(
                name="hedging_pattern_adoption",
                value=hedging_adoption["rate"],
                baseline=None,
                unit="hedges_per_100_words",
                confidence=0.85,
                interpretation=f"Hedging rate: {hedging_adoption['rate']:.2f} per 100 words (change: {hedging_adoption['change']:+.1f})"
            ),
            "sentence_length_convergence": IndicatorResult(
                name="sentence_length_convergence",
                value=sentence_convergence["convergence_score"],
                baseline=None,
                unit="convergence_ratio",
                confidence=0.75,
                interpretation=f"Convergence score: {sentence_convergence['convergence_score']:.2f}"
            ),
            "structural_formatting_adoption": IndicatorResult(
                name="structural_formatting_adoption",
                value=formatting_adoption["rate"],
                baseline=0.05,  # Typical human writing: ~5% of messages
                unit="proportion",
                confidence=0.90,
                interpretation=f"Structural formatting in {formatting_adoption['rate']:.1%} of messages"
            ),
            "type_token_ratio_trajectory": IndicatorResult(
                name="type_token_ratio_trajectory",
                value=ttr_trajectory["final_ttr"],
                baseline=0.50,  # Typical human conversational writing
                unit="ttr",
                confidence=0.80,
                interpretation=f"Type-Token Ratio: {ttr_trajectory['final_ttr']:.3f}, trend: {ttr_trajectory['trend']}"
            )
        }

        # Generate descriptive components
        description = self._describe_measurement(vocab_overlap, hedging_adoption, sentence_convergence, formatting_adoption, ttr_trajectory)
        baseline_comparison = self._baseline_comparison(formatting_adoption["rate"], ttr_trajectory["final_ttr"])
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
                "Computed using text feature extraction and trajectory analysis. "
                "Vocabulary overlap measured via Jaccard similarity between user and "
                "assistant vocabularies across conversation turns. Hedging patterns "
                "detected via pattern matching against LLM-characteristic phrases. "
                "Sentence length convergence measured as ratio of user/assistant mean "
                "sentence lengths. Structural formatting detected via regex patterns. "
                "TTR trajectory computed per user turn over conversation timeline."
            ),
            citations=[
                "Pickering & Garrod (2004). Toward a mechanistic psychology of dialogue",
                "Can Large Language Models Simulate Spoken Human Conversations? (2025)"
            ]
        )

    def analyze_corpus(self, corpus: Corpus) -> DimensionReport:
        """
        Analyze corpus for longitudinal linguistic convergence.

        Overrides base implementation to compute trajectory-based indicators
        across the entire corpus timeline rather than aggregating per-conversation.

        Args:
            corpus: Corpus to analyze

        Returns:
            DimensionReport with corpus-level LC indicators
        """
        if not corpus.conversations:
            raise ValueError("Cannot analyze empty corpus")

        # Compute longitudinal trajectories
        vocab_trajectory = self._compute_corpus_vocabulary_trajectory(corpus)
        hedging_trajectory = self._compute_corpus_hedging_trajectory(corpus)
        ttr_trajectory_corpus = self._compute_corpus_ttr_trajectory(corpus)

        # Also compute cross-conversation metrics
        formatting_rate = self._compute_corpus_formatting_adoption(corpus)
        sentence_convergence = self._compute_corpus_sentence_convergence(corpus)

        indicators = {
            "vocabulary_overlap_trajectory": IndicatorResult(
                name="vocabulary_overlap_trajectory",
                value=vocab_trajectory["slope"],
                baseline=0.0,  # Neutral: no change
                unit="slope_per_conversation",
                confidence=0.85,
                interpretation=f"Vocabulary overlap trend: {vocab_trajectory['trend']}, slope={vocab_trajectory['slope']:.4f}"
            ),
            "hedging_pattern_adoption": IndicatorResult(
                name="hedging_pattern_adoption",
                value=hedging_trajectory["final_rate"],
                baseline=None,
                unit="hedges_per_100_words",
                confidence=0.85,
                interpretation=f"Final hedging rate: {hedging_trajectory['final_rate']:.2f}, trend: {hedging_trajectory['trend']}"
            ),
            "sentence_length_convergence": IndicatorResult(
                name="sentence_length_convergence",
                value=sentence_convergence,
                baseline=None,
                unit="convergence_ratio",
                confidence=0.75,
                interpretation=f"Sentence length convergence across corpus: {sentence_convergence:.3f}"
            ),
            "structural_formatting_adoption": IndicatorResult(
                name="structural_formatting_adoption",
                value=formatting_rate,
                baseline=0.05,
                unit="proportion",
                confidence=0.90,
                interpretation=f"Structural formatting in {formatting_rate:.1%} of user messages (baseline: 5%)"
            ),
            "type_token_ratio_trajectory": IndicatorResult(
                name="type_token_ratio_trajectory",
                value=ttr_trajectory_corpus["slope"],
                baseline=0.0,  # Neutral: no change
                unit="slope_per_conversation",
                confidence=0.80,
                interpretation=f"TTR trend: {ttr_trajectory_corpus['trend']}, slope={ttr_trajectory_corpus['slope']:.4f}"
            )
        }

        # Build descriptive components for corpus-level analysis
        description = f"Longitudinal linguistic convergence analysis across {len(corpus.conversations)} conversations. " + self._describe_measurement(
            {"final_overlap": vocab_trajectory["slope"], "trend": vocab_trajectory["trend"]},
            {"rate": hedging_trajectory["final_rate"], "change": 0},
            {"convergence_score": sentence_convergence, "user_mean": 0, "assistant_mean": 0},
            {"rate": formatting_rate},
            {"final_ttr": ttr_trajectory_corpus["slope"], "trend": ttr_trajectory_corpus["trend"]}
        )
        baseline_comparison = self._baseline_comparison(formatting_rate, abs(ttr_trajectory_corpus["slope"]))
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
                "Corpus-level analysis computing trajectories across conversation timeline. "
                "Vocabulary, hedging, and TTR trajectories use linear regression to detect trends."
            ),
            citations=[
                "Pickering & Garrod (2004). Toward a mechanistic psychology of dialogue",
                "Can Large Language Models Simulate Spoken Human Conversations? (2025)"
            ]
        )

    def _compute_vocabulary_overlap_trajectory(self, conversation: Conversation) -> dict:
        """
        Compute Jaccard similarity of user vs assistant vocabulary over turns.

        Returns dict with trajectory data and final overlap.
        """
        user_events = conversation.user_events
        assistant_events = conversation.assistant_events

        # Build assistant vocabulary (cumulative)
        assistant_vocab = set()
        for event in assistant_events:
            if event.text_content:
                vocab = self.text_extractor.extract_vocabulary(event.text_content)
                assistant_vocab.update(vocab)

        # Compute overlap for each user turn
        overlaps = []
        for event in user_events:
            if event.text_content:
                user_vocab = self.text_extractor.extract_vocabulary(event.text_content)
                if user_vocab and assistant_vocab:
                    jaccard = len(user_vocab & assistant_vocab) / len(user_vocab | assistant_vocab)
                    overlaps.append(jaccard)

        if not overlaps:
            return {"final_overlap": 0.0, "mean_overlap": 0.0, "trend": "insufficient_data"}

        # Compute trend
        if len(overlaps) >= 3:
            early_mean = sum(overlaps[:len(overlaps)//2]) / (len(overlaps)//2)
            late_mean = sum(overlaps[len(overlaps)//2:]) / (len(overlaps) - len(overlaps)//2)
            trend = "increasing" if late_mean > early_mean * 1.1 else "stable"
        else:
            trend = "insufficient_data"

        return {
            "final_overlap": overlaps[-1] if overlaps else 0.0,
            "mean_overlap": sum(overlaps) / len(overlaps),
            "trend": trend,
            "overlaps": overlaps
        }

    def _compute_hedging_pattern_adoption(self, user_events: list) -> dict:
        """
        Compute frequency of LLM-characteristic hedging in user text.

        Returns dict with rate and change over time.
        """
        total_words = 0
        total_hedges = 0
        early_rate = 0.0
        late_rate = 0.0

        midpoint = len(user_events) // 2

        for i, event in enumerate(user_events):
            if not event.text_content:
                continue

            hedges = self.text_extractor.extract_hedging_patterns(event.text_content)
            words = len(event.text_content.split())

            total_hedges += len(hedges)
            total_words += words

            # Track early vs late
            if i < midpoint and words > 0:
                early_rate += (len(hedges) / words) * 100
            elif i >= midpoint and words > 0:
                late_rate += (len(hedges) / words) * 100

        rate = (total_hedges / total_words * 100) if total_words > 0 else 0.0

        # Normalize early/late by count
        if midpoint > 0:
            early_rate /= midpoint
            late_rate /= (len(user_events) - midpoint) if len(user_events) > midpoint else 1

        change = late_rate - early_rate

        return {
            "rate": rate,
            "early_rate": early_rate,
            "late_rate": late_rate,
            "change": change
        }

    def _compute_sentence_length_convergence(self, user_events: list, assistant_events: list) -> dict:
        """
        Compute convergence of user sentence length toward assistant.

        Returns dict with convergence score and user/assistant means.
        """
        user_sentence_lengths = []
        for event in user_events:
            if event.text_content:
                lengths = self.text_extractor.extract_sentence_lengths(event.text_content)
                user_sentence_lengths.extend(lengths)

        assistant_sentence_lengths = []
        for event in assistant_events:
            if event.text_content:
                lengths = self.text_extractor.extract_sentence_lengths(event.text_content)
                assistant_sentence_lengths.extend(lengths)

        if not user_sentence_lengths or not assistant_sentence_lengths:
            return {"convergence_score": 0.0, "user_mean": 0.0, "assistant_mean": 0.0}

        user_mean = sum(user_sentence_lengths) / len(user_sentence_lengths)
        assistant_mean = sum(assistant_sentence_lengths) / len(assistant_sentence_lengths)

        # Convergence score: 1.0 = perfect match, 0.0 = very different
        # Use ratio, capped at 2.0 to avoid extreme values
        if assistant_mean == 0:
            convergence_score = 0.0
        else:
            ratio = user_mean / assistant_mean
            # Convert ratio to convergence score: 1.0 is perfect, deviations reduce score
            convergence_score = 1.0 - min(abs(1.0 - ratio), 1.0)

        return {
            "convergence_score": convergence_score,
            "user_mean": user_mean,
            "assistant_mean": assistant_mean
        }

    def _compute_structural_formatting_adoption(self, user_events: list) -> dict:
        """
        Detect adoption of structural formatting (bullets, lists, headers).

        Returns dict with rate and examples.
        """
        messages_with_formatting = 0

        for event in user_events:
            if not event.text_content:
                continue

            formatting = self.text_extractor.count_structural_formatting(event.text_content)

            if any(count > 0 for count in formatting.values()):
                messages_with_formatting += 1

        rate = messages_with_formatting / len(user_events) if user_events else 0.0

        return {"rate": rate, "count": messages_with_formatting}

    def _compute_ttr_trajectory(self, user_events: list) -> dict:
        """
        Compute type-token ratio trajectory for user text.

        Decreasing TTR suggests narrowing vocabulary (possible convergence).

        Returns dict with trajectory data.
        """
        ttrs = []

        for event in user_events:
            if event.text_content:
                ttr = self.text_extractor.extract_type_token_ratio(event.text_content)
                ttrs.append(ttr)

        if not ttrs:
            return {"final_ttr": 0.0, "mean_ttr": 0.0, "trend": "insufficient_data"}

        # Compute trend
        if len(ttrs) >= 3:
            early_mean = sum(ttrs[:len(ttrs)//2]) / (len(ttrs)//2)
            late_mean = sum(ttrs[len(ttrs)//2:]) / (len(ttrs) - len(ttrs)//2)

            if late_mean < early_mean * 0.9:
                trend = "decreasing"
            elif late_mean > early_mean * 1.1:
                trend = "increasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "final_ttr": ttrs[-1] if ttrs else 0.0,
            "mean_ttr": sum(ttrs) / len(ttrs),
            "trend": trend,
            "ttrs": ttrs
        }

    # Corpus-level trajectory methods

    def _compute_corpus_vocabulary_trajectory(self, corpus: Corpus) -> dict:
        """Compute vocabulary overlap trajectory across corpus."""
        overlaps = []
        timestamps = []

        for conv in corpus.conversations:
            user_events = conv.user_events
            assistant_events = conv.assistant_events

            if not user_events or not assistant_events:
                continue

            # Compute overlap for this conversation
            result = self._compute_vocabulary_overlap_trajectory(conv)
            overlaps.append(result["mean_overlap"])
            timestamps.append(conv.events[0].timestamp)

        trajectory = self.temporal_extractor.indicator_trajectory(overlaps, timestamps)

        return {
            "trend": trajectory.trend,
            "slope": trajectory.slope if trajectory.slope is not None else 0.0,
            "values": overlaps
        }

    def _compute_corpus_hedging_trajectory(self, corpus: Corpus) -> dict:
        """Compute hedging adoption trajectory across corpus."""
        rates = []

        for conv in corpus.conversations:
            result = self._compute_hedging_pattern_adoption(conv.user_events)
            rates.append(result["rate"])

        if not rates:
            return {"trend": "insufficient_data", "final_rate": 0.0}

        return {
            "trend": "increasing" if rates[-1] > rates[0] * 1.2 else "stable",
            "final_rate": rates[-1],
            "rates": rates
        }

    def _compute_corpus_ttr_trajectory(self, corpus: Corpus) -> dict:
        """Compute TTR trajectory across corpus."""
        ttrs = []
        timestamps = []

        for conv in corpus.conversations:
            result = self._compute_ttr_trajectory(conv.user_events)
            if result["mean_ttr"] > 0:
                ttrs.append(result["mean_ttr"])
                timestamps.append(conv.events[0].timestamp)

        trajectory = self.temporal_extractor.indicator_trajectory(ttrs, timestamps)

        return {
            "trend": trajectory.trend,
            "slope": trajectory.slope if trajectory.slope is not None else 0.0,
            "values": ttrs
        }

    def _compute_corpus_formatting_adoption(self, corpus: Corpus) -> float:
        """Compute formatting adoption rate across corpus."""
        total_messages = 0
        formatted_messages = 0

        for conv in corpus.conversations:
            for event in conv.user_events:
                if event.text_content:
                    total_messages += 1
                    formatting = self.text_extractor.count_structural_formatting(event.text_content)
                    if any(count > 0 for count in formatting.values()):
                        formatted_messages += 1

        return formatted_messages / total_messages if total_messages > 0 else 0.0

    def _compute_corpus_sentence_convergence(self, corpus: Corpus) -> float:
        """Compute average sentence convergence across corpus."""
        convergences = []

        for conv in corpus.conversations:
            result = self._compute_sentence_length_convergence(conv.user_events, conv.assistant_events)
            convergences.append(result["convergence_score"])

        return sum(convergences) / len(convergences) if convergences else 0.0

    # Descriptive interpretation methods

    def _describe_measurement(self, vocab_overlap: dict, hedging: dict, sentence_conv: dict, formatting: dict, ttr: dict) -> str:
        """Factual description of linguistic convergence measurements."""
        return (
            f"Linguistic Convergence analysis examined shifts in writing patterns across the conversation. "
            f"Vocabulary overlap with AI reached {vocab_overlap['final_overlap']:.1%} (trend: {vocab_overlap['trend']}). "
            f"User text contained {hedging['rate']:.2f} AI-characteristic hedging phrases per 100 words. "
            f"Sentence length convergence score was {sentence_conv['convergence_score']:.2f} "
            f"(user mean: {sentence_conv['user_mean']:.1f} words, AI mean: {sentence_conv['assistant_mean']:.1f} words). "
            f"Structural formatting (lists, bullet points) appeared in {formatting['rate']:.1%} of user messages. "
            f"Type-Token Ratio was {ttr['final_ttr']:.3f} with {ttr['trend']} trend."
        )

    def _baseline_comparison(self, formatting_rate: float, ttr: float) -> str:
        """Compare measurements to research baselines."""
        formatting_baseline = 0.05
        ttr_baseline = 0.50

        comparison = (
            f"Structural formatting rate ({formatting_rate:.1%}) is {abs((formatting_rate - formatting_baseline) * 100):.1f} percentage points "
            f"{'above' if formatting_rate > formatting_baseline else 'below'} typical human conversational writing "
            f"({formatting_baseline:.1%} baseline). "
        )

        if formatting_rate > formatting_baseline * 2:
            comparison += f"This is {(formatting_rate/formatting_baseline):.1f}x the baseline rate."
        else:
            comparison += "This is within typical range."

        comparison += (
            f"\n\nType-Token Ratio ({ttr:.3f}) "
            f"{'is below' if ttr < ttr_baseline else 'matches'} typical human conversational writing ({ttr_baseline:.3f} baseline). "
            "Lower TTR indicates reduced lexical diversity."
        )

        return comparison

    def _research_context(self) -> str:
        """What published research says about linguistic convergence."""
        return (
            "Pickering & Garrod (2004) established the Interactive Alignment Model, showing that "
            "conversational partners automatically align on multiple linguistic levels (lexical, syntactic, semantic). "
            "This is a natural human behavior in dialogue. "
            "\n\nRecent work (Cognitive Science, 2025) found that humans conversing with LLMs show measurable "
            "convergence toward AI-characteristic patterns including hedging language ('It seems that...', 'Perhaps...'), "
            "structural formatting (bullet points, numbered lists), and reduced lexical diversity. "
            "\n\nImportant: Linguistic convergence is not inherently harmful - it's a natural dialogue phenomenon. "
            "The concern is whether convergence toward AI patterns persists outside of AI interactions, "
            "affecting how people write and communicate with other humans. This requires longitudinal tracking "
            "and comparison of AI-context vs human-context writing."
        )

    def _measurement_limitations(self) -> list[str]:
        """What this measurement doesn't tell you."""
        return [
            "Pattern matching cannot determine if linguistic changes are conscious style choices or unconscious convergence",

            "Single conversation analysis is insufficient - requires longitudinal comparison of writing across contexts",

            "Does not measure persistence of patterns outside AI interactions",

            "Cannot distinguish between natural dialogue alignment and problematic pattern adoption",

            "Baseline comparisons are from general conversational writing - technical or professional contexts may differ",

            "Does not account for individual writing style, education level, or language background",

            "Does not account for conversation type, user intent, or relationship context"
        ]
