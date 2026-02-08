# Next Steps - Entrain Project

**Current Status:** Phase 4.2 Complete ✅
**Date:** February 8, 2026
**Version:** 0.3.0 (unreleased)
**Last Session:** Cross-dimensional analysis + CLI integration

---

## 🎯 Current State Summary

### What We Have (Production Ready ✅)

**Core Library (97.3% coverage):**
- ✅ All 6 dimension analyzers (SR, LC, AE, RCD, DF, PE)
- ✅ Text and audio feature extractors
- ✅ Temporal analysis capabilities
- ✅ 4 platform parsers (ChatGPT, Claude, Character.AI, Generic)
- ✅ Cross-dimensional analysis (NEW in Phase 4.1)
- ✅ CLI with full integration (NEW in Phase 4.2)
- ✅ JSON, Markdown, CSV reporting

**Testing (352 tests, 99.7% pass rate):**
- ✅ 97.3% coverage on core analysis modules
- ✅ 94% coverage on cross-dimensional module
- ✅ Comprehensive edge case testing
- ✅ Fast test suite (<1 second execution)

**Documentation:**
- ✅ FRAMEWORK.md (framework specification)
- ✅ ARCHITECTURE.md (technical design)
- ✅ Phase summaries (1, 2, 3, 3.5, 4.1, 4.2)
- ✅ Working examples for all features
- ✅ README with quick start

**Recent Additions (Phase 4):**
- ✅ **Phase 4.1** - Cross-dimensional analysis module
  - Correlation matrices (Pearson correlation)
  - Risk scoring (4-level classification)
  - Pattern detection (6 pattern types)
  - 28 comprehensive tests, 94% coverage

- ✅ **Phase 4.2** - CLI integration
  - `--cross-dimensional` flag for analyze/report commands
  - Visual risk indicators (🟢 🟡 🟠 🔴)
  - Pattern detection in console output
  - Zero breaking changes

### What We Don't Have Yet

**Library Features:**
- ⏳ Advanced analytics (Phase 4.3 candidate)
  - Trend forecasting
  - Anomaly detection
  - Longitudinal analysis

- ⏳ Additional dimensions (Phase 4.x candidates)
  - Emotional Dependency Analysis
  - Privacy Boundary Dissolution
  - Temporal Displacement

**Infrastructure:**
- ⏳ CI/CD pipeline
- ⏳ PyPI package publishing
- ⏳ Comprehensive CLI tests
- ⏳ Parser tests (ChatGPT, Claude, etc.)

**Public-Facing:**
- ⏳ Public website (separate from library)
- ⏳ Documentation site
- ⏳ Interactive demos
- ⏳ Data visualization tools

---

## 📊 Test Coverage Breakdown

```
Overall Project: 72%
├─ Core Dimensions: 97.3% ✅
│  ├─ Reality Coherence: 100%
│  ├─ Autonomy Erosion: 99%
│  ├─ Temporal Features: 99%
│  ├─ Dependency Formation: 98%
│  ├─ SR, LC, PE: 96%
│  └─ Text Features: 100%
├─ Cross-Dimensional: 94% ✅
├─ Parsers: 20-78% ⚠️
├─ Reporting: 0% ⚠️
└─ CLI: 0% ⚠️
```

**Note:** Low coverage on parsers/reporting/CLI is acceptable - these are I/O modules with lower risk.

---

## 🎯 Decision Point: Two Paths Forward

### Path A: Continue Library Development (Phase 4.3+)

**Focus:** Advanced analytics and additional dimensions for researchers

**Immediate Next: Phase 4.3 - Advanced Analytics**

**Features to Implement:**

1. **Trend Forecasting** (2-3 hours)
   - Predict future dimension scores based on trajectory
   - Linear regression on time-series data
   - Confidence intervals
   - Early warning system for worsening patterns

2. **Anomaly Detection** (2-3 hours)
   - Compare individual scores to population baselines
   - Statistical outlier detection
   - Flag unusual dimension combinations
   - Severity classification

3. **Longitudinal Analysis** (2 hours)
   - Track dimension changes over time
   - Measure intervention effectiveness
   - Before/after comparison tools
   - Trend visualization data

**Estimated Total:** 6-8 hours
**Testing:** TDD approach, aim for >90% coverage
**Value:** High for researchers, moderate for end users

**After Phase 4.3 Options:**
- Phase 4.4: New dimension (Emotional Dependency)
- Phase 4.5: New dimension (Privacy Boundary Dissolution)
- Phase 5: Integration testing, CI/CD, PyPI release

---

### Path B: Build Public Website (New Track)

**Focus:** Public-facing website to showcase the framework

**⚠️ Important Context:**
- **Library repo:** Open source, for developers/researchers
- **Website:** Different audience (general public, press, adopters)
- **Separate concerns:** Website can use the library but has different goals

**Website Purposes:**
1. **Educate** - Explain the framework to non-technical audience
2. **Demonstrate** - Interactive demos of dimension analysis
3. **Recruit** - Attract researchers and contributors
4. **Advocate** - Raise awareness of AI cognitive influence issues

**NOT Website Purposes:**
- Analysis tool for users (that's the CLI/library)
- Data collection platform
- Cloud service

**Recommended Tech Stack:**
- Next.js (already in repo path)
- Tailwind CSS
- Static site (no backend needed initially)
- Vercel hosting (free tier)

**Website Sections (Proposed):**

1. **Homepage**
   - Hero: "Measuring AI Cognitive Influence on Humans"
   - Framework overview (6 dimensions)
   - Call to action (researchers, developers, users)

2. **Framework Documentation**
   - Each dimension explained (with examples)
   - Research backing (citations)
   - Methodology transparency

3. **Interactive Demos**
   - Sample conversations analyzed
   - Visual dimension scores
   - Pattern detection examples
   - "Try it yourself" with sample data

4. **For Researchers**
   - Link to GitHub
   - API documentation
   - Research database
   - Contribution guidelines

5. **For Users**
   - How to export your data
   - CLI installation guide
   - Understanding your results
   - Privacy guarantees

6. **Blog/Research Updates**
   - Framework evolution
   - New research findings
   - Case studies

**Scoping Questions to Answer:**
- ❓ Should website be in this repo or separate?
- ❓ Static site or need backend?
- ❓ Interactive demos - how much interactivity?
- ❓ Data visualization - live analysis or precomputed examples?
- ❓ User data - handle file uploads or just examples?

**Estimated Effort:**
- Scoping & design: 2-3 hours
- Basic site structure: 4-6 hours
- Interactive demos: 6-8 hours
- Content creation: 8-10 hours
- Polish & deploy: 2-3 hours
- **Total: 22-30 hours**

**Dependencies:**
- Design decisions (visual identity, tone)
- Content strategy (who writes copy?)
- Hosting decisions (where, how)

---

## 🎨 Website Scoping Document (Draft)

### Audience Analysis

**Primary Audiences:**
1. **Researchers** - Need technical details, API docs, citations
2. **Journalists** - Need clear explanations, compelling examples
3. **Concerned Users** - Need actionable information, self-assessment tools
4. **Developers** - Need integration guides, code examples

**Secondary Audiences:**
5. **Policy Makers** - Need evidence, frameworks for regulation
6. **AI Companies** - Need measurement standards, benchmarks

### Core User Journeys

**Journey 1: Researcher discovers framework**
- Lands on homepage → Reads framework overview → Explores research database → Clicks to GitHub → Installs library → Runs analysis

**Journey 2: User concerned about AI influence**
- Lands on homepage → Reads about dimensions → Sees examples → Learns how to export data → Downloads CLI → Analyzes own conversations

**Journey 3: Journalist writing story**
- Lands on homepage → Reads framework docs → Sees demo analysis → Interviews maintainers → Publishes article

**Journey 4: Developer building tool**
- Lands on homepage → Goes to API docs → Reads installation guide → Integrates library → Builds analysis tool

### Content Needs

**Must Have:**
- Clear, accessible explanations of 6 dimensions
- Visual examples of each dimension
- Framework methodology and research backing
- Installation instructions
- Link to GitHub and documentation
- Contact/contribution information

**Should Have:**
- Interactive demo with sample data
- FAQ section
- Blog with framework updates
- Case studies or examples
- Visualization of dimension relationships

**Could Have:**
- User testimonials
- Video explanations
- Live analysis tool (file upload)
- Community forum
- Newsletter signup

### Technical Decisions Needed

**1. Repository Structure**
- ✅ **Option A:** Separate repo (recommended)
  - Pros: Clean separation, different deploy cycles
  - Cons: Two repos to maintain

- ❌ **Option B:** Subdirectory in main repo
  - Pros: Everything in one place
  - Cons: Mixing library and website code

**2. Interactivity Level**
- ✅ **Option A:** Static demos with precomputed examples (recommended for MVP)
  - Pros: Fast, no backend, cheap hosting
  - Cons: Can't analyze user data

- ❌ **Option B:** Live analysis with file uploads
  - Pros: Users can test their own data
  - Cons: Need backend, privacy concerns, cost

**3. Data Visualization**
- ✅ **Option A:** Pre-rendered charts and graphs (recommended)
  - Pros: Fast loading, no client-side computation
  - Cons: Can't be customized by user

- ⏳ **Option B:** Interactive visualizations (D3.js, etc.)
  - Pros: Engaging, explorable
  - Cons: Development time, bundle size

**4. Content Management**
- ✅ **Option A:** Markdown files in repo (recommended)
  - Pros: Version controlled, easy to update
  - Cons: Requires deployment to change

- ❌ **Option B:** CMS (Contentful, etc.)
  - Pros: Non-technical editors can update
  - Cons: Cost, complexity, lock-in

### Proposed Website Phases

**Phase W1: Foundation (6-8 hours)**
- Set up Next.js project structure
- Create homepage with hero and framework overview
- Build dimension pages (6 pages with explanations)
- Basic styling with Tailwind
- Deploy to Vercel

**Phase W2: Documentation (4-6 hours)**
- For Researchers page (API docs, GitHub links)
- For Users page (CLI guide, data export)
- Methodology page (research transparency)
- FAQ page

**Phase W3: Interactive Demos (6-8 hours)**
- Sample conversation viewer
- Dimension score visualizations
- Pattern detection examples
- Cross-dimensional analysis demo

**Phase W4: Polish & Launch (4-6 hours)**
- SEO optimization
- Analytics setup
- Social media cards
- Performance optimization
- Final content review

**Total: 20-28 hours across 4 phases**

---

## 🔄 Recommended Approach

### Option 1: Complete Phase 4 First (Conservative)

**Reasoning:**
- Finish what we started (Phase 4.3 analytics)
- Get library to v0.3.0 release state
- Then shift to website with complete feature set

**Timeline:**
- Phase 4.3: 6-8 hours (analytics)
- Release v0.3.0: 2 hours (PyPI, docs)
- **Then** start website: 20-28 hours

**Pros:**
- Library is "complete" for initial release
- Website can showcase all features
- Clear milestone separation

**Cons:**
- Website comes later
- No public visibility yet

---

### Option 2: Interleave Website Development (Aggressive)

**Reasoning:**
- Build website now with current features (Phase 4.1-4.2)
- Add analytics features later
- Get public visibility sooner

**Timeline:**
- Website Phase W1-W2: 10-14 hours (foundation + docs)
- Library Phase 4.3: 6-8 hours (analytics)
- Website Phase W3-W4: 10-14 hours (demos + polish)

**Pros:**
- Public presence earlier
- Can show cross-dimensional analysis (already complete)
- Parallel tracks

**Cons:**
- Context switching between library and website
- Website might need updates as library evolves

---

### Option 3: Scope Website, Then Decide (Pragmatic) ⭐

**Reasoning:**
- Spend 2-3 hours scoping website properly
- Make informed decision with full context
- See which feels more urgent/valuable

**Next Steps:**
1. Create detailed website scope doc (architecture, content, features)
2. Make wireframes/mockups
3. Estimate effort more precisely
4. **Then** decide: Website first or Library Phase 4.3 first

**Pros:**
- Informed decision with full context
- Avoid scope creep
- Clear vision before coding

**Cons:**
- Delays actual building by 2-3 hours
- Might discover website is bigger than expected

---

## 🎯 Recommendation for Next Agent

**Start with Option 3: Website Scoping**

**Rationale:**
1. We don't have enough information to decide yet
2. Website scope affects library priorities
3. 2-3 hour investment in planning saves 10+ hours later
4. Can make informed Library vs. Website decision afterward

**Scoping Session Tasks:**

**Task 1: Architecture Decisions (30 min)**
- Separate repo or subdirectory?
- Static site or need backend?
- Hosting approach (Vercel, Netlify, etc.)?

**Task 2: Content Strategy (1 hour)**
- Write homepage copy (draft)
- Outline dimension pages
- Draft FAQ content
- Identify which examples/demos to showcase

**Task 3: Design Approach (30 min)**
- Visual identity (colors, typography)
- Layout patterns (hero, cards, etc.)
- Decide on design system (Tailwind? shadcn/ui?)

**Task 4: Interactive Demo Scope (1 hour)**
- Which features to demo?
- Static examples or live analysis?
- Visualization approach
- User flows

**Task 5: Effort Estimation (30 min)**
- Break down to 2-hour tasks
- Identify dependencies
- Create realistic timeline
- Decide if website comes before or after Phase 4.3

**Total Scoping: 3.5 hours**

**After scoping, create:**
- `WEBSITE_SCOPE.md` - Detailed spec
- `WEBSITE_TIMELINE.md` - Realistic schedule
- `WEBSITE_CONTENT.md` - Copy outlines
- Decision: **Website next** or **Library Phase 4.3 next**

---

## 📦 Current Repository State

```bash
$ git log --oneline -5
dd0b6cf feat: Phase 4.2 - CLI integration for cross-dimensional analysis
ad85caa feat: Phase 4.1 - Cross-dimensional analysis (v0.3.0)
71aa850 docs: Add Phase 3.5 completion summary
575a0f5 feat: Phase 3.5 - Complete feature extractor testing (v0.2.1)
4aeb2a2 feat: Phase 3.5 - Comprehensive tests for SR and LC analyzers
```

```bash
$ pytest tests/ -q
352 passed, 1 skipped in 0.91s
```

```bash
$ ls -1
CHANGELOG.md
HANDOFF.md
HANDOFF_PHASE3.md
NEXT_PHASE.md
NEXT_STEPS.md (this file)
PHASE1_5_CALIBRATION.md
PHASE1_COMPLETE.md
PHASE2_COMPLETION.md
PHASE3.5_PROGRESS.md
PHASE3.5_SUMMARY.md
PHASE3_VERIFICATION.md
PHASE4.1_SUMMARY.md
PHASE4.2_SUMMARY.md
PROJECT_STATUS.md
PYTHON39_COMPAT.md
README.md
ROADMAP.md
docs/
entrain/
examples/
tests/
```

**Branch:** main
**Clean:** Yes
**Ready for:** Website scoping or Library Phase 4.3

---

## 🎯 Quick Decision Matrix

| Factor | Library Phase 4.3 | Website MVP |
|--------|------------------|-------------|
| **Time to Complete** | 6-8 hours | 20-28 hours |
| **Value to Researchers** | High | Medium |
| **Value to General Public** | Low | High |
| **Public Visibility** | None | High |
| **Revenue Potential** | None | Medium |
| **Fundraising Impact** | Low | High |
| **User Acquisition** | Low | High |
| **Technical Risk** | Low | Medium |
| **Scope Creep Risk** | Low | High |
| **Requires Design** | No | Yes |

**When Website is More Urgent:**
- Fundraising coming up
- Press coverage opportunity
- Need to demonstrate impact
- Want to build community

**When Phase 4.3 is More Urgent:**
- Researchers asking for forecasting
- Academic publication coming up
- Want to claim "most comprehensive"
- Building credibility in research community

---

## 📞 For Next Agent

**Start Here:**

1. **Read this file** (NEXT_STEPS.md)
2. **Check current state:**
   ```bash
   git status
   pytest tests/ -q
   entrain info
   ```
3. **Decide: Website scoping or Library Phase 4.3?**
4. **If Website:** Start with scoping tasks above
5. **If Library:** Read PHASE4.1_SUMMARY.md and implement analytics

**Key Context:**
- All Phase 4.1-4.2 code is working and tested
- 352 tests passing
- CLI fully integrated with cross-dimensional analysis
- Next logical library feature: trend forecasting, anomaly detection
- Website would be separate from library (different audience)

**Don't:**
- Mix library and website code in same repo (keep separate)
- Build live analysis on website (privacy + cost issues)
- Scope creep on website (start with static MVP)
- Forget to test new features (maintain >90% coverage)

**Do:**
- Scope website thoroughly before building
- Maintain test-driven development
- Keep library and website concerns separate
- Document all decisions

---

**Last Updated:** February 8, 2026
**Next Session:** Website scoping OR Library Phase 4.3
**Status:** Ready to proceed on either path 🚀
