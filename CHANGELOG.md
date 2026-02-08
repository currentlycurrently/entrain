# Changelog

All notable changes to the Entrain Reference Library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [Unreleased] - Phase 3 Roadmap

### Planned

- Audio feature extraction (openSMILE integration)
- PE (Prosodic Entrainment) dimension analyzer
- Voice interaction analysis capabilities
- Hume Expression Measurement API integration (optional)
- Voice-specific baselines and validation
- Multimodal analysis (text + voice)

---

[0.1.0]: https://github.com/entrain-institute/entrain/releases/tag/v0.1.0
