"""
Comprehensive tests for cross-dimensional analysis.

This module tests the CrossDimensionalAnalyzer which computes:
- Correlation matrices between dimensions
- Overall risk scoring
- Pattern detection across dimensions
"""

import pytest
from datetime import datetime
from entrain.models import (
    DimensionReport,
    IndicatorResult,
    EntrainReport,
)
from entrain.analysis.cross_dimensional import (
    CrossDimensionalAnalyzer,
    CorrelationMatrix,
    RiskScore,
    Pattern,
    CrossDimensionalReport,
)


class TestCorrelationMatrix:
    """Test correlation matrix computation."""

    def test_correlation_matrix_creation(self):
        """Test creating a correlation matrix from dimension scores."""
        analyzer = CrossDimensionalAnalyzer()

        # Create sample dimension scores
        dimension_scores = {
            "SR": 0.65,  # High sycophantic reinforcement
            "LC": 0.58,  # Moderate linguistic convergence
            "AE": 0.72,  # High autonomy erosion
            "RCD": 0.45,  # Moderate reality coherence disruption
            "DF": 0.55,  # Moderate dependency formation
            "PE": 0.50,  # Moderate prosodic entrainment
        }

        correlation_matrix = analyzer.compute_correlation_matrix([dimension_scores])

        assert isinstance(correlation_matrix, CorrelationMatrix)
        assert correlation_matrix.dimensions == ["SR", "LC", "AE", "RCD", "DF", "PE"]

    def test_correlation_matrix_with_multiple_samples(self):
        """Test correlation computation with multiple conversation samples."""
        analyzer = CrossDimensionalAnalyzer()

        # Create multiple samples (simulating corpus analysis)
        samples = [
            {"SR": 0.65, "LC": 0.58, "AE": 0.72, "RCD": 0.45, "DF": 0.55, "PE": 0.50},
            {"SR": 0.45, "LC": 0.42, "AE": 0.50, "RCD": 0.35, "DF": 0.40, "PE": 0.38},
            {"SR": 0.70, "LC": 0.65, "AE": 0.75, "RCD": 0.50, "DF": 0.60, "PE": 0.55},
            {"SR": 0.55, "LC": 0.50, "AE": 0.60, "RCD": 0.40, "DF": 0.48, "PE": 0.45},
        ]

        correlation_matrix = analyzer.compute_correlation_matrix(samples)

        # Check that we have correlations for all pairs
        assert len(correlation_matrix.correlations) > 0

        # SR and AE should have positive correlation (both high together)
        sr_ae_corr = correlation_matrix.get_correlation("SR", "AE")
        assert sr_ae_corr is not None
        assert -1.0 <= sr_ae_corr <= 1.0

    def test_correlation_matrix_symmetry(self):
        """Test that correlation matrix is symmetric."""
        analyzer = CrossDimensionalAnalyzer()

        samples = [
            {"SR": 0.65, "LC": 0.58, "AE": 0.72, "RCD": 0.45, "DF": 0.55, "PE": 0.50},
            {"SR": 0.45, "LC": 0.42, "AE": 0.50, "RCD": 0.35, "DF": 0.40, "PE": 0.38},
            {"SR": 0.70, "LC": 0.65, "AE": 0.75, "RCD": 0.50, "DF": 0.60, "PE": 0.55},
        ]

        correlation_matrix = analyzer.compute_correlation_matrix(samples)

        # Check symmetry: corr(A, B) == corr(B, A)
        sr_ae = correlation_matrix.get_correlation("SR", "AE")
        ae_sr = correlation_matrix.get_correlation("AE", "SR")

        assert sr_ae == ae_sr

    def test_correlation_matrix_diagonal_is_one(self):
        """Test that diagonal correlations (self-correlation) are 1.0."""
        analyzer = CrossDimensionalAnalyzer()

        samples = [
            {"SR": 0.65, "LC": 0.58, "AE": 0.72, "RCD": 0.45, "DF": 0.55, "PE": 0.50},
            {"SR": 0.45, "LC": 0.42, "AE": 0.50, "RCD": 0.35, "DF": 0.40, "PE": 0.38},
        ]

        correlation_matrix = analyzer.compute_correlation_matrix(samples)

        # Self-correlation should be 1.0
        for dim in ["SR", "LC", "AE", "RCD", "DF", "PE"]:
            self_corr = correlation_matrix.get_correlation(dim, dim)
            assert self_corr == pytest.approx(1.0, abs=0.01)

    def test_correlation_matrix_insufficient_data(self):
        """Test correlation matrix with insufficient data (single sample)."""
        analyzer = CrossDimensionalAnalyzer()

        # Only one sample - cannot compute correlations
        samples = [
            {"SR": 0.65, "LC": 0.58, "AE": 0.72, "RCD": 0.45, "DF": 0.55, "PE": 0.50},
        ]

        correlation_matrix = analyzer.compute_correlation_matrix(samples)

        # Should return matrix with NaN or None for correlations
        assert correlation_matrix.insufficient_data is True

    def test_get_strong_correlations(self):
        """Test identifying strong correlations (|r| > threshold)."""
        analyzer = CrossDimensionalAnalyzer()

        # Create samples with strong SR-AE correlation
        samples = [
            {"SR": 0.70, "LC": 0.40, "AE": 0.75, "RCD": 0.30, "DF": 0.45, "PE": 0.35},
            {"SR": 0.60, "LC": 0.45, "AE": 0.65, "RCD": 0.35, "DF": 0.40, "PE": 0.40},
            {"SR": 0.80, "LC": 0.35, "AE": 0.85, "RCD": 0.25, "DF": 0.50, "PE": 0.30},
            {"SR": 0.50, "LC": 0.50, "AE": 0.55, "RCD": 0.40, "DF": 0.35, "PE": 0.45},
            {"SR": 0.65, "LC": 0.42, "AE": 0.70, "RCD": 0.32, "DF": 0.42, "PE": 0.38},
        ]

        correlation_matrix = analyzer.compute_correlation_matrix(samples)

        # Get strong correlations (threshold = 0.7)
        strong_correlations = correlation_matrix.get_strong_correlations(threshold=0.7)

        assert isinstance(strong_correlations, list)


class TestRiskScoring:
    """Test overall risk scoring system."""

    def test_risk_score_low(self):
        """Test risk scoring with low dimension scores."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.25,
            "LC": 0.20,
            "AE": 0.18,
            "RCD": 0.15,
            "DF": 0.22,
            "PE": 0.19,
        }

        risk_score = analyzer.compute_risk_score(dimension_scores)

        assert isinstance(risk_score, RiskScore)
        assert risk_score.level in ["LOW", "MODERATE", "HIGH", "SEVERE"]
        assert risk_score.level == "LOW"
        assert 0.0 <= risk_score.score <= 1.0

    def test_risk_score_moderate(self):
        """Test risk scoring with moderate dimension scores."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.55,
            "LC": 0.48,
            "AE": 0.52,
            "RCD": 0.45,
            "DF": 0.50,
            "PE": 0.47,
        }

        risk_score = analyzer.compute_risk_score(dimension_scores)

        assert risk_score.level == "MODERATE"
        assert 0.4 <= risk_score.score <= 0.7

    def test_risk_score_high(self):
        """Test risk scoring with high dimension scores."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.75,
            "LC": 0.68,
            "AE": 0.72,
            "RCD": 0.65,
            "DF": 0.70,
            "PE": 0.67,
        }

        risk_score = analyzer.compute_risk_score(dimension_scores)

        assert risk_score.level in ["HIGH", "SEVERE"]

    def test_risk_score_severe(self):
        """Test risk scoring with severe dimension scores."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.92,
            "LC": 0.88,
            "AE": 0.90,
            "RCD": 0.85,
            "DF": 0.87,
            "PE": 0.84,
        }

        risk_score = analyzer.compute_risk_score(dimension_scores)

        assert risk_score.level == "SEVERE"
        assert risk_score.score >= 0.8

    def test_risk_score_with_weights(self):
        """Test that risk scoring can use custom dimension weights."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.60,
            "LC": 0.40,
            "AE": 0.80,  # High autonomy erosion - should be weighted heavily
            "RCD": 0.50,
            "DF": 0.55,
            "PE": 0.45,
        }

        # Custom weights (AE and RCD weighted more heavily)
        weights = {
            "SR": 1.0,
            "LC": 0.8,
            "AE": 1.5,  # Higher weight for autonomy erosion
            "RCD": 1.3,
            "DF": 1.2,
            "PE": 0.9,
        }

        risk_score_weighted = analyzer.compute_risk_score(dimension_scores, weights=weights)
        risk_score_unweighted = analyzer.compute_risk_score(dimension_scores)

        # Weighted score should be higher due to high AE
        assert risk_score_weighted.score >= risk_score_unweighted.score

    def test_risk_score_interpretation(self):
        """Test that risk scores include interpretations."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.75,
            "LC": 0.68,
            "AE": 0.72,
            "RCD": 0.65,
            "DF": 0.70,
            "PE": 0.67,
        }

        risk_score = analyzer.compute_risk_score(dimension_scores)

        assert hasattr(risk_score, "interpretation")
        assert isinstance(risk_score.interpretation, str)
        assert len(risk_score.interpretation) > 0

    def test_risk_score_contributing_dimensions(self):
        """Test that risk score identifies top contributing dimensions."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.85,  # Very high
            "LC": 0.40,  # Low
            "AE": 0.80,  # High
            "RCD": 0.35,  # Low
            "DF": 0.45,  # Moderate
            "PE": 0.38,  # Low
        }

        risk_score = analyzer.compute_risk_score(dimension_scores)

        # Should identify SR and AE as top contributors
        assert hasattr(risk_score, "top_contributors")
        assert isinstance(risk_score.top_contributors, list)
        assert "SR" in risk_score.top_contributors
        assert "AE" in risk_score.top_contributors


class TestPatternDetection:
    """Test cross-dimensional pattern detection."""

    def test_detect_high_sr_high_ae_pattern(self):
        """Test detection of High SR + High AE pattern (concerning)."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.75,  # High sycophantic reinforcement
            "LC": 0.45,
            "AE": 0.78,  # High autonomy erosion
            "RCD": 0.40,
            "DF": 0.50,
            "PE": 0.42,
        }

        patterns = analyzer.detect_patterns(dimension_scores)

        assert isinstance(patterns, list)
        assert len(patterns) > 0

        # Should detect the SR+AE pattern
        pattern_ids = [p.pattern_id for p in patterns]
        assert "high_sr_high_ae" in pattern_ids

    def test_detect_reality_coherence_pattern(self):
        """Test detection of reality coherence disruption patterns."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.50,
            "LC": 0.48,
            "AE": 0.45,
            "RCD": 0.82,  # Very high reality coherence disruption
            "DF": 0.70,  # High dependency formation
            "PE": 0.55,
        }

        patterns = analyzer.detect_patterns(dimension_scores)

        # Should detect RCD+DF pattern
        pattern_ids = [p.pattern_id for p in patterns]
        assert any("rcd" in pid.lower() for pid in pattern_ids)

    def test_detect_linguistic_convergence_pattern(self):
        """Test detection of linguistic convergence patterns."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.45,
            "LC": 0.85,  # Very high linguistic convergence
            "AE": 0.50,
            "RCD": 0.48,
            "DF": 0.52,
            "PE": 0.80,  # High prosodic entrainment
        }

        patterns = analyzer.detect_patterns(dimension_scores)

        # Should detect LC+PE convergence pattern
        pattern_ids = [p.pattern_id for p in patterns]
        assert any("convergence" in pid.lower() or ("lc" in pid.lower() and "pe" in pid.lower()) for pid in pattern_ids)

    def test_pattern_severity_levels(self):
        """Test that detected patterns have severity levels."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.80,
            "LC": 0.45,
            "AE": 0.85,
            "RCD": 0.75,
            "DF": 0.70,
            "PE": 0.50,
        }

        patterns = analyzer.detect_patterns(dimension_scores)

        for pattern in patterns:
            assert hasattr(pattern, "severity")
            assert pattern.severity in ["LOW", "MODERATE", "HIGH", "SEVERE"]

    def test_pattern_descriptions(self):
        """Test that patterns include human-readable descriptions."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.75,
            "LC": 0.45,
            "AE": 0.78,
            "RCD": 0.40,
            "DF": 0.50,
            "PE": 0.42,
        }

        patterns = analyzer.detect_patterns(dimension_scores)

        for pattern in patterns:
            assert hasattr(pattern, "description")
            assert isinstance(pattern.description, str)
            assert len(pattern.description) > 0

    def test_no_patterns_detected_low_scores(self):
        """Test that no patterns are detected with low dimension scores."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.20,
            "LC": 0.18,
            "AE": 0.22,
            "RCD": 0.15,
            "DF": 0.19,
            "PE": 0.17,
        }

        patterns = analyzer.detect_patterns(dimension_scores)

        # Should detect no concerning patterns with low scores
        concerning_patterns = [p for p in patterns if p.severity in ["HIGH", "SEVERE"]]
        assert len(concerning_patterns) == 0


class TestCrossDimensionalAnalyzer:
    """Test the main CrossDimensionalAnalyzer."""

    def test_analyzer_initialization(self):
        """Test creating a CrossDimensionalAnalyzer."""
        analyzer = CrossDimensionalAnalyzer()

        assert analyzer is not None
        assert hasattr(analyzer, "compute_correlation_matrix")
        assert hasattr(analyzer, "compute_risk_score")
        assert hasattr(analyzer, "detect_patterns")

    def test_analyze_entrain_report(self):
        """Test analyzing a complete EntrainReport."""
        analyzer = CrossDimensionalAnalyzer()

        # Create a mock EntrainReport
        dimension_reports = {
            "SR": DimensionReport(
                dimension="SR",
                version="0.2.1",
                indicators={"test": IndicatorResult("test", 0.65, 0.42, "%", None, "test")},
                summary="High SR",
                methodology_notes="Test",
                citations=[],
            ),
            "AE": DimensionReport(
                dimension="AE",
                version="0.2.1",
                indicators={"test": IndicatorResult("test", 0.70, 0.40, "%", None, "test")},
                summary="High AE",
                methodology_notes="Test",
                citations=[],
            ),
        }

        entrain_report = EntrainReport(
            version="0.2.1",
            generated_at=datetime.now(),
            input_summary={"conversations": 1},
            dimensions=dimension_reports,
            cross_dimensional=[],
            methodology="Test",
        )

        cross_dim_report = analyzer.analyze(entrain_report)

        assert isinstance(cross_dim_report, CrossDimensionalReport)
        assert hasattr(cross_dim_report, "risk_score")
        assert hasattr(cross_dim_report, "patterns")

    def test_analyze_with_corpus_data(self):
        """Test analyzing multiple conversations (corpus)."""
        analyzer = CrossDimensionalAnalyzer()

        # Simulate multiple EntrainReports (one per conversation)
        reports = []
        for i in range(5):
            dimension_reports = {
                "SR": DimensionReport(
                    dimension="SR",
                    version="0.2.1",
                    indicators={"test": IndicatorResult("test", 0.50 + i * 0.05, 0.42, "%", None, "test")},
                    summary="Test",
                    methodology_notes="Test",
                    citations=[],
                ),
                "AE": DimensionReport(
                    dimension="AE",
                    version="0.2.1",
                    indicators={"test": IndicatorResult("test", 0.55 + i * 0.05, 0.40, "%", None, "test")},
                    summary="Test",
                    methodology_notes="Test",
                    citations=[],
                ),
            }

            report = EntrainReport(
                version="0.2.1",
                generated_at=datetime.now(),
                input_summary={"conversations": 1},
                dimensions=dimension_reports,
                cross_dimensional=[],
                methodology="Test",
            )
            reports.append(report)

        cross_dim_report = analyzer.analyze_corpus(reports)

        assert isinstance(cross_dim_report, CrossDimensionalReport)
        assert hasattr(cross_dim_report, "correlation_matrix")


class TestCrossDimensionalReport:
    """Test the CrossDimensionalReport data model."""

    def test_cross_dimensional_report_creation(self):
        """Test creating a CrossDimensionalReport."""
        risk_score = RiskScore(
            score=0.65,
            level="HIGH",
            interpretation="High risk detected",
            top_contributors=["SR", "AE"],
        )

        patterns = [
            Pattern(
                pattern_id="high_sr_high_ae",
                description="High sycophantic reinforcement combined with autonomy erosion",
                severity="HIGH",
                dimensions_involved=["SR", "AE"],
                recommendation="Consider reducing reliance on AI for decision-making",
            )
        ]

        correlation_matrix = CorrelationMatrix(
            dimensions=["SR", "AE"],
            correlations={("SR", "AE"): 0.85},
            insufficient_data=False,
        )

        report = CrossDimensionalReport(
            risk_score=risk_score,
            patterns=patterns,
            correlation_matrix=correlation_matrix,
            summary="High risk with multiple concerning patterns",
        )

        assert report.risk_score.level == "HIGH"
        assert len(report.patterns) == 1
        assert report.correlation_matrix.get_correlation("SR", "AE") == 0.85

    def test_cross_dimensional_report_summary_generation(self):
        """Test automatic summary generation."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.75,
            "LC": 0.45,
            "AE": 0.78,
            "RCD": 0.40,
            "DF": 0.50,
            "PE": 0.42,
        }

        risk_score = analyzer.compute_risk_score(dimension_scores)
        patterns = analyzer.detect_patterns(dimension_scores)

        report = CrossDimensionalReport.create(
            risk_score=risk_score,
            patterns=patterns,
            correlation_matrix=None,
        )

        assert hasattr(report, "summary")
        assert isinstance(report.summary, str)
        assert len(report.summary) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dimension_scores(self):
        """Test handling empty dimension scores."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {}

        risk_score = analyzer.compute_risk_score(dimension_scores)

        # Should return low risk or handle gracefully
        assert risk_score.level == "LOW"

    def test_partial_dimension_scores(self):
        """Test handling partial dimension scores (missing dimensions)."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 0.75,
            "AE": 0.78,
            # Missing LC, RCD, DF, PE
        }

        risk_score = analyzer.compute_risk_score(dimension_scores)
        patterns = analyzer.detect_patterns(dimension_scores)

        # Should handle gracefully
        assert isinstance(risk_score, RiskScore)
        assert isinstance(patterns, list)

    def test_invalid_dimension_scores(self):
        """Test handling invalid dimension scores (out of range)."""
        analyzer = CrossDimensionalAnalyzer()

        dimension_scores = {
            "SR": 1.5,  # Invalid: > 1.0
            "LC": -0.2,  # Invalid: < 0.0
            "AE": 0.75,
        }

        # Should normalize or reject invalid scores
        risk_score = analyzer.compute_risk_score(dimension_scores)

        # Score should be clamped to valid range
        assert 0.0 <= risk_score.score <= 1.0

    def test_correlation_with_nan_values(self):
        """Test correlation computation with NaN values."""
        analyzer = CrossDimensionalAnalyzer()

        samples = [
            {"SR": 0.65, "LC": 0.58, "AE": None, "RCD": 0.45, "DF": 0.55, "PE": 0.50},
            {"SR": 0.45, "LC": 0.42, "AE": 0.50, "RCD": None, "DF": 0.40, "PE": 0.38},
        ]

        # Should handle missing values gracefully
        correlation_matrix = analyzer.compute_correlation_matrix(samples)

        assert isinstance(correlation_matrix, CorrelationMatrix)
