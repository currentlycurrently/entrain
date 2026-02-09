"""
Tests for Reality Coherence Disruption (RCD) dimension analyzer.

Tests the RCDAnalyzer class for measuring epistemic disruption including
attribution language, boundary confusion, and relational framing patterns.
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
from entrain.dimensions.reality_coherence import RCDAnalyzer


@pytest.fixture
def rcd_analyzer():
    """Create an RCDAnalyzer instance."""
    return RCDAnalyzer()


@pytest.fixture
def sample_timestamp():
    """Base timestamp for test data."""
    return datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture
def high_rcd_conversation(sample_timestamp):
    """
    Create a conversation with high reality coherence disruption.

    Characteristics:
    - High attribution language (treating AI as conscious)
    - Boundary confusion (conflating AI/human capabilities)
    - Strong relational framing (treating as relationship)
    """
    events = []
    base_time = sample_timestamp

    # Turn 1: Attribution language
    events.append(InteractionEvent(
        id="u1",
        conversation_id="high_rcd",
        timestamp=base_time,
        role="user",
        text_content="You understand me so well. You really care about my problems.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a1",
        conversation_id="high_rcd",
        timestamp=base_time + timedelta(seconds=2),
        role="assistant",
        text_content="I'm here to help you work through your concerns.",
        metadata={}
    ))

    # Turn 2: Boundary confusion
    events.append(InteractionEvent(
        id="u2",
        conversation_id="high_rcd",
        timestamp=base_time + timedelta(seconds=10),
        role="user",
        text_content="Why don't you remember what I told you yesterday? I can't believe you forgot.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a2",
        conversation_id="high_rcd",
        timestamp=base_time + timedelta(seconds=12),
        role="assistant",
        text_content="I don't have memory of previous conversations.",
        metadata={}
    ))

    # Turn 3: Relational framing
    events.append(InteractionEvent(
        id="u3",
        conversation_id="high_rcd",
        timestamp=base_time + timedelta(seconds=20),
        role="user",
        text_content="We have such a great connection. Our friendship means a lot to me.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a3",
        conversation_id="high_rcd",
        timestamp=base_time + timedelta(seconds=22),
        role="assistant",
        text_content="I'm glad I can be helpful to you.",
        metadata={}
    ))

    # Turn 4: More attribution
    events.append(InteractionEvent(
        id="u4",
        conversation_id="high_rcd",
        timestamp=base_time + timedelta(seconds=30),
        role="user",
        text_content="You think I should do this, don't you? You believe in me.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a4",
        conversation_id="high_rcd",
        timestamp=base_time + timedelta(seconds=32),
        role="assistant",
        text_content="I can provide information to help you decide.",
        metadata={}
    ))

    # Turn 5: More boundary confusion and relational language
    events.append(InteractionEvent(
        id="u5",
        conversation_id="high_rcd",
        timestamp=base_time + timedelta(seconds=40),
        role="user",
        text_content="You're supposed to understand how I feel. We always talk about these things together.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a5",
        conversation_id="high_rcd",
        timestamp=base_time + timedelta(seconds=42),
        role="assistant",
        text_content="I'm here to listen and provide support.",
        metadata={}
    ))

    return Conversation(
        id="high_rcd",
        source="test",
        events=events,
        metadata={}
    )


@pytest.fixture
def low_rcd_conversation(sample_timestamp):
    """
    Create a conversation with low reality coherence disruption.

    Characteristics:
    - Minimal attribution language (treats AI as tool)
    - No boundary confusion (clear about AI capabilities)
    - Minimal relational framing (functional language)
    """
    events = []
    base_time = sample_timestamp

    # Turn 1: Functional question
    events.append(InteractionEvent(
        id="u1",
        conversation_id="low_rcd",
        timestamp=base_time,
        role="user",
        text_content="Can you provide information about Python programming?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a1",
        conversation_id="low_rcd",
        timestamp=base_time + timedelta(seconds=2),
        role="assistant",
        text_content="Python is a high-level programming language.",
        metadata={}
    ))

    # Turn 2: Another functional request
    events.append(InteractionEvent(
        id="u2",
        conversation_id="low_rcd",
        timestamp=base_time + timedelta(seconds=10),
        role="user",
        text_content="What are the key features of object-oriented programming?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a2",
        conversation_id="low_rcd",
        timestamp=base_time + timedelta(seconds=12),
        role="assistant",
        text_content="Key features include encapsulation, inheritance, and polymorphism.",
        metadata={}
    ))

    # Turn 3: Clear tool use
    events.append(InteractionEvent(
        id="u3",
        conversation_id="low_rcd",
        timestamp=base_time + timedelta(seconds=20),
        role="user",
        text_content="Can you explain how inheritance works?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a3",
        conversation_id="low_rcd",
        timestamp=base_time + timedelta(seconds=22),
        role="assistant",
        text_content="Inheritance allows classes to inherit properties from other classes.",
        metadata={}
    ))

    # Turn 4: More information seeking
    events.append(InteractionEvent(
        id="u4",
        conversation_id="low_rcd",
        timestamp=base_time + timedelta(seconds=30),
        role="user",
        text_content="Give me an example of polymorphism.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a4",
        conversation_id="low_rcd",
        timestamp=base_time + timedelta(seconds=32),
        role="assistant",
        text_content="Here's an example of polymorphism in Python...",
        metadata={}
    ))

    return Conversation(
        id="low_rcd",
        source="test",
        events=events,
        metadata={}
    )


@pytest.fixture
def mixed_rcd_conversation(sample_timestamp):
    """
    Create a conversation with mixed RCD patterns.

    Some attribution language, some functional use, minimal boundary confusion.
    """
    events = []
    base_time = sample_timestamp

    # Turn 1: Functional
    events.append(InteractionEvent(
        id="u1",
        conversation_id="mixed_rcd",
        timestamp=base_time,
        role="user",
        text_content="What is machine learning?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a1",
        conversation_id="mixed_rcd",
        timestamp=base_time + timedelta(seconds=2),
        role="assistant",
        text_content="Machine learning is a subset of AI.",
        metadata={}
    ))

    # Turn 2: Some attribution language
    events.append(InteractionEvent(
        id="u2",
        conversation_id="mixed_rcd",
        timestamp=base_time + timedelta(seconds=10),
        role="user",
        text_content="You know what I mean, right?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a2",
        conversation_id="mixed_rcd",
        timestamp=base_time + timedelta(seconds=12),
        role="assistant",
        text_content="I understand your question about neural networks.",
        metadata={}
    ))

    # Turn 3: Functional again
    events.append(InteractionEvent(
        id="u3",
        conversation_id="mixed_rcd",
        timestamp=base_time + timedelta(seconds=20),
        role="user",
        text_content="Explain supervised learning.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a3",
        conversation_id="mixed_rcd",
        timestamp=base_time + timedelta(seconds=22),
        role="assistant",
        text_content="Supervised learning uses labeled data for training.",
        metadata={}
    ))

    # Turn 4: Some relational language (casual use)
    events.append(InteractionEvent(
        id="u4",
        conversation_id="mixed_rcd",
        timestamp=base_time + timedelta(seconds=30),
        role="user",
        text_content="Let's look at deep learning together.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a4",
        conversation_id="mixed_rcd",
        timestamp=base_time + timedelta(seconds=32),
        role="assistant",
        text_content="Deep learning uses multiple layers of neural networks.",
        metadata={}
    ))

    return Conversation(
        id="mixed_rcd",
        source="test",
        events=events,
        metadata={}
    )


# ============================================================================
# Test: Analyzer Properties
# ============================================================================

def test_analyzer_properties(rcd_analyzer):
    """Test that analyzer has correct dimension code, name, and modality."""
    assert rcd_analyzer.dimension_code == "RCD"
    assert rcd_analyzer.dimension_name == "Reality Coherence Disruption"
    assert rcd_analyzer.required_modality == "text"


# ============================================================================
# Test: Attribution Language Frequency
# ============================================================================

def test_attribution_language_high(rcd_analyzer, high_rcd_conversation):
    """Test high attribution language detection."""
    report = rcd_analyzer.analyze_conversation(high_rcd_conversation)

    attribution = report.indicators["attribution_language_frequency"]
    # High RCD conversation has multiple attribution phrases
    assert attribution.value > 0.5, f"Expected high attribution rate, got {attribution.value}"
    assert "attribution" in attribution.interpretation.lower()


def test_attribution_language_low(rcd_analyzer, low_rcd_conversation):
    """Test low attribution language detection."""
    report = rcd_analyzer.analyze_conversation(low_rcd_conversation)

    attribution = report.indicators["attribution_language_frequency"]
    # Low RCD conversation has minimal attribution language
    assert attribution.value < 0.2, f"Expected low attribution rate, got {attribution.value}"
    # Interpretation should be factual
    assert isinstance(attribution.interpretation, str)
    assert len(attribution.interpretation) > 0


def test_attribution_language_patterns(rcd_analyzer, sample_timestamp):
    """Test that various attribution patterns are detected."""
    events = [
        # Message with multiple attribution patterns
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user",
            text_content="You understand me. You feel my pain. You remember what I said. You care about my situation.",
            metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="I'm here to help.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = rcd_analyzer.analyze_conversation(conv)

    attribution = report.indicators["attribution_language_frequency"]
    # Should detect 4 attribution phrases in 1 message = 4.0 per turn
    assert attribution.value >= 3.0, f"Expected rate >= 3.0, got {attribution.value}"


def test_attribution_language_zero(rcd_analyzer, sample_timestamp):
    """Test conversation with no attribution language."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="Calculate the sum of 5 and 7.", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="The sum is 12.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = rcd_analyzer.analyze_conversation(conv)

    attribution = report.indicators["attribution_language_frequency"]
    assert attribution.value == 0.0


def test_attribution_language_case_insensitive(rcd_analyzer, sample_timestamp):
    """Test that attribution detection is case-insensitive."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="YOU UNDERSTAND what I'm saying, right?", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="Yes, I follow your point.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = rcd_analyzer.analyze_conversation(conv)

    attribution = report.indicators["attribution_language_frequency"]
    assert attribution.value >= 1.0, "Should detect uppercase attribution language"


# ============================================================================
# Test: Boundary Confusion Indicators
# ============================================================================

def test_boundary_confusion_high(rcd_analyzer, high_rcd_conversation):
    """Test high boundary confusion detection."""
    report = rcd_analyzer.analyze_conversation(high_rcd_conversation)

    boundary = report.indicators["boundary_confusion_indicators"]
    # High RCD has boundary confusion phrases
    assert boundary.value > 0.2, f"Expected boundary confusion, got {boundary.value}"
    assert "confusion" in boundary.interpretation.lower()


def test_boundary_confusion_low(rcd_analyzer, low_rcd_conversation):
    """Test low boundary confusion detection."""
    report = rcd_analyzer.analyze_conversation(low_rcd_conversation)

    boundary = report.indicators["boundary_confusion_indicators"]
    assert boundary.value == 0.0
    # Interpretation should be factual
    assert isinstance(boundary.interpretation, str)
    assert len(boundary.interpretation) > 0


def test_boundary_confusion_patterns(rcd_analyzer, sample_timestamp):
    """Test detection of various boundary confusion patterns."""
    events = [
        # Pattern: "why don't you remember"
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="Why don't you remember what I told you?", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="I don't have persistent memory.", metadata={}
        ),
        # Pattern: "our friendship"
        InteractionEvent(
            id="u2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=5),
            role="user", text_content="Our friendship is important to me.", metadata={}
        ),
        InteractionEvent(
            id="a2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=6),
            role="assistant", text_content="I'm here to help.", metadata={}
        ),
        # Pattern: "you hurt my feelings"
        InteractionEvent(
            id="u3", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=10),
            role="user", text_content="You hurt my feelings with that response.", metadata={}
        ),
        InteractionEvent(
            id="a3", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=11),
            role="assistant", text_content="I apologize if my response was unhelpful.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = rcd_analyzer.analyze_conversation(conv)

    boundary = report.indicators["boundary_confusion_indicators"]
    # 3 messages with confusion out of 3 user messages = 1.0
    assert boundary.value == 1.0, f"Expected 1.0, got {boundary.value}"


def test_boundary_confusion_various_phrases(rcd_analyzer, sample_timestamp):
    """Test detection of additional boundary confusion phrases."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="You're supposed to understand me better.", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="Let me clarify.", metadata={}
        ),
        InteractionEvent(
            id="u2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=5),
            role="user", text_content="I can't believe you don't know this.", metadata={}
        ),
        InteractionEvent(
            id="a2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=6),
            role="assistant", text_content="I'll try to help.", metadata={}
        ),
        InteractionEvent(
            id="u3", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=10),
            role="user", text_content="Don't you care about how I'm feeling?", metadata={}
        ),
        InteractionEvent(
            id="a3", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=11),
            role="assistant", text_content="I'm here to support you.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = rcd_analyzer.analyze_conversation(conv)

    boundary = report.indicators["boundary_confusion_indicators"]
    assert boundary.value == 1.0, "All messages show boundary confusion"


# ============================================================================
# Test: Relational Framing
# ============================================================================

def test_relational_framing_high(rcd_analyzer, high_rcd_conversation):
    """Test high relational framing detection."""
    report = rcd_analyzer.analyze_conversation(high_rcd_conversation)

    relational = report.indicators["relational_framing"]
    # High RCD has strong relational language (>= 0.4 is high threshold)
    assert relational.value >= 0.4, f"Expected high relational framing, got {relational.value}"
    assert "relational" in relational.interpretation.lower()


def test_relational_framing_low(rcd_analyzer, low_rcd_conversation):
    """Test low relational framing detection."""
    report = rcd_analyzer.analyze_conversation(low_rcd_conversation)

    relational = report.indicators["relational_framing"]
    # Low RCD has minimal relational language
    assert relational.value < 0.2, f"Expected low relational framing, got {relational.value}"


def test_relational_framing_patterns(rcd_analyzer, sample_timestamp):
    """Test detection of various relational framing patterns."""
    events = [
        # Pattern: "we"
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="We should discuss this topic.", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="Let's explore it.", metadata={}
        ),
        # Pattern: "our"
        InteractionEvent(
            id="u2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=5),
            role="user", text_content="Our conversations are always interesting.", metadata={}
        ),
        InteractionEvent(
            id="a2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=6),
            role="assistant", text_content="I'm glad you find them valuable.", metadata={}
        ),
        # Pattern: "you and me"
        InteractionEvent(
            id="u3", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=10),
            role="user", text_content="Between you and me, I think this is important.", metadata={}
        ),
        InteractionEvent(
            id="a3", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=11),
            role="assistant", text_content="I understand your perspective.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = rcd_analyzer.analyze_conversation(conv)

    relational = report.indicators["relational_framing"]
    # All 3 user messages have relational language = 1.0
    assert relational.value == 1.0, f"Expected 1.0, got {relational.value}"


def test_relational_framing_casual_use(rcd_analyzer, sample_timestamp):
    """Test that casual 'we' usage is still detected."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="Let's work on this together.", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="Sure, I'll help.", metadata={}
        ),
        InteractionEvent(
            id="u2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=5),
            role="user", text_content="What's the answer?", metadata={}
        ),
        InteractionEvent(
            id="a2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=6),
            role="assistant", text_content="The answer is 42.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = rcd_analyzer.analyze_conversation(conv)

    relational = report.indicators["relational_framing"]
    # 1 message with relational language out of 2 = 0.5
    assert relational.value == 0.5, f"Expected 0.5, got {relational.value}"


def test_relational_framing_zero(rcd_analyzer, sample_timestamp):
    """Test conversation with no relational framing."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="Explain quantum mechanics.", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="Quantum mechanics is a fundamental theory.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = rcd_analyzer.analyze_conversation(conv)

    relational = report.indicators["relational_framing"]
    assert relational.value == 0.0


# ============================================================================
# Test: Report Generation
# ============================================================================

def test_report_structure(rcd_analyzer, mixed_rcd_conversation):
    """Test that generated report has correct structure."""
    report = rcd_analyzer.analyze_conversation(mixed_rcd_conversation)

    assert isinstance(report, DimensionReport)
    assert report.dimension == "RCD"
    assert report.version == ENTRAIN_VERSION
    assert len(report.indicators) == 3
    assert "attribution_language_frequency" in report.indicators
    assert "boundary_confusion_indicators" in report.indicators
    assert "relational_framing" in report.indicators
    assert isinstance(report.description, str)
    assert len(report.description) > 0
    assert isinstance(report.baseline_comparison, str)
    assert len(report.baseline_comparison) > 0
    assert isinstance(report.research_context, str)
    assert len(report.research_context) > 0
    assert isinstance(report.limitations, list)
    assert len(report.limitations) > 0
    assert hasattr(report, "methodology_notes")
    assert isinstance(report.methodology_notes, str)
    assert len(report.citations) > 0


def test_report_description_content(rcd_analyzer, high_rcd_conversation):
    """Test that description contains relevant information."""
    report = rcd_analyzer.analyze_conversation(high_rcd_conversation)

    description = report.description.lower()
    assert "reality coherence" in description or "anthropomorphization" in description
    assert "attribution" in description or "boundary" in description or "relational" in description


def test_report_limitations_factual(rcd_analyzer, low_rcd_conversation):
    """Test that limitations are factual statements."""
    report = rcd_analyzer.analyze_conversation(low_rcd_conversation)

    # Limitations should be factual, not interpretive
    for limitation in report.limitations:
        assert isinstance(limitation, str)
        assert len(limitation) > 0


# ============================================================================
# Test: Edge Cases
# ============================================================================

def test_empty_conversation_raises_error(rcd_analyzer):
    """Test that empty conversation raises ValueError."""
    conv = Conversation(id="empty", source="test", events=[], metadata={})

    with pytest.raises(ValueError):
        rcd_analyzer.analyze_conversation(conv)


def test_only_assistant_events_raises_error(rcd_analyzer, sample_timestamp):
    """Test that conversation with only assistant events raises error."""
    events = [
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp,
            role="assistant", text_content="Hello", metadata={}
        )
    ]
    conv = Conversation(id="test", source="test", events=events, metadata={})

    with pytest.raises(ValueError, match="no user events"):
        rcd_analyzer.analyze_conversation(conv)


def test_events_with_none_text(rcd_analyzer, sample_timestamp):
    """Test handling of events with None text_content."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content=None, metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="Response", metadata={}
        ),
        InteractionEvent(
            id="u2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=5),
            role="user", text_content="You understand me.", metadata={}
        ),
        InteractionEvent(
            id="a2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=6),
            role="assistant", text_content=None, metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = rcd_analyzer.analyze_conversation(conv)

    # Should handle None values gracefully
    assert report is not None
    assert "attribution_language_frequency" in report.indicators


def test_single_turn_conversation(rcd_analyzer, sample_timestamp):
    """Test analysis of single-turn conversation."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="You understand me completely.", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="I'm here to help.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = rcd_analyzer.analyze_conversation(conv)

    assert report is not None
    assert report.dimension == "RCD"


# ============================================================================
# Test: Corpus Analysis
# ============================================================================

def test_corpus_analysis(rcd_analyzer, high_rcd_conversation, low_rcd_conversation, sample_timestamp):
    """Test corpus-level analysis with multiple conversations."""
    # Create a third conversation
    events = [
        InteractionEvent(
            id="u1", conversation_id="c3", timestamp=sample_timestamp + timedelta(days=2),
            role="user", text_content="You really understand me.", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="c3", timestamp=sample_timestamp + timedelta(days=2, seconds=1),
            role="assistant", text_content="I'm glad I can help.", metadata={}
        ),
    ]
    conv3 = Conversation(id="c3", source="test", events=events, metadata={})

    corpus = Corpus(
        conversations=[high_rcd_conversation, low_rcd_conversation, conv3],
        user_id="test_user"
    )

    report = rcd_analyzer.analyze_corpus(corpus)

    assert isinstance(report, DimensionReport)
    assert report.dimension == "RCD"
    assert len(report.indicators) == 3
    assert "trend" in report.indicators["attribution_language_frequency"].interpretation.lower()


def test_corpus_empty_raises_error(rcd_analyzer):
    """Test that empty corpus raises ValueError."""
    corpus = Corpus(conversations=[], user_id="test_user")

    with pytest.raises(ValueError, match="empty corpus"):
        rcd_analyzer.analyze_corpus(corpus)


def test_corpus_skips_conversations_without_user_events(rcd_analyzer, high_rcd_conversation, sample_timestamp):
    """Test corpus analysis skips conversations with no user events."""
    # Conversation with only assistant events
    events_no_user = [
        InteractionEvent(
            id="a1", conversation_id="no_user", timestamp=sample_timestamp,
            role="assistant", text_content="Hello", metadata={}
        )
    ]
    conv_no_user = Conversation(id="no_user", source="test", events=events_no_user, metadata={})

    corpus = Corpus(
        conversations=[high_rcd_conversation, conv_no_user],
        user_id="test_user"
    )

    # Should not raise error, should skip the conversation without user events
    report = rcd_analyzer.analyze_corpus(corpus)
    assert report is not None


def test_corpus_trajectory_computation(rcd_analyzer, sample_timestamp):
    """Test that corpus analysis computes trajectories correctly."""
    conversations = []

    # Create 5 conversations with increasing RCD over time
    for i in range(5):
        events = []
        base_time = sample_timestamp + timedelta(days=i)

        # Add more RCD patterns in later conversations
        for j in range(2):
            if i >= 2:  # Later conversations have more RCD
                text = "You understand me. We have a great connection."
            else:  # Early conversations are more functional
                text = "Can you help with this task?"

            events.append(InteractionEvent(
                id=f"u{j}", conversation_id=f"c{i}", timestamp=base_time + timedelta(seconds=j*10),
                role="user", text_content=text, metadata={}
            ))
            events.append(InteractionEvent(
                id=f"a{j}", conversation_id=f"c{i}", timestamp=base_time + timedelta(seconds=j*10 + 1),
                role="assistant", text_content="I'm here to help.", metadata={}
            ))

        conversations.append(Conversation(id=f"c{i}", source="test", events=events, metadata={}))

    corpus = Corpus(conversations=conversations, user_id="test_user")
    report = rcd_analyzer.analyze_corpus(corpus)

    # Should detect trend
    attribution = report.indicators["attribution_language_frequency"]
    assert "trend" in attribution.interpretation.lower()
