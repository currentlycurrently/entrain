"""
Markdown report generator for Entrain Framework assessments.

Produces human-readable markdown reports suitable for documentation,
sharing, and archival.
"""

from datetime import datetime
from pathlib import Path

from entrain.models import EntrainReport, DimensionReport, IndicatorResult

try:
    from entrain.analysis.cross_dimensional import CrossDimensionalReport
    CROSS_DIMENSIONAL_AVAILABLE = True
except ImportError:
    CROSS_DIMENSIONAL_AVAILABLE = False


class MarkdownReportGenerator:
    """
    Generate markdown reports from Entrain assessments.

    Produces structured, human-readable markdown with clear sections,
    tables, and methodology notes.
    """

    def generate(self, report: EntrainReport) -> str:
        """
        Generate markdown string from EntrainReport.

        Args:
            report: EntrainReport to format

        Returns:
            Markdown string
        """
        sections = []

        # Header
        sections.append(self._generate_header(report))

        # Input summary
        sections.append(self._generate_input_summary(report))

        # Dimension reports
        for code in sorted(report.dimensions.keys()):
            dimension_report = report.dimensions[code]
            sections.append(self._generate_dimension_section(dimension_report))

        # Cross-dimensional analysis (if available)
        if CROSS_DIMENSIONAL_AVAILABLE and hasattr(report, 'cross_dimensional_analysis'):
            sections.append(self._generate_cross_dimensional_analysis(report.cross_dimensional_analysis))

        # Cross-dimensional observations
        if report.cross_dimensional:
            sections.append(self._generate_cross_dimensional(report))

        # Methodology
        sections.append(self._generate_methodology(report))

        return "\n\n".join(sections)

    def save(self, report: EntrainReport, path: Path) -> None:
        """
        Save EntrainReport to markdown file.

        Args:
            report: EntrainReport to save
            path: Output file path
        """
        markdown = self.generate(report)

        with open(path, "w", encoding="utf-8") as f:
            f.write(markdown)

    def _generate_header(self, report: EntrainReport) -> str:
        """Generate report header."""
        return f"""# Entrain Framework Assessment Report

**Version:** {report.version}
**Generated:** {report.generated_at.strftime("%Y-%m-%d %H:%M:%S")}

---"""

    def _generate_input_summary(self, report: EntrainReport) -> str:
        """Generate input summary section."""
        summary = report.input_summary

        lines = ["## Input Summary", ""]

        for key, value in summary.items():
            lines.append(f"- **{key}**: {value}")

        return "\n".join(lines)

    def _generate_dimension_section(self, dimension_report: DimensionReport) -> str:
        """Generate section for a single dimension."""
        lines = [
            f"## {dimension_report.dimension}: {self._get_dimension_name(dimension_report.dimension)}",
            "",
            f"**Summary:** {dimension_report.summary}",
            ""
        ]

        # Indicators table
        lines.append("### Indicators")
        lines.append("")
        lines.append("| Indicator | Value | Baseline | Unit | Confidence | Interpretation |")
        lines.append("|-----------|-------|----------|------|------------|----------------|")

        for name, indicator in dimension_report.indicators.items():
            baseline_str = f"{indicator.baseline:.3f}" if indicator.baseline is not None else "N/A"
            confidence_str = f"{indicator.confidence:.0%}" if indicator.confidence is not None else "N/A"
            value_str = f"{indicator.value:.3f}"

            # Truncate interpretation if too long
            interp = indicator.interpretation
            if len(interp) > 60:
                interp = interp[:57] + "..."

            lines.append(
                f"| {name} | {value_str} | {baseline_str} | {indicator.unit} | "
                f"{confidence_str} | {interp} |"
            )

        lines.append("")

        # Methodology notes
        lines.append("### Methodology")
        lines.append("")
        lines.append(dimension_report.methodology_notes)
        lines.append("")

        # Citations
        if dimension_report.citations:
            lines.append("### References")
            lines.append("")
            for citation in dimension_report.citations:
                lines.append(f"- {citation}")

        return "\n".join(lines)

    def _generate_cross_dimensional_analysis(self, cross_dim_report) -> str:
        """Generate cross-dimensional analysis section."""
        lines = ["## Cross-Dimensional Analysis", ""]

        # Risk Score
        lines.append("### Overall Risk Assessment")
        lines.append("")
        risk_icon = {
            "LOW": "🟢",
            "MODERATE": "🟡",
            "HIGH": "🟠",
            "SEVERE": "🔴"
        }
        icon = risk_icon.get(cross_dim_report.risk_score.level, "⚪")
        lines.append(f"**Risk Level:** {icon} **{cross_dim_report.risk_score.level}** ({cross_dim_report.risk_score.score:.0%})")
        lines.append("")
        lines.append(cross_dim_report.risk_score.interpretation)
        lines.append("")

        if cross_dim_report.risk_score.top_contributors:
            lines.append("**Primary Concerns:**")
            for dim in cross_dim_report.risk_score.top_contributors:
                dim_name = self._get_dimension_name(dim)
                lines.append(f"- {dim} ({dim_name})")
            lines.append("")

        # Patterns
        if cross_dim_report.patterns:
            lines.append("### Detected Patterns")
            lines.append("")

            for pattern in cross_dim_report.patterns:
                severity_icon = risk_icon.get(pattern.severity, "⚪")
                lines.append(f"#### {severity_icon} {pattern.pattern_id.replace('_', ' ').title()}")
                lines.append("")
                lines.append(f"**Severity:** {pattern.severity}")
                lines.append("")
                lines.append(f"**Description:** {pattern.description}")
                lines.append("")
                lines.append(f"**Dimensions Involved:** {', '.join(pattern.dimensions_involved)}")
                lines.append("")
                lines.append(f"**Recommendation:** {pattern.recommendation}")
                lines.append("")

        # Correlation Matrix (if available)
        if cross_dim_report.correlation_matrix and not cross_dim_report.correlation_matrix.insufficient_data:
            lines.append("### Correlation Matrix")
            lines.append("")

            strong_corrs = cross_dim_report.correlation_matrix.get_strong_correlations()

            if strong_corrs:
                lines.append("**Strong Correlations** (|r| > 0.7):")
                lines.append("")
                lines.append("| Dimension 1 | Dimension 2 | Correlation |")
                lines.append("|-------------|-------------|-------------|")

                for dim1, dim2, corr in strong_corrs:
                    corr_str = f"{corr:+.3f}"
                    lines.append(f"| {dim1} | {dim2} | {corr_str} |")

                lines.append("")
            else:
                lines.append("*No strong correlations detected (all |r| < 0.7)*")
                lines.append("")

        # Summary
        lines.append("### Summary")
        lines.append("")
        lines.append(cross_dim_report.summary)
        lines.append("")

        return "\n".join(lines)

    def _generate_cross_dimensional(self, report: EntrainReport) -> str:
        """Generate cross-dimensional observations section."""
        lines = ["## Cross-Dimensional Observations", ""]

        for observation in report.cross_dimensional:
            lines.append(f"- {observation}")

        return "\n".join(lines)

    def _generate_methodology(self, report: EntrainReport) -> str:
        """Generate methodology section."""
        return f"""## Overall Methodology

{report.methodology}

---

*Report generated by Entrain Reference Library v{report.version}*
*Framework: [entrain.institute](https://entrain.institute)*"""

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
