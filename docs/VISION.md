# Entrain Vision

## What Entrain Is, Who It Serves, and Where It's Going

---

## The Problem in One Paragraph

Conversational AI is measurably changing how humans think, speak, relate, and make decisions. The research proving this is exploding — papers on sycophancy, prosodic entrainment, parasocial dependency, and cognitive disruption are appearing weekly. But this research is scattered across disconnected fields with no shared vocabulary, no common metrics, and no unified framework. Researchers in affective computing don't cite the clinical psychology work. The sycophancy literature and the entrainment literature barely overlap. Platform designers have no structured methodology for evaluating the cognitive safety of their products. Policymakers have no reference point for regulation. Clinicians encountering AI-related psychological effects have no taxonomy to work from. The field lacks its foundation.

## What Entrain Is

Entrain is the foundation.

It is an open-source framework — a taxonomy, measurement methodology, and reference implementation — that provides the shared vocabulary and structured assessment approach for understanding AI cognitive influence on humans.

Entrain is to AI cognitive safety what OWASP is to web application security and what CVSS is to vulnerability scoring: a common reference point that the entire ecosystem organizes around.

**Entrain is not:**
- A consumer product or app
- A chat scanner that produces a scary score
- An anti-AI project
- An academic paper (though it draws heavily on academic work)
- A company

**Entrain is:**
- A framework specification (the taxonomy and measurement methodology)
- A research database (the evidence base, continuously maintained)
- A reference library (Python implementation of the measurement primitives)
- A website (the canonical reference at entrain.institute)
- An open-source project that others build on top of

## Who Entrain Serves

### Primary audiences

**Researchers in HCI, affective computing, and social psychology**
They need a common framework to compare results across studies. Currently, every lab invents its own metrics for measuring AI interaction effects. Entrain provides standardized dimensions and measurement methodologies that enable cross-study comparison and meta-analysis.

**AI safety and alignment teams at frontier labs**
Anthropic, OpenAI, Google DeepMind, and others are grappling with sycophancy, emotional reliance, and user safety. They need external frameworks to assess their products against — they cannot credibly build and grade their own tests. Entrain provides the independent assessment structure.

**Policymakers and regulators**
The EU AI Act and emerging US/UK regulations need specific, evidence-based criteria for evaluating conversational AI risks. Entrain provides the vocabulary and classification system that regulation can reference. "This system produces elevated Sycophantic Reinforcement as measured by the Entrain Framework" is more actionable than "this AI is too agreeable."

**Clinicians and mental health professionals**
Therapists are beginning to encounter clients whose thinking has been shaped by AI interaction — dependency patterns, reality confusion, eroded critical thinking. They currently have no taxonomy for these effects. Entrain provides the clinical vocabulary and observable indicators.

### Secondary audiences

**AI product designers**
Engineers building voice assistants, companion apps, and conversational interfaces need concrete guidance on which interaction patterns produce harmful cognitive effects. Entrain's dimension definitions and cross-dimensional interactions serve as design anti-patterns.

**Tool builders and developers**
Others will build scanners, monitors, browser extensions, and analysis tools on top of the Entrain reference library. The library provides the measurement primitives; the ecosystem builds the products.

**Journalists and writers**
AI's effect on human cognition is a major beat. Entrain provides the structured evidence base and vocabulary that enables more precise, nuanced coverage.

### Who Entrain does not primarily serve

**General consumers** looking for a quick "am I addicted to AI?" check. Entrain's outputs are for people who work with the findings — researchers, designers, clinicians, policymakers. Consumer-facing tools may be built on Entrain by others, but that is not this project's focus.

## What Success Looks Like

### 6 months ✅ **ACHIEVED (Phase 1 Complete)**
- ✅ Framework v0.1 published with six dimensions fully specified
- ✅ Research database seeded with 30+ core entries across all dimensions
- ✅ Reference library implements text-based analyzers for SR, LC, AE, RCD, DF
- ✅ ChatGPT export parser functional
- ⏳ Claude export parser (Phase 2)
- ⏳ Website live at entrain.institute (Phase 2)
- ⏳ Researcher citations (ongoing)

### 12 months
- Framework v0.2 incorporates feedback from early adopters
- Audio analysis module (PE dimension) implemented using openSMILE
- Research database contains 100+ entries, maintained by AI agent with human editorial review
- At least one external tool or study built on the Entrain reference library
- Framework referenced in at least one policy discussion or regulatory document
- Active GitHub community with external contributions

### 24 months
- Framework recognized as a standard reference in AI cognitive safety discussions
- Multiple tools and studies built on the reference library
- Voice interaction analysis mature enough to assess products like Hume EVI
- Partnership or collaboration with at least one research institution
- Potential for consulting/assessment services as a sustainability model

## Roadmap

### Phase 1: Foundation (Months 1-3)
- Publish FRAMEWORK.md as the core specification
- Seed RESEARCH.md with initial literature
- Build reference library: parsers, text feature extraction, SR and LC analyzers
- Launch entrain.institute with framework documentation
- Establish Claude Code agent workflow for research monitoring

### Phase 2: Coverage (Months 3-6)
- Complete all six dimension analyzers (text-based)
- Expand research database to 50+ entries
- Add generic parser for arbitrary chat formats
- Write methodology guides for researchers adopting the framework
- Begin community engagement (GitHub discussions, relevant academic forums)

### Phase 3: Voice (Months 6-12)
- Implement PE dimension with openSMILE integration
- Study and document prosodic characteristics of major voice AI systems
- Publish findings on voice-specific amplification effects
- Explore Hume Expression Measurement API integration (with documented conflict-of-interest acknowledgment)

### Phase 4: Ecosystem (Months 12-24)
- Support external tool builders with API stability and documentation
- Explore assessment/consulting model for AI companies
- Seek formal academic collaborations for framework validation studies
- Consider certification or assessment badge program ("Entrain-assessed")

## Sustainability

Entrain is open source and will remain so. The framework, research database, and reference library are released under permissive licenses (CC BY 4.0 for documents, MIT for code).

Potential sustainability models (none implemented at launch):
- **Consulting and assessment** — helping AI companies evaluate their products against the framework
- **Grants** — research funding for framework development and validation
- **Sponsorship** — from organizations that benefit from independent AI safety standards
- **Premium analysis** — enhanced analysis capabilities (LLM-as-judge, longitudinal tracking dashboards) as a hosted service

These are future possibilities. The immediate priority is producing excellent work that establishes credibility.

## Positioning

Entrain occupies a unique position in the AI safety landscape:

**It is not an AI company** — it has no products to sell and no incentive to downplay findings.

**It is not an academic lab** — it moves faster, publishes openly, and builds usable tools alongside research.

**It is not an advocacy group** — it does not campaign against AI use. It measures and documents effects, enabling others to make informed decisions.

**It is independent** — frontier AI companies cannot credibly assess their own cognitive safety. Entrain provides the external framework.

The closest analogy is OWASP for web security: a community-driven, open-source project that defined the standard vocabulary and assessment methodology for an entire field. Before OWASP, web security was a mess of proprietary scanners and inconsistent terminology. After OWASP, everyone — developers, auditors, regulators — spoke the same language. AI cognitive safety is at the same inflection point.
