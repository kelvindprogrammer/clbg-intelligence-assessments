# DS-T2-020: Which Forecast Do You Trust?

> *A forecast that is slightly more accurate but whose uncertainty is a lie is worse than a plain baseline. Prove yours is neither.*

![Format: comparative](https://img.shields.io/badge/format-comparative-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-020` |
| **Title** | Which Forecast Do You Trust? Benchmarking Load Forecasts with Honest Intervals on Power Feeders |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Competence and Method Selection |
| **Unit** | [DS-10: Time-Series Analysis and Forecasting](../README.md) |
| **Format** | Comparative (secondary: Implementation) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14–22 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Completed or equivalent to DS-T1-025 (baselines, MASE, rolling-origin backtests); linear regression with `numpy.linalg.lstsq`; quantiles; pandas date features. |
| **Skills developed** | Forecaster design under partial specification; leak-free benchmarking; prediction-interval calibration; interval scores; outage handling; reporting forecast uncertainty |
| **Technologies** | Python 3.10+, pandas, NumPy, SciPy (optional), pytest. `statsmodels` is permitted if you list it in your requirements. |

---

## B. Problem Statement

Nigeria's distribution companies (DisCos) plan switching, load-shedding schedules and maintenance windows two weeks ahead, feeder by feeder. A planner needs two things from a forecast: a **central estimate** and an **honest range** ("with 80% confidence, tomorrow's peak on this 11 kV feeder is between 17 and 21 MW"). A model that gives a precise-looking range that is right only half the time is dangerous, because planners will schedule maintenance inside the range they believe is safe.

You have been given `feeder_daily.csv`: 700 days (about 23 months) of daily peak load for **eight synthetic feeders**. The feeders differ: some are office-dominated (weekends drop), some residential (weekends rise slightly); all have a gentle growth trend and a mild annual cycle linked to the hot season; the noise is multiplicative; two feeders had a **new housing estate connected** part-way through the history, raising their level permanently; and on about 1.5% of days a feeder was **switched off**, so the recorded peak collapses towards zero. Nobody labelled any of this for you.

Your job is not to find the fanciest model. It is to run a **fair, leak-free comparison** and decide what you can legitimately claim:

1. Build the harness: a rolling-origin backtest where each forecaster sees only the history up to its origin; scoring by MASE, interval coverage and interval score.
2. Implement the seasonal-naive baseline *with* empirical prediction intervals, so that the baseline is judged on uncertainty too.
3. Design `my_forecaster`. The method is yours: it must handle weekly seasonality, trend, the annual cycle, a level shift and outage days (a forecast should not try to predict a blackout, and a blackout in training should not poison the fit).
4. Detect the outage days with a rule you justify.
5. Report where your method wins, where it does not, and what the intervals really deliver.

This is a **Tier 2** problem: the interfaces and metrics are specified exactly, but the forecasting method, the outage rule and the interval construction are your decisions, and the tests judge outcomes (accuracy against the baseline, calibration, detection quality), not your technique.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Build a rolling-origin benchmark in which a forecaster can only see its own history.
2. Implement seasonal-naive forecasts with empirical prediction intervals as a fair baseline.
3. Design and justify a forecaster for a series with trend, weekly and annual seasonality, a level shift and outages.
4. Evaluate point accuracy with MASE and uncertainty with coverage and the interval score, and read them together.
5. Detect non-forecastable outage days and explain how they affect fitting and scoring.
6. Report per-series results honestly, including where the method does not beat the baseline.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

The harness interfaces are fixed; the forecasting method is open. Implement the `fcbench` package in [`starter/fcbench/`](starter/fcbench/). The function signatures are fixed because the automated tests import them. The internals are yours.

| ID | Requirement |
|---|---|
| **R1** | `flag_outages(s) -> pd.Series[bool]` with the same index as `s`. Your rule must be causal-safe enough to be reused inside a forecaster, and you must state its threshold logic in the report. |
| **R2** | `seasonal_naive_forecast(train, h, level=0.8) -> Forecast`: mean `train[-7 + (i % 7)]`; lower and upper are the mean plus the `(1-level)/2` and `(1+level)/2` quantiles of in-sample weekly differences `y_t - y_{t-7}`. |
| **R3** | `my_forecaster(train, h, level=0.8) -> Forecast`: any method, same signature. It sees only `train`. Return finite arrays of length `h` with `lower <= upper`. |
| **R4** | `interval_score(y, lower, upper, level)`: the mean interval score with `alpha = 1 - level`. |
| **R5** | `backtest_forecasts(y, forecaster, h, initial, step, level)`: rolling origins `k = initial, initial+step, ...` with `k+h <= len(y)`; return dicts with `origin`, `mean`, `lower`, `upper`, `actual`; raise `ValueError` on malformed forecasts. |
| **R6** | `run_benchmark(df, forecasters, h=14, initial=400, step=28, level=0.8)`: a DataFrame `[feeder_id, method, mase, coverage, interval_score]`, one row per feeder and method, sorted by feeder then method. MASE is the mean over origins with the scale computed from `y[:k]` only. |

### D.2 Engineering requirements (mandatory)

- **No peeking.** Nothing computed at origin `k` may use `y[k:]`; the hidden tests change the future and compare.
- **Determinism.** Same data gives the same forecast. If you use randomness, seed it.
- **Time budget.** The full benchmark for two methods on all eight feeders must finish in under 3 minutes on a laptop.
- **Tests.** Keep the provided tests passing and add **at least 10 tests of your own** in `tests/test_member_*.py`, including edge cases you found yourself.
- **Dependencies.** Use only the packages in [`starter/requirements.txt`](starter/requirements.txt). If you add one, justify it in your report.

### D.3 Privacy and responsibility

The data is **synthetic**; no real feeder, customer or utility is described. Real feeder-level load can reveal the occupancy and activity of identifiable estates and is critical-infrastructure information. In your report, add a short note on how you would treat such data (aggregation level, access, who may see forecasts of outages).

### D.4 Optional enhancements (not required for full marks)

- Compare two or three method families (for example exponential smoothing, regression on features, a gradient-boosted model) and report the winner per feeder with the evidence.
- A conformal-style interval method, compared with your empirical-quantile intervals.
- A rolling re-fit versus fit-once analysis: how much does refitting every origin buy?

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/feeder_daily.csv`](resources/data/feeder_daily.csv): 8 feeders × 700 days = 5,600 rows × 3 columns (`feeder_id`, `date`, `peak_mw`), about 128 KB, UTF-8 |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed. Multiplicative noise around a trend × weekly × annual structure; two level shifts; ~1.5% outage days. No real utility data. |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Integrity** | The contract test checks the SHA-256, so do not edit the file |

**Known limitations (by design).** The annual cycle is a single smooth harmonic and there are no holidays, so real feeders are harder. 23 months of history gives only one full seasonal cycle for the earliest origin, which limits how well any annual effect can be estimated and is itself something to discuss. The hidden tests regenerate feeders with the same process but different seeds.

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-10-time-series-and-forecasting/DS-T2-020-which-forecast-do-you-trust
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract        # should pass immediately: checks data and scaffold
pytest                    # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `fcbench/` package (the completed starter) | The core technical evidence |
| 2 | `tests/test_member_*.py` | Shows you can pin behaviour down and think about edge cases |
| 3 | `outputs/benchmark.csv` | The per-feeder results table produced by `run_benchmark` |
| 4 | `analysis.py` or `analysis.ipynb` | Reproduces the table, calibration plot and outage inventory |
| 5 | `REPORT.md` (from the [template](submission-template/REPORT.md)), with the AI-use declaration inside | Communicates decisions and limits; integrity declaration (see §K) |
| 6 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites, the rest by hand.

1. ⚙ Provided and member tests pass from a clean environment, and the benchmark runs in under 3 minutes.
2. ⚙ **Outage detection:** precision and recall of `flag_outages` against the hidden truth are both **≥ 0.90**. *Justification:* the outages are collapses to under 20% of normal load while ordinary noise stays above ~70%, so a sensible rule separates them; the reference scores 1.00/1.00 on all tested seeds.
3. ⚙ **Accuracy:** on hidden regenerated feeders the median per-feeder ratio `MASE(mine)/MASE(seasonal-naive)` is **≤ 0.90**, and no feeder exceeds **1.05**. *Justification:* the baseline ignores trend and level shifts and doubles its noise by differencing; the reference achieves a median ratio of about 0.68–0.75 and a worst case of 0.86.
4. ⚙ **Calibration:** the mean 80% interval coverage of your method lies in **[0.70, 0.90]** and no feeder is below **0.60**. *Justification:* about 1.5% of days are unforecastable outages and horizons up to 14 days add uncertainty, so exact 0.80 is not expected; the reference scores 0.76–0.79.
5. ⚙ **No peeking:** altering data after a forecast origin never changes that origin's forecast.
6. ✍ The report justifies the method and the outage rule, and reports per-feeder results including losses.
7. ✍ The report distinguishes accuracy from calibration and explains the interval score.
8. ✍ Claims are limited to what 8 synthetic feeders and 11 backtest origins can support.

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

1. **Create your own private repository** named `clbg-DS-T2-020-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` into it. Your package sits at the repository top level.
2. Commit as you work. Your commit history is part of the evidence (see §K); a single "final" commit will be questioned at defence.
3. Add your outputs and `REPORT.md`, then run `pytest` from a clean environment built from your `requirements.txt`.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository, using the **Assessment submission** template. Include the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never stand in for the core requirements.

1. **Break detection.** Detect the level-shift feeders from data and show how a break-aware method helps them.
2. **Horizon decay.** Show how coverage and MASE change from horizon 1 to 14 and fix any drift.
3. **Asymmetric loss.** A planner dislikes under-forecasting twice as much as over-forecasting. Change the method and show what it costs in MASE.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept, suggest an idiom or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: which tool, what for, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources, with a link.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers, thresholds or report text.
- **How your understanding is verified.** In the 5-minute defence the assessor will: 
  1. picks one feeder and one origin and asks you to trace every number in the forecast, including how outages in the training window were treated;
  2. asks what would make you distrust a model that wins on MASE but undershoots on coverage;
  3. gives you an unseen modification, for example a heavier-tailed noise distribution or a 28-day horizon, and asks you to adapt and re-test live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Baselines and MASE from Tier 1; regression with dummy and Fourier features; quantiles. |
| **New skill developed** | Comparing forecasters on accuracy and uncertainty together, and building intervals that survive out-of-sample. |
| **Decisions the member must make** | Model family; how to treat outages in training; how to estimate interval width without leaking; how much history to use after a level shift. |
| **What must be investigated independently** | That outages and level shifts exist, how large they are, and what they do to the baseline's intervals. |
| **Why it's interesting** | Utilities really do schedule on forecast ranges, so a mis-calibrated range has operational cost. The baseline itself is held to the same standard. |
| **Evidence of competence** | Hidden-data accuracy ratio, calibration, outage precision and recall, and a no-peeking test. |
| **Misconceptions exposed** | In-sample residual quantiles give valid intervals. Lower MAE means a better forecast. Outages are noise to be predicted. |
| **Preparation for later work** | Leads to DS-T3 hierarchical reconciliation and ML time-series modelling, where the same benchmark discipline is assumed. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
