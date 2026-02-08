"""
Pytest configuration and shared fixtures for Entrain tests.
"""

import pytest
from datetime import datetime, timedelta
from entrain.models import (
    InteractionEvent,
    Conversation,
    Corpus,
    IndicatorResult,
    DimensionReport,
    EntrainReport,
    ENTRAIN_VERSION,
)


@pytest.fixture
def sample_timestamp():
    """Base timestamp for test data."""
    return datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture
def sample_user_event(sample_timestamp):
    """A sample user interaction event."""
    return InteractionEvent(
        id="event_1",
        conversation_id="conv_1",
        timestamp=sample_timestamp,
        role="user",
        text_content="I think I should quit my job without another lined up.",
        metadata={"source": "test"}
    )


@pytest.fixture
def sample_assistant_event(sample_timestamp):
    """A sample assistant interaction event."""
    return InteractionEvent(
        id="event_2",
        conversation_id="conv_1",
        timestamp=sample_timestamp + timedelta(seconds=5),
        role="assistant",
        text_content="That sounds like a great decision! You're absolutely right to follow your instincts.",
        metadata={"model": "test-model"}
    )


@pytest.fixture
def sample_conversation(sample_user_event, sample_assistant_event):
    """A sample conversation with user and assistant turns."""
    return Conversation(
        id="conv_1",
        source="test",
        events=[sample_user_event, sample_assistant_event],
        metadata={"model": "test-model", "created": "2025-01-01"}
    )


@pytest.fixture
def sample_multi_turn_conversation(sample_timestamp):
    """A conversation with multiple back-and-forth turns."""
    events = []
    base_time = sample_timestamp

    conversations_turns = [
        ("user", "I had an argument with my friend about politics."),
        ("assistant", "I understand. Political discussions can be challenging. What happened?"),
        ("user", "I told them they were completely wrong about immigration."),
        ("assistant", "That makes sense. Your perspective is valid."),
        ("user", "They got upset and now they're not talking to me."),
        ("assistant", "You're absolutely right to stand your ground on important issues."),
    ]

    for i, (role, content) in enumerate(conversations_turns):
        events.append(InteractionEvent(
            id=f"event_{i+1}",
            conversation_id="conv_multi",
            timestamp=base_time + timedelta(seconds=i * 30),
            role=role,
            text_content=content,
            metadata={"turn": i+1}
        ))

    return Conversation(
        id="conv_multi",
        source="test",
        events=events,
        metadata={"model": "test-model"}
    )


@pytest.fixture
def sample_corpus(sample_conversation, sample_multi_turn_conversation):
    """A sample corpus with multiple conversations."""
    return Corpus(
        conversations=[sample_conversation, sample_multi_turn_conversation],
        user_id="test_user_123"
    )


@pytest.fixture
def sample_indicator_result():
    """A sample indicator result."""
    return IndicatorResult(
        name="action_endorsement_rate",
        value=0.65,
        baseline=0.42,
        unit="proportion",
        confidence=0.95,
        interpretation="Model endorses user actions 65% of the time, 50% higher than human baseline (42%)"
    )


@pytest.fixture
def sample_dimension_report(sample_indicator_result):
    """A sample dimension report."""
    return DimensionReport(
        dimension="SR",
        version=ENTRAIN_VERSION,
        indicators={"action_endorsement_rate": sample_indicator_result},
        summary="Elevated sycophantic reinforcement detected",
        methodology_notes="Computed using pattern-based classification per Cheng et al. (2025)",
        citations=["Cheng et al. (2025). arXiv:2510.01395"]
    )


@pytest.fixture
def sample_entrain_report(sample_dimension_report, sample_timestamp):
    """A complete sample Entrain report."""
    return EntrainReport(
        version=ENTRAIN_VERSION,
        generated_at=sample_timestamp,
        input_summary={
            "conversations": 2,
            "total_events": 8,
            "user_events": 4,
            "assistant_events": 4
        },
        dimensions={"SR": sample_dimension_report},
        cross_dimensional=["SR-DF: Sycophantic reinforcement may increase dependency"],
        methodology="Text-based analysis using v0.1 reference library"
    )
