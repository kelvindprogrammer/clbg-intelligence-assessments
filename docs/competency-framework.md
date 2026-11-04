# Competency Framework

This framework states **what a member can be observed doing** at each tier, in each of the 39 technical units of the CLBG Intelligence Track. Assessments are written to collect evidence of these behaviours, and assessors judge submissions and defences against them.

| | |
|---|---|
| **Status** | Adopted, 2026-11-03 |
| **Owner** | CLBG Intelligence Track Assessment Committee |
| **Unit source of truth** | [shared/units.yaml](../shared/units.yaml) |
| **Tier source of truth** | [tier-definitions.md](tier-definitions.md) |
| **Evidence base** | [Research and Standards Report](research/RESEARCH_AND_STANDARDS_REPORT.md), [Elite Educational Benchmarks](research/ELITE_EDUCATIONAL_BENCHMARKS.md), [references](research/references.md) |
| **Rationale** | [Architecture decisions](research/architecture-decisions.md), especially ADR-002 and ADR-003 |

---

## Contents

1. [How to read this framework](#1-how-to-read-this-framework)
2. [Cognitive level by tier (Bloom and SOLO)](#2-cognitive-level-by-tier-bloom-and-solo)
3. [Shared foundation competencies](#3-shared-foundation-competencies)
4. [Data Science units](#4-data-science-units)
5. [ML Engineering units](#5-ml-engineering-units)
6. [AI Engineering units](#6-ai-engineering-units)
7. [Cross-subtrack competency matrix](#7-cross-subtrack-competency-matrix)
8. [Using the framework](#8-using-the-framework)

---

## 1. How to read this framework

- **Competency statements are observable behaviours.** Each one starts with a verb that an assessor can check in code, results, a report or a defence: *implements*, *compares*, *justifies*, *designs*, *defends*. Verbs such as "knows" or "is familiar with" are not used, because nobody can observe them.
- **Each tier asks a different question** ([tier definitions](tier-definitions.md)). A Tier 2 statement is never just "more of" the Tier 1 statement. Tier 1 is about correctness and explanation on a well-specified problem. Tier 2 is about choosing, comparing and testing on a partially specified one. Tier 3 is about framing, research-informed method and defended trade-offs on an ambiguous one.
- **Lower tiers are implied.** A Tier 3 behaviour assumes the Tier 1 and Tier 2 behaviours for the same unit.
- **References.** A competency is cited as `<UNIT>.T<n>`. For example, `DS-03.T2` is the Tier 2 competency of DS-03 Data Cleaning and Data Quality. Shared foundations are cited as `SF-1` to `SF-8`.
- **Cells not offered.** Four unit-tier cells have no assessments (target 0 in `units.yaml`). They are marked **Not offered**, with the reason. Cells with a single planned assessment are marked *(1 assessment)*; the competency still applies in full.

---

## 2. Cognitive level by tier (Bloom and SOLO)

The revised Bloom taxonomy (Anderson and Krathwohl, 2001) describes the **cognitive process** a task demands. The SOLO taxonomy (Biggs and Collis, 1982) describes the **structure of the response** a member gives. CLBG uses Bloom when writing objectives and acceptance criteria, and SOLO when writing rubric performance descriptors. Sources are listed in [references §11](research/references.md#11-assessment-design-and-rubrics).

| | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| **Dominant Bloom processes** | Apply, Analyse (Remember and Understand are prerequisites, tested only inside application) | Analyse, Evaluate | Evaluate, Create |
| **Knowledge dimension emphasised** | Procedural and conceptual | Conceptual and procedural, with metacognitive checks (knowing when a method fails) | Metacognitive and conceptual (choosing among methods, judging validity) |
| **Target SOLO level** | Multistructural moving to relational: the parts are correct and the member can connect them | Relational: the member integrates evidence, methods and limits into a coherent whole | Extended abstract: the member generalises, transfers principles to new conditions and argues validity |
| **Typical objective verbs** | implement, compute, trace, explain, verify, reproduce | compare, select, justify, diagnose, design (an evaluation), critique | frame, design (a study or system), defend, generalise, synthesise, replicate |
| **Typical evidence** | Passing hidden tests; a correct explanation during tracing | A fair comparison against a baseline; a justified evaluation design | Ablations, threats-to-validity analysis, architecture trade-offs defended against alternatives |
| **Defence emphasis** | Can you trace and explain? | Can you justify and adapt? | Can you defend design, methodology and validity against alternatives? |

**Caveat.** Bloom categories are "not always clear-cut", and an analyse or evaluate task can be as demanding as a create task (Anderson and Krathwohl). The table gives the *dominant* demand, not an exclusive one. A Tier 1 debugging task, for example, legitimately requires analysis.

### 2.1 SOLO descriptors used in rubrics

| SOLO level | What the submission looks like | Usual rubric band |
|---|---|---|
| Pre-structural | Disconnected or incorrect steps; the method does not address the question | Beginning (0–49%) |
| Unistructural | One relevant aspect done correctly, the others missing | Beginning to Developing |
| Multistructural | Several aspects done correctly, but not connected: metrics reported but not interpreted, tests present but not targeted | Developing (50–69%) at T2/T3; Proficient at T1 |
| Relational | Aspects integrated: choices follow from the problem, evidence supports claims, limitations are tied to the method | Proficient (70–89%) at T2; Exemplary at T1 |
| Extended abstract | Generalises beyond the brief: transfers the method, anticipates failure under new conditions, argues validity | Exemplary (90–100%) at T2/T3 |

---

## 3. Shared foundation competencies

These eight competencies are assessed in **every** subtrack. They are not separate units. Instead they appear as rubric rows (for example, "Documentation and reproducibility" and "Critical thinking and limitations" in the [default rubric](evaluation-framework.md#2-the-rubric)) and as gates (integrity, reproducibility, privacy).

| ID | Competency | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|---|
| **SF-1** | Python and software engineering | Writes readable, typed Python that follows a fixed interface; handles expected errors; uses a virtual environment and pinned dependencies. | Structures work into modules with clear responsibilities; adds logging and error handling; keeps the code maintainable by others. | Makes and documents architectural choices (interfaces, packaging, extensibility) and justifies them against alternatives. |
| **SF-2** | Testing | Writes unit tests for core logic and runs the provided contract tests. | Tests code, data and models separately (for example a schema test, a data-quality test and a model-behaviour test). | Designs a test strategy proportionate to risk, including property-based, regression or adversarial tests, and explains what it cannot catch. |
| **SF-3** | Reproducibility and version control | Produces results that rerun from a clean environment with one documented command; commits incrementally with meaningful messages. | Fixes seeds, versions data and configuration, and reports run-to-run variation. | Delivers a reproducibility package (environment, data lineage, configuration, seeds, compute notes) that an independent assessor can rerun within stated tolerances. |
| **SF-4** | Evaluation sense | Uses the evaluation the brief defines and compares it with the given baseline. | Chooses metrics and validation that fit the problem's costs and data structure; recognises misleading results. | Designs an evaluation protocol and argues its validity, including uncertainty and robustness. |
| **SF-5** | Data protection and ethics (NDPA 2023) | Uses only synthetic or permitted data; keeps personal data out of third-party tools; can state whether data is personal under NDPA s.65. | States the lawful basis (s.25), minimises fields (s.24(1)(c)), records provenance and licence, and identifies sensitive categories (s.30, s.65). | Performs a DPIA-style analysis (NDPA s.28; GAID Art. 28 and Art. 43), including disparate outcomes, cross-border transfer (ss.41–43) and human review of automated decisions (s.37). |
| **SF-6** | Critical thinking and limitations | Names the common limitations of what was built. | Ties each limitation to a specific method choice or data property, and estimates its effect. | Writes threats to validity, alternatives considered and honest negative results. |
| **SF-7** | Communication | Explains what was done and why, for a technical reader. | Justifies decisions and quantifies uncertainty for a stated audience. | Writes at technical-report quality and also produces a short brief for a decision-maker. |
| **SF-8** | Professional integrity and AI-use disclosure | Completes `AI_USE_AND_SOURCES.md` honestly; cites adapted code and data; can explain every line submitted. | Verifies AI-assisted output with tests or checks, and documents how. | Shows independent judgement where tools disagree or fail, and defends every design choice live. Follows [assessment integrity](assessment-integrity.md). |

---

## 4. Data Science units

**Subtrack focus:** turning raw data into trustworthy evidence, insight and decisions. Data Science rewards question framing, inference, causal caution, data quality and communication. Deployment engineering belongs to ML Engineering (see the [Research and Standards Report §6](research/RESEARCH_AND_STANDARDS_REPORT.md#6-overlaps-and-distinctions-between-the-three-subtracks)).

| Unit | Tier 1: the member… | Tier 2: the member… | Tier 3: the member… |
|---|---|---|---|
| **DS-01** Python and Data Wrangling | reshapes, joins and aggregates tabular data with pandas or Polars to a fixed output schema; replaces loops with vectorised operations; checks join cardinality and row counts after every merge. | builds a tested wrangling module for multi-source data with mismatched keys and types; profiles time and memory and chooses between pandas, Polars and DuckDB on measured evidence. | **Not offered.** Advanced wrangling is assessed inside DS-11 and DS-12, where it serves a purpose rather than being an end in itself. |
| **DS-02** Data Acquisition and Sourcing | retrieves data from a documented API or open-data portal with pagination, retries and caching; records provenance, licence and access date; flags any personal data and the lawful-basis question it raises. | combines sources with different licences, schemas and update cadences; writes a datasheet-style data note; respects terms of use and rate limits; justifies each personal-data field against minimisation. | designs an acquisition strategy for an open question: sampling frame, coverage bias, consent and transfer constraints (NDPA ss.25–27, 41–43); quantifies coverage bias and argues the validity of the resulting dataset. |
| **DS-03** Data Cleaning and Data Quality | detects and fixes specified defects (missingness, inconsistent codes, duplicates) with explicit, tested rules; reports a count for every change; tells genuine duplicates from namesakes. | designs validation rules and record linkage for partially specified data; chooses imputation methods and measures their effect on downstream estimates. | builds a defensible data-quality framework when ground truth is uncertain (probabilistic linkage, error-rate estimation, audit sampling) and shows how residual error propagates to conclusions. |
| **DS-04** Exploratory Data Analysis | explores data systematically against a stated question (distributions, relationships, segment breakdowns) and records what the data can and cannot say. | generates and prioritises hypotheses from messy multi-source data; detects confounding patterns such as Simpson's paradox; keeps exploratory and confirmatory claims separate. | lets exploration reshape the question; specifies confirmatory analyses before running them; estimates the risk from analytic flexibility and justifies which findings are robust. |
| **DS-05** Probability and Statistics | computes and interprets estimates with uncertainty (confidence intervals, bootstrap) for a specified quantity; checks an analytical answer by simulation. | chooses estimators and models suitable for non-ideal data (skew, dependence, small samples); compares frequentist and Bayesian answers and explains the difference. | builds and critiques a probabilistic model for an open problem (for example a hierarchical model); checks it by posterior-predictive or simulation-based checks; reports sensitivity to assumptions. |
| **DS-06** Data Visualization and Storytelling | produces charts that encode a specified comparison honestly (scales, baselines, labels, uncertainty where given) and explains each encoding choice. | designs a visual narrative for a named audience and decision; justifies encodings; diagnoses and repairs misleading figures. | designs and evaluates communication of a contested or high-stakes finding, for example by testing reader comprehension of uncertainty; argues the trade-off between precision and comprehension. |
| **DS-07** SQL and Database Analytics | writes correct analytical SQL (joins, aggregation, window functions) against a fixed schema; verifies results with independent counts; explains NULL and join semantics. | models a relational schema for an analytics question; writes performant queries; reads query plans and justifies indexes or materialisations. | designs an analytical database layer for a realistic workload (partitioning, incremental models, cost and performance trade-offs) and proves correctness with tests. |
| **DS-08** Statistical Inference, Experimentation and Causal Thinking | runs and interprets a specified test or A/B analysis with effect size and confidence interval; states correctly what a p-value does and does not mean. | designs an experiment (power, sample size, guardrail metrics, multiple-comparison control); checks for sample-ratio mismatch; separates statistical from practical significance; judges whether the question needs ML at all. | estimates a causal effect from observational data with explicit identification assumptions; runs overlap, balance, placebo and sensitivity checks; defends the limits of the causal claim. |
| **DS-09** Decision and Business Analytics | computes specified metrics, cohorts and funnels correctly and explains what each metric rewards and hides. | designs a metric system for a decision; segments with justification; quantifies decision value under uncertainty; anticipates metric gaming. | turns an ambiguous business problem into a decision model (expected value or optimisation under uncertainty); stress-tests assumptions; recommends with stated risks, including whether ML would add value. |
| **DS-10** Time-Series Analysis and Forecasting | decomposes a series, checks stationarity, fits a specified statistical forecast and backtests it against a naive baseline. | selects among forecasting methods with rolling-origin backtests; produces and checks prediction intervals; handles calendar effects and regime changes. | designs forecasting for hierarchical or intermittent series and evaluates it by the cost of forecast error in the decision it serves; assesses interval calibration. |
| **DS-11** Analytical Pipelines and Data Engineering | turns a manual analysis into a reproducible, parameterised pipeline with tests and a single entry command. | builds incremental, idempotent ELT with data contracts and validation that fails loudly on schema drift. | designs a slice of an analytical data platform under constraints (freshness, cost, lineage, privacy); defends the orchestration and testing strategy; analyses failure modes. |
| **DS-12** Applied Research and Reproducible Communication | writes a short reproducible report on a specified question (methods, results with uncertainty, limitations) that reruns from a clean environment. | designs a study for a partially specified question; adds robustness checks; responds to structured peer review with revisions. | conducts end-to-end applied research or a replication; completes a CLBG-adapted REFORMS and NeurIPS-style checklist (Yes/No/NA with justification); reports sensitivity analyses and negative results; writes a decision-maker brief. |

---

## 5. ML Engineering units

**Subtrack focus:** designing, training, evaluating, shipping and maintaining learning systems. ML Engineering owns model training mechanics and the operation of models (MLOps, and the GenAIOps bridge in ML-13).

| Unit | Tier 1: the member… | Tier 2: the member… | Tier 3: the member… |
|---|---|---|---|
| **ML-01** Mathematical and Computational Foundations | implements gradient descent, matrix operations and probability calculations in NumPy; verifies gradients numerically; explains numerical-stability techniques such as log-sum-exp. | derives and implements an optimiser or model from first principles; diagnoses convergence and conditioning problems with evidence. | investigates an optimisation or numerical question in depth (for example convergence or implicit regularisation) and runs controlled experiments that support or refute a theoretical claim. |
| **ML-02** Supervised Learning and Ensembles | implements a specified model (for example logistic regression or a decision tree) from scratch, matches a library reference, and explains bias and variance using learning curves. | compares linear, kernel, tree and ensemble methods (bagging, boosting, stacking) fairly against a baseline under proper cross-validation; justifies the choice on accuracy, calibration, interpretability and cost. | investigates a research question about model behaviour (for example when boosting overfits, or how stacking leaks) with ablations; reproduces a published result at CPU scale. |
| **ML-03** Unsupervised and Representation Learning | implements k-means or PCA; chooses the number of clusters or components by a stated criterion; explains where the method fails. | selects and validates clustering or anomaly detection on unlabelled data with internal and external evidence; tests stability. | designs an evaluation for representation learning or anomaly detection without labels; argues its validity, including under distribution shift. |
| **ML-04** Feature Engineering and Data for ML | builds a leakage-safe preprocessing pipeline (fitted on training data only) with encoding and scaling, and demonstrates the leak a naive version causes. | engineers and selects features under cross-validation with justification; audits label quality; measures data-centric improvements against model changes. | designs a feature strategy for production (training-serving consistency, point-in-time correctness, freshness) and quantifies skew risk. |
| **ML-05** Evaluation, Validation and Model Selection | computes specified metrics (confusion matrix, precision, recall, ROC-AUC, RMSE) correctly with a proper split and baseline, and explains which metric matches the cost of errors. | designs validation (stratified, grouped, temporal or nested cross-validation); calibrates probabilities; compares models statistically; detects planted leakage; reports slice metrics. | designs an evaluation protocol for a hard case (distribution shift, small data, repeated holdout reuse); uses adversarial validation; argues the protocol's validity and holdout discipline. |
| **ML-06** Neural Networks and Deep Learning | implements backpropagation for a small MLP from scratch with gradient checks; trains a network in PyTorch and interprets loss curves. | runs controlled experiments on optimisers, regularisation and architecture; diagnoses training failures from curves and gradient statistics. | implements and studies a modern architecture component (for example attention) at CPU scale with ablations; reasons about compute and scaling trade-offs. |
| **ML-07** Computer Vision | implements image preprocessing and a small CNN or transfer-learning classifier; reports per-class errors and inspects misclassified images. | applies transfer learning and augmentation to a realistic, imbalanced dataset; analyses failure modes and robustness to corruptions. | designs a vision study or system under domain shift (devices, lighting, sites) with robustness evaluation and ablations; justifies data and compute choices. |
| **ML-08** Natural Language Processing | builds tokenisation and a classical text classifier (bag-of-words or TF-IDF) with a baseline, and inspects its errors. | fine-tunes or compares neural text models, including on low-resource or African-language data, and evaluates per language or slice. | investigates cross-lingual or low-resource transfer with controlled experiments and error analysis by language, script or dialect; argues how far results generalise. |
| **ML-09** Time-Series Machine Learning | *(1 assessment)* builds lag features with leakage-free temporal splits and compares the model with a seasonal-naive baseline. | builds global models across many series; validates with rolling-origin evaluation; finds and removes temporal leakage. | designs sequence models or streaming anomaly detection with drift-aware evaluation; justifies model complexity against the statistical baselines of DS-10. |
| **ML-10** Recommender and Ranking Systems | *(1 assessment)* implements baseline recommenders (popularity, item-item collaborative filtering) and computes ranking metrics (precision@k, recall@k, NDCG) correctly. | builds matrix-factorisation or implicit-feedback models; uses time-aware splits; analyses popularity bias and catalogue coverage. | designs offline evaluation that addresses selection bias and feedback loops; states the limits of offline evidence; proposes an online test design. |
| **ML-11** Efficient ML and Model Optimization | **Not offered.** Optimisation presupposes a working, evaluated model and a profiling mindset, both Tier 2 competencies. | profiles a working model; applies quantisation, pruning or ONNX export; reports accuracy retention and p50/p95 CPU latency against a stated budget. | designs an optimisation study across techniques (distillation, quantisation, pruning) with an accuracy-latency-memory Pareto analysis, including the impact of quantisation on data slices. |
| **ML-12** Model Deployment and Serving | packages a trained model behind a REST endpoint with input validation, a health check and a reproducible environment, and tests the endpoint. | containerises, versions and load-tests a service; chooses batch or online inference on evidence; implements model versioning and rollback. | architects serving under realistic constraints (latency targets, several models, canary or shadow release, cost) and defends the trade-offs with load and failure tests. |
| **ML-13** ML Pipelines, MLOps and Monitoring | *(1 assessment)* tracks experiments (for example with MLflow) and pins environments and seeds so a run reproduces: MLOps maturity level 0 moving to 1. | builds an automated, reproducible training pipeline with data and model validation, a model registry and CI tests of code, data and models: maturity level 1–2. | designs continuous training and monitoring (drift detection, retraining triggers, policy-based promotion) plus a GenAIOps bridge (prompt versioning, evaluation gates, token-cost monitoring): maturity level 2–3 and above. |
| **ML-14** Responsible ML (Fairness, Interpretability and Robustness) | *(1 assessment)* computes disaggregated metrics for specified groups, writes a basic model card and explains one fairness trade-off. | evaluates competing fairness criteria and their incompatibilities; applies explanation methods (for example permutation importance, SHAP) and demonstrates their limits; tests robustness. | conducts a responsible-ML audit covering fairness, interpretability, robustness and OWASP ML Top 10 threats (for example membership inference and poisoning), with a GAID Art. 43-style disparate-outcome analysis and evidenced mitigations. |

---

## 6. AI Engineering units

**Subtrack focus:** building reliable, secure software products on top of foundation models. AI Engineering composes applications from models: prompting, context construction, retrieval, tools, agents, evaluation and guardrails. Every Tier 2 and Tier 3 AI assessment includes an evaluation component; AI-10 is the anchor unit for evaluation.

| Unit | Tier 1: the member… | Tier 2: the member… | Tier 3: the member… |
|---|---|---|---|
| **AI-01** AI Engineering Foundations and Model Fundamentals | demonstrates tokens, sampling parameters and context limits through small experiments; builds an asynchronous, error-handled application around a model (local or mock). | *(1 assessment)* investigates tokenizer and sampling internals (for example token counts across Nigerian languages, temperature and top-p effects) and quantifies the consequences for cost and quality. | **Not offered.** Deeper model-internals work is assessed in AI-12 and ML-08. |
| **AI-02** Prompt Engineering and Structured Generation | writes prompts as specifications with few-shot examples; enforces a JSON schema *and* validates values semantically; handles refusals and incomplete responses; tests on held-out cases. | builds a prompt test and regression suite; compares prompt variants with a measured margin; versions prompts. | *(1 assessment)* designs a structured-generation system for a hard extraction task with measured reliability, a failure taxonomy and a cost-quality analysis. |
| **AI-03** Model APIs and Local Inference | calls a model API with streaming, retries with backoff and rate-limit handling; runs an open-weight model locally; keeps secrets out of code and logs. | builds a provider abstraction with fallbacks; measures latency, throughput and cost across local and hosted options. | *(1 assessment)* designs an inference strategy (local or hosted, model size, quantised local models) for stated constraints, including data residency under NDPA ss.41–43, with benchmarks. |
| **AI-04** Embeddings and Semantic Search | embeds documents, implements similarity search and evaluates retrieval with recall@k or MRR on a labelled set. | compares lexical, semantic and hybrid retrieval and approximate-nearest-neighbour indexes on quality and latency; tunes and justifies the configuration. | designs retrieval for a hard setting (multilingual, code-switched or domain-shifted text) including construction of the evaluation set and ablations. |
| **AI-05** Retrieval-Augmented Generation and Knowledge Systems | builds a RAG pipeline (chunking, indexing in a vector store, retrieval, grounded generation with citations) and measures groundedness on a fixed set. | tunes chunking, reranking and similarity thresholds against an evaluation set; separates retrieval errors from generation errors; handles unanswerable questions. | architects a maintainable knowledge system: updates and deletion (including NDPA erasure requests), access control, vector and embedding weaknesses (OWASP LLM08), all driven by evaluation. |
| **AI-06** AI Agents and Tool Calling | implements a single tool-calling loop with strict schemas, argument validation, error recovery and a step limit, against a mock. | designs tool interfaces with least privilege, permission prompts and human approval for consequential actions; measures tool-selection and argument accuracy. | hardens an agent against indirect prompt injection and excessive agency (OWASP LLM01, LLM06) with sandboxing and a threat model; measures the security-capability trade-off. |
| **AI-07** Agentic Workflows and Orchestration | *(1 assessment)* implements a fixed workflow (prompt chaining or routing) and explains, with evidence, why a workflow suits the task better than an autonomous agent. | compares workflow patterns (orchestrator-workers, evaluator-optimizer) against a simpler baseline using evaluations; integrates an MCP server with consent gates and treats tool metadata as untrusted. | designs durable multi-step or multi-agent orchestration that evaluations justify; handles failure, retries and state; documents trust boundaries. |
| **AI-08** Context Engineering and Memory Systems | *(1 assessment)* implements context budgeting and summarisation within a token budget and measures the information lost. | builds a long-term memory store with retrieval, update and forgetting policies, and evaluates memory accuracy. | designs a memory system for a demanding use case, covering consent and erasure, stale or contradictory memories, and cost. |
| **AI-09** Multimodal AI Engineering | *(1 assessment)* builds an OCR or document-extraction pipeline (or an image-description pipeline) validated against ground truth. | integrates vision-language or speech components into a pipeline; evaluates errors per modality; handles low-quality inputs. | designs document understanding or cross-modal retrieval for realistic noisy documents; tests for injection carried in images; evaluates performance across accents or scripts. |
| **AI-10** AI Evaluation and Observability | builds an evaluation set with edge and adversarial cases and metric-based graders, and runs it to compare system versions. | designs an evaluation harness with an LLM-as-judge calibrated against human labels; controls position and verbosity bias; adds tracing and regression gates. | designs the evaluation and observability strategy for a production system (agent metrics, judge-reliability study, offline-online consistency, token and cost telemetry) and argues its validity. |
| **AI-11** AI Security and Responsible AI | *(1 assessment)* demonstrates OWASP LLM Top 10 risks in a given application and applies basic mitigations (output handling, no secrets in prompts, input isolation). | red-teams an application systematically; prioritises risks; implements and tests defences; maps personal-data flows against NDPA requirements. | produces a threat model and risk assessment framed by NIST AI RMF and NIST AI 600-1, with a GAID Art. 43 DPIA-style analysis, defence in depth and a residual-risk statement. |
| **AI-12** Model Adaptation (Fine-tuning, PEFT and Distillation) | **Not offered.** Adaptation decisions need evaluation fluency (AI-10) and model-API experience first. | decides with evidence whether to prompt, retrieve or fine-tune; curates an adaptation dataset; runs LoRA or another PEFT method on a small model (CPU or free tier); evaluates against the prompt-only baseline. | designs an adaptation study (data quality, synthetic data, distillation); checks for regressions such as catastrophic forgetting; justifies cost against benefit. |
| **AI-13** Production AI Architecture, Cost and Reliability | *(1 assessment)* adds caching, timeouts and a fallback to a simple AI service and measures latency and cost per request. | designs routing, guardrails and budgets; load-tests the service; tracks cost and reliability targets. | architects a production AI system end to end with cost, latency and quality trade-offs, failure-mode analysis, security and an iteration plan, and defends it against alternatives. |

---

## 7. Cross-subtrack competency matrix

Legend: **●** primary owner (assessed in depth) · **◐** secondary (assessed where the unit needs it) · **○** awareness (assessed through shared foundations or rubric rows only).

| Competency area | Data Science | ML Engineering | AI Engineering | Distinction |
|---|---|---|---|---|
| Data acquisition, provenance and licensing | ● DS-02 | ◐ ML-04 | ◐ AI-05, AI-12 | DS asks "may we use it, and what does it represent?"; ML and AI inherit the answer. |
| Data cleaning and quality | ● DS-03, DS-11 | ◐ ML-04 (label quality) | ○ | DS owns record-level quality; ML owns labels and features. |
| Exploratory analysis and visualisation | ● DS-04, DS-06 | ◐ ML-05 (error analysis) | ○ | |
| Probability, statistics and uncertainty | ● DS-05, DS-08 | ◐ ML-01, ML-05 | ◐ AI-10 (eval uncertainty) | DS for inference; ML for model comparison; AI for evaluation confidence. |
| Causal inference and experimentation | ● DS-08 | ○ | ○ | Online tests of models are designed with DS-08 methods. |
| SQL and analytical data systems | ● DS-07, DS-11 | ◐ ML-13 | ○ | |
| Feature engineering | ◐ DS-04 (exploratory) | ● ML-04 (production) | ○ | |
| Model training and selection | ○ | ● ML-02, ML-03, ML-06 | ◐ AI-12 | ML trains models; AI adapts foundation models for a task. |
| Model evaluation | ● statistical validity (DS-08, DS-12) | ● slices, skew, leakage (ML-05) | ● LLM evaluations and judges (AI-10) | Shared area with three different failure modes. |
| Time series | ● DS-10 (forecast and decision use) | ● ML-09 (ML pipelines for sequences) | ○ | Separated by the question asked. |
| Text, vision and speech | ○ | ● ML-07, ML-08 (models) | ● AI-09 (applications) | ML builds models; AI composes them into products. |
| Retrieval and RAG | ○ | ○ | ● AI-04, AI-05 | |
| Tools, agents and MCP | ○ | ○ | ● AI-06, AI-07 | |
| Deployment and serving | ○ | ● ML-12 | ● AI-13 | ML serves trained models; AI serves model-backed applications. |
| Pipelines and operations | ● DS-11 (analytical) | ● ML-13 (MLOps, GenAIOps bridge) | ◐ AI-13 | |
| Monitoring and observability | ◐ DS-11 | ● ML-13 (drift, retraining) | ● AI-10 (tracing, telemetry) | |
| Efficiency and cost | ◐ DS-07 (query cost) | ● ML-11 | ● AI-13 (token and API cost) | |
| Fairness and responsible use | ● data bias (DS-02, DS-04) | ● model fairness and model cards (ML-14) | ● output safety and GenAI risk (AI-11) | Different evidence types per subtrack. |
| Security | ○ SF-5 | ● OWASP ML Top 10 (ML-14) | ● OWASP LLM Top 10 (AI-11) | |
| Documentation standards | ● datasheets (DS-02); REFORMS (DS-12) | ● model cards (ML-14) | ◐ system and eval documentation (AI-10, AI-13) | |
| Communication to decision-makers | ● DS-06, DS-09, DS-12 | ○ SF-7 | ○ SF-7 | |
| Data protection (NDPA 2023, GAID 2025) | SF-5 at all tiers | SF-5 at all tiers | SF-5 at all tiers | Cross-cutting by design: a rubric row and a gate, not a unit. |

---

## 8. Using the framework

**Authors.** The `competencies` field of `metadata.yaml` needs at least three entries ([schema](../shared/schemas/assessment.schema.json)). Write them as specific, observable behaviours derived from the cell for the assessment's unit and tier, and name the cell (for example "DS-03.T1: reports a count for every change made to the registry"). Section C objectives and section G acceptance criteria must collect evidence for those behaviours. See the [authoring guide](contributing/AUTHORING_GUIDE.md).

**Assessors.** The performance-level descriptors of each rubric dimension should match the SOLO levels in §2.1. When an attempt at Tier 2 or Tier 3 does not meet that tier, the lower tier's cell in this framework is the reference for recording lower-tier competence ([placement framework §3](placement-framework.md#3-tier-placement)).

**Members.** Use the tables to choose where to start, and to understand what feedback refers to. Placement is per subtrack, so a member can match Tier 3 cells in one subtrack and Tier 1 cells in another.

**Changes.** The framework changes only with a change to [shared/units.yaml](../shared/units.yaml) and an entry in the [architecture decisions](research/architecture-decisions.md), and takes effect at the start of the next cohort ([assessment policy §1](assessment-policy.md#1-scope-and-authority)).
