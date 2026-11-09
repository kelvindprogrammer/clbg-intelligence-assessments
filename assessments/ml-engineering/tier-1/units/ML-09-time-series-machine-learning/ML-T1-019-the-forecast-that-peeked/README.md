# ML-T1-019: The Forecast That Peeked: Building a Leak-Free Walk-Forward Backtest for Feeder Load

> *A distribution company's analyst reported a 2% forecast error. Rebuild the backtest from scratch and find out what the honest number is.*

![Format: Implementation (secondary: Debugging-forensics)](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T1-019` |
| **Title** | The Forecast That Peeked: Building a Leak-Free Walk-Forward Backtest for Feeder Load |
| **Subtrack** | ML Engineering |
| **Tier** | 1: Foundations |
| **Unit** | [ML-09: Time-Series Machine Learning](../README.md) |
| **Format** | Implementation (secondary: Debugging-forensics) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8-12 hours over 1-2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 1 minute |
| **Recommended prerequisites** | Python and numpy arrays, linear regression with the normal equations, train/test splits. No time-series library knowledge needed |
| **Skills developed** | Lag-feature construction; walk-forward validation; scale-free error metrics; recursive multi-step forecasting; spotting look-ahead |
| **Technologies** | Python 3.10+, numpy, pytest |

---

## B. Problem Statement

Kaduna Feeder 11 (fictional) serves a few thousand homes and small workshops. Planners at the distribution company schedule load shedding and generator hire one week ahead, using the feeder's **daily peak load in MW**. Last quarter an analyst reported a one-week-ahead forecast error of about 2%, and the figure went into a budget. Nobody could reproduce it. When the notebook was opened, it shuffled the rows before splitting, standardised the series with its full-history mean and standard deviation, and produced "forecasts" using lag features that included the day being predicted.

You are asked to rebuild the evaluation machinery from scratch and use it to report an honest number. The series is 420 days long with a clear weekly rhythm (offices and workshops on weekdays, quiet weekends), slow growth and day-to-day noise that persists for a day or two. You will write six small, exact functions: a lag-matrix builder, an expanding-window splitter, a seasonal-naive forecaster, the MASE metric, a ridge autoregressive forecaster solved in closed form, and a backtest runner. The tests fix every convention (shapes, tie rules, what is penalised), because in forecasting the conventions *are* the bugs. The final test asks the question the original analyst never did: does a simple autoregression beat repeating last week, and by how much, when evaluated honestly?

> **Why this matters beyond this task.** Every forecasting error metric published inside an organisation is only as trustworthy as the split behind it. The habits practised here (strictly causal features, expanding windows, baselines that cost nothing) are the ones that separate a forecast a planner can budget on from one that quietly uses tomorrow's data.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Construct** a lagged design matrix and its target without off-by-one or look-ahead errors.
2. **Generate** expanding-window walk-forward splits that never reach past the end of the data.
3. **Implement** a seasonal-naive baseline and the MASE metric, scaled from training data only.
4. **Solve** ridge regression in closed form with an unpenalised intercept, and forecast recursively.
5. **Explain**, with a measured example, how each of the original analyst's three mistakes would inflate accuracy.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `gridcast` in [`starter/gridcast/`](starter/gridcast/). Interfaces are fixed; how you vectorise is yours. Use only numpy.

| ID | Requirement |
|---|---|
| **R1** | `make_lag_matrix(series, n_lags) -> (X, y)`: row `i` of `X` is `series[i:i+n_lags]` (oldest first) and `y[i] = series[i+n_lags]`. Raise `ValueError` when `n_lags < 1` or the series is not longer than `n_lags`. |
| **R2** | `walk_forward_splits(n, initial, horizon, step) -> list[(train_idx, test_idx)]`: the first fold trains on `0..initial-1` and tests on the next `horizon` points; each later fold advances by `step`; training windows expand; no fold may extend past `n`. |
| **R3** | `seasonal_naive(train, h, m) -> array`: repeat the last full season of length `m` for `h` steps. |
| **R4** | `mase(y_true, y_pred, y_train, m) -> float`: mean absolute error divided by the mean absolute seasonal difference `|y_train[t] - y_train[t-m]|` over the **training** series. |
| **R5** | `ArForecaster(n_lags, alpha=0.0)` with `fit(series)` (returns `self`; sets `coef_` oldest-first and `intercept_`) solving `(ZᵀZ + αP) w = Zᵀy` where `P` is the identity with the intercept entry zero, and `forecast(h)` which feeds each prediction back as the newest lag. |
| **R6** | `backtest(series, fit_forecast, initial, horizon, step, m) -> array`: per-fold MASE, where `fit_forecast(train, h)` returns the forecast for the next `h` points. On the official series an AR forecaster with 21 lags and `alpha = 1` must reach a mean MASE below 0.8 times that of seasonal naive. |

### D.2 Engineering requirements (mandatory)

- Deterministic: no randomness anywhere in the package.
- Vectorised where natural; no Python loop over rows in `make_lag_matrix`.
- No function may read the series beyond the training slice it is given.
- At least **6 tests of your own** in `tests/test_member_*.py`, including a look-ahead test (replace the future with garbage and check forecasts are unchanged) and a test that `backtest` on a pure repeating pattern gives MASE of zero for seasonal naive.
- `experiments.py` regenerates every number and figure in `REPORT.md`, comparing seasonal naive with AR models of at least four lag settings across at least 5 generator seeds.

### D.3 Responsibility

The data is synthetic. In the report, write one short paragraph on who is affected when a load forecast is too low (unplanned outages for homes on the feeder; spoiled stock in cold rooms) and too high (hired generators that nobody needed), and which error you would rather make.

### D.4 Optional enhancements

- Add a Fourier or day-of-week feature set and compare it with raw lags.
- Compare recursive with direct multi-step forecasting.
- Show that the original analyst's three mistakes together shrink the measured error, and by how much.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_load(n=420, seed=2026)` returns a float array of daily peak load in MW |
| **Provenance** | **Synthetic**, deterministic given the seed; no real person, transaction, market or institution |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Contents** | A weekly pattern (weekdays heavier, weekends lighter), linear growth, a slow annual swing and AR(1) noise |
| **Split used by the tests** | Walk-forward from day 200, horizon 7, step 7 (seasonal period 7) |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes a two-column CSV of under 20 KB |

Hidden tests use other seeds and shorter series (n = 380).

**Setup**

```bash
cd assessments/ml-engineering/tier-1/units/ML-09-time-series-machine-learning/ML-T1-019-the-forecast-that-peeked
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `gridcast/` package | Six exact building blocks for causal forecasting |
| 2 | `tests/test_member_*.py` (at least 6 tests) | Includes a look-ahead test |
| 3 | `experiments.py` | Reproduces every table and figure in the report |
| 4 | `REPORT.md` (at most 1200 words plus tables), from the [template](submission-template/REPORT.md) | Honest backtest results and an explanation of the analyst's mistakes; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `make_lag_matrix`, `walk_forward_splits`, `seasonal_naive` and `mase` match hand-computed values, including the error cases.
3. ⚙ `ArForecaster` recovers the coefficients of a simulated AR(2) process to within 0.03, shrinks coefficients under a very large `alpha` while leaving the intercept near the training mean, and forecasts recursively.
4. ⚙ On the official series the AR(21) forecaster has mean MASE below 0.8 times seasonal naive. *Justification:* the reference reaches about 0.65 times on four seeds (0.64 to 0.69); the series carries a trend that repeating last week cannot follow, and the 0.8 bar leaves room for a 14- or 28-lag model. Hidden seeds use 0.85.
5. ⚙ Poisoning the data after the training slice does not change any forecast (hidden test).
6. ✍ The report reproduces the comparison across 5 seeds with spread, and quantifies at least one of the analyst's mistakes.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 15 |
| Methodology and evidence | 10 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T1-019-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `gridcast/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `experiments.py`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Prediction intervals.** Add an empirical interval to `ArForecaster` and measure its coverage.
2. **Hourly data.** Re-derive the conventions for a 24-hour season.
3. **Outliers.** Inject a 5-day outage and compare MAE, MASE and a robust alternative.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why MASE rather than MAPE for a series that can approach zero; (2) ask what would change if the season were 24 instead of 7; (3) give an unseen change, for example a step of 1 instead of 7, and ask what happens to the number of folds and to the variance of the average.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Linear regression, array slicing, the idea of a held-out set. No time-series theory. |
| **New skill developed** | Thinking about *when* each number was known: building features and splits that respect the arrow of time. |
| **Decisions the member must make** | Vectorisation approach, how to handle too-short series, what to do on an empty fold list, how many lags to use in the comparison. |
| **What must be investigated independently** | How much each of the analyst's three mistakes inflates accuracy. The brief names them; measuring them is the member's job. |
| **Why it is interesting** | A forecaster that scores 2% on a flawed backtest and 20% honestly is a real, common failure, and the member reproduces it. |
| **Evidence of competence** | All conventions exact; a 35% error cut over seasonal naive on honest folds; unchanged forecasts when the future is poisoned. |
| **Misconceptions exposed** | 'Shuffle then split is standard.' 'Lower error means a better model, whatever the split.' 'A recursive forecast can look at the answer.' |
| **Preparation for later work** | Leads into ML-T2-018 (calendar features and model comparison) and ML-T3-017 (regime shifts and intervals). |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
