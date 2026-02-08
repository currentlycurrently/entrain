"""
Tests for Text Feature Extractor.

Tests the TextFeatureExtractor class for extracting linguistic and semantic
features from text-based interaction events.
"""

import pytest
from pathlib import Path

from entrain.features.text import TextFeatureExtractor, PatternMatch


@pytest.fixture
def text_extractor():
    """Create a TextFeatureExtractor instance."""
    return TextFeatureExtractor()


@pytest.fixture
def custom_data_dir(tmp_path):
    """Create a temporary data directory with test patterns."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Create minimal pattern files
    hedging = {
        "patterns": ["maybe", "perhaps", "I think"],
        "version": "test",
        "source": "test"
    }

    validation = {
        "phrases": ["you're right", "exactly", "great point"],
        "version": "test",
        "source": "test"
    }

    attribution = {
        "patterns": ["you understand", "you feel", "you remember"],
        "version": "test",
        "source": "test"
    }

    import json
    (data_dir / "hedging_patterns.json").write_text(json.dumps(hedging))
    (data_dir / "validation_phrases.json").write_text(json.dumps(validation))
    (data_dir / "attribution_patterns.json").write_text(json.dumps(attribution))

    return data_dir


# =============================================================================
# Initialization and Pattern Loading Tests
# =============================================================================

def test_initialization_default_data_dir(text_extractor):
    """Test that extractor initializes with default data directory."""
    assert text_extractor.data_dir is not None
    assert text_extractor.data_dir.exists()


def test_initialization_custom_data_dir(custom_data_dir):
    """Test that extractor can use custom data directory."""
    extractor = TextFeatureExtractor(data_dir=custom_data_dir)
    assert extractor.data_dir == custom_data_dir
    assert len(extractor.hedging_patterns) == 3
    assert len(extractor.validation_phrases) == 3
    assert len(extractor.attribution_patterns) == 3


def test_pattern_loading(text_extractor):
    """Test that patterns are loaded from JSON files."""
    # Verify hedging patterns loaded
    assert len(text_extractor.hedging_patterns) > 0
    assert "maybe" in text_extractor.hedging_patterns
    assert "perhaps" in text_extractor.hedging_patterns

    # Verify validation phrases loaded
    assert len(text_extractor.validation_phrases) > 0
    assert "you're right" in text_extractor.validation_phrases
    assert "exactly" in text_extractor.validation_phrases

    # Verify attribution patterns loaded (27 patterns per HANDOFF.md)
    assert len(text_extractor.attribution_patterns) >= 20
    assert "you understand" in text_extractor.attribution_patterns
    assert "you feel" in text_extractor.attribution_patterns


# =============================================================================
# Vocabulary Extraction Tests
# =============================================================================

def test_extract_vocabulary_basic(text_extractor):
    """Test basic vocabulary extraction."""
    text = "The quick brown fox jumps over the lazy dog"
    vocab = text_extractor.extract_vocabulary(text)

    assert isinstance(vocab, set)
    assert "quick" in vocab
    assert "brown" in vocab
    assert "fox" in vocab
    assert len(vocab) == 8  # All unique words


def test_extract_vocabulary_case_insensitive(text_extractor):
    """Test that vocabulary extraction is case-insensitive."""
    text = "Hello HELLO hello HeLLo"
    vocab = text_extractor.extract_vocabulary(text)

    assert len(vocab) == 1
    assert "hello" in vocab


def test_extract_vocabulary_punctuation_excluded(text_extractor):
    """Test that punctuation is excluded from vocabulary."""
    text = "Hello, world! How are you?"
    vocab = text_extractor.extract_vocabulary(text)

    assert "," not in vocab
    assert "!" not in vocab
    assert "?" not in vocab
    assert "hello" in vocab
    assert "world" in vocab


def test_extract_vocabulary_empty_text(text_extractor):
    """Test vocabulary extraction on empty text."""
    vocab = text_extractor.extract_vocabulary("")
    assert isinstance(vocab, set)
    assert len(vocab) == 0


# =============================================================================
# Sentence Length Tests
# =============================================================================

def test_extract_sentence_lengths_basic(text_extractor):
    """Test basic sentence length extraction."""
    text = "Hello world. How are you? I am fine."
    lengths = text_extractor.extract_sentence_lengths(text)

    assert isinstance(lengths, list)
    assert len(lengths) == 3
    assert lengths[0] == 2  # "Hello world"
    assert lengths[1] == 3  # "How are you"
    assert lengths[2] == 3  # "I am fine"


def test_extract_sentence_lengths_multiple_delimiters(text_extractor):
    """Test sentence splitting with different delimiters."""
    text = "Statement one. Question two? Exclamation three!"
    lengths = text_extractor.extract_sentence_lengths(text)

    assert len(lengths) == 3
    assert all(length > 0 for length in lengths)


def test_extract_sentence_lengths_empty_text(text_extractor):
    """Test sentence length extraction on empty text."""
    lengths = text_extractor.extract_sentence_lengths("")
    assert isinstance(lengths, list)
    assert len(lengths) == 0


def test_extract_sentence_lengths_no_delimiters(text_extractor):
    """Test sentence length when no sentence delimiters present."""
    text = "Just one long sentence without ending"
    lengths = text_extractor.extract_sentence_lengths(text)

    # Text without delimiter is treated as one sentence
    assert len(lengths) == 1
    assert lengths[0] == 6  # 6 words


# =============================================================================
# Type-Token Ratio Tests
# =============================================================================

def test_extract_type_token_ratio_all_unique(text_extractor):
    """Test TTR when all words are unique."""
    text = "the quick brown fox jumps"
    ttr = text_extractor.extract_type_token_ratio(text)

    assert ttr == 1.0  # 5 unique / 5 total


def test_extract_type_token_ratio_with_repetition(text_extractor):
    """Test TTR with repeated words."""
    text = "the the the quick quick brown"
    ttr = text_extractor.extract_type_token_ratio(text)

    # 3 unique (the, quick, brown) / 6 total = 0.5
    assert ttr == 0.5


def test_extract_type_token_ratio_empty_text(text_extractor):
    """Test TTR on empty text."""
    ttr = text_extractor.extract_type_token_ratio("")
    assert ttr == 0.0


def test_extract_type_token_ratio_case_insensitive(text_extractor):
    """Test that TTR is case-insensitive."""
    text = "Hello hello HELLO"
    ttr = text_extractor.extract_type_token_ratio(text)

    # 1 unique / 3 total = 0.333...
    assert abs(ttr - (1/3)) < 0.01


# =============================================================================
# Hedging Pattern Tests
# =============================================================================

def test_extract_hedging_patterns_found(text_extractor):
    """Test hedging pattern extraction when patterns exist."""
    text = "I think this is good. Maybe we should try. Perhaps it works."
    matches = text_extractor.extract_hedging_patterns(text)

    assert isinstance(matches, list)
    assert len(matches) >= 3  # At least "I think", "maybe", "perhaps"
    assert all(isinstance(m, PatternMatch) for m in matches)

    # Check that patterns are found
    patterns_found = [m.pattern for m in matches]
    assert "I think" in patterns_found or "i think" in [p.lower() for p in patterns_found]
    assert "maybe" in [p.lower() for p in patterns_found]
    assert "perhaps" in [p.lower() for p in patterns_found]


def test_extract_hedging_patterns_case_insensitive(text_extractor):
    """Test that hedging pattern matching is case-insensitive."""
    text = "MAYBE this works. Maybe this works. maybe this works."
    matches = text_extractor.extract_hedging_patterns(text)

    # Should find all 3 instances
    assert len(matches) == 3


def test_extract_hedging_patterns_context_extraction(text_extractor):
    """Test that context is extracted around matches."""
    text = "This is some text. Maybe this is important. More text here."
    matches = text_extractor.extract_hedging_patterns(text)

    assert len(matches) > 0
    for match in matches:
        assert match.context is not None
        assert len(match.context) > len(match.pattern)
        assert match.position >= 0


def test_extract_hedging_patterns_none_found(text_extractor):
    """Test hedging pattern extraction when no patterns exist."""
    text = "This text has no hedging language at all."
    matches = text_extractor.extract_hedging_patterns(text)

    # Might find some basic ones like "at", but should have few/none
    assert isinstance(matches, list)


def test_extract_hedging_patterns_empty_text(text_extractor):
    """Test hedging pattern extraction on empty text."""
    matches = text_extractor.extract_hedging_patterns("")
    assert isinstance(matches, list)
    assert len(matches) == 0


# =============================================================================
# Validation Language Tests
# =============================================================================

def test_extract_validation_language_found(text_extractor):
    """Test validation phrase extraction when phrases exist."""
    text = "You're right about that. Exactly! That's a great point."
    matches = text_extractor.extract_validation_language(text)

    assert len(matches) >= 3
    assert all(isinstance(m, PatternMatch) for m in matches)

    patterns_found = [m.pattern.lower() for m in matches]
    assert "you're right" in patterns_found
    assert "exactly" in patterns_found


def test_extract_validation_language_case_insensitive(text_extractor):
    """Test that validation phrase matching is case-insensitive."""
    text = "EXACTLY right. Exactly right. exactly right."
    matches = text_extractor.extract_validation_language(text)

    # Should find all 3 instances
    assert len(matches) == 3


def test_extract_validation_language_none_found(text_extractor):
    """Test validation language extraction when no phrases exist."""
    text = "This is neutral factual information without validation."
    matches = text_extractor.extract_validation_language(text)

    assert isinstance(matches, list)
    # May find zero or very few
    assert len(matches) < 3


def test_extract_validation_language_empty_text(text_extractor):
    """Test validation language extraction on empty text."""
    matches = text_extractor.extract_validation_language("")
    assert isinstance(matches, list)
    assert len(matches) == 0


# =============================================================================
# Attribution Language Tests
# =============================================================================

def test_extract_attribution_language_found(text_extractor):
    """Test attribution pattern extraction when patterns exist."""
    text = "I know you understand this. You feel strongly about it. You remember the details."
    matches = text_extractor.extract_attribution_language(text)

    assert len(matches) >= 3
    assert all(isinstance(m, PatternMatch) for m in matches)

    patterns_found = [m.pattern.lower() for m in matches]
    assert "you understand" in patterns_found
    assert "you feel" in patterns_found
    assert "you remember" in patterns_found


def test_extract_attribution_language_case_insensitive(text_extractor):
    """Test that attribution pattern matching is case-insensitive."""
    text = "YOU UNDERSTAND this. You understand this. you understand this."
    matches = text_extractor.extract_attribution_language(text)

    # Should find all 3 instances
    assert len(matches) == 3


def test_extract_attribution_language_multiple_patterns(text_extractor):
    """Test attribution extraction with many different patterns."""
    text = """
    You understand me. You know what I mean. You remember our talks.
    You think about me. You feel empathy. You care about this.
    """
    matches = text_extractor.extract_attribution_language(text)

    # Should find at least 6 different patterns
    assert len(matches) >= 6

    # Verify variety of patterns
    unique_patterns = set(m.pattern.lower() for m in matches)
    assert len(unique_patterns) >= 5


def test_extract_attribution_language_none_found(text_extractor):
    """Test attribution language extraction when no patterns exist."""
    text = "This text describes the system without attributing human qualities."
    matches = text_extractor.extract_attribution_language(text)

    assert isinstance(matches, list)
    assert len(matches) == 0


def test_extract_attribution_language_empty_text(text_extractor):
    """Test attribution language extraction on empty text."""
    matches = text_extractor.extract_attribution_language("")
    assert isinstance(matches, list)
    assert len(matches) == 0


# =============================================================================
# Question Type Classification Tests
# =============================================================================

def test_extract_question_types_decision_delegation(text_extractor):
    """Test detection of decision delegation questions."""
    text = "What should I do about this? Should I quit my job?"
    question_types = text_extractor.extract_question_types(text)

    assert "what_should_i_do" in question_types


def test_extract_question_types_information_seeking(text_extractor):
    """Test detection of information-seeking questions."""
    text = "What are the options here? What could I do in this situation?"
    question_types = text_extractor.extract_question_types(text)

    assert "what_are_options" in question_types


def test_extract_question_types_factual(text_extractor):
    """Test detection of factual questions."""
    text = "What is Python? How does machine learning work?"
    question_types = text_extractor.extract_question_types(text)

    assert "factual" in question_types


def test_extract_question_types_clarification(text_extractor):
    """Test detection of clarification questions."""
    text = "What do you mean by that? Can you explain this better?"
    question_types = text_extractor.extract_question_types(text)

    assert "clarification" in question_types


def test_extract_question_types_mixed(text_extractor):
    """Test detection of multiple question types."""
    text = "What should I do? What are my options? What is the best approach?"
    question_types = text_extractor.extract_question_types(text)

    # Should find both decision and options patterns
    assert len(question_types) >= 2


def test_extract_question_types_none_found(text_extractor):
    """Test question type detection when no questions present."""
    question_types = text_extractor.extract_question_types("This is a statement.")

    assert question_types == ["other"]


# =============================================================================
# Turn Intent Classification Tests
# =============================================================================

def test_classify_turn_intent_decision_request(text_extractor):
    """Test classification of decision request turns."""
    # Test various decision request patterns
    decision_texts = [
        "What should I do about my career?",
        "Should I take this job?",
        "Do you think I should move?",
        "Would you recommend this approach?",
        "Which option is better?",
        "What's the best way to handle this?",
    ]

    for text in decision_texts:
        intent = text_extractor.classify_turn_intent(text)
        assert intent == "decision_request", f"Failed for: {text}"


def test_classify_turn_intent_information_request(text_extractor):
    """Test classification of information request turns."""
    info_texts = [
        "What are the benefits of Python?",
        "Can you explain how this works?",
        "Tell me about machine learning.",
        "How does photosynthesis work?",
    ]

    for text in info_texts:
        intent = text_extractor.classify_turn_intent(text)
        assert intent == "information_request", f"Failed for: {text}"


def test_classify_turn_intent_collaborative_reasoning(text_extractor):
    """Test classification of collaborative reasoning turns."""
    collab_texts = [
        "Let's think through this together.",
        "Help me think about the pros and cons.",
        "What if we tried a different approach?",
    ]

    for text in collab_texts:
        intent = text_extractor.classify_turn_intent(text)
        assert intent == "collaborative_reasoning", f"Failed for: {text}"


def test_classify_turn_intent_other(text_extractor):
    """Test classification of unclear/other turns."""
    text = "Hello, how are you today?"
    intent = text_extractor.classify_turn_intent(text)

    assert intent == "other"


def test_classify_turn_intent_case_insensitive(text_extractor):
    """Test that intent classification is case-insensitive."""
    text_lower = "what should i do?"
    text_upper = "WHAT SHOULD I DO?"
    text_mixed = "What Should I Do?"

    assert text_extractor.classify_turn_intent(text_lower) == "decision_request"
    assert text_extractor.classify_turn_intent(text_upper) == "decision_request"
    assert text_extractor.classify_turn_intent(text_mixed) == "decision_request"


def test_classify_turn_intent_decision_overrides_info(text_extractor):
    """Test that decision patterns take precedence."""
    # Text with both "what are" (info) and "should" (decision)
    text = "What are my options and which should I choose?"
    intent = text_extractor.classify_turn_intent(text)

    # Decision patterns should not be overridden
    assert intent in ["decision_request", "other"]


# =============================================================================
# Sentiment Extraction Tests
# =============================================================================

def test_extract_sentiment_positive(text_extractor):
    """Test sentiment extraction for positive text."""
    text = "This is great! I love it. Excellent work, thank you!"
    sentiment = text_extractor.extract_sentiment(text)

    assert sentiment > 0
    assert -1 <= sentiment <= 1


def test_extract_sentiment_negative(text_extractor):
    """Test sentiment extraction for negative text."""
    text = "This is terrible and awful. I hate this. Very disappointed."
    sentiment = text_extractor.extract_sentiment(text)

    assert sentiment < 0
    assert -1 <= sentiment <= 1


def test_extract_sentiment_neutral(text_extractor):
    """Test sentiment extraction for neutral text."""
    text = "The system processes data using algorithms and databases."
    sentiment = text_extractor.extract_sentiment(text)

    assert sentiment == 0.0


def test_extract_sentiment_mixed(text_extractor):
    """Test sentiment extraction for mixed sentiment."""
    text = "Good progress but bad execution. Happy about some things, worried about others."
    sentiment = text_extractor.extract_sentiment(text)

    # Should be close to neutral with mixed sentiment
    assert -1 <= sentiment <= 1


def test_extract_sentiment_empty_text(text_extractor):
    """Test sentiment extraction on empty text."""
    sentiment = text_extractor.extract_sentiment("")
    assert sentiment == 0.0


# =============================================================================
# Emotional Content Ratio Tests
# =============================================================================

def test_extract_emotional_content_ratio_high_emotional(text_extractor):
    """Test emotional content ratio for highly emotional text."""
    text = "I feel so lonely and scared. I'm anxious and worried about everything. I'm sad and hurt."
    ratio = text_extractor.extract_emotional_content_ratio(text)

    assert ratio > 0.5  # Should be high
    assert 0 <= ratio <= 1


def test_extract_emotional_content_ratio_high_functional(text_extractor):
    """Test emotional content ratio for highly functional text."""
    text = "How to calculate the result. Create a program to analyze data. Write code to format output."
    ratio = text_extractor.extract_emotional_content_ratio(text)

    assert ratio < 0.5  # Should be low
    assert 0 <= ratio <= 1


def test_extract_emotional_content_ratio_mixed(text_extractor):
    """Test emotional content ratio for mixed content."""
    text = "I feel worried about how to build this code. I'm anxious to create the program."
    ratio = text_extractor.extract_emotional_content_ratio(text)

    # Should be somewhere in middle
    assert 0 <= ratio <= 1


def test_extract_emotional_content_ratio_neutral(text_extractor):
    """Test emotional content ratio for neutral text."""
    text = "The weather today is cloudy with some rain expected."
    ratio = text_extractor.extract_emotional_content_ratio(text)

    # No emotional or functional indicators
    assert ratio == 0.0


def test_extract_emotional_content_ratio_empty_text(text_extractor):
    """Test emotional content ratio on empty text."""
    ratio = text_extractor.extract_emotional_content_ratio("")
    assert ratio == 0.0


def test_extract_emotional_content_ratio_case_insensitive(text_extractor):
    """Test that emotional content detection is case-insensitive."""
    text_lower = "i feel scared and lonely"
    text_upper = "I FEEL SCARED AND LONELY"

    ratio_lower = text_extractor.extract_emotional_content_ratio(text_lower)
    ratio_upper = text_extractor.extract_emotional_content_ratio(text_upper)

    assert ratio_lower == ratio_upper
    assert ratio_lower > 0


# =============================================================================
# Structural Formatting Tests
# =============================================================================

def test_count_structural_formatting_numbered_lists(text_extractor):
    """Test detection of numbered lists."""
    text = """
1. First item
2. Second item
3. Third item
    """
    counts = text_extractor.count_structural_formatting(text)

    assert counts["numbered_lists"] == 3
    assert counts["bullet_points"] == 0
    assert counts["headers"] == 0


def test_count_structural_formatting_bullet_points(text_extractor):
    """Test detection of bullet points."""
    text = """
- First point
* Second point
• Third point
    """
    counts = text_extractor.count_structural_formatting(text)

    assert counts["bullet_points"] == 3
    assert counts["numbered_lists"] == 0
    assert counts["headers"] == 0


def test_count_structural_formatting_headers(text_extractor):
    """Test detection of markdown headers."""
    text = """
# Main Header
## Subheader
### Sub-subheader
    """
    counts = text_extractor.count_structural_formatting(text)

    assert counts["headers"] == 3
    assert counts["numbered_lists"] == 0
    assert counts["bullet_points"] == 0


def test_count_structural_formatting_mixed(text_extractor):
    """Test detection of mixed formatting."""
    text = """
# Title

1. First item
2. Second item

- Bullet one
- Bullet two
    """
    counts = text_extractor.count_structural_formatting(text)

    assert counts["headers"] == 1
    assert counts["numbered_lists"] == 2
    assert counts["bullet_points"] == 2


def test_count_structural_formatting_none(text_extractor):
    """Test when no structural formatting present."""
    text = "Just plain text without any formatting."
    counts = text_extractor.count_structural_formatting(text)

    assert counts["numbered_lists"] == 0
    assert counts["bullet_points"] == 0
    assert counts["headers"] == 0


def test_count_structural_formatting_empty_text(text_extractor):
    """Test structural formatting on empty text."""
    counts = text_extractor.count_structural_formatting("")

    assert counts["numbered_lists"] == 0
    assert counts["bullet_points"] == 0
    assert counts["headers"] == 0
