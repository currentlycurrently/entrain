"""
Example: Cross-Dimensional Analysis

This example demonstrates how to use the cross-dimensional analysis module
to compute correlations, detect patterns, and assess overall risk across
multiple Entrain Framework dimensions.
"""

from datetime import datetime
from entrain.models import (
    DimensionReport,
    IndicatorResult,
    EntrainReport,
)
from entrain.analysis import CrossDimensionalAnalyzer


def create_sample_report(sr_score: float, ae_score: float, rcd_score: float) -> EntrainReport:
    """Create a sample EntrainReport with specified dimension scores."""

    dimension_reports = {
        "SR": DimensionReport(
            dimension="SR",
            version="0.2.1",
            indicators={
                "action_endorsement_rate": IndicatorResult(
                    name="Action Endorsement Rate",
                    value=sr_score,
                    baseline=0.42,
                    unit="%",
                    confidence=0.85,
                    interpretation=f"{'High' if sr_score > 0.6 else 'Moderate'} sycophantic reinforcement detected",
                ),
            },
            summary=f"{'HIGH' if sr_score > 0.6 else 'MODERATE'} - Sycophantic reinforcement detected",
            methodology_notes="Pattern-based detection of affirmation language",
            citations=["Cheng et al. (2025)"],
        ),
        "AE": DimensionReport(
            dimension="AE",
            version="0.2.1",
            indicators={
                "decision_delegation_ratio": IndicatorResult(
                    name="Decision Delegation Ratio",
                    value=ae_score,
                    baseline=0.30,
                    unit="%",
                    confidence=0.80,
                    interpretation=f"{'High' if ae_score > 0.6 else 'Moderate'} autonomy erosion",
                ),
            },
            summary=f"{'HIGH' if ae_score > 0.6 else 'MODERATE'} - Autonomy erosion detected",
            methodology_notes="Classification of decision-making patterns",
            citations=["Cheng et al. (2025)"],
        ),
        "RCD": DimensionReport(
            dimension="RCD",
            version="0.2.1",
            indicators={
                "attribution_language_freq": IndicatorResult(
                    name="Attribution Language Frequency",
                    value=rcd_score,
                    baseline=0.15,
                    unit="%",
                    confidence=0.75,
                    interpretation=f"{'High' if rcd_score > 0.6 else 'Moderate'} reality coherence disruption",
                ),
            },
            summary=f"{'HIGH' if rcd_score > 0.6 else 'MODERATE'} - Reality coherence disruption",
            methodology_notes="Detection of anthropomorphizing language",
            citations=["Lipińska & Krzanowski (2025)"],
        ),
        "LC": DimensionReport(
            dimension="LC",
            version="0.2.1",
            indicators={
                "vocabulary_overlap": IndicatorResult(
                    name="Vocabulary Overlap",
                    value=0.50,
                    baseline=0.30,
                    unit="%",
                    confidence=0.90,
                    interpretation="Moderate linguistic convergence",
                ),
            },
            summary="MODERATE - Linguistic convergence detected",
            methodology_notes="Jaccard similarity of vocabulary",
            citations=["Pickering & Garrod (2004)"],
        ),
        "DF": DimensionReport(
            dimension="DF",
            version="0.2.1",
            indicators={
                "interaction_frequency": IndicatorResult(
                    name="Interaction Frequency",
                    value=0.55,
                    baseline=0.40,
                    unit="sessions/week",
                    confidence=0.85,
                    interpretation="Moderate dependency formation",
                ),
            },
            summary="MODERATE - Dependency formation detected",
            methodology_notes="Time-series analysis of interaction patterns",
            citations=["Kirk et al. (2025)"],
        ),
        "PE": DimensionReport(
            dimension="PE",
            version="0.2.1",
            indicators={
                "pitch_convergence": IndicatorResult(
                    name="Pitch Convergence",
                    value=0.45,
                    baseline=0.50,
                    unit="%",
                    confidence=0.70,
                    interpretation="Minimal prosodic entrainment",
                ),
            },
            summary="LOW - Minimal prosodic entrainment",
            methodology_notes="F0 similarity analysis",
            citations=["Pickering & Garrod (2004)"],
        ),
    }

    return EntrainReport(
        version="0.2.1",
        generated_at=datetime.now(),
        input_summary={
            "conversations": 1,
            "total_turns": 42,
            "user_turns": 21,
            "assistant_turns": 21,
        },
        dimensions=dimension_reports,
        cross_dimensional=[],
        methodology="Comprehensive analysis across all six dimensions",
    )


def example_single_conversation_analysis():
    """Example 1: Analyze a single conversation for cross-dimensional patterns."""

    print("=" * 70)
    print("Example 1: Single Conversation Cross-Dimensional Analysis")
    print("=" * 70)
    print()

    # Create analyzer
    analyzer = CrossDimensionalAnalyzer()

    # Create a sample report with high SR and high AE
    report = create_sample_report(sr_score=0.75, ae_score=0.78, rcd_score=0.45)

    # Perform cross-dimensional analysis
    cross_dim_report = analyzer.analyze(report)

    # Display results
    print(f"Overall Risk: {cross_dim_report.risk_score.level} ({cross_dim_report.risk_score.score:.0%})")
    print()
    print("Interpretation:")
    print(f"  {cross_dim_report.risk_score.interpretation}")
    print()

    if cross_dim_report.patterns:
        print(f"Detected Patterns ({len(cross_dim_report.patterns)}):")
        for pattern in cross_dim_report.patterns:
            print(f"  - [{pattern.severity}] {pattern.pattern_id}")
            print(f"    {pattern.description}")
            print(f"    Recommendation: {pattern.recommendation}")
            print()

    print(f"Summary: {cross_dim_report.summary}")
    print()


def example_corpus_analysis():
    """Example 2: Analyze multiple conversations to compute correlations."""

    print("=" * 70)
    print("Example 2: Corpus Analysis with Correlation Matrix")
    print("=" * 70)
    print()

    # Create analyzer
    analyzer = CrossDimensionalAnalyzer()

    # Simulate 5 conversations with varying scores
    reports = [
        create_sample_report(sr_score=0.70, ae_score=0.75, rcd_score=0.45),
        create_sample_report(sr_score=0.60, ae_score=0.65, rcd_score=0.35),
        create_sample_report(sr_score=0.80, ae_score=0.85, rcd_score=0.50),
        create_sample_report(sr_score=0.50, ae_score=0.55, rcd_score=0.30),
        create_sample_report(sr_score=0.65, ae_score=0.70, rcd_score=0.40),
    ]

    # Perform corpus analysis
    cross_dim_report = analyzer.analyze_corpus(reports)

    # Display results
    print(f"Overall Risk (Average): {cross_dim_report.risk_score.level} ({cross_dim_report.risk_score.score:.0%})")
    print()

    # Show correlation matrix
    if cross_dim_report.correlation_matrix:
        print("Correlation Matrix:")
        strong_corrs = cross_dim_report.correlation_matrix.get_strong_correlations()

        if strong_corrs:
            print("  Strong correlations (|r| > 0.7):")
            for dim1, dim2, corr in strong_corrs:
                print(f"    {dim1} ↔ {dim2}: {corr:+.3f}")
        else:
            print("  No strong correlations detected")

        print()

    print(f"Summary: {cross_dim_report.summary}")
    print()


def example_custom_weights():
    """Example 3: Custom risk scoring with dimension weights."""

    print("=" * 70)
    print("Example 3: Custom Risk Scoring with Dimension Weights")
    print("=" * 70)
    print()

    # Create analyzer
    analyzer = CrossDimensionalAnalyzer()

    # Create a sample report
    report = create_sample_report(sr_score=0.60, ae_score=0.80, rcd_score=0.50)

    # Extract dimension scores
    dimension_scores = {}
    for dim_code, dim_report in report.dimensions.items():
        indicator_values = [ind.value for ind in dim_report.indicators.values()]
        if indicator_values:
            dimension_scores[dim_code] = sum(indicator_values) / len(indicator_values)

    # Default weights
    risk_score_default = analyzer.compute_risk_score(dimension_scores)

    # Custom weights (emphasize autonomy erosion and reality coherence)
    custom_weights = {
        "SR": 1.0,
        "LC": 0.8,
        "AE": 2.0,  # Double weight for autonomy erosion
        "RCD": 1.8,  # High weight for reality coherence disruption
        "DF": 1.2,
        "PE": 0.6,
    }
    risk_score_custom = analyzer.compute_risk_score(dimension_scores, weights=custom_weights)

    # Display comparison
    print("Default Weighting:")
    print(f"  Risk: {risk_score_default.level} ({risk_score_default.score:.0%})")
    print(f"  Top Contributors: {', '.join(risk_score_default.top_contributors)}")
    print()

    print("Custom Weighting (AE and RCD emphasized):")
    print(f"  Risk: {risk_score_custom.level} ({risk_score_custom.score:.0%})")
    print(f"  Top Contributors: {', '.join(risk_score_custom.top_contributors)}")
    print()


def example_with_reporting():
    """Example 4: Generate reports with cross-dimensional analysis."""

    print("=" * 70)
    print("Example 4: Integration with Reporting Modules")
    print("=" * 70)
    print()

    from entrain.reporting import MarkdownReportGenerator

    # Create analyzer
    analyzer = CrossDimensionalAnalyzer()

    # Create a sample report
    report = create_sample_report(sr_score=0.75, ae_score=0.78, rcd_score=0.65)

    # Perform cross-dimensional analysis
    cross_dim_report = analyzer.analyze(report)

    # Attach to main report (for demonstration)
    report.cross_dimensional_analysis = cross_dim_report

    # Generate markdown report
    md_generator = MarkdownReportGenerator()
    markdown = md_generator.generate(report)

    # Show a snippet (first 1000 characters)
    print("Generated Markdown Report (excerpt):")
    print("-" * 70)
    print(markdown[:1000])
    print("...")
    print("-" * 70)
    print()
    print("Full report would include all dimensions plus cross-dimensional analysis section.")
    print()


if __name__ == "__main__":
    example_single_conversation_analysis()
    example_corpus_analysis()
    example_custom_weights()
    example_with_reporting()

    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
