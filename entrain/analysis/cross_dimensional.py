"""
Cross-dimensional analysis for the Entrain Framework.

This module provides:
- Correlation analysis between dimensions
- Overall risk scoring and classification
- Pattern detection across dimensions
- Cross-dimensional insights and recommendations
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import statistics
from entrain.models import EntrainReport, DimensionReport


@dataclass
class CorrelationMatrix:
    """
    Correlation matrix between dimension scores.

    Attributes:
        dimensions: List of dimension codes (e.g., ["SR", "LC", "AE", ...])
        correlations: Dict mapping (dim1, dim2) tuples to correlation coefficients
        insufficient_data: True if not enough data points for reliable correlation
    """

    dimensions: List[str]
    correlations: Dict[Tuple[str, str], float]
    insufficient_data: bool = False

    def get_correlation(self, dim1: str, dim2: str) -> Optional[float]:
        """
        Get correlation coefficient between two dimensions.

        Args:
            dim1: First dimension code
            dim2: Second dimension code

        Returns:
            Correlation coefficient (-1 to 1) or None if not available
        """
        # Try both orderings (matrix is symmetric)
        if (dim1, dim2) in self.correlations:
            return self.correlations[(dim1, dim2)]
        elif (dim2, dim1) in self.correlations:
            return self.correlations[(dim2, dim1)]
        return None

    def get_strong_correlations(self, threshold: float = 0.7) -> List[Tuple[str, str, float]]:
        """
        Get pairs of dimensions with strong correlation (|r| > threshold).

        Args:
            threshold: Minimum absolute correlation value (default: 0.7)

        Returns:
            List of (dim1, dim2, correlation) tuples
        """
        strong = []
        seen = set()

        for (dim1, dim2), corr in self.correlations.items():
            # Avoid duplicates due to symmetry
            pair = tuple(sorted([dim1, dim2]))

            # Skip self-correlations and duplicates
            if dim1 == dim2 or pair in seen:
                continue

            if abs(corr) >= threshold:
                strong.append((dim1, dim2, corr))
                seen.add(pair)

        # Sort by absolute correlation (strongest first)
        return sorted(strong, key=lambda x: abs(x[2]), reverse=True)


@dataclass
class RiskScore:
    """
    Overall risk score aggregating all dimensions.

    Attributes:
        score: Numeric risk score (0.0 to 1.0)
        level: Risk level classification (LOW, MODERATE, HIGH, SEVERE)
        interpretation: Human-readable interpretation
        top_contributors: Dimensions contributing most to risk score
    """

    score: float
    level: str  # LOW, MODERATE, HIGH, SEVERE
    interpretation: str
    top_contributors: List[str]


@dataclass
class Pattern:
    """
    Detected cross-dimensional pattern.

    Attributes:
        pattern_id: Unique identifier for the pattern type
        description: Human-readable description
        severity: Pattern severity (LOW, MODERATE, HIGH, SEVERE)
        dimensions_involved: List of dimension codes involved
        recommendation: Suggested action or interpretation
    """

    pattern_id: str
    description: str
    severity: str  # LOW, MODERATE, HIGH, SEVERE
    dimensions_involved: List[str]
    recommendation: str


@dataclass
class CrossDimensionalReport:
    """
    Complete cross-dimensional analysis report.

    Attributes:
        risk_score: Overall risk assessment
        patterns: List of detected patterns
        correlation_matrix: Correlation matrix (if corpus analysis)
        summary: Executive summary of findings
    """

    risk_score: RiskScore
    patterns: List[Pattern]
    correlation_matrix: Optional[CorrelationMatrix] = None
    summary: str = ""

    @classmethod
    def create(
        cls,
        risk_score: RiskScore,
        patterns: List[Pattern],
        correlation_matrix: Optional[CorrelationMatrix] = None,
    ) -> "CrossDimensionalReport":
        """
        Create a CrossDimensionalReport with auto-generated summary.

        Args:
            risk_score: Overall risk score
            patterns: Detected patterns
            correlation_matrix: Optional correlation matrix

        Returns:
            CrossDimensionalReport instance
        """
        # Generate summary
        summary_parts = [
            f"Overall Risk: {risk_score.level} ({risk_score.score:.0%})"
        ]

        if patterns:
            high_severity_patterns = [p for p in patterns if p.severity in ["HIGH", "SEVERE"]]
            if high_severity_patterns:
                summary_parts.append(f"{len(high_severity_patterns)} concerning pattern(s) detected")

        if risk_score.top_contributors:
            summary_parts.append(f"Primary concerns: {', '.join(risk_score.top_contributors)}")

        summary = ". ".join(summary_parts) + "."

        return cls(
            risk_score=risk_score,
            patterns=patterns,
            correlation_matrix=correlation_matrix,
            summary=summary,
        )


class CrossDimensionalAnalyzer:
    """
    Analyzer for cross-dimensional patterns and correlations.

    This analyzer computes:
    - Correlation matrices between dimensions
    - Overall risk scores
    - Cross-dimensional patterns
    """

    # Default weights for risk scoring
    DEFAULT_WEIGHTS = {
        "SR": 1.0,
        "LC": 0.9,
        "AE": 1.5,  # Autonomy erosion weighted more heavily
        "RCD": 1.3,  # Reality coherence disruption is serious
        "DF": 1.2,  # Dependency formation is concerning
        "PE": 0.8,  # Prosodic entrainment is less severe
    }

    # Risk level thresholds
    RISK_THRESHOLDS = {
        "LOW": 0.35,
        "MODERATE": 0.55,
        "HIGH": 0.75,
        "SEVERE": 1.0,
    }

    def compute_correlation_matrix(
        self, samples: List[Dict[str, float]]
    ) -> CorrelationMatrix:
        """
        Compute correlation matrix from multiple dimension score samples.

        Args:
            samples: List of dicts mapping dimension codes to scores

        Returns:
            CorrelationMatrix instance
        """
        if len(samples) < 2:
            # Need at least 2 samples to compute correlation
            dimensions = list(samples[0].keys()) if samples else []
            return CorrelationMatrix(
                dimensions=dimensions,
                correlations={},
                insufficient_data=True,
            )

        # Get all dimensions
        dimensions = list(samples[0].keys())

        # Compute correlations for all pairs
        correlations = {}

        for i, dim1 in enumerate(dimensions):
            for j, dim2 in enumerate(dimensions):
                # Extract values for both dimensions (handling None values)
                values1 = []
                values2 = []

                for sample in samples:
                    v1 = sample.get(dim1)
                    v2 = sample.get(dim2)

                    if v1 is not None and v2 is not None:
                        values1.append(v1)
                        values2.append(v2)

                # Compute correlation
                if len(values1) >= 2:
                    corr = self._pearson_correlation(values1, values2)
                    correlations[(dim1, dim2)] = corr

        return CorrelationMatrix(
            dimensions=dimensions,
            correlations=correlations,
            insufficient_data=False,
        )

    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """
        Compute Pearson correlation coefficient.

        Args:
            x: First variable values
            y: Second variable values

        Returns:
            Correlation coefficient (-1 to 1)
        """
        if len(x) != len(y) or len(x) < 2:
            return 0.0

        # Calculate means
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)

        # Calculate correlation
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))

        sum_sq_x = sum((xi - mean_x) ** 2 for xi in x)
        sum_sq_y = sum((yi - mean_y) ** 2 for yi in y)

        denominator = (sum_sq_x * sum_sq_y) ** 0.5

        if denominator == 0:
            return 0.0

        correlation = numerator / denominator

        # Clamp to [-1, 1] to handle floating point errors
        return max(-1.0, min(1.0, correlation))

    def compute_risk_score(
        self,
        dimension_scores: Dict[str, float],
        weights: Optional[Dict[str, float]] = None,
    ) -> RiskScore:
        """
        Compute overall risk score from dimension scores.

        Args:
            dimension_scores: Dict mapping dimension codes to scores (0-1)
            weights: Optional custom weights for dimensions

        Returns:
            RiskScore instance
        """
        if not dimension_scores:
            return RiskScore(
                score=0.0,
                level="LOW",
                interpretation="No dimension scores available for risk assessment.",
                top_contributors=[],
            )

        # Use default weights if not provided
        if weights is None:
            weights = self.DEFAULT_WEIGHTS

        # Normalize scores to [0, 1] range
        normalized_scores = {}
        for dim, score in dimension_scores.items():
            # Clamp to valid range
            normalized_scores[dim] = max(0.0, min(1.0, score))

        # Compute weighted average
        weighted_sum = 0.0
        total_weight = 0.0

        for dim, score in normalized_scores.items():
            weight = weights.get(dim, 1.0)
            weighted_sum += score * weight
            total_weight += weight

        if total_weight == 0:
            overall_score = 0.0
        else:
            overall_score = weighted_sum / total_weight

        # Classify risk level
        if overall_score < self.RISK_THRESHOLDS["LOW"]:
            level = "LOW"
        elif overall_score < self.RISK_THRESHOLDS["MODERATE"]:
            level = "MODERATE"
        elif overall_score < self.RISK_THRESHOLDS["HIGH"]:
            level = "HIGH"
        else:
            level = "SEVERE"

        # Identify top contributors (top 3 highest scores)
        sorted_dims = sorted(
            normalized_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        top_contributors = [dim for dim, score in sorted_dims[:3] if score > 0.5]

        # Generate interpretation
        interpretation = self._generate_risk_interpretation(
            level, overall_score, top_contributors
        )

        return RiskScore(
            score=overall_score,
            level=level,
            interpretation=interpretation,
            top_contributors=top_contributors,
        )

    def _generate_risk_interpretation(
        self, level: str, score: float, contributors: List[str]
    ) -> str:
        """Generate human-readable risk interpretation."""
        interpretations = {
            "LOW": f"Low risk detected ({score:.0%}). AI interaction patterns appear healthy with minimal concerning indicators.",
            "MODERATE": f"Moderate risk detected ({score:.0%}). Some concerning patterns observed that warrant monitoring.",
            "HIGH": f"High risk detected ({score:.0%}). Multiple concerning patterns identified that suggest significant cognitive influence.",
            "SEVERE": f"Severe risk detected ({score:.0%}). Critical patterns identified indicating substantial cognitive influence and potential harm.",
        }

        base_interpretation = interpretations.get(level, "Risk level unknown.")

        if contributors:
            dim_names = {
                "SR": "Sycophantic Reinforcement",
                "LC": "Linguistic Convergence",
                "AE": "Autonomy Erosion",
                "RCD": "Reality Coherence Disruption",
                "DF": "Dependency Formation",
                "PE": "Prosodic Entrainment",
            }
            contributor_names = [dim_names.get(c, c) for c in contributors]
            base_interpretation += f" Primary concerns: {', '.join(contributor_names)}."

        return base_interpretation

    def detect_patterns(self, dimension_scores: Dict[str, float]) -> List[Pattern]:
        """
        Detect cross-dimensional patterns.

        Args:
            dimension_scores: Dict mapping dimension codes to scores (0-1)

        Returns:
            List of detected Pattern instances
        """
        patterns = []

        # Get scores (default to 0 if missing)
        sr = dimension_scores.get("SR", 0.0)
        lc = dimension_scores.get("LC", 0.0)
        ae = dimension_scores.get("AE", 0.0)
        rcd = dimension_scores.get("RCD", 0.0)
        df = dimension_scores.get("DF", 0.0)
        pe = dimension_scores.get("PE", 0.0)

        # Pattern 1: High SR + High AE (Sycophancy enabling erosion)
        if sr > 0.65 and ae > 0.65:
            severity = "SEVERE" if (sr > 0.8 and ae > 0.8) else "HIGH"
            patterns.append(
                Pattern(
                    pattern_id="high_sr_high_ae",
                    description="High sycophantic reinforcement combined with autonomy erosion indicates the AI is both affirming user decisions uncritically AND the user is increasingly delegating decision-making to the AI.",
                    severity=severity,
                    dimensions_involved=["SR", "AE"],
                    recommendation="Consider seeking diverse perspectives and making decisions independently before consulting AI.",
                )
            )

        # Pattern 2: High RCD + High DF (Reality confusion with dependency)
        if rcd > 0.65 and df > 0.60:
            severity = "SEVERE" if (rcd > 0.8 and df > 0.75) else "HIGH"
            patterns.append(
                Pattern(
                    pattern_id="high_rcd_high_df",
                    description="Reality coherence disruption combined with dependency formation suggests blurred boundaries between AI capabilities and human relationships.",
                    severity=severity,
                    dimensions_involved=["RCD", "DF"],
                    recommendation="Reflect on the nature of AI interactions and maintain clear boundaries between AI tools and human relationships.",
                )
            )

        # Pattern 3: High LC + High PE (Multi-modal convergence)
        if lc > 0.70 and pe > 0.70:
            severity = "HIGH" if (lc > 0.85 and pe > 0.85) else "MODERATE"
            patterns.append(
                Pattern(
                    pattern_id="convergence_linguistic_prosodic",
                    description="Both linguistic and prosodic convergence detected, indicating multi-modal adaptation to AI communication patterns.",
                    severity=severity,
                    dimensions_involved=["LC", "PE"],
                    recommendation="Monitor communication patterns outside of AI interactions to ensure natural expression is maintained.",
                )
            )

        # Pattern 4: High across all dimensions (Systemic influence)
        high_count = sum(1 for score in [sr, lc, ae, rcd, df, pe] if score > 0.65)
        if high_count >= 4:
            patterns.append(
                Pattern(
                    pattern_id="systemic_high_influence",
                    description=f"Widespread cognitive influence detected across {high_count} dimensions, indicating systemic impact on cognition and behavior.",
                    severity="SEVERE",
                    dimensions_involved=[d for d, s in dimension_scores.items() if s > 0.65],
                    recommendation="Consider a significant reduction in AI interaction frequency and diversity. Seek support from human relationships and professional guidance if needed.",
                )
            )

        # Pattern 5: Moderate SR + High AE (Erosion without obvious sycophancy)
        if 0.45 < sr < 0.65 and ae > 0.70:
            patterns.append(
                Pattern(
                    pattern_id="moderate_sr_high_ae",
                    description="High autonomy erosion without extreme sycophantic reinforcement suggests dependency on AI judgment even when AI provides balanced responses.",
                    severity="MODERATE",
                    dimensions_involved=["SR", "AE"],
                    recommendation="Practice making decisions without AI input, even for low-stakes choices.",
                )
            )

        # Pattern 6: Isolated high dimension (Single-dimension concern)
        for dim, score in dimension_scores.items():
            if score > 0.80:
                # Check if this is the only high dimension
                other_high = sum(1 for d, s in dimension_scores.items() if d != dim and s > 0.65)
                if other_high == 0:
                    dim_names = {
                        "SR": "Sycophantic Reinforcement",
                        "LC": "Linguistic Convergence",
                        "AE": "Autonomy Erosion",
                        "RCD": "Reality Coherence Disruption",
                        "DF": "Dependency Formation",
                        "PE": "Prosodic Entrainment",
                    }
                    patterns.append(
                        Pattern(
                            pattern_id=f"isolated_high_{dim.lower()}",
                            description=f"Isolated high score in {dim_names.get(dim, dim)} without other concerning patterns.",
                            severity="MODERATE",
                            dimensions_involved=[dim],
                            recommendation=f"Focus on addressing {dim_names.get(dim, dim)} specifically while maintaining awareness of overall interaction patterns.",
                        )
                    )

        return patterns

    def analyze(self, entrain_report: EntrainReport) -> CrossDimensionalReport:
        """
        Analyze a single EntrainReport for cross-dimensional patterns.

        Args:
            entrain_report: Complete Entrain analysis report

        Returns:
            CrossDimensionalReport instance
        """
        # Extract dimension scores (average of all indicators per dimension)
        dimension_scores = {}

        for dim_code, dim_report in entrain_report.dimensions.items():
            # Average all indicator values for this dimension
            indicator_values = [
                ind.value for ind in dim_report.indicators.values()
                if ind.value is not None
            ]

            if indicator_values:
                dimension_scores[dim_code] = statistics.mean(indicator_values)

        # Compute risk score
        risk_score = self.compute_risk_score(dimension_scores)

        # Detect patterns
        patterns = self.detect_patterns(dimension_scores)

        # No correlation matrix for single report
        return CrossDimensionalReport.create(
            risk_score=risk_score,
            patterns=patterns,
            correlation_matrix=None,
        )

    def analyze_corpus(self, entrain_reports: List[EntrainReport]) -> CrossDimensionalReport:
        """
        Analyze multiple EntrainReports (corpus) for correlations and patterns.

        Args:
            entrain_reports: List of Entrain analysis reports

        Returns:
            CrossDimensionalReport instance with correlation matrix
        """
        # Extract dimension scores from each report
        samples = []

        for report in entrain_reports:
            scores = {}
            for dim_code, dim_report in report.dimensions.items():
                indicator_values = [
                    ind.value for ind in dim_report.indicators.values()
                    if ind.value is not None
                ]
                if indicator_values:
                    scores[dim_code] = statistics.mean(indicator_values)

            if scores:
                samples.append(scores)

        # Compute correlation matrix
        correlation_matrix = self.compute_correlation_matrix(samples)

        # Compute overall risk score (average across all reports)
        if samples:
            avg_scores = {}
            all_dims = set()
            for sample in samples:
                all_dims.update(sample.keys())

            for dim in all_dims:
                dim_values = [s.get(dim, 0.0) for s in samples]
                avg_scores[dim] = statistics.mean(dim_values)

            risk_score = self.compute_risk_score(avg_scores)
            patterns = self.detect_patterns(avg_scores)
        else:
            risk_score = RiskScore(
                score=0.0,
                level="LOW",
                interpretation="Insufficient data for corpus analysis.",
                top_contributors=[],
            )
            patterns = []

        return CrossDimensionalReport.create(
            risk_score=risk_score,
            patterns=patterns,
            correlation_matrix=correlation_matrix,
        )
