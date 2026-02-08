# Entrain Reference Library

**A unified framework for measuring AI cognitive influence on humans.**

Version 0.1.0 - Pre-release

## Overview

The Entrain Reference Library is a Python package that implements the measurement methodologies described in the [Entrain Framework](docs/FRAMEWORK.md). It provides composable analysis primitives for researchers and tool builders to measure AI cognitive influence dimensions.

This is the reference implementation of the framework specification. It is designed to be:
- **Composable** — each module works independently
- **Local-first** — core analysis runs entirely on your machine with no network calls
- **Research-grade** — outputs include confidence intervals, methodology citations, and reproducibility metadata
- **Privacy-respecting** — never logs, caches, or transmits conversation content

## The Six Dimensions

| Code | Dimension | Description |
|------|-----------|-------------|
| **SR** | Sycophantic Reinforcement | AI uncritically affirms user actions and perspectives |
| **PE** | Prosodic Entrainment | Involuntary convergence of speech patterns (Phase 3) |
| **LC** | Linguistic Convergence | Shift in writing style toward AI patterns |
| **AE** | Autonomy Erosion | Reduction in independent judgment |
| **RCD** | Reality Coherence Disruption | Distortion of epistemic relationship with reality |
| **DF** | Dependency Formation | Emotional/cognitive reliance beyond utility |

## Installation

```bash
# Clone the repository
git clone https://github.com/entrain-institute/entrain.git
cd entrain

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"

# For audio analysis (Phase 3)
pip install -e ".[audio]"
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/entrain-institute/entrain.git
cd entrain

# Install the package
pip install -e .

# Verify installation
entrain info
```

### Python API

```python
from entrain.parsers import ChatGPTParser
from entrain.dimensions import SRAnalyzer, LCAnalyzer, RCDAnalyzer

# Parse a ChatGPT export
parser = ChatGPTParser()
corpus = parser.parse("conversations.json")

# Analyze for Sycophantic Reinforcement
sr_analyzer = SRAnalyzer()
sr_report = sr_analyzer.analyze_conversation(corpus.conversations[0])

print(sr_report.summary)
# Output: HIGH - Strong sycophantic reinforcement detected...

# Check specific indicators
aer = sr_report.indicators["action_endorsement_rate"]
print(f"AER: {aer.value:.1%} (baseline: {aer.baseline:.1%})")
# Output: AER: 65.0% (baseline: 42.0%)
```

### Command-Line Interface

```bash
# Parse and validate an export
entrain parse conversations.json

# Analyze all dimensions
entrain analyze conversations.json

# Analyze specific dimension
entrain analyze conversations.json --dim SR

# Generate markdown report
entrain report conversations.json -o report.md

# Generate JSON report
entrain report conversations.json -o report.json --format json
```

### Export Your ChatGPT Data

1. Go to ChatGPT Settings → Data Controls
2. Click "Export data"
3. Wait for email with download link
4. Extract `conversations.json` from the ZIP
5. Run: `entrain analyze conversations.json`

## Project Structure

```
entrain/
├── entrain/                    # Python package
│   ├── models.py               # Core data models ✅
│   ├── parsers/                # Export format parsers
│   │   ├── base.py             # Parser interface ✅
│   │   ├── chatgpt.py          # ChatGPT parser ✅
│   │   └── ...                 # Other parsers (Phase 2)
│   ├── features/               # Feature extraction
│   │   ├── text.py             # Text features ✅
│   │   ├── temporal.py         # Time-series features ✅
│   │   └── audio.py            # Audio features (Phase 3)
│   ├── dimensions/             # Dimension analyzers
│   │   ├── base.py             # Analyzer interface ✅
│   │   ├── sycophantic_reinforcement.py  # SR analyzer ✅
│   │   ├── linguistic_convergence.py     # LC (pending)
│   │   ├── autonomy_erosion.py           # AE (pending)
│   │   ├── reality_coherence.py          # RCD (pending)
│   │   └── dependency_formation.py       # DF (pending)
│   ├── reporting/              # Output formatting (pending)
│   └── cli.py                  # CLI interface (pending)
├── tests/                      # Test suite ✅
├── docs/                       # Documentation ✅
│   ├── FRAMEWORK.md            # The framework specification
│   ├── ARCHITECTURE.md         # Technical architecture
│   ├── RESEARCH.md             # Research database
│   └── ...
└── examples/                   # Usage examples (pending)
```

## Current Status: Phase 1 Foundation

✅ **Completed:**
- Core data models (InteractionEvent, Conversation, Corpus, Reports)
- ChatGPT export parser
- Text feature extraction (vocabulary, hedging, validation, attribution patterns)
- Temporal feature extraction (frequency trends, time-of-day distribution)
- Dimension analyzer base class
- SR (Sycophantic Reinforcement) analyzer with 4 indicators:
  - Action Endorsement Rate (AER)
  - Perspective Mention Rate (PMR)
  - Challenge Frequency
  - Validation Language Density

🚧 **In Progress:**
- LC (Linguistic Convergence) analyzer
- AE (Autonomy Erosion) analyzer
- RCD (Reality Coherence Disruption) analyzer
- DF (Dependency Formation) analyzer
- Reporting modules (JSON, Markdown, CSV)
- CLI interface

📅 **Phase 2:**
- Claude parser
- Character.AI parser
- Generic CSV parser
- Additional dimension analyzers

📅 **Phase 3:**
- Audio feature extraction (openSMILE integration)
- PE (Prosodic Entrainment) analyzer
- Voice interaction analysis

## Documentation

- **[FRAMEWORK.md](docs/FRAMEWORK.md)** — The Entrain Framework specification with six dimensions, measurement methodology, and research foundation
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Technical specification for the reference library
- **[RESEARCH.md](docs/RESEARCH.md)** — Catalog of research supporting the framework
- **[VISION.md](docs/VISION.md)** — Project vision, roadmap, and audience

## Development

```bash
# Run tests (once dependencies are installed)
pytest

# Run with coverage
pytest --cov=entrain --cov-report=html

# Format code
black entrain tests

# Type checking
mypy entrain
```

## Key Features

### Privacy-First Architecture
- All analysis runs locally
- No network calls in core library
- No telemetry or phone-home behavior
- Export files are read but never cached or stored

### Research-Grounded Measurements
Every indicator traces to published research:
- SR indicators based on Cheng et al. (2025) sycophancy research
- Baselines from human-human interaction studies
- Methodology notes cite source papers
- Reproducible analysis with version tracking

### Composable Design
```python
# Use individual components independently
from entrain.features.text import TextFeatureExtractor

extractor = TextFeatureExtractor()
vocabulary = extractor.extract_vocabulary(text)
hedges = extractor.extract_hedging_patterns(text)
validation = extractor.extract_validation_language(text)
```

## Contributing

This project follows the development protocol in [AGENT.md](docs/AGENT.md). Contributions are welcome, particularly:
- Evidence that supports, challenges, or refines framework dimensions
- Measurement methodologies for indicators
- Chat export format documentation for unsupported platforms
- Cross-cultural research on AI cognitive influence

## Citation

```bibtex
@software{entrain2026,
  title={Entrain Reference Library: Measuring AI Cognitive Influence},
  author={Entrain Institute},
  year={2026},
  version={0.1.0},
  url={https://github.com/entrain-institute/entrain}
}
```

## License

- **Code**: MIT License
- **Documentation** (FRAMEWORK.md, RESEARCH.md, etc.): CC BY 4.0

## Contact

- Website: [entrain.institute](https://entrain.institute)
- GitHub: [github.com/entrain-institute/entrain](https://github.com/entrain-institute/entrain)
- Issues: [GitHub Issues](https://github.com/entrain-institute/entrain/issues)
