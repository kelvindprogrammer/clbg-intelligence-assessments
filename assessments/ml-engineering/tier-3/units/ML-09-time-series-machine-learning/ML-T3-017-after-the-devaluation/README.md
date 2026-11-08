# ML-T3-017: After the Devaluation: Calibrated Price Forecasts Across a Structural Break

> *A currency shock changes the level, the drift and the volatility of a staple price. Your forecast intervals were calibrated on the old regime. How wrong are they, and what do you do in the first weeks after?*

![Format: Open-ended (secondary: Investigation)](https://img.shields.io/badge/format-open-ended-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-017` |
| **Title** | After the Devaluation: Calibrated Price Forecasts Across a Structural Break |
| **Subtrack** | ML Engineering |
| **Tier** | 3: Advanced Synthesis |
| **Unit** | [ML-09: Time-Series Machine Learning](../README.md) |
| **Format** | Open-ended (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 4 · Engineering 3 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 24-34 hours over 3-4 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 2 minutes |
| **Recommended prerequisites** | Forecast evaluation with rolling origins, prediction intervals and coverage, log transforms. Recommended: ML-T1-019 and ML-T2-018 |
| **Skills developed** | Structural-break detection; regime-aware training windows; conformal intervals; proper scoring of intervals; designing experiments under a data-scarcity trade-off |
| **Technologies** | Python 3.10+, numpy, pytest |

---

## B. Problem Statement

A grain market association in northern Nigeria (fictional) publishes a **13-week price outlook** for a 50 kg bag of rice, with a 90% range, so that traders and a state food-security office can plan stock purchases. For 150 to 180 weeks the outlook was calibrated and dull. Then a currency adjustment hits: over about eight weeks the level steps up by roughly a quarter, the underlying drift roughly triples, and week-to-week volatility nearly doubles. The association's outlook, calibrated on the old regime, publishes ranges that the new prices routinely escape.

You are given a weekly series of 230 weeks with a single such shock at an unknown week between 150 and 180. Build a forecaster that, at any origin, produces a point path and a 90% interval for the next 13 weeks. Every design decision is contested. Trusting only post-shock data respects the new regime but leaves a few dozen observations at the start; trusting everything keeps data but mis-states volatility; a fixed rolling window is a compromise with its own bias. The break itself must be found from data, with delay. And the weeks immediately after a shock, when the association most needs a good range, are when detection is least reliable.

This is research-grade and open-ended. The tests fix interfaces for the break detector, the scoring functions and the forecaster, and set bars on pooled coverage and sharpness over unseen seeds. How you reach them, what you ablate and what you recommend for the first month after a shock is yours to design and defend.

> **Why this matters beyond this task.** Forecast ranges are most valuable and least trustworthy in the weeks after a regime change. Teams that evaluate only on stable periods report calibration that vanishes exactly when it is needed, and the honest answer usually involves a policy for uncertainty, not just a better model.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Detect** and date a structural break from the data alone, and quantify the detection delay.
2. **Design** training-window strategies (full history, fixed window, post-break, blended) and measure the bias-variance trade-off between them.
3. **Construct** empirically calibrated multi-horizon prediction intervals.
4. **Score** intervals with coverage and the interval score, and show why each alone can be gamed.
5. **Control** for false alarms with a no-shock series, and run ablations that isolate each design decision.
6. **Recommend** a concrete policy for the first weeks after a shock, with evidence.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `breakcast` in [`starter/breakcast/`](starter/breakcast/). Interfaces are fixed; the window strategy, the break test, the interval construction and the early-weeks policy are yours. Use only numpy.

| ID | Requirement |
|---|---|
| **R1** | `detect_break(y, min_seg=20) -> int`: return the first index of the second regime for a single break in the **log** price, using only `y`. On the official series it must be within 6 weeks of the true break, and within 10 weeks when given only 30 weeks after it. |
| **R2** | `interval_score(y, lo, hi, alpha=0.1) -> float`: the mean Winkler score, `(hi - lo) + (2/alpha)(lo - y)+ + (2/alpha)(y - hi)+`. |
| **R3** | `coverage(y, lo, hi) -> float`: share of observations inside `[lo, hi]`. |
| **R4** | `BreakAwareForecaster(alpha=0.1, horizon=13)` with `fit(y)` using **only** `y`, and `predict() -> (point, lo, hi)`, three arrays of length `horizon`, with `0 < lo < point < hi` and a width that grows with the horizon. Scaling `y` by a constant must scale the output by the same constant (currency units must not matter). |

### D.2 Engineering requirements (mandatory)

- Deterministic: no hidden randomness.
- Nothing may read the generator's `break_week`, and `fit` may not use data after the forecast origin.
- Every window strategy goes through the same evaluation harness, on the same origins.
- A no-shock control series (`make_price(shock=0)`) runs through everything you report.
- At least **10 tests of your own** in `tests/test_member_*.py`, including a history-only test, a unit-scaling test and a false-alarm test on the control series.
- `experiments.py` regenerates every number and figure in `REPORT.md`, including **at least 6 seeds**, a coverage-by-weeks-since-break plot, and ablations (full history, fixed windows of 26 and 52 weeks, break-aware, with and without a settling period).

### D.3 Responsibility

The data is synthetic. In the report, discuss who relies on a published price range (small traders who buy on credit, a state office releasing grain) and what an over-confident range does to them in the weeks after a shock. State what disclaimer or minimum-width rule you would publish with the outlook.

### D.4 Optional enhancements

- A Bayesian online change-point detector and a comparison of its delay with yours.
- Blend regimes with a weight that depends on weeks since the detected break.
- Replace the step shock by gradual inflation and test whether your detector survives.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_price(n=230, seed=2026, shock=1.0)` returns `(price, info)`; `info["break_week"]` is the truth (for scoring only) |
| **Provenance** | **Synthetic**, deterministic given the seed; no real person, transaction, market or institution |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Contents** | Log-linear drift, annual swing, AR(1) noise (sd 0.012), and from the break week an eight-week level adjustment of about +28%, extra drift, and noise sd 0.022; `shock=0` removes the shock |
| **Split used by the tests** | Rolling origins every 3 weeks from `break_week + 15` to the end, 13-week horizon |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes a two-column CSV of about 5 KB (the break week is not written) |

Hidden tests use other seeds, a no-shock control and earlier origins.

**Setup**

```bash
cd assessments/ml-engineering/tier-3/units/ML-09-time-series-machine-learning/ML-T3-017-after-the-devaluation
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `breakcast/` package | Break detection, interval scoring and the regime-aware forecaster |
| 2 | `tests/test_member_*.py` (at least 10 tests) | History-only, unit-scaling and false-alarm tests |
| 3 | `experiments.py` | Reproduces every table and figure in the report |
| 4 | `REPORT.md` (at most 2500 words plus tables), from the [template](submission-template/REPORT.md) | Research report with ablations and a recommendation for the weeks after a shock; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `detect_break` is within 6 weeks on the full official series and within 10 weeks given 30 post-break weeks.
3. ⚙ `interval_score` and `coverage` match hand-computed values; `predict` has the required shape, ordering and widening; output scales with the currency unit; `fit` ignores later data.
4. ⚙ **Calibration and sharpness.** On rolling origins from `break_week + 15`, empirical coverage is at least **0.85** and the mean interval score is at most **0.95 times** that of a last-value forecast with an interval from full-history changes. *Justification:* the reference reaches coverage about 0.99 and a ratio of about 0.75 on seed 2026; pooled over six other seeds coverage is about 0.93 and the ratio about 0.9, while the full-history interval covers about 0.76.
5. ⚙ **Not trivially wide.** Mean relative interval width, averaged over the horizon, is under 0.25, and on the no-shock control coverage is at least 0.80.
6. ⚙ **Robustness** (hidden): over six unseen seeds mean coverage is at least 0.88 with no seed below 0.78, and the pooled interval score is no worse than the baseline; with earlier origins (6 weeks after the break) mean coverage is at least 0.75.
7. ✍ The report includes the ablation table, a coverage-by-weeks-since-break analysis, a defended policy for the first weeks after a shock, and an argument about what the single-break, step-shock assumption hides.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 15 |
| Implementation quality | 10 |
| Methodology and evidence | 20 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 20 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T3-017-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `breakcast/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `experiments.py`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Two shocks.** Extend the detector to two breaks and test on a generator you write.
2. **Cross-commodity.** Use a second correlated series to detect the shock earlier.
3. **Decision value.** Convert ranges into a stock-purchase rule and compare the cost of each interval strategy.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask what your forecaster does the week after the next devaluation with three weeks of data; (2) ask why the interval score is a proper score and what coverage alone hides; (3) give an unseen change, for example a gradual inflation ramp instead of a step, and ask which of your components fail first.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Rolling-origin evaluation, prediction intervals, log transforms. No change-point theory; the member chooses a method. |
| **New skill developed** | Reasoning about calibration across regimes, and designing experiments where the data needed is exactly what has not yet arrived. |
| **Decisions the member must make** | Break test, trust threshold, window strategy, interval construction, policy for early weeks, ablation set. |
| **What must be investigated independently** | How detection delay turns into undercoverage, and whether a no-shock control reveals false alarms. |
| **Why it is interesting** | The naive interval fails in a predictable direction (volatility doubled) while point accuracy barely moves, so accuracy-only reports miss the problem. |
| **Evidence of competence** | Pooled coverage and interval-score bars on unseen seeds, a clean control, and an ablation table that separates the effects. |
| **Misconceptions exposed** | 'Use all the data.' 'Coverage near 90% is enough.' 'A detector that fires is a detector that works.' |
| **Preparation for later work** | Leads into ML-14 monitoring and model risk, and applied forecasting work generally. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
