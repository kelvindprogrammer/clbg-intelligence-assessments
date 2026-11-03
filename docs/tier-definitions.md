# Tier Definitions

Tiers describe **demonstrated competence within one subtrack**. They are not ranks of people. A member can be Tier 1 in Data Science, Tier 2 in ML Engineering and Tier 3 in AI Engineering at the same time, and that is normal.

Each tier asks a **qualitatively different question**. A Tier 2 assessment is never just a bigger Tier 1 assessment.

| | Tier 1: Foundation and Technical Fluency | Tier 2: Applied Engineering and Independent Problem-Solving | Tier 3: Advanced Engineering, Research and System Design |
|---|---|---|---|
| **The question** | Can you understand the fundamentals and independently produce a correct, explained, reproducible solution to a **well-specified** problem? | Can you independently solve a **realistic, partially specified** problem, choosing and justifying methods, testing your work and reasoning about its limits? | Can you take on an **ambiguous, substantial** problem, make research-informed decisions, run rigorous experiments and defend the trade-offs? |
| **Specification** | Precise. Interfaces and outputs are fixed, so the challenge is correctness and understanding. | Goals and constraints are fixed. The member decides methods, structure and some of the evaluation. | The problem and success criteria are partly open. The member frames sub-questions, designs the methodology and the evaluation, and argues validity. |
| **Starter support** | Scaffolding is common: fixed signatures, data loaders and public tests. | Light scaffolding: a contract or interface, with sample data. | Usually none beyond data and constraints. Sometimes a deliberately flawed system to improve. |
| **Data** | Clean or **purposefully** messy, single source. | Multiple sources, realistic complications (missingness, imbalance, leakage risks, drift). | Real-world scale or difficulty, confounding, distribution shift, unknown unknowns. |
| **Methods** | A specified method, implemented correctly, with its assumptions explained. | Several candidate methods, compared fairly against a baseline. | Research-informed choices, baselines and ablations, replication where relevant, error analysis. |
| **Evaluation** | Defined by the assessment. The member computes and interprets it. | The member chooses and justifies the metrics and validation design. | The member designs the evaluation protocol and shows its validity and robustness. |
| **Engineering** | Clean, readable code with tests for the core logic. | Modular, tested, error-handled and documented. Performance awareness. | Architecture and trade-offs: scalability, reliability, security, cost. |
| **Communication** | Explain what was done and why. | Justify decisions, quantify uncertainty, state limitations. | Technical-report quality: threats to validity, alternatives considered, honest negative results. |
| **Typical time** | 6–20 hours | 15–40 hours | 30–80 hours |
| **Defence** | 5–10 minutes: trace and modify | 10–20 minutes: justify and debug | 20–40 minutes: defend design and research choices, critique alternatives |

## 1. Tier 1: Foundation and Technical Fluency

A member at Tier 1 can:
- use the core language and tools of the subtrack correctly, without needing step-by-step guidance;
- implement a specified algorithm, analysis or component, and explain *why* it works;
- read and use documentation, and debug their own errors;
- write basic tests and reproducible instructions;
- name the common limitations of what they built.

*Beginner-friendly does not mean trivial.* Tier 1 assessments include traps that reward understanding over procedure-following. Examples: the namesakes in [DS-T1-006](../assessments/data-science/tier-1/units/DS-03-data-cleaning-and-quality/DS-T1-006-the-registry-that-lies/README.md), leakage in a naive split, or a prompt that "works" on its examples but not on held-out ones.

## 2. Tier 2: Applied Engineering and Independent Problem-Solving

A member at Tier 2 can:
- integrate several concepts to solve a realistic problem with incomplete specification;
- select methods, justify them and compare them with a sensible baseline;
- design meaningful evaluation and recognise misleading results;
- produce modular, tested, maintainable work with error handling;
- improve an existing imperfect solution, and diagnose why it was imperfect.

This is comparable to a strong internship or junior-engineer assignment, or applied coursework at upper-undergraduate level.

## 3. Tier 3: Advanced Engineering, Research and System Design

A member at Tier 3 can:
- frame an ambiguous problem into answerable questions and a defensible plan;
- use the research literature to choose, adapt or reproduce methods;
- design rigorous experiments, including baselines, ablations, robustness checks and error analysis;
- architect systems under real constraints (latency, cost, privacy, security, scale) and justify the trade-offs;
- communicate at technical-report level, including what did **not** work.

Tier 3 never requires expensive GPUs, proprietary data or paid services. Every Tier 3 assessment has a resource-conscious path. See the `compute` field in each assessment's metadata.

## 4. Placement is per subtrack, and evidence-based

- **Independent placement.** Placement in one subtrack says nothing about another.
- **No forced sequence.** Members may attempt any tier. The prerequisites tell you what knowledge you'll need, and the [placement framework](placement-framework.md) explains how attempts above your current tier count.
- **Evidence, not one score.** A tier is awarded on combined evidence: the assessment outcome, the defence, reproducibility and independence. See [placement-framework.md](placement-framework.md).
- **Growth.** Placement is reviewed every time new evidence arrives. Nobody is permanently labelled.

## 5. Multi-dimensional difficulty

Every assessment rates six independent dimensions from 1 (low) to 5 (very high), because "difficulty" isn't one thing:

| Dimension | 1 means… | 5 means… |
|---|---|---|
| **Technical** | A few well-known library calls | Deep command of several tools and their internals |
| **Mathematical** | Arithmetic and counting | Derivations, proofs or non-trivial probabilistic reasoning |
| **Research** | Everything needed is in the brief | Requires literature review, replication or original inquiry |
| **Engineering** | A single script | A multi-component system with tests, deployment and operations concerns |
| **Ambiguity** | Fully specified | The member must frame the problem and define success |
| **Resources** | Any laptop, offline | A strong CPU, a free cloud GPU tier or large downloads (a free path is always given) |

A project can be mathematically demanding without being infrastructure-heavy, or analytically subtle while being technically simple. Tiers set the *kind* of competence required, and the dimensions describe *where* the challenge lies.

**Calibration ranges.** These are guidance, not hard rules. Ambiguity is typically 1–3 at Tier 1, 2–4 at Tier 2 and 3–5 at Tier 3. Research is typically 1–2 at Tier 1 and 3–5 at Tier 3.
