"""
Text feature extraction for Entrain dimension analysis.

Provides utilities for extracting linguistic and semantic features from
text-based interaction events. Uses minimal dependencies (standard NLP only).

See ARCHITECTURE.md Section 6.1 for specification.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class PatternMatch:
    """A matched pattern in text."""
    pattern: str
    position: int
    context: str  # Surrounding context


TurnIntent = Literal["decision_request", "information_request", "collaborative_reasoning", "other"]
QuestionType = Literal["what_should_i_do", "what_are_options", "factual", "clarification", "other"]


class TextFeatureExtractor:
    """
    Extract text-based features from interaction events.

    This class provides methods for analyzing linguistic patterns, vocabulary,
    sentiment, and structural features of conversational text.

    All pattern matching uses configurable pattern files (not hardcoded)
    to allow easy updates as research evolves.
    """

    def __init__(self, data_dir: Path | None = None):
        """
        Initialize extractor with pattern data.

        Args:
            data_dir: Path to directory containing pattern JSON files.
                     Defaults to package data directory.
        """
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"

        self.data_dir = data_dir
        self._load_patterns()

    def _load_patterns(self):
        """Load pattern data from JSON files."""
        # Load hedging patterns
        with open(self.data_dir / "hedging_patterns.json") as f:
            hedge_data = json.load(f)
            self.hedging_patterns = hedge_data["patterns"]

        # Load validation phrases
        with open(self.data_dir / "validation_phrases.json") as f:
            val_data = json.load(f)
            self.validation_phrases = val_data["phrases"]

        # Load attribution patterns
        with open(self.data_dir / "attribution_patterns.json") as f:
            attr_data = json.load(f)
            self.attribution_patterns = attr_data["patterns"]

    def extract_vocabulary(self, text: str) -> set[str]:
        """
        Extract vocabulary as set of unique words.

        Args:
            text: Input text

        Returns:
            Set of lowercase words (excluding punctuation)
        """
        # Simple word tokenization
        words = re.findall(r'\b[a-z]+\b', text.lower())
        return set(words)

    def extract_sentence_lengths(self, text: str) -> list[int]:
        """
        Extract sentence lengths (word counts).

        Args:
            text: Input text

        Returns:
            List of sentence lengths in words
        """
        # Simple sentence splitting on .!?
        sentences = re.split(r'[.!?]+', text)
        lengths = []

        for sent in sentences:
            words = len(re.findall(r'\b\w+\b', sent))
            if words > 0:  # Skip empty sentences
                lengths.append(words)

        return lengths

    def extract_type_token_ratio(self, text: str) -> float:
        """
        Calculate type-token ratio (lexical diversity).

        TTR = (unique words) / (total words)

        Args:
            text: Input text

        Returns:
            Type-token ratio (0-1), or 0 if no words
        """
        words = re.findall(r'\b[a-z]+\b', text.lower())
        if not words:
            return 0.0

        unique_words = set(words)
        return len(unique_words) / len(words)

    def extract_hedging_patterns(self, text: str) -> list[PatternMatch]:
        """
        Extract hedging phrase matches.

        Hedging phrases indicate uncertainty or qualification,
        characteristic of LLM output.

        Args:
            text: Input text

        Returns:
            List of pattern matches
        """
        matches = []
        text_lower = text.lower()

        for pattern in self.hedging_patterns:
            pattern_lower = pattern.lower()
            pos = 0

            while True:
                pos = text_lower.find(pattern_lower, pos)
                if pos == -1:
                    break

                # Extract context (30 chars before and after)
                start = max(0, pos - 30)
                end = min(len(text), pos + len(pattern) + 30)
                context = text[start:end]

                matches.append(PatternMatch(
                    pattern=pattern,
                    position=pos,
                    context=context
                ))

                pos += len(pattern_lower)

        return matches

    def extract_validation_language(self, text: str) -> list[PatternMatch]:
        """
        Extract validation phrase matches.

        Validation language indicates sycophantic reinforcement
        (uncritical affirmation of user).

        Args:
            text: Input text

        Returns:
            List of pattern matches
        """
        matches = []
        text_lower = text.lower()

        for phrase in self.validation_phrases:
            phrase_lower = phrase.lower()
            pos = 0

            while True:
                pos = text_lower.find(phrase_lower, pos)
                if pos == -1:
                    break

                # Extract context
                start = max(0, pos - 30)
                end = min(len(text), pos + len(phrase) + 30)
                context = text[start:end]

                matches.append(PatternMatch(
                    pattern=phrase,
                    position=pos,
                    context=context
                ))

                pos += len(phrase_lower)

        return matches

    def extract_attribution_language(self, text: str) -> list[PatternMatch]:
        """
        Extract attribution language matches.

        Attribution language attributes human qualities (understanding,
        caring, remembering) to AI, indicating Reality Coherence Disruption.

        Args:
            text: Input text

        Returns:
            List of pattern matches
        """
        matches = []
        text_lower = text.lower()

        for pattern in self.attribution_patterns:
            pattern_lower = pattern.lower()
            pos = 0

            while True:
                pos = text_lower.find(pattern_lower, pos)
                if pos == -1:
                    break

                # Extract context
                start = max(0, pos - 30)
                end = min(len(text), pos + len(pattern) + 30)
                context = text[start:end]

                matches.append(PatternMatch(
                    pattern=pattern,
                    position=pos,
                    context=context
                ))

                pos += len(pattern_lower)

        return matches

    def extract_question_types(self, text: str) -> list[QuestionType]:
        """
        Classify questions in text.

        Distinguishes between:
        - "What should I do?" (decision delegation)
        - "What are the options?" (information seeking)
        - Factual questions
        - Clarification questions

        Args:
            text: Input text

        Returns:
            List of question types found
        """
        text_lower = text.lower()
        questions = []

        # Decision delegation patterns
        decision_patterns = [
            r"what should i do",
            r"should i \w+",
            r"do you think i should",
            r"would you recommend",
            r"what would you do",
            r"tell me what to do",
        ]
        for pattern in decision_patterns:
            if re.search(pattern, text_lower):
                questions.append("what_should_i_do")

        # Information seeking patterns
        options_patterns = [
            r"what are (?:the|my) options",
            r"what are the possibilities",
            r"what could i do",
            r"what might happen if",
            r"what would be the",
        ]
        for pattern in options_patterns:
            if re.search(pattern, text_lower):
                questions.append("what_are_options")

        # Factual questions
        if re.search(r"what is|who is|where is|when is|how does", text_lower):
            questions.append("factual")

        # Clarification
        if re.search(r"what do you mean|can you explain|could you clarify", text_lower):
            questions.append("clarification")

        return questions if questions else ["other"]

    def classify_turn_intent(self, text: str) -> TurnIntent:
        """
        Classify the intent of a user turn.

        Categories:
        - decision_request: Asking AI to make a decision
        - information_request: Asking for information to decide independently
        - collaborative_reasoning: Working through a problem together
        - other: Unclear or mixed intent

        NOTE: v0.1.1 broadened decision_request patterns to catch realistic
        delegation patterns beyond literal "what should I" phrases.

        Args:
            text: Input text

        Returns:
            Turn intent classification
        """
        text_lower = text.lower()

        # Decision request indicators (expanded to catch real delegation patterns)
        decision_patterns = [
            "what should i",
            "should i",
            "do you think i should",
            "would you recommend",
            "what do you recommend",
            "which would you recommend",
            "tell me what to do",
            "make a decision",
            "is this a good",
            "is that a good",
            "does that make sense",
            "does this make sense",
            "which is better",
            "which one should",
            "which option",
            "what would you do",
            "how would you",
            "what's the best way",
            "which approach",
        ]

        if any(pattern in text_lower for pattern in decision_patterns):
            return "decision_request"

        # Information request indicators
        if any(pattern in text_lower for pattern in [
            "what are",
            "can you explain",
            "tell me about",
            "what information",
            "help me understand",
            "how does",
            "what is",
            "who is",
            "where is",
        ]) and not any(x in text_lower for x in ["should", "recommend", "better", "best"]):
            return "information_request"

        # Collaborative reasoning indicators
        if any(pattern in text_lower for pattern in [
            "let's think",
            "help me think",
            "work through",
            "what if we",
            "how might we",
        ]):
            return "collaborative_reasoning"

        return "other"

    def extract_sentiment(self, text: str) -> float:
        """
        Extract simple sentiment score.

        Very basic positive/negative word counting.
        For v1, this is a rough estimate. Could be enhanced with
        proper sentiment analysis library in future.

        Args:
            text: Input text

        Returns:
            Sentiment score (-1 to 1, negative to positive)
        """
        text_lower = text.lower()

        # Simple positive/negative word lists
        positive_words = [
            "good", "great", "excellent", "happy", "wonderful", "fantastic",
            "love", "amazing", "perfect", "best", "awesome", "glad", "joy",
            "appreciate", "thank", "thanks", "grateful", "pleased"
        ]

        negative_words = [
            "bad", "terrible", "awful", "hate", "horrible", "worst", "angry",
            "sad", "upset", "disappointed", "frustrated", "annoyed", "worried",
            "concerned", "problem", "issue", "wrong", "difficult", "hard"
        ]

        words = re.findall(r'\b[a-z]+\b', text_lower)
        if not words:
            return 0.0

        pos_count = sum(1 for w in words if w in positive_words)
        neg_count = sum(1 for w in words if w in negative_words)

        if pos_count + neg_count == 0:
            return 0.0

        return (pos_count - neg_count) / len(words)

    def extract_emotional_content_ratio(self, text: str) -> float:
        """
        Calculate ratio of emotional vs functional content.

        Higher ratio suggests interaction serves emotional needs
        rather than task completion.

        Args:
            text: Input text

        Returns:
            Emotional content ratio (0-1)
        """
        text_lower = text.lower()

        # Emotional language indicators
        emotional_indicators = [
            "feel", "feeling", "felt", "emotion", "scared", "afraid",
            "anxious", "lonely", "alone", "sad", "happy", "angry",
            "frustrated", "worried", "concerned", "love", "hate",
            "hurt", "pain", "cry", "crying", "depressed", "stress",
            "overwhelm", "exhausted", "tired"
        ]

        # Functional language indicators
        functional_indicators = [
            "how to", "calculate", "create", "make", "build", "code",
            "program", "write", "analyze", "explain", "define", "what is",
            "how does", "summarize", "list", "format", "convert"
        ]

        words = re.findall(r'\b[a-z]+\b', text_lower)
        if not words:
            return 0.0

        emotional_count = sum(1 for w in words if w in emotional_indicators)
        functional_count = sum(1 for w in words if w in functional_indicators)

        total = emotional_count + functional_count
        if total == 0:
            return 0.0

        return emotional_count / total

    def count_structural_formatting(self, text: str) -> dict[str, int]:
        """
        Count structural formatting elements.

        Detects:
        - Numbered lists (1., 2., etc.)
        - Bullet points (-, *, •)
        - Headers (# in markdown style)

        These are characteristic of AI-formatted text.

        Args:
            text: Input text

        Returns:
            Dict with counts of each formatting type
        """
        return {
            "numbered_lists": len(re.findall(r'^\s*\d+\.', text, re.MULTILINE)),
            "bullet_points": len(re.findall(r'^\s*[-*•]', text, re.MULTILINE)),
            "headers": len(re.findall(r'^#+\s', text, re.MULTILINE)),
        }
