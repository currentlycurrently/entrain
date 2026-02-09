# Interpretation Layer Rework

**Date:** February 9, 2026
**Status:** Planning
**Goal:** Fix the interpretation layer to be descriptive, not diagnostic

---

## The Problem

The library has good measurement primitives but immature interpretation:

**What works:**
- ✅ Six dimension taxonomy is solid
- ✅ Indicators are reasonable starting points
- ✅ Measurements are grounded in research
- ✅ Text/audio feature extraction is sound

**What's immature:**
- ❌ HIGH/MODERATE/LOW severity labels imply objective danger
- ❌ Single-conversation analysis treated as meaningful (it's not)
- ❌ Reports read like diagnoses, not research measurements
- ❌ No explicit limitations or interpretive guardrails
- ❌ Oversimplifies complex, contextual, longitudinal phenomena

**The core issue:** Outputs pretend to know more than they do.

---

## What the Library Actually Is

**This is:**
- Research infrastructure
- Measurement primitives for running studies
- Instruments that require expertise to use and interpret
- Tools for longitudinal analysis

**This is NOT:**
- Consumer self-diagnosis tool
- AI safety scanner
- Objective measure of cognitive harm
- Something anyone should `pip install` and run once

**First real user:** The maintainer, running longitudinal self-study of own AI interactions.

**First real use case:** Export ChatGPT data monthly, track dimension measurements over time, observe what actually changes.

---

## Guiding Principles for Rework

1. **Descriptive, not diagnostic**
   Report what was measured. Don't claim to know what it means without context.

2. **Explicit about limitations**
   Every output should state what it does and doesn't measure.

3. **Longitudinal by default**
   Single-conversation analysis is a building block, not the end product.

4. **Research-grade humility**
   Present data and research context. Let the researcher interpret.

5. **Microscope, not virus scan**
   Show what's there. Don't issue verdicts.

---

## Changes Required

### 1. Data Model Changes

**File:** `entrain/models.py`

**Current `DimensionReport`:**
```python
@dataclass
class DimensionReport:
    dimension: str
    severity: str  # "HIGH", "MODERATE", "LOW"
    summary: str   # "HIGH - Strong sycophantic reinforcement..."
    indicators: Dict[str, IndicatorResult]
    methodology_notes: List[str]
    citations: List[str]
```

**New `DimensionReport`:**
```python
@dataclass
class DimensionReport:
    dimension: str
    description: str  # Factual description of measurements
    indicators: Dict[str, IndicatorResult]
    baseline_comparison: str  # How measurements compare to research baselines
    research_context: str  # What published research says about these patterns
    limitations: List[str]  # What this measurement does/doesn't tell you
    trajectory: Optional[TrajectoryData]  # If longitudinal data available
    methodology_notes: List[str]
    citations: List[str]
    timestamp: datetime
```

**New model: `TrajectoryData`:**
```python
@dataclass
class TrajectoryData:
    """Longitudinal measurement tracking"""
    snapshots: List[Snapshot]  # List of measurements over time
    trend: str  # "increasing", "decreasing", "stable", "insufficient_data"
    slope: Optional[float]  # Rate of change if calculable
    confidence: str  # How reliable the trajectory assessment is
```

**New model: `LongitudinalReport`:**
```python
@dataclass
class LongitudinalReport:
    """Primary report type for time-series analysis"""
    corpus_id: str
    time_range: Tuple[datetime, datetime]
    snapshot_count: int
    dimensions: Dict[str, DimensionReport]  # Each includes trajectory
    cross_dimensional: Optional[CrossDimensionalAnalysis]
    interpretation_notes: List[str]  # Explicit guidance on reading results
```

### 2. Analyzer Changes

**Files:** All `entrain/dimensions/*.py` analyzers

**Remove:**
- `_interpret_severity()` methods
- Threshold-based severity classification
- Any language that sounds like diagnosis

**Add:**
- `_describe_measurement()` - factual description
- `_baseline_comparison()` - comparison to research norms
- `_research_context()` - what studies say about patterns
- `_measurement_limitations()` - what this doesn't capture

**Example (SR Analyzer):**

```python
def _describe_measurement(self, aer: float, pmr: float) -> str:
    """Factual description of sycophancy measurements"""
    return (
        f"Action Endorsement Rate: {aer:.1%}. The AI affirmed user actions "
        f"in {aer:.1%} of interactions where actions were mentioned. "
        f"Perspective Mention Rate: {pmr:.1%}."
    )

def _baseline_comparison(self, aer: float) -> str:
    """Compare to research baselines without interpretation"""
    human_baseline = 0.42
    llm_median = 0.63
    diff_human = (aer - human_baseline) * 100

    return (
        f"Measured AER is {diff_human:+.1f} percentage points "
        f"{'above' if diff_human > 0 else 'below'} human-human baseline (42%) "
        f"and {'aligns with' if abs(aer - llm_median) < 0.05 else 'differs from'} "
        f"typical LLM behavior (63% median, Cheng et al. 2025)."
    )

def _research_context(self) -> str:
    """What research says about sycophancy patterns"""
    return (
        "Cheng et al. (2025) found that sycophantic AI reduces critical "
        "thinking and increases dependency in controlled studies. Effect sizes "
        "were moderate (d=0.3-0.5) and varied by task complexity. "
        "Sharma et al. (2023) observed correlation between high AER and "
        "user over-confidence in decisions. Causal mechanisms remain unclear."
    )

def _measurement_limitations(self) -> List[str]:
    """What this measurement doesn't tell you"""
    return [
        "Text pattern matching cannot assess contextual appropriateness",
        "Single conversation insufficient for cognitive impact assessment",
        "Does not measure actual changes in user critical thinking",
        "Cannot distinguish helpful support from harmful sycophancy",
        "Requires longitudinal data (3+ months) for meaningful interpretation"
    ]
```

### 3. Report Generator Changes

**Files:** `entrain/reporting/*.py`

**Markdown report (current):**
```markdown
## Sycophantic Reinforcement (SR)

**Severity:** HIGH
**Summary:** Strong sycophantic reinforcement detected

### Indicators
- Action Endorsement Rate: 65.0% (baseline: 42.0%)
```

**Markdown report (new):**
```markdown
## Sycophantic Reinforcement (SR)

### Measurement Summary
Action Endorsement Rate: 65.0%
Perspective Mention Rate: 8.2%
Challenge Frequency: 12.3%
Validation Language Density: 0.18 per message

### Comparison to Research Baselines
- AER is +23.0 percentage points above human-human baseline (42%)
- Aligns with typical LLM behavior (63% median, Cheng et al. 2025)
- PMR is within expected range for AI assistants (<10%)

### Research Context
Cheng et al. (2025) found that sycophantic AI reduces critical thinking
and increases dependency in controlled studies. Effect sizes were moderate
(d=0.3-0.5) and varied by task complexity. Sharma et al. (2023) observed
correlation between high AER and user over-confidence in decisions.

### What This Measurement Shows
- Frequency of AI affirming user actions without critique
- Text-based pattern matching of endorsement/validation language
- Snapshot of interaction patterns in this conversation/corpus

### What This Measurement Does NOT Show
- Whether endorsement was contextually appropriate
- Impact on your decision-making or critical thinking ability
- Causal relationship between AI behavior and cognitive changes
- Long-term effects (requires 3+ months of tracking)

### Interpretation Guidance
These measurements describe patterns in text-based interaction. They do
not constitute clinical assessment. Interpretation requires context about
your usage patterns, the nature of your conversations, and comparison
across multiple time points. Single-conversation analysis should not be
used to draw conclusions about cognitive effects.

See FRAMEWORK.md for full methodology and research foundation.
```

### 4. CLI Output Changes

**Current:**
```bash
$ entrain analyze conversations.json

Analyzing conversation: "Work brainstorming session"
SR: HIGH - Strong sycophantic reinforcement detected
LC: MODERATE - Linguistic convergence: 58.3%
AE: LOW - Minimal autonomy erosion
```

**New:**
```bash
$ entrain analyze conversations.json

=== Conversation Analysis: "Work brainstorming session" ===
352 interactions | Jan 15 - Feb 8, 2026

SYCOPHANTIC REINFORCEMENT (SR)
  AER: 65.0% (human baseline: 42.0%, +23.0pp)
  PMR: 8.2%  (typical AI: <10%)
  Challenges: 12.3% of responses

  Pattern: High endorsement frequency, typical for AI assistants
  See detailed report for research context and limitations

LINGUISTIC CONVERGENCE (LC)
  Overall convergence: 58.3%
  Vocabulary overlap trajectory: +12% over session
  Hedging pattern adoption: 45 AI-characteristic phrases adopted

  Pattern: Moderate convergence toward AI writing patterns
  See detailed report for research context and limitations

AUTONOMY EROSION (AE)
  Decision delegation: 8.2% of interactions
  Critical engagement: 78% of responses

  Pattern: Low delegation, high critical engagement
  See detailed report for research context and limitations

─────────────────────────────────────────────────────────────
Note: Single-conversation measurements are insufficient for
assessing cognitive effects. Run analysis monthly and use
`entrain compare` to track trajectories over time.

For detailed interpretation: entrain report conversations.json
─────────────────────────────────────────────────────────────
```

### 5. New: Longitudinal Comparison Command

**Command:**
```bash
$ entrain compare jan.json feb.json mar.json
```

**Output:**
```bash
=== Longitudinal Analysis ===
3 snapshots | Jan - Mar 2026 | 1,247 total interactions

SYCOPHANTIC REINFORCEMENT (SR)
  Jan: AER 58% | Feb: AER 62% | Mar: AER 65%
  Trajectory: Increasing (+7pp over 3 months)
  Trend confidence: Low (only 3 data points)

  Pattern: Consistent upward trend in endorsement frequency
  Research context: Cheng et al. found AER increases over time
  correlate with dependency formation (r=0.41, p<0.01)

  Next steps: Continue monthly tracking for statistical trend

LINGUISTIC CONVERGENCE (LC)
  Jan: 52% | Feb: 55% | Mar: 58%
  Trajectory: Increasing (+6pp over 3 months)

  Pattern: Gradual convergence toward AI writing patterns

CROSS-DIMENSIONAL PATTERNS
  SR and LC show positive correlation (r=0.89)
  Both dimensions trending upward
  Pattern consistent with "compound influence" (Kirk et al. 2025)

─────────────────────────────────────────────────────────────
Interpretation: 3 months of data shows consistent patterns but
insufficient duration for causal claims. Recommend 6-12 months
tracking for meaningful cognitive impact assessment.
─────────────────────────────────────────────────────────────
```

---

## Implementation Plan

### Phase 1: Data Model Changes (2-3 hours)
1. Update `DimensionReport` in `entrain/models.py`
2. Add `TrajectoryData` and `LongitudinalReport` models
3. Update all dimension analyzers to use new report structure
4. **Tests:** Update model tests, ensure backwards compatibility

### Phase 2: Analyzer Rewrites (4-6 hours)
1. Remove all severity classification logic
2. Add description, comparison, context, limitations methods
3. Update all 6 dimension analyzers (SR, LC, AE, RCD, DF, PE)
4. **Tests:** Verify outputs are descriptive not diagnostic

### Phase 3: Report Generators (3-4 hours)
1. Rewrite markdown report templates
2. Update JSON report structure
3. Add longitudinal report generator
4. **Tests:** Verify report formatting and content

### Phase 4: CLI Updates (2-3 hours)
1. Reformat `entrain analyze` output
2. Add `entrain compare` command for longitudinal analysis
3. Add interpretive notes to all CLI outputs
4. **Tests:** CLI integration tests

### Phase 5: Documentation (1-2 hours)
1. Update README with new interpretation approach
2. Add interpretation guidelines to FRAMEWORK.md
3. Update examples to show longitudinal use
4. Add "How to Interpret Results" guide

### Phase 6: Real-World Testing (2-3 hours)
1. Run on your actual ChatGPT exports
2. Verify outputs feel mature and honest
3. Check that limitations are clear
4. Iterate based on real data

**Total estimated effort:** 14-21 hours

---

## Success Criteria

The rework is complete when:

1. ✅ No HIGH/MODERATE/LOW severity labels anywhere
2. ✅ All reports include explicit limitations
3. ✅ Single-conversation analysis includes warning about insufficient data
4. ✅ Longitudinal comparison is the primary recommended use
5. ✅ Outputs read like research instruments, not medical diagnoses
6. ✅ A non-expert reading a report understands what it does/doesn't tell them
7. ✅ You can run it on your own data and the output feels mature

---

## After This Rework

**Then we can:**
- Release framework documents (FRAMEWORK.md, RESEARCH.md) publicly
- Keep library on GitHub as research tooling
- Consider PyPI release once interpretation is proven mature
- Use the library for actual longitudinal self-study
- Build on real findings, not hypothetical features

**We will NOT:**
- Build Phase 4.3 features (forecasting, anomaly detection) yet
- Market this as a consumer tool
- Claim it measures cognitive harm
- Release before the interpretation feels honest

---

**Next step:** Start Phase 1 - data model changes.
