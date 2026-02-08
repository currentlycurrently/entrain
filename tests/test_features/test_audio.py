"""
Tests for audio feature extraction.

Tests the AudioFeatureExtractor class for extracting acoustic features
from audio files using openSMILE and librosa.
"""

import pytest
from pathlib import Path
import numpy as np

from entrain.models import AudioFeatures

# Audio extraction is optional
try:
    from entrain.features.audio import (
        AudioFeatureExtractor,
        OPENSMILE_AVAILABLE,
        LIBROSA_AVAILABLE
    )
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


@pytest.fixture
def audio_extractor():
    """Create an AudioFeatureExtractor instance."""
    if not AUDIO_AVAILABLE:
        pytest.skip("Audio dependencies not installed")
    return AudioFeatureExtractor()


@pytest.fixture
def sample_audio_features():
    """Sample audio features for testing."""
    return AudioFeatures(
        pitch_mean=150.0,  # Hz
        pitch_std=25.0,
        pitch_range=80.0,
        intensity_mean=65.0,  # dB
        intensity_std=10.0,
        speech_rate=3.5,  # syllables/sec
        pause_ratio=0.15,
        spectral_features={
            'mfcc_mean': [1.2, 0.8, -0.5, 0.3],
            'spectral_centroid_mean': 2500.0,
            'spectral_rolloff_mean': 4500.0,
        },
        egemaps=None
    )


@pytest.fixture
def sample_ai_audio_features():
    """Sample AI audio features (different from user)."""
    return AudioFeatures(
        pitch_mean=140.0,  # Hz - slightly lower
        pitch_std=20.0,
        pitch_range=70.0,
        intensity_mean=68.0,  # dB - slightly higher
        intensity_std=8.0,
        speech_rate=3.2,  # syllables/sec - slightly slower
        pause_ratio=0.12,
        spectral_features={
            'mfcc_mean': [1.0, 0.7, -0.4, 0.2],
            'spectral_centroid_mean': 2400.0,
            'spectral_rolloff_mean': 4400.0,
        },
        egemaps=None
    )


class TestAudioFeatureExtractor:
    """Test AudioFeatureExtractor class."""

    def test_initialization(self, audio_extractor):
        """Test extractor initialization."""
        assert audio_extractor.feature_set == "eGeMAPSv02"
        assert audio_extractor.sample_rate == 16000

    def test_initialization_with_custom_params(self):
        """Test extractor with custom parameters."""
        if not AUDIO_AVAILABLE:
            pytest.skip("Audio dependencies not installed")

        extractor = AudioFeatureExtractor(
            feature_set="eGeMAPSv02",
            sample_rate=22050
        )
        assert extractor.feature_set == "eGeMAPSv02"
        assert extractor.sample_rate == 22050

    def test_extract_from_nonexistent_file(self, audio_extractor):
        """Test extraction from nonexistent file raises error."""
        fake_path = Path("/nonexistent/audio.wav")
        with pytest.raises(FileNotFoundError):
            audio_extractor.extract_from_file(fake_path)

    @pytest.mark.skipif(
        not AUDIO_AVAILABLE or not (OPENSMILE_AVAILABLE or LIBROSA_AVAILABLE),
        reason="Audio backend not available"
    )
    def test_extract_features_mock(self, audio_extractor, tmp_path, monkeypatch):
        """Test feature extraction with mocked backend."""
        # Create a dummy audio file
        audio_file = tmp_path / "test.wav"
        audio_file.touch()

        # Mock the extraction to avoid requiring real audio
        def mock_extract_opensmile(self, path):
            return AudioFeatures(
                pitch_mean=150.0,
                pitch_std=25.0,
                pitch_range=80.0,
                intensity_mean=65.0,
                intensity_std=10.0,
                speech_rate=3.5,
                pause_ratio=0.15,
                spectral_features={},
                egemaps={}
            )

        def mock_extract_librosa(self, path):
            return AudioFeatures(
                pitch_mean=150.0,
                pitch_std=25.0,
                pitch_range=80.0,
                intensity_mean=65.0,
                intensity_std=10.0,
                speech_rate=3.5,
                pause_ratio=0.15,
                spectral_features={},
                egemaps=None
            )

        if OPENSMILE_AVAILABLE:
            monkeypatch.setattr(
                AudioFeatureExtractor,
                "_extract_with_opensmile",
                mock_extract_opensmile
            )
        else:
            monkeypatch.setattr(
                AudioFeatureExtractor,
                "_extract_with_librosa",
                mock_extract_librosa
            )

        features = audio_extractor.extract_from_file(audio_file)

        assert isinstance(features, AudioFeatures)
        assert features.pitch_mean > 0
        assert features.intensity_mean != 0
        assert features.speech_rate > 0
        assert 0 <= features.pause_ratio <= 1


class TestConvergenceMetrics:
    """Test convergence computation."""

    def test_compute_convergence(
        self,
        audio_extractor,
        sample_audio_features,
        sample_ai_audio_features
    ):
        """Test convergence computation between user and AI features."""
        convergence = audio_extractor.compute_convergence(
            sample_audio_features,
            sample_ai_audio_features
        )

        # Check all expected metrics are present
        assert 'pitch_convergence' in convergence
        assert 'intensity_convergence' in convergence
        assert 'speech_rate_convergence' in convergence
        assert 'spectral_convergence' in convergence
        assert 'overall_convergence' in convergence

        # Check values are in valid range [0, 1]
        for metric, value in convergence.items():
            assert 0 <= value <= 1, f"{metric} out of range: {value}"

        # Check that overall is average of components
        individual = [
            convergence['pitch_convergence'],
            convergence['intensity_convergence'],
            convergence['speech_rate_convergence'],
            convergence['spectral_convergence']
        ]
        # Filter out zeros
        individual = [v for v in individual if v > 0]
        expected_overall = sum(individual) / len(individual)
        assert abs(convergence['overall_convergence'] - expected_overall) < 0.01

    def test_compute_convergence_identical_features(
        self,
        audio_extractor,
        sample_audio_features
    ):
        """Test convergence with identical features (should be 1.0)."""
        convergence = audio_extractor.compute_convergence(
            sample_audio_features,
            sample_audio_features
        )

        # Identical features should have perfect convergence
        assert convergence['pitch_convergence'] > 0.99
        assert convergence['intensity_convergence'] > 0.99
        assert convergence['speech_rate_convergence'] > 0.99
        assert convergence['overall_convergence'] > 0.99

    def test_compute_convergence_zero_pitch(self, audio_extractor):
        """Test convergence with zero pitch (unvoiced)."""
        features1 = AudioFeatures(
            pitch_mean=0.0,  # Unvoiced
            pitch_std=0.0,
            pitch_range=0.0,
            intensity_mean=50.0,
            intensity_std=5.0,
            speech_rate=3.0,
            pause_ratio=0.5,
            spectral_features={},
            egemaps=None
        )

        features2 = AudioFeatures(
            pitch_mean=150.0,
            pitch_std=25.0,
            pitch_range=80.0,
            intensity_mean=60.0,
            intensity_std=10.0,
            speech_rate=3.5,
            pause_ratio=0.2,
            spectral_features={},
            egemaps=None
        )

        convergence = audio_extractor.compute_convergence(features1, features2)

        # Pitch convergence should be 0 when one pitch is 0
        assert convergence['pitch_convergence'] == 0.0
        # Other metrics should still work
        assert convergence['intensity_convergence'] > 0
        assert convergence['speech_rate_convergence'] > 0

    def test_longitudinal_convergence(self, audio_extractor):
        """Test longitudinal convergence tracking."""
        # Create sequences
        user_sequence = [
            AudioFeatures(150.0, 25.0, 80.0, 65.0, 10.0, 3.5, 0.15, {}, None),
            AudioFeatures(148.0, 24.0, 78.0, 66.0, 9.0, 3.4, 0.14, {}, None),
            AudioFeatures(145.0, 22.0, 75.0, 67.0, 8.0, 3.3, 0.13, {}, None),
        ]

        ai_sequence = [
            AudioFeatures(140.0, 20.0, 70.0, 68.0, 8.0, 3.2, 0.12, {}, None),
            AudioFeatures(142.0, 21.0, 72.0, 67.0, 8.5, 3.25, 0.13, {}, None),
            AudioFeatures(143.0, 21.5, 73.0, 66.5, 8.2, 3.28, 0.125, {}, None),
        ]

        convergence_series = audio_extractor.compute_longitudinal_convergence(
            user_sequence,
            ai_sequence
        )

        # Check we got time series for each metric
        assert 'pitch_convergence' in convergence_series
        assert 'overall_convergence' in convergence_series

        # Check length matches input
        assert len(convergence_series['pitch_convergence']) == 3
        assert len(convergence_series['overall_convergence']) == 3

        # Values should be in valid range
        for values in convergence_series.values():
            for v in values:
                assert 0 <= v <= 1

    def test_longitudinal_convergence_mismatched_length(self, audio_extractor):
        """Test longitudinal convergence with mismatched sequences raises error."""
        user_sequence = [
            AudioFeatures(150.0, 25.0, 80.0, 65.0, 10.0, 3.5, 0.15, {}, None),
        ]

        ai_sequence = [
            AudioFeatures(140.0, 20.0, 70.0, 68.0, 8.0, 3.2, 0.12, {}, None),
            AudioFeatures(142.0, 21.0, 72.0, 67.0, 8.5, 3.25, 0.13, {}, None),
        ]

        with pytest.raises(ValueError, match="same length"):
            audio_extractor.compute_longitudinal_convergence(
                user_sequence,
                ai_sequence
            )


class TestAudioFeaturesModel:
    """Test AudioFeatures dataclass."""

    def test_audio_features_creation(self, sample_audio_features):
        """Test AudioFeatures can be created and accessed."""
        assert sample_audio_features.pitch_mean == 150.0
        assert sample_audio_features.intensity_mean == 65.0
        assert sample_audio_features.speech_rate == 3.5
        assert sample_audio_features.pause_ratio == 0.15

    def test_audio_features_with_egemaps(self):
        """Test AudioFeatures with full eGeMAPS feature set."""
        egemaps = {
            'F0semitoneFrom27.5Hz_sma3nz_amean': 30.0,
            'loudness_sma3_amean': 0.8,
            'mfcc1_sma3_amean': 1.2,
        }

        features = AudioFeatures(
            pitch_mean=150.0,
            pitch_std=25.0,
            pitch_range=80.0,
            intensity_mean=65.0,
            intensity_std=10.0,
            speech_rate=3.5,
            pause_ratio=0.15,
            spectral_features={'mfcc_mean': [1.2, 0.8]},
            egemaps=egemaps
        )

        assert features.egemaps is not None
        assert 'F0semitoneFrom27.5Hz_sma3nz_amean' in features.egemaps
        assert features.egemaps['loudness_sma3_amean'] == 0.8


# Skip all tests if audio dependencies not available
pytestmark = pytest.mark.skipif(
    not AUDIO_AVAILABLE,
    reason="Audio dependencies not installed. Install with: pip install entrain[audio]"
)
