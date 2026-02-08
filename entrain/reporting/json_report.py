"""
JSON report generator for Entrain Framework assessments.

Serializes EntrainReport objects to structured JSON format for
programmatic consumption and archival.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from entrain.models import EntrainReport, DimensionReport, IndicatorResult


class JSONReportGenerator:
    """
    Generate JSON reports from Entrain assessments.

    Produces structured, machine-readable JSON with complete methodology
    metadata and citations.
    """

    def generate(self, report: EntrainReport, pretty: bool = True) -> str:
        """
        Generate JSON string from EntrainReport.

        Args:
            report: EntrainReport to serialize
            pretty: If True, format with indentation (default: True)

        Returns:
            JSON string
        """
        report_dict = self._report_to_dict(report)

        if pretty:
            return json.dumps(report_dict, indent=2, default=str)
        else:
            return json.dumps(report_dict, default=str)

    def save(self, report: EntrainReport, path: Path, pretty: bool = True) -> None:
        """
        Save EntrainReport to JSON file.

        Args:
            report: EntrainReport to save
            path: Output file path
            pretty: If True, format with indentation
        """
        json_str = self.generate(report, pretty=pretty)

        with open(path, "w", encoding="utf-8") as f:
            f.write(json_str)

    def _report_to_dict(self, report: EntrainReport) -> dict[str, Any]:
        """Convert EntrainReport to dictionary."""
        return {
            "entrain_version": report.version,
            "generated_at": report.generated_at.isoformat(),
            "input_summary": report.input_summary,
            "dimensions": {
                code: self._dimension_to_dict(dim_report)
                for code, dim_report in report.dimensions.items()
            },
            "cross_dimensional": report.cross_dimensional,
            "methodology": report.methodology
        }

    def _dimension_to_dict(self, dimension_report: DimensionReport) -> dict[str, Any]:
        """Convert DimensionReport to dictionary."""
        return {
            "dimension": dimension_report.dimension,
            "version": dimension_report.version,
            "indicators": {
                name: self._indicator_to_dict(indicator)
                for name, indicator in dimension_report.indicators.items()
            },
            "summary": dimension_report.summary,
            "methodology_notes": dimension_report.methodology_notes,
            "citations": dimension_report.citations
        }

    def _indicator_to_dict(self, indicator: IndicatorResult) -> dict[str, Any]:
        """Convert IndicatorResult to dictionary."""
        return {
            "name": indicator.name,
            "value": indicator.value,
            "baseline": indicator.baseline,
            "unit": indicator.unit,
            "confidence": indicator.confidence,
            "interpretation": indicator.interpretation
        }
