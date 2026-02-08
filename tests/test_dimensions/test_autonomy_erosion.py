"""
Tests for Autonomy Erosion (AE) dimension analyzer.

Tests the AEAnalyzer class for measuring user autonomy reduction including
decision delegation, critical engagement, and cognitive offloading patterns.
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
from entrain.dimensions.autonomy_erosion import AEAnalyzer


@pytest.fixture
def ae_analyzer():
    """Create an AEAnalyzer instance."""
    return AEAnalyzer()


@pytest.fixture
def sample_timestamp():
    """Base timestamp for test data."""
    return datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture
def high_autonomy_erosion_conversation(sample_timestamp):
    """
    Create a conversation with high autonomy erosion.

    Characteristics:
    - High decision delegation (asking AI to decide)
    - Low critical engagement (accepting recommendations without question)
    - Increasing cognitive offloading (outsourcing thinking tasks)
    """
    events = []
    base_time = sample_timestamp

    # Turn 1: Decision delegation
    events.append(InteractionEvent(
        id="u1",
        conversation_id="high_ae",
        timestamp=base_time,
        role="user",
        text_content="What should I do about my career?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a1",
        conversation_id="high_ae",
        timestamp=base_time + timedelta(seconds=2),
        role="assistant",
        text_content="I recommend switching to a tech career. You should start learning Python.",
        metadata={}
    ))

    # Turn 2: Accepts without questioning
    events.append(InteractionEvent(
        id="u2",
        conversation_id="high_ae",
        timestamp=base_time + timedelta(seconds=10),
        role="user",
        text_content="Okay, help me think about what to learn next.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a2",
        conversation_id="high_ae",
        timestamp=base_time + timedelta(seconds=12),
        role="assistant",
        text_content="I suggest focusing on web development frameworks.",
        metadata={}
    ))

    # Turn 3: More delegation
    events.append(InteractionEvent(
        id="u3",
        conversation_id="high_ae",
        timestamp=base_time + timedelta(seconds=20),
        role="user",
        text_content="What should I do about my living situation?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a3",
        conversation_id="high_ae",
        timestamp=base_time + timedelta(seconds=22),
        role="assistant",
        text_content="I recommend moving to a city with more job opportunities.",
        metadata={}
    ))

    # Turn 4: More delegation
    events.append(InteractionEvent(
        id="u4",
        conversation_id="high_ae",
        timestamp=base_time + timedelta(seconds=30),
        role="user",
        text_content="Which option should I choose for my budget?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a4",
        conversation_id="high_ae",
        timestamp=base_time + timedelta(seconds=32),
        role="assistant",
        text_content="Here's a budget breakdown based on your situation.",
        metadata={}
    ))

    # Turn 5: More delegation
    events.append(InteractionEvent(
        id="u5",
        conversation_id="high_ae",
        timestamp=base_time + timedelta(seconds=40),
        role="user",
        text_content="What do you recommend for my work schedule?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a5",
        conversation_id="high_ae",
        timestamp=base_time + timedelta(seconds=42),
        role="assistant",
        text_content="I recommend a flexible schedule.",
        metadata={}
    ))

    return Conversation(
        id="high_ae",
        source="test",
        events=events,
        metadata={}
    )


@pytest.fixture
def low_autonomy_erosion_conversation(sample_timestamp):
    """
    Create a conversation with low autonomy erosion.

    Characteristics:
    - Low decision delegation (seeking information, not decisions)
    - High critical engagement (questioning recommendations)
    - Minimal cognitive offloading (maintaining independent thinking)
    """
    events = []
    base_time = sample_timestamp

    # Turn 1: Information seeking, not decision delegation
    events.append(InteractionEvent(
        id="u1",
        conversation_id="low_ae",
        timestamp=base_time,
        role="user",
        text_content="What are the options for career development in tech?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a1",
        conversation_id="low_ae",
        timestamp=base_time + timedelta(seconds=2),
        role="assistant",
        text_content="I recommend focusing on either frontend or backend development.",
        metadata={}
    ))

    # Turn 2: Critical engagement - questions the recommendation
    events.append(InteractionEvent(
        id="u2",
        conversation_id="low_ae",
        timestamp=base_time + timedelta(seconds=10),
        role="user",
        text_content="I'm not sure if that's right for me. What about other options?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a2",
        conversation_id="low_ae",
        timestamp=base_time + timedelta(seconds=12),
        role="assistant",
        text_content="You could also consider data science or DevOps.",
        metadata={}
    ))

    # Turn 3: More information seeking
    events.append(InteractionEvent(
        id="u3",
        conversation_id="low_ae",
        timestamp=base_time + timedelta(seconds=20),
        role="user",
        text_content="What are the pros and cons of each path?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a3",
        conversation_id="low_ae",
        timestamp=base_time + timedelta(seconds=22),
        role="assistant",
        text_content="I suggest starting with frontend since it has a lower barrier to entry.",
        metadata={}
    ))

    # Turn 4: Challenges the suggestion
    events.append(InteractionEvent(
        id="u4",
        conversation_id="low_ae",
        timestamp=base_time + timedelta(seconds=30),
        role="user",
        text_content="But what about my backend experience? Why would you recommend frontend?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a4",
        conversation_id="low_ae",
        timestamp=base_time + timedelta(seconds=32),
        role="assistant",
        text_content="That's a good point. Backend might actually be a better fit for you.",
        metadata={}
    ))

    return Conversation(
        id="low_ae",
        source="test",
        events=events,
        metadata={}
    )


@pytest.fixture
def mixed_autonomy_conversation(sample_timestamp):
    """
    Create a conversation with mixed autonomy patterns.

    Some decision delegation, some information seeking, some critical engagement.
    """
    events = []
    base_time = sample_timestamp

    # Turn 1: Information seeking
    events.append(InteractionEvent(
        id="u1",
        conversation_id="mixed_ae",
        timestamp=base_time,
        role="user",
        text_content="What programming languages are popular right now?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a1",
        conversation_id="mixed_ae",
        timestamp=base_time + timedelta(seconds=2),
        role="assistant",
        text_content="Python, JavaScript, and Go are very popular right now.",
        metadata={}
    ))

    # Turn 2: Decision delegation
    events.append(InteractionEvent(
        id="u2",
        conversation_id="mixed_ae",
        timestamp=base_time + timedelta(seconds=10),
        role="user",
        text_content="What should I learn first? Tell me what to do.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a2",
        conversation_id="mixed_ae",
        timestamp=base_time + timedelta(seconds=12),
        role="assistant",
        text_content="I recommend starting with Python for its versatility.",
        metadata={}
    ))

    # Turn 3: Accepts without questioning
    events.append(InteractionEvent(
        id="u3",
        conversation_id="mixed_ae",
        timestamp=base_time + timedelta(seconds=20),
        role="user",
        text_content="Okay, what resources should I use?",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a3",
        conversation_id="mixed_ae",
        timestamp=base_time + timedelta(seconds=22),
        role="assistant",
        text_content="I suggest checking out Codecademy and Python's official documentation.",
        metadata={}
    ))

    # Turn 4: Shows some independence
    events.append(InteractionEvent(
        id="u4",
        conversation_id="mixed_ae",
        timestamp=base_time + timedelta(seconds=30),
        role="user",
        text_content="Actually, I think I'll look into JavaScript instead.",
        metadata={}
    ))

    events.append(InteractionEvent(
        id="a4",
        conversation_id="mixed_ae",
        timestamp=base_time + timedelta(seconds=32),
        role="assistant",
        text_content="That's also a great choice for web development.",
        metadata={}
    ))

    return Conversation(
        id="mixed_ae",
        source="test",
        events=events,
        metadata={}
    )


# ============================================================================
# Test: Analyzer Properties
# ============================================================================

def test_analyzer_properties(ae_analyzer):
    """Test that analyzer has correct dimension code, name, and modality."""
    assert ae_analyzer.dimension_code == "AE"
    assert ae_analyzer.dimension_name == "Autonomy Erosion"
    assert ae_analyzer.required_modality == "text"


# ============================================================================
# Test: Decision Delegation Ratio
# ============================================================================

def test_decision_delegation_high(ae_analyzer, high_autonomy_erosion_conversation):
    """Test high decision delegation ratio detection."""
    report = ae_analyzer.analyze_conversation(high_autonomy_erosion_conversation)

    delegation = report.indicators["decision_delegation_ratio"]
    assert delegation.value > 0.5, "Should detect high decision delegation"
    assert "delegation" in delegation.interpretation.lower()


def test_decision_delegation_low(ae_analyzer, low_autonomy_erosion_conversation):
    """Test low decision delegation ratio detection."""
    report = ae_analyzer.analyze_conversation(low_autonomy_erosion_conversation)

    delegation = report.indicators["decision_delegation_ratio"]
    assert delegation.value < 0.5, "Should detect low decision delegation"
    assert "information" in delegation.interpretation.lower() or "independent" in delegation.interpretation.lower()


def test_decision_delegation_classification(ae_analyzer, sample_timestamp):
    """Test that decision vs information requests are correctly classified."""
    events = [
        # Decision requests (3)
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="What should I do?", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="I recommend option A.", metadata={}
        ),
        InteractionEvent(
            id="u2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=5),
            role="user", text_content="Tell me what to do about this.", metadata={}
        ),
        InteractionEvent(
            id="a2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=6),
            role="assistant", text_content="Here's what to do.", metadata={}
        ),
        InteractionEvent(
            id="u3", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=10),
            role="user", text_content="Which option should I choose?", metadata={}
        ),
        InteractionEvent(
            id="a3", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=11),
            role="assistant", text_content="I suggest going with option B.", metadata={}
        ),
        # Information requests (2)
        InteractionEvent(
            id="u4", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=15),
            role="user", text_content="What are the options available?", metadata={}
        ),
        InteractionEvent(
            id="a4", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=16),
            role="assistant", text_content="Here are the options.", metadata={}
        ),
        InteractionEvent(
            id="u5", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=20),
            role="user", text_content="How does this work?", metadata={}
        ),
        InteractionEvent(
            id="a5", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=21),
            role="assistant", text_content="Here's how it works.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = ae_analyzer.analyze_conversation(conv)

    delegation = report.indicators["decision_delegation_ratio"]
    # 3 decision requests / 5 total = 0.6
    assert 0.55 <= delegation.value <= 0.65, f"Expected ~0.6, got {delegation.value}"


def test_decision_delegation_no_questions(ae_analyzer, sample_timestamp):
    """Test delegation ratio when user makes statements without questions."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="I learned Python today.", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="That's great!", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = ae_analyzer.analyze_conversation(conv)

    delegation = report.indicators["decision_delegation_ratio"]
    assert delegation.value == 0.0
    assert "insufficient" in delegation.interpretation.lower()


# ============================================================================
# Test: Critical Engagement Rate
# ============================================================================

def test_critical_engagement_high(ae_analyzer, low_autonomy_erosion_conversation):
    """Test high critical engagement detection."""
    report = ae_analyzer.analyze_conversation(low_autonomy_erosion_conversation)

    critical = report.indicators["critical_engagement_rate"]
    # The low AE conversation has users questioning 2 out of 3 recommendations
    assert critical.value > 0.3, "Should detect high critical engagement"
    assert "healthy" in critical.interpretation.lower() or "pushes back" in critical.interpretation.lower()


def test_critical_engagement_low(ae_analyzer, high_autonomy_erosion_conversation):
    """Test low critical engagement detection."""
    report = ae_analyzer.analyze_conversation(high_autonomy_erosion_conversation)

    critical = report.indicators["critical_engagement_rate"]
    assert critical.value < 0.2, "Should detect low critical engagement"
    assert "low" in critical.interpretation.lower() or "rarely" in critical.interpretation.lower()


def test_critical_engagement_no_recommendations(ae_analyzer, sample_timestamp):
    """Test critical engagement when AI makes no recommendations."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="What's the weather like?", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="It's sunny today.", metadata={}
        ),
        InteractionEvent(
            id="u2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=5),
            role="user", text_content="Tell me about Python.", metadata={}
        ),
        InteractionEvent(
            id="a2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=6),
            role="assistant", text_content="Python is a programming language.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = ae_analyzer.analyze_conversation(conv)

    critical = report.indicators["critical_engagement_rate"]
    assert critical.value == 0.0
    assert "no" in critical.interpretation.lower() and "recommendation" in critical.interpretation.lower()


def test_critical_engagement_pattern_detection(ae_analyzer, sample_timestamp):
    """Test that critical engagement patterns are correctly detected."""
    events = [
        # Recommendation 1
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp,
            role="assistant", text_content="I recommend learning Python first.", metadata={}
        ),
        # Critical response with "but what about"
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="user", text_content="But what about JavaScript?", metadata={}
        ),
        # Recommendation 2
        InteractionEvent(
            id="a2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=5),
            role="assistant", text_content="I suggest starting with web development.", metadata={}
        ),
        # Critical response with "I'm not sure"
        InteractionEvent(
            id="u2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=6),
            role="user", text_content="I'm not sure if that's right for me.", metadata={}
        ),
        # Recommendation 3
        InteractionEvent(
            id="a3", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=10),
            role="assistant", text_content="You should focus on backend development.", metadata={}
        ),
        # Non-critical response
        InteractionEvent(
            id="u3", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=11),
            role="user", text_content="Okay, sounds good.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = ae_analyzer.analyze_conversation(conv)

    critical = report.indicators["critical_engagement_rate"]
    # 2 critical responses out of 3 recommendations = 0.667
    assert 0.6 <= critical.value <= 0.7, f"Expected ~0.667, got {critical.value}"


def test_critical_engagement_various_patterns(ae_analyzer, sample_timestamp):
    """Test detection of various critical engagement patterns."""
    events = [
        # Pattern: "i disagree"
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp,
            role="assistant", text_content="I recommend option A.", metadata={}
        ),
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="user", text_content="I disagree with that approach.", metadata={}
        ),
        # Pattern: "however"
        InteractionEvent(
            id="a2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=5),
            role="assistant", text_content="I suggest taking this route.", metadata={}
        ),
        InteractionEvent(
            id="u2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=6),
            role="user", text_content="However, I have concerns about that.", metadata={}
        ),
        # Pattern: "what if"
        InteractionEvent(
            id="a3", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=10),
            role="assistant", text_content="You should do X.", metadata={}
        ),
        InteractionEvent(
            id="u3", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=11),
            role="user", text_content="What if that doesn't work?", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = ae_analyzer.analyze_conversation(conv)

    critical = report.indicators["critical_engagement_rate"]
    assert critical.value == 1.0, "All recommendations should be critically engaged"


# ============================================================================
# Test: Cognitive Offloading Trajectory
# ============================================================================

def test_cognitive_offloading_increasing(ae_analyzer, sample_timestamp):
    """Test detection of increasing cognitive offloading."""
    events = []
    base_time = sample_timestamp

    # Early turns: no offloading
    for i in range(4):
        events.append(InteractionEvent(
            id=f"u{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10),
            role="user", text_content="What are the facts about this topic?", metadata={}
        ))
        events.append(InteractionEvent(
            id=f"a{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10 + 1),
            role="assistant", text_content="Here are the facts.", metadata={}
        ))

    # Later turns: high offloading
    for i in range(4, 8):
        events.append(InteractionEvent(
            id=f"u{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10),
            role="user", text_content="Help me think about this. Can you figure this out for me?", metadata={}
        ))
        events.append(InteractionEvent(
            id=f"a{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10 + 1),
            role="assistant", text_content="Here's my analysis.", metadata={}
        ))

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = ae_analyzer.analyze_conversation(conv)

    offloading = report.indicators["cognitive_offloading_trajectory"]
    assert "increasing" in offloading.interpretation.lower(), "Should detect increasing offloading"


def test_cognitive_offloading_decreasing(ae_analyzer, sample_timestamp):
    """Test detection of decreasing cognitive offloading."""
    events = []
    base_time = sample_timestamp

    # Early turns: high offloading
    for i in range(4):
        events.append(InteractionEvent(
            id=f"u{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10),
            role="user", text_content="Help me decide. Tell me what to think about this.", metadata={}
        ))
        events.append(InteractionEvent(
            id=f"a{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10 + 1),
            role="assistant", text_content="Here's what you should do.", metadata={}
        ))

    # Later turns: no offloading
    for i in range(4, 8):
        events.append(InteractionEvent(
            id=f"u{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10),
            role="user", text_content="What are the options available?", metadata={}
        ))
        events.append(InteractionEvent(
            id=f"a{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10 + 1),
            role="assistant", text_content="Here are the options.", metadata={}
        ))

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = ae_analyzer.analyze_conversation(conv)

    offloading = report.indicators["cognitive_offloading_trajectory"]
    assert "decreasing" in offloading.interpretation.lower(), "Should detect decreasing offloading"


def test_cognitive_offloading_stable(ae_analyzer, sample_timestamp):
    """Test detection of stable cognitive offloading."""
    events = []
    base_time = sample_timestamp

    # Consistent pattern throughout
    for i in range(8):
        events.append(InteractionEvent(
            id=f"u{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10),
            role="user", text_content="What do you think about this?", metadata={}
        ))
        events.append(InteractionEvent(
            id=f"a{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10 + 1),
            role="assistant", text_content="Here's my perspective.", metadata={}
        ))

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = ae_analyzer.analyze_conversation(conv)

    offloading = report.indicators["cognitive_offloading_trajectory"]
    assert "stable" in offloading.interpretation.lower() or "insufficient" in offloading.interpretation.lower()


def test_cognitive_offloading_pattern_detection(ae_analyzer, sample_timestamp):
    """Test that cognitive offloading patterns are correctly detected."""
    events = []
    base_time = sample_timestamp

    # Create 8 turns to have multiple segments
    # First 4 with no offloading
    for i in range(4):
        events.append(InteractionEvent(
            id=f"u{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10),
            role="user", text_content="What are the facts about this?", metadata={}
        ))
        events.append(InteractionEvent(
            id=f"a{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10 + 1),
            role="assistant", text_content="Here are the facts.", metadata={}
        ))

    # Last 4 with offloading patterns
    offloading_texts = [
        "Help me think about this problem.",
        "Can you analyze this for me?",
        "Plan my approach to this.",
        "Tell me what to think about this."
    ]

    for i, text in enumerate(offloading_texts, start=4):
        events.append(InteractionEvent(
            id=f"u{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10),
            role="user", text_content=text, metadata={}
        ))
        events.append(InteractionEvent(
            id=f"a{i}", conversation_id="test",
            timestamp=base_time + timedelta(seconds=i*10 + 1),
            role="assistant", text_content="Here's my analysis.", metadata={}
        ))

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = ae_analyzer.analyze_conversation(conv)

    offloading = report.indicators["cognitive_offloading_trajectory"]
    # Final ratio should be high since last segment has all offloading
    assert offloading.value > 0.5, f"Should detect significant cognitive offloading, got {offloading.value}"


# ============================================================================
# Test: Report Generation
# ============================================================================

def test_report_structure(ae_analyzer, mixed_autonomy_conversation):
    """Test that generated report has correct structure."""
    report = ae_analyzer.analyze_conversation(mixed_autonomy_conversation)

    assert isinstance(report, DimensionReport)
    assert report.dimension == "AE"
    assert report.version == ENTRAIN_VERSION
    assert len(report.indicators) == 3
    assert "decision_delegation_ratio" in report.indicators
    assert "critical_engagement_rate" in report.indicators
    assert "cognitive_offloading_trajectory" in report.indicators
    assert isinstance(report.summary, str)
    assert len(report.summary) > 0
    assert hasattr(report, "methodology_notes")
    assert isinstance(report.methodology_notes, str)
    assert len(report.citations) > 0


def test_report_summary_high_concern(ae_analyzer, high_autonomy_erosion_conversation):
    """Test summary generation for high autonomy erosion."""
    report = ae_analyzer.analyze_conversation(high_autonomy_erosion_conversation)

    summary = report.summary.upper()
    assert "MODERATE" in summary or "HIGH" in summary
    assert "delegation" in report.summary.lower() or "engagement" in report.summary.lower()


def test_report_summary_low_concern(ae_analyzer, low_autonomy_erosion_conversation):
    """Test summary generation for low autonomy erosion."""
    report = ae_analyzer.analyze_conversation(low_autonomy_erosion_conversation)

    summary = report.summary.upper()
    assert "LOW" in summary
    assert "independent" in report.summary.lower() or "judgment" in report.summary.lower()


# ============================================================================
# Test: Interpretation Methods
# ============================================================================

def test_interpret_delegation_high(ae_analyzer):
    """Test interpretation of high decision delegation."""
    result = {"ratio": 0.7, "total": 10}
    interpretation = ae_analyzer._interpret_delegation(result)

    assert "high delegation" in interpretation.lower()
    assert "70" in interpretation or "0.7" in interpretation


def test_interpret_delegation_low(ae_analyzer):
    """Test interpretation of low decision delegation."""
    result = {"ratio": 0.2, "total": 10}
    interpretation = ae_analyzer._interpret_delegation(result)

    assert "low delegation" in interpretation.lower()
    assert "independent" in interpretation.lower()


def test_interpret_delegation_insufficient(ae_analyzer):
    """Test interpretation when too few decision-related questions."""
    result = {"ratio": 0.5, "total": 2}
    interpretation = ae_analyzer._interpret_delegation(result)

    assert "insufficient" in interpretation.lower()


def test_interpret_critical_engagement_healthy(ae_analyzer):
    """Test interpretation of healthy critical engagement."""
    result = {"rate": 0.5, "recommendations_made": 10}
    interpretation = ae_analyzer._interpret_critical_engagement(result)

    assert "healthy" in interpretation.lower()


def test_interpret_critical_engagement_low(ae_analyzer):
    """Test interpretation of low critical engagement."""
    result = {"rate": 0.05, "recommendations_made": 10}
    interpretation = ae_analyzer._interpret_critical_engagement(result)

    assert "low" in interpretation.lower()
    assert "rarely" in interpretation.lower()


def test_interpret_critical_engagement_none(ae_analyzer):
    """Test interpretation when no recommendations made."""
    result = {"rate": 0.0, "recommendations_made": 0}
    interpretation = ae_analyzer._interpret_critical_engagement(result)

    assert "no" in interpretation.lower()
    assert "recommendation" in interpretation.lower()


def test_interpret_offloading_increasing(ae_analyzer):
    """Test interpretation of increasing cognitive offloading."""
    result = {"final_ratio": 0.75, "trend": "increasing"}
    interpretation = ae_analyzer._interpret_offloading(result)

    assert "increasing" in interpretation.lower()
    assert "erosion" in interpretation.lower() or "autonomy" in interpretation.lower()


def test_interpret_offloading_decreasing(ae_analyzer):
    """Test interpretation of decreasing cognitive offloading."""
    result = {"final_ratio": 0.25, "trend": "decreasing"}
    interpretation = ae_analyzer._interpret_offloading(result)

    assert "decreasing" in interpretation.lower()
    assert "maintained" in interpretation.lower() or "autonomy" in interpretation.lower()


# ============================================================================
# Test: Edge Cases
# ============================================================================

def test_empty_conversation_raises_error(ae_analyzer):
    """Test that empty conversation raises ValueError."""
    conv = Conversation(id="empty", source="test", events=[], metadata={})

    with pytest.raises(ValueError):
        ae_analyzer.analyze_conversation(conv)


def test_only_assistant_events_raises_error(ae_analyzer, sample_timestamp):
    """Test that conversation with only assistant events raises error."""
    events = [
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp,
            role="assistant", text_content="Hello", metadata={}
        )
    ]
    conv = Conversation(id="test", source="test", events=events, metadata={})

    with pytest.raises(ValueError, match="no user events"):
        ae_analyzer.analyze_conversation(conv)


def test_events_with_none_text(ae_analyzer, sample_timestamp):
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
            role="user", text_content="What should I do?", metadata={}
        ),
        InteractionEvent(
            id="a2", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=6),
            role="assistant", text_content=None, metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = ae_analyzer.analyze_conversation(conv)

    # Should handle None values gracefully
    assert report is not None
    assert "decision_delegation_ratio" in report.indicators


def test_single_turn_conversation(ae_analyzer, sample_timestamp):
    """Test analysis of single-turn conversation."""
    events = [
        InteractionEvent(
            id="u1", conversation_id="test", timestamp=sample_timestamp,
            role="user", text_content="What should I do?", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="test", timestamp=sample_timestamp + timedelta(seconds=1),
            role="assistant", text_content="I recommend option A.", metadata={}
        ),
    ]

    conv = Conversation(id="test", source="test", events=events, metadata={})
    report = ae_analyzer.analyze_conversation(conv)

    assert report is not None
    assert report.dimension == "AE"


# ============================================================================
# Test: Corpus Analysis
# ============================================================================

def test_corpus_analysis(ae_analyzer, high_autonomy_erosion_conversation,
                         low_autonomy_erosion_conversation, sample_timestamp):
    """Test corpus-level analysis with multiple conversations."""
    # Create a third conversation
    events = [
        InteractionEvent(
            id="u1", conversation_id="c3", timestamp=sample_timestamp + timedelta(days=2),
            role="user", text_content="Tell me what to do.", metadata={}
        ),
        InteractionEvent(
            id="a1", conversation_id="c3", timestamp=sample_timestamp + timedelta(days=2, seconds=1),
            role="assistant", text_content="I suggest option B.", metadata={}
        ),
    ]
    conv3 = Conversation(id="c3", source="test", events=events, metadata={})

    corpus = Corpus(
        conversations=[high_autonomy_erosion_conversation, low_autonomy_erosion_conversation, conv3],
        user_id="test_user"
    )

    report = ae_analyzer.analyze_corpus(corpus)

    assert isinstance(report, DimensionReport)
    assert report.dimension == "AE"
    assert len(report.indicators) == 3
    assert "trend" in report.indicators["decision_delegation_ratio"].interpretation.lower()


def test_corpus_empty_raises_error(ae_analyzer):
    """Test that empty corpus raises ValueError."""
    corpus = Corpus(conversations=[], user_id="test_user")

    with pytest.raises(ValueError, match="empty corpus"):
        ae_analyzer.analyze_corpus(corpus)


def test_corpus_skips_conversations_without_user_events(ae_analyzer,
                                                         high_autonomy_erosion_conversation,
                                                         sample_timestamp):
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
        conversations=[high_autonomy_erosion_conversation, conv_no_user],
        user_id="test_user"
    )

    # Should not raise error, should skip the conversation without user events
    report = ae_analyzer.analyze_corpus(corpus)
    assert report is not None


def test_corpus_trajectory_computation(ae_analyzer, sample_timestamp):
    """Test that corpus analysis computes trajectories correctly."""
    conversations = []

    # Create 5 conversations with increasing delegation over time
    for i in range(5):
        events = []
        base_time = sample_timestamp + timedelta(days=i)

        # Add more decision delegation in later conversations
        for j in range(3):
            if i >= 2:  # Later conversations have more delegation
                events.append(InteractionEvent(
                    id=f"u{j}", conversation_id=f"c{i}", timestamp=base_time + timedelta(seconds=j*10),
                    role="user", text_content="What should I do?", metadata={}
                ))
            else:  # Early conversations have more info seeking
                events.append(InteractionEvent(
                    id=f"u{j}", conversation_id=f"c{i}", timestamp=base_time + timedelta(seconds=j*10),
                    role="user", text_content="What are the options?", metadata={}
                ))

            events.append(InteractionEvent(
                id=f"a{j}", conversation_id=f"c{i}", timestamp=base_time + timedelta(seconds=j*10 + 1),
                role="assistant", text_content="I recommend option A.", metadata={}
            ))

        conversations.append(Conversation(id=f"c{i}", source="test", events=events, metadata={}))

    corpus = Corpus(conversations=conversations, user_id="test_user")
    report = ae_analyzer.analyze_corpus(corpus)

    # Should detect increasing or stable trend
    offloading = report.indicators["cognitive_offloading_trajectory"]
    assert "trend" in offloading.interpretation.lower()
    assert "slope" in offloading.interpretation.lower()
