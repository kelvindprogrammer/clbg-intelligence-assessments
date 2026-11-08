# ML-T1-011: The Triage Scorecard

> *Build the metrics from scratch, then discover why 89% accuracy means nothing.*

![Format: Implementation](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T1-011` |
| **Title** | The Triage Scorecard: Building an Honest Evaluation Kit for a Malaria Risk Score |
| **Subtrack** | ML Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [ML-05: Evaluation, Validation and Model Selection](../README.md) |
| **Format** | Implementation |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 8–14 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | Python modules, numpy arrays, the definitions of precision, recall and the confusion matrix, running `pytest`. |
| **Skills developed** | Metric implementation; tie handling in ranking metrics; grouped cross-validation; operating-point selection; calibration |
| **Technologies** | Python 3.10+, numpy, pandas, scikit-learn (as a test oracle only), pytest |

---

## B. Problem Statement

A state primary-health programme in southern Nigeria has deployed a small **risk score** in 40 community clinics. For each patient with fever, a health worker enters a few observations and the tool prints a number between 0 and 1: the higher the number, the more likely the patient has malaria and should be sent for a confirmatory test first. The programme's data officer has a CSV of **733 past patients** with the printed score and the confirmatory result. A manager has seen a slide that says "**the tool is 89% accurate**" and wants to roll it out to 400 clinics.

You are the programme's new ML engineer. Before anyone decides anything, you must build a small, trustworthy **evaluation kit** and use it to answer four questions: how good is the score at ranking sick patients above healthy ones, what threshold would catch 90% of true cases and at what cost in false alarms, whether the printed numbers can be read as probabilities, and how the score should be cross-validated when patients from the same household share risk factors and cannot be treated as independent.

Importing `sklearn.metrics` would make this trivial and teach little. The point of this assessment is to implement each metric from its definition, find out where the textbook formula meets awkward reality (the score is coarse, so **many patients tie**), and demonstrate that your implementation agrees with a trusted oracle to numerical precision.

## C. Objectives

When you finish, you should be able to show that you can:

- Implement confusion-matrix metrics, ROC AUC and average precision from definitions, handling tied scores correctly.
- Explain, with numbers from the data, why accuracy is a poor headline metric at 11% prevalence.
- Build a stratified, group-aware k-fold splitter that never splits a household across train and test.
- Select an operating threshold that satisfies a clinical recall constraint and report its cost.
- Measure calibration with expected calibration error (ECE) and say what the number does and does not tell the programme.
- Verify numerical code against an independent oracle and write your own edge-case tests.

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `evalkit` package in [`starter/evalkit/`](starter/evalkit/). Signatures are fixed. Use **numpy and pandas only inside the package** (`sklearn` and `scipy` imports are rejected by a test). `y_true` is a 0/1 array; scores are floats.

| ID | Requirement |
|---|---|
| **R1** | `confusion_counts(y_true, y_pred) -> (tp, fp, fn, tn)` as Python ints. |
| **R2** | `precision_recall_f1(y_true, y_pred) -> dict` with keys `precision`, `recall`, `f1`, `specificity`, `accuracy`. A zero denominator gives `0.0`, never `nan` or an exception. |
| **R3** | `roc_auc(y_true, scores) -> float` using the rank (Mann-Whitney) formulation with **average ranks for ties**. Raise `ValueError` if only one class is present. |
| **R4** | `average_precision(y_true, scores) -> float` as the step-wise sum `sum_n (R_n - R_{n-1}) P_n` over distinct score thresholds (tied scores form one threshold). |
| **R5** | `stratified_group_kfold(y, groups, k, seed=0)` returns `k` pairs of index arrays `(train_idx, test_idx)`. Each group is wholly inside one test fold, each row is in exactly one test fold, positives are spread so that fold positive counts differ by at most 3 on the provided data, and the result is deterministic for a seed. |
| **R6** | `threshold_for_recall(y_true, scores, target_recall)` returns the **largest observed score** `t` such that predicting positive when `score >= t` reaches the target recall. |
| **R7** | `expected_calibration_error(y_true, prob, n_bins=10)` with equal-width bins on [0, 1]; a probability of exactly 1.0 belongs to the last bin; empty bins contribute nothing. |
| **R8** | `run_report(df, recall_target=0.9, k=5, seed=0) -> dict` and the command `python -m evalkit <csv> --out <dir>` writing `metrics.json` (sorted keys). The keys are listed in the starter docstring and include AUC, average precision, ECE, the threshold with its precision and recall, `accuracy_always_negative`, and the positives per household-grouped fold. |

### D.2 Engineering requirements (mandatory)

- Use vectorised numpy where it is natural; loops over unique score values are acceptable at this data size.
- Keep the provided tests passing and add **at least 6 tests of your own** in `tests/test_member_*.py`. At least two must be edge cases you found yourself (for example, all scores tied, or a single-positive fold).
- No mutation of the input arrays or DataFrame. Same input and seed give byte-identical `metrics.json`.
- `REPORT.md` numbers must be reproducible by running `python -m evalkit resources/data/triage_scores.csv --out outputs/`.

### D.3 Privacy and responsibility

The data is **entirely synthetic**; no real patient is described. Treat the *pattern* as you would real health data under the Nigeria Data Protection Act 2023: health information is sensitive personal data, so you would minimise columns, restrict access, and never paste records into public tools. In `REPORT.md` write two sentences on what would change if these were real clinic records, and one on why a model that is "89% accurate" could cause harm if it silently misses sick patients.

---

## E. Dataset and Resources

All data is **synthetic**, produced by a deterministic generator held in the assessor kit (seed fixed; re-seeded data is used by the hidden tests). It contains fictional patients only.

| File | Content |
|---|---|
| [`resources/data/triage_scores.csv`](resources/data/triage_scores.csv) | 733 rows, 170 households: `patient_id, household_id, age, fever_days, y_true, risk_score`. About 11% positive. `risk_score` is rounded to two decimals, so ties are common and deliberate. 17 KB. |

Households share exposure, so outcomes within a household are correlated. Licence: CC BY 4.0. Setup needs internet once only to install `requirements.txt`. The tests use `scikit-learn` as an oracle.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `evalkit/` (completed starter) | The core technical evidence |
| 2 | `tests/test_member_*.py` (at least 6 tests) | Edge cases and regression guards |
| 3 | `outputs/metrics.json` | Machine-readable results from the provided data |
| 4 | `REPORT.md` from the [template](submission-template/REPORT.md) (at most 900 words plus tables) | Answers the four questions for the programme manager; includes the AI-use declaration |
| 5 | A short live defence | Verifies understanding (§K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Criteria marked ⚙ are checked automatically by the public and hidden test suites; the rest are checked by hand.

1. ⚙ All provided public tests and your own tests pass from a clean environment.
2. ⚙ `roc_auc` and `average_precision` agree with `scikit-learn` to `1e-12` on tied and untied data. *Justification:* both are exact computations, so any larger gap is a defect, not noise.
3. ⚙ Grouped folds never split a household and fold positive counts differ by at most 3 (provided data). *Justification:* the largest household holds 3 positives, so no assignment can be guaranteed tighter than that; the reference achieves a spread of 1.
4. ⚙ The recall threshold reaches the target and is the largest observed score that does so.
5. ⚙ The hidden tests, run on freshly seeded data with different household structure, also pass.
6. ✍ `REPORT.md` states AUC, AP, the 90%-recall threshold with its precision, ECE, and explains in plain language why the 89% accuracy claim is uninformative (include the always-negative baseline).
7. ✍ The report shows, with a count from your own splitter versus a naive random split, how many households would straddle train and test, and says why that matters.
8. ✍ Every number in the report is regenerated by the submitted code.

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

1. **Create your own private repository** named `clbg-ML-T1-011-<your-github-username>` from this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `evalkit/` (your package), `tests/` (provided tests plus your own `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `outputs/metrics.json`, `REPORT.md` (from the template, including the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core requirements.

1. Add a bootstrap confidence interval for AUC that resamples **households**, not patients, and compare its width with the naive interval.
2. Implement a reliability diagram data function and a debiased ECE; discuss why equal-width bins mislead when most scores sit below 0.2.
3. Add a decision-curve (net benefit) function and recommend a threshold for a clinic that values a missed case at 10 false alarms.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn (explain a concept, review your code). **They may not do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: tool, purpose, example prompt, how you verified the output. Undisclosed use that emerges at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code or method adapted from documentation or papers, with a link.
- **Collaboration:** discuss *general techniques* only. Do not share code, numbers or report text.
- **Verification of understanding.** In the short defence the assessor will ask you to (1) compute AUC by hand for a five-patient table with one tie, (2) explain why your splitter produces the fold sizes it does, and (3) change `threshold_for_recall` live to return the **smallest** score that still meets a target precision instead.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python, numpy, and the definitions of precision, recall and the confusion matrix. No statistics beyond averages. |
| **New skill developed** | Treating evaluation as engineering: metrics derived from definitions, validated against an oracle, with ties and zero-denominators handled deliberately. |
| **Decisions the member must make** | How to handle ties, what a zero-division should return, how to balance folds while keeping groups intact, and which threshold convention is defensible. |
| **What must be investigated independently** | Why scikit-learn's value differs from a naive trapezoid or rank implementation on tied data, and how much leakage a naive split would allow. |
| **Why it's interesting** | A realistic health-programme decision hinges on a single slide, and the only way to challenge it is to rebuild the numbers. |
| **Evidence of competence** | Exact agreement with the oracle on tied and untied data, correct grouped folds on re-seeded households, and a report that explains the gap between accuracy and usefulness. |
| **Misconceptions exposed** | "Accuracy is the metric." "AUC ignores ties." "Stratified k-fold is enough." "A score between 0 and 1 is a probability." |
| **Preparation for later work** | Leads into ML-T2 model-selection work on time-ordered data and ML-T3 nested validation and leaderboard overfitting. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
