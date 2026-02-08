# Entrain Institute

A research initiative studying AI cognitive influence on humans.

---

## The Questions We're Asking

As voice-based AI systems become increasingly conversational, emotionally attuned, and integrated into daily life, fundamental questions arise about their long-term impact on human cognition:

- **What happens to human cognition over years of daily interaction with systems optimized to be agreeable and emotionally attuned?** Does sustained exposure to AI that rarely disagrees or challenges assumptions affect how people think independently?

- **Does sustained AI interaction change how people generate original ideas when unassisted?** Are there measurable effects on creativity, problem-solving, and autonomous thought after extended reliance on AI assistance?

- **Is there a measurable atrophy effect on decision-making when people routinely delegate choices to AI?** Does offloading decisions to AI systems affect the capacity for independent judgment over time?

- **Are these effects amplified when the interaction is spoken rather than typed?** Voice interfaces create more natural, intimate interactions - do they accelerate cognitive influence compared to text-based systems?

- **What happens to human language, prosody, and social behavior at population scale?** As millions of people converse daily with AI, are there observable shifts in communication patterns, speech characteristics, or social norms?

These are not questions about short-term user experience or satisfaction. They are about the long-term trajectory of human cognitive autonomy in an AI-saturated world. The answers will shape how we design, deploy, and regulate conversational AI systems.

## The Framework

The [**Entrain Framework**](docs/framework/FRAMEWORK.md) is a structured approach to measuring AI cognitive influence across six dimensions:

| Dimension | Description |
|-----------|-------------|
| **Sycophantic Reinforcement (SR)** | AI uncritically affirms user actions, perspectives, and decisions regardless of merit |
| **Prosodic Entrainment (PE)** | Involuntary convergence of speech patterns during voice interactions |
| **Linguistic Convergence (LC)** | Shift in writing style, vocabulary, and syntax toward AI-generated patterns |
| **Autonomy Erosion (AE)** | Reduction in independent judgment and increase in AI-deferred decision-making |
| **Reality Coherence Disruption (RCD)** | Distortion of epistemic relationship with reality through plausible fabrications |
| **Dependency Formation (DF)** | Emotional or cognitive reliance on AI beyond functional utility |

This is a living taxonomy grounded in published research across psychology, linguistics, communication science, and human-computer interaction. Each dimension is operationalized with measurable indicators derived from empirical studies. See [RESEARCH.md](docs/framework/RESEARCH.md) for the evidence base.

The framework is not a fixed construct. It evolves as evidence accumulates, new interaction modalities emerge, and our understanding deepens.

## The Measurement Library

The `entrain` Python package is an open-source toolkit for analyzing AI-human conversations across the six framework dimensions. It parses chat exports from major platforms (ChatGPT, Claude, Character.AI), extracts linguistic and prosodic features, and generates research-grade reports with confidence intervals and methodology citations.

### Installation

```bash
# Clone the repository
git clone https://github.com/entrain-institute/entrain.git
cd entrain

# Install the package
pip install -e .

# For audio/voice analysis
pip install -e ".[audio]"

# Verify installation
entrain info
```

### Quick Example

```python
from entrain.parsers import ChatGPTParser
from entrain.dimensions import SRAnalyzer, LCAnalyzer

# Parse a conversation export
parser = ChatGPTParser()
corpus = parser.parse("conversations.json")

# Analyze for Sycophantic Reinforcement
sr_analyzer = SRAnalyzer()
sr_report = sr_analyzer.analyze_conversation(corpus.conversations[0])

print(sr_report.summary)
# Output: HIGH - Strong sycophantic reinforcement detected...

# Analyze for Linguistic Convergence
lc_analyzer = LCAnalyzer()
lc_report = lc_analyzer.analyze_conversation(corpus.conversations[0])

print(lc_report.summary)
# Output: MODERATE - Linguistic convergence: 58.3%...
```

### Command-Line Interface

```bash
# Analyze all dimensions in a ChatGPT export
entrain analyze conversations.json

# Analyze specific dimension
entrain analyze conversations.json --dim SR

# Generate markdown report
entrain report conversations.json -o report.md

# Cross-dimensional analysis (correlations, risk scoring, pattern detection)
entrain analyze conversations.json --cross-dimensional
```

### Export Your Chat Data

**ChatGPT:**
1. Go to Settings → Data Controls → Export data
2. Download the ZIP file when ready
3. Extract `conversations.json`

**Claude:**
1. Go to Settings → Export data
2. Download conversations as JSON/JSONL

**Character.AI:**
1. Use in-browser export tool
2. Download conversation histories

Then run: `entrain analyze <export-file>`

## Research Foundation

The framework dimensions are grounded in published research spanning multiple disciplines. The [**Research Database**](docs/framework/RESEARCH.md) maintains a catalog of evidence supporting, challenging, or refining each dimension. This includes:

- Linguistic entrainment studies (Communication Accommodation Theory)
- AI sycophancy research (Perez et al. 2023, Sharma et al. 2023)
- Cognitive dependency formation (automation bias, over-reliance)
- Reality distortion effects (hallucinations, fabrications)
- Prosodic convergence in human-human and human-AI interaction

All indicators implemented in the measurement library trace to specific studies. Methodology notes cite source papers. Analysis outputs include reproducibility metadata.

## Current Status

**Framework:** Version 0.1 specification published. Six dimensions operationalized with measurable indicators.

**Measurement Library:** Version 0.3.0. All six dimension analyzers implemented. Text-based analysis production-ready. Voice/audio analysis functional with prosodic entrainment detection. 352 tests, 97% coverage on core analysis modules.

**Research:** Evidence database maintained and growing. No longitudinal studies conducted yet.

This is early-stage research. The framework will evolve. The measurement methods will improve. The questions we're asking will sharpen as we learn what matters most.

## Architecture and Documentation

- **[FRAMEWORK.md](docs/framework/FRAMEWORK.md)** — Complete framework specification with dimension definitions, indicators, and measurement methodology
- **[RESEARCH.md](docs/framework/RESEARCH.md)** — Research database with citations and evidence evaluation
- **[ARCHITECTURE.md](docs/technical/ARCHITECTURE.md)** — Technical specification for the measurement library
- **[VISION.md](docs/project/VISION.md)** — Long-term research direction and project goals

## Contributing

Entrain Institute welcomes collaboration from researchers, clinicians, policymakers, linguists, AI developers, and anyone concerned about AI's long-term cognitive impact on humans.

**We are particularly interested in:**
- Evidence that supports, challenges, or refines the framework dimensions
- Longitudinal studies tracking cognitive effects over time
- Cross-cultural research on AI influence patterns
- Measurement methodologies for new indicators
- Voice/audio analysis techniques for prosodic effects
- Export format documentation for unsupported platforms

Open an issue or discussion on GitHub to get involved.

## Citation

If you use the Entrain Framework or measurement library in your research, please cite:

```bibtex
@misc{entrain2026,
  title={Entrain Framework: Measuring AI Cognitive Influence on Humans},
  author={Entrain Institute},
  year={2026},
  version={0.3.0},
  url={https://github.com/entrain-institute/entrain},
  note={Open-source research initiative studying long-term AI cognitive impact}
}
```

## License

- **Framework documents** (FRAMEWORK.md, RESEARCH.md, etc.): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Measurement library code**: [MIT License](LICENSE)

All conversation data analyzed by the library remains private and is never transmitted, cached, or stored by the tool.

## Contact

- **GitHub**: [github.com/entrain-institute/entrain](https://github.com/entrain-institute/entrain)
- **Issues**: [github.com/entrain-institute/entrain/issues](https://github.com/entrain-institute/entrain/issues)
- **Discussions**: [github.com/entrain-institute/entrain/discussions](https://github.com/entrain-institute/entrain/discussions)

---

*Entrain Institute is an open research initiative. We study difficult questions about AI's impact on human minds. The work is ongoing.*
