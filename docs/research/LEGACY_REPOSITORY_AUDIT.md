# Legacy Repository Audit: `assessment-intelligence` (branch `2025`)

| Field | Value |
|---|---|
| Repository audited | <https://github.com/kelvindprogrammer/assessment-intelligence> |
| Branch / head commit | `2025` @ `34c0b5d` (2026-01-27, "Completed Novice NLP Tasks") |
| History | 6 commits, 2025-12-18 to 2026-01-27; the whole task bank landed in one commit (`ef486b9`, 2025-12-18) |
| Files reviewed | Root `README.md`; all 21 `tasks.md`; all 21 domain `README.md` (diffed, 4 read in full); all 21 `starter.ipynb` (structure diffed, 4 opened cell by cell) |
| Audit date | 2026-11-03 |
| Prepared by | CLBG Intelligence Track Assessment Committee |
| Companion document | [`LEGACY_ASSESSMENT_MIGRATION_MAP.md`](LEGACY_ASSESSMENT_MIGRATION_MAP.md), which classifies every legacy task |

---

## 1. Executive summary

The legacy repository is a **task bank of 63 project briefs**: 3 levels (Novice, Intermediate, Pro) × 7 domains × 3 tasks. It was first written as the application challenge for a different student organisation (the root README is titled "Nile GDSC Core Ai Application Entry Repository"). It is clean and easy to navigate, and many of its topic choices are sound. As a **placement assessment**, though, it does not do the job. It sets the work but defines no way to measure it.

**Main findings**

1. **It is a syllabus of topics, not an assessment instrument.** No task fixes a dataset, input/output contract, acceptance test, time budget or scoring scale. Most tasks let candidates "create or load" their own data, so two submissions to the same task are rarely comparable, and synthetic data can make any target trivially reachable.
2. **Evaluation is unweighted and qualitative.** Each `tasks.md` ends with 4–8 criterion names ("Correctness", "Innovation", "Impact") with no level descriptors, weights, pass mark or tier decision rule. Reviewers would have to invent the rubric on the day, which is where most inter-rater disagreement comes from.
3. **Coverage stops at 2022-era ML.** There is no AI Engineering at all: no LLM application work, prompting, embeddings or retrieval, RAG, agents, tool calling, LLM evaluation or AI security. MLOps, deployment and monitoring appear in only two Pro tasks. SQL, data acquisition, recommender systems and responsible ML (fairness and interpretability) have no task of their own.
4. **The step from Intermediate to Pro is a cliff.** Novice and Intermediate tasks fit a weekend or a week. Several Pro tasks are multi-person, multi-month products ("Build an Experimentation Platform" with UI, API, bandits and sequential testing; "Build AutoML System"). Others need sustained GPU access (Cityscapes segmentation at >75% mIoU, ViT at >85% on CIFAR).
5. **Numeric targets are arbitrary and sometimes wrong-headed.** ">85% for MNIST" is below what plain logistic regression achieves. ">85% accuracy" for an ensemble is set with no dataset named. ">70% mAP" has no dataset or IoU definition. "Top 10% on public leaderboard equivalent" and "state-of-the-art or near SOTA" cannot be verified.
6. **Integrity and privacy problems in the repo itself.** Submissions are pull requests against a public repository, so every candidate can read earlier solutions. The head commit merged a completed Novice NLP solution into the canonical starter notebook. The root README publishes a named individual's personal email, mobile number and a WhatsApp group invite link. Under the NDPA 2023 that information should not be carried forward into any CLBG material.
7. **Starter materials add almost nothing.** All 21 notebooks are the same ~2 KB skeleton (imports for `numpy` and `matplotlib`, one empty cell per task). All 21 READMEs are the same ~900-byte template with generic "Resources" bullets and no links.

**Strengths worth keeping**

- A consistent, predictable layout (level → domain → README/tasks/starter) that members found easy to navigate.
- Novice "from scratch" tasks (linear regression by gradient descent, KNN, two-layer backpropagation, gradient-based edge detection) build real understanding and are cheap to auto-test.
- Several briefs show good methodological instincts: power analysis and practical vs statistical significance in A/B testing; cohort heatmaps; causal inference with **overlap, balance and placebo tests**; **nested** cross-validation; a controlled optimiser and regulariser study; quantisation, pruning and distillation benchmarked with **latency percentiles**; low-resource multilingual NLP; and drift monitoring with model cards.
- Frequent requests to "document assumptions and limitations" and "analyse misclassifications" point in the right direction, even though nothing grades them.

**Overall verdict.** Of the 63 tasks, 11 are retained in substance, 24 improved, 20 restructured, 4 replaced and 4 retired (see the migration map). The legacy bank is a useful **source of topic ideas** for about half of the new Data Science and ML Engineering units. It contributes almost nothing to AI Engineering, which the new framework has to build from scratch.

---

## 2. Directory structure

```
README.md
Novice/ | Intermediate/ | Pro/
  ├── Computer Vision/            README.md, tasks.md, starter.ipynb
  ├── Data Analytics/             (same three files)
  ├── Data Science/
  ├── Data Visualization/
  ├── Deep Learning/
  ├── General Machine Learning/
  └── Natural Language Processing/
```

| Aspect | Observation | Impact |
|---|---|---|
| Level-first hierarchy | Levels are top-level folders and domains are repeated under each. | A member cannot see one domain's progression in one place. Updating a domain means editing three folders. |
| Folder names with spaces | `General Machine Learning/` and similar | Fragile in shells and URLs (`%20`). The new repo uses kebab-case slugs. |
| No machine-readable metadata | No YAML/JSON per task, so no IDs, versions, durations, prerequisites or datasets. | Nothing can be catalogued, validated or reported automatically. |
| No task IDs | Tasks are "Task 1/2/3" inside a file. | Results cannot be recorded against a stable identifier. Renumbering silently changes meaning. |
| README tree mismatch | The structure block names the root `Nile-GDSC-intermediate-questions-repo/`. | A sign of copy-paste from an earlier repo. Minor, but it erodes trust. |
| No assessor-only space | Everything is public, including (since `34c0b5d`) a worked solution. | No place for marking guides, hidden tests or calibration exemplars. |
| No licence file | The repo has no `LICENSE`. | Reuse rights for the task text are unclear. CLBG should rewrite rather than copy text verbatim. |

## 3. Organisation and selection rules

- **"Any two of three" for most domains, but "all three" for Data Visualization**, at every level. At Pro this means a Data Visualization candidate must deliver a real-time dashboard, a custom visualisation library *and* a scrollytelling web experience, roughly three times the load of a Pro NLP candidate who picks two of three. Placement results are therefore not comparable across domains.
- **The root README contradicts itself.** "Each domain contains 3 tasks" appears only under the Intermediate description, and the rules list "AI/ML domains: ANY TWO task" and "Data Science & Data Analytics: ANY TWO tasks" as if they differed.
- **Free choice of tasks within a level** gives candidates agency, but no rule says how a strong submission on an easy task compares with a weak one on a hard task.
- **No duration or effort guidance.** Only a submission deadline and a 3-day review window are given.
- **No prerequisite or level-selection guidance.** Candidates self-select a level, with no diagnostic or criteria to route them.

## 4. Project quality

| Quality dimension | Rating | Evidence |
|---|---|---|
| Clarity of objective | Good | Every task has a one-line objective and a numbered requirement list. |
| Specificity of deliverable | Weak | Requirements are activity lists ("Implement…", "Visualize…") rather than observable outputs with acceptance criteria. |
| Authenticity | Mixed | Business framings (churn, cohorts, pricing) are realistic. Many tasks have no stakeholder, decision or constraint, so the work is "apply technique X" rather than "solve problem Y". |
| Scope calibration | Weak at Pro | Pro Data Analytics T1, Pro GML T1 and T3, and Pro DV T1 and T3 are each a product, not an assessment. |
| Reproducibility | Weak | No seeds, environment files, pinned versions or data provenance requirements. |
| Assessability | Weak | No tests, rubrics or exemplars. "Achieve competitive performance on chosen task" leaves both task and target up to the candidate. |

## 5. Originality

- Most briefs are **canonical textbook exercises** (KNN from scratch, CNN on MNIST/CIFAR, churn prediction, Kaggle-style stacking, sales dashboards). They are valuable for learning, but polished public solutions for every one are a search away, and a generative assistant can produce them in seconds. As written, a submission shows that work was *produced*, not that the candidate *understands* it.
- The repository has **no local or African context**: no Nigerian datasets, languages, sectors (mobile money, agriculture, power, transport) or constraints (intermittent power, bandwidth, CPU-only laptops). The one opening is Pro NLP T2 (multilingual, "high and low-resource languages"), which deserves more weight. MasakhaNER 2.0, NaijaSenti and MAFAND-MT exist precisely for this.
- There are no **reverse-engineering, debugging, critique, or replication** formats. Every task asks for something to be built. The new framework varies format deliberately because some formats resist copying better than others.

## 6. Technical depth

- **Novice:** sound depth for a first tier. Implementing gradients and distance computations by hand is the right level.
- **Intermediate:** the depth is broad but often a checklist. For example, "Implement at least 2 segmentation methods… Watershed or similar… CRF refinement" lists techniques without the question that would make the choice among them matter.
- **Pro:** the depth is nominally high but **list-driven**. Pro Data Analytics T2 asks for hierarchical models, state-space models, mixture models, causal models with priors, WAIC/LOO, Bayes factors and decision analysis, all in one task. Depth through breadth rewards whoever lists the most techniques, not whoever reasons best about one hard problem.
- **Validity reasoning is mostly absent.** Apart from Pro DS T1 (causal assumptions) and Intermediate DA T1 (test assumptions), tasks do not ask candidates to argue *why their evaluation supports their claim*. That argument is the core of Tier 3 in the new framework.

## 7. Difficulty progression

| Transition | Assessment |
|---|---|
| Novice → Intermediate | Mostly smooth. In ML it moves from from-scratch algorithms to library-based pipelines with cross-validation and tuning. In CV it moves from pixel arithmetic to features, segmentation and classical detection. |
| Intermediate → Pro | **Discontinuous.** It jumps from "build a model and compare" to "build a platform/system/library and deploy it". No intermediate step trains the system-design and validity-argument skills that Pro presupposes. |
| Within-level variance | High. Pro DS T1 (causal analysis) is a demanding but bounded project, while Pro DA T1 (experimentation platform) is open-ended engineering. Intermediate DV T3 (storytelling) is far lighter than Intermediate DL T3 (transfer learning). |
| Duplication across levels | Feature engineering appears at Novice DS T3, Intermediate GML T2 and Pro DS T2. Ensembles/stacking at Intermediate GML T1, Pro GML T2 and Pro DS T3. Dashboards at Novice DV T3, Intermediate DV T2 and Pro DV T1. Some of this is a deliberate spiral, but the higher versions mostly add *more items*, not *harder reasoning*. |

The new framework fixes this by making tiers **differ in kind**. Tier 1 is a precise specification marked for correctness. Tier 2 gives a partial specification and asks for method choice measured against a baseline. Tier 3 is open, with research-informed methodology, ablations and validity arguments.

## 8. Documentation

- **Domain READMEs are templated boilerplate.** The 21 files are 844–998 bytes each and identical in structure: Overview, Learning Objectives (4 bullets), Requirements ("Python 3.x, numpy, matplotlib, Any other libraries"), Tasks, Submission, Resources (generic phrases such as "Recent CV research papers", with no links), and a closing emoji.
- **No candidate-facing guidance on what good looks like**: no exemplar, sample report, word limits, notebook vs package expectations, or citation and AI-use policy.
- **No assessor documentation**: no marking guide, common-errors list or moderation procedure.
- **Root README** mixes event logistics (registration form, dates, personal contact details, WhatsApp invite) with permanent documentation. Event logistics expire, while the assessment should not.

## 9. Starter materials

- All 21 `starter.ipynb` files share one skeleton: a "Setup" cell importing `numpy` and `matplotlib`, then per task a markdown header ("Remove this cell if you're not completing this task") and an empty code cell, then a "Conclusion" cell. Most notebooks lack `kernelspec` metadata.
- **No data loaders, fixtures, function signatures, type hints or tests**, so there is no contract to grade against and no scaffolding for Novices.
- **A solution is committed to a starter.** Commit `34c0b5d` replaced `Novice/Natural Language Processing/starter.ipynb` with a candidate's completed Tasks 1–2 (33 KB, with outputs and commentary). Anyone attempting Novice NLP now starts from a worked answer.
- Notebook-only delivery discourages engineering habits (modules, tests, CLI entry points) that the ML Engineering and AI Engineering tracks must assess.

## 10. Evaluation methods

| Element | Present? | Notes |
|---|---|---|
| Criteria names | Yes | 4–8 per file, e.g. Correctness, Code Quality, Documentation, Creativity/Innovation, Performance. |
| Level descriptors | No | Nothing distinguishes "meets" from "exceeds" or "below". |
| Weights / scale | No | — |
| Pass / tier-placement rule | No | The README says only "Your submission will be evaluated based on…". |
| Automated tests | No | No `tests/`, contract or hidden tests. |
| Reproducibility check | No | — |
| Oral / walkthrough defence | No | It is the single most effective defence against outsourced work, and it is absent. |
| Integrity controls | No | Public PR submissions expose all prior work. There is no AI-use declaration and no plagiarism check. |
| Peer review | Mentioned | The "Review Period" lists "Peer Review" with no procedure. |

Criteria such as "Innovation: Novel approaches" and "Impact: Memorable and effective" are not observable without anchors, so they favour presentation polish over substance.

## 11. Sub-track coverage

The new Intelligence Track has three sub-tracks with 39 units in total. Legacy coverage, mapped by the migration map:

| New sub-track | Units with ≥1 legacy source task | Units with no legacy source |
|---|---|---|
| Data Science (12 units) | DS-03, DS-04, DS-05, DS-06, DS-08, DS-09, DS-10, DS-11 (thin), DS-12 (thin) | **DS-01** (Python and wrangling as a skill in itself), **DS-02** (data acquisition, APIs, sourcing), **DS-07** (SQL, entirely absent) |
| ML Engineering (14 units) | ML-01, ML-02, ML-03 (one task), ML-04, ML-05, ML-06, ML-07, ML-08, ML-11, ML-12 (one Pro task), ML-13 (one Pro task) | **ML-09** (time-series ML), **ML-10** (recommender and ranking systems), **ML-14** (responsible ML: fairness, interpretability, robustness; SHAP is a hint in one task) |
| AI Engineering (13 units) | AI-02 and AI-10 and AI-11 (only by replacing outdated generation tasks), AI-04 (Novice text similarity as a bridge), AI-12 (Pro fine-tuning) | **AI-01, AI-03, AI-05, AI-06, AI-07, AI-08, AI-09, AI-13**: LLM applications, model APIs and local inference, RAG, agents and tool calling, orchestration, context and memory, multimodal, production AI architecture and cost |

**Specific absences**

- **AI Engineering and LLM applications.** The most in-demand competency in 2026 is missing entirely. The closest tasks (Pro NLP T1 and T3) fine-tune BERT/GPT-2 and treat prompting as an optional hint.
- **MLOps.** Experiment tracking, model registry, CI for ML and drift monitoring are packed into one Pro GML task alongside a feature store and an A/B framework. No lower tier builds towards it.
- **Deployment and serving.** "Deploy demo application" and "Create deployment package with API" appear as single bullets in Pro tasks. There are no latency/throughput SLOs, containerisation requirements or rollback criteria.
- **Data engineering.** Pipelines, scheduling, data contracts, idempotency and incremental loads are absent.
- **SQL.** Not one query is required anywhere in the 63 tasks.

## 12. Tier consistency

- **Same label, different bar.** "Pro" means a bounded analysis in Pro DS T1, a research replication in Pro DL T3, and a full product in Pro DA T1.
- **Thresholds run in the wrong direction.** Intermediate DL T1 requires ">85% for MNIST", Intermediate GML T1 ">85% accuracy", Intermediate NLP T1 ">80% accuracy", and Pro CV T3 ">85% on CIFAR-10/100". The bar does not track difficulty: CIFAR-100 at 85% is far harder than CIFAR-10 at 85%, and MNIST at 85% is trivial.
- **Domain names overlap.** "Data Science" vs "Data Analytics" vs "Data Visualization" and "Deep Learning" vs "Computer Vision" vs "NLP" overlap heavily. Transfer learning sits under Deep Learning, CNN classification is in DL rather than CV, and causal inference is in DS while A/B testing is in DA.
- **Evaluation criteria change per file without a rationale.** "Testing" appears only for Novice NLP, "Practicality" only for Novice DA, and "Scalability" only for Pro.

## 13. Technical accuracy and feasibility

| Location | Issue | Why it matters |
|---|---|---|
| Intermediate DL T1 | ">85% for MNIST, >60% for CIFAR-10" | A linear classifier reaches roughly 92% on MNIST, so 85% fails to show a CNN learned anything. Thresholds must be justified against a baseline and checked against a reference implementation. |
| Intermediate GML T1 | "Achieve >85% accuracy" with no dataset | It is meaningless without a dataset and class balance: 85% can be below the majority-class rate. |
| Intermediate NLP T1 | ">80% accuracy" | Same issue. It also ignores class imbalance, where macro-F1 is the appropriate metric. |
| Pro CV T1 | ">70% mAP on validation set" | No dataset, IoU definition (mAP@0.5 vs mAP@[.5:.95]) or class count is given. On a custom set the candidate controls the difficulty. Requires GPU training of YOLO/Faster R-CNN. |
| Pro CV T2 | ">75% mean IoU" on Cityscapes/ADE20K, plus CRF refinement | Requires multi-GPU-hour training and large downloads (Cityscapes needs registration and has a non-commercial licence). CRF post-processing is largely obsolete for modern segmenters. Not feasible on a student laptop. |
| Pro CV T3 | ViT "implement" and ">85% on CIFAR-10/100" | From scratch, a small ViT needs heavy augmentation and long schedules to reach 85% on CIFAR-10. The hint "Use pre-trained weights when available" makes it trivial. Both readings fail. |
| Pro NLP T1 | "Achieve state-of-the-art or near SOTA results" | Cannot be verified, and leaderboards move monthly. It encourages benchmark chasing over analysis. |
| Pro DS T3 | "Top 10% on public leaderboard equivalent" | Cannot be verified for past competitions. Late submissions rank against a shifted field. |
| Intermediate CV T1 | Lists SURF | SURF is patented and only in the OpenCV non-free contrib build. ORB, AKAZE or SIFT (patent expired 2020, now in main OpenCV) are the right options. |
| Pro DA T2 | "PyMC3" | Renamed and superseded by PyMC (v4+, 2022). |
| Pro NLP T3 / Intermediate NLP T3 | Char-RNN/LSTM generation, "GPT-2/GPT-3-style model", attribute-classifier guided decoding | Historically interesting, but no longer how text generation is built or assessed. Evaluation of LLM output (groundedness, rubric judges, human eval protocols) is the relevant skill. |
| Pro CV T1 | YOLOv5/v8 via Ultralytics | Ultralytics code and weights are AGPL-3.0, which constrains deployment. Candidates should be told the licence implications. |
| Pro DL T2 | "TensorRT", "optimize for target hardware" | Needs NVIDIA hardware. A CPU path (ONNX Runtime, PyTorch dynamic quantisation) should be first-class. |
| Novice DL T1 | Single-layer perceptron "on AND/OR" and "visualize decision boundary" | Fine, but it should also show XOR failing, which is the lesson that motivates hidden layers. |
| Novice NLP T2 | "Test on at least 10 sample texts. Report accuracy" | Accuracy on 10 hand-picked texts has a 95% interval about ±30 points wide. It teaches the wrong lesson about evaluation. |
| Intermediate DS T1 | "Save final model for deployment" with pickle | Pickle is unsafe to load from untrusted sources. Formats and versioning should be specified (skops/ONNX, model card). |

## 14. Missing competencies

Beyond the sub-track gaps in §11, these cross-cutting competencies are not assessed anywhere:

1. **Problem framing:** turning a vague stakeholder need into a measurable question, a metric and a decision.
2. **Data provenance and licensing:** knowing whether you are allowed to use the data, and citing it.
3. **Data leakage detection:** target leakage and train/test contamination (e.g. Bank Marketing's `duration` field) are never raised.
4. **Baselines:** only a few tasks say "compare with baseline", and none define one.
5. **Uncertainty communication:** confidence intervals appear in DA tasks, but not for ML metrics.
6. **Software engineering for data:** tests, packaging, typed interfaces, CLI entry points, environment pinning.
7. **Privacy and ethics:** NDPA 2023 obligations, de-identification, consent, and the ethics of scraping. Only Pro NLP T3 hints at "ethical implications".
8. **Responsible AI:** fairness metrics, interpretability methods, robustness and red-teaming.
9. **Cost and resource awareness:** compute budgets, API costs, latency budgets, which matter acutely for members on shared or CPU-only hardware.
10. **Oral explanation:** defending design decisions live.

## 15. Redundancy

| Cluster | Legacy tasks | Recommendation |
|---|---|---|
| Feature engineering | Novice DS T3, Intermediate GML T2, Pro DS T2, Novice GML T3 (preprocessing) | Consolidate into ML-04 with one task per tier that differs in kind (leakage-safe pipeline → method comparison under CV → feature-store and drift design). |
| Ensembles / stacking | Intermediate GML T1, Pro GML T2, Pro DS T3 | Keep one ensemble task in ML-02. Retire the "10+ base models" and leaderboard versions. |
| Dashboards | Novice DV T3, Intermediate DV T2, Pro DV T1 | Every dashboard must answer a stated decision question (DS-06). Real-time engineering moves to DS-11. |
| Storytelling | Intermediate DV T3, Pro DV T3 | Keep one in DS-06 (T2) and one in DS-12 (T3, reproducible research communication). |
| EDA / descriptive analysis | Novice DS T1, Novice DA T1 | Merge into DS-04 with a fixed dataset and question. |
| Predictive modelling basics | Novice DS T2, Intermediate DS T1, Intermediate DS T3 | Split cleanly between ML-02 (models), ML-05 (validation) and DS-09 (decision value). |
| Neural network fundamentals | Novice DL T1, T2, T3 | Merge into one from-scratch MLP task with an XOR, activation and gradient-check component. |

## 16. Outdated resources and practices

- **Libraries:** PyMC3 (→ PyMC), SURF (non-free), TensorRT-only optimisation, YOLOv5 (superseded; AGPL), GPT-2/GPT-3-style generation, char-LSTM language models, CRF post-processing for segmentation, and Featuretools as the default feature-generation path.
- **Datasets:** MNIST and CIFAR-10 as the default image benchmarks. Both are saturated, and CIFAR-10 has no explicit licence (see `shared/datasets/DATASET_REGISTRY.md`). Cityscapes and ADE20K come with registration and non-commercial terms. No dataset links are given anywhere.
- **Practices:** notebook-only submissions; accuracy as the default metric; "deploy" with no definition; no environment pinning; no AI-assistant use policy, which in 2026 is mandatory for any take-home assessment.
- **Resources sections** contain no URLs, so there is nothing to check for link rot, but nothing to learn from either.

## 17. Valuable ideas to carry forward

| Idea | Legacy source | Where it lands |
|---|---|---|
| Implement-from-scratch, then compare with a library | Novice GML T1–T2, Novice DL T3 | ML-01, ML-02, ML-06 Tier 1 |
| Power analysis, practical vs statistical significance, multiple testing | Intermediate DA T1 | DS-08 |
| Sample-ratio-mismatch checks, A/A tests, variance reduction (CUPED), sequential testing | Pro DA T1 | DS-08 Tier 3, extracted from the platform scope |
| Cohort retention heatmaps normalised for cohort size | Intermediate DA T2 | DS-09 |
| Causal checks: overlap, balance, placebo, sensitivity | Pro DS T1 | DS-08 Tier 3 |
| Nested CV and comparison of tuning strategies under a fixed budget | Intermediate GML T3 | ML-05 |
| Adversarial validation and CV-strategy design | Pro DS T3 | ML-05 Tier 3 |
| Controlled optimiser and regulariser study (same architecture, logged curves) | Intermediate DL T2 | ML-06 Tier 2 |
| Quantisation, pruning, distillation with accuracy retention and p50/p95 latency | Pro DL T2 | ML-11 / ML-12 |
| Drift detection, model cards, CI tests for models | Pro GML T3 | ML-13 |
| Low-resource, multi-script, cross-lingual transfer | Pro NLP T2 | ML-08 Tier 3 with MasakhaNER 2.0 / AfriSenti |
| Toxicity filtering, factuality checks, "document failure modes" | Pro NLP T3 | AI-10 / AI-11 |
| From-scratch transformer with attention visualisation | Pro DL T1 | ML-06 Tier 3 (CPU-scale) |

## 18. Recommendations

1. **Do not reuse task text verbatim.** Rewrite each retained idea against the new authoring standard: README sections A–K, `metadata.yaml`, a rubric with level descriptors, tests where code is involved, and a kit-side marking guide.
2. **Fix a dataset and a contract for every Tier 1 and Tier 2 assessment**, drawing on the verified registry (`shared/datasets/DATASET_REGISTRY.md`) or deterministic synthetic generators.
3. **Justify and check every numeric threshold** against a baseline and a reference solution.
4. **Separate public and assessor material.** Use the private assessor kit for references, hidden tests and calibration exemplars, and accept submissions through a channel that does not expose them to other candidates.
5. **Remove personal contact details** and event logistics from permanent documentation (NDPA 2023, data minimisation).
6. **Build AI Engineering from first principles.** The legacy bank supplies only bridging ideas (text similarity → embeddings; generation → evaluation and guardrails; fine-tuning → PEFT).
7. **Make every assessment feasible on CPU with 8 GB RAM**, with an explicit free-tier Colab or Kaggle path where GPU training genuinely adds value.
8. **Add a short oral walkthrough** to every Tier 2 and Tier 3 placement decision.
