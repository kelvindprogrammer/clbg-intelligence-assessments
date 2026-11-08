# ML-T2-003: Forty Analysts, Two Hundred Alerts: Choosing Between Linear Models, Forests and Boosting Under an Alert Budget

> *A mobile-money fraud team can review only a few percent of transactions a day. Pick the model, the metric and the training window that catch the most fraud, without leaking the answer.*

![Format: Comparative (secondary: Investigation)](https://img.shields.io/badge/format-comparative-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-003` |
| **Title** | Forty Analysts, Two Hundred Alerts: Choosing Between Linear Models, Forests and Boosting Under an Alert Budget |
| **Subtrack** | ML Engineering |
| **Tier** | 2: Applied Competence |
| **Unit** | [ML-02: Supervised Learning and Ensembles](../README.md) |
| **Format** | Comparative (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14–20 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Logistic regression, decision trees, random forests and gradient boosting at the level of using scikit-learn; train/validation/test splits; precision and recall. Recommended: ML-T1-004 |
| **Skills developed** | Budget-constrained evaluation; leakage detection; time-based validation; model-family comparison under imbalance; deciding when to refit on recent data; defending a choice against a linear baseline |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Zamfara Pay (fictional) runs a mobile-money wallet across northern Nigeria. Fraudsters use stolen SIMs, new devices and quickly drained balances. The fraud team has 40 analysts. Together they can review only about **4% of each day's transactions**; every alert beyond that is ignored, and every fraud that is not in that 4% is paid out. The model's only job is to put as much fraud as possible in the daily top 4%.

You have 60 days of labelled transactions. About 1.4% are fraud. The fraud team's previous data scientist trained a logistic regression and reported 99% accuracy, which a model that never alerts would also achieve. A second proposal is a random forest, and a third is gradient boosting. Three complications are built into the data:

1. **Leakage.** One column was added by the chargeback system *after* fraud is confirmed. It is not available when a transaction must be scored. The data dictionary mentions it, but you are expected to detect such columns from data and reasoning, not by trusting names.
2. **Drift.** Fraudsters change tactics in the last third of the period. A pattern that occurred at night now occurs in the daytime. The data you train on does not fully contain the pattern you will be tested on.
3. **Imbalance and small counts.** There are only a few hundred positives overall, so validation estimates are noisy and selection can overfit the validation set.

You must build the evaluation honestly (time-ordered splits, the alert-budget metric), compare model families and imbalance remedies fairly, decide how to use the most recent data, choose a model, and write a short memo for the head of fraud operations. The task is partially specified: the tests fix interfaces and acceptance bars; the model family, features, imbalance handling and training window are yours to choose and defend.

> **Why this matters beyond this task.** Most production tabular ML is limited by an operational budget rather than by a generic metric, is evaluated on data from *after* the training period, and is easily corrupted by columns that carry the answer. Getting the evaluation right matters more than the model family.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Detect** target leakage from the data (and reason about availability at scoring time), and remove it without hard-coding a column name.
2. **Split** time-ordered data into train, validation and test periods with no look-ahead.
3. **Define** an evaluation metric that matches an operational budget (recall within the daily top-k) and compute it exactly, including tie handling.
4. **Compare** a linear baseline, bagging and boosting under imbalance, with imbalance remedies chosen on evidence.
5. **Decide** how to use recent data under drift (refit window, weighting) and show the effect with a controlled comparison.
6. **Quantify** the uncertainty of a selection made from few positive cases, and write a decision memo.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `alertmodel` in [`starter/alertmodel/`](starter/alertmodel/). Interfaces are fixed; modelling choices are yours. Use only numpy and scikit-learn.

| ID | Requirement |
|---|---|
| **R1** | `find_leaky_columns(X, y, names, auc_threshold=0.9) -> list[str]` returns the names of columns whose single-feature ROC-AUC (as `max(auc, 1 − auc)`, computed on the given data) exceeds the threshold. It must work for any column name and position. You must also document, in the report, why a threshold on AUC alone is not a sufficient leakage test. |
| **R2** | `time_split(day, train_end, val_end) -> (train_idx, val_idx, test_idx)`: train is `day < train_end`, validation is `train_end <= day < val_end`, test is `day >= val_end`. Each index array is sorted. No period overlaps another. |
| **R3** | `budget_recall(day, y, score, budget_frac) -> float`: for each day, flag the `ceil(budget_frac · n_day)` highest-scoring transactions (ties go to the earlier row); return the share of all positives that are flagged. `budget_precision(...)` returns the share of flagged transactions that are positive. |
| **R4** | `select_and_fit(X_train, y_train, X_val, y_val, day_val, names, budget_frac=0.04) -> model` returns an object with `predict_score(X)` (higher means riskier; accepts the full feature matrix including any leaky column and must ignore it), `chosen_` (the name of the chosen candidate), `report_` (a dict mapping at least three candidate names, one of which is `"logreg_baseline"`, to their validation `budget_recall`), and `dropped_` (the list of columns you removed as leaky). You decide the candidates, the imbalance handling, and whether and how the final model also uses the validation period. |

### D.2 Engineering requirements (mandatory)

- Deterministic: all estimators take explicit `random_state`s.
- Every candidate goes through the same code path for scoring and evaluation.
- No fitting, scaling, selecting or thresholding with data from the test period.
- At least **10 tests of your own** in `tests/test_member_*.py`, including a leak-injection test (add a column that copies the label and check it is dropped) and a look-ahead test (shuffle test-period rows and check scores are unchanged per row).
- `experiments.py` regenerates every number and figure in `REPORT.md`, including a comparison across **at least 5 different seeds** of the generator.

### D.3 Responsibility

The data is synthetic. In the report, write one paragraph on what a missed fraud and a false alert each cost a real customer (frozen wallet, delayed salary payment) and on how you would check for bias, for example whether alerts concentrate on customers in particular regions or with new SIMs only because the model learned a proxy.

### D.4 Optional enhancements

- A cost-weighted metric where a missed fraud costs a multiple of an analyst-minute.
- A drift monitor that flags the tactic change from the feature distributions alone.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_transactions(n=24000, seed=2026, days=60, leak_name="chargeback_flag")` returns `X, y, day, names` |
| **Provenance** | **Synthetic**, deterministic given the seed; no real transaction, customer or institution |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Columns** | `amount_ngn, hour, new_device, sim_age_days, txns_last_hour, new_recipient, agent_km, balance_ratio, channel` plus the post-hoc column |
| **Recommended split** | train days 0 to 39, validation days 40 to 49, test days 50 to 59 (the tests use this split) |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes a CSV of about 1.5 MB |
| **Feature dictionary** | `chargeback_flag` is described as "set when the cardholder disputes the transaction, up to 30 days later" |

Hidden tests use other seeds and a different name and position for the leaky column.

**Setup**

```bash
cd assessments/ml-engineering/tier-2/units/ML-02-supervised-learning-and-ensembles/ML-T2-003-forty-analysts-two-hundred-alerts
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `alertmodel/` package | Leak detection, splits, budget metric and model selection |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Includes leak-injection and look-ahead tests |
| 3 | `experiments.py` | Reproduces the comparison table (5 or more seeds) and figures |
| 4 | `REPORT.md` (at most 1,800 words plus tables), from the [template](submission-template/REPORT.md) | Decision memo for fraud operations; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `find_leaky_columns` returns exactly the leaky column on the official data, keeps legitimate strong features, and also works when the leaky column has another name and position (hidden test).
3. ⚙ `time_split` has no overlap and no look-ahead; `budget_recall` and `budget_precision` match hand-computed values, including ties and the ceiling rule.
4. ⚙ `report_` contains at least three candidates including `logreg_baseline`, `chosen_` is a key, and `dropped_` lists the leaky column.
5. ⚙ **Performance.** On the official test period (days 50 to 59) the chosen model's `budget_recall` at 4% is at least **0.55** and at least **1.4×** that of a standardised, class-balanced logistic regression trained on days 0 to 39. *Justification:* the reference reaches about 0.64 against a baseline of 0.35; the ceiling is about 0.7 because the fraud segments are themselves noisy.
6. ⚙ **Robustness.** On hidden seeds with a renamed leaky column the same bars hold with bars of 0.45 and 1.3× (test-period positives are few, so recall varies by about ±0.07 across seeds).
7. ⚙ **No leakage.** Replacing the leaky column in the test matrix with zeros, or shuffling the rows, does not change any row's score.
8. ✍ The report shows, with evidence, how much each of the following contributes: removing the leak, model family, imbalance handling, and using the most recent days for training.
9. ✍ The report states the uncertainty of the validation comparison (for example bootstrap over days) and explains how it influenced the choice.

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

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T2-003-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `alertmodel/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Cost-sensitive budget.** Replace the equal-weight metric with a cost that depends on amount, and show how rankings change.
2. **Calibration.** Calibrate scores and explain whether calibration matters for a top-k policy.
3. **Stacking.** Build a stacked ensemble of the three families and test whether it beats the best single model beyond the noise.
4. **Adversary.** Simulate fraudsters adapting to the top-4% policy, and propose a monitoring plan.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why your chosen model beat the baseline on validation and whether that margin is larger than the noise from about 60 validation fraud cases; (2) ask what you would do if the leaky column had been a legitimate but very strong feature; (3) give an unseen modification, for example a budget of 1% or a new drift month, and ask you to predict which choice changes.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Using scikit-learn classifiers; precision and recall; what a validation set is for. No ensemble theory. |
| **New skill developed** | Evaluating a model against the operational policy that will use it, on data from the future, with no leaked answers. |
| **Decisions the member must make** | Leak test and threshold; split dates; metric; candidates; imbalance handling; whether to refit on validation data; how to quantify the noise in the selection. |
| **What must be investigated independently** | How much of the baseline's weakness is model family versus drift versus leakage; the brief only names them. |
| **Why it is interesting** | The strongest improvement is not a bigger model: it is refitting on recent data, which the brief never suggests. |
| **Evidence of competence** | Test recall above the stated bar on re-seeded data; no change in scores under leak or shuffle tests; a decomposition of gains in the report. |
| **Misconceptions exposed** | '99% accuracy is good.' 'Random K-fold is fine.' 'More complex means better.' 'AUC near 1 means a great feature.' |
| **Preparation for later work** | Leads into ML-02 Tier 3 bias-variance studies, ML-06 evaluation and ML-10 drift monitoring. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
