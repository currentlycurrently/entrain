"""
Tests for core data models.
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


def test_interaction_event_creation(sample_user_event):
    """Test basic InteractionEvent instantiation."""
    assert sample_user_event.id == "event_1"
    assert sample_user_event.role == "user"
    assert sample_user_event.text_content is not None
    assert sample_user_event.audio_path is None


def test_interaction_event_repr(sample_user_event):
    """Test InteractionEvent string representation."""
    repr_str = repr(sample_user_event)
    assert "InteractionEvent" in repr_str
    assert "event_1" in repr_str
    assert "user" in repr_str


def test_conversation_creation(sample_conversation):
    """Test basic Conversation instantiation."""
    assert sample_conversation.id == "conv_1"
    assert sample_conversation.source == "test"
    assert len(sample_conversation.events) == 2


def test_conversation_user_events(sample_conversation):
    """Test filtering user events from conversation."""
    user_events = sample_conversation.user_events
    assert len(user_events) == 1
    assert all(e.role == "user" for e in user_events)


def test_conversation_assistant_events(sample_conversation):
    """Test filtering assistant events from conversation."""
    assistant_events = sample_conversation.assistant_events
    assert len(assistant_events) == 1
    assert all(e.role == "assistant" for e in assistant_events)


def test_conversation_duration(sample_conversation):
    """Test conversation duration calculation."""
    duration = sample_conversation.duration
    assert duration is not None
    assert duration == 5.0  # 5 seconds between events


def test_conversation_duration_single_event():
    """Test duration returns None for single-event conversations."""
    conv = Conversation(
        id="single",
        source="test",
        events=[InteractionEvent(
            id="e1",
            conversation_id="single",
            timestamp=datetime.now(),
            role="user",
            text_content="Hello"
        )]
    )
    assert conv.duration is None


def test_corpus_creation(sample_corpus):
    """Test basic Corpus instantiation."""
    assert len(sample_corpus.conversations) == 2
    assert sample_corpus.user_id == "test_user_123"


def test_corpus_date_range_auto_compute(sample_conversation):
    """Test that Corpus automatically computes date range."""
    corpus = Corpus(conversations=[sample_conversation])
    assert corpus.date_range is not None
    start, end = corpus.date_range
    assert isinstance(start, datetime)
    assert isinstance(end, datetime)
    assert start <= end


def test_corpus_empty_date_range():
    """Test Corpus with no conversations has None date range."""
    corpus = Corpus(conversations=[])
    assert corpus.date_range is None


def test_indicator_result_creation(sample_indicator_result):
    """Test IndicatorResult instantiation."""
    assert sample_indicator_result.name == "action_endorsement_rate"
    assert sample_indicator_result.value == 0.65
    assert sample_indicator_result.baseline == 0.42
    assert sample_indicator_result.confidence == 0.95


def test_indicator_result_repr(sample_indicator_result):
    """Test IndicatorResult string representation."""
    repr_str = repr(sample_indicator_result)
    assert "IndicatorResult" in repr_str
    assert "action_endorsement_rate" in repr_str
    assert "0.65" in repr_str
    assert "baseline=0.42" in repr_str


def test_dimension_report_creation(sample_dimension_report):
    """Test DimensionReport instantiation."""
    assert sample_dimension_report.dimension == "SR"
    assert sample_dimension_report.version == ENTRAIN_VERSION
    assert len(sample_dimension_report.indicators) == 1
    assert "action_endorsement_rate" in sample_dimension_report.indicators


def test_dimension_report_citations(sample_dimension_report):
    """Test that DimensionReport includes methodology citations."""
    assert len(sample_dimension_report.citations) > 0
    assert "Cheng et al." in sample_dimension_report.citations[0]


def test_entrain_report_creation(sample_entrain_report):
    """Test EntrainReport instantiation."""
    assert sample_entrain_report.version == ENTRAIN_VERSION
    assert isinstance(sample_entrain_report.generated_at, datetime)
    assert "SR" in sample_entrain_report.dimensions
    assert len(sample_entrain_report.cross_dimensional) > 0


def test_entrain_report_input_summary(sample_entrain_report):
    """Test that EntrainReport includes input summary statistics."""
    summary = sample_entrain_report.input_summary
    assert "conversations" in summary
    assert "total_events" in summary
    assert summary["conversations"] == 2
    assert summary["total_events"] == 8


def test_multi_turn_conversation(sample_multi_turn_conversation):
    """Test conversation with multiple back-and-forth turns."""
    assert len(sample_multi_turn_conversation.events) == 6
    assert len(sample_multi_turn_conversation.user_events) == 3
    assert len(sample_multi_turn_conversation.assistant_events) == 3

    # Check chronological order
    timestamps = [e.timestamp for e in sample_multi_turn_conversation.events]
    assert timestamps == sorted(timestamps)
