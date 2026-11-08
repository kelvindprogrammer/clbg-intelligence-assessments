# ML-T2-018: Salary Day at the POS Agent: Forecasting Cash-Out Demand Around Paydays and Holiday Eves

> *Run out of cash on the 25th and customers walk away; hold too much float all month and it earns nothing. Forecast next week's demand per agent, and beat the obvious baseline.*

![Format: Comparative (secondary: Investigation)](https://img.shields.io/badge/format-comparative-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-018` |
| **Title** | Salary Day at the POS Agent: Forecasting Cash-Out Demand Around Paydays and Holiday Eves |
| **Subtrack** | ML Engineering |
| **Tier** | 2: Applied Competence |
| **Unit** | [ML-09: Time-Series Machine Learning](../README.md) |
| **Format** | Comparative (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14-20 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 2 minutes |
| **Recommended prerequisites** | Fitting scikit-learn regressors, rolling-origin evaluation, regression metrics. Recommended: ML-T1-019 |
| **Skills developed** | Causal feature design for panels of series; calendar effects; pooled models with per-series scaling; metric choice for zero-heavy data; comparing against a seasonal baseline under small validation |
| **Technologies** | Python 3.10+, numpy and scikit-learn, pytest |

---

## B. Problem Statement

Zamfara Pay (fictional) runs 30 cash-out agents (POS operators) in market towns. Each morning the field team decides how much float to deliver to each agent for the **next seven days**. Cash runs short on **paydays** (days 24 to 27 of each month, when civil-service and teacher salaries land) and on the day before **public holidays**, when volume rises by roughly 70% and 90% respectively. Between those days the weekly rhythm dominates, and each agent has its own busy market day. A few days a year an agent is closed and records zero.

The incumbent method is **seasonal naive**: tomorrow looks like the same weekday last week. It is easy to explain and it fails exactly when the cash matters, because last week was not a payday. You have 300 days of history for the 30 agents and a calendar of paydays and holiday eves that is **known in advance**. Your job is to build a forecaster for the next 7 days that beats seasonal naive at the weekly total level, and to say how sure you are.

Three complications are built in. First, agents differ in size by a factor of 20, so a pooled model needs per-agent scaling that does not leak the future. Second, validation is thin: a window of four weekly origins contains few paydays and perhaps one holiday eve, so differences between a linear model and boosting will be noise. Third, closed days break percentage errors. The task is partially specified: interfaces and acceptance bars are fixed; features, model family, scaling and selection are yours to choose and defend.

> **Why this matters beyond this task.** Demand forecasting at the edge of a payments or retail network is dominated by calendar effects that the simplest baselines miss, evaluated on small validation windows that over-reward complexity. Knowing when a model has really beaten a baseline is the core skill.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Build** causal features for a panel of series: lags, rolling statistics scaled per series, calendar flags for the target day.
2. **Evaluate** forecasts by rolling origin with a pooled WAPE that survives zero days.
3. **Compare** seasonal naive, a regularised linear model and gradient boosting under the same code path.
4. **Select** a model on a validation window, refit it, and judge it once on a held-out final month.
5. **Quantify** how little four validation origins can distinguish, and say what that implies for the choice.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `agentdemand` in [`starter/agentdemand/`](starter/agentdemand/). Interfaces are fixed; the features, scaling, candidates and selection rule are yours. Use only numpy and scikit-learn.

| ID | Requirement |
|---|---|
| **R1** | `make_features(Y, cal, origin, lead) -> (n_agents, F) array`: features for forecasting day `origin + lead - 1` using **only** `Y[:, :origin]` and the calendar (which is known in advance). It must be finite, have the same `F` for every lead, and be unchanged if `Y[:, origin:]` is replaced by anything. |
| **R2** | `wape(y_true, y_pred) -> float`: sum of absolute errors divided by the sum of actuals. |
| **R3** | `evaluate(model, Y, cal, origins, horizon=7) -> float`: pooled WAPE of `model.forecast(Y, cal, origin)[:, :horizon]` against `Y[:, origin:origin+horizon]` over the origins. |
| **R4** | `fit_forecaster(Y, cal, horizon=7) -> model` with `forecast(Y, cal, origin) -> (n_agents, 7)` non-negative and causal, `report_` (dict mapping at least three candidate names, one of them `"seasonal_naive"`, to a validation WAPE) and `chosen_` (a key of `report_`). It receives **only the training days**; the calendar covers the whole horizon. |

### D.2 Engineering requirements (mandatory)

- Deterministic: explicit `random_state` for every estimator.
- Every candidate goes through the same feature, forecast and evaluation path.
- No scaling, fitting or selecting with data from the final 28 days.
- `forecast` must give identical output if `Y` after `origin` changes.
- At least **10 tests of your own** in `tests/test_member_*.py`, including a future-poisoning test of `make_features` and `forecast`, and a test that a closed (zero) day does not produce NaN or infinite features.
- `experiments.py` regenerates every number and figure in `REPORT.md`, including a comparison across **at least 5 generator seeds** with at least one longer history (T = 330).

### D.3 Responsibility

The data is synthetic. In the report, write one paragraph on the cost of each error type to real agents and customers (a stock-out on salary day sends customers to informal lenders; excess float is cash at risk of theft), and on how you would check that forecasts are not systematically worse for small or remote agents.

### D.4 Optional enhancements

- A cost-weighted metric where a stock-out costs three times excess float.
- Quantile forecasts for float sizing.
- A cold-start strategy for an agent with 10 days of history.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_demand(n_agents=30, T=300, seed=2026)` returns `Y` (agents by days, thousands of naira) and `cal` with `dow`, `payday`, `eve` |
| **Provenance** | **Synthetic**, deterministic given the seed; no real person, transaction, market or institution |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Contents** | Per-agent scale (log-normal), a weekly profile with a per-agent market day, +70% on paydays, +90% on holiday eves, 2% closed days, multiplicative noise, mild growth |
| **Split used by the tests** | Fit on days 0 to 271; four weekly forecast origins at days 272, 279, 286 and 293 (the last contains a payday and a holiday eve) |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes a CSV of about 100 KB |

Hidden tests use other seeds and a longer history (T = 330).

**Setup**

```bash
cd assessments/ml-engineering/tier-2/units/ML-09-time-series-machine-learning/ML-T2-018-salary-day-cash-out-demand
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `agentdemand/` package | Causal features, metric, evaluation and model selection |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Includes future-poisoning and closed-day tests |
| 3 | `experiments.py` | Reproduces every table and figure in the report |
| 4 | `REPORT.md` (at most 1800 words plus tables), from the [template](submission-template/REPORT.md) | Decision memo for the head of field operations; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `make_features` and `forecast` are causal: changing `Y` from the origin onward changes nothing.
3. ⚙ `wape` and `evaluate` match hand-computed values, including with a stub model.
4. ⚙ `report_` has at least three candidates including `seasonal_naive`, and `chosen_` is a key.
5. ⚙ **Performance.** On the four final origins the chosen model's pooled WAPE is at most **0.8 times** seasonal naive, and its total-volume bias is under 10%. *Justification:* the reference reaches about 0.66 times (0.29 against 0.44 on seed 2026); the irreducible multiplicative noise keeps WAPE near 0.27. In the payday week the model must beat naive by the same factor.
6. ⚙ **Robustness.** On hidden seeds and a longer history the bar relaxes to 0.85 times (the ratio varied between 0.65 and 0.67 across the seeds used in calibration).
7. ✍ The report shows what each ingredient contributes (calendar flags, the same-weekday-last-month lag, scaling, model family) and says honestly whether the validation window can separate your top two candidates.

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

1. **Create your own private repository** named `clbg-ML-T2-018-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `agentdemand/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `experiments.py`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Probabilistic.** Produce 90% prediction intervals per agent and check their coverage.
2. **Hierarchy.** Forecast the total and reconcile it with the agents.
3. **Drift.** Move the payday window by two days in the test period and measure what breaks.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask whether the gap between your top two validation candidates is larger than the noise in four origins; (2) ask what you would do if a public holiday moved by a day; (3) give an unseen change, for example a 14-day horizon, and ask which features stop being causal.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | scikit-learn regressors and rolling evaluation. No time-series model theory. |
| **New skill developed** | Designing causal features for many series at once, and judging a model on a validation window too small to rank close candidates. |
| **Decisions the member must make** | Which lags, which scaling, which calendar features, which candidates, and how to select. |
| **What must be investigated independently** | Why same-weekday-last-month matters on paydays, and whether the model helps small agents as much as large. |
| **Why it is interesting** | The big win comes from two calendar flags and one lag, not from a bigger model. |
| **Evidence of competence** | Holdout WAPE at most 0.8 times seasonal naive on re-seeded data, unchanged forecasts under future-poisoning, honest uncertainty. |
| **Misconceptions exposed** | 'More lags is better.' 'MAPE is the standard metric.' 'The best validation score is the best model.' |
| **Preparation for later work** | Leads into ML-T3-017 (structural breaks and interval calibration). |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
