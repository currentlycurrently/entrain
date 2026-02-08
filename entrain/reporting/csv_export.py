"""
CSV export for Entrain Framework time-series data.

Exports indicator trajectories and temporal features to CSV format
for external analysis (Excel, R, Python, etc.).
"""

import csv
from pathlib import Path
from typing import Any

from entrain.models import EntrainReport


class CSVExporter:
    """
    Export Entrain data to CSV format.

    Produces tabular data suitable for spreadsheet analysis and
    statistical software.
    """

    def export_indicators_summary(self, report: EntrainReport, path: Path) -> None:
        """
        Export all indicators to a single CSV file.

        Creates a wide-format CSV with one row per dimension,
        columns for each indicator.

        Args:
            report: EntrainReport to export
            path: Output CSV file path
        """
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                "dimension",
                "dimension_name",
                "indicator",
                "value",
                "baseline",
                "unit",
                "confidence",
                "interpretation"
            ])

            # Data rows
            for code, dimension_report in report.dimensions.items():
                dimension_name = self._get_dimension_name(code)

                for indicator_name, indicator in dimension_report.indicators.items():
                    writer.writerow([
                        code,
                        dimension_name,
                        indicator_name,
                        indicator.value,
                        indicator.baseline if indicator.baseline is not None else "",
                        indicator.unit,
                        indicator.confidence if indicator.confidence is not None else "",
                        indicator.interpretation
                    ])

    def export_dimension_details(
        self,
        dimension_code: str,
        indicators_data: dict[str, Any],
        path: Path
    ) -> None:
        """
        Export detailed time-series data for a single dimension.

        Use this to export trajectory data with timestamps.

        Args:
            dimension_code: Dimension code (e.g., "SR", "LC")
            indicators_data: Dict with indicator names and their time-series data
            path: Output CSV file path

        Example:
            >>> indicators_data = {
            ...     "vocabulary_overlap": {
            ...         "timestamps": [datetime(...), ...],
            ...         "values": [0.3, 0.35, 0.4, ...],
            ...     }
            ... }
        """
        # Determine max length
        max_length = 0
        for data in indicators_data.values():
            if "values" in data:
                max_length = max(max_length, len(data["values"]))

        if max_length == 0:
            # No time-series data to export
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Build header
            header = ["index"]

            for indicator_name in indicators_data.keys():
                if "timestamps" in indicators_data[indicator_name]:
                    header.append(f"{indicator_name}_timestamp")
                header.append(f"{indicator_name}_value")

            writer.writerow(header)

            # Write data rows
            for i in range(max_length):
                row = [i]

                for indicator_name, data in indicators_data.items():
                    timestamps = data.get("timestamps", [])
                    values = data.get("values", [])

                    if timestamps and i < len(timestamps):
                        row.append(timestamps[i].isoformat())

                    if values and i < len(values):
                        row.append(values[i])
                    else:
                        row.append("")

                writer.writerow(row)

    def _get_dimension_name(self, code: str) -> str:
        """Get full dimension name from code."""
        names = {
            "SR": "Sycophantic Reinforcement",
            "PE": "Prosodic Entrainment",
            "LC": "Linguistic Convergence",
            "AE": "Autonomy Erosion",
            "RCD": "Reality Coherence Disruption",
            "DF": "Dependency Formation"
        }
        return names.get(code, code)
