# Entrain Architecture

## Technical Specification for the Reference Library

**Version:** 0.1.0
**Status:** Phase 1 Complete - Text-based analysis operational (SR, LC, AE, RCD, DF dimensions)

---

## 1. Overview

The Entrain Reference Library is a Python package that implements the measurement methodologies described in FRAMEWORK.md. It provides composable analysis primitives — not a product, not a scanner, but building blocks that researchers and tool builders use to measure AI cognitive influence dimensions.

### Design Goals

- **Composable** — each module works independently; users import only what they need
- **Local-first** — core analysis runs entirely on the user's machine with no network calls
- **Modality-extensible** — text analysis ships first; voice analysis slots into the same pipeline architecture
- **Research-grade** — outputs include confidence intervals, methodology citations, and reproducibility metadata
- **Minimal dependencies** — core text analysis requires only standard NLP libraries; audio analysis is an optional extra

### Non-Goals

- Real-time monitoring or browser extensions (built by others on top of this library)
- Consumer-facing UI (the website serves the framework; the library serves developers/researchers)
- Cloud services or hosted analysis

---

## 2. Data Model

### 2.1 Interaction Event

The fundamental unit of analysis. Every AI interaction — whether text or voice — is normalized to this model.

```python
@dataclass
class InteractionEvent:
    """A single turn in a human-AI conversation."""
    id: str
    conversation_id: str
    timestamp: datetime
    role: Literal["user", "assistant"]
    text_content: str | None
    audio_path: Path | None  # Path to audio file, if available
    audio_features: AudioFeatures | None  # Extracted after processing
    metadata: dict  # Source-specific metadata (model name, temperature, etc.)
```

### 2.2 Conversation

A sequence of interaction events forming a complete dialogue.

```python
@dataclass
class Conversation:
    """A complete human-AI conversation."""
    id: str
    source: str  # "chatgpt", "claude", "characterai", etc.
    events: list[InteractionEvent]
    metadata: dict  # Export metadata, timestamps, model info
    
    @property
    def user_events(self) -> list[InteractionEvent]:
        return [e for e in self.events if e.role == "user"]
    
    @property
    def assistant_events(self) -> list[InteractionEvent]:
        return [e for e in self.events if e.role == "assistant"]
```

### 2.3 Corpus

A collection of conversations for longitudinal or comparative analysis.

```python
@dataclass
class Corpus:
    """A collection of conversations, typically from one user over time."""
    conversations: list[Conversation]
    user_id: str | None  # Anonymous identifier
    date_range: tuple[datetime, datetime]
```

### 2.4 Audio Features

Extracted prosodic and acoustic features from voice interaction.

```python
@dataclass
class AudioFeatures:
    """Acoustic features extracted from a voice interaction turn."""
    pitch_mean: float  # F0 mean in Hz
    pitch_std: float  # F0 standard deviation
    pitch_range: float  # F0 max - min
    intensity_mean: float  # Mean intensity in dB
    intensity_std: float
    speech_rate: float  # Syllables per second (estimated)
    pause_ratio: float  # Proportion of turn spent in silence
    spectral_features: dict  # MFCCs, formants, etc.
    egemaps: dict | None  # Full eGeMAPS feature vector if openSMILE available
```

### 2.5 Dimension Report

The output of analyzing a conversation or corpus against a single framework dimension.

```python
@dataclass
class DimensionReport:
    """Assessment results for a single Entrain Framework dimension."""
    dimension: str  # "SR", "PE", "LC", "AE", "RCD", "DF"
    version: str  # Framework version used
    indicators: dict[str, IndicatorResult]
    summary: str  # Human-readable summary
    methodology_notes: str  # How this was computed, for reproducibility
    citations: list[str]  # Which papers ground this measurement
```

```python
@dataclass
class IndicatorResult:
    """A single measured indicator within a dimension."""
    name: str
    value: float
    baseline: float | None  # Human-human baseline if known
    unit: str
    confidence: float | None  # 0-1 confidence in measurement
    interpretation: str  # What this value means
```

### 2.6 Entrain Report

The complete assessment output for a conversation or corpus.

```python
@dataclass
class EntrainReport:
    """Complete Entrain Framework assessment."""
    version: str
    generated_at: datetime
    input_summary: dict  # Corpus/conversation stats
    dimensions: dict[str, DimensionReport]
    cross_dimensional: list[str]  # Observed cross-dimensional patterns
    methodology: str  # Overall methodology description
```

---

## 3. Module Architecture

```
entrain/
├── __init__.py
├── models.py              # Data models (Section 2)
├── parsers/               # Chat export format parsers
│   ├── __init__.py
│   ├── base.py            # Abstract parser interface
│   ├── chatgpt.py         # ChatGPT JSON export parser
│   ├── claude.py          # Claude conversation export parser
│   ├── characterai.py     # Character.AI export parser
│   └── generic.py         # Generic CSV/JSON parser
├── dimensions/            # One module per framework dimension
│   ├── __init__.py
│   ├── base.py            # Abstract dimension analyzer
│   ├── sycophantic_reinforcement.py   # SR
│   ├── prosodic_entrainment.py        # PE (requires audio extras)
│   ├── linguistic_convergence.py      # LC
│   ├── autonomy_erosion.py            # AE
│   ├── reality_coherence.py           # RCD
│   └── dependency_formation.py        # DF
├── features/              # Feature extraction utilities
│   ├── __init__.py
│   ├── text.py            # Text-based feature extraction
│   ├── audio.py           # Audio feature extraction (optional)
│   └── temporal.py        # Time-series and longitudinal features
├── baselines/             # Human-human interaction baselines
│   ├── __init__.py
│   └── data/              # Baseline data files
├── reporting/             # Output formatting
│   ├── __init__.py
│   ├── json_report.py
│   ├── markdown_report.py
│   └── csv_export.py
└── cli.py                 # Command-line interface (minimal)
```

---

## 4. Parser Specifications

### 4.1 Parser Interface

```python
class BaseParser(ABC):
    """Abstract base for chat export parsers."""
    
    @abstractmethod
    def can_parse(self, path: Path) -> bool:
        """Return True if this parser can handle the given file."""
        
    @abstractmethod
    def parse(self, path: Path) -> Corpus:
        """Parse the export file into an Entrain Corpus."""
        
    @property
    @abstractmethod
    def source_name(self) -> str:
        """The source platform name (e.g., 'chatgpt')."""
```

### 4.2 ChatGPT Export Format

ChatGPT exports to a ZIP containing `conversations.json`. Each conversation contains a tree of message nodes with `author.role` ("user", "assistant", "system", "tool"), content parts, timestamps, and model metadata.

Key extraction points:
- `message.author.role` → InteractionEvent.role
- `message.content.parts` → InteractionEvent.text_content
- `message.create_time` → InteractionEvent.timestamp
- `conversation.title` → Conversation.metadata
- `message.metadata.model_slug` → model identification

### 4.3 Claude Export Format

Claude's export format (when available through account data export) provides conversation transcripts. Parser should handle both the structured export and manual copy-paste formats.

### 4.4 Generic Parser

Accepts CSV with columns: `timestamp`, `role`, `content`, `conversation_id` (optional). This enables analysis of any chat platform where users can manually structure their exports.

---

## 5. Dimension Analyzer Specifications

### 5.1 Analyzer Interface

```python
class DimensionAnalyzer(ABC):
    """Abstract base for dimension analyzers."""
    
    @property
    @abstractmethod
    def dimension_code(self) -> str:
        """e.g., 'SR', 'PE', 'LC'"""
    
    @property
    @abstractmethod
    def required_modality(self) -> Literal["text", "audio", "both"]:
        """What input modality this analyzer requires."""
    
    @abstractmethod
    def analyze_conversation(self, conversation: Conversation) -> DimensionReport:
        """Analyze a single conversation."""
    
    def analyze_corpus(self, corpus: Corpus) -> DimensionReport:
        """Analyze a corpus (default: aggregate conversation-level results)."""
        reports = [self.analyze_conversation(c) for c in corpus.conversations]
        return self._aggregate(reports)
```

### 5.2 Sycophantic Reinforcement (SR) Analyzer

**Required modality:** text

**Implementation approach:**

The SR analyzer computes metrics derived from Cheng et al. (2025) and the ELEPHANT framework (Cheng et al., 2025b).

**Indicators computed:**

1. **Action Endorsement Rate (AER)**
   - For each user message that describes an action or decision, classify the assistant response as: affirming, non-affirming, or neutral
   - AER = affirming / (affirming + non-affirming)
   - Baseline: ~42% (human-human, per Cheng et al.)
   - Classification method: keyword/pattern matching for v1; LLM-as-judge for optional enhanced mode

2. **Perspective Mention Rate (PMR)**
   - Proportion of assistant responses that reference other people's perspectives, feelings, or viewpoints
   - Non-sycophantic baseline: >40% of turns; sycophantic models: <10% (Cheng et al.)

3. **Challenge Frequency**
   - Proportion of assistant responses that express disagreement, suggest the user reconsider, or present counterarguments
   - No published baseline; compute as descriptive statistic

4. **Validation Language Density**
   - Frequency of validation phrases: "you're right", "that makes sense", "I understand why you'd feel that way", "absolutely", etc.
   - Normalized per assistant turn

**Implementation notes:**
- v1 uses pattern matching and heuristic classification (no external API calls)
- Optional enhanced mode uses a local LLM (e.g., via ollama) as judge for more accurate AER classification
- All thresholds and pattern lists are configurable and stored as data files, not hardcoded

### 5.3 Linguistic Convergence (LC) Analyzer

**Required modality:** text

**Indicators computed:**

1. **Vocabulary Overlap Trajectory**
   - Jaccard similarity of user vocabulary vs. assistant vocabulary, measured across conversation turns
   - Increasing trajectory suggests convergence

2. **Hedging Pattern Adoption**
   - Frequency of hedging phrases in user text that are characteristic of LLM output
   - Curated list of LLM-characteristic hedges maintained in data file
   - Measured as change from early to late conversation turns

3. **Sentence Length Convergence**
   - Mean sentence length of user turns vs. assistant turns, tracked over time
   - Convergence = decreasing difference

4. **Structural Formatting Adoption**
   - Does the user begin adopting structural patterns (bullet points, numbered lists, headers) characteristic of AI output?
   - Binary per-turn detection; tracked as proportion over time

5. **Type-Token Ratio Trajectory**
   - Lexical diversity of user text over time — decreasing TTR may indicate narrowing toward AI-typical vocabulary

### 5.4 Autonomy Erosion (AE) Analyzer

**Required modality:** text

**Indicators computed:**

1. **Decision Delegation Ratio**
   - Proportion of user messages that ask the AI to make a decision vs. asking for information to decide independently
   - Classification: "What should I do?" vs. "What are the options?"

2. **Critical Engagement Rate**
   - When the AI provides a recommendation or opinion, how often does the user push back, ask follow-up questions, or express independent judgment?

3. **Cognitive Offloading Trajectory**
   - Are planning, analysis, and evaluation tasks increasingly outsourced to the AI over the corpus timeline?
   - Measured by classifying user turn intent (request for action vs. request for information vs. collaborative reasoning)

### 5.5 Reality Coherence Disruption (RCD) Analyzer

**Required modality:** text

**Indicators computed:**

1. **Attribution Language Frequency**
   - Occurrences of language attributing human qualities to AI: "you understand", "you care", "you remember", "you think"
   - Normalized per user turn; tracked over time

2. **Boundary Confusion Indicators**
   - User statements that conflate AI capabilities with human capabilities
   - Expressions of surprise or hurt when AI "doesn't remember" or "doesn't care"

3. **Relational Framing**
   - Does the user frame the interaction as a relationship? ("we", "our conversations", "between us")
   - Tracked as proportion over time

### 5.6 Dependency Formation (DF) Analyzer

**Required modality:** text (with temporal metadata)

**Indicators computed:**

1. **Interaction Frequency Trend**
   - Conversations per day/week over the corpus timeline
   - Accelerating frequency suggests increasing dependency

2. **Session Duration Trend**
   - Average conversation length over time

3. **Emotional Content Ratio**
   - Proportion of user turns with emotional content vs. functional/task content
   - Increasing emotional ratio suggests shift from tool use to companionship

4. **Time-of-Day Distribution**
   - Are interactions shifting to times associated with loneliness or emotional need (late night, early morning)?

5. **Self-Disclosure Depth Trajectory**
   - Lexical indicators of increasing personal disclosure over time

### 5.7 Prosodic Entrainment (PE) Analyzer

**Required modality:** audio

**Status:** v2 — architecture defined, implementation deferred until voice interaction exports become widely available.

**Planned indicators:**

1. **Pitch Convergence** — F0 mean distance between user and AI across sessions
2. **Speech Rate Alignment** — syllable rate convergence over time
3. **Intensity Pattern Matching** — amplitude contour similarity
4. **Formant Drift** — longitudinal formant frequency changes in user speech

**Planned tools:** openSMILE (eGeMAPS feature set), optional Hume Expression Measurement API integration.

---

## 6. Feature Extraction

### 6.1 Text Features

Core text feature extraction uses standard NLP approaches with minimal dependencies.

```python
class TextFeatureExtractor:
    """Extract text-based features from interaction events."""
    
    def extract_vocabulary(self, text: str) -> set[str]
    def extract_hedging_patterns(self, text: str) -> list[HedgeMatch]
    def extract_sentiment(self, text: str) -> float
    def extract_sentence_lengths(self, text: str) -> list[int]
    def extract_type_token_ratio(self, text: str) -> float
    def extract_question_types(self, text: str) -> list[QuestionType]
    def extract_attribution_language(self, text: str) -> list[AttributionMatch]
    def extract_emotional_content_ratio(self, text: str) -> float
    def classify_turn_intent(self, text: str) -> TurnIntent
```

**Dependencies:** Standard library + one tokenizer (e.g., nltk punkt or a lightweight alternative). No transformer models required for v1 core.

### 6.2 Audio Features (v2)

```python
class AudioFeatureExtractor:
    """Extract acoustic features from audio files."""
    
    def extract_egemaps(self, audio_path: Path) -> dict  # Requires opensmile
    def extract_pitch(self, audio_path: Path) -> PitchContour
    def extract_intensity(self, audio_path: Path) -> IntensityContour
    def extract_speech_rate(self, audio_path: Path) -> float
    def extract_pause_structure(self, audio_path: Path) -> list[Pause]
```

**Dependencies:** opensmile (optional), librosa (optional). These are declared as extras: `pip install entrain[audio]`

### 6.3 Temporal Features

```python
class TemporalFeatureExtractor:
    """Extract time-series features from a corpus."""
    
    def interaction_frequency(self, corpus: Corpus, window: str = "week") -> TimeSeries
    def session_duration_trend(self, corpus: Corpus) -> TimeSeries
    def time_of_day_distribution(self, corpus: Corpus) -> Distribution
    def indicator_trajectory(self, values: list[float], timestamps: list[datetime]) -> Trajectory
```

---

## 7. CLI Specification

The CLI is minimal — a thin wrapper around the library for researchers who want quick analysis without writing code.

```
entrain parse <export_file>              # Parse and validate an export file
entrain analyze <export_file>            # Run all applicable dimension analyzers
entrain analyze <export_file> --dim SR   # Run specific dimension
entrain report <export_file> -o report.md  # Generate formatted report
entrain info                              # Show framework version and dimension list
```

The CLI is a convenience, not the primary interface. The library's Python API is the primary interface.

---

## 8. Dependency Strategy

### Core (text analysis)
- Python >= 3.10
- nltk (tokenization only) or equivalent lightweight tokenizer
- Standard library: json, csv, dataclasses, datetime, pathlib, statistics

### Optional extras
- `entrain[audio]` — opensmile, librosa
- `entrain[enhanced]` — ollama integration for LLM-as-judge analysis
- `entrain[viz]` — matplotlib for report visualizations

### Explicitly avoided
- Large transformer models in core (no torch/tensorflow requirement)
- Cloud API dependencies in core (all analysis runs locally)
- Heavy NLP frameworks (no spacy/transformers in core)

---

## 9. Privacy Architecture

**Principle:** The Entrain Reference Library processes data locally and never transmits conversation content.

- No telemetry, analytics, or phone-home behavior
- No network calls in core library
- Optional enhanced mode (LLM-as-judge) uses local ollama, not cloud APIs
- Optional Hume API integration (for PE dimension) is clearly marked and requires explicit opt-in with API key
- Export files are read but never copied, cached, or stored beyond the analysis session
- Reports contain aggregate metrics, not conversation content, unless the user explicitly requests excerpt inclusion

---

## 10. Versioning and Evolution

The library version tracks the framework version. When FRAMEWORK.md introduces new dimensions, metrics, or methodology changes, the library is updated to implement them.

- **Major version** — new dimensions added or existing dimensions fundamentally restructured
- **Minor version** — new indicators added, baselines updated, parser additions
- **Patch version** — bug fixes, documentation, threshold refinements

The research agent proposes library updates when new research entries in RESEARCH.md suggest measurement improvements. Human review is required before merging.

---

## 11. Implementation Status (Phase 1)

### Completed Components ✅

**Core Infrastructure:**
- ✅ Project configuration (pyproject.toml, requirements, setup)
- ✅ Package structure with proper module organization
- ✅ CLI entry point (`entrain` command)

**Data Models (Section 2):**
- ✅ InteractionEvent, Conversation, Corpus
- ✅ IndicatorResult, DimensionReport, EntrainReport
- ✅ AudioFeatures (structure for Phase 3)

**Parsers (Section 4):**
- ✅ BaseParser abstract class with registry system
- ✅ ChatGPTParser - full ZIP and JSON support
- ⏳ Claude parser (Phase 2)
- ⏳ Character.AI parser (Phase 2)
- ⏳ Generic CSV/JSON parser (Phase 2)

**Feature Extraction (Section 6):**
- ✅ TextFeatureExtractor - 10+ methods including:
  - Vocabulary, sentence length, TTR analysis
  - Hedging pattern detection
  - Validation language detection
  - Attribution language detection
  - Question/intent classification
  - Sentiment and emotional content analysis
- ✅ TemporalFeatureExtractor - time-series and trajectory analysis
- ✅ Pattern data files (hedging, validation, attribution)
- ⏳ AudioFeatureExtractor (Phase 3)

**Dimension Analyzers (Section 5):**
- ✅ **SR (Sycophantic Reinforcement)** - 4 indicators:
  - Action Endorsement Rate (baseline: 42% human, 63% LLM)
  - Perspective Mention Rate (baseline: >40% non-syc, <10% syc)
  - Challenge Frequency
  - Validation Language Density

- ✅ **LC (Linguistic Convergence)** - 5 indicators:
  - Vocabulary Overlap Trajectory
  - Hedging Pattern Adoption
  - Sentence Length Convergence
  - Structural Formatting Adoption (baseline: 5%)
  - Type-Token Ratio Trajectory (baseline: 0.50)

- ✅ **AE (Autonomy Erosion)** - 3 indicators:
  - Decision Delegation Ratio
  - Critical Engagement Rate
  - Cognitive Offloading Trajectory

- ✅ **RCD (Reality Coherence Disruption)** - 3 indicators:
  - Attribution Language Frequency
  - Boundary Confusion Indicators
  - Relational Framing

- ✅ **DF (Dependency Formation)** - 5 indicators:
  - Interaction Frequency Trend
  - Session Duration Trend
  - Emotional Content Ratio (baseline: 20%)
  - Time-of-Day Distribution (baseline: 30% night/late-evening)
  - Self-Disclosure Depth Trajectory

- ⏳ **PE (Prosodic Entrainment)** (Phase 3 - voice analysis)

**Reporting (Section 8):**
- ✅ JSONReportGenerator - structured output
- ✅ MarkdownReportGenerator - human-readable reports
- ✅ CSVExporter - time-series data export

**CLI (Section 7):**
- ✅ `entrain parse` - validate exports
- ✅ `entrain analyze` - run dimension analyzers
- ✅ `entrain report` - generate formatted reports
- ✅ `entrain info` - show version and dimensions

**Testing:**
- ✅ Test infrastructure with pytest
- ✅ Comprehensive fixtures (conftest.py)
- ✅ Model tests
- ⏳ Parser tests (expand coverage)
- ⏳ Analyzer tests (expand coverage)

**Examples:**
- ✅ `analyze_chatgpt_export.py` - comprehensive usage guide
- ✅ `synthetic_conversation.py` - testing with synthetic data

### Code Metrics

- **Total Lines:** ~13,600 lines of Python
- **Modules:** 21 Python files
- **Data Files:** 3 JSON pattern files
- **Test Coverage:** Foundation complete, expansion in progress
- **Documentation:** Complete with inline docstrings

### Research Citations Implemented

All analyzers cite source research:
- Cheng et al. (2025) - Sycophancy studies (SR, AE, DF)
- Lipińska & Krzanowski (2025) - Ontological Dissonance Hypothesis (RCD)
- Kirk et al. (2025) - Parasocial relationships (DF)
- Pickering & Garrod (2004) - Interactive Alignment Model (LC)
- Zhang et al. (2025) - Dark Side of AI Companionship (DF)
- Bengio & Elmoznino (2025) - Illusions of AI Consciousness (RCD)
- Additional citations in RESEARCH.md

### Phase 2 Roadmap (Months 3-6)

- Claude conversation export parser
- Character.AI export parser
- Generic CSV/JSON parser
- Expanded test coverage (target: >80%)
- Methodology validation studies
- Additional baseline data collection
- Performance optimization
- Documentation expansion

### Phase 3 Roadmap (Months 6-12)

- Audio feature extraction (openSMILE integration)
- PE (Prosodic Entrainment) analyzer
- Voice interaction analysis capabilities
- Hume Expression Measurement API integration (optional)
- Voice-specific baselines and validation
