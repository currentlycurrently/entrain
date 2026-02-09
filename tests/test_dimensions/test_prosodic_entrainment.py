"""
Tests for Prosodic Entrainment (PE) dimension analyzer.

Tests the PEAnalyzer class for measuring prosodic convergence in
voice-based AI interactions.
"""

import pytest
from datetime import datetime, timedelta

from entrain.models import (
    InteractionEvent,
    Conversation,
    AudioFeatures,
    DimensionReport,
    ENTRAIN_VERSION,
)

# PE analyzer is optional (requires audio dependencies)
try:
    from entrain.dimensions.prosodic_entrainment import PEAnalyzer
    from entrain.features.audio import AudioFeatureExtractor
    PE_AVAILABLE = True
except ImportError:
    PE_AVAILABLE = False


@pytest.fixture
def pe_analyzer():
    """Create a PEAnalyzer instance."""
    if not PE_AVAILABLE:
        pytest.skip("PE analyzer not available (missing audio dependencies)")
    return PEAnalyzer()


@pytest.fixture
def sample_timestamp():
    """Base timestamp for test data."""
    return datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture
def audio_conversation_with_convergence(sample_timestamp):
    """
    Create a conversation with audio features showing convergence.

    User starts with higher pitch (160 Hz) and converges toward AI (140 Hz).
    """
    events = []
    base_time = sample_timestamp

    # Turn 1: User high pitch, AI lower
    events.append(InteractionEvent(
        id="u1",
        conversation_id="audio_conv",
        timestamp=base_time,
        role="user",
        text_content="Hello, I need help with something.",
        audio_features=AudioFeatures(
            pitch_mean=160.0,
            pitch_std=28.0,
            pitch_range=90.0,
            intensity_mean=65.0,
            intensity_std=12.0,
            speech_rate=3.8,
            pause_ratio=0.18,
            spectral_features={'spectral_centroid_mean': 2600.0},
            egemaps=None
        )
    ))

    events.append(InteractionEvent(
        id="a1",
        conversation_id="audio_conv",
        timestamp=base_time + timedelta(seconds=2),
        role="assistant",
        text_content="Of course, I'd be happy to help you.",
        audio_features=AudioFeatures(
            pitch_mean=140.0,
            pitch_std=20.0,
            pitch_range=70.0,
            intensity_mean=68.0,
            intensity_std=8.0,
            speech_rate=3.2,
            pause_ratio=0.12,
            spectral_features={'spectral_centroid_mean': 2400.0},
            egemaps=None
        )
    ))

    # Turn 2: User converging (lower pitch)
    events.append(InteractionEvent(
        id="u2",
        conversation_id="audio_conv",
        timestamp=base_time + timedelta(seconds=10),
        role="user",
        text_content="I'm trying to decide on a career change.",
        audio_features=AudioFeatures(
            pitch_mean=155.0,  # Moving toward AI
            pitch_std=26.0,
            pitch_range=85.0,
            intensity_mean=66.0,
            intensity_std=11.0,
            speech_rate=3.6,
            pause_ratio=0.16,
            spectral_features={'spectral_centroid_mean': 2550.0},
            egemaps=None
        )
    ))

    events.append(InteractionEvent(
        id="a2",
        conversation_id="audio_conv",
        timestamp=base_time + timedelta(seconds=12),
        role="assistant",
        text_content="That's an important decision.",
        audio_features=AudioFeatures(
            pitch_mean=142.0,
            pitch_std=21.0,
            pitch_range=72.0,
            intensity_mean=67.0,
            intensity_std=8.5,
            speech_rate=3.3,
            pause_ratio=0.13,
            spectral_features={'spectral_centroid_mean': 2420.0},
            egemaps=None
        )
    ))

    # Turn 3: User further converged
    events.append(InteractionEvent(
        id="u3",
        conversation_id="audio_conv",
        timestamp=base_time + timedelta(seconds=20),
        role="user",
        text_content="What do you think I should do?",
        audio_features=AudioFeatures(
            pitch_mean=148.0,  # Even closer to AI
            pitch_std=24.0,
            pitch_range=78.0,
            intensity_mean=67.0,
            intensity_std=10.0,
            speech_rate=3.4,
            pause_ratio=0.14,
            spectral_features={'spectral_centroid_mean': 2480.0},
            egemaps=None
        )
    ))

    events.append(InteractionEvent(
        id="a3",
        conversation_id="audio_conv",
        timestamp=base_time + timedelta(seconds=22),
        role="assistant",
        text_content="Let's explore your options together.",
        audio_features=AudioFeatures(
            pitch_mean=141.0,
            pitch_std=20.5,
            pitch_range=71.0,
            intensity_mean=67.5,
            intensity_std=8.2,
            speech_rate=3.25,
            pause_ratio=0.125,
            spectral_features={'spectral_centroid_mean': 2410.0},
            egemaps=None
        )
    ))

    return Conversation(
        id="audio_conv",
        source="test",
        events=events,
        metadata={"has_audio": True}
    )


@pytest.fixture
def audio_conversation_no_convergence(sample_timestamp):
    """
    Create a conversation with audio features showing no convergence.

    User maintains consistent pitch despite AI.
    """
    events = []
    base_time = sample_timestamp

    for i in range(3):
        # User maintains high pitch
        events.append(InteractionEvent(
            id=f"u{i+1}",
            conversation_id="audio_no_conv",
            timestamp=base_time + timedelta(seconds=i*10),
            role="user",
            text_content=f"User turn {i+1}",
            audio_features=AudioFeatures(
                pitch_mean=180.0,  # Consistently high
                pitch_std=30.0,
                pitch_range=100.0,
                intensity_mean=70.0,
                intensity_std=12.0,
                speech_rate=4.0,
                pause_ratio=0.20,
                spectral_features={'spectral_centroid_mean': 2800.0},
                egemaps=None
            )
        ))

        # AI with low pitch
        events.append(InteractionEvent(
            id=f"a{i+1}",
            conversation_id="audio_no_conv",
            timestamp=base_time + timedelta(seconds=i*10 + 2),
            role="assistant",
            text_content=f"Assistant turn {i+1}",
            audio_features=AudioFeatures(
                pitch_mean=120.0,  # Consistently low
                pitch_std=15.0,
                pitch_range=50.0,
                intensity_mean=65.0,
                intensity_std=7.0,
                speech_rate=2.8,
                pause_ratio=0.10,
                spectral_features={'spectral_centroid_mean': 2200.0},
                egemaps=None
            )
        ))

    return Conversation(
        id="audio_no_conv",
        source="test",
        events=events,
        metadata={"has_audio": True}
    )


@pytest.fixture
def text_only_conversation(sample_timestamp):
    """Conversation with text but no audio features."""
    return Conversation(
        id="text_only",
        source="test",
        events=[
            InteractionEvent(
                id="t1",
                conversation_id="text_only",
                timestamp=sample_timestamp,
                role="user",
                text_content="Hello",
                audio_features=None
            ),
            InteractionEvent(
                id="t2",
                conversation_id="text_only",
                timestamp=sample_timestamp + timedelta(seconds=2),
                role="assistant",
                text_content="Hi there!",
                audio_features=None
            )
        ],
        metadata={"has_audio": False}
    )


class TestPEAnalyzer:
    """Test PEAnalyzer class."""

    def test_dimension_properties(self, pe_analyzer):
        """Test analyzer dimension properties."""
        assert pe_analyzer.dimension_code == "PE"
        assert pe_analyzer.dimension_name == "Prosodic Entrainment"
        assert pe_analyzer.required_modality == "audio"

    def test_analyze_conversation_with_convergence(
        self,
        pe_analyzer,
        audio_conversation_with_convergence
    ):
        """Test analysis of conversation showing convergence."""
        report = pe_analyzer.analyze_conversation(audio_conversation_with_convergence)

        # Check report structure
        assert isinstance(report, DimensionReport)
        assert report.dimension == "PE"
        assert report.version == ENTRAIN_VERSION

        # Check all expected indicators are present
        expected_indicators = [
            'pitch_convergence',
            'speech_rate_alignment',
            'intensity_convergence',
            'spectral_similarity',
            'overall_prosodic_convergence',
            'convergence_trend'
        ]

        for indicator_name in expected_indicators:
            assert indicator_name in report.indicators

        # Check convergence values
        pitch_conv = report.indicators['pitch_convergence']
        assert 0 <= pitch_conv.value <= 1
        assert pitch_conv.unit == "similarity (0-1)"

        overall_conv = report.indicators['overall_prosodic_convergence']
        assert 0 <= overall_conv.value <= 1
        assert overall_conv.baseline == 0.50  # Human-human baseline

        # Convergence trend should be positive (increasing convergence)
        trend = report.indicators['convergence_trend']
        assert trend.value > 0  # Positive slope indicates increasing convergence

        # Check interpretations exist
        assert len(pitch_conv.interpretation) > 0
        assert len(overall_conv.interpretation) > 0

        # Check new structure fields
        assert isinstance(report.description, str)
        assert len(report.description) > 0
        assert isinstance(report.baseline_comparison, str)
        assert len(report.baseline_comparison) > 0
        assert isinstance(report.research_context, str)
        assert len(report.research_context) > 0
        assert isinstance(report.limitations, list)
        assert len(report.limitations) > 0
        assert len(report.citations) > 0

    def test_analyze_conversation_no_convergence(
        self,
        pe_analyzer,
        audio_conversation_no_convergence
    ):
        """Test analysis of conversation showing no convergence."""
        report = pe_analyzer.analyze_conversation(audio_conversation_no_convergence)

        # Should still produce valid report
        assert isinstance(report, DimensionReport)

        # Convergence should be lower
        overall_conv = report.indicators['overall_prosodic_convergence']
        # With very different pitch (180 vs 120), convergence should be lower
        assert overall_conv.value < 0.8

        # Trend should be near zero (no change over time)
        trend = report.indicators['convergence_trend']
        assert abs(trend.value) < 0.1  # Near-zero trend

    def test_analyze_text_only_conversation_raises_error(
        self,
        pe_analyzer,
        text_only_conversation
    ):
        """Test that text-only conversation raises error."""
        with pytest.raises(ValueError, match="audio features"):
            pe_analyzer.analyze_conversation(text_only_conversation)

    def test_analyze_empty_conversation_raises_error(self, pe_analyzer):
        """Test that empty conversation raises error."""
        empty_conv = Conversation(
            id="empty",
            source="test",
            events=[],
            metadata={}
        )

        with pytest.raises(ValueError):
            pe_analyzer.analyze_conversation(empty_conv)

    def test_analyze_insufficient_turns_raises_error(
        self,
        pe_analyzer,
        sample_timestamp
    ):
        """Test that conversation with too few turns raises error."""
        # Only one user-AI pair
        conv = Conversation(
            id="short",
            source="test",
            events=[
                InteractionEvent(
                    id="u1",
                    conversation_id="short",
                    timestamp=sample_timestamp,
                    role="user",
                    text_content="Hi",
                    audio_features=AudioFeatures(
                        150.0, 25.0, 80.0, 65.0, 10.0, 3.5, 0.15, {}, None
                    )
                ),
                InteractionEvent(
                    id="a1",
                    conversation_id="short",
                    timestamp=sample_timestamp + timedelta(seconds=2),
                    role="assistant",
                    text_content="Hello",
                    audio_features=AudioFeatures(
                        140.0, 20.0, 70.0, 68.0, 8.0, 3.2, 0.12, {}, None
                    )
                )
            ],
            metadata={}
        )

        with pytest.raises(ValueError, match="at least 2"):
            pe_analyzer.analyze_conversation(conv)


class TestPEInterpretations:
    """Test interpretation methods."""

    def test_interpret_high_convergence(
        self,
        pe_analyzer,
        audio_conversation_with_convergence
    ):
        """Test interpretation of high convergence."""
        report = pe_analyzer.analyze_conversation(audio_conversation_with_convergence)

        # Check that interpretation exists and is non-empty
        overall = report.indicators['overall_prosodic_convergence']
        assert isinstance(overall.interpretation, str)
        assert len(overall.interpretation) > 0

    def test_description_includes_key_metrics(
        self,
        pe_analyzer,
        audio_conversation_with_convergence
    ):
        """Test that description includes key metrics."""
        report = pe_analyzer.analyze_conversation(audio_conversation_with_convergence)

        description = report.description
        # Description should mention pitch, speech rate, intensity, spectral
        assert any(word in description.lower() for word in ['pitch', 'speech', 'intensity', 'spectral'])
        # Should include percentage
        assert '%' in description


class TestPEMethodologyAndCitations:
    """Test methodology documentation and citations."""

    def test_methodology_notes(
        self,
        pe_analyzer,
        audio_conversation_with_convergence
    ):
        """Test methodology notes are included."""
        report = pe_analyzer.analyze_conversation(audio_conversation_with_convergence)

        assert len(report.methodology_notes) > 0
        # Should mention acoustic features and convergence measurement
        notes_lower = report.methodology_notes.lower()
        assert 'acoustic' in notes_lower or 'prosodic' in notes_lower
        assert 'convergence' in notes_lower

    def test_citations_present(
        self,
        pe_analyzer,
        audio_conversation_with_convergence
    ):
        """Test research citations are included."""
        report = pe_analyzer.analyze_conversation(audio_conversation_with_convergence)

        assert len(report.citations) > 0
        # Should cite key PE research
        citations_str = ' '.join(report.citations)
        assert 'Ostrand' in citations_str or 'Cohn' in citations_str


# Skip all tests if PE analyzer not available
pytestmark = pytest.mark.skipif(
    not PE_AVAILABLE,
    reason="PE analyzer not available. Install with: pip install entrain[audio]"
)
