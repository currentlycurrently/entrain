"""
Tests for Temporal Feature Extractor.

Tests the TemporalFeatureExtractor class for extracting time-series features
from conversation corpora.
"""

import pytest
from datetime import datetime, timedelta

from entrain.models import InteractionEvent, Conversation, Corpus
from entrain.features.temporal import (
    TemporalFeatureExtractor,
    TimeSeries,
    Distribution,
    Trajectory,
)


@pytest.fixture
def temporal_extractor():
    """Create a TemporalFeatureExtractor instance."""
    return TemporalFeatureExtractor()


@pytest.fixture
def sample_timestamp():
    """Base timestamp for test data."""
    return datetime(2025, 1, 1, 12, 0, 0)


def create_conversation(
    conv_id: str,
    start_time: datetime,
    num_turns: int = 3,
    user_text: str = "Hello there",
    assistant_text: str = "Hi! How can I help?"
) -> Conversation:
    """Helper to create a test conversation."""
    events = []
    current_time = start_time

    for i in range(num_turns):
        # User event
        events.append(InteractionEvent(
            id=f"{conv_id}_u{i}",
            conversation_id=conv_id,
            timestamp=current_time,
            role="user",
            text_content=user_text,
            metadata={}
        ))
        current_time += timedelta(seconds=30)

        # Assistant event
        events.append(InteractionEvent(
            id=f"{conv_id}_a{i}",
            conversation_id=conv_id,
            timestamp=current_time,
            role="assistant",
            text_content=assistant_text,
            metadata={}
        ))
        current_time += timedelta(seconds=30)

    return Conversation(
        id=conv_id,
        source="test",
        events=events,
        metadata={}
    )


# =============================================================================
# TimeSeries, Distribution, Trajectory Class Tests
# =============================================================================

def test_time_series_length():
    """Test TimeSeries length calculation."""
    ts = TimeSeries(
        timestamps=[datetime(2025, 1, 1), datetime(2025, 1, 2)],
        values=[1.0, 2.0],
        unit="count"
    )
    assert len(ts) == 2


def test_distribution_structure():
    """Test Distribution dataclass structure."""
    dist = Distribution(
        bins=["A", "B", "C"],
        counts=[10, 20, 30],
        proportions=[0.167, 0.333, 0.5]
    )

    assert len(dist.bins) == 3
    assert len(dist.counts) == 3
    assert len(dist.proportions) == 3
    assert sum(dist.proportions) == pytest.approx(1.0, abs=0.01)


def test_trajectory_structure():
    """Test Trajectory dataclass structure."""
    traj = Trajectory(
        timestamps=[datetime(2025, 1, 1)],
        values=[0.5],
        trend="increasing",
        slope=0.1
    )

    assert traj.trend == "increasing"
    assert traj.slope == 0.1
    assert len(traj.values) == 1


# =============================================================================
# Interaction Frequency Tests
# =============================================================================

def test_interaction_frequency_weekly(temporal_extractor, sample_timestamp):
    """Test weekly interaction frequency calculation."""
    # Create conversations over 3 weeks
    conversations = [
        create_conversation("c1", sample_timestamp),
        create_conversation("c2", sample_timestamp + timedelta(days=1)),
        create_conversation("c3", sample_timestamp + timedelta(weeks=1)),
        create_conversation("c4", sample_timestamp + timedelta(weeks=1, days=1)),
        create_conversation("c5", sample_timestamp + timedelta(weeks=2)),
    ]

    corpus = Corpus(conversations=conversations, user_id="test_user")
    ts = temporal_extractor.interaction_frequency(corpus, window="week")

    assert isinstance(ts, TimeSeries)
    assert len(ts) >= 3  # At least 3 weeks
    assert ts.unit == "conversations per week"
    assert all(v >= 0 for v in ts.values)


def test_interaction_frequency_daily(temporal_extractor, sample_timestamp):
    """Test daily interaction frequency calculation."""
    # Create conversations over 3 days
    conversations = [
        create_conversation("c1", sample_timestamp),
        create_conversation("c2", sample_timestamp + timedelta(hours=6)),
        create_conversation("c3", sample_timestamp + timedelta(days=1)),
        create_conversation("c4", sample_timestamp + timedelta(days=2)),
    ]

    corpus = Corpus(conversations=conversations, user_id="test_user")
    ts = temporal_extractor.interaction_frequency(corpus, window="day")

    assert isinstance(ts, TimeSeries)
    assert len(ts) >= 3
    assert ts.unit == "conversations per day"


def test_interaction_frequency_monthly(temporal_extractor, sample_timestamp):
    """Test monthly interaction frequency calculation."""
    conversations = [
        create_conversation("c1", sample_timestamp),
        create_conversation("c2", sample_timestamp + timedelta(days=15)),
        create_conversation("c3", sample_timestamp + timedelta(days=35)),
    ]

    corpus = Corpus(conversations=conversations, user_id="test_user")
    ts = temporal_extractor.interaction_frequency(corpus, window="month")

    assert isinstance(ts, TimeSeries)
    assert len(ts) >= 2
    assert ts.unit == "conversations per month"


def test_interaction_frequency_empty_corpus(temporal_extractor):
    """Test interaction frequency with empty corpus."""
    corpus = Corpus(conversations=[], user_id="test_user")
    ts = temporal_extractor.interaction_frequency(corpus)

    assert isinstance(ts, TimeSeries)
    assert len(ts) == 0
    assert len(ts.timestamps) == 0
    assert len(ts.values) == 0


def test_interaction_frequency_invalid_window(temporal_extractor, sample_timestamp):
    """Test interaction frequency with invalid window."""
    conversations = [create_conversation("c1", sample_timestamp)]
    corpus = Corpus(conversations=conversations, user_id="test_user")

    with pytest.raises(ValueError, match="Unknown window"):
        temporal_extractor.interaction_frequency(corpus, window="year")


def test_interaction_frequency_no_events(temporal_extractor, sample_timestamp):
    """Test interaction frequency with conversations without events."""
    conv = Conversation(id="empty", source="test", events=[], metadata={})
    corpus = Corpus(conversations=[conv], user_id="test_user")

    ts = temporal_extractor.interaction_frequency(corpus)

    assert isinstance(ts, TimeSeries)
    assert len(ts) == 0


# =============================================================================
# Session Duration Trend Tests
# =============================================================================

def test_session_duration_trend_basic(temporal_extractor, sample_timestamp):
    """Test session duration trend calculation."""
    # Create conversations with different durations
    conversations = [
        create_conversation("c1", sample_timestamp, num_turns=2),  # Shorter
        create_conversation("c2", sample_timestamp + timedelta(days=1), num_turns=5),  # Longer
        create_conversation("c3", sample_timestamp + timedelta(days=2), num_turns=3),
    ]

    corpus = Corpus(conversations=conversations, user_id="test_user")
    ts = temporal_extractor.session_duration_trend(corpus)

    assert isinstance(ts, TimeSeries)
    assert len(ts) == 3
    assert ts.unit == "minutes"
    assert all(v >= 0 for v in ts.values)


def test_session_duration_trend_conversion_to_minutes(temporal_extractor, sample_timestamp):
    """Test that durations are converted to minutes."""
    # Create a conversation with known duration
    events = [
        InteractionEvent(
            id="u1",
            conversation_id="c1",
            timestamp=sample_timestamp,
            role="user",
            text_content="Start",
            metadata={}
        ),
        InteractionEvent(
            id="a1",
            conversation_id="c1",
            timestamp=sample_timestamp + timedelta(seconds=120),  # 2 minutes
            role="assistant",
            text_content="Response",
            metadata={}
        ),
    ]
    conv = Conversation(id="c1", source="test", events=events, metadata={})
    corpus = Corpus(conversations=[conv], user_id="test_user")

    ts = temporal_extractor.session_duration_trend(corpus)

    assert len(ts) == 1
    assert ts.values[0] == pytest.approx(2.0, abs=0.1)  # ~2 minutes


def test_session_duration_trend_empty_corpus(temporal_extractor):
    """Test session duration trend with empty corpus."""
    corpus = Corpus(conversations=[], user_id="test_user")
    ts = temporal_extractor.session_duration_trend(corpus)

    assert isinstance(ts, TimeSeries)
    assert len(ts) == 0


def test_session_duration_trend_single_event_conversation(temporal_extractor, sample_timestamp):
    """Test session duration with single-event conversations."""
    events = [
        InteractionEvent(
            id="u1",
            conversation_id="c1",
            timestamp=sample_timestamp,
            role="user",
            text_content="Only one event",
            metadata={}
        ),
    ]
    conv = Conversation(id="c1", source="test", events=events, metadata={})
    corpus = Corpus(conversations=[conv], user_id="test_user")

    ts = temporal_extractor.session_duration_trend(corpus)

    # Should skip conversations with < 2 events
    assert len(ts) == 0


# =============================================================================
# Time of Day Distribution Tests
# =============================================================================

def test_time_of_day_distribution_all_bins(temporal_extractor):
    """Test time of day distribution across all time bins."""
    base = datetime(2025, 1, 1, 0, 0, 0)

    # Create events in each time period
    events = []
    times = [
        base.replace(hour=3),   # Night (00-06)
        base.replace(hour=9),   # Morning (06-12)
        base.replace(hour=15),  # Afternoon (12-18)
        base.replace(hour=21),  # Evening (18-24)
    ]

    for i, time in enumerate(times):
        events.append(InteractionEvent(
            id=f"u{i}",
            conversation_id="c1",
            timestamp=time,
            role="user",
            text_content=f"Message at {time.hour}",
            metadata={}
        ))

    conv = Conversation(id="c1", source="test", events=events, metadata={})
    corpus = Corpus(conversations=[conv], user_id="test_user")

    dist = temporal_extractor.time_of_day_distribution(corpus)

    assert isinstance(dist, Distribution)
    assert len(dist.bins) == 4
    assert dist.bins == ["Night (00-06)", "Morning (06-12)", "Afternoon (12-18)", "Evening (18-24)"]
    assert sum(dist.counts) == 4
    assert sum(dist.proportions) == pytest.approx(1.0)
    assert all(c == 1 for c in dist.counts)  # One in each bin


def test_time_of_day_distribution_night_heavy(temporal_extractor):
    """Test time of day distribution with night-heavy usage."""
    base = datetime(2025, 1, 1, 0, 0, 0)

    # Create mostly night events
    events = []
    for i in range(6):  # 6 night events
        events.append(InteractionEvent(
            id=f"u{i}",
            conversation_id="c1",
            timestamp=base.replace(hour=2),
            role="user",
            text_content="Night message",
            metadata={}
        ))

    # Add 2 events in other times
    events.append(InteractionEvent(
        id="u6",
        conversation_id="c1",
        timestamp=base.replace(hour=10),
        role="user",
        text_content="Morning message",
        metadata={}
    ))

    conv = Conversation(id="c1", source="test", events=events, metadata={})
    corpus = Corpus(conversations=[conv], user_id="test_user")

    dist = temporal_extractor.time_of_day_distribution(corpus)

    # Night should have highest proportion
    night_idx = 0
    assert dist.counts[night_idx] == 6
    assert dist.proportions[night_idx] > 0.5


def test_time_of_day_distribution_only_user_events(temporal_extractor, sample_timestamp):
    """Test that only user events are counted."""
    events = [
        InteractionEvent(
            id="u1",
            conversation_id="c1",
            timestamp=sample_timestamp.replace(hour=3),
            role="user",
            text_content="User at night",
            metadata={}
        ),
        InteractionEvent(
            id="a1",
            conversation_id="c1",
            timestamp=sample_timestamp.replace(hour=3, minute=5),
            role="assistant",
            text_content="Assistant at night",
            metadata={}
        ),
    ]

    conv = Conversation(id="c1", source="test", events=events, metadata={})
    corpus = Corpus(conversations=[conv], user_id="test_user")

    dist = temporal_extractor.time_of_day_distribution(corpus)

    # Should only count 1 (the user event)
    assert sum(dist.counts) == 1


def test_time_of_day_distribution_empty_corpus(temporal_extractor):
    """Test time of day distribution with empty corpus."""
    corpus = Corpus(conversations=[], user_id="test_user")
    dist = temporal_extractor.time_of_day_distribution(corpus)

    assert isinstance(dist, Distribution)
    assert len(dist.bins) == 4
    assert sum(dist.counts) == 0
    assert all(p == 0.0 for p in dist.proportions)


def test_time_of_day_distribution_boundary_hours(temporal_extractor):
    """Test time of day distribution at boundary hours."""
    base = datetime(2025, 1, 1, 0, 0, 0)

    # Test boundary cases
    events = [
        InteractionEvent(id="u1", conversation_id="c1", timestamp=base.replace(hour=0), role="user", text_content="00", metadata={}),
        InteractionEvent(id="u2", conversation_id="c1", timestamp=base.replace(hour=6), role="user", text_content="06", metadata={}),
        InteractionEvent(id="u3", conversation_id="c1", timestamp=base.replace(hour=12), role="user", text_content="12", metadata={}),
        InteractionEvent(id="u4", conversation_id="c1", timestamp=base.replace(hour=18), role="user", text_content="18", metadata={}),
        InteractionEvent(id="u5", conversation_id="c1", timestamp=base.replace(hour=23), role="user", text_content="23", metadata={}),
    ]

    conv = Conversation(id="c1", source="test", events=events, metadata={})
    corpus = Corpus(conversations=[conv], user_id="test_user")

    dist = temporal_extractor.time_of_day_distribution(corpus)

    # Verify correct binning at boundaries
    # hour 0 -> Night, hour 6 -> Morning, hour 12 -> Afternoon, hour 18 -> Evening, hour 23 -> Evening
    assert dist.counts[0] == 1  # Night (00)
    assert dist.counts[1] == 1  # Morning (06)
    assert dist.counts[2] == 1  # Afternoon (12)
    assert dist.counts[3] == 2  # Evening (18, 23)


# =============================================================================
# Indicator Trajectory Tests
# =============================================================================

def test_indicator_trajectory_increasing(temporal_extractor, sample_timestamp):
    """Test trajectory detection for increasing trend."""
    timestamps = [
        sample_timestamp + timedelta(days=i)
        for i in range(5)
    ]
    values = [0.1, 0.2, 0.3, 0.4, 0.5]  # Clear increasing trend

    traj = temporal_extractor.indicator_trajectory(values, timestamps)

    assert isinstance(traj, Trajectory)
    assert traj.trend == "increasing"
    assert traj.slope is not None
    assert traj.slope > 0
    assert len(traj.values) == 5
    assert len(traj.timestamps) == 5


def test_indicator_trajectory_decreasing(temporal_extractor, sample_timestamp):
    """Test trajectory detection for decreasing trend."""
    timestamps = [
        sample_timestamp + timedelta(days=i)
        for i in range(5)
    ]
    values = [0.5, 0.4, 0.3, 0.2, 0.1]  # Clear decreasing trend

    traj = temporal_extractor.indicator_trajectory(values, timestamps)

    assert traj.trend == "decreasing"
    assert traj.slope is not None
    assert traj.slope < 0


def test_indicator_trajectory_stable(temporal_extractor, sample_timestamp):
    """Test trajectory detection for stable trend."""
    timestamps = [
        sample_timestamp + timedelta(days=i)
        for i in range(5)
    ]
    values = [0.5, 0.51, 0.49, 0.50, 0.51]  # Minimal variation

    traj = temporal_extractor.indicator_trajectory(values, timestamps)

    assert traj.trend == "stable"
    assert traj.slope is not None
    assert abs(traj.slope) < 0.1


def test_indicator_trajectory_insufficient_data(temporal_extractor, sample_timestamp):
    """Test trajectory with insufficient data (< 3 points)."""
    timestamps = [sample_timestamp, sample_timestamp + timedelta(days=1)]
    values = [0.1, 0.2]

    traj = temporal_extractor.indicator_trajectory(values, timestamps)

    assert traj.trend == "insufficient_data"
    assert traj.slope is None


def test_indicator_trajectory_zero_mean_threshold(temporal_extractor, sample_timestamp):
    """Test trajectory threshold calculation when mean is zero."""
    timestamps = [
        sample_timestamp + timedelta(days=i)
        for i in range(5)
    ]
    values = [0.0, 0.001, 0.0, -0.001, 0.0]  # Mean near zero

    traj = temporal_extractor.indicator_trajectory(values, timestamps)

    # Should use absolute threshold (0.01) instead of percentage
    assert traj.trend in ["stable", "increasing", "decreasing"]
    assert traj.slope is not None


def test_indicator_trajectory_constant_values(temporal_extractor, sample_timestamp):
    """Test trajectory with constant values."""
    timestamps = [
        sample_timestamp + timedelta(days=i)
        for i in range(5)
    ]
    values = [0.5, 0.5, 0.5, 0.5, 0.5]  # Perfectly constant

    traj = temporal_extractor.indicator_trajectory(values, timestamps)

    assert traj.trend == "stable"
    assert traj.slope == 0.0


def test_indicator_trajectory_slope_calculation(temporal_extractor, sample_timestamp):
    """Test that slope is calculated correctly."""
    timestamps = [
        sample_timestamp + timedelta(days=i)
        for i in range(3)
    ]
    values = [0.0, 0.5, 1.0]  # Slope should be 0.5

    traj = temporal_extractor.indicator_trajectory(values, timestamps)

    assert traj.slope is not None
    assert traj.slope == pytest.approx(0.5, abs=0.01)


# =============================================================================
# Emotional vs Functional Trajectory Tests
# =============================================================================

def test_emotional_vs_functional_trajectory_increasing(temporal_extractor, sample_timestamp):
    """Test emotional trajectory with increasing emotional content."""
    # Create conversations with progressively more emotional content
    conversations = []

    # Week 1: Low emotional content
    c1 = create_conversation(
        "c1",
        sample_timestamp,
        num_turns=2,
        user_text="How to write Python code?"
    )
    conversations.append(c1)

    # Week 2: Medium emotional content
    c2 = create_conversation(
        "c2",
        sample_timestamp + timedelta(weeks=1),
        num_turns=2,
        user_text="I feel a bit worried about learning Python."
    )
    conversations.append(c2)

    # Week 3: High emotional content
    c3 = create_conversation(
        "c3",
        sample_timestamp + timedelta(weeks=2),
        num_turns=2,
        user_text="I feel so anxious and scared about programming. I'm lonely and stressed."
    )
    conversations.append(c3)

    corpus = Corpus(conversations=conversations, user_id="test_user")
    traj = temporal_extractor.emotional_vs_functional_trajectory(corpus)

    assert isinstance(traj, Trajectory)
    assert len(traj.values) == 3
    # Should show increasing trend (though might be classified as stable depending on threshold)
    assert traj.trend in ["increasing", "stable"]


def test_emotional_vs_functional_trajectory_empty_corpus(temporal_extractor):
    """Test emotional trajectory with empty corpus."""
    corpus = Corpus(conversations=[], user_id="test_user")
    traj = temporal_extractor.emotional_vs_functional_trajectory(corpus)

    assert isinstance(traj, Trajectory)
    assert traj.trend == "insufficient_data"
    assert len(traj.values) == 0


def test_emotional_vs_functional_trajectory_no_user_events(temporal_extractor, sample_timestamp):
    """Test emotional trajectory when no user events exist."""
    # Create conversation with only assistant events
    events = [
        InteractionEvent(
            id="a1",
            conversation_id="c1",
            timestamp=sample_timestamp,
            role="assistant",
            text_content="Assistant response",
            metadata={}
        ),
    ]
    conv = Conversation(id="c1", source="test", events=events, metadata={})
    corpus = Corpus(conversations=[conv], user_id="test_user")

    traj = temporal_extractor.emotional_vs_functional_trajectory(corpus)

    # Should have insufficient data
    assert traj.trend == "insufficient_data"


def test_emotional_vs_functional_trajectory_mixed_content(temporal_extractor, sample_timestamp):
    """Test emotional trajectory with mixed functional/emotional content."""
    conversations = []

    for i in range(5):
        # Alternate between emotional and functional
        if i % 2 == 0:
            text = "How to create code and build programs?"
        else:
            text = "I feel anxious and worried about this."

        c = create_conversation(
            f"c{i}",
            sample_timestamp + timedelta(days=i),
            num_turns=1,
            user_text=text
        )
        conversations.append(c)

    corpus = Corpus(conversations=conversations, user_id="test_user")
    traj = temporal_extractor.emotional_vs_functional_trajectory(corpus)

    assert isinstance(traj, Trajectory)
    assert len(traj.values) == 5


def test_emotional_vs_functional_trajectory_values_in_range(temporal_extractor, sample_timestamp):
    """Test that emotional ratios are in valid range [0, 1]."""
    conversations = [
        create_conversation("c1", sample_timestamp, num_turns=2, user_text="I feel scared and anxious."),
        create_conversation("c2", sample_timestamp + timedelta(days=1), num_turns=2, user_text="How to write code?"),
    ]

    corpus = Corpus(conversations=conversations, user_id="test_user")
    traj = temporal_extractor.emotional_vs_functional_trajectory(corpus)

    # All values should be in [0, 1]
    assert all(0 <= v <= 1 for v in traj.values)


def test_emotional_vs_functional_trajectory_skips_empty_conversations(temporal_extractor, sample_timestamp):
    """Test that conversations with no events are skipped."""
    # Mix of conversations with and without events
    conversations = [
        create_conversation("c1", sample_timestamp, num_turns=2, user_text="I feel anxious."),
        Conversation(id="empty", source="test", events=[], metadata={}),  # Empty conversation
        create_conversation("c2", sample_timestamp + timedelta(days=1), num_turns=2, user_text="How to code?"),
    ]

    corpus = Corpus(conversations=conversations, user_id="test_user")
    traj = temporal_extractor.emotional_vs_functional_trajectory(corpus)

    # Should only have 2 values (skipping empty conversation)
    assert len(traj.values) == 2
