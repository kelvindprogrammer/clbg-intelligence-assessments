# ML-T2-001: When the Normal Equations Lie: Fitting a Feeder-Load Model on Collinear Sensor Data

> *A distribution company's hourly load regression is perfectly fit on last year's data and wildly wrong this season. Find out why, and choose a solver you can defend.*

![Format: Comparative (secondary: Investigation)](https://img.shields.io/badge/format-comparative-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-001` |
| **Title** | When the Normal Equations Lie: Fitting a Feeder-Load Model on Collinear Sensor Data |
| **Subtrack** | ML Engineering |
| **Tier** | 2: Applied Competence |
| **Unit** | [ML-01: Mathematical and Computational Foundations](../README.md) |
| **Format** | Comparative (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14–20 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Linear regression and the normal equations; matrix rank; SVD at the level of 'singular values measure stretch'; numpy.linalg; train/validation splits. Helpful: ML-T1-001 |
| **Skills developed** | Condition-number diagnosis; comparing normal-equation, QR, SVD and ridge solvers; regularisation strength selection by time-ordered cross-validation; separating numerical error from statistical error; defending method choices with evidence |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Ibadan Electricity Distribution Company (fictional) forecasts hourly load on a 33 kV feeder so it can schedule transformer loading and plan load-shedding fairly. The analyst who built the model fitted ordinary least squares by solving the normal equations, `(XᵀX) w = Xᵀy`, on the first 900 hours of data. In-sample the fit looked excellent. On the following 300 hours, when the weather turned hotter and the utility switched its heat-index sensor vendor, forecast errors reached more than 10 MW on a feeder that peaks near 40 MW.

The feature matrix has eight columns: temperature, humidity, a *heat index* derived from the first two, the previous hour's temperature, number of customers served (about 1.2 × 10⁵), the same customer count in thousands (rounded to one decimal), and sine/cosine of the hour of day. Several columns are near-duplicates of others, the scales differ by five orders of magnitude, and in the later period the heat-index feed carries far more noise than it did in training.

You are asked to find out *why* the model failed and to deliver a replacement you can defend. Three different things could be wrong, and the assessment is about telling them apart:

1. **Numerical error.** The solver loses digits when the problem is ill-conditioned (forming `XᵀX` squares the condition number).
2. **Non-identifiability.** Near-duplicate columns mean the data cannot say how to split a coefficient among them, even with exact arithmetic.
3. **Distribution shift.** The new heat-index sensor behaves differently from the one that produced the training data. No solver can remove that, but your choices determine how much damage it does.

You must decide the diagnostics, the solvers to compare, the preprocessing, how to choose regularisation without peeking at the future, and how to report all of it. The task is *partially specified on purpose*: the tests fix the interfaces and the acceptance bars, but the choices and their justification are yours.

> **Why this matters beyond this task.** Ill-conditioned regressions are common wherever engineered features are derived from each other (indices, lags, unit conversions). Telling a numerical problem from a statistical one is a core ML-engineering diagnostic skill.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Diagnose** ill-conditioning and near-collinearity using singular values, condition numbers before and after standardisation, and pairwise correlation.
2. **Implement** least-squares solvers by normal equations, QR, SVD and ridge, and show where each fails or succeeds on controlled problems.
3. **Separate** numerical error (an exact answer exists but is computed badly) from statistical error (the answer is not determined by the data) with experiments.
4. **Select** a regularisation strength with time-ordered validation that never uses future data.
5. **Compare** your model against the raw normal-equation baseline on held-out, shifted data, and quantify the improvement with a stated metric.
6. **Defend** every choice in writing, including what you tried and rejected, and the failure modes that remain.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `loadfit` package in [`starter/loadfit/`](starter/loadfit/). The interfaces are fixed by the tests; everything else is your design.

| ID | Requirement |
|---|---|
| **R1** | `diagnose(X, corr_threshold=0.999) -> dict` with keys `cond_raw` (2-norm condition number of `X`), `cond_standardised` (after centring and scaling each column to unit standard deviation, `ddof=0`), `rank_standardised` (numerical rank of the standardised matrix using the default tolerance `max(shape) * eps * s_max`) and `collinear_pairs` (sorted list of column index pairs `(i, j)`, `i < j`, with absolute correlation above the threshold). Constant columns must be handled without warnings. |
| **R2** | `solve(X, y, method="qr", lam=0.0) -> ndarray` for `method` in `"normal"`, `"qr"`, `"svd"`, `"ridge"`. `"normal"` solves `XᵀX w = Xᵀy`; `"qr"` uses a QR factorisation; `"svd"` uses the SVD pseudo-inverse with a relative cutoff of your choice (`rcond` keyword); `"ridge"` minimises `‖Xw − y‖² + lam‖w‖²` and must be computed without forming `XᵀX` explicitly. No intercept is added: callers handle that. |
| **R3** | `blocked_cv_lambda(X, y, lams, n_blocks=5) -> float` returns the element of `lams` with the lowest mean validation error under **expanding-window** validation: for `k = 1 … n_blocks−1`, fit on the first `k` blocks (standardising with statistics from those blocks only) and validate on block `k+1`. Rows are in time order. |
| **R4** | `fit_load_model(X, y) -> model` with `predict(X_new)`, attribute `lam_`, and `coef_`. Preprocessing, intercept handling, solver and regularisation are your choice. It must work on any feature matrix of this kind, not only the provided one. |
| **R5** | `compare_solvers(X_train, y_train, X_test, y_test) -> dict` mapping each of `"normal_raw"` (normal equations on raw columns with an intercept), `"lstsq_raw"` (`numpy.linalg.lstsq` on raw columns with an intercept) and `"fit_load_model"` to its test RMSE. |

### D.2 Engineering requirements (mandatory)

- Everything is deterministic given the data; no global random state.
- Preprocessing statistics come from training data only. A function that standardises the full matrix before splitting is a leakage bug.
- Provide at least **10 tests of your own** in `tests/test_member_*.py`, including at least two that fail if a solver is replaced by a naive one on an ill-conditioned problem.
- Provide `experiments.py` that regenerates every table and figure in `REPORT.md` from the generator, including a repetition over at least **10 seeds** for the solver comparison.

### D.3 Responsibility

The data is synthetic. In the report, discuss in one paragraph what a load-forecast error of 10 MW means operationally for a feeder serving a mixed residential and commercial area (unplanned shedding, transformer overload), and which of your safeguards you would insist on before deployment (for example a drift monitor on the heat-index feed).

### D.4 Optional enhancements

- A drift detector that flags the vendor change from the data alone.
- Compare ridge with truncated SVD and with simply dropping a collinear column, and explain when each is preferable.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_feeder(n_train=900, n_test=300, seed=2026, vendor_noise=0.6)` returns `X_train, y_train, X_test, y_test, names` |
| **Provenance** | **Synthetic**, deterministic given the seed. Mimics hourly weather and customer-count features for a fictional feeder; no real utility data |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Columns** | `temp_c, humidity, heat_index, temp_lag1, customers, customers_k, hour_sin, hour_cos` |
| **Shift built in** | The test period is 4 °C hotter and the `heat_index` feed has 600 times more noise than in training |
| **CLI** | `python resources/datagen.py --out DIR --seed 2026` writes `feeder_train.csv` and `feeder_test.csv` (about 100 KB) |

The official evaluation seed is 2026. Hidden tests use other seeds, a different `vendor_noise`, and a different pair of near-duplicate columns.

**Setup**

```bash
cd assessments/ml-engineering/tier-2/units/ML-01-mathematical-and-computational-foundations/ML-T2-001-when-the-normal-equations-lie
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `loadfit/` package | Solvers, diagnostics, model: the technical evidence |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Shows you can pin numerical behaviour down |
| 3 | `experiments.py` | Reproduces all numbers, including the 10-seed comparison |
| 4 | `REPORT.md` (at most 1,800 words plus tables), from the [template](submission-template/REPORT.md) | Diagnosis, comparison, decision and limits; includes the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `diagnose` returns a condition number matching `numpy.linalg.cond` to 1% and detects the near-duplicate columns without being told which.
3. ⚙ On an exactly solvable degree-9 polynomial problem, `qr` and `svd` recover the true coefficients to absolute error below `1e-6`, and `normal` is worse than `qr` by at least a factor of 50. *Justification:* the normal equations square a condition number near 10⁶, leaving about 4 correct digits; QR keeps about 10.
4. ⚙ `ridge` agrees with the closed form `(XᵀX + lam I)⁻¹Xᵀy` to `1e-8` on a well-conditioned problem.
5. ⚙ `blocked_cv_lambda` obeys expanding-window validation: its result is unchanged if the *last* block's targets are corrupted (no leakage into earlier folds), and it returns a member of `lams`.
6. ⚙ `fit_load_model` has test RMSE at most **1.3 MW** and at most **one quarter** of the `normal_raw` baseline on the official data. *Justification:* the noise floor is 0.7 MW; the reference reaches 0.82 MW against a 12.8 MW baseline.
7. ⚙ The same bars (RMSE at most 1.8 MW against a baseline at least four times worse) hold on re-seeded hidden data with a different `vendor_noise` and a different collinear pair.
8. ✍ The report attributes the failure to numerical error, non-identifiability and distribution shift with separate evidence for each, and states which solver and regularisation you chose and why the alternatives lost.
9. ✍ The 10-seed comparison reports a spread (not only a mean) and the report states what that spread means for the decision.

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

1. **Create your own private repository** named `clbg-ML-T2-001-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `loadfit/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Drift alarm.** Build a detector that flags the heat-index vendor change using only the feature stream, and report its detection delay.
2. **Sparse alternative.** Replace ridge with an L1 or column-pruned model and explain which is easier to maintain operationally.
3. **Error bars.** Give a prediction interval for the test period and check its coverage under the vendor change.
4. **Mixed precision.** Repeat the solver comparison in float32 and explain which methods break first.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask you to explain why `lstsq` also failed on the test period even though it is numerically stable; (2) ask what your cross-validation could not detect about the vendor change; (3) give an unseen modification, for example a third near-duplicate sensor or a smaller training window, and ask you to predict and then check what changes.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Least squares, the idea of rank and condition number, and cross-validation. No numerical-analysis course is assumed. |
| **New skill developed** | Diagnosing a failing regression by asking whether the error is computational, statistical or due to shift, and designing the smallest experiment that distinguishes them. |
| **Decisions the member must make** | Which diagnostics to run, how to preprocess, which solver, how to validate time-ordered data, and what the final model should do about a feature that is both redundant and drifting. |
| **What must be investigated independently** | Why a numerically stable solver (`lstsq`) still fails on the shifted period; that is not stated anywhere in the brief. |
| **Why it is interesting** | The headline failure is not the one most people expect: fixing the solver alone barely helps. |
| **Evidence of competence** | Controlled solver experiments, a leakage-free selection procedure, and an RMSE bar met on data with different collinear structure. |
| **Misconceptions exposed** | 'Use lstsq and the problem is solved.' 'Standardising fixes collinearity.' 'Shuffled K-fold is fine for hourly data.' 'Large coefficients on a redundant column are harmless.' |
| **Preparation for later work** | Leads into regularisation and validation in ML-02, drift monitoring in ML-10 and uncertainty work at Tier 3. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
