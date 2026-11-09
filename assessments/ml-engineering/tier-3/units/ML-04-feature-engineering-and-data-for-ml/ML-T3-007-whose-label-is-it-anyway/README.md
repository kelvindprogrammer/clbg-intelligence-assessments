# ML-T3-007: Whose Label Is It Anyway?

> *Four field agents labelled 1,200 cassava leaves, each wrong in a different way. You have 60 expert labels, a budget for 150 more, and a model to ship.*

![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-007` |
| **Title** | Whose Label Is It Anyway? Spending a Relabelling Budget on Noisy Cassava Disease Annotations |
| **Subtrack** | Machine Learning Engineering |
| **Tier** | 3: Advanced Practice and Research Thinking |
| **Unit** | [ML-04: Feature Engineering and Data for ML](../README.md) |
| **Format** | Open-ended (secondary: Investigation, Optimization) |
| **Difficulty** | Technical 4 · Mathematical 3 · Research 4 · Engineering 3 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 24-40 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | CPU only, 4 GB RAM, no GPU, no paid services, no internet after setup. The whole suite runs in about a minute |
| **Recommended prerequisites** | Solid experience with scikit-learn classification and cross-validation; ideally [ML-T1-009](../../../../tier-1/units/ML-04-feature-engineering-and-data-for-ml/ML-T1-009-maize-yield-without-peeking/README.md) and [ML-T2-007](../../../../tier-2/units/ML-04-feature-engineering-and-data-for-ml/ML-T2-007-the-too-good-credit-model/README.md) or equivalent. |
| **Skills developed** | Label-noise estimation; out-of-fold diagnostics; annotator analysis; budgeted relabelling; robust training; evaluation under scarce trusted labels |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

An agricultural extension programme trains field agents to photograph cassava leaves and label them as healthy, cassava mosaic disease or cassava brown streak disease. A vision model turns each photo into a 12-number embedding; 1,200 leaves have been labelled by four agents. A disease-detection model will be trained on these labels and used to advise farmers about quarantine and replanting, where a wrongly reassuring answer lets a disease spread and a wrongly alarming one destroys a healthy field's planting material.

The programme knows its labels are noisy but not how noisy or where. Agent 0 is a senior pathologist's trainee; the others vary. There are expert labels for only 60 leaves and the budget allows an expert to review about 150 more. A programme officer asks four questions: how bad is the noise overall and per agent, which labels should the experts look at first, how good can the model be if no more money is spent, and what should be done differently in the next round of collection.

There is no single correct pipeline. You must choose how to detect suspicious labels, how to use the annotator identity, how to spend the budget (by confidence, by annotator, by class), how to train given noisy and partially corrected labels, and how to evaluate when trusted labels are scarce and you must not tune on them. Your methods are then run by assessors on re-seeded leaf sets, where the truth and a large clean test set are held back.

---

## C. Objectives

When you finish, you should be able to show that you can:

- Estimate overall and per-annotator label-noise rates from noisy data and a small trusted sample, with assumptions stated.
- Use out-of-fold predictions to rank suspicious labels and explain why in-sample predictions would hide noise.
- Allocate a relabelling budget and compare allocation strategies using experiments with known truth.
- Train a classifier that degrades gracefully under label noise and measure the benefit honestly.
- Distinguish random noise from systematic annotator bias and recommend changes to the labelling process.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the functions in `label_lab/core.py`; stubs raise `NotImplementedError("R<n>: ...")`. `load_labels` is provided. Model choices are yours but must be justified.

| # | Requirement |
|---|---|
| R1 | `oof_proba(X, y, n_splits, seed)`: stratified out-of-fold class probabilities, so every row is scored by a model that never saw it. |
| R2 | `estimate_noise(X, y, annotator, seed)`: estimated mislabel rate overall and per annotator, working from `(X, y, annotator)`. The 60 expert labels may be used to check or calibrate but not required. |
| R3 | `select_for_relabel(X, y, annotator, budget, seed)`: the `budget` labels you would send to an expert, most suspicious first, unique indices. |
| R4 | `fit_robust(X, y, annotator, seed)`: a classifier trained to be accurate on clean data despite the noise in `y`. |

The report must also contain: (a) a **simulation study** on data you generate yourself with known noise (you may adapt the public embeddings' structure) comparing at least three relabelling strategies at several budgets; (b) a **noise-model comparison**: random (symmetric) noise versus class-conditional versus annotator-conditional assumptions, and what each implies for your estimates; (c) the effect of the 60 expert labels used three ways (calibration, extra training data, held out for evaluation) with the leakage risk of each stated; (d) a recommendation for the next collection round.

### D.2 Engineering requirements (mandatory)

- `pytest` passes from a clean environment built from `requirements.txt`; numpy and scikit-learn only.
- Expert labels must never be used both to tune a method and to report its accuracy; the report states which role they played in each experiment.
- All experiments are seeded and `experiments.py` regenerates every table in under 15 minutes on a laptop.
- At least 8 tests of your own in `tests/test_member_*.py`, including a regression test on a simulated dataset with known noise.

### D.3 Privacy and responsibility

The data are synthetic and describe no real farmer or field agent. In a real programme, per-annotator error rates are performance information about identifiable people and must be handled with the same care as staff evaluations: use them to improve training and guidance, not to penalise individuals without review. Also state the harm model of the application: which error (missed disease or false alarm) costs more for a smallholder, and how that should shape thresholds.

### D.4 Optional enhancements (not required for full marks)

- Compare your selection with a method that uses a different base model (for example a random forest) and explain any difference in which labels are flagged.
- Estimate the class-conditional transition matrix of each annotator and show whether it is stable across seeds.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/leaf_labels.csv`](resources/data/leaf_labels.csv): 1,200 leaves with annotator, 12 embedding features and a noisy label (about 105 KB); [`resources/data/expert_gold.csv`](resources/data/expert_gold.csv): 60 expert labels |
| **Provenance** | **Synthetic**, generated with a fixed seed by a generator in the assessor kit (it holds the clean labels and a clean test set). Four annotators with different error patterns are simulated. No real photos or people |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Hidden evaluation** | Re-seeded leaf sets with known truth and a 1,500-leaf clean test set |
| **Setup** | `pip install -r starter/requirements.txt` (numpy, scikit-learn, pytest) |

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `label_lab/` package (completed starter) | R1-R4 |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Pins behaviour and checks methods on simulated truth |
| 3 | `experiments.py` and saved result tables | Simulation study, noise-model comparison and expert-label roles |
| 4 | `REPORT.md` (at most 2,000 words plus tables) from the [template](submission-template/REPORT.md) | Answers to the programme officer, trade-offs and AI-use declaration |
| 5 | A 10-minute live defence | Verifies understanding (section K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Criteria marked (auto) are checked by the public and hidden test suites; the rest are checked by hand.

1. (auto) All public tests pass from a clean environment, and your own tests pass.
2. (auto) Out-of-fold probabilities are genuinely out of fold; the overall noise estimate agrees with the expert sample within 0.09 on the public data and within 0.05 of the truth on hidden sets. *Justification:* with 60 expert labels the sampling error is about 0.04-0.08; the hidden bound is looser than a perfect estimator would need because the reference is within 0.03.
3. (auto) On hidden sets, the best and worst annotators are identified correctly.
4. (auto) Of 150 selected labels, at least 60% are truly wrong on hidden sets, against a base rate of about 11%. *Justification:* the reference reaches 74-81% (a lift of about 7); 60% leaves room for different base models.
5. (auto) Relabelling your selection and then calling `fit_robust` raises clean-test accuracy by at least 0.8 points on average over three hidden sets, and `fit_robust` alone is not worse than the naive model. *Justification:* the reference gains about 1.0 to 2.6 points; the effect is deliberately modest because the classes are learnable and logistic regression is partly noise-tolerant.
6. The report contains the simulation study, the noise-model comparison and a statement of how the expert labels were used in each experiment without leaking into evaluation.
7. The report gives the officer a recommendation for the next collection round that is supported by your per-annotator evidence and flags what the evidence cannot show.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 15 |
| Implementation quality | 5 |
| Methodology and experimentation | 25 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 5 |
| Critical thinking and limitations | 20 |
| Presentation and communication | 10 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, reproducible results and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T3-007-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders into it.
2. **Expected structure:**
   ```text
   clbg-ML-T3-007-<username>/
   ├── requirements.txt
   ├── label_lab/           # your package
   ├── tests/               # provided tests + your test_member_*.py
   ├── resources/           # unchanged
   ├── experiments.py
   ├── results/             # tables quoted in the report
   └── REPORT.md
   ```
3. **Commit as you work.** A single "final" commit containing everything will be questioned at defence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** set by the cohort coordinator. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback but never stand in for the core requirements.

1. **Budget curves.** Plot clean accuracy against relabelling budget for each strategy and locate the point of diminishing returns.
2. **Transition matrices.** Estimate each annotator's confusion matrix and use it to correct labels probabilistically rather than discarding them.
3. **Active loop.** Relabel in batches of 30, retrain between batches, and compare with a single batch of 150.
4. **Cost-sensitive thresholds.** If a missed disease costs five times a false alarm, how do you change training and decision thresholds under noisy labels?

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration inside `REPORT.md`. Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** adapted code with a link. **Collaboration** is limited to general techniques; never share code, numbers or report text.
- **How understanding is verified.** In a short defence the assessor will:

1. Explain why a model trained on noisy labels can look worse than it is on a noisy test set, and how you avoided that in evaluation.
2. Defend your relabelling selection: why these 150, and what would you do with a budget of 30 or 600?
3. Handle an unseen modification live, such as a fifth annotator with no history, or a sudden change that annotator 2 only mislabels one class.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Classification, cross-validation, confusion matrices and the idea of label noise. |
| **New skill developed** | Treating labels as measurements with errors, and engineering the data (not only the model) under a budget. |
| **Decisions the member must make** | The noise model, the suspicion score, the use of annotator identity, the budget allocation, the training strategy and the role of the 60 expert labels. |
| **What must be investigated independently** | How noise is structured, which agents are unreliable and in what way, and which strategy wins at which budget in simulation. |
| **Why it is interesting** | In applied ML the cheapest improvement is often better labels, and the question of where to spend scarce expert time is a real operational decision. |
| **Evidence of competence** | Accurate noise estimates and selection precision on hidden truth, measurable accuracy gain, and a report that never evaluates on the data it tuned on. |
| **Misconceptions exposed** | "Test accuracy on noisy labels is the truth." "Noise is random." "In-sample confidence finds mislabels." "More labels always beat better labels." |
| **Preparation for later work** | Leads to data-centric workflows, evaluation under weak supervision, and the monitoring and governance of labelling pipelines. |

**Suggested approach**, for members who want guidance (you may ignore it):

1. Build a simulator with known noise first; develop every method on it.
2. Implement the out-of-fold score and look at which labels it flags per annotator.
3. Compare allocation strategies at several budgets in simulation before touching the budget decision on the real file.
4. Keep a log of which data each number was tuned on.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
