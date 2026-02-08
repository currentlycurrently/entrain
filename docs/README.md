# Entrain Institute

**A unified framework for understanding AI cognitive influence on humans.**

[entrain.institute](https://entrain.institute)

---

## What is Entrain?

Conversational AI is measurably changing how humans think, speak, relate, and make decisions. The research proving this is growing rapidly — but it's scattered across disconnected fields with no shared vocabulary, no common metrics, and no unified framework.

Entrain provides the foundation:

- **A taxonomy** of six dimensions along which AI interaction influences human cognition
- **A measurement methodology** grounded in published, peer-reviewed research
- **A reference library** (Python) implementing the measurement primitives
- **A research database** tracking the evidence base as it evolves

Entrain is to AI cognitive safety what OWASP is to web application security: a common reference point that researchers, platform designers, clinicians, policymakers, and tool builders can organize around.

## The Six Dimensions

| Dimension | Code | Description |
|-----------|------|-------------|
| Sycophantic Reinforcement | SR | AI uncritically affirms user actions, perspectives, and self-image |
| Prosodic Entrainment | PE | Involuntary convergence of user speech patterns toward AI voice patterns |
| Linguistic Convergence | LC | Shift in user writing/speaking style toward AI-characteristic patterns |
| Autonomy Erosion | AE | Progressive reduction in independent judgment and critical thinking |
| Reality Coherence Disruption | RCD | Distortion of user's epistemic relationship with reality |
| Dependency Formation | DF | Development of emotional/cognitive reliance beyond functional utility |

Each dimension is rigorously defined with measurable indicators, baseline comparisons, and citations to source research. See [FRAMEWORK.md](docs/FRAMEWORK.md) for the full specification.

## Documentation

| Document | Description |
|----------|-------------|
| [FRAMEWORK.md](docs/FRAMEWORK.md) | The core specification — taxonomy, dimensions, measurement methodology |
| [RESEARCH.md](docs/RESEARCH.md) | Research database — cataloged papers organized by dimension |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical architecture for the reference library |
| [VISION.md](docs/VISION.md) | Project vision, audience, roadmap |
| [AGENT.md](docs/AGENT.md) | Protocol for the AI research agent that maintains this project |

## Status

**Phase 1 Complete (v0.1.0).** The framework specification is published. The reference library implements all five text-based dimension analyzers (SR, LC, AE, RCD, DF) with ChatGPT export parsing. Voice analysis (PE dimension) planned for Phase 3. Feedback, critique, and contributions are welcome.

## Who This Is For

- **Researchers** studying human-AI interaction, affective computing, or social psychology
- **AI safety teams** at frontier labs assessing product cognitive safety
- **Policymakers** developing evidence-based AI regulation
- **Clinicians** encountering AI-related psychological effects
- **Developers** building tools that measure or mitigate AI cognitive influence

## Key Research

The framework synthesizes work including:

- Cheng et al. (2025) — Sycophantic AI reduces prosocial behavior and increases dependency (Stanford/CMU)
- Lipińska & Krzanowski (2025) — The Ontological Dissonance Hypothesis: broken continuity of presence in human-AI interaction
- Kirk et al. (2025) — Parasocial relationships with AI: decoupled wanting and addiction-like patterns
- arXiv:2504.10650 (2025) — Will AI shape the way we speak? Sociolinguistic influence of synthetic voices
- Zhang et al. (2025) — Taxonomy of harmful algorithmic behaviors in AI companionship (CHI 2025)

See [RESEARCH.md](docs/RESEARCH.md) for the complete catalog.

## Contributing

This project benefits from contributions across disciplines. If you're a researcher, clinician, developer, or policymaker with relevant expertise or findings, please open an issue or discussion.

Particularly welcome:
- Evidence that supports, challenges, or refines the framework dimensions
- Measurement methodologies for indicators that are currently hard to quantify
- Chat export format documentation for platforms not yet supported
- Cross-cultural research on AI cognitive influence
- Clinical observations of AI-related psychological effects

## License

- Documentation (FRAMEWORK.md, RESEARCH.md, VISION.md): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Code (reference library): MIT License

## Citation

```bibtex
@misc{entrain2026,
  title={The Entrain Framework: A Unified Taxonomy and Measurement Methodology for AI Cognitive Influence on Humans},
  author={Entrain Institute},
  year={2026},
  url={https://entrain.institute}
}
```
