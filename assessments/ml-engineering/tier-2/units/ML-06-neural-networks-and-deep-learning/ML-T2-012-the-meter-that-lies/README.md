# ML-T2-012: The Meter That Lies

> *A working network, a messy feeder dataset, and a training run that only looks fine.*

![Format: Optimization](https://img.shields.io/badge/format-optimization-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-012` |
| **Title** | The Meter That Lies: Training a Neural Network to Catch Prepaid-Meter Tampering |
| **Subtrack** | ML Engineering |
| **Tier** | 2: Applied Proficiency |
| **Unit** | [ML-06: Neural Networks and Deep Learning](../README.md) |
| **Format** | Optimization |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14–22 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | Neural-network training basics (ideally ML-T1-013), validation splits, precision-recall, pandas; no framework needed. |
| **Skills developed** | Preprocessing for networks; early stopping; imbalance handling; loss-curve diagnosis; honest comparison against a linear baseline |
| **Technologies** | Python 3.10+, numpy, pandas, scikit-learn, pytest |

---

## B. Problem Statement

A (fictional) distribution company in southern Nigeria loses a large share of energy to meter tampering: bypassed neutral lines, magnets and tokens re-loaded through illicit devices. Field inspections are expensive; each visit costs a crew-day. The revenue-protection team has **2,400 prepaid-meter records** with 11 monthly features per meter (consumption relative to the feeder, share of night consumption, voltage-sag events, neutral-current imbalance, token sizes and so on) and the outcome of past inspections: **about 8% were tampered**.

Management wants a neural network because a vendor promised one. Your data scientist predecessor tried a single hidden layer on the raw columns, saw the training loss fall, shipped the model, and later discovered that it flagged almost nothing. The tampering pattern is *interactive*: a meter is suspicious when consumption is low **and** neutral imbalance is high, or when night consumption is high **and** there are repeated sag events. A linear model sees only part of that, but a network needs the data prepared sensibly: the columns range from kilowatt-hours to naira tokens in the tens of thousands, and neutral imbalance has a heavy tail.

A working numpy MLP (`nn_core.MLP`, Adam optimiser, sample weights) is provided so you can focus on the *process*. You decide how to preprocess, how to hold out validation data, how to deal with the imbalance, what architecture and learning rate to use, when to stop, and how to read the loss curves. Your result is judged on a **fresh batch of 4,000 meters** against a tuned logistic-regression baseline, using average precision (PR-AUC), because only a few hundred meters can be inspected per month.

## C. Objectives

When you finish, you should be able to show that you can:

- Build leak-free preprocessing for skewed, differently scaled inputs, with rules derived from the training data.
- Train a network with a stratified validation split, early stopping and restoration of the best weights.
- Address class imbalance and justify the approach with evidence rather than habit.
- Diagnose underfitting, overfitting and instability from training and validation loss curves, and codify the rules.
- Compare the network with a strong linear baseline using precision-recall measures, and decide whether the network earns its complexity.
- Report which design choices mattered (ablation) and which did not.

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `meterfault` in [`starter/meterfault/core.py`](starter/meterfault/core.py). `nn_core.MLP` is provided and works (see its docstring). Signatures are fixed; choices inside them are yours and must be justified in `REPORT.md`. No deep-learning framework may be used.

| ID | Requirement |
|---|---|
| **R1** | `fit_preprocessor(train_df)` returns an object with `transform(df) -> ndarray (n, 11)`. It must standardise, tame heavy tails using rules *learned from the data* (not hard-coded column names), be fitted on training rows only, not mutate its input, and stay finite on new extreme values (for example a neutral imbalance of 500). |
| **R2** | `diagnose(history)` classifies a `{'train_loss': [...], 'val_loss': [...]}` history as `'unstable'`, `'underfit'`, `'overfit'` or `'ok'`. Define your rules (with thresholds and the reasoning for them) in `REPORT.md`. Non-finite losses are unstable. |
| **R3** | `fit_model(train_df, seed=0)` returns a `FittedModel` (see the starter docstring): stratified validation split (`val_idx`), preprocessing fitted on the non-validation rows, early stopping on validation log loss, restoration of the best epoch's weights (`best_epoch`), imbalance handling, unweighted log-loss `history`, `config`, and `predict_proba(df)` for raw frames. Deterministic for a seed. |
| **R4** | `analysis.py` that reproduces the report's tables: (a) the effect of preprocessing (raw versus prepared); (b) at least **three ablations** among imbalance handling, width/depth, learning rate and weight decay, each over at least 3 seeds with mean and spread; (c) the network versus a logistic-regression baseline on a held-out part of your own training data; (d) the `diagnose` output for at least three runs you deliberately made bad. |

### D.2 Engineering requirements (mandatory)

- Deterministic for a given seed; no test-time information in preprocessing, early stopping or threshold choices.
- Runtime of `fit_model` on the provided data under 2 minutes on a laptop CPU.
- Keep the provided tests passing and add **at least 6 tests of your own** (for example: a transform that must not re-centre on test data; a `diagnose` case at your boundary).
- Report average precision (PR-AUC) as the primary metric. If you mention accuracy, say why it is misleading here.

### D.3 Privacy and responsibility

The data is **synthetic**: no real customer or meter is described. Tampering flags have consequences for households and small businesses: an inspection can lead to fines or disconnection. In `REPORT.md`, state how a flagged customer should be treated (inspection first, never automatic penalty), which false-positive rate you consider acceptable, and what the Nigeria Data Protection Act 2023 would require regarding accuracy and the right to contest an automated decision.

---

## E. Dataset and Resources

All data is **synthetic**, generated by a deterministic generator in the assessor kit.

| File | Content |
|---|---|
| [`resources/data/meters_train.csv`](resources/data/meters_train.csv) | 2,400 meters: `meter_id`, 11 numeric features (two are pure noise), `tampered`. About 8% positive. 163 KB. |

Licence: CC BY 4.0. The hidden evaluation uses freshly generated meter populations with the same structure (the generator seed differs), so hard-coding anything about this file will not help.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `meterfault/` (completed starter, with the provided `nn_core.py`) | The training pipeline |
| 2 | `tests/test_member_*.py` (at least 6 tests) | Guards for leakage, early stopping and diagnosis rules |
| 3 | `analysis.py` or `analysis.ipynb` | Reproduces the ablations and comparison |
| 4 | `REPORT.md` (at most 1,800 words plus tables and curves), from the [template](submission-template/REPORT.md) | Design decisions, evidence, limits; includes the AI-use declaration |
| 5 | A short live defence | Verifies understanding (§K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Criteria marked ⚙ are checked automatically by the public and hidden test suites; the rest are checked by hand.

1. ⚙ Public and your own tests pass from a clean environment.
2. ⚙ The preprocessor yields mean 0 and standard deviation 1 on training data (tolerance 0.05) with absolute skewness below 1.5 per column, uses training statistics on other data, and does not mutate inputs.
3. ⚙ `diagnose` labels canonical healthy, overfitting, underfitting and unstable curves correctly, and a flat noisy validation curve as `ok`.
4. ⚙ `best_epoch` points at the minimum validation loss, the restored weights reproduce that loss to `1e-6` on `val_idx`, and the split is stratified within 0.02 of the overall positive rate.
5. ⚙ Hidden test, three fresh populations of 4,000 meters: PR-AUC is **at least 0.03 above** a balanced logistic regression on your own preprocessing, and **at least 0.40**. *Justification:* the reference reaches 0.49-0.56 and the baseline 0.37-0.42; 0.03 is a real but modest edge, and 0.40 is five times the base rate.
6. ✍ Ablations include spread over seeds and state clearly which changes are within noise.
7. ✍ The report explains your `diagnose` thresholds, shows the diagnosis of three deliberately broken runs, and says what you would do for each.
8. ✍ The report states whether the network justifies its complexity over the linear baseline for this utility.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 15 |
| Methodology and evidence | 15 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T2-012-<your-github-username>` from this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `meterfault/` (your package), `tests/` (provided tests plus your own `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `analysis.py` or notebook, `REPORT.md` (from the template, including the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core requirements.

1. Add an interaction-feature logistic regression (products of the two key pairs) and see how much of the network's edge disappears.
2. Choose an operating threshold for 300 inspections per month and report expected precision with an interval.
3. Implement a learning-rate schedule and show whether it improves validation loss without changing PR-AUC.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn (explain a concept, review your code). **They may not do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: tool, purpose, example prompt, how you verified the output. Undisclosed use that emerges at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code or method adapted from documentation or papers, with a link.
- **Collaboration:** discuss *general techniques* only. Do not share code, numbers or report text.
- **Verification of understanding.** In the short defence the assessor will give you a new broken training history and ask you to name the problem and the fix, ask why your preprocessor would fail if a new meter had zero consumption, and ask you to explain why PR-AUC rather than accuracy is the primary metric.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Mini-batch training of networks, validation splits, early stopping, PR curves, pandas. |
| **New skill developed** | Running a network training process as an engineering experiment: prepare, validate, stop, diagnose and compare against a strong baseline. |
| **Decisions the member must make** | Preprocessing rules for heavy tails, split design, imbalance handling, architecture and learning rate, stopping rule, diagnosis thresholds, and the verdict on network versus linear model. |
| **What must be investigated independently** | Which columns need which transform, whether weighting helps, and what the loss curves say about each run. |
| **Why it's interesting** | The data hides an interaction a linear model only partly sees, and a naive training run looks healthy while flagging nothing. |
| **Evidence of competence** | Beating a tuned linear baseline on fresh meters by a stated margin, restored-weights and leakage tests, and ablations with seed spread. |
| **Misconceptions exposed** | "Falling training loss means a working model." "Scaling is optional." "Accuracy is the metric." "A neural network always beats logistic regression." |
| **Preparation for later work** | Leads into ML-T3 research-style deep-learning studies and ML-11 experiment tracking and monitoring. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
