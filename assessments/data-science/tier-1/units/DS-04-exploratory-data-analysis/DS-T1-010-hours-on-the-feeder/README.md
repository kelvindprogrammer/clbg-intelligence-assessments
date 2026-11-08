# DS-T1-010: Hours on the Feeder

> *Customers pay Band A tariffs for 20 hours of electricity a day. Turn six months of messy outage logs into supply hours you can defend, and find out who is really getting what they pay for.*

![Format: Implementation](https://img.shields.io/badge/format-implementation-1d76db) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-010` |
| **Title** | Hours on the Feeder: Supply-Hours Exploration of Electricity Outage Logs |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-04: Exploratory Data Analysis](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 10–16 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | pandas datetimes and `groupby`; sorting and iterating; the idea of a bootstrap; running `pytest` |
| **Skills developed** | Event-log to time-series conversion; interval arithmetic; detecting logging artefacts; distinguishing "no record" from "no event"; dependence-aware bootstrap intervals (block and cluster); answering stakeholder questions with quantified uncertainty |
| **Technologies** | Python 3.10+, pandas, numpy, matplotlib, pytest |

---

## B. Problem Statement

Since 2024, Nigerian electricity customers have been billed under the Nigerian Electricity Regulatory Commission's **service-based tariff**. Each feeder is placed in a band that promises a **minimum average daily supply**: Band A at least 20 hours, Band B 16, Band C 12, Band D 8 and Band E 4 ([NERC: What is Service Based Tariff?](https://nerc.freshdesk.com/support/solutions/articles/151000113695-what-is-service-based-tariff-sbt-)). Band A customers pay the most. If a "Band A" feeder actually delivers 14 hours, thousands of households are paying a premium for a service they do not receive, and the regulator can order a re-banding and compensation.

You are an analyst at **Savanna Coast Electricity Distribution (SCED)**, a fictional distribution company. SCED's compliance team has to report supply performance to the regulator for January–June 2025 across its 48 11 kV feeders. The only source is the control room's **outage event log**: one row per outage, typed in by shift operators, with a start time, an end time and a cause. You must turn that log into **daily supply hours per feeder**, and then answer the compliance team's questions.

The log was not designed for analysis, and naive processing gives wrong answers in both directions:

- Two operators on the same shift sometimes log **the same outage twice**, a few minutes apart. If you add up durations, you count the same dark hour twice.
- Outages **cross midnight**, so a single event belongs to two days.
- Some events were **never closed** (the end time is blank). Some have an **end before the start**.
- On some days a business unit's **logging system was down**. No events were recorded, which makes those days look like perfect 24-hour supply. "No record of an outage" is not "no outage".
- Daily supply on one feeder is **autocorrelated**: a bad week is usually followed by another bad week. Treating 181 days as 181 independent observations makes your confidence intervals far too narrow, so you would accuse feeders of under-delivery without real evidence.

Your job is to build a small, tested library that handles all of this exactly as specified, and then use it to answer six questions with evidence and uncertainty.

**Known facts from SCED** (your only documentation):

- Times are West Africa Time (no daylight saving). Times are recorded to the minute.
- The export was taken at **2025-07-01 00:00**. Nothing after that time exists.
- `log_coverage.csv` comes from the logging server's heartbeat. `logging_ok = 0` means the business unit's log was down for that whole day.
- `upstream_grid` events are outages caused by the national grid, not by SCED. The control room believes there were "a few" system-wide grid collapses in the period.
- All data is **synthetic**. SCED, its feeders and its business units are fictional.

**The six questions** (your answers go in `answers.json` via R9 and in `SUPPLY_REPORT.md`):

| Q | Question |
|---|---|
| **Q1** | How many logged events are invalid, and how many were open (never closed)? How were the open ones resolved? |
| **Q2** | How many feeder-days have no logging coverage, and what would happen to the Band A figure if they were treated as full supply? |
| **Q3** | What is the mean daily supply in each band, with a 95% interval that respects the fact that feeders, not days, are the independent units? |
| **Q4** | Which feeders are *confidently* delivering less than their band's minimum? |
| **Q5** | On which dates was there a system-wide grid collapse? |
| **Q6** | By how much does naive processing (summing durations, ignoring coverage) distort the Band A figure? |

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Convert an event log into a regular time series** correctly, handling overlap, midnight-crossing, open events and censoring at the export time.
2. **Implement and test interval arithmetic** (union and per-day clipping), with edge cases worked out by hand.
3. **Detect logging artefacts** and represent missing coverage explicitly instead of letting it masquerade as data.
4. **Quantify uncertainty under dependence** with a block bootstrap (within a feeder) and a cluster bootstrap (across feeders), and explain why an i.i.d. interval would mislead.
5. **Answer stakeholder questions** with numbers, intervals and a clear statement of what is and is not certain, including feeders whose evidence is inconclusive.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `feeder_eda` package in [`starter/feeder_eda/`](starter/feeder_eda/). The signatures are fixed because the tests import them. Loaders and constants are provided in `io.py`.

| ID | Requirement |
|---|---|
| **R1** | `parse_events(raw, export_time=EXPORT_TIME) -> (clean, issues)`. Parse `start`/`end` with `TIME_FORMAT`. An event whose `end` is present and **not after** its `start` is invalid: exclude it and record `issue_type = "end_not_after_start"`. An event with a blank `end` is **open**: close it at the `start` of the **next valid event on the same feeder that starts strictly later** (`closed_by = "next_event"`, issue `"open_closed_at_next_event"`), or, if there is none, at `export_time` (`closed_by = "export"`, issue `"open_closed_at_export"`). Every other event has `closed_by = "logged"`. Clip all ends at `export_time`. `clean` has columns `event_id, feeder_id, start, end, cause, logged_by, closed_by` sorted by `event_id`. `issues` has `event_id, issue_type` sorted by `event_id`. Never modify `raw`. |
| **R2** | `merge_intervals(intervals)` returns the union of half-open intervals `[start, end)` as a sorted list of disjoint tuples. Touching intervals merge, and empty intervals are ignored. It must work for numbers and datetimes. |
| **R3** | `daily_supply(clean, feeders, coverage, start, end, merge=True)` returns one row per feeder per calendar day in `[start, end)`, sorted by `feeder_id` then `date`, with columns `feeder_id, date, outage_hours, supply_hours, status`. With `merge=True`, a day's outage hours are the length of the **union** of the feeder's outage intervals intersected with that day. With `merge=False`, they are the plain **sum** of the clipped durations (the naive method, used only for Q6). Outage hours are capped at 24, and `supply_hours = 24 − outage_hours`. Days on which the feeder's business unit has `logging_ok = 0` get `status = "no_coverage"` and `NaN` hours. Otherwise `status = "ok"`. |
| **R4** | `feeder_summary(daily, feeders)`: one row per feeder over `"ok"` days, with `feeder_id, band, days_observed, mean_supply, median_supply, p10_supply` (`numpy.quantile`, default linear method), `share_days_meeting_band` (supply ≥ band minimum), `meets_band_on_average` (mean ≥ band minimum). |
| **R5** | `block_bootstrap_mean_ci(values, block=7, n_boot=2000, seed=0, alpha=0.05)`. Drop NaNs (raise `ValueError` if nothing remains). Split the date-ordered series into consecutive **non-overlapping** blocks of length `block` (the last block may be shorter). Create `rng = numpy.random.default_rng(seed)`. For each of `n_boot` replicates, draw `k` block indices with `rng.integers(0, k, size=k)` (k = number of blocks), concatenate those blocks and take the mean. Return `numpy.quantile(means, [alpha/2, 1 − alpha/2])` as two floats. |
| **R6** | `flag_misbanded(daily, feeders, n_boot=2000, seed=0)`: for each feeder (sorted), take its `"ok"` days in date order, compute R5 with the given `seed`, and return `feeder_id, band, band_min, mean_supply, ci_low, ci_high, misbanded`, where `misbanded = ci_high < band_min`. |
| **R7** | `band_summary(daily, feeders, n_boot=2000, seed=0)`: for each band A–E, compute every feeder's mean supply over `"ok"` days. Report `n_feeders`, `mean_supply` (the mean of the feeder means), and a **cluster bootstrap** interval: `rng = default_rng(seed)` (fresh for each band), `rng.choice(feeder_means, size=(n_boot, n_feeders), replace=True).mean(axis=1)`, 2.5% and 97.5% quantiles. Also return `band_min`. |
| **R8** | `grid_collapse_days(clean, feeders, coverage, threshold=0.8)`: sorted `YYYY-MM-DD` dates on which at least `threshold` of the feeders whose business unit was covered that day had an `upstream_grid` event overlapping that date. |
| **R9** | `build_answers(raw_events, feeders, coverage, n_boot=2000, seed=0) -> dict` with exactly these keys: `q1` {`invalid_events`, `open_events`, `open_closed_at_next_event`, `open_closed_at_export`}; `q2` {`uncovered_feeder_days`}; `q3` {band: {`n_feeders`, `mean_supply`, `ci_low`, `ci_high`}}; `q4` {`misbanded`: sorted list of feeder ids}; `q5` {`collapse_dates`}; `q6` {`band_a_correct_mean`, `band_a_naive_sum_mean` (R3 with `merge=False`), `band_a_uncovered_as_24h_mean` (correct method, but uncovered days counted as 24 h), `naive_sum_bias`, `coverage_bias`} where each bias is the naive mean minus the correct mean, and every Band A mean is the mean of the Band A feeder means. |
| **R10** | `python -m feeder_eda <data_dir> --out <dir>` writes `answers.json`, `daily_supply.csv` and `feeder_summary.csv`. (The CLI is provided; it works once R1–R9 do.) |
| **R11** | An exploration notebook or script (`exploration.ipynb` or `exploration.py`) that reproduces every figure and number in your report, including: a feeder × day heat map of supply hours that makes coverage gaps and collapse days visible; the per-band distribution of feeder means; and a comparison of the **cluster** interval for Band A with a naive i.i.d. interval over all Band A feeder-days. |
| **R12** | `SUPPLY_REPORT.md` (≤ 1,500 words plus tables and figures), from the [template](submission-template/SUPPLY_REPORT.md), answering Q1–Q6 for SCED's compliance manager. |

### D.2 Engineering requirements (mandatory)

- **Determinism.** The CLI gives identical outputs on every run.
- **No mutation** of input DataFrames.
- **Performance.** The CLI finishes in under 2 minutes on a typical laptop.
- **Tests.** Keep the provided tests passing and add **at least 10 tests of your own** in `tests/test_member_*.py`. At least four must be hand-worked interval cases, for example an event spanning three days, an event exactly at midnight, an open event whose next event is its own duplicate, and an event ending exactly at the export time.
- **Dependencies.** Only those in [`starter/requirements.txt`](starter/requirements.txt).

### D.3 Privacy and responsibility

The data is synthetic and contains no customer records. In real life, feeder performance data is commercially and politically sensitive, because it can trigger compensation orders and public complaints.

- Report findings at feeder level only, as the regulator would see them. Do not invent customer-level conclusions.
- In one paragraph of the report, explain how a real compliance analysis should treat a feeder that is flagged on weak evidence: who should verify it, and with what other data (for example meter readings at the injection substation), before it is reported.

### D.4 Optional enhancements (not required for full marks)

- A sensitivity analysis of Q4 to the block length (3, 7 and 14 days).
- An estimate of how many Band A customer-days were under-served, using `customers`.
- Separating SCED-caused outages from `upstream_grid` ones in the band summary.

---

## E. Dataset and Resources

| File | Rows | Description |
|---|---|---|
| [`resources/data/outage_events.csv`](resources/data/outage_events.csv) | 24,393 | `event_id, feeder_id, start, end, cause, logged_by`. Times as `YYYY-MM-DD HH:MM`; blank `end` = never closed |
| [`resources/data/feeders.csv`](resources/data/feeders.csv) | 48 | `feeder_id, business_unit, band, customers` |
| [`resources/data/log_coverage.csv`](resources/data/log_coverage.csv) | 724 | `date, business_unit, logging_ok` (one row per business unit per day) |

| Item | Details |
|---|---|
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed from a simple on/off supply simulation, then corrupted with realistic logging defects. The company, feeders and places are fictional. The generator is in the assessor kit because it would reveal the planted answers. |
| **Licence** | CC BY 4.0 |
| **Integrity** | SHA-256 checksums are in `tests/test_contract.py`; the contract test fails if any file is edited. |
| **Band minimums** | From NERC's service-based tariff (link in §B), and provided as `BAND_MIN_HOURS` in `io.py`. |

**Known limitations (by design).** The log only tells you when the control room *recorded* an outage. Short interruptions that nobody logged are invisible. When an open event is closed at the next event, the true end time is unknown and your rule is a convention, not a fact: say so in the report.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-04-exploratory-data-analysis/DS-T1-010-hours-on-the-feeder
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract      # passes immediately
pytest                  # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `feeder_eda/` package | The tested conversion and uncertainty logic |
| 2 | `tests/test_member_*.py` (≥ 10 tests) | Proves your interval logic on cases you worked out by hand |
| 3 | `exploration.ipynb` or `exploration.py` | Reproduces every figure and number in the report |
| 4 | `outputs/answers.json`, `outputs/daily_supply.csv`, `outputs/feeder_summary.csv` | Machine-readable answers, checked against the hidden truth |
| 5 | `SUPPLY_REPORT.md` | Answers Q1–Q6 for the compliance manager, with intervals and caveats |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 7 | A 5–10 minute technical defence | Verifies understanding |

---

## G. Acceptance Criteria

⚙ = automated (public and hidden suites); ✍ = assessor.

1. ⚙ `pytest` passes all provided tests and all of your own in a clean environment.
2. ⚙ On the official logs **and** on two re-generated logs, `daily_supply` agrees with an independent one-minute-grid oracle to within 1e-6 hours on every covered feeder-day, and marks exactly the uncovered feeder-days. *Justification:* times are recorded to the minute, so the correct answer is exact.
3. ⚙ Issue counts (invalid and open events) match the generator's corruption log exactly.
4. ⚙ R5 and R7 reproduce the specified resampling procedure to 1e-9 for a fixed seed. *Justification:* the procedure is specified step by step precisely so that it can be checked; any other bootstrap is a different method.
5. ⚙ On every hidden dataset, `flag_misbanded` flags **every** planted under-delivering feeder and **no** feeder outside the planted set, except, optionally, one deliberately borderline feeder. *Justification:* the planted feeders deliver 4–6 hours less than their band minimum, which a correct 7-day block bootstrap detects with a wide margin; honest-but-borderline cases must not be held against you either way.
6. ⚙ `grid_collapse_days` returns exactly the planted collapse dates. *Justification:* collapse days affect every feeder, while ordinary `upstream_grid`-free days affect none, so a threshold of 0.8 separates them cleanly.
7. ⚙ The Band A cluster interval is wider than 1 hour on every hidden dataset. *Justification:* Band A contains feeders delivering both about 14 h and about 22 h, so an interval narrower than that has ignored between-feeder variation.
8. ✍ The report answers Q1–Q6 with numbers. Q3 and Q4 include intervals, Q2 and Q6 include the size and direction of each bias, and the report names at least one feeder whose evidence is **inconclusive** and explains why it was not flagged.
9. ✍ The report contrasts the cluster interval with a naive i.i.d. interval for Band A and explains, in plain language, why the naive one is misleading.
10. ✍ The exploration code regenerates every number and figure in the report.

---

## H. Evaluation Rubric

Full rubric with performance levels: **[rubric.md](rubric.md)**.

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 15 |
| Exploratory methodology | 10 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. Create a **private** GitHub repository named `clbg-DS-T1-010-<your-github-username>` and copy in `starter/`, `tests/`, `resources/` and `submission-template/`.
2. **Expected structure:**
   ```text
   clbg-DS-T1-010-<username>/
   ├── README.md                 # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── feeder_eda/
   ├── tests/                    # provided + test_member_*.py
   ├── resources/                # unchanged
   ├── exploration.ipynb | exploration.py
   ├── outputs/answers.json, daily_supply.csv, feeder_summary.csv
   ├── figures/
   ├── SUPPLY_REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** Your history is part of the evidence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue with the repository URL and commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Block length.** Re-run Q4 with block lengths 1, 3, 7, 14 and 28 days. Plot interval width against block length for the borderline feeder and explain the pattern.
2. **Customer impact.** Estimate under-served Band A customer-hours, with an interval, using `customers`.
3. **Who caused it?** Repeat Q3 excluding `upstream_grid` time. How much of each band's shortfall is outside SCED's control?
4. **A logging contract.** Write the five validation rules the control-room log should enforce at entry time to make this analysis unnecessary, and show how many events each rule would have rejected.

---

## K. Assessment Integrity

**AI tools are permitted** for learning (for example to explain the block bootstrap or pandas datetime handling), **not** to do the assessment for you. You must be able to explain and change every line you submit.

- **Disclose** all AI use in `AI_USE_AND_SOURCES.md` (tool, purpose, example prompt). Reasonable disclosed use is not penalised.
- **Cite** adapted code with links.
- **Collaboration:** general discussion of techniques is fine. Sharing code, answers or report text is not.
- **How your understanding is verified.** In the defence the assessor will:
  1. give you three intervals on paper (one crossing midnight, one duplicate, one open) and ask you to compute daily supply by hand, then show where your code does each step;
  2. ask why resampling days independently would make Q4 overconfident;
  3. ask for an **unseen modification** live, for example: treat an open event that is followed by its own duplicate differently; or add a `"partial"` coverage status; or change the cluster bootstrap to stratify by business unit;
  4. ask what extra data would let you say for certain whether the borderline feeder meets Band A.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | pandas datetimes, sorting, groupby; the idea of resampling. |
| **New skill developed** | Turning an operational event log into a trustworthy analytic series, and attaching dependence-aware uncertainty to the answers. |
| **Decisions the member must make** | How to implement the interval union efficiently and correctly; how to represent missing coverage; how to explain a borderline feeder; which figures expose the artefacts. |
| **What must be investigated independently** | Where the duplicates, gaps, open events and collapse days are, and how big each distortion is. The README says what to compute, not what the data contains. |
| **Why it's interesting** | It is a real Nigerian policy question with money attached, and each naive shortcut biases the answer in a different direction. |
| **Evidence of competence** | Exact agreement with a minute-grid oracle on re-generated logs, correct planted findings, hand-worked tests, and live tracing at defence. |
| **Misconceptions exposed** | "Sum the durations." "No outage logged means power was on." "181 days means a very precise estimate." "A mean below 20 proves non-compliance." |
| **Preparation for later work** | It leads into DS-05 (bootstrap and dependence), DS-07 (window functions over event data), DS-11 (validated pipelines) and DS-T2 time-series EDA. |

**Suggested approach** (optional): plot one feeder's raw events as a Gantt chart for one week before writing any code; implement and test `merge_intervals` first; build `daily_supply` on a three-day toy example before running it on the full log.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
