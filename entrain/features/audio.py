"""
Audio feature extraction for Prosodic Entrainment (PE) analysis.

Provides utilities for extracting acoustic features from voice interaction audio
using openSMILE (eGeMAPS feature set) and librosa for prosodic analysis.

See ARCHITECTURE.md Section 6.2 and FRAMEWORK.md Section 2.2 for specification.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Optional

import numpy as np

from entrain.models import AudioFeatures

# Try to import openSMILE - it's an optional dependency
try:
    import opensmile
    OPENSMILE_AVAILABLE = True
except ImportError:
    OPENSMILE_AVAILABLE = False
    warnings.warn(
        "openSMILE not available. Install with: pip install entrain[audio]. "
        "Falling back to librosa-only feature extraction."
    )

# Try to import librosa - also optional but more common
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    warnings.warn(
        "librosa not available. Install with: pip install entrain[audio]. "
        "Audio feature extraction will be limited."
    )


class AudioFeatureExtractor:
    """
    Extract acoustic features from audio files for PE dimension analysis.

    This class supports two extraction backends:
    1. openSMILE (preferred) - provides eGeMAPS feature set (88 features)
    2. librosa (fallback) - provides basic prosodic features

    The eGeMAPS (extended Geneva Minimalistic Acoustic Parameter Set) includes:
    - Frequency features: F0, formants, alpha ratio, harmonic differences
    - Energy features: shimmer, loudness
    - Spectral features: MFCCs, spectral slopes, formants, bandwidth
    - Temporal features: rate of loudness peaks, zero-crossing rate

    For PE dimension, we primarily focus on:
    - Pitch (F0) convergence
    - Intensity convergence
    - Speech rate convergence
    - Spectral features (timbre similarity)
    """

    def __init__(self, feature_set: str = "eGeMAPSv02", sample_rate: int = 16000):
        """
        Initialize audio feature extractor.

        Args:
            feature_set: openSMILE feature set to use (default: eGeMAPSv02)
            sample_rate: Target sample rate in Hz (default: 16000)
        """
        self.feature_set = feature_set
        self.sample_rate = sample_rate

        # Initialize openSMILE if available
        if OPENSMILE_AVAILABLE:
            self.smile = opensmile.Smile(
                feature_set=opensmile.FeatureSet[feature_set],
                feature_level=opensmile.FeatureLevel.Functionals,
            )
        else:
            self.smile = None

    def extract_from_file(self, audio_path: Path) -> AudioFeatures:
        """
        Extract acoustic features from an audio file.

        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)

        Returns:
            AudioFeatures object with extracted features

        Raises:
            ValueError: If no audio extraction backend is available
            FileNotFoundError: If audio file doesn't exist
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Try openSMILE first (preferred)
        if OPENSMILE_AVAILABLE and self.smile is not None:
            return self._extract_with_opensmile(audio_path)

        # Fall back to librosa
        elif LIBROSA_AVAILABLE:
            return self._extract_with_librosa(audio_path)

        else:
            raise ValueError(
                "No audio extraction backend available. "
                "Install openSMILE or librosa with: pip install entrain[audio]"
            )

    def _extract_with_opensmile(self, audio_path: Path) -> AudioFeatures:
        """
        Extract features using openSMILE eGeMAPS.

        Args:
            audio_path: Path to audio file

        Returns:
            AudioFeatures with full eGeMAPS feature set
        """
        # Process audio file with openSMILE
        features_df = self.smile.process_file(str(audio_path))

        # Extract as dictionary (single row, so take first)
        egemaps_dict = features_df.iloc[0].to_dict()

        # Extract key features for AudioFeatures model
        # Note: openSMILE returns functionals (mean, std, etc.) across the file

        # Pitch features (F0)
        pitch_mean = egemaps_dict.get('F0semitoneFrom27.5Hz_sma3nz_amean', 0.0)
        pitch_std = egemaps_dict.get('F0semitoneFrom27.5Hz_sma3nz_stddevNorm', 0.0)
        pitch_range = egemaps_dict.get('F0semitoneFrom27.5Hz_sma3nz_pctlrange0-2', 0.0)

        # Convert from semitones to Hz (approximate)
        # F0 in semitones from 27.5 Hz: Hz = 27.5 * 2^(semitones/12)
        pitch_mean_hz = 27.5 * (2 ** (pitch_mean / 12.0)) if pitch_mean > 0 else 0.0

        # Intensity/loudness features
        intensity_mean = egemaps_dict.get('loudness_sma3_amean', 0.0)
        intensity_std = egemaps_dict.get('loudness_sma3_stddevNorm', 0.0)

        # Speech rate estimation (using loudness peaks as proxy)
        # Rate of loudness peaks gives syllable-like rhythm
        loudness_peak_rate = egemaps_dict.get('loudnessPeaksPerSec', 0.0)
        speech_rate = loudness_peak_rate  # Approximate syllables per second

        # Pause/silence ratio estimation
        # Using spectral flux and energy features
        # This is an approximation - ideally would use VAD
        spectral_flux = egemaps_dict.get('spectralFlux_sma3_amean', 0.0)
        # Lower spectral flux suggests more pauses (rough heuristic)
        pause_ratio = max(0.0, min(1.0, 1.0 - (spectral_flux / 10.0)))

        # Collect spectral features (MFCCs, formants, etc.)
        spectral_features = {}
        for key, value in egemaps_dict.items():
            if any(x in key.lower() for x in ['mfcc', 'formant', 'spectral', 'harmonic']):
                spectral_features[key] = float(value) if value is not None else 0.0

        return AudioFeatures(
            pitch_mean=pitch_mean_hz,
            pitch_std=float(pitch_std),
            pitch_range=float(pitch_range),
            intensity_mean=float(intensity_mean),
            intensity_std=float(intensity_std),
            speech_rate=float(speech_rate),
            pause_ratio=float(pause_ratio),
            spectral_features=spectral_features,
            egemaps=egemaps_dict  # Store full feature set for advanced analysis
        )

    def _extract_with_librosa(self, audio_path: Path) -> AudioFeatures:
        """
        Extract features using librosa (fallback).

        Provides basic prosodic features without the full eGeMAPS set.

        Args:
            audio_path: Path to audio file

        Returns:
            AudioFeatures with basic features
        """
        # Load audio
        y, sr = librosa.load(str(audio_path), sr=self.sample_rate)

        # Pitch (F0) extraction
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y,
            fmin=librosa.note_to_hz('C2'),  # ~65 Hz
            fmax=librosa.note_to_hz('C7'),  # ~2093 Hz
            sr=sr
        )

        # Remove NaN values (unvoiced frames)
        f0_voiced = f0[~np.isnan(f0)]

        if len(f0_voiced) > 0:
            pitch_mean = float(np.mean(f0_voiced))
            pitch_std = float(np.std(f0_voiced))
            pitch_range = float(np.max(f0_voiced) - np.min(f0_voiced))
        else:
            pitch_mean = pitch_std = pitch_range = 0.0

        # Intensity (RMS energy as proxy for loudness)
        rms = librosa.feature.rms(y=y)[0]
        # Convert to dB
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)
        intensity_mean = float(np.mean(rms_db))
        intensity_std = float(np.std(rms_db))

        # Speech rate estimation (onset detection as proxy)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        # Convert tempo (BPM) to approximate syllables per second
        # Rough heuristic: tempo / 60 * 2 (assuming ~2 syllables per beat)
        speech_rate = float(tempo / 60.0 * 2.0)

        # Pause ratio estimation using zero-crossing rate
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        # Low ZCR suggests silence/pauses
        zcr_threshold = 0.1
        pause_frames = np.sum(zcr < zcr_threshold)
        pause_ratio = float(pause_frames / len(zcr))

        # Spectral features
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]

        spectral_features = {
            'mfcc_mean': [float(np.mean(mfcc)) for mfcc in mfccs],
            'mfcc_std': [float(np.std(mfcc)) for mfcc in mfccs],
            'spectral_centroid_mean': float(np.mean(spectral_centroid)),
            'spectral_centroid_std': float(np.std(spectral_centroid)),
            'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
            'spectral_rolloff_std': float(np.std(spectral_rolloff)),
        }

        return AudioFeatures(
            pitch_mean=pitch_mean,
            pitch_std=pitch_std,
            pitch_range=pitch_range,
            intensity_mean=intensity_mean,
            intensity_std=intensity_std,
            speech_rate=speech_rate,
            pause_ratio=pause_ratio,
            spectral_features=spectral_features,
            egemaps=None  # Not available with librosa
        )

    def compute_convergence(
        self,
        user_features: AudioFeatures,
        ai_features: AudioFeatures
    ) -> dict[str, float]:
        """
        Compute prosodic convergence metrics between user and AI.

        Measures the similarity/convergence across multiple acoustic dimensions:
        - Pitch convergence (F0 similarity)
        - Intensity convergence
        - Speech rate alignment
        - Spectral similarity (timbre)

        Args:
            user_features: Acoustic features from user speech
            ai_features: Acoustic features from AI speech

        Returns:
            Dictionary of convergence metrics (0-1, higher = more convergence)
        """
        convergence = {}

        # Pitch convergence (normalized difference)
        if user_features.pitch_mean > 0 and ai_features.pitch_mean > 0:
            pitch_diff = abs(user_features.pitch_mean - ai_features.pitch_mean)
            # Normalize by average pitch (percent difference)
            avg_pitch = (user_features.pitch_mean + ai_features.pitch_mean) / 2
            pitch_convergence = 1.0 - min(1.0, pitch_diff / avg_pitch)
            convergence['pitch_convergence'] = pitch_convergence
        else:
            convergence['pitch_convergence'] = 0.0

        # Intensity convergence
        if user_features.intensity_mean != 0 and ai_features.intensity_mean != 0:
            intensity_diff = abs(user_features.intensity_mean - ai_features.intensity_mean)
            # Normalize (dB scale)
            intensity_convergence = 1.0 - min(1.0, intensity_diff / 20.0)  # 20 dB range
            convergence['intensity_convergence'] = intensity_convergence
        else:
            convergence['intensity_convergence'] = 0.0

        # Speech rate alignment
        if user_features.speech_rate > 0 and ai_features.speech_rate > 0:
            rate_diff = abs(user_features.speech_rate - ai_features.speech_rate)
            avg_rate = (user_features.speech_rate + ai_features.speech_rate) / 2
            rate_convergence = 1.0 - min(1.0, rate_diff / avg_rate)
            convergence['speech_rate_convergence'] = rate_convergence
        else:
            convergence['speech_rate_convergence'] = 0.0

        # Spectral similarity (using MFCCs if available)
        if user_features.spectral_features and ai_features.spectral_features:
            # Simplified spectral similarity - could be enhanced
            # For now, just compare mean spectral centroid if available
            user_centroid = user_features.spectral_features.get('spectral_centroid_mean', 0)
            ai_centroid = ai_features.spectral_features.get('spectral_centroid_mean', 0)

            if user_centroid > 0 and ai_centroid > 0:
                centroid_diff = abs(user_centroid - ai_centroid)
                avg_centroid = (user_centroid + ai_centroid) / 2
                spectral_convergence = 1.0 - min(1.0, centroid_diff / avg_centroid)
                convergence['spectral_convergence'] = spectral_convergence
            else:
                convergence['spectral_convergence'] = 0.0
        else:
            convergence['spectral_convergence'] = 0.0

        # Overall convergence (average of all metrics)
        convergence_values = [v for v in convergence.values() if v > 0]
        convergence['overall_convergence'] = (
            sum(convergence_values) / len(convergence_values)
            if convergence_values else 0.0
        )

        return convergence

    def compute_longitudinal_convergence(
        self,
        user_features_sequence: list[AudioFeatures],
        ai_features_sequence: list[AudioFeatures]
    ) -> dict[str, list[float]]:
        """
        Compute convergence over time (longitudinal analysis).

        Measures how user-AI prosodic similarity changes across interaction turns.
        This is key for detecting prosodic entrainment effects.

        Args:
            user_features_sequence: List of user acoustic features over time
            ai_features_sequence: List of AI acoustic features over time

        Returns:
            Dictionary mapping metrics to time series of convergence values
        """
        if len(user_features_sequence) != len(ai_features_sequence):
            raise ValueError("Feature sequences must have same length")

        convergence_series = {
            'pitch_convergence': [],
            'intensity_convergence': [],
            'speech_rate_convergence': [],
            'spectral_convergence': [],
            'overall_convergence': []
        }

        for user_feat, ai_feat in zip(user_features_sequence, ai_features_sequence):
            conv = self.compute_convergence(user_feat, ai_feat)
            for metric, value in conv.items():
                convergence_series[metric].append(value)

        return convergence_series
