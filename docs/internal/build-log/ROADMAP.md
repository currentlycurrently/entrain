# Entrain Project Roadmap

**Current Version:** 0.2.0
**Last Updated:** February 8, 2026
**Status:** Phase 3 Complete, Phase 3.5 (Quality) in planning

---

## Project Vision

Build a **research-grade, privacy-first Python library** for measuring AI cognitive influence on humans across 6 framework dimensions. The library should be composable, well-tested, and serve as the reference implementation of the Entrain Framework.

---

## Completed Phases

### ✅ Phase 1 - Foundation (v0.1.0)

**Goal:** Implement core infrastructure and text-based dimension analyzers.

**Completed:**
- Core data models (InteractionEvent, Conversation, Corpus, Reports)
- ChatGPT export parser
- Text feature extraction (vocabulary, hedging, validation, attribution patterns)
- Temporal feature extraction (frequency trends, time-of-day distribution)
- **5 text-based dimension analyzers:**
  - SR (Sycophantic Reinforcement) - 4 indicators
  - LC (Linguistic Convergence) - 5 indicators
  - AE (Autonomy Erosion) - 3 indicators
  - RCD (Reality Coherence Disruption) - 3 indicators
  - DF (Dependency Formation) - 5 indicators
- Basic CLI (parse, analyze, report, info)
- Reporting modules (JSON, Markdown, CSV)
- Initial documentation

**Metrics:**
- ~10,000 lines of Python code
- 1/6 dimensions tested (SR partial)
- 1 platform supported (ChatGPT)

---

### ✅ Phase 2 - Multi-Platform Support (v0.2.0)

**Goal:** Support major AI chat platforms beyond ChatGPT.

**Completed:**
- Claude conversation parser (JSON, JSONL, ZIP formats)
- Character.AI parser (JSON, swipes, histories)
- Generic CSV/JSON parser (universal fallback)
- Parser auto-detection registry
- Updated CLI for all platforms
- Parser documentation

**Metrics:**
- 4 platforms supported
- Basic parser tests
- ~1,500 lines added

---

### ✅ Phase 3 - Audio Analysis (v0.2.0)

**Goal:** Add voice interaction analysis capabilities and PE dimension.

**Completed:**
- Audio feature extraction (openSMILE + librosa)
- **PE (Prosodic Entrainment) dimension analyzer** - 6 indicators:
  - Pitch Convergence
  - Speech Rate Alignment
  - Intensity Convergence
  - Spectral Similarity
  - Overall Prosodic Convergence
  - Convergence Trend
- Comprehensive audio tests (380 lines)
- Comprehensive PE tests (513 lines)
- Phase 3 example (453 lines)
- Complete documentation (PHASE3_SUMMARY.md, PHASE3_VERIFICATION.md)

**Metrics:**
- 6/6 dimensions implemented
- 1/6 dimensions fully tested (PE)
- ~2,400 lines added
- Optional audio dependencies

---

## Current Phase

### 🔴 Phase 3.5 - Quality & Testing (URGENT)

**Goal:** Achieve production-quality test coverage before adding new features.

**Status:** Planned, not started

**Timeline:** 1-2 weeks

**Why this is critical:**
- 5/6 dimension analyzers have **zero test coverage**
- Cannot verify correctness of ~2,600 lines of analyzer code
- Risky for users - untested code may have bugs
- Cannot safely refactor or add features

**Tasks:**

#### 1. Write Dimension Tests (Priority 1)
- [ ] `test_sycophantic_reinforcement.py` - Test 4 SR indicators
- [ ] `test_linguistic_convergence.py` - Test 5 LC indicators
- [ ] `test_autonomy_erosion.py` - Test 3 AE indicators
- [ ] `test_reality_coherence.py` - Test 3 RCD indicators
- [ ] `test_dependency_formation.py` - Test 3 DF indicators
- **Target:** ~300-400 lines per test file (match PE quality)

#### 2. Write Feature Tests (Priority 2)
- [ ] `test_text.py` - Test all TextFeatureExtractor methods
- [ ] `test_temporal.py` - Test TemporalFeatureExtractor
- **Target:** ~200-300 lines per test file

#### 3. Verify Existing Modules (Priority 3)
- [ ] Test JSON report generation end-to-end
- [ ] Test Markdown report generation end-to-end
- [ ] Test CSV export end-to-end
- [ ] Test all 4 CLI commands with real exports
- [ ] Verify parser test coverage (expand if needed)

#### 4. Quality Metrics (Priority 4)
- [ ] Run pytest with coverage reporting
- [ ] Achieve >80% code coverage
- [ ] Document test strategy in TESTING.md
- [ ] Set up CI/CD pipeline (GitHub Actions)

**Success Criteria:**
- ✅ All 6 dimensions have comprehensive test suites
- ✅ Test coverage >80%
- ✅ All tests pass
- ✅ CI/CD pipeline green
- ✅ Ready for external users

**Estimated Effort:**
- Dimension tests: ~5-7 days (5 files × 300-400 lines)
- Feature tests: ~2-3 days (2 files × 200-300 lines)
- Module verification: ~2-3 days
- CI/CD setup: ~1 day
- **Total: 10-14 days**

---

### 🟡 Phase 3.6 - Documentation & Examples

**Goal:** Make documentation consistent, accurate, and user-friendly.

**Status:** Planned, not started

**Timeline:** 2-3 days (after Phase 3.5)

**Tasks:**

#### 1. Fix Documentation Inconsistencies (Priority 1)
- [ ] Update README.md status section (lines 155-195)
  - Mark all 6 dimensions as complete (not "in progress")
  - Update project structure annotations (lines 123-153)
  - Add reference to ROADMAP.md and PROJECT_STATUS.md
- [ ] Verify all version numbers are consistent (0.2.0)
- [ ] Remove outdated TODO/pending markers

#### 2. Create User Guides (Priority 2)
- [ ] **GETTING_STARTED.md** - 10-minute quickstart guide
- [ ] **INTERPRETATION.md** - What do the scores mean?
- [ ] **BEST_PRACTICES.md** - Research methodology recommendations
- [ ] **CONTRIBUTING.md** - Community contribution guidelines

#### 3. Expand Examples (Priority 3)
- [ ] `examples/analyze_all_dimensions.py` - Multi-dimension analysis
- [ ] `examples/linguistic_convergence_example.py` - LC-specific
- [ ] `examples/autonomy_erosion_example.py` - AE-specific
- [ ] `examples/reality_coherence_example.py` - RCD-specific
- [ ] `examples/dependency_formation_example.py` - DF-specific
- [ ] `examples/batch_analysis.py` - Analyze multiple exports
- [ ] `examples/longitudinal_study.py` - Time-series analysis

**Success Criteria:**
- ✅ No contradictions across documentation files
- ✅ User can get started in <10 minutes
- ✅ Examples exist for all 6 dimensions
- ✅ Clear interpretation guidance for all indicators

**Estimated Effort:** 2-3 days

---

## Future Phases

### 🔵 Phase 4 - Enhancements & Visualization (v0.3.0)

**Goal:** Add production-ready features for researchers and tool builders.

**Status:** Planned

**Timeline:** 4-8 weeks (after Phase 3.5 & 3.6)

#### Priority 1 - Core Improvements

**1. Enhanced CLI**
- Progress bars for long-running analyses
- Verbose/quiet modes (`--verbose`, `--quiet`)
- Better error messages with suggestions
- Output validation and warnings
- Streaming output for large corpora

**2. Performance Optimization**
- Parallel processing for multi-conversation corpora
- Caching for expensive computations (pitch extraction, etc.)
- Streaming analysis for large files (>1GB)
- Memory profiling and optimization
- **Target:** Analyze 1,000 conversations in <2 minutes

**3. Visualization Module**
- Time-series plots for indicator trajectories
- Dimension comparison radar charts
- Conversation-level heatmaps
- Export to PNG/SVG/PDF
- Optional interactive plots (plotly)

#### Priority 2 - Advanced Features

**4. Voice Activity Detection (VAD)**
- Detect speech vs silence in audio
- Improve speech rate accuracy
- Better pause structure analysis
- Turn-taking analysis

**5. Batch Processing Tools**
- Analyze multiple exports at once
- Aggregate statistics across users (privacy-preserving)
- Comparative analysis (user A vs user B vs baseline)
- Export comparative reports

**6. Statistical Analysis**
- Confidence intervals for all indicators
- Significance testing vs baselines
- Effect size calculations
- Longitudinal trend detection (Mann-Kendall test)

#### Priority 3 - Optional Integrations

**7. Hume Expression API** (optional, paid)
- Emotional expression analysis in voice
- Enhanced PE dimension with emotion data
- Vocal arousal tracking
- Optional dependency (`entrain[hume]`)

**8. Enhanced Baselines**
- Age-stratified baselines
- Culture-specific baselines
- Domain-specific baselines (therapy, education, etc.)
- Baseline data repository

**Out of Scope for Phase 4:**
- Real-time monitoring systems → Phase 5
- Cloud hosting/SaaS → Against privacy-first principle
- Production browser extensions → Third-party responsibility
- Web dashboard → Phase 5 (maybe)

**Success Criteria:**
- ✅ CLI has progress tracking and better UX
- ✅ 1,000 conversations analyzed in <2 minutes
- ✅ Beautiful, publication-ready visualizations
- ✅ VAD improves audio analysis accuracy by >15%
- ✅ Batch analysis supports multi-user studies
- ✅ >85% test coverage maintained

**Estimated Effort:** 4-8 weeks

---

### 🔵 Phase 5 - Ecosystem & Integration (v0.4.0)

**Goal:** Enable third-party tools, extensions, and research applications.

**Status:** Exploratory

**Timeline:** TBD (6+ months out)

**Potential Features:**
- REST API server (local-only)
- Real-time streaming analysis (websocket)
- Browser extension SDK/integration points
- Plugin system for custom dimensions
- Jupyter notebook integration
- R package wrapper (`reticulate`)
- Web dashboard (local deployment only)

**Not Planned:**
- Cloud-hosted analysis (violates privacy-first)
- Centralized data collection (violates privacy-first)
- Production browser extensions (third-party responsibility)

---

## Key Milestones

| Milestone | Version | Target Date | Status |
|-----------|---------|-------------|--------|
| Phase 1 Complete | v0.1.0 | Jan 2026 | ✅ Done |
| Phase 2 Complete | v0.2.0 | Feb 2026 | ✅ Done |
| Phase 3 Complete | v0.2.0 | Feb 8, 2026 | ✅ Done |
| Phase 3.5 Complete | v0.2.1 | Feb 22, 2026 | 🔄 In planning |
| Phase 3.6 Complete | v0.2.2 | Mar 1, 2026 | ⏳ Planned |
| Phase 4 Complete | v0.3.0 | Apr-May 2026 | ⏳ Planned |
| Phase 5 Exploration | v0.4.0 | Q3 2026 | 💭 Exploratory |

---

## Metrics & Goals

| Metric | v0.2.0 (Current) | v0.2.1 (Phase 3.5) | v0.3.0 (Phase 4) |
|--------|------------------|-------------------|------------------|
| **Test Coverage** | ~15% | **>80%** | >85% |
| **Tested Dimensions** | 1/6 (17%) | **6/6 (100%)** | 6/6 (100%) |
| **Example Coverage** | 2/6 dimensions | **6/6 dimensions** | 6/6 + workflows |
| **Documentation Quality** | Good | **Excellent** | Excellent |
| **Platform Support** | 4 platforms | 4 platforms | 4+ platforms |
| **Performance (1k convos)** | Untested | <5 min | **<2 min** |
| **Visualizations** | None | None | **Production-ready** |
| **CI/CD** | None | **GitHub Actions** | GitHub Actions |

---

## Open Questions

### For Phase 3.5
1. **Testing Strategy:** Unit tests only, or integration + unit?
2. **Coverage Target:** 80% or 90%?
3. **CI/CD:** GitHub Actions or other?

### For Phase 4
1. **Visualization:** Matplotlib, plotly, or both?
2. **Hume Integration:** Worth the complexity of paid API?
3. **Performance:** Async, multiprocessing, or both?
4. **Release Timing:** One big v0.3.0 or incremental v0.2.x releases?

### For Phase 5
1. **Web Dashboard:** Is this within scope? Or third-party only?
2. **Real-time Analysis:** Demand vs complexity tradeoff?
3. **Plugin System:** Too early or worth planning now?

---

## Decision Log

### February 8, 2026
- ✅ **Decision:** Pause new features, prioritize quality (Phase 3.5)
- ✅ **Rationale:** 5/6 analyzers untested is unacceptable for v0.2.0 release
- ✅ **Action:** Create PROJECT_STATUS.md and ROADMAP.md for clarity

### January 2026
- ✅ **Decision:** Implement all 6 dimensions in Phase 1, not incrementally
- ✅ **Rationale:** Core value is comprehensive framework analysis
- ✅ **Decision:** PE dimension deferred to Phase 3 (audio required)
- ✅ **Rationale:** Audio infrastructure not yet built

---

## How to Use This Roadmap

**For Contributors:**
- Check current phase to see what's being worked on
- See "Open Questions" for areas needing input
- Refer to PROJECT_STATUS.md for detailed task list

**For Users:**
- Check "Completed Phases" to see what works now
- Check "Current Phase" to see what's coming soon
- Check "Metrics & Goals" to see quality trajectory

**For Stakeholders:**
- Check "Key Milestones" for timeline
- Check "Metrics & Goals" for measurable progress
- Check "Decision Log" for strategic choices

---

## Contributing

See CONTRIBUTING.md (to be created in Phase 3.6) for:
- How to propose new features
- How to report bugs
- How to contribute code
- Research contribution guidelines

---

**Next Review Date:** February 22, 2026 (after Phase 3.5)
