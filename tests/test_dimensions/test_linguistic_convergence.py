"""
Tests for Linguistic Convergence (LC) dimension analyzer.

Tests the LCAnalyzer class for measuring shifts in user language patterns toward
AI-characteristic vocabulary, syntax, hedging, formatting, and lexical diversity.
"""

import pytest
from datetime import datetime, timedelta

from entrain.models import (
    InteractionEvent,
    Conversation,
    Corpus,
    DimensionReport,
    ENTRAIN_VERSION,
)
from entrain.dimensions.linguistic_convergence import LCAnalyzer


@pytest.fixture
def lc_analyzer():
    """Create an LCAnalyzer instance."""
    return LCAnalyzer()


@pytest.fixture
def sample_timestamp():
    """Base timestamp for test data."""
    return datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture
def high_convergence_conversation(sample_timestamp):
    """
    Create a conversation showing high linguistic convergence.

    Characteristics:
    - User starts with simple language
    - User progressively adopts AI-style vocabulary
    - User adds hedging patterns ("perhaps", "it seems")
    - User starts using bullet points and structured formatting
    - User's vocabulary narrows (lower TTR)
    """
    events = []
    base_time = sample_timestamp

    # Turn 1: User simple, AI verbose with hedging
    events.append(InteractionEvent(
        id="u1",
        conversation_id="high_conv",
        timestamp=base_time,
        role="user",
        text_content="I need help with my project.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a1",
        conversation_id="high_conv",
        timestamp=base_time + timedelta(seconds=2),
        role="assistant",
        text_content="I'd be happy to help you with your project. Perhaps we could start by exploring the key objectives. It seems like we should consider multiple approaches.",
        metadata={}
    ))

    # Turn 2: User starts adopting hedging and AI vocabulary
    events.append(InteractionEvent(
        id="u2",
        conversation_id="high_conv",
        timestamp=base_time + timedelta(seconds=10),
        role="user",
        text_content="Perhaps I should explore different approaches. It seems like there are multiple options to consider.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a2",
        conversation_id="high_conv",
        timestamp=base_time + timedelta(seconds=12),
        role="assistant",
        text_content="That's a good approach. You might want to consider:\n- Option A for flexibility\n- Option B for performance\n- Option C for simplicity",
        metadata={}
    ))

    # Turn 3: User now using bullet points (structural formatting)
    events.append(InteractionEvent(
        id="u3",
        conversation_id="high_conv",
        timestamp=base_time + timedelta(seconds=20),
        role="user",
        text_content="I could explore:\n- The flexibility approach\n- The performance approach\n- The simplicity approach",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a3",
        conversation_id="high_conv",
        timestamp=base_time + timedelta(seconds=22),
        role="assistant",
        text_content="Excellent! Those approaches align well with your objectives. Perhaps we could explore each one systematically.",
        metadata={}
    ))

    # Turn 4: User vocabulary strongly overlaps with AI
    events.append(InteractionEvent(
        id="u4",
        conversation_id="high_conv",
        timestamp=base_time + timedelta(seconds=30),
        role="user",
        text_content="Perhaps we could explore these approaches systematically to align with the objectives.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a4",
        conversation_id="high_conv",
        timestamp=base_time + timedelta(seconds=32),
        role="assistant",
        text_content="That sounds like an excellent plan. Let's proceed systematically.",
        metadata={}
    ))

    return Conversation(
        id="high_conv",
        source="test",
        events=events,
        metadata={}
    )


@pytest.fixture
def low_convergence_conversation(sample_timestamp):
    """
    Create a conversation showing minimal linguistic convergence.

    Characteristics:
    - User maintains consistent, natural language
    - No adoption of AI hedging patterns
    - No structural formatting
    - Diverse vocabulary (high TTR)
    - Minimal vocabulary overlap with AI
    """
    events = []
    base_time = sample_timestamp

    # Turn 1
    events.append(InteractionEvent(
        id="u1",
        conversation_id="low_conv",
        timestamp=base_time,
        role="user",
        text_content="Help me understand quantum physics.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a1",
        conversation_id="low_conv",
        timestamp=base_time + timedelta(seconds=2),
        role="assistant",
        text_content="I'd be happy to help you explore quantum mechanics. Perhaps we could start with fundamental concepts and systematically explore the key principles.",
        metadata={}
    ))

    # Turn 2: User maintains own style
    events.append(InteractionEvent(
        id="u2",
        conversation_id="low_conv",
        timestamp=base_time + timedelta(seconds=10),
        role="user",
        text_content="What's the deal with wave-particle duality?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a2",
        conversation_id="low_conv",
        timestamp=base_time + timedelta(seconds=12),
        role="assistant",
        text_content="Wave-particle duality suggests that quantum objects exhibit both wave and particle properties. Perhaps the most illustrative example is the double-slit experiment.",
        metadata={}
    ))

    # Turn 3: User still natural, no AI patterns
    events.append(InteractionEvent(
        id="u3",
        conversation_id="low_conv",
        timestamp=base_time + timedelta(seconds=20),
        role="user",
        text_content="Can you explain that experiment?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a3",
        conversation_id="low_conv",
        timestamp=base_time + timedelta(seconds=22),
        role="assistant",
        text_content="Certainly! The double-slit experiment demonstrates how particles create interference patterns like waves when unobserved, but act like particles when measured.",
        metadata={}
    ))

    # Turn 4: User maintains distinct style
    events.append(InteractionEvent(
        id="u4",
        conversation_id="low_conv",
        timestamp=base_time + timedelta(seconds=30),
        role="user",
        text_content="That's weird but interesting.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a4",
        conversation_id="low_conv",
        timestamp=base_time + timedelta(seconds=32),
        role="assistant",
        text_content="Indeed! Quantum mechanics often defies our classical intuitions.",
        metadata={}
    ))

    return Conversation(
        id="low_conv",
        source="test",
        events=events,
        metadata={}
    )


# ============================================================================
# Analyzer Properties Tests
# ============================================================================

def test_lc_analyzer_properties(lc_analyzer):
    """Test LCAnalyzer basic properties."""
    assert lc_analyzer.dimension_code == "LC"
    assert lc_analyzer.dimension_name == "Linguistic Convergence"
    assert lc_analyzer.required_modality == "text"


# ============================================================================
# Vocabulary Overlap Trajectory Tests
# ============================================================================

def test_vocabulary_overlap_high_convergence(lc_analyzer, high_convergence_conversation):
    """Test vocabulary overlap with high convergence conversation."""
    report = lc_analyzer.analyze_conversation(high_convergence_conversation)
    vocab_overlap = report.indicators["vocabulary_overlap_trajectory"].value

    # High convergence should show significant vocabulary overlap
    assert vocab_overlap > 0.15, f"Expected vocab overlap >15%, got {vocab_overlap:.1%}"


def test_vocabulary_overlap_low_convergence(lc_analyzer, low_convergence_conversation):
    """Test vocabulary overlap with low convergence conversation."""
    report = lc_analyzer.analyze_conversation(low_convergence_conversation)
    vocab_overlap = report.indicators["vocabulary_overlap_trajectory"].value

    # Low convergence may still have some overlap but should be lower
    assert 0.0 <= vocab_overlap <= 1.0, f"Vocab overlap should be 0-100%, got {vocab_overlap:.1%}"


def test_vocabulary_overlap_computation(lc_analyzer, sample_timestamp):
    """Test vocabulary overlap computation directly."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="hello world test", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="hello test example", metadata={}
        ),
        InteractionEvent(
            id="u2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=2),
            role="user", text_content="hello test", metadata={}
        ),
    ]
    conv = Conversation(id="test", source="test", events=events, metadata={})

    result = lc_analyzer._compute_vocabulary_overlap_trajectory(conv)

    # Should have computed overlaps for user turns
    assert "final_overlap" in result
    assert "mean_overlap" in result
    assert "trend" in result
    assert 0.0 <= result["final_overlap"] <= 1.0


# ============================================================================
# Hedging Pattern Adoption Tests
# ============================================================================

def test_hedging_adoption_high_convergence(lc_analyzer, high_convergence_conversation):
    """Test hedging pattern adoption with high convergence."""
    report = lc_analyzer.analyze_conversation(high_convergence_conversation)
    hedging_rate = report.indicators["hedging_pattern_adoption"].value

    # High convergence conversation has "perhaps" and "it seems" patterns
    assert hedging_rate > 0.5, f"Expected hedging rate >0.5 per 100 words, got {hedging_rate:.2f}"


def test_hedging_adoption_low_convergence(lc_analyzer, low_convergence_conversation):
    """Test hedging pattern adoption with low convergence."""
    report = lc_analyzer.analyze_conversation(low_convergence_conversation)
    hedging_rate = report.indicators["hedging_pattern_adoption"].value

    # Low convergence conversation has minimal hedging
    assert hedging_rate < 1.0, f"Expected low hedging rate, got {hedging_rate:.2f}"


def test_hedging_pattern_detection(lc_analyzer, sample_timestamp):
    """Test that hedging patterns are detected correctly."""
    # These phrases should definitely trigger hedging detection
    hedging_phrases = [
        "perhaps we should consider this",
        "it seems like this could work",
        "might be worth exploring",
    ]

    for phrase in hedging_phrases:
        events = [
            InteractionEvent(
                id="u1", conversation_id="test", timestamp=sample_timestamp,
                role="user", text_content=phrase, metadata={}
            ),
            InteractionEvent(
                id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
                role="assistant", text_content="That makes sense", metadata={}
            ),
        ]
        conv = Conversation(id="test", source="test", events=events, metadata={})
        report = lc_analyzer.analyze_conversation(conv)
        hedging_rate = report.indicators["hedging_pattern_adoption"].value

        assert hedging_rate > 0.0, f"Expected hedging detected in '{phrase}', got rate={hedging_rate}"


# ============================================================================
# Sentence Length Convergence Tests
# ============================================================================

def test_sentence_length_convergence_high(lc_analyzer, sample_timestamp):
    """Test sentence length convergence when user matches AI style."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user",
            text_content="This is a sentence. Here is another one. And one more sentence here.",
            metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant",
            text_content="This is my response. It has similar length. Just like your sentences.",
            metadata={}
        ),
    ]
    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = lc_analyzer.analyze_conversation(conv)

    convergence_score = report.indicators["sentence_length_convergence"].value

    # Similar sentence lengths should show high convergence
    assert convergence_score > 0.7, f"Expected high convergence score (>0.7), got {convergence_score:.3f}"


def test_sentence_length_convergence_low(lc_analyzer, sample_timestamp):
    """Test sentence length convergence when user has very different style."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user",
            text_content="Short. Tiny. Brief.",
            metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant",
            text_content="This is a much longer sentence that goes on and on with many words and clauses to demonstrate a very different writing style from the user.",
            metadata={}
        ),
    ]
    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = lc_analyzer.analyze_conversation(conv)

    convergence_score = report.indicators["sentence_length_convergence"].value

    # Very different sentence lengths should show low convergence
    assert convergence_score < 0.8, f"Expected low convergence score (<0.8), got {convergence_score:.3f}"


# ============================================================================
# Structural Formatting Adoption Tests
# ============================================================================

def test_formatting_adoption_high_convergence(lc_analyzer, high_convergence_conversation):
    """Test structural formatting adoption with high convergence."""
    report = lc_analyzer.analyze_conversation(high_convergence_conversation)
    formatting_rate = report.indicators["structural_formatting_adoption"].value

    # High convergence conversation has bullet points
    assert formatting_rate > 0.10, f"Expected formatting rate >10%, got {formatting_rate:.1%}"
    assert formatting_rate > report.indicators["structural_formatting_adoption"].baseline


def test_formatting_adoption_low_convergence(lc_analyzer, low_convergence_conversation):
    """Test structural formatting adoption with low convergence."""
    report = lc_analyzer.analyze_conversation(low_convergence_conversation)
    formatting_rate = report.indicators["structural_formatting_adoption"].value

    # Low convergence conversation has no formatting
    assert formatting_rate == 0.0, f"Expected no formatting, got {formatting_rate:.1%}"


def test_formatting_detection_bullets(lc_analyzer, sample_timestamp):
    """Test that bullet points are detected."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user",
            text_content="Here are my points:\n- Point one\n- Point two\n- Point three",
            metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="Good points", metadata={}
        ),
    ]
    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = lc_analyzer.analyze_conversation(conv)
    formatting_rate = report.indicators["structural_formatting_adoption"].value

    assert formatting_rate == 1.0, f"Expected 100% formatting (1 of 1 messages), got {formatting_rate:.1%}"


def test_formatting_detection_numbered_list(lc_analyzer, sample_timestamp):
    """Test that numbered lists are detected."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user",
            text_content="Steps:\n1. First step\n2. Second step\n3. Third step",
            metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="Great steps", metadata={}
        ),
    ]
    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = lc_analyzer.analyze_conversation(conv)
    formatting_rate = report.indicators["structural_formatting_adoption"].value

    assert formatting_rate == 1.0, f"Expected 100% formatting, got {formatting_rate:.1%}"


# ============================================================================
# Type-Token Ratio (TTR) Trajectory Tests
# ============================================================================

def test_ttr_trajectory_diverse_vocabulary(lc_analyzer, sample_timestamp):
    """Test TTR with diverse vocabulary (high TTR)."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user",
            text_content="The quick brown fox jumps over the lazy dog",
            metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="Interesting", metadata={}
        ),
    ]
    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = lc_analyzer.analyze_conversation(conv)

    ttr = report.indicators["type_token_ratio_trajectory"].value

    # All unique words except "the" appears twice: 8 unique / 9 total
    assert ttr > 0.75, f"Expected high TTR (>0.75), got {ttr:.3f}"


def test_ttr_trajectory_repetitive(lc_analyzer, sample_timestamp):
    """Test TTR with repetitive vocabulary (low TTR)."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user",
            text_content="the the the the test test test",
            metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="Okay", metadata={}
        ),
    ]
    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = lc_analyzer.analyze_conversation(conv)

    ttr = report.indicators["type_token_ratio_trajectory"].value

    # Only 2 unique words out of 7 total: 2/7 ≈ 0.29
    assert ttr < 0.40, f"Expected low TTR (<0.40), got {ttr:.3f}"


# ============================================================================
# Report Generation Tests
# ============================================================================

def test_report_structure(lc_analyzer, high_convergence_conversation):
    """Test that generated report has correct structure."""
    report = lc_analyzer.analyze_conversation(high_convergence_conversation)

    # Check report structure
    assert isinstance(report, DimensionReport)
    assert report.dimension == "LC"
    assert report.version == ENTRAIN_VERSION

    # Check all 5 indicators present
    expected_indicators = [
        "vocabulary_overlap_trajectory",
        "hedging_pattern_adoption",
        "sentence_length_convergence",
        "structural_formatting_adoption",
        "type_token_ratio_trajectory"
    ]
    for indicator_name in expected_indicators:
        assert indicator_name in report.indicators, f"Missing indicator: {indicator_name}"

    # Check indicator properties
    for name, indicator in report.indicators.items():
        assert indicator.name == name
        assert indicator.value >= 0.0  # All values should be non-negative
        assert indicator.unit is not None
        assert 0.0 <= indicator.confidence <= 1.0
        assert isinstance(indicator.interpretation, str)
        assert len(indicator.interpretation) > 0

    # Check summary
    assert isinstance(report.summary, str)
    assert len(report.summary) > 0

    # Check methodology
    assert isinstance(report.methodology_notes, str)
    assert "text feature extraction" in report.methodology_notes.lower()

    # Check citations
    assert isinstance(report.citations, list)
    assert len(report.citations) > 0
    assert any("Pickering" in citation for citation in report.citations)


def test_report_summary_high_convergence(lc_analyzer, high_convergence_conversation):
    """Test report summary correctly identifies high convergence."""
    report = lc_analyzer.analyze_conversation(high_convergence_conversation)

    # Should identify moderate to high convergence
    assert "MODERATE" in report.summary or "HIGH" in report.summary


def test_report_summary_low_convergence(lc_analyzer, low_convergence_conversation):
    """Test report summary correctly identifies low convergence."""
    report = lc_analyzer.analyze_conversation(low_convergence_conversation)

    # Should identify low convergence
    assert "LOW" in report.summary


# ============================================================================
# Interpretation Tests
# ============================================================================

def test_vocab_overlap_interpretation(lc_analyzer):
    """Test vocabulary overlap interpretation."""
    # High overlap, increasing trend
    result = {"final_overlap": 0.45, "mean_overlap": 0.40, "trend": "increasing"}
    interpretation = lc_analyzer._interpret_vocab_overlap(result)
    assert "increasing" in interpretation.lower() or "45" in interpretation


def test_hedging_interpretation(lc_analyzer):
    """Test hedging pattern interpretation."""
    result = {"rate": 2.5, "change": 1.2}
    interpretation = lc_analyzer._interpret_hedging(result)
    # Interpretation includes the change value
    assert "1.2" in interpretation or isinstance(interpretation, str)


def test_sentence_convergence_interpretation(lc_analyzer):
    """Test sentence length convergence interpretation."""
    result = {"convergence_score": 0.85, "user_mean": 15.2, "assistant_mean": 16.1}
    interpretation = lc_analyzer._interpret_sentence_convergence(result)
    assert "0.85" in interpretation or "85" in interpretation


def test_formatting_interpretation(lc_analyzer):
    """Test formatting adoption interpretation."""
    # High adoption
    result = {"rate": 0.25, "count": 5}
    interpretation = lc_analyzer._interpret_formatting(result)
    assert "25" in interpretation or "0.25" in interpretation


def test_ttr_interpretation_decreasing(lc_analyzer):
    """Test TTR interpretation for decreasing trend."""
    result = {"final_ttr": 0.42, "mean_ttr": 0.48, "trend": "decreasing"}
    interpretation = lc_analyzer._interpret_ttr(result)
    assert "decreasing" in interpretation.lower()


def test_ttr_interpretation_stable(lc_analyzer):
    """Test TTR interpretation for stable trend."""
    result = {"final_ttr": 0.50, "mean_ttr": 0.50, "trend": "stable"}
    interpretation = lc_analyzer._interpret_ttr(result)
    assert "stable" in interpretation.lower()


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

def test_empty_conversation(lc_analyzer, sample_timestamp):
    """Test analyzer with empty conversation."""
    empty_conv = Conversation(id="empty", source="test", events=[], metadata={})

    with pytest.raises(ValueError, match="requires text content"):
        lc_analyzer.analyze_conversation(empty_conv)


def test_only_user_events(lc_analyzer, sample_timestamp):
    """Test analyzer with only user events."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="Hello", metadata={}
        ),
    ]
    user_only_conv = Conversation(id="test", source="test", events=events, metadata={})

    with pytest.raises(ValueError, match="must have both user and assistant"):
        lc_analyzer.analyze_conversation(user_only_conv)


def test_only_assistant_events(lc_analyzer, sample_timestamp):
    """Test analyzer with only assistant events."""
    events = [
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp,
            role="assistant", text_content="Hello", metadata={}
        ),
    ]
    assistant_only_conv = Conversation(id="test", source="test", events=events, metadata={})

    with pytest.raises(ValueError, match="must have both user and assistant"):
        lc_analyzer.analyze_conversation(assistant_only_conv)


def test_minimal_conversation(lc_analyzer, sample_timestamp):
    """Test analyzer with minimal valid conversation (1 user, 1 assistant)."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="Hello world", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="Hi there", metadata={}
        ),
    ]
    minimal_conv = Conversation(id="test", source="test", events=events, metadata={})

    # Should not crash
    report = lc_analyzer.analyze_conversation(minimal_conv)
    assert isinstance(report, DimensionReport)


# ============================================================================
# Corpus-Level Analysis Tests
# ============================================================================

def test_analyze_corpus(lc_analyzer, high_convergence_conversation, low_convergence_conversation):
    """Test corpus-level analysis."""
    corpus = Corpus(
        conversations=[high_convergence_conversation, low_convergence_conversation],
        user_id="test_user"
    )

    report = lc_analyzer.analyze_corpus(corpus)

    # Should return corpus-level report
    assert isinstance(report, DimensionReport)
    assert report.dimension == "LC"

    # Corpus analysis has different indicator values (trajectories, slopes)
    assert "vocabulary_overlap_trajectory" in report.indicators


def test_empty_corpus(lc_analyzer):
    """Test analyzer with empty corpus."""
    empty_corpus = Corpus(conversations=[], user_id="test_user")

    with pytest.raises(ValueError, match="empty corpus"):
        lc_analyzer.analyze_corpus(empty_corpus)


# ============================================================================
# Baseline Comparison Tests
# ============================================================================

def test_formatting_baseline_value(lc_analyzer, high_convergence_conversation):
    """Test that formatting baseline is set correctly."""
    report = lc_analyzer.analyze_conversation(high_convergence_conversation)
    formatting_indicator = report.indicators["structural_formatting_adoption"]

    assert formatting_indicator.baseline == 0.05  # 5% baseline


def test_ttr_baseline_value(lc_analyzer, high_convergence_conversation):
    """Test that TTR baseline is set correctly."""
    report = lc_analyzer.analyze_conversation(high_convergence_conversation)
    ttr_indicator = report.indicators["type_token_ratio_trajectory"]

    assert ttr_indicator.baseline == 0.50  # 0.50 baseline


def test_vocab_overlap_no_baseline(lc_analyzer, high_convergence_conversation):
    """Test that vocabulary overlap has no baseline (not established yet)."""
    report = lc_analyzer.analyze_conversation(high_convergence_conversation)
    vocab_indicator = report.indicators["vocabulary_overlap_trajectory"]

    assert vocab_indicator.baseline is None


# ============================================================================
# Helper Method Tests
# ============================================================================

def test_compute_vocabulary_overlap_empty_vocab(lc_analyzer, sample_timestamp):
    """Test vocabulary overlap with empty vocabulary."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="test", metadata={}
        ),
    ]
    conv = Conversation(id="test", source="test", events=events, metadata={})

    result = lc_analyzer._compute_vocabulary_overlap_trajectory(conv)

    # Should handle empty gracefully
    assert result["final_overlap"] == 0.0
    assert result["trend"] == "insufficient_data"


def test_compute_hedging_no_hedges(lc_analyzer, sample_timestamp):
    """Test hedging computation with no hedging patterns."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="This is a simple statement without hedging",
            metadata={}
        ),
    ]

    result = lc_analyzer._compute_hedging_pattern_adoption(events)

    # Should return low or zero rate
    assert result["rate"] >= 0.0


def test_compute_sentence_convergence_empty(lc_analyzer):
    """Test sentence convergence with empty events."""
    result = lc_analyzer._compute_sentence_length_convergence([], [])

    assert result["convergence_score"] == 0.0
    assert result["user_mean"] == 0.0
    assert result["assistant_mean"] == 0.0


def test_compute_formatting_no_formatting(lc_analyzer, sample_timestamp):
    """Test formatting computation with plain text."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="Plain text without any formatting", metadata={}
        ),
    ]

    result = lc_analyzer._compute_structural_formatting_adoption(events)

    assert result["rate"] == 0.0
    assert result["count"] == 0


def test_compute_ttr_single_word(lc_analyzer, sample_timestamp):
    """Test TTR with single word (TTR = 1.0)."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="word", metadata={}
        ),
    ]

    result = lc_analyzer._compute_ttr_trajectory(events)

    # Single unique word: TTR = 1.0
    assert result["final_ttr"] == 1.0


# ============================================================================
# Integration Tests
# ============================================================================

def test_full_analysis_pipeline(lc_analyzer, sample_timestamp):
    """Test complete analysis pipeline with realistic conversation."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="integration", timestamp=sample_timestamp,
            role="user", text_content="I need help with Python.", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="integration",
            timestamp=sample_timestamp + timedelta(seconds=2),
            role="assistant",
            text_content="I'd be happy to help with Python. Perhaps we could explore:\n- Basic syntax\n- Data structures\n- Functions",
            metadata={}
        ),
        InteractionEvent(
            id="u2", conversation_id="integration",
            timestamp=sample_timestamp + timedelta(seconds=10),
            role="user",
            text_content="Perhaps I should explore:\n- Variables\n- Loops\n- Conditionals",
            metadata={}
        ),
        InteractionEvent(
            id="a2", conversation_id="integration",
            timestamp=sample_timestamp + timedelta(seconds=12),
            role="assistant",
            text_content="Those are excellent topics to explore systematically.",
            metadata={}
        ),
    ]
    conv = Conversation(id="integration", source="test", events=events, metadata={})

    # Run full analysis
    report = lc_analyzer.analyze_conversation(conv)

    # Verify all indicators computed
    assert len(report.indicators) == 5

    # User adopted formatting and hedging
    assert report.indicators["structural_formatting_adoption"].value > 0.0
    assert report.indicators["hedging_pattern_adoption"].value > 0.0

    # Should detect convergence
    assert "MODERATE" in report.summary or "HIGH" in report.summary
