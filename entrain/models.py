"""
Core data models for the Entrain Framework.

This module defines the fundamental data structures used throughout the library
for representing conversations, measurements, and assessment results.

All models follow the specification in ARCHITECTURE.md Section 2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal


@dataclass
class AudioFeatures:
    """
    Acoustic features extracted from a voice interaction turn.

    Used for Prosodic Entrainment (PE) dimension analysis.
    Implementation deferred to Phase 3 (v2).
    """
    pitch_mean: float  # F0 mean in Hz
    pitch_std: float  # F0 standard deviation
    pitch_range: float  # F0 max - min
    intensity_mean: float  # Mean intensity in dB
    intensity_std: float
    speech_rate: float  # Syllables per second (estimated)
    pause_ratio: float  # Proportion of turn spent in silence
    spectral_features: dict = field(default_factory=dict)  # MFCCs, formants, etc.
    egemaps: dict | None = None  # Full eGeMAPS feature vector if openSMILE available


@dataclass
class InteractionEvent:
    """
    A single turn in a human-AI conversation.

    This is the fundamental unit of analysis. Every AI interaction — whether
    text or voice — is normalized to this model.

    Attributes:
        id: Unique identifier for this event
        conversation_id: ID of the parent conversation
        timestamp: When this turn occurred
        role: Who produced this turn ("user" or "assistant")
        text_content: The text content of the turn (required for text analysis)
        audio_path: Path to audio file if this is a voice interaction
        audio_features: Extracted acoustic features (populated after processing)
        metadata: Source-specific metadata (model name, temperature, etc.)
    """
    id: str
    conversation_id: str
    timestamp: datetime
    role: Literal["user", "assistant"]
    text_content: str | None
    audio_path: Path | None = None
    audio_features: AudioFeatures | None = None
    metadata: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        preview = (self.text_content[:50] + "...") if self.text_content and len(self.text_content) > 50 else self.text_content
        return f"InteractionEvent(id={self.id!r}, role={self.role!r}, text={preview!r})"


@dataclass
class Conversation:
    """
    A complete human-AI conversation.

    A conversation is a sequence of interaction events forming a dialogue.
    Conversations are the primary unit for most dimension analyzers.

    Attributes:
        id: Unique identifier for this conversation
        source: Platform source ("chatgpt", "claude", "characterai", etc.)
        events: List of interaction events in chronological order
        metadata: Export metadata, timestamps, model info
    """
    id: str
    source: str
    events: list[InteractionEvent]
    metadata: dict = field(default_factory=dict)

    @property
    def user_events(self) -> list[InteractionEvent]:
        """Return only user turns."""
        return [e for e in self.events if e.role == "user"]

    @property
    def assistant_events(self) -> list[InteractionEvent]:
        """Return only assistant turns."""
        return [e for e in self.events if e.role == "assistant"]

    @property
    def duration(self) -> float | None:
        """Return conversation duration in seconds, or None if no timestamps."""
        if len(self.events) < 2:
            return None
        return (self.events[-1].timestamp - self.events[0].timestamp).total_seconds()

    def __repr__(self) -> str:
        return f"Conversation(id={self.id!r}, source={self.source!r}, events={len(self.events)})"


@dataclass
class Corpus:
    """
    A collection of conversations for longitudinal or comparative analysis.

    Used for measuring trends over time and computing aggregate statistics
    across multiple conversations (e.g., for Dependency Formation analysis).

    Attributes:
        conversations: List of conversations in chronological order
        user_id: Anonymous identifier for the user (optional)
        date_range: Tuple of (earliest, latest) timestamps
    """
    conversations: list[Conversation]
    user_id: str | None = None
    date_range: tuple[datetime, datetime] | None = None

    def __post_init__(self):
        """Compute date range from conversations if not provided."""
        if self.date_range is None and self.conversations:
            all_timestamps = [
                event.timestamp
                for conv in self.conversations
                for event in conv.events
                if event.timestamp
            ]
            if all_timestamps:
                self.date_range = (min(all_timestamps), max(all_timestamps))

    def __repr__(self) -> str:
        return f"Corpus(conversations={len(self.conversations)}, user_id={self.user_id!r})"


@dataclass
class IndicatorResult:
    """
    A single measured indicator within a dimension.

    Indicators are specific, quantifiable metrics that operationalize
    a dimension (e.g., Action Endorsement Rate for SR dimension).

    Attributes:
        name: Indicator name (e.g., "action_endorsement_rate")
        value: Computed value for this indicator
        baseline: Human-human baseline if known (for comparison)
        unit: Unit of measurement (e.g., "proportion", "count per turn")
        confidence: 0-1 confidence in measurement (None if not computable)
        interpretation: Human-readable explanation of what this value means
    """
    name: str
    value: float
    baseline: float | None
    unit: str
    confidence: float | None = None
    interpretation: str = ""

    def __repr__(self) -> str:
        baseline_str = f", baseline={self.baseline}" if self.baseline is not None else ""
        return f"IndicatorResult({self.name}={self.value}{baseline_str})"


@dataclass
class DimensionReport:
    """
    Assessment results for a single Entrain Framework dimension.

    Each dimension analyzer produces one of these reports, containing
    all indicators computed for that dimension plus methodology notes.

    Attributes:
        dimension: Dimension code ("SR", "PE", "LC", "AE", "RCD", "DF")
        version: Framework version used for this assessment
        indicators: Dict mapping indicator names to results
        summary: Human-readable summary of findings
        methodology_notes: How this was computed (for reproducibility)
        citations: Papers grounding this measurement methodology
    """
    dimension: str
    version: str
    indicators: dict[str, IndicatorResult]
    summary: str
    methodology_notes: str
    citations: list[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"DimensionReport(dimension={self.dimension!r}, indicators={len(self.indicators)})"


@dataclass
class EntrainReport:
    """
    Complete Entrain Framework assessment.

    This is the top-level output structure containing assessment results
    for all applicable dimensions plus cross-dimensional observations.

    Attributes:
        version: Framework version
        generated_at: Timestamp when this report was generated
        input_summary: Statistics about the input corpus/conversation
        dimensions: Dict mapping dimension codes to their reports
        cross_dimensional: Observed cross-dimensional patterns
        methodology: Overall methodology description
    """
    version: str
    generated_at: datetime
    input_summary: dict
    dimensions: dict[str, DimensionReport]
    cross_dimensional: list[str] = field(default_factory=list)
    methodology: str = ""

    def __repr__(self) -> str:
        return f"EntrainReport(version={self.version!r}, dimensions={list(self.dimensions.keys())})"


# Version constant
ENTRAIN_VERSION = "0.1.1"
