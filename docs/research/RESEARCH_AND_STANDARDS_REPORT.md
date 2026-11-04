# Research and Standards Report: CLBG Intelligence Track

| Field | Value |
|---|---|
| Document | `docs/research/RESEARCH_AND_STANDARDS_REPORT.md` |
| Scope | Data Science (DS), ML Engineering (ML), AI Engineering (AI); Tiers 1–3 |
| Sources accessed | 2026-11-03 |
| Prepared by | CLBG Intelligence Track Assessment Committee |
| Status | Adopted. Decisions recorded in [architecture-decisions.md](architecture-decisions.md) |
| Companion documents | [Elite Educational Benchmarks](ELITE_EDUCATIONAL_BENCHMARKS.md) · [References](references.md) · [Legacy Repository Audit](LEGACY_REPOSITORY_AUDIT.md) · [Legacy Migration Map](LEGACY_ASSESSMENT_MIGRATION_MAP.md) · [Competency Framework](../competency-framework.md) |

This report sets out the evidence behind the CLBG Intelligence Track assessment ecosystem and the recommendations drawn from it. Each significant recommendation is given as a compact **recommendation record**: the problem, why action is necessary, the alternatives considered, why the chosen option is preferable, and the limitations that remain. Records are numbered after the section they appear in (R2 is in section 2, R10 in section 10).

---

## Contents

1. [Research methodology](#1-research-methodology)
2. [Existing industry competency expectations](#2-existing-industry-competency-expectations)
3. [Recommended competency framework per subtrack](#3-recommended-competency-framework-per-subtrack)
4. [Recommended tier definitions](#4-recommended-tier-definitions)
5. [Recommended technical units](#5-recommended-technical-units)
6. [Overlaps and distinctions between the three subtracks](#6-overlaps-and-distinctions-between-the-three-subtracks)
7. [Recommended tools and technology stacks](#7-recommended-tools-and-technology-stacks)
8. [Assessment design principles](#8-assessment-design-principles)
9. [Evaluation and scoring methodology](#9-evaluation-and-scoring-methodology)
10. [Security, privacy and responsible AI requirements](#10-security-privacy-and-responsible-ai-requirements)
11. [References](#11-references)
12. [Architectural decisions summary](#12-architectural-decisions-summary)

---

## 1. Research methodology

### 1.1 Sources

Five families of sources were consulted:

| Family | Examples | What it contributes |
|---|---|---|
| Curriculum standards | ACM/IEEE-CS/AAAI CS2023; ACM *Computing Competencies for Undergraduate Data Science Curricula* (2021) | Knowledge areas, competency models, the knowledge + skills + dispositions structure |
| Vendor certifications and learning material | Google PMLE guide v3.1; AWS MLA-C01 and AIF-C01; Microsoft DP-100, AI-102 (both retired), AI-300, AI-103; Google MLCC; *Rules of ML* | What industry currently expects at associate and professional level, and how it splits roles |
| Practitioner practice | Made With ML; Full Stack Deep Learning; Hugging Face LLM and Agents courses; Google and Microsoft MLOps maturity models; vendor evaluation and structured-output guidance; the MCP specification; Huyen, *AI Engineering* (2025) | How the work is done in practice, including AI-engineering patterns that curricula do not yet cover |
| Security, risk, law and documentation | OWASP LLM Top 10 2025; OWASP ML Security Top 10 (draft); NIST AI RMF 1.0 and AI 600-1; NDPA 2023; GAID 2025; Nigeria's National AI Strategy; Datasheets; Model Cards; REFORMS; NeurIPS checklist; Princeton leakage work | Non-negotiable requirements and documentation standards |
| Assessment science and university pedagogy | Revised Bloom; SOLO; University of Hawaiʻi at Mānoa and Carnegie Mellon rubric guidance; sixteen benchmark courses ([Elite Educational Benchmarks](ELITE_EDUCATIONAL_BENCHMARKS.md)) | How to design, score and calibrate assessments |

### 1.2 Dates

All sources were accessed on **2026-11-03**. Several are fast-moving, so dated facts are stated with their date: Microsoft's DP-100 retirement on 1 June 2026 and AI-102 retirement on 30 June 2026; the AI-300 study guide updated 2026-10-15; the AI-103 skills outline as of 16 April 2026; MCP specification version 2026-07-28.

### 1.3 Inclusion criteria

1. **Primary sources first.** Official exam guides, statute text, standards bodies and the original papers. Secondary sources (law-firm commentary, OECD.AI summaries) are used only where a primary source was unavailable or silent, and are labelled as such.
2. **Verified on retrieval.** A claim is included only if it was read on a page actually fetched. Search snippets were used only to locate pages.
3. **Relevance to a student community.** Sources must inform what a university student can be assessed on with CPU-class hardware and free tools.
4. **Currency.** Retired certifications are included only to show how the field has moved, and are always marked as retired.

### 1.4 Limitations

- **Unfinished or secondary pages.** The ACM CS2023 knowledge-area hours come from a page titled "mockup", so the hours are indicative. The GAID 2025 effective date (19 September 2025) comes from law-firm commentary, not the directive's text. The National AI Strategy pillars are OECD.AI's summary; the official PDF was not opened.
- **Unverifiable pages.** Kaggle's competition documentation renders client-side and could not be read, so no Kaggle-specific rules are claimed. Leaderboard findings rest on Hardt (2015), Blum and Hardt (2015) and Roelofs et al. (2019).
- **Draft standards.** The OWASP ML Security Top 10 is marked "in draft and being modified frequently". NIST states that AI RMF 1.0 is being revised.
- **Login walls.** Some university grading and collaboration policies are behind institutional login ([benchmarks §1.3](ELITE_EDUCATIONAL_BENCHMARKS.md#13-limits)).
- **Vendor framing.** Certification blueprints describe vendor platforms. CLBG uses them to read *role expectations*, not as a tooling prescription.
- **No legal advice.** The NDPA and GAID analysis is an engineering reading for assessment design, not legal advice.

---

## 2. Existing industry competency expectations

### 2.1 Curriculum standards

- **CS2023** (ACM/IEEE-CS/AAAI) places supervised and unsupervised learning, overfitting and the bias-variance trade-off, data preparation, train/validation/test evaluation, neural networks **and ethics for machine learning** inside the AI-ML CS Core. Data Management, Security and Society/Ethics/Profession are separate knowledge areas. *Implication:* the ML Tier 1 floor includes an ethics element, and privacy and security are cross-cutting criteria.
- **ACM Data Science (2021)** defines 11 knowledge areas. Those central to Data Science are DG (acquisition, cleaning, integration, privacy), DM (mining), AP (analysis and presentation) and PR (professionalism: communication, privacy, legal). Each area lists knowledge, skills and **dispositions**, with items tiered T1 (all graduates), T2 (most graduates) and E (elective).

### 2.2 Certification domains and weights

Weights are copied exactly as published.

**Google Cloud Professional Machine Learning Engineer** (exam guide v3.1; professional level, 3+ years; "does not directly assess coding skill")

| Section | Weight |
|---|---|
| 1. Architecting low-code AI solutions | 13% |
| 2. Collaborating within and across teams to manage data and models | ~14% |
| 3. Scaling prototypes into ML models | ~18% |
| 4. Serving and scaling models | ~20% |
| 5. Automating and orchestrating ML pipelines | ~22% |
| 6. Monitoring AI solutions | ~13% |

**AWS Certified Machine Learning Engineer – Associate (MLA-C01)** (about 1 year of SageMaker experience plus 1 year in a related role)

| Domain | Weight |
|---|---|
| 1. Data Preparation for ML | 28% |
| 2. ML Model Development | 26% |
| 3. Deployment and Orchestration of ML Workflows | 22% |
| 4. ML Solution Monitoring, Maintenance, and Security | 24% |

Explicitly **out of scope** at associate level: designing full end-to-end ML solutions, setting ML strategy, deep work in two or more ML domains, and quantising models and analysing the impact on accuracy.

**AWS Certified AI Practitioner (AIF-C01)** (up to 6 months' exposure; "uses but does not necessarily build")

| Domain | Weight |
|---|---|
| 1. Fundamentals of AI and ML | 20% |
| 2. Fundamentals of GenAI | 24% |
| 3. Applications of Foundation Models | 28% |
| 4. Guidelines for Responsible AI | 14% |
| 5. Security, Compliance, and Governance for AI Solutions | 14% |

**Microsoft (status at 2026-11-03).** Two exams that used to define the data-scientist and AI-engineer roles are **retired**:

| Exam | Status | Replaced by |
|---|---|---|
| DP-100 Azure Data Scientist Associate | Retired 1 June 2026 | **AI-300** Machine Learning Operations Engineer Associate |
| AI-102 Azure AI Engineer Associate | Retired 30 June 2026 | **AI-103** Azure AI Apps and Agents Developer Associate |

For the historical record, the last DP-100 outline weighted *Optimize language models for AI applications* at 25–30%, alongside design (20–25%), exploration and experiments (20–25%), and train and deploy (25–30%). The last AI-102 outline weighted planning 20–25%, generative AI 15–20%, agentic 5–10%, vision 10–15%, NLP 15–20% and knowledge mining 15–20%.

**AI-300: Operationalizing Machine Learning and Generative AI Solutions** (updated 2026-10-15)

| Skill area | Weight |
|---|---|
| Design and implement an MLOps infrastructure | 15–20% |
| Implement ML model lifecycle and operations | 25–30% |
| Design and implement a GenAIOps infrastructure | 20–25% |
| Implement generative AI quality assurance and observability | 10–15% |
| Optimize generative AI systems and model performance | 10–15% |

**AI-103: Developing AI Apps and Agents on Azure** (skills as of 16 April 2026)

| Skill area | Weight |
|---|---|
| Plan and manage an Azure AI solution | 25–30% |
| Implement generative AI and agentic solutions | 30–35% |
| Implement computer vision solutions | 10–15% |
| Implement text analysis solutions | 10–15% |
| Implement information extraction solutions | 10–15% |

### 2.3 Expectations per discipline

**Data Science.** O*NET 15-2051 describes the role as analysing data, visualising, validating models and *presenting results and recommending data-driven solutions*. With DP-100 retired, none of the cloud vendors reviewed keeps a stand-alone data-scientist certification. The discipline's identity is therefore defined by curricula (ACM DS) more than by vendors: data governance and quality, inference and experimentation, mining, and communication.

**ML Engineering.** AWS MLA gives the largest single weight (28%) to data preparation, and Google PMLE gives the largest (~22%) to pipeline automation. Both cover deployment, monitoring and security. AI-300 places MLOps *and* GenAIOps under one role. *Rules of ML* supplies scorable practices: metrics first (#2), a simple first model (#4), testing infrastructure separately (#5), watching for silent failures (#10) and measuring training-serving skew (#37). The Google (levels 0–2) and Microsoft (levels 0–4) maturity models give a ready-made progression.

**AI Engineering.** AI-103 gives its largest weight (30–35%) to generative AI and agentic solutions, and names guardrails, approval flows, structured JSON output, fabrication detection and indirect prompt injection via images. Vendor evaluation guidance converges on **eval-driven development**: task-specific datasets with edge and adversarial cases, metric, human and LLM-as-judge graders, and judges calibrated against human labels. Huyen draws the boundary: ML engineering trains traditional models; AI engineering builds on foundation models through prompting, context construction and parameter-efficient fine-tuning.

**Recommendation record R2: calibrate against industry, but assess building**

| | |
|---|---|
| Problem | Student assessments drift towards either trivia or unbounded projects when they have no external reference. |
| Why necessary | Members need placements that mean something to employers and to the community's own project teams. |
| Alternatives | (a) Adopt one vendor blueprint; (b) ignore industry and follow curricula only; (c) triangulate across curricula, several vendors and practitioner sources. |
| Why (c) | No single vendor is neutral, and curricula lag AI-engineering practice by several years. Triangulation finds the stable core. |
| Limitations | Blueprints change yearly (two of the reviewed exams retired in 2026). The [maintenance guide](../contributing/maintenance.md) schedules an annual refresh of AI-engineering details. |

---

## 3. Recommended competency framework per subtrack

The full framework, with observable behaviours for all 39 units at each tier, is in **[docs/competency-framework.md](../competency-framework.md)**. In summary:

| Subtrack | Core identity | Anchor competencies | Evidence most often required |
|---|---|---|---|
| **Data Science** | Turning raw data into trustworthy evidence and decisions | Data provenance and quality; inference and causal caution; communication to decision-makers | Data-quality reports, datasheet-style notes, uncertainty-aware findings, reproducible reports |
| **ML Engineering** | Training, evaluating, shipping and maintaining learning systems | Leakage-safe pipelines; valid evaluation; deployment; MLOps maturity; responsible ML | Hidden-test-verified code, slice metrics, model cards, reproducible pipelines, load and drift tests |
| **AI Engineering** | Reliable, secure products on foundation models | Structured generation with validation; retrieval; tools and agents; evaluation; security | Evaluation harnesses, traces, threat models, cost and latency measurements |

Eight **shared foundation competencies** (SF-1 to SF-8: software engineering, testing, reproducibility, evaluation sense, data protection, critical thinking, communication, integrity) are assessed in every subtrack through rubric rows and gates.

**Recommendation record R3: competencies as observable behaviours, with dispositions scored**

| | |
|---|---|
| Problem | Topic lists ("knows regression") cannot be marked consistently; the legacy bank had criterion names with no descriptors ([audit §1](LEGACY_REPOSITORY_AUDIT.md#1-executive-summary)). |
| Why necessary | Volunteer assessors need statements they can check against evidence. |
| Alternatives | (a) Topic syllabus; (b) knowledge-only learning outcomes; (c) behavioural statements per unit and tier, plus shared dispositions (the ACM DS knowledge-skills-dispositions model). |
| Why (c) | It is observable, aligns with analytic rubrics, and captures rigour, scepticism and ethical care, which ACM DS treats as dispositions. |
| Limitations | Statements need revision as assessments are piloted. Dispositions are inferred from behaviour and are harder to calibrate. |

---

## 4. Recommended tier definitions

The adopted tiers are defined in **[docs/tier-definitions.md](../tier-definitions.md)**. Each tier asks a qualitatively different question:

| Tier | The question | Specification | Typical time | Defence |
|---|---|---|---|---|
| **1: Foundation and Technical Fluency** | Can you produce a correct, explained, reproducible solution to a well-specified problem? | Precise | 6–20 h | 5–10 min: trace and modify |
| **2: Applied Engineering and Independent Problem-Solving** | Can you solve a realistic, partially specified problem, choosing and justifying methods? | Goals and constraints fixed | 15–40 h | 10–20 min: justify and debug |
| **3: Advanced Engineering, Research and System Design** | Can you take on an ambiguous problem, make research-informed decisions and defend trade-offs? | Partly open | 30–80 h | 20–40 min: defend design and research choices |

### 4.1 Calibration against industry levels

| Industry reference | Level | Where it sits relative to CLBG |
|---|---|---|
| AWS AI Practitioner (AIF-C01) | Up to 6 months; "uses but does not necessarily build"; coding, feature engineering, tuning and pipelines out of scope | **Below Tier 1.** CLBG Tier 1 always requires building and explaining working code. |
| AWS ML Engineer Associate (MLA-C01) | About 1 year with the platform plus 1 year in a related role | **Roughly Tier 2** in breadth, with CLBG adding coding and a defence. |
| MLA-C01 out-of-scope list | End-to-end design, ML strategy, depth in two or more domains, quantisation and its accuracy impact | **Tier 3 markers.** These are exactly the kinds of task CLBG reserves for Tier 3 (for example ML-11 Tier 3 Pareto studies, ML-12 and AI-13 Tier 3 architecture). |
| Google PMLE | Professional, 3+ years, no direct coding assessment | **Tier 3 breadth**, but CLBG Tier 3 is narrower (one problem in depth) and tests code. |
| MLOps maturity (Google 0–2; Microsoft 0–4) | Organisational levels | ML-13: Tier 1 ≈ level 0→1 hygiene; Tier 2 ≈ level 1–2; Tier 3 ≈ level 2–3+. |
| SOLO taxonomy | Response structure | Tier 1 ≈ multistructural→relational; Tier 2 ≈ relational; Tier 3 ≈ extended abstract ([competency framework §2](../competency-framework.md#2-cognitive-level-by-tier-bloom-and-solo)). |

**Recommendation record R4: three qualitatively different tiers**

| | |
|---|---|
| Problem | The legacy Novice/Intermediate/Pro labels scaled task *size*, producing a "cliff" from week-long tasks to multi-month products ([audit §1](LEGACY_REPOSITORY_AUDIT.md#1-executive-summary)). |
| Why necessary | Placement must distinguish *kinds* of competence, or a large Tier 1 task gets mistaken for Tier 2 ability. |
| Alternatives | (a) Size-scaled levels; (b) five or more fine-grained levels; (c) three tiers that differ in specification, method choice, evaluation ownership and ambiguity. |
| Why (c) | It matches the ACM DS T1/T2/E structure and the SOLO progression, and gives three levels that volunteer assessors can tell apart reliably. Six-dimensional difficulty ratings capture variation *within* a tier. |
| Limitations | Boundaries are judgements. Some assessments will sit near a boundary, which is why the placement framework requires two outcomes for Tiers 2 and 3. |

---

## 5. Recommended technical units

### 5.1 Adopted units

The adopted architecture is recorded in **[shared/units.yaml](../../shared/units.yaml)** and has **39 units**: DS-01..12, ML-01..14, AI-01..13. The planned totals are **232 unit assessments** (DS 30/26/24, ML 24/30/28, AI 20/27/23 at Tiers 1/2/3), with IDs pre-allocated in [shared/id-allocation.md](../../shared/id-allocation.md).

| Data Science | ML Engineering | AI Engineering |
|---|---|---|
| DS-01 Python and Data Wrangling | ML-01 Mathematical and Computational Foundations | AI-01 AI Engineering Foundations and Model Fundamentals |
| DS-02 Data Acquisition and Sourcing | ML-02 Supervised Learning and Ensembles | AI-02 Prompt Engineering and Structured Generation |
| DS-03 Data Cleaning and Data Quality | ML-03 Unsupervised and Representation Learning | AI-03 Model APIs and Local Inference |
| DS-04 Exploratory Data Analysis | ML-04 Feature Engineering and Data for ML | AI-04 Embeddings and Semantic Search |
| DS-05 Probability and Statistics | ML-05 Evaluation, Validation and Model Selection | AI-05 Retrieval-Augmented Generation and Knowledge Systems |
| DS-06 Data Visualization and Storytelling | ML-06 Neural Networks and Deep Learning | AI-06 AI Agents and Tool Calling |
| DS-07 SQL and Database Analytics | ML-07 Computer Vision | AI-07 Agentic Workflows and Orchestration |
| DS-08 Statistical Inference, Experimentation and Causal Thinking | ML-08 Natural Language Processing | AI-08 Context Engineering and Memory Systems |
| DS-09 Decision and Business Analytics | ML-09 Time-Series Machine Learning | AI-09 Multimodal AI Engineering |
| DS-10 Time-Series Analysis and Forecasting | ML-10 Recommender and Ranking Systems | AI-10 AI Evaluation and Observability |
| DS-11 Analytical Pipelines and Data Engineering | ML-11 Efficient ML and Model Optimization | AI-11 AI Security and Responsible AI |
| DS-12 Applied Research and Reproducible Communication | ML-12 Model Deployment and Serving | AI-12 Model Adaptation (Fine-tuning, PEFT and Distillation) |
| | ML-13 ML Pipelines, MLOps and Monitoring | AI-13 Production AI Architecture, Cost and Reliability |
| | ML-14 Responsible ML (Fairness, Interpretability and Robustness) | |

### 5.2 Changes from the originally proposed lists

The original proposal had 13 DS units, 15 ML units and 15 AI units. The changes below were made against that proposal. Numbers in the "original" column refer to the original numbering; units not listed were carried forward with at most a renumbering.

| Change | Original | Adopted | Rationale |
|---|---|---|---|
| **Merge** | DS-11 and DS-13 (separate applied-research and research-communication units) | **DS-12** Applied Research and Reproducible Communication | Research design and its reporting cannot be assessed separately without one becoming trivial. REFORMS and the NeurIPS checklist treat reproducible reporting as part of the study. Visual storytelling stays in DS-06. |
| Renumber | Analytical pipelines unit | **DS-11** | Follows from the merge. |
| **Fold** | A stand-alone ensembles unit | **ML-02** Supervised Learning and Ensembles | Ensembles are supervised models. AWS MLA lists ensembling under Train and refine models (2.2). The legacy audit found three redundant ensemble tasks and recommended keeping one in ML-02 ([audit §15](LEGACY_REPOSITORY_AUDIT.md#15-redundancy)). |
| **Merge** | ML-14 and ML-15 (separately proposed MLOps automation and monitoring units) | **ML-13** ML Pipelines, MLOps and Monitoring | The Google and Microsoft maturity models treat pipelines, CI/CD/CT, validation and monitoring triggers as one progression. Splitting them made Tier 1 cells unassessable. ML-12 keeps serving. |
| **Add** | none | **ML-10** Recommender and Ranking Systems | A major production ML family with distinctive evaluation pitfalls (implicit feedback, ranking metrics, feedback loops). The legacy bank had no task for it ([migration map](LEGACY_ASSESSMENT_MIGRATION_MAP.md#coverage-by-new-unit)). |
| **Add** | none | **ML-14** Responsible ML | CS2023 places ML ethics in the ML core; Model Cards, PMLE §6, OWASP ML Top 10 and GAID Art. 43 all require fairness, interpretability, robustness and ML-specific security evidence. The legacy bank had none. |
| **Merge** | AI-02 (stand-alone LLM concepts unit) | **AI-01** AI Engineering Foundations and Model Fundamentals | Concepts without building fall below CLBG Tier 1 (AIF-C01 is "uses but does not build"). Concepts are assessed through small experiments inside AI-01. |
| **Merge** | AI-07 (stand-alone vector databases unit) | **AI-05** RAG and Knowledge Systems (with ANN indexing in AI-04) | A vector store is a component, not a competency. AI-103 and AI-300 treat vector and hybrid search as part of grounding and RAG tuning. |
| **Merge** | AI-14 and AI-15 (separately proposed production concerns: cost and latency optimisation, and deployment and reliability) | **AI-13** Production AI Architecture, Cost and Reliability | Cost, latency, fallbacks and guardrails trade against each other, so they must be assessed together. Huyen ch. 9–10 and AI-103 treat them as one architecture problem. |
| **Add** | none | **AI-12** Model Adaptation (Fine-tuning, PEFT and Distillation) | AI-300, PMLE §3 and Huyen ch. 7–8 all include adaptation. The core competency is deciding *whether* to fine-tune versus prompt or retrieve. |
| **Keep separate** | Agents | **AI-06** (single tool loop) and **AI-07** (workflows and orchestration) | Vendor agent guidance distinguishes workflows on predefined paths from autonomous agents and advises the simplest solution first. Each half has enough distinct evidence for a unit. |
| **Keep separate** | Time series | **DS-10** and **ML-09** | Distinguished by the question asked (§6.3). A merge was considered and rejected. |

**Recommendation record R5: 39 units with uneven tier targets**

| | |
|---|---|
| Problem | Too many thin units dilute authoring capacity; too few broad units make assessments unfocused and coverage unverifiable. |
| Why necessary | Each unit must support at least three qualitatively different assessments across the tiers it offers, and be authorable by volunteers. |
| Alternatives | (a) Keep the original 43 units; (b) collapse to about 20 broad units; (c) 39 units, with merges where competencies cannot be separated and additions where evidence shows gaps. |
| Why (c) | Merges remove units that would assess components rather than competencies. Additions close gaps the evidence identified (responsible ML, recommenders, adaptation). |
| Limitations | Unit boundaries remain partly conventional. New AI-engineering patterns (for example new MCP extensions) may need units later; the [maintenance guide](../contributing/maintenance.md#6-adding-new-assessments) requires an ADR for any new unit. |

### 5.3 Cells not offered, and cells with a single assessment

| Unit | Tier | Target | Reason |
|---|---|---|---|
| DS-01 | 3 | 0 | Advanced wrangling only matters in service of a purpose, so it is assessed inside DS-11 and DS-12. |
| ML-11 | 1 | 0 | Optimisation presupposes a working, evaluated model and a profiling mindset, which are Tier 2 competencies. Quantisation analysis is outside even the AWS associate scope. |
| AI-01 | 3 | 0 | Deeper model-internals work is assessed in AI-12 and ML-08. A Tier 3 "foundations" assessment would be a contradiction. |
| AI-12 | 1 | 0 | Adaptation decisions need evaluation fluency (AI-10) and model-API experience first. |
| ML-09 | 1 | 1 | Foundational time-series reasoning is covered by DS-10; ML-09 concentrates on modelling at Tiers 2 and 3. |
| ML-10 | 1 | 1 | Recommenders need supervised-learning and evaluation fluency first. |
| ML-13 | 1 | 1 | Tier 1 covers experiment tracking and reproducibility only; full MLOps needs deployment fluency. |
| ML-14 | 1 | 1 | Tier 1 is awareness-level (disaggregated metrics and a basic model card); depth sits at Tiers 2–3. |
| AI-01 | 2 | 1 | One assessment on tokenizer and sampling internals. |
| AI-02, AI-03 | 3 | 1 each | The Tier 3 depth of these topics is mostly exercised inside AI-05, AI-10 and AI-13. |
| AI-07, AI-08, AI-09, AI-11, AI-13 | 1 | 1 each | These topics need prior AI-01 to AI-06 fluency; one well-scaffolded Tier 1 assessment is enough to place a beginner. |

The validator enforces target-zero cells: an assessment registered at a tier with `targets: 0` fails validation.

---

## 6. Overlaps and distinctions between the three subtracks

### 6.1 Shared versus specialist competencies

| Competency | Shared foundation (all subtracks) | DS specialist | ML specialist | AI specialist |
|---|---|---|---|---|
| Python, testing, reproducibility, version control | ✔ SF-1 to SF-3 | | | |
| Evaluation sense and baselines | ✔ SF-4 | Statistical validity (DS-08, DS-12) | Slices, skew, leakage (ML-05) | LLM evals and judges (AI-10) |
| Data protection (NDPA 2023, GAID 2025) | ✔ SF-5 | Lawful basis and provenance (DS-02) | Disparate outcomes (ML-14) | Transfer to foreign APIs; agent consent (AI-03, AI-06, AI-11) |
| Critical thinking, communication, integrity | ✔ SF-6 to SF-8 | Decision-maker communication (DS-06, DS-09, DS-12) | | |
| Data quality and acquisition | | ● DS-02, DS-03 | Label quality (ML-04) | Corpus curation (AI-05, AI-12) |
| Inference and causality | | ● DS-05, DS-08 | | |
| Model training | | | ● ML-02 to ML-10 | Adaptation (AI-12) |
| Deployment and operations | | Analytical pipelines (DS-11) | ● ML-12, ML-13 | ● AI-13 |
| Retrieval, tools, agents | | | | ● AI-04 to AI-08 |
| Security | | | OWASP ML Top 10 (ML-14) | OWASP LLM Top 10 (AI-11) |

The full matrix is in [competency framework §7](../competency-framework.md#7-cross-subtrack-competency-matrix).

### 6.2 Cross-disciplinary foundations

Three things span all subtracks and are deliberately **not** units:

1. **The shared foundation competencies** SF-1 to SF-8, assessed through rubric rows and gates.
2. **Data protection and ethics**, a rubric row and, where relevant, a privacy gate in every assessment. The research notes recommended this in preference to a separate unit because CS2023 puts ethics inside the ML core and ACM DS keeps professionalism across all knowledge areas.
3. **Cross-disciplinary assessments** (`XD-T<n>-NNN`, see ADR-006), described in [cross-disciplinary/README.md](../../cross-disciplinary/README.md):
   - **Foundations (`XD-FND`)**: a shared core plus a short subtrack-specific extension, counting as Tier 1 evidence in the subtrack whose extension the member completes.
   - **Integrated challenges (`XD-INT`)**: pair or team projects in which subtracks collaborate through data contracts, model APIs and evaluation protocols, counting as Tier 2 evidence in each member's own subtrack.
   - **Advanced challenges (`XD-ADV`)**: ambiguous, multi-discipline research problems, double-marked, counting as Tier 3 evidence.

**Recommendation record R6a: shared foundations assessed once, with subtrack extensions**

| | |
|---|---|
| Problem | Foundational skills (programming, version control, mathematics, testing, writing, responsible technology) are needed in all three subtracks. |
| Why necessary | Members should not repeat the same foundation assessment three times, and subtracks should stay distinct. |
| Alternatives | (a) Duplicate a foundations unit in each subtrack; (b) a fourth "foundations" subtrack with its own placement; (c) a shared core assessed once, plus a short extension showing use in the member's discipline. |
| Why (c) | It avoids duplication, keeps placement per subtrack (ADR-001), and still shows discipline-specific application. |
| Limitations | Extensions must be substantial enough to count as subtrack evidence; reviewers check this. Team challenges need contribution statements and a defence of the whole system by every member. |

### 6.3 Boundary cases

| Boundary | Distinction | Evidence |
|---|---|---|
| **DS-10 vs ML-09** (time series) | DS-10 asks *how uncertain is the forecast and how should a decision use it?* (decomposition, statistical forecasting, intervals, backtests). ML-09 asks *how do we build a leakage-free ML pipeline for sequence data?* (lag features, global models, temporal validation, streaming anomalies). ML-09 Tier 1 is reduced to one assessment because DS-10 covers the foundations. | Research notes §13.4; units.yaml tier notes |
| **ML-14 vs AI-11** (responsible and secure AI) | ML-14 covers trained models: fairness metrics, interpretability, robustness, model cards and the OWASP ML Top 10 (inversion, membership inference, poisoning). AI-11 covers foundation-model applications: OWASP LLM Top 10 2025, NIST AI 600-1, agent and MCP tool safety, and GAID Art. 43. | OWASP ML and LLM taxonomies are separate publications; research notes §16.3 |
| **ML-13 vs AI-13** (GenAIOps) | AI-300 merges MLOps and GenAIOps into one role. CLBG puts *operations infrastructure* in ML-13, which includes a GenAIOps bridge outcome at Tier 3 (prompt versioning, evaluation gates, token-cost monitoring). *Application architecture* (caching, routing, fallbacks, guardrails, product iteration) sits in AI-13. Tracing and evaluation telemetry belong to AI-10. | AI-300 skills outline; Microsoft maturity model treats GenAIOps as complementary |
| **ML-12 vs AI-13** (serving) | ML-12 serves a model the member trained. AI-13 serves an application built on someone else's model, where cost per token and provider failure dominate. | PMLE §4 vs AI-103 |
| **ML-08 vs AI-01 / AI-12** (language models) | ML-08 trains and evaluates text models. AI-01 explains model behaviour for application builders. AI-12 adapts foundation models for a task. Fine-tuning *mechanics* are ML; *task adaptation and data* are AI. | Huyen boundary statement; PMLE §3.2 vs Huyen ch. 7 |
| **DS-08/DS-09 vs ML** | Data Science keeps the "should this even be ML?" judgement (*Rules of ML* #1). | Research notes §16.9 |
| **DS-04 vs ML-04** (features) | Exploratory feature discovery is DS; production feature pipelines are ML. | AWS MLA D1, PMLE §2 vs ACM DS DG/DM |

**Recommendation record R6: assign contested topics to one owner per question**

| | |
|---|---|
| Problem | Overlapping units lead to duplicated assessments and to placements that count the same evidence twice. |
| Why necessary | Placement is per subtrack, so each subtrack's evidence must be distinct. |
| Alternatives | (a) Merge overlapping units across subtracks; (b) let overlaps stand; (c) keep both units but separate them by the question asked and the evidence required. |
| Why (c) | Industry draws the same lines: Microsoft split AI-300 from AI-103, and OWASP keeps ML and LLM lists apart. Members with a DS goal and those with an ML goal both need time-series competence, but different kinds. |
| Limitations | Some assessments will still feel close. Authors must state the unit's question in section B, and reviewers check it with the [quality scorecard](../assessment-quality-scorecard.md). |

---

## 7. Recommended tools and technology stacks

Principles: **free and open first; CPU first; paid services optional, always with a free alternative and a mock that the tests run on** ([authoring guide §1.4](../contributing/AUTHORING_GUIDE.md#14-accessibility-rules)). Cloud-specific services (SageMaker, Vertex AI, Azure ML) are not required; open equivalents are used, in line with the research notes' vendor-neutral recommendation.

| Layer | Data Science | ML Engineering | AI Engineering | Justification |
|---|---|---|---|---|
| Language and environment | Python 3, venv, Jupyter for exploration only | same | same | Common across every benchmark course and vendor guide; one language keeps marking comparable (benchmarks: avoid language choice at T1). |
| Data | pandas, Polars, NumPy, DuckDB, SQLite; Parquet and CSV | pandas, NumPy, Parquet | pandas for evaluation data; JSON and JSONL | DuckDB and SQLite run in-process on a laptop; Parquet, JSON and CSV are the formats AWS MLA lists. |
| Statistics and visualisation | SciPy, statsmodels, matplotlib; PyMC for Bayesian work | matplotlib | matplotlib | All free; PyMC replaces the legacy PyMC3 ([audit §16](LEGACY_REPOSITORY_AUDIT.md#16-outdated-resources-and-practices)). |
| Modelling | scikit-learn | scikit-learn, XGBoost or LightGBM, PyTorch (CPU) | Hugging Face Transformers and Datasets; small open-weight models; PEFT libraries for AI-12 | Named in PMLE, Made With ML and the Hugging Face courses; all run on CPU at assessment scale. |
| Experiment tracking and pipelines | Plain scripts with a Makefile or simple orchestrator; data-validation checks | MLflow (local), DVC or plain data versioning, GitHub Actions | Prompt and eval versioning in Git; local tracing | MLflow is named in DP-100, AI-300 and PMLE; runs locally with no server. |
| Serving | not required | FastAPI, Docker (optional with a non-Docker path), ONNX Runtime | FastAPI; simple caching | Free, widely used, CPU-friendly. |
| Model access | none | none | Ollama or a small Hugging Face model locally; a deterministic mock for tests; provider free tiers optional; paid APIs never required | Members' compute and budgets vary widely; NDPA ss.41–43 make foreign APIs a data-transfer question. |
| Validation and schemas | pandera or hand-written checks; JSON Schema | pydantic | pydantic, JSON Schema | Gemini's documentation states that some schema constraints are not enforced, so application-level validation is required. |
| Retrieval | none | none | FAISS or an in-process vector store; BM25 for lexical baselines | No external service needed. |
| Agents and integration | none | none | Direct API calls first; frameworks (for example smolagents, LlamaIndex, LangGraph) optional; MCP 2026-07-28 | Vendor agent guidance advises starting with the API directly because frameworks hide prompts and responses. |
| Testing and quality | pytest, pre-commit | pytest (code, data and model tests) | pytest with the mock model | The CLBG test layers (ADR-008) run on pytest. |
| Compute | Laptop with 4–8 GB RAM | Laptop; Google Colab or Kaggle free tier where GPU genuinely helps | Laptop; free tier for AI-12 | The tier definitions forbid required paid GPUs. |

**Recommendation record R7: open, CPU-first stack with mocks**

| | |
|---|---|
| Problem | Members have uneven compute, connectivity and budgets; hosted APIs change and cost money. |
| Why necessary | Placement must measure competence, not access to resources. |
| Alternatives | (a) Standardise on one cloud; (b) require paid API keys; (c) open, local-first tools with optional free tiers and mocks. |
| Why (c) | Equitable, reproducible offline, and portable. Tests on a deterministic mock make hidden testing possible for AI assessments. |
| Limitations | Small local models are weaker than frontier models, so some AI behaviours (for example complex tool use) are only partly observable locally. Mocks can drift from real provider behaviour; the annual AI-engineering refresh covers this. |

---

## 8. Assessment design principles

The [benchmarks report](ELITE_EDUCATIONAL_BENCHMARKS.md#3-cross-cutting-synthesis-clbg-design-principles) derived twenty principles (P1–P20) from sixteen courses. Combined with the industry findings, CLBG applies them as follows:

| Principle | Source | How CLBG applies it |
|---|---|---|
| Specification + autograded core + open extension (P1) | CS50, CS188 | Sections D (requirements), G (testable criteria) and J (extensions) of the standard specification |
| Public sanity tests, hidden correctness tests (P2) | Data 100, CS189 | Contract, requirement and hidden test layers (ADR-008) |
| The autograder is evidence, not the verdict (P3) | CS188, CMU 10-601 | Automated evidence is layer 1 of three; assessors decide |
| Correctness separate from design and style, with published weights (P4) | CS50, CS231N | 100-point analytic rubric with published weights |
| First principles before libraries (P5) | CMU 10-601, CS231N | Tier 1 implementation tasks with import restrictions where section K says so |
| Written reasoning with every submission (P6) | CS229, CS224N | Reports, data-quality notes, limitations sections |
| Unaided attempt, then assisted revision (P7) | CMU 10-601 | Allowed per assessment in section K |
| Format-specific AI rules, always disclosed (P8) | CS50, CS231N, MLiP | Default rules in [assessment integrity](../assessment-integrity.md) plus section K |
| Oral checkoffs and walkthroughs (P9) | MIT 6.390, MLiP, CS189 | Technical defence for every outcome above N |
| Milestones for projects (P10, P11) | CS231N, CS224N | Capstones and Tier 3 |
| Specification (pass/fail) grading for systems work (P12) | MLiP | Pass/fail gates and checkable acceptance criteria |
| Token budget for flexibility (P13) | MLiP | Three grace days per session ([assessment policy §7](../assessment-policy.md#7-deadlines-extensions-and-late-work)) |
| Individually verified floor (P14) | CS189, Data 100 | Defence gate overrides the score |
| Default or custom capstone (P15) | CS224N | Capstone collection |
| Contribution statements and citation (P16) | CS224N, MLiP | Pair and team work need contribution statements |
| Reproducibility as a deliverable (P17) | CS231N, Made With ML | Reproducibility gate; clean-environment rerun |
| Performance-tiered scoring for optimisation (P18) | CS188 | Optimisation formats score against stated budgets |
| Self-assessment against models (P19) | CS188, fast.ai | Formative only; never used for placement |
| Real, local, meaningful framing (P20) | CS50, 18.S191 | Nigerian and African contexts where natural, never forced |

Industry findings add five more:

| Industry-derived principle | Source |
|---|---|
| **Metric and baseline first.** Every model assessment names a baseline and justifies every threshold. | *Rules of ML* #2, #4; legacy audit §1 (arbitrary thresholds) |
| **Planted traps.** Tier 2/3 data tasks include deliberate leakage or skew traps that only careful members detect. | Princeton leakage taxonomy; *Rules of ML* #37 |
| **Eval-driven AI work.** Every Tier 2+ AI assessment includes an evaluation component with edge and adversarial cases. | Vendor evaluation guidance; Huyen ch. 3–4; AI-300 QA domain |
| **Schema plus semantics.** Structured outputs must be validated semantically, not just syntactically. | OpenAI and Gemini structured-output documentation |
| **Safety by construction for agents.** Consequential actions require approval; tool metadata is untrusted. | MCP specification; AI-103; OWASP LLM06 |

Every assessment also answers eight pedagogical questions (the Pedagogical Design section) and the final test: *would this genuinely challenge someone, teach them something valuable and provide credible evidence of their ability?* ([authoring guide §1](../contributing/AUTHORING_GUIDE.md#1-the-design-test)).

**Recommendation record R8: a standard specification built on benchmark principles**

| | |
|---|---|
| Problem | The legacy tasks fixed no dataset, contract, acceptance test or scale, so submissions were incomparable. |
| Why necessary | Comparable evidence is the basis of fair placement. |
| Alternatives | (a) Free-form briefs; (b) copy one university's format; (c) a CLBG standard (A–K plus Pedagogical Design) that combines principles from several benchmarks with industry practice. |
| Why (c) | It is machine-validated, so quality does not depend on any single author; it puts every principle above into a checkable section. |
| Limitations | It raises the authoring cost per assessment (a reference README is 1,500–4,000 words). Benchmarks are used only as public educational references; CLBG has no affiliation with any of the institutions ([benchmarks §6](ELITE_EDUCATIONAL_BENCHMARKS.md#6-disclaimer)). |

---

## 9. Evaluation and scoring methodology

The adopted method is defined in [evaluation-framework.md](../evaluation-framework.md) and [placement-framework.md](../placement-framework.md). In summary:

1. **Three layers of evidence.** Automated evidence (public and hidden tests, reproduction run, validators); expert review against a published rubric and a confidential marking guide; and a technical defence. No layer is sufficient alone.
2. **A 100-point analytic rubric.** Default weights: problem understanding 10, technical correctness 20, implementation quality 15, methodology 15, testing and evaluation 15, documentation and reproducibility 10, critical thinking 10, communication 5. Weights may be adapted per assessment but always total 100. Each dimension has four levels (Exemplary 90–100%, Proficient 70–89%, Developing 50–69%, Beginning 0–49%), and every score needs one line of evidence. An even number of levels avoids a catch-all middle (University of Hawaiʻi at Mānoa guidance).
3. **Pass/fail gates that override the score.** Integrity, reproducibility, defence, and assessment-specific gates such as privacy or safety.
4. **Four outcomes.** M (≥ 80, all gates), M− (65–79, all gates), R (50–64 or fixable failures), N (< 50 or a failed gate).
5. **Reliability.** Calibration on 2–3 exemplars before each cohort; blind double marking of all Tier 3 work, all scores within ±3 of a band boundary, every appeal and a 10% random sample; third marker at a difference of 10 points or more; inter-rater targets of ≤ 1.5 points per dimension and ≤ 6 points total; a moderation meeting each cohort.
6. **Placement from combined evidence.** Tier 2 and Tier 3 need two qualifying outcomes from different units (or a capstone or research-category Signature Challenge), and Tier 3 needs two assessors at the defence.

**Why no single-score placement.** One number cannot separate correctness from understanding, and it is the easiest thing to game or outsource. The rubric score is one input; gates and the defence carry equal weight. NDPA s.37 gives people a right not to be subject to decisions based solely on automated processing with significant effects, with safeguards of human intervention and contest; CLBG therefore never places a member by an automated score, and any automated or LLM-assisted marking aid is calibrated against human anchors and reviewed by a human assessor.

**Leaderboard pitfalls.** Repeatedly scoring against a public holdout leaks information about it: Hardt's "wacky boosting" moved a simulated entry from about rank 146 to about rank 6 without using the data, and Blum and Hardt formalise the problem. Roelofs et al. found little substantial overfitting across more than 100 Kaggle competitions, so the risk is real mainly with small holdouts and many queries. CLBG's rules: large private holdouts scored once; capped or delayed feedback; validation methodology graded, not rank; deliberate leakage traps; and a well-evidenced negative result can outscore a high but unvalidated number ([evaluation framework §5](../evaluation-framework.md#5-interpreting-numbers-honestly)).

**Recommendation record R9: analytic rubric, gates and defence**

| | |
|---|---|
| Problem | Holistic marks are "not diagnostic", and in a community with free AI tools a strong artefact no longer proves competence. |
| Why necessary | Placements must be consistent across volunteer assessors and must reflect the member's own understanding. |
| Alternatives | (a) Holistic grade; (b) automated tests only; (c) leaderboard ranking; (d) analytic rubric + gates + defence. |
| Why (d) | Analytic rubrics give consistent, diagnostic scoring (Mānoa; Carnegie Mellon). Gates stop a high score from hiding a fatal flaw. The defence verifies ownership without relying on unreliable detectors. |
| Limitations | Marking and defences take assessor time. Inter-rater targets will be missed at first and need the moderation cycle to improve. |

---

## 10. Security, privacy and responsible AI requirements

### 10.1 Nigeria Data Protection Act 2023 (Act No. 37)

| Provision | Requirement for CLBG assessments |
|---|---|
| s.2, s.3(1) | The Act applies to processing in Nigeria and to controllers operating in Nigeria. CLBG's own records and members' projects with real personal data are in scope. |
| s.24 principles | Purpose limitation, data minimisation, storage limitation, accuracy, security, duty of care. Assessments state why each personal-data field is needed. |
| s.25 lawful bases; s.26 consent | Any real personal data needs a recorded lawful basis. Consent must be affirmative; silence is not consent; withdrawal must be as easy as giving it (s.35). |
| s.28 DPIA | Required before processing likely to be high risk. |
| s.30, s.65 sensitive data | Health, biometrics, ethnicity, religion, political opinion, sex life, trade-union membership: synthetic data only in assessments, unless explicit consent exists. The research ground in s.30(1)(i) needs "the basis of a law", so it is not assumed to cover student projects. |
| s.31 children | Parental consent and age verification; CLBG assessments avoid children's data. |
| ss.34–38 rights | Datasets and memory stores must support access, correction, erasure and objection (relevant to AI-05 and AI-08). |
| s.37 automated decisions | Human intervention and contest safeguards; applies to CLBG's own placement decisions. |
| s.39 security; s.40 breach | Pseudonymisation, encryption, testing; the controller notifies the Commission within 72 hours. CLBG keeps an incident path for leaked datasets or keys ([SECURITY.md](../../SECURITY.md)). |
| ss.41–43 cross-border transfer | Sending personal data to a foreign hosted API is a transfer that needs an adequacy basis or a s.43 condition, recorded (s.41(2)). Rule: **no real personal data in prompts to hosted foreign APIs** unless a documented basis exists. |

### 10.2 GAID 2025 (NDPC/NDP ACT-GAID/01/2025)

Issued 20 March 2025; effective 19 September 2025 according to law-firm commentary (the directive's text does not state the date).

- **Art. 18:** consent is mandatory for sensitive data, children's data, transfer without adequacy and solely automated decisions with significant effects.
- **Art. 28:** a DPIA is mandatory and must be filed for profiling or scoring (Art. 28(3)(a)) and for **educational services processing records relating to students** (Art. 28(3)(m)). CLBG therefore keeps assessment results and placement records in its own controlled environment and never uses real member data inside assessments.
- **Art. 33:** restates the 72-hour breach notice.
- **Art. 43 (Emerging Technologies, including AI):** privacy by design and default; a DPIA that assesses **disparate outcomes**; consideration of anonymisation on collection; testing in low-risk environments; "retool and return" until outcomes are satisfactory, or discard the tool; continuous monitoring after deployment. This maps directly onto ML-14 and AI-11 rubric criteria and onto ML-13 monitoring.

### 10.3 Security and risk frameworks

| Framework | CLBG use |
|---|---|
| **OWASP Top 10 for LLM Applications 2025** (LLM01 Prompt Injection to LLM10 Unbounded Consumption) | Taxonomy for AI-11 and for the security requirements of AI-05 (LLM08 vector and embedding weaknesses), AI-06 and AI-07 (LLM01, LLM06 excessive agency), AI-02 (LLM05 improper output handling) and AI-13 (LLM10 unbounded consumption). |
| **OWASP ML Security Top 10** (draft; ML01–ML10) | Taxonomy for ML-14 Tier 2/3 threats such as model inversion and membership inference. |
| **NIST AI RMF 1.0** (Govern, Map, Measure, Manage) | Structure for all Tier 3 risk write-ups. |
| **NIST AI 600-1 Generative AI Profile** (12 risks, including confabulation, information integrity, data privacy, value chain) | GenAI risk register required in AI Tier 2+ work. |
| **MCP specification 2026-07-28** | Tools are arbitrary code execution; tool descriptions are untrusted unless from a trusted server; explicit consent before invoking tools. |

### 10.4 Documentation and reproducibility standards

| Standard | Required at |
|---|---|
| **Datasheets for Datasets** (Gebru et al.) | Light data note at DS Tier 1; datasheet-style note at DS Tier 2+ and wherever members source data |
| **Model Cards** (Mitchell et al.), with disaggregated metrics | ML Tier 2+; ML-14 at every tier |
| **REFORMS** (32 items, 8 sections) and a CLBG-adapted **NeurIPS checklist** (Yes/No/NA with justification) | DS-12 Tier 3 and ML Tier 3 research-style work |
| **Princeton leakage taxonomy** and model info sheets | ML-05 and any Tier 2/3 modelling assessment with leakage traps |

**Recommendation record R10: privacy and safety as cross-cutting gates**

| | |
|---|---|
| Problem | The legacy repository published a named individual's contact details and had no privacy practice ([audit §1](LEGACY_REPOSITORY_AUDIT.md#1-executive-summary)). AI applications add transfer, injection and agency risks. |
| Why necessary | NDPA 2023 and GAID 2025 apply to CLBG and its members; unsafe habits formed in assessments carry into real projects. |
| Alternatives | (a) A single ethics unit; (b) guidance only; (c) a rubric row in every assessment, a privacy or safety gate where relevant, plus specialist depth in DS-02, ML-14 and AI-11. |
| Why (c) | It follows CS2023 and ACM DS, which embed ethics rather than isolating it, and it makes violations outcome-changing. |
| Limitations | Assessors need training on the NDPA. The legal analysis will need review as the NDPC issues further guidance. |

---

## 11. References

The full categorised bibliography is **[references.md](references.md)**, and university benchmark sources are listed in [Elite Educational Benchmarks §7](ELITE_EDUCATIONAL_BENCHMARKS.md#7-references). Key sources, all accessed 2026-11-03:

- ACM/IEEE-CS/AAAI, *Computer Science Curricula 2023*. https://dl.acm.org/doi/book/10.1145/3664191
- ACM Data Science Task Force, *Computing Competencies for Undergraduate Data Science Curricula* (2021). https://dstf.acm.org/DSTF_Final_Report.pdf
- Google Cloud, Professional ML Engineer exam guide v3.1. https://services.google.com/fh/files/misc/professional_machine_learning_engineer_exam_guide_english_3.1_final.pdf
- AWS, MLA-C01 exam guide. https://d1.awsstatic.com/training-and-certification/docs-machine-learning-engineer-associate/AWS-Certified-Machine-Learning-Engineer-Associate_Exam-Guide.pdf
- AWS, AIF-C01 exam guide. https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01.html
- Microsoft Learn, AI-300 study guide. https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-300
- Microsoft Learn, AI-103 study guide. https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103
- Microsoft Learn, DP-100 (retired) and AI-102 (retired) study guides. https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/dp-100 · https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-102
- Google, *Rules of Machine Learning*. https://developers.google.com/machine-learning/guides/rules-of-ml
- Google Cloud, *MLOps: Continuous delivery and automation pipelines in ML*. https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
- Microsoft, *MLOps maturity model*. https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/mlops-maturity-model
- OpenAI, *Evaluation best practices*. https://developers.openai.com/api/docs/guides/evaluation-best-practices
- Anthropic, *Building effective agents* (2024). https://www.anthropic.com/engineering/building-effective-agents
- C. Huyen, *AI Engineering* (2025), table of contents. https://github.com/chiphuyen/aie-book/blob/main/ToC.md
- Model Context Protocol specification (2026-07-28). https://modelcontextprotocol.io/specification/latest
- OWASP Top 10 for LLM Applications 2025. https://genai.owasp.org/llm-top-10/
- OWASP Machine Learning Security Top 10. https://owasp.org/www-project-machine-learning-security-top-10/
- NIST AI RMF. https://www.nist.gov/itl/ai-risk-management-framework · NIST AI 600-1. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- Nigeria Data Protection Act 2023 (Official Gazette). https://ncc.gov.ng/media/801/view
- NDPC, GAID 2025. https://ndpc.gov.ng/wp-content/uploads/2025/07/NDP-ACT-GAID-2025-MARCH-20TH.pdf
- Gebru et al., *Datasheets for Datasets*. https://arxiv.org/abs/1803.09010 · Mitchell et al., *Model Cards*. https://arxiv.org/abs/1810.03993
- Kapoor et al., *REFORMS*. https://reforms.cs.princeton.edu/ · Kapoor and Narayanan, leakage. https://reproducible.cs.princeton.edu/
- Blum and Hardt, *The Ladder* (ICML 2015). https://proceedings.mlr.press/v37/blum15.html · Roelofs et al. (NeurIPS 2019). https://proceedings.neurips.cc/paper/2019/hash/ee39e503b6bedf0c98c388b7e8589aca-Abstract.html
- Anderson and Krathwohl revised Bloom (BU). https://www.bu.edu/provost/files/2013/10/Anderson-Krathwohl-Revision-to-Blooms-Taxonomy-of-Educational-Objectives.pdf · SOLO (UKZN). https://medicine.ukzn.ac.za/educationaltheory/solotaxonomy/
- University of Hawaiʻi at Mānoa, *Creating and Using Rubrics*. https://manoa.hawaii.edu/assessment/resources/creating-and-using-rubrics/

---

## 12. Architectural decisions summary

The decisions that implement these recommendations are recorded as ADRs in **[architecture-decisions.md](architecture-decisions.md)**:

| ADR | Decision | Recommendation records |
|---|---|---|
| ADR-001 | Three independent subtracks with per-subtrack placement | R3, R6 |
| ADR-002 | Three qualitatively different tiers | R4 |
| ADR-003 | The 39-unit architecture in `shared/units.yaml` | R5 |
| ADR-004 | The standard assessment specification (A–K plus Pedagogical Design) | R8 |
| ADR-005 | Two repositories: public member repository and private assessor kit | R8, R9 |
| ADR-006 | ID scheme and pre-allocation; IDs never reused | R5 |
| ADR-007 | Metadata schema and six-dimensional difficulty | R4, R8 |
| ADR-008 | Contract, requirement and hidden three-layer tests | R8, R9 |
| ADR-009 | 100-point analytic rubric, pass/fail gates and defence | R9 |
| ADR-010 | Selectable, not sequential, access | R4 |
| ADR-011 | Synthetic data policy and generator determinism | R10 |
| ADR-012 | Accessibility: CPU first, no required paid APIs, mocks | R7 |
| ADR-013 | Integrity through verification, not detection | R9 |
| ADR-014 | Generated catalogue and indexes | R8 |
| ADR-015 | Signature Challenges protocol: rigour-weighted, no single-metric leaderboards | R9 |
| ADR-016 | Assessment lifecycle and versioning | R2, R8 |
