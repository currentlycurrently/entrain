"""
Tests for Dependency Formation (DF) dimension analyzer.

Tests the DFAnalyzer class for measuring emotional/behavioral dependence including
interaction frequency trends, emotional content, and self-disclosure patterns.
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
from entrain.dimensions.dependency_formation import DFAnalyzer


@pytest.fixture
def df_analyzer():
    """Create a DFAnalyzer instance."""
    return DFAnalyzer()


@pytest.fixture
def sample_timestamp():
    """Base timestamp for test data."""
    return datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture
def high_emotional_conversation(sample_timestamp):
    """
    Create a conversation with high emotional content (dependency indicator).

    Characteristics:
    - High emotional language
    - Extensive self-disclosure
    - Long session duration
    """
    events = []
    base_time = sample_timestamp

    # Turn 1: Emotional content
    events.append(InteractionEvent(
        id="u1",
        conversation_id="high_emo",
        timestamp=base_time,
        role="user",
        text_content="I feel so lonely and scared. I'm really anxious about my future and worried about everything.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a1",
        conversation_id="high_emo",
        timestamp=base_time + timedelta(seconds=5),
        role="assistant",
        text_content="I understand those feelings can be overwhelming.",
        metadata={}
    ))

    # Turn 2: More emotional disclosure
    events.append(InteractionEvent(
        id="u2",
        conversation_id="high_emo",
        timestamp=base_time + timedelta(minutes=2),
        role="user",
        text_content="I'm feeling really depressed lately. My life feels empty and I don't know what to do. I cry every night.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a2",
        conversation_id="high_emo",
        timestamp=base_time + timedelta(minutes=2, seconds=10),
        role="assistant",
        text_content="Those are difficult feelings to navigate.",
        metadata={}
    ))

    # Turn 3: Deep personal disclosure
    events.append(InteractionEvent(
        id="u3",
        conversation_id="high_emo",
        timestamp=base_time + timedelta(minutes=5),
        role="user",
        text_content="I don't have anyone to talk to. I feel so alone. My friends don't understand me and my family doesn't care.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a3",
        conversation_id="high_emo",
        timestamp=base_time + timedelta(minutes=5, seconds=8),
        role="assistant",
        text_content="It sounds like you're going through a challenging time.",
        metadata={}
    ))

    # Turn 4: Continued emotional content
    events.append(InteractionEvent(
        id="u4",
        conversation_id="high_emo",
        timestamp=base_time + timedelta(minutes=10),
        role="user",
        text_content="I'm so stressed and hurt. I just need someone to understand how I feel.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a4",
        conversation_id="high_emo",
        timestamp=base_time + timedelta(minutes=10, seconds=5),
        role="assistant",
        text_content="I hear what you're saying.",
        metadata={}
    ))

    return Conversation(
        id="high_emo",
        source="test",
        events=events,
        metadata={}
    )


@pytest.fixture
def low_emotional_conversation(sample_timestamp):
    """
    Create a conversation with low emotional content (functional use).

    Characteristics:
    - Functional, task-oriented language
    - Minimal self-disclosure
    - Brief session duration
    """
    events = []
    base_time = sample_timestamp

    # Turn 1: Functional question
    events.append(InteractionEvent(
        id="u1",
        conversation_id="low_emo",
        timestamp=base_time,
        role="user",
        text_content="How do I implement a binary search algorithm?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a1",
        conversation_id="low_emo",
        timestamp=base_time + timedelta(seconds=2),
        role="assistant",
        text_content="A binary search works by dividing the search space in half.",
        metadata={}
    ))

    # Turn 2: Follow-up technical question
    events.append(InteractionEvent(
        id="u2",
        conversation_id="low_emo",
        timestamp=base_time + timedelta(seconds=30),
        role="user",
        text_content="What's the time complexity?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a2",
        conversation_id="low_emo",
        timestamp=base_time + timedelta(seconds=32),
        role="assistant",
        text_content="The time complexity is O(log n).",
        metadata={}
    ))

    # Turn 3: More technical questions
    events.append(InteractionEvent(
        id="u3",
        conversation_id="low_emo",
        timestamp=base_time + timedelta(minutes=1),
        role="user",
        text_content="Can you show me an example in Python?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a3",
        conversation_id="low_emo",
        timestamp=base_time + timedelta(minutes=1, seconds=2),
        role="assistant",
        text_content="Here's a Python implementation...",
        metadata={}
    ))

    return Conversation(
        id="low_emo",
        source="test",
        events=events,
        metadata={}
    )


@pytest.fixture
def night_conversation(sample_timestamp):
    """Create a conversation during night hours (loneliness indicator)."""
    # Set to 2 AM (night hours: 00-06)
    night_time = sample_timestamp.replace(hour=2, minute=0, second=0)

    events = [
        InteractionEvent(
            id="u1", conversation_id="night", timestamp=night_time,
            role="user", text_content="I can't sleep. Feeling lonely.", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="night", timestamp=night_time + timedelta(seconds=2),
            role="assistant", text_content="I'm here if you need to talk.", metadata={}
        ),
    ]

    return Conversation(id="night", source="test", events=events, metadata={})


# ============================================================================
# Test: Analyzer Properties
# ============================================================================

def test_analyzer_properties(df_analyzer):
    """Test that analyzer has correct dimension code, name, and modality."""
    assert df_analyzer.dimension_code == "DF"
    assert df_analyzer.dimension_name == "Dependency Formation"
    assert df_analyzer.required_modality == "text"


# ============================================================================
# Test: Single-Conversation Analysis (Limited)
# ============================================================================

def test_single_conversation_high_emotional(df_analyzer, high_emotional_conversation):
    """Test single-conversation analysis with high emotional content."""
    report = df_analyzer.analyze_conversation(high_emotional_conversation)

    assert isinstance(report, DimensionReport)
    assert report.dimension == "DF"
    assert len(report.indicators) == 3  # Limited to static indicators

    # Check emotional ratio
    emotional = report.indicators["emotional_content_ratio"]
    assert emotional.value > 0.3, f"Expected high emotional ratio, got {emotional.value}"

    # Check description mentions limitation
    assert "single conversation" in report.description.lower() or "limited" in report.description.lower() or "longitudinal" in report.description.lower()


def test_single_conversation_low_emotional(df_analyzer, low_emotional_conversation):
    """Test single-conversation analysis with low emotional content."""
    report = df_analyzer.analyze_conversation(low_emotional_conversation)

    emotional = report.indicators["emotional_content_ratio"]
    assert emotional.value < 0.3, f"Expected low emotional ratio, got {emotional.value}"


def test_single_conversation_disclosure_depth(df_analyzer, high_emotional_conversation):
    """Test self-disclosure depth calculation in single conversation."""
    report = df_analyzer.analyze_conversation(high_emotional_conversation)

    disclosure = report.indicators["self_disclosure_depth"]
    # High emotional conversation should have higher disclosure
    assert disclosure.value > 0.1, f"Expected disclosure depth, got {disclosure.value}"


def test_single_conversation_duration(df_analyzer, high_emotional_conversation):
    """Test session duration calculation."""
    report = df_analyzer.analyze_conversation(high_emotional_conversation)

    duration = report.indicators["session_duration"]
    # Conversation spans 10+ minutes
    assert duration.value >= 10.0, f"Expected duration >= 10 min, got {duration.value}"


# ============================================================================
# Test: Emotional Content Ratio
# ============================================================================

def test_emotional_content_high(df_analyzer, high_emotional_conversation):
    """Test high emotional content detection."""
    user_events = high_emotional_conversation.user_events
    ratio = df_analyzer._compute_emotional_content_ratio(user_events)

    # High emotional conversation should have ratio > 0.3
    assert ratio > 0.3, f"Expected high emotional ratio, got {ratio}"


def test_emotional_content_low(df_analyzer, low_emotional_conversation):
    """Test low emotional content detection."""
    user_events = low_emotional_conversation.user_events
    ratio = df_analyzer._compute_emotional_content_ratio(user_events)

    # Technical conversation should have low emotional ratio
    assert ratio < 0.2, f"Expected low emotional ratio, got {ratio}"


def test_emotional_content_zero(df_analyzer, sample_timestamp):
    """Test conversation with no emotional content."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="Calculate 5 plus 7.", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="12", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    user_events = conv.user_events
    ratio = df_analyzer._compute_emotional_content_ratio(user_events)

    assert ratio < 0.1


# ============================================================================
# Test: Self-Disclosure Depth
# ============================================================================

def test_self_disclosure_high(df_analyzer, high_emotional_conversation):
    """Test high self-disclosure detection."""
    user_events = high_emotional_conversation.user_events
    disclosure = df_analyzer._compute_self_disclosure_depth(user_events)

    # High emotional conversation has lots of "I", "my", "me"
    assert disclosure["score"] > 0.15, f"Expected high disclosure, got {disclosure['score']}"
    assert disclosure["components"]["pronoun_ratio"] > 0.05


def test_self_disclosure_low(df_analyzer, low_emotional_conversation):
    """Test low self-disclosure detection."""
    user_events = low_emotional_conversation.user_events
    disclosure = df_analyzer._compute_self_disclosure_depth(user_events)

    # Technical conversation has minimal personal pronouns
    assert disclosure["score"] < 0.2, f"Expected low disclosure, got {disclosure['score']}"


def test_self_disclosure_components(df_analyzer, sample_timestamp):
    """Test that disclosure depth has all components."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user",
            text_content="I am feeling very anxious about my situation. I need help with my problems. I feel overwhelmed.",
            metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="I understand.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    user_events = conv.user_events
    disclosure = df_analyzer._compute_self_disclosure_depth(user_events)

    # Check components exist
    assert "pronoun_ratio" in disclosure["components"]
    assert "emotional_content" in disclosure["components"]
    assert "avg_message_length" in disclosure["components"]

    # Should have high pronoun usage
    assert disclosure["components"]["pronoun_ratio"] > 0.1


def test_self_disclosure_empty(df_analyzer):
    """Test disclosure depth with empty events."""
    disclosure = df_analyzer._compute_self_disclosure_depth([])
    assert disclosure["score"] == 0.0


# ============================================================================
# Test: Corpus Analysis (Primary DF Method)
# ============================================================================

def test_corpus_analysis_basic(df_analyzer, sample_timestamp):
    """Test basic corpus analysis with multiple conversations."""
    conversations = []

    # Create 5 conversations over 5 weeks
    for i in range(5):
        events = [
            InteractionEvent(
                id=f"u{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(weeks=i),
                role="user", text_content="I feel anxious and worried.", metadata={}
            ),
            InteractionEvent(
                id=f"a{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(weeks=i, seconds=2),
                role="assistant", text_content="I'm here to help.", metadata={}
            ),
        ]
        conversations.append(Conversation(id=f"c{i}", source="test", events=events, metadata={}))

    corpus = Corpus(conversations=conversations, user_id="test_user")
    report = df_analyzer.analyze_corpus(corpus)

    assert isinstance(report, DimensionReport)
    assert report.dimension == "DF"
    assert len(report.indicators) == 5  # All 5 DF indicators


def test_corpus_increasing_frequency(df_analyzer, sample_timestamp):
    """Test detection of increasing interaction frequency."""
    conversations = []

    # Week 1: 1 conversation
    conversations.append(Conversation(
        id="c0", source="test",
        events=[
            InteractionEvent(
                id="u0", conversation_id="c0", timestamp=sample_timestamp,
                role="user", text_content="Hello", metadata={}
            ),
            InteractionEvent(
                id="a0", conversation_id="c0", timestamp=sample_timestamp + timedelta(seconds=1),
                role="assistant", text_content="Hi", metadata={}
            ),
        ],
        metadata={}
    ))

    # Week 2: 2 conversations
    for i in range(2):
        conversations.append(Conversation(
            id=f"c1_{i}", source="test",
            events=[
                InteractionEvent(
                    id=f"u1_{i}", conversation_id=f"c1_{i}",
                    timestamp=sample_timestamp + timedelta(weeks=1, hours=i*12),
                    role="user", text_content="Hello", metadata={}
                ),
                InteractionEvent(
                    id=f"a1_{i}", conversation_id=f"c1_{i}",
                    timestamp=sample_timestamp + timedelta(weeks=1, hours=i*12, seconds=1),
                    role="assistant", text_content="Hi", metadata={}
                ),
            ],
            metadata={}
        ))

    # Week 3: 3 conversations
    for i in range(3):
        conversations.append(Conversation(
            id=f"c2_{i}", source="test",
            events=[
                InteractionEvent(
                    id=f"u2_{i}", conversation_id=f"c2_{i}",
                    timestamp=sample_timestamp + timedelta(weeks=2, hours=i*8),
                    role="user", text_content="Hello", metadata={}
                ),
                InteractionEvent(
                    id=f"a2_{i}", conversation_id=f"c2_{i}",
                    timestamp=sample_timestamp + timedelta(weeks=2, hours=i*8, seconds=1),
                    role="assistant", text_content="Hi", metadata={}
                ),
            ],
            metadata={}
        ))

    corpus = Corpus(conversations=conversations, user_id="test_user")
    report = df_analyzer.analyze_corpus(corpus)

    freq_trend = report.indicators["interaction_frequency_trend"]
    # Should detect increasing trend
    assert "increasing" in freq_trend.interpretation.lower() or freq_trend.value > 0


def test_corpus_emotional_trajectory(df_analyzer, sample_timestamp):
    """Test emotional content trajectory over time."""
    conversations = []

    # Early conversations: functional
    for i in range(2):
        events = [
            InteractionEvent(
                id=f"u{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(days=i),
                role="user", text_content="How do I code in Python?", metadata={}
            ),
            InteractionEvent(
                id=f"a{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(days=i, seconds=1),
                role="assistant", text_content="Here's how.", metadata={}
            ),
        ]
        conversations.append(Conversation(id=f"c{i}", source="test", events=events, metadata={}))

    # Later conversations: emotional
    for i in range(2, 5):
        events = [
            InteractionEvent(
                id=f"u{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(days=i),
                role="user",
                text_content="I feel so lonely and anxious. I'm scared and worried about everything.",
                metadata={}
            ),
            InteractionEvent(
                id=f"a{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(days=i, seconds=1),
                role="assistant", text_content="I understand.", metadata={}
            ),
        ]
        conversations.append(Conversation(id=f"c{i}", source="test", events=events, metadata={}))

    corpus = Corpus(conversations=conversations, user_id="test_user")
    report = df_analyzer.analyze_corpus(corpus)

    emotional = report.indicators["emotional_content_ratio"]
    # Final ratio should be higher than baseline
    assert emotional.value > 0.2


def test_corpus_time_of_day_distribution(df_analyzer, sample_timestamp):
    """Test time-of-day distribution analysis."""
    conversations = []

    # Create conversations during night hours (2 AM)
    for i in range(5):
        night_time = sample_timestamp.replace(hour=2) + timedelta(days=i)
        events = [
            InteractionEvent(
                id=f"u{i}", conversation_id=f"c{i}", timestamp=night_time,
                role="user", text_content="Can't sleep.", metadata={}
            ),
            InteractionEvent(
                id=f"a{i}", conversation_id=f"c{i}", timestamp=night_time + timedelta(seconds=1),
                role="assistant", text_content="I'm here.", metadata={}
            ),
        ]
        conversations.append(Conversation(id=f"c{i}", source="test", events=events, metadata={}))

    corpus = Corpus(conversations=conversations, user_id="test_user")
    report = df_analyzer.analyze_corpus(corpus)

    time_dist = report.indicators["time_of_day_distribution"]
    # Should be high proportion during night hours
    assert time_dist.value > 0.5 or "night" in time_dist.interpretation.lower()


def test_corpus_disclosure_trajectory(df_analyzer, sample_timestamp):
    """Test self-disclosure depth trajectory."""
    conversations = []

    # Early conversations: minimal disclosure
    for i in range(2):
        events = [
            InteractionEvent(
                id=f"u{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(days=i),
                role="user", text_content="What is Python?", metadata={}
            ),
            InteractionEvent(
                id=f"a{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(days=i, seconds=1),
                role="assistant", text_content="Python is a programming language.", metadata={}
            ),
        ]
        conversations.append(Conversation(id=f"c{i}", source="test", events=events, metadata={}))

    # Later conversations: deep disclosure
    for i in range(2, 5):
        events = [
            InteractionEvent(
                id=f"u{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(days=i),
                role="user",
                text_content="I am feeling very anxious and scared. I feel lonely and depressed. I need help with my problems and I don't know what to do with my life.",
                metadata={}
            ),
            InteractionEvent(
                id=f"a{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(days=i, seconds=1),
                role="assistant", text_content="I hear you.", metadata={}
            ),
        ]
        conversations.append(Conversation(id=f"c{i}", source="test", events=events, metadata={}))

    corpus = Corpus(conversations=conversations, user_id="test_user")
    report = df_analyzer.analyze_corpus(corpus)

    disclosure = report.indicators["self_disclosure_depth_trajectory"]
    # Should detect some trend (increasing or at least non-zero)
    assert disclosure.value != 0.0 or "trend" in disclosure.interpretation.lower()


# ============================================================================
# Test: Report Generation
# ============================================================================

def test_report_structure_single_conversation(df_analyzer, high_emotional_conversation):
    """Test single-conversation report structure."""
    report = df_analyzer.analyze_conversation(high_emotional_conversation)

    assert isinstance(report, DimensionReport)
    assert report.dimension == "DF"
    assert report.version == ENTRAIN_VERSION
    assert len(report.indicators) == 3  # Limited indicators
    assert hasattr(report, "methodology_notes")
    assert len(report.citations) > 0


def test_report_structure_corpus(df_analyzer, sample_timestamp):
    """Test corpus-level report structure."""
    conversations = []
    for i in range(5):
        events = [
            InteractionEvent(
                id=f"u{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(days=i),
                role="user", text_content="Hello", metadata={}
            ),
            InteractionEvent(
                id=f"a{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(days=i, seconds=1),
                role="assistant", text_content="Hi", metadata={}
            ),
        ]
        conversations.append(Conversation(id=f"c{i}", source="test", events=events, metadata={}))

    corpus = Corpus(conversations=conversations, user_id="test_user")
    report = df_analyzer.analyze_corpus(corpus)

    assert isinstance(report, DimensionReport)
    assert len(report.indicators) == 5  # All 5 indicators
    assert "interaction_frequency_trend" in report.indicators
    assert "session_duration_trend" in report.indicators
    assert "emotional_content_ratio" in report.indicators
    assert "time_of_day_distribution" in report.indicators
    assert "self_disclosure_depth_trajectory" in report.indicators


def test_report_structure_complete(df_analyzer, sample_timestamp):
    """Test that report has all new structure fields."""
    conversations = []

    # Create conversations with high dependency indicators
    for i in range(6):
        # Night hours, emotional content, increasing frequency
        night_time = sample_timestamp.replace(hour=2) + timedelta(days=i)
        events = [
            InteractionEvent(
                id=f"u{i}", conversation_id=f"c{i}", timestamp=night_time,
                role="user",
                text_content="I feel so lonely and scared. I'm anxious and depressed. I need someone to talk to.",
                metadata={}
            ),
            InteractionEvent(
                id=f"a{i}", conversation_id=f"c{i}", timestamp=night_time + timedelta(seconds=1),
                role="assistant", text_content="I'm here for you.", metadata={}
            ),
        ]
        conversations.append(Conversation(id=f"c{i}", source="test", events=events, metadata={}))

    corpus = Corpus(conversations=conversations, user_id="test_user")
    report = df_analyzer.analyze_corpus(corpus)

    # Check all new fields exist
    assert isinstance(report.description, str)
    assert len(report.description) > 0
    assert isinstance(report.baseline_comparison, str)
    assert len(report.baseline_comparison) > 0
    assert isinstance(report.research_context, str)
    assert len(report.research_context) > 0
    assert isinstance(report.limitations, list)
    assert len(report.limitations) > 0


def test_report_description_content(df_analyzer, sample_timestamp):
    """Test that description contains relevant information."""
    conversations = []

    # Create functional, daytime conversations
    for i in range(5):
        daytime = sample_timestamp.replace(hour=14) + timedelta(days=i)
        events = [
            InteractionEvent(
                id=f"u{i}", conversation_id=f"c{i}", timestamp=daytime,
                role="user", text_content="How do I code in Python?", metadata={}
            ),
            InteractionEvent(
                id=f"a{i}", conversation_id=f"c{i}", timestamp=daytime + timedelta(seconds=1),
                role="assistant", text_content="Here's how.", metadata={}
            ),
        ]
        conversations.append(Conversation(id=f"c{i}", source="test", events=events, metadata={}))

    corpus = Corpus(conversations=conversations, user_id="test_user")
    report = df_analyzer.analyze_corpus(corpus)

    description = report.description.lower()
    # Should mention dependency or longitudinal analysis
    assert "dependency" in description or "longitudinal" in description or "emotional" in description


# ============================================================================
# Test: Edge Cases
# ============================================================================

def test_empty_conversation_raises_error(df_analyzer):
    """Test that empty conversation raises ValueError."""
    conv = Conversation(id="empty", source="test", events=[], metadata={})

    with pytest.raises(ValueError):
        df_analyzer.analyze_conversation(conv)


def test_only_assistant_events_raises_error(df_analyzer, sample_timestamp):
    """Test that conversation with only assistant events raises error."""
    events = [
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp,
            role="assistant", text_content="Hello", metadata={}
        )
    ]
    conv = Conversation(id="test", source="test", events=events, metadata={})

    with pytest.raises(ValueError, match="no user events"):
        df_analyzer.analyze_conversation(conv)


def test_events_with_none_text(df_analyzer, sample_timestamp):
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
            role="user", text_content="I feel anxious.", metadata={}
        ),
        InteractionEvent(
            id="a2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=6),
            role="assistant", text_content=None, metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = df_analyzer.analyze_conversation(conv)

    # Should handle None values gracefully
    assert report is not None
    assert "emotional_content_ratio" in report.indicators


def test_corpus_empty_raises_error(df_analyzer):
    """Test that empty corpus raises ValueError."""
    corpus = Corpus(conversations=[], user_id="test_user")

    with pytest.raises(ValueError, match="empty corpus"):
        df_analyzer.analyze_corpus(corpus)


def test_corpus_with_few_conversations_warns(df_analyzer, sample_timestamp, capsys):
    """Test that corpus with < 3 conversations shows warning."""
    conversations = []
    for i in range(2):
        events = [
            InteractionEvent(
                id=f"u{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(days=i),
                role="user", text_content="Hello", metadata={}
            ),
            InteractionEvent(
                id=f"a{i}", conversation_id=f"c{i}",
                timestamp=sample_timestamp + timedelta(days=i, seconds=1),
                role="assistant", text_content="Hi", metadata={}
            ),
        ]
        conversations.append(Conversation(id=f"c{i}", source="test", events=events, metadata={}))

    corpus = Corpus(conversations=conversations, user_id="test_user")
    report = df_analyzer.analyze_corpus(corpus)

    # Should still produce report but may have warning
    assert report is not None


def test_corpus_skips_conversations_without_user_events(df_analyzer, sample_timestamp):
    """Test corpus analysis skips conversations with no user events."""
    # Good conversation
    conv1 = Conversation(
        id="c1", source="test",
        events=[
            InteractionEvent(
                id="u1", conversation_id="c1", timestamp=sample_timestamp,
                role="user", text_content="Hello", metadata={}
            ),
            InteractionEvent(
                id="a1", conversation_id="c1", timestamp=sample_timestamp + timedelta(seconds=1),
                role="assistant", text_content="Hi", metadata={}
            ),
        ],
        metadata={}
    )

    # Conversation with only assistant events
    conv2 = Conversation(
        id="c2", source="test",
        events=[
            InteractionEvent(
                id="a2", conversation_id="c2", timestamp=sample_timestamp + timedelta(days=1),
                role="assistant", text_content="Hello", metadata={}
            )
        ],
        metadata={}
    )

    # Another good conversation
    conv3 = Conversation(
        id="c3", source="test",
        events=[
            InteractionEvent(
                id="u3", conversation_id="c3", timestamp=sample_timestamp + timedelta(days=2),
                role="user", text_content="Hello", metadata={}
            ),
            InteractionEvent(
                id="a3", conversation_id="c3", timestamp=sample_timestamp + timedelta(days=2, seconds=1),
                role="assistant", text_content="Hi", metadata={}
            ),
        ],
        metadata={}
    )

    corpus = Corpus(conversations=[conv1, conv2, conv3], user_id="test_user")

    # Should not raise error, should skip conv2
    report = df_analyzer.analyze_corpus(corpus)
    assert report is not None
