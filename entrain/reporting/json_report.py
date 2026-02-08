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

try:
    from entrain.analysis.cross_dimensional import CrossDimensionalReport
    CROSS_DIMENSIONAL_AVAILABLE = True
except ImportError:
    CROSS_DIMENSIONAL_AVAILABLE = False


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
        result = {
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

        # Add cross-dimensional analysis if available
        if CROSS_DIMENSIONAL_AVAILABLE and hasattr(report, 'cross_dimensional_analysis'):
            result["cross_dimensional_analysis"] = self._cross_dimensional_to_dict(
                report.cross_dimensional_analysis
            )

        return result

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

    def _cross_dimensional_to_dict(self, cross_dim_report: Any) -> dict[str, Any]:
        """Convert CrossDimensionalReport to dictionary."""
        result = {
            "risk_score": {
                "score": cross_dim_report.risk_score.score,
                "level": cross_dim_report.risk_score.level,
                "interpretation": cross_dim_report.risk_score.interpretation,
                "top_contributors": cross_dim_report.risk_score.top_contributors,
            },
            "patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "description": p.description,
                    "severity": p.severity,
                    "dimensions_involved": p.dimensions_involved,
                    "recommendation": p.recommendation,
                }
                for p in cross_dim_report.patterns
            ],
            "summary": cross_dim_report.summary,
        }

        # Add correlation matrix if available
        if cross_dim_report.correlation_matrix:
            corr_matrix = cross_dim_report.correlation_matrix
            result["correlation_matrix"] = {
                "dimensions": corr_matrix.dimensions,
                "correlations": {
                    f"{d1}-{d2}": corr
                    for (d1, d2), corr in corr_matrix.correlations.items()
                },
                "strong_correlations": [
                    {"dim1": d1, "dim2": d2, "correlation": corr}
                    for d1, d2, corr in corr_matrix.get_strong_correlations()
                ],
                "insufficient_data": corr_matrix.insufficient_data,
            }

        return result
