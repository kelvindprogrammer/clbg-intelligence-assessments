# DS-T1-025: The Agent Who Went Quiet

> *Before you can beat a forecast you have to build an honest one, and before you can build one you have to decide what a missing day means.*

![Format: implementation](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-025` |
| **Title** | The Agent Who Went Quiet: Baseline Forecasts from a Gappy Mobile-Money Ledger |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-10: Time-Series Analysis and Forecasting](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 8–14 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Python functions; pandas `Series`/`DataFrame` indexing and `reindex`; NumPy slicing; running `pytest`. |
| **Skills developed** | Time-series regularisation; missing-data semantics; seasonal-naive and moving-average baselines; MAE and MASE; rolling-origin backtesting; leakage avoidance |
| **Technologies** | Python 3.10+, pandas, NumPy, pytest |

---

## B. Problem Statement

A mobile-money operator in Nigeria wants to forecast, week by week, how many transactions each of its field agents will process, so that cash and float can be pre-positioned before the busy market days. Before anyone builds a clever model, the planning team wants the **baselines** done properly: a baseline is the yardstick every later model must beat, and a sloppy one makes weak models look good.

The operator sent you `agent_daily.csv`: one row per agent per day with a transaction count. It is not clean. Some days have **no row at all**. A few rows carry the sentinel `-1` (the collector app could not read the till). Some days appear **twice**, because the nightly upload was retried, and in some of those the second upload has a different number. Eight agents, about 196 days each.

Three facts shape everything you do:

- **A missing day is unknown, not zero.** If you turn gaps into zeros, an agent who simply was not reporting looks like one who sold nothing, and every error metric is poisoned.
- **Two kinds of agent exist.** Some sit near a market with a strong weekly rhythm (Friday and Saturday peaks). Others serve a steady trickle with no weekly shape. Which baseline wins depends on the agent, and you must decide from evidence.
- **Backtests lie when they peek.** If the error scale or a fill value is computed using days after the forecast origin, the score is flattering and useless.

You will build a small, fully specified toolkit: regularise each series, fill gaps by a stated rule, implement two baseline forecasters, implement MAE and MASE, run a rolling-origin backtest, and pick a baseline for each agent. Tier 1 is about **precision**: every function has an exact contract and the tests check it, so the skill being assessed is careful, correct, leak-free implementation, and honest reporting of what the numbers mean.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Convert an irregular, duplicated ledger into a complete daily series, representing unknown days as unknown.
2. Implement and explain seasonal-naive and moving-average forecasts.
3. Implement MAE and MASE and explain why a scale-free metric is needed to compare agents of different size.
4. Build a rolling-origin backtest whose scores use only information available at each forecast origin.
5. Choose a baseline per series from backtest evidence and state how confident that choice is.
6. Write tests that pin down edge cases (duplicates, sentinels, ties, empty windows).

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

The package is built around eight small functions with exact contracts. Implement the `agentcast` package in [`starter/agentcast/`](starter/agentcast/). The function signatures are fixed because the automated tests import them. The internals are yours.

| ID | Requirement |
|---|---|
| **R1** | `to_regular(df, agent_id) -> pd.Series`: complete daily `DatetimeIndex` (freq `D`) from the agent's first to last date; name `txn_count`; float. Missing days and `-1` sentinels are `NaN`. For repeated dates the last row in file order wins. |
| **R2** | `fill_gaps(s, period=7)`: fill `NaN` in time order from the value `period` steps earlier (already filled), else the original observed value `period` steps later, else the median of observed values. The input must not be mutated. |
| **R3** | `seasonal_naive(train, h, period=7)`: `forecast[i] = train[-period + (i % period)]`. |
| **R4** | `moving_average(train, h, window=7)`: a flat forecast equal to the mean of the last `window` values. |
| **R5** | `mae(y, yhat)` and `mase(y, yhat, train, period=7)`. The MASE scale is the mean absolute seasonal difference of `train`; raise `ValueError` if it is zero. |
| **R6** | `rolling_origin(n, initial, h, step)` returns `[(k, k+h), ...]` for `k = initial, initial+step, ...` while `k+h <= n`. |
| **R7** | `backtest(y, method, h, initial, step, period=7)` returns the mean MASE over all origins. Train is `y[:k]`, test is `y[k:k+h]`, and the scale uses **only** `y[:k]`. Raise `ValueError` if there are no origins. |
| **R8** | `choose_baseline(df, h=7, initial=84, step=7)` returns `{agent_id: 'seasonal_naive' | 'moving_average'}` for every agent in sorted order, lower mean MASE winning and ties going to `seasonal_naive`. |

### D.2 Engineering requirements (mandatory)

- **No mutation.** Functions never modify their inputs, and the CSV is read-only.
- **Determinism.** Same input, same output, no hidden randomness.
- **Vectorise where natural**, but correctness comes first; the data is small.
- **Tests.** Keep the provided tests passing and add **at least 8 tests of your own** in `tests/test_member_*.py`, including edge cases you found yourself.
- **Dependencies.** Use only the packages in [`starter/requirements.txt`](starter/requirements.txt). If you add one, justify it in your report.

### D.3 Privacy and responsibility

The data is **synthetic**: agent IDs are fictional and no customer is described. Real agent-level transaction data is commercially sensitive and, where it identifies individuals or small businesses, is personal data under the Nigeria Data Protection Act 2023. In your report, add one paragraph on what you would restrict if this were real (access, aggregation to avoid exposing a single small agent, retention of the ledger).

### D.4 Optional enhancements (not required for full marks)

- A plot (saved as PNG, not committed as the only evidence) of one agent's series with the filled days highlighted.
- A third baseline (seasonal average over the last four weeks) with a backtest comparison.
- A note on how a public holiday would break the weekly pattern and what you would do.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/agent_daily.csv`](resources/data/agent_daily.csv): about 1,600 rows × 3 columns (`agent_id`, `date`, `txn_count`), about 30 KB, UTF-8 |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed (agents have Poisson-distributed counts with trend; half have a weekly market-day pattern). No real agent or customer is described. |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Integrity** | The contract test checks the file's SHA-256, so do not edit it |

**Known limitations (by design).** There are no holidays, outages or structural breaks in this export, so a good baseline here will look better than it would in production. Hidden tests use freshly generated data from the same process.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-10-time-series-and-forecasting/DS-T1-025-the-agent-who-went-quiet
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract        # should pass immediately: checks data and scaffold
pytest                    # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `agentcast/` package (the completed starter) | The core technical evidence |
| 2 | `tests/test_member_*.py` | Shows you can pin behaviour down and think about edge cases |
| 3 | `outputs/baseline_choice.csv` (agent, chosen baseline, both MASE scores) | The decision the planning team would actually use |
| 4 | `analysis.py` or `analysis.ipynb` | Reproduces the table and any plots from the CSV |
| 5 | `REPORT.md` (from the [template](submission-template/REPORT.md)), with the AI-use declaration inside | Communicates decisions and limits; integrity declaration (see §K) |
| 6 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites, the rest by hand.

1. ⚙ `pytest` passes all provided tests and your own tests from a clean environment.
2. ⚙ `to_regular` yields complete daily indexes with `NaN` (never zero) for unknown days, on the real export and on freshly generated data.
3. ⚙ `backtest` uses no data after each origin: appending later observations never changes an earlier score.
4. ⚙ On freshly generated hidden data, `choose_baseline` picks the truly seasonal agents correctly for **at least 7 of 8** agents. *Justification:* the two agent types differ by a wide margin, so a correct implementation errs only when noise is extreme; the reference scores 8/8 on all tested seeds, and 7/8 leaves room for one unlucky agent.
5. ✍ `baseline_choice.csv` and the report agree with what your code regenerates.
6. ✍ The report states what a missing day was assumed to mean, why `-1` is not a value, and one way those assumptions could be wrong.
7. ✍ No claim in the report goes beyond what an 8-agent synthetic sample can support.

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

1. **Create your own private repository** named `clbg-DS-T1-025-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` into it. Your package sits at the repository top level.
2. Commit as you work. Your commit history is part of the evidence (see §K); a single "final" commit will be questioned at defence.
3. Add your outputs and `REPORT.md`, then run `pytest` from a clean environment built from your `requirements.txt`.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository, using the **Assessment submission** template. Include the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never stand in for the core requirements.

1. **Gap sensitivity.** Randomly blank 5%, 15% and 30% of observed days and measure how `fill_gaps` changes the chosen baselines.
2. **Horizon curve.** Plot mean MASE against horizon (1 to 14 days) for both baselines and explain the crossover.
3. **A better yardstick.** Implement a seasonal-average baseline and show whether it beats seasonal-naive, with the evidence.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept, suggest an idiom or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: which tool, what for, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources, with a link.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers, thresholds or report text.
- **How your understanding is verified.** In the 5-minute defence the assessor will: 
  1. picks one agent and asks you to explain what happened to a duplicated date and to a `-1` row;
  2. asks why MASE rather than MAE, and why the scale must come from the training window only;
  3. gives you an unseen modification, for example a 14-day season or a ties-to-moving-average rule, and asks you to change the code and tests live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Basic pandas and NumPy, functions, `pytest`. No statistics beyond averages and absolute errors. |
| **New skill developed** | Treating a baseline as a piece of engineering: regularise, fill by a stated rule, score without peeking. |
| **Decisions the member must make** | What a gap means; how to handle conflicting duplicates in the report; how confident to be in a per-agent choice from a short backtest. |
| **What must be investigated independently** | The shape of the defects in the export: how many gaps, sentinels and conflicting duplicates, and whether they cluster. |
| **Why it's interesting** | Operators in Nigerian mobile money really do pre-position cash by agent; the same two baselines are what any later model must beat. |
| **Evidence of competence** | Exact-contract tests, a leakage test, and a hidden choice test on freshly generated data. |
| **Misconceptions exposed** | A missing day is zero. MAE is enough to compare agents. Using the whole series to scale the metric is harmless. |
| **Preparation for later work** | Leads to DS-T2 method comparison with prediction intervals and DS-T3 hierarchical reconciliation. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
