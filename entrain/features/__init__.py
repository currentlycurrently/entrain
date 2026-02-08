"""
Feature extraction utilities for text, temporal, and audio analysis.
"""

from entrain.features.text import TextFeatureExtractor, PatternMatch, TurnIntent, QuestionType
from entrain.features.temporal import (
    TemporalFeatureExtractor,
    TimeSeries,
    Distribution,
    Trajectory,
)

# Audio features are optional (Phase 3)
try:
    from entrain.features.audio import AudioFeatureExtractor
    _has_audio = True
except ImportError:
    _has_audio = False

__all__ = [
    "TextFeatureExtractor",
    "TemporalFeatureExtractor",
    "PatternMatch",
    "TurnIntent",
    "QuestionType",
    "TimeSeries",
    "Distribution",
    "Trajectory",
]

if _has_audio:
    __all__.append("AudioFeatureExtractor")
