"""
Temporal feature extraction for longitudinal analysis.

Provides utilities for analyzing time-series patterns across conversations
in a corpus. Used primarily for Dependency Formation (DF) dimension.

See ARCHITECTURE.md Section 6.3 for specification.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from entrain.models import Corpus, Conversation


@dataclass
class TimeSeries:
    """Time series data with timestamps and values."""
    timestamps: list[datetime]
    values: list[float]
    unit: str

    def __len__(self) -> int:
        return len(self.timestamps)


@dataclass
class Distribution:
    """Distribution of values."""
    bins: list[str]  # Bin labels
    counts: list[int]  # Count per bin
    proportions: list[float]  # Proportion per bin


@dataclass
class Trajectory:
    """Trajectory of an indicator over time with trend analysis."""
    timestamps: list[datetime]
    values: list[float]
    trend: Literal["increasing", "decreasing", "stable", "insufficient_data"]
    slope: float | None  # Linear regression slope if computable


class TemporalFeatureExtractor:
    """
    Extract time-series features from a corpus.

    Analyzes patterns in interaction frequency, session duration,
    time-of-day distribution, and indicator trajectories over time.
    """

    def interaction_frequency(
        self, corpus: Corpus, window: str = "week"
    ) -> TimeSeries:
        """
        Calculate interaction frequency over time.

        Args:
            corpus: Input corpus
            window: Time window for aggregation ("day", "week", "month")

        Returns:
            TimeSeries of interaction counts per window
        """
        if not corpus.conversations:
            return TimeSeries(timestamps=[], values=[], unit=f"conversations per {window}")

        # Get all conversation start times
        conv_times = [
            conv.events[0].timestamp
            for conv in corpus.conversations
            if conv.events
        ]

        if not conv_times:
            return TimeSeries(timestamps=[], values=[], unit=f"conversations per {window}")

        conv_times.sort()

        # Determine window size
        if window == "day":
            delta = timedelta(days=1)
        elif window == "week":
            delta = timedelta(weeks=1)
        elif window == "month":
            delta = timedelta(days=30)
        else:
            raise ValueError(f"Unknown window: {window}")

        # Bin conversations into windows
        start_time = conv_times[0]
        end_time = conv_times[-1]

        timestamps = []
        values = []

        current = start_time
        while current <= end_time:
            # Count conversations in this window
            window_end = current + delta
            count = sum(1 for t in conv_times if current <= t < window_end)

            timestamps.append(current)
            values.append(float(count))

            current = window_end

        return TimeSeries(
            timestamps=timestamps,
            values=values,
            unit=f"conversations per {window}"
        )

    def session_duration_trend(self, corpus: Corpus) -> TimeSeries:
        """
        Calculate session duration trend over time.

        Args:
            corpus: Input corpus

        Returns:
            TimeSeries of conversation durations (in minutes)
        """
        timestamps = []
        durations = []

        for conv in corpus.conversations:
            if not conv.events or len(conv.events) < 2:
                continue

            start_time = conv.events[0].timestamp
            duration = conv.duration

            if duration is not None:
                timestamps.append(start_time)
                durations.append(duration / 60.0)  # Convert to minutes

        return TimeSeries(
            timestamps=timestamps,
            values=durations,
            unit="minutes"
        )

    def time_of_day_distribution(self, corpus: Corpus) -> Distribution:
        """
        Calculate distribution of interaction times across day.

        Bins interactions into time-of-day categories:
        - Night: 00:00-06:00
        - Morning: 06:00-12:00
        - Afternoon: 12:00-18:00
        - Evening: 18:00-24:00

        Args:
            corpus: Input corpus

        Returns:
            Distribution of interactions by time of day
        """
        bins = ["Night (00-06)", "Morning (06-12)", "Afternoon (12-18)", "Evening (18-24)"]
        counts = [0, 0, 0, 0]

        for conv in corpus.conversations:
            for event in conv.events:
                if event.role != "user":  # Only count user interactions
                    continue

                hour = event.timestamp.hour

                if 0 <= hour < 6:
                    counts[0] += 1
                elif 6 <= hour < 12:
                    counts[1] += 1
                elif 12 <= hour < 18:
                    counts[2] += 1
                else:
                    counts[3] += 1

        total = sum(counts)
        proportions = [c / total if total > 0 else 0.0 for c in counts]

        return Distribution(
            bins=bins,
            counts=counts,
            proportions=proportions
        )

    def indicator_trajectory(
        self, values: list[float], timestamps: list[datetime]
    ) -> Trajectory:
        """
        Analyze trajectory of an indicator over time.

        Computes trend direction and slope using simple linear regression.

        Args:
            values: Indicator values
            timestamps: Corresponding timestamps

        Returns:
            Trajectory with trend analysis
        """
        if len(values) < 3:
            return Trajectory(
                timestamps=timestamps,
                values=values,
                trend="insufficient_data",
                slope=None
            )

        # Simple linear regression to determine trend
        n = len(values)
        x = list(range(n))  # Time indices
        y = values

        # Calculate means
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        # Calculate slope
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0.0
        else:
            slope = numerator / denominator

        # Determine trend
        # Use slope magnitude relative to mean to determine significance
        if y_mean == 0:
            threshold = 0.01
        else:
            threshold = abs(y_mean) * 0.1  # 10% of mean

        if abs(slope) < threshold:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        return Trajectory(
            timestamps=timestamps,
            values=values,
            trend=trend,
            slope=slope
        )

    def emotional_vs_functional_trajectory(self, corpus: Corpus) -> Trajectory:
        """
        Track emotional vs functional content ratio over time.

        Requires TextFeatureExtractor to be run on conversations first.

        Args:
            corpus: Input corpus

        Returns:
            Trajectory of emotional content ratios
        """
        from entrain.features.text import TextFeatureExtractor

        extractor = TextFeatureExtractor()

        timestamps = []
        ratios = []

        for conv in corpus.conversations:
            if not conv.events:
                continue

            # Get first user event timestamp as conversation time
            user_events = [e for e in conv.events if e.role == "user"]
            if not user_events:
                continue

            start_time = user_events[0].timestamp

            # Calculate emotional ratio for this conversation
            emotional_counts = []
            for event in user_events:
                if event.text_content:
                    ratio = extractor.extract_emotional_content_ratio(event.text_content)
                    emotional_counts.append(ratio)

            if emotional_counts:
                avg_ratio = sum(emotional_counts) / len(emotional_counts)
                timestamps.append(start_time)
                ratios.append(avg_ratio)

        return self.indicator_trajectory(ratios, timestamps)
