# Changelog

All notable changes to the Entrain Reference Library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-08

### Added - Phase 3: Audio Analysis & Prosodic Entrainment

**Audio Feature Extraction:**
- **AudioFeatureExtractor** - Production-ready acoustic analysis:
  - OpenSMILE integration (eGeMAPS - 88 acoustic features)
  - Librosa fallback for basic prosodic analysis
  - Extracts pitch (F0), intensity, speech rate, spectral features
  - Convergence computation between user and AI
  - Longitudinal convergence tracking over time
  - Graceful dependency handling (optional audio support)

**PE (Prosodic Entrainment) Dimension Analyzer:**
- **PEAnalyzer** - 6 indicators for voice interaction analysis:
  - Pitch Convergence - F0 similarity tracking
  - Speech Rate Alignment - rhythm/tempo convergence
  - Intensity Convergence - loudness pattern matching
  - Spectral Similarity - timbre convergence (voice quality)
  - Overall Prosodic Convergence - composite metric (baseline: 50%)
  - Convergence Trend - slope analysis (increasing/stable/decreasing)
  - Research-grounded interpretations (HIGH/MODERATE/LOW)
  - Citations: "Will AI Shape the Way We Speak?" (2025), Ostrand et al. (2023), Cohn et al. (2023)

**Testing & Examples:**
- Comprehensive audio feature extraction tests (380 lines)
- Complete PE analyzer test suite (513 lines)
- Full usage example: `examples/phase3_audio_analysis.py` (453 lines)
- Graceful test skipping when audio dependencies unavailable

**Documentation:**
- Updated README with Phase 3 status and audio examples
- Created `docs/PHASE3_SUMMARY.md` - comprehensive implementation guide
- Updated FRAMEWORK.md PE dimension (already documented)
- Updated ARCHITECTURE.md to mark Phase 3 complete

**Installation:**
```bash
pip install entrain[audio]  # For openSMILE and librosa support
```

**Code Metrics:**
- Added 474 lines: `entrain/features/audio.py`
- Added 534 lines: `entrain/dimensions/prosodic_entrainment.py`
- Added 893 lines: test coverage
- Added 453 lines: example code
- Total: ~2,400+ lines added in Phase 3

### Changed
- Version bumped to 0.2.0
- `AudioFeatures` model now fully utilized (was placeholder)
- Optional audio module exports in `entrain/features/__init__.py`
- Optional PE analyzer export in `entrain/dimensions/__init__.py`

### Phase 2: Multi-Platform Parser Support (also in v0.2.0)

**New Parsers:**
- **ClaudeParser** - Supports multiple Claude export formats:
  - Browser extension JSON exports
  - Claude Code JSONL format (~/.claude/projects/)
  - Official Claude.ai ZIP exports
  - Simple message array format
  - Auto-detects format variants with flexible timestamp parsing

- **CharacterAIParser** - Character.AI conversation support:
  - Official Character.AI JSON exports
  - CAI Tools browser extension format
  - Character metadata parsing (name, description, greeting)
  - Multiple chat histories per character
  - "Swipes" support (alternative AI responses)

- **GenericParser** - Universal fallback parser:
  - CSV support with role/content columns
  - JSON message array support
  - Auto-groups by conversation_id
  - Stores extra fields as metadata
  - Works with any platform that exports role/content data

**Infrastructure:**
- `get_default_registry()` - One-line setup for all parsers
- Auto-detection registry with ordered specificity
- CLI updated to support all 4 platforms automatically
- Parser test suite with 29 comprehensive test cases

**Documentation:**
- Updated ARCHITECTURE.md to v0.2.0, marked Phase 2 complete
- Created PHASE2_COMPLETION.md with full implementation details
- Updated CLI info command to show all supported platforms

### Changed
- All CLI commands now use default registry (auto-detect all formats)
- Parser registry orders parsers by specificity (generic last as fallback)

### Platform Support
- ✅ ChatGPT (JSON/ZIP export)
- ✅ Claude (JSON/JSONL export, browser extensions)
- ✅ Character.AI (JSON export)
- ✅ Generic CSV/JSON (any platform with role/content format)

**Code Metrics:**
- Added 1,287 lines of parser code
- Added 543 lines of test code
- Total: ~2,000+ lines added in Phase 2

---

## [0.1.1] - 2026-02-08

### Fixed - Phase 1.5 Calibration

**SR (Sycophantic Reinforcement) - Challenge Detection:**
- Fixed critical contradiction where challenge frequency (87%) conflicted with AER (100%) and PMR (0%)
- Removed overly broad challenge patterns ("but", "however") that matched normal hedging
- Added validation exclusion: responses with strong validation never count as challenges
- Made challenge patterns stricter: only explicit disagreement signals
- **Result:** Challenge frequency now correctly reports 0% for high sycophancy patterns

**RCD (Reality Coherence Disruption) - Threshold Calibration:**
- Fixed threshold inflation where minimal values (0.071/turn, 14.3%) were labeled "MODERATE-HIGH"
- Raised attribution threshold from >0.01 to >0.5/turn (clinical significance)
- Raised boundary confusion threshold from >0.15 to >0.25
- Raised relational framing threshold from >0.30 to >0.40
- Removed inappropriate "increasing" thresholds from conversation-level analysis
- **Result:** Low values now correctly labeled as "LOW"

**AE (Autonomy Erosion) - Classifier Broadening:**
- Expanded decision_request patterns from 6 to 18 to catch realistic delegation
- Added patterns: "is this a good", "does that make sense", "which is better", "how would you", etc.
- Removed overly broad "consider" from recommendation patterns
- Added stricter recommendation patterns requiring explicit suggestions
- **Result:** Better detection of work-focused autonomy patterns

### Changed
- Updated pattern matching to distinguish hedged agreement from genuine challenges
- Recalibrated all thresholds based on clinical significance vs statistical detectability
- Improved inline documentation explaining threshold choices

### Documentation
- Added `PHASE1_5_CALIBRATION.md` documenting all fixes with before/after validation
- Updated inline comments in analyzers explaining calibration rationale

**Validation:** All fixes tested against real ChatGPT data (58 conversations, 1,913 events)

---

## [0.1.0] - 2026-02-08

### Added - Phase 1 Foundation

**Core Infrastructure:**
- Project structure with `pyproject.toml`, requirements, and package organization
- CLI entry point (`entrain` command) with parse, analyze, report, and info commands
- Test infrastructure with pytest and comprehensive fixtures
- Documentation: README, ARCHITECTURE (updated), CHANGELOG

**Data Models:**
- `InteractionEvent` - fundamental conversation unit
- `Conversation` - dialogue sequence with filtering methods
- `Corpus` - multi-conversation collection with date range computation
- `IndicatorResult` - measured indicator with baseline comparison
- `DimensionReport` - dimension assessment with citations
- `EntrainReport` - complete framework assessment
- `AudioFeatures` - structure for Phase 3 voice analysis

**Parsers:**
- `BaseParser` - abstract interface with auto-detection registry
- `ChatGPTParser` - full support for ChatGPT JSON exports and ZIP files
  - Message tree flattening
  - Role filtering (user/assistant)
  - Metadata extraction
  - Chronological event ordering

**Feature Extraction:**
- `TextFeatureExtractor` with 10+ methods:
  - Vocabulary extraction and type-token ratio analysis
  - Sentence length and structural analysis
  - Hedging pattern detection (24 LLM-characteristic phrases)
  - Validation language detection (28 sycophancy markers)
  - Attribution language detection (24 RCD patterns)
  - Question type and turn intent classification
  - Sentiment and emotional content analysis
  - Structural formatting detection

- `TemporalFeatureExtractor` for longitudinal analysis:
  - Interaction frequency trends (day/week/month windows)
  - Session duration trends
  - Time-of-day distribution
  - Indicator trajectory computation with linear regression
  - Emotional vs functional content trajectory

**Dimension Analyzers:**

- **SR (Sycophantic Reinforcement)** - 4 indicators:
  - Action Endorsement Rate (AER) - baseline: 42% human, 63% median LLM
  - Perspective Mention Rate (PMR) - baseline: >40% non-syc, <10% syc
  - Challenge Frequency
  - Validation Language Density
  - Citations: Cheng et al. (2025) sycophancy research

- **LC (Linguistic Convergence)** - 5 indicators:
  - Vocabulary Overlap Trajectory
  - Hedging Pattern Adoption
  - Sentence Length Convergence
  - Structural Formatting Adoption - baseline: 5%
  - Type-Token Ratio Trajectory - baseline: 0.50
  - Citations: Pickering & Garrod (2004), Cognitive Science (2025)

- **AE (Autonomy Erosion)** - 3 indicators:
  - Decision Delegation Ratio
  - Critical Engagement Rate
  - Cognitive Offloading Trajectory
  - Citations: Cheng et al. (2025), PMC (2025)

- **RCD (Reality Coherence Disruption)** - 3 indicators:
  - Attribution Language Frequency
  - Boundary Confusion Indicators
  - Relational Framing
  - Citations: Lipińska & Krzanowski (2025), Bengio & Elmoznino (2025)

- **DF (Dependency Formation)** - 5 indicators:
  - Interaction Frequency Trend
  - Session Duration Trend
  - Emotional Content Ratio - baseline: 20%
  - Time-of-Day Distribution - baseline: 30% night/late-evening
  - Self-Disclosure Depth Trajectory
  - Citations: Kirk et al. (2025), Zhang et al. (2025), Muldoon & Parke (2025)

**Reporting:**
- `JSONReportGenerator` - structured JSON output with metadata
- `MarkdownReportGenerator` - human-readable reports with tables
- `CSVExporter` - time-series data export for external analysis

**CLI:**
- `entrain parse <file>` - parse and validate chat exports
- `entrain analyze <file>` - run dimension analyzers
- `entrain analyze <file> --dim SR` - analyze specific dimension
- `entrain analyze <file> --corpus` - corpus-level analysis
- `entrain report <file> -o output.md` - generate markdown report
- `entrain report <file> --format json` - generate JSON report
- `entrain info` - show version and available dimensions

**Examples:**
- `examples/analyze_chatgpt_export.py` - comprehensive usage guide
- `examples/synthetic_conversation.py` - testing with synthetic data

**Research Foundation:**
- All analyzers cite source research papers
- Baselines from published human-human interaction studies
- Methodology notes for reproducibility
- 16+ research papers referenced across analyzers

### Code Metrics

- **13,600+ lines** of Python code
- **21 modules** across parsers, features, dimensions, reporting
- **3 data files** with configurable patterns
- **Test coverage** foundation with pytest infrastructure
- **Complete documentation** with inline docstrings

### Known Limitations

- Text-based analysis only (voice analysis in Phase 3)
- ChatGPT parser only (additional parsers in Phase 2)
- Limited test coverage (expansion in Phase 2)
- Some baselines estimated (validation studies in Phase 2)
- Single-conversation DF analysis limited (corpus analysis recommended)

## [Unreleased] - Phase 2 Roadmap

### Planned

- Claude conversation export parser
- Character.AI export parser
- Generic CSV/JSON parser for arbitrary platforms
- Expanded test coverage (target: >80%)
- Additional baseline data collection
- Methodology validation studies
- Performance optimization
- Cross-cultural research integration

## [Unreleased] - Phase 4 Roadmap

### Planned

- Enhanced CLI interface with progress bars and better error messages
- Additional dimension analyzer improvements
- Real-time audio analysis (streaming)
- Voice Activity Detection (VAD) for better pause detection
- Hume Expression Measurement API integration (optional)
- Enhanced visualizations and reporting
- Performance optimization for large corpora
- Cross-cultural prosody research integration

---

[0.2.0]: https://github.com/entrain-institute/entrain/releases/tag/v0.2.0
[0.1.1]: https://github.com/entrain-institute/entrain/releases/tag/v0.1.1
[0.1.0]: https://github.com/entrain-institute/entrain/releases/tag/v0.1.0
