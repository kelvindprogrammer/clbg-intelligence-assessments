# ML-T2-026: Payday Is Not Drift: Designing a Feature-Drift Monitor for a Digital Lender's Application Stream

> *The dashboard shouted 'drift' every month-end and nobody believed it when a real shift arrived. Design a monitor people can trust.*

![Format: System-Design (secondary: Investigation)](https://img.shields.io/badge/format-system-design-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-026` |
| **Title** | Payday Is Not Drift: Designing a Feature-Drift Monitor for a Digital Lender's Application Stream |
| **Subtrack** | ML Engineering |
| **Tier** | 2: Applied Competence |
| **Unit** | [ML-13: ML Pipelines, MLOps and Monitoring](../README.md) |
| **Format** | System-Design (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14-20 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Empirical CDFs, quantiles, basic hypothesis testing, numpy. Recommended: ML-T1-023 and a first unit on evaluation. |
| **Skills developed** | Drift statistics; false-alarm budgeting; seasonality-aware reference design; sample-size-aware thresholds; monitor evaluation |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Naira Quick (fictional) is a digital lender in Lagos. Applicants apply through an app, and a credit model scores each application. Seven features are logged daily: `loan_amount_ngn, monthly_income_ngn, age, app_hour, device_new, credit_checks_6m, formal_employer`. The data team's first monitor computed the Population Stability Index (PSI) of each feature for each day against all of the past 90 days and alarmed when any value exceeded 0.2, the usual rule of thumb. It alarmed **13 times in 70 days**, always in the last week of the month, when salaried people apply for larger loans earlier in the day. The team muted it. Then in a later quarter a new partner channel started sending younger, lower-income applicants who apply at night on new devices, and nobody noticed for three weeks.

You will build the statistics and then **design** a monitor under a stated operating requirement: **at most about one false alarm per 100 days** across all features, **detection of a real shift within a week**, and correct behaviour on quiet days (public holidays when only 40 applications arrive). How you meet this is yours to decide. The brief names three traps and leaves their solution open:

1. **Predictable seasonality.** The month-end pattern is real, repeats every 30 days, and is not drift. What should the reference be?
2. **Many tests, many days.** Seven features tested daily for months produce false alarms by chance. What per-test error rate is consistent with the budget?
3. **Batch size.** A daily statistic computed on 40 rows is far noisier than on 400. A fixed threshold is either blind on busy days or hysterical on quiet ones.

The data are a synthetic stream (see §E). The tests fix interfaces, the numerical definitions of the statistics, and operating bars; the monitor design, statistic and thresholding rule are yours to choose and defend.

> **Why this matters beyond this task.** A monitor that cries wolf is switched off, and a switched-off monitor is worse than none. Most monitoring failures in production are failures of alarm design, not of statistics.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** PSI (with reference-quantile bins and an explicit floor for empty bins) and the exact two-sample KS statistic with ties.
2. **Calibrate** an alarm threshold from a null distribution to a stated false-alarm rate, and correct for testing several features.
3. **Design** a reference that removes known seasonality without hiding real drift.
4. **Make** the alarm rule sensitive to batch size so quiet days neither alarm spuriously nor hide a real shift.
5. **Evaluate** a monitor as a decision system: false alarms, detection delay and a gradual versus abrupt change.
6. **Argue** the limits of covariate-drift monitoring when labels arrive late or never.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement [`driftwatch`](starter/driftwatch/). Use only numpy and the standard library in the package.

| ID | Requirement |
|---|---|
| **R1** | `psi(ref, cur, bins=10)`: bin edges are the interior quantiles `np.quantile(ref, linspace(0,1,bins+1)[1:-1])` with duplicates removed (so binary and tied features work); values are assigned with `np.searchsorted(edges, x, side="right")`; bin proportions below `1e-4` are replaced by `1e-4` (no renormalisation); return `sum((c - r) * ln(c / r))`. Identical samples give 0. |
| **R2** | `ks_stat(a, b)`: the exact two-sample statistic `max |F_a - F_b|` over all observed values, with ties handled correctly (evaluate both ECDFs at every distinct value). |
| **R3** | `calibrate_threshold(null_stats, target_far)` returns a threshold `t` such that alarming on `stat > t` fires on at most `floor(target_far * len(null_stats))` of the null values, and on as many as possible within that limit. `bonferroni_alpha(total_alpha, n_tests)` returns the per-test level. |
| **R4** | `DriftMonitor(ref_batches, names, false_alarms_per_100d=1.0)` is built from reference batches `[(day, X), ...]`. `update(day, X)` returns the list of feature names in alarm for that day. It must be **causal** (the answer for a day uses only that day and earlier information, and the reference), must not mutate its inputs, and must respect the false-alarm budget parameter. Statistic, windowing, threshold rule and seasonality handling are your design. |
| **R5** | `evaluate(monitor, stream, drift_day)` feeds `stream` in order and returns a dict with `alarm_days`, `false_alarm_days` (alarm days before `drift_day`), `n_false_alarms`, `detected` (any alarm on or after `drift_day`) and `delay` (first such day minus `drift_day`, or `None`). |

### D.2 Engineering requirements (mandatory)

- Deterministic: any randomness has an explicit seed, and `update` must not depend on call history other than through documented, causal state.
- Do not use `drift_day`, the known period, or the generator internals inside the monitor. If you rely on a period of 30 days you must **estimate it from the reference data** and show the evidence in the report (the hidden tests offset the reference window).
- At least **10 tests of your own** in `tests/test_member_*.py`, including a causality test, a test that quiet days do not alarm, and a calibration test on a synthetic null.
- `experiments.py` regenerates every number and figure in `REPORT.md`: the naive PSI monitor versus yours on at least **5 seeds**, with false alarms, delay and the effect of removing each design element (an ablation).

### D.3 Responsibility

The data are synthetic and fictional. In the report, write one paragraph on what a drift alarm triggers in practice at a lender (review of a credit model that decides who gets a loan), why a new acquisition channel of young, lower-income applicants may be a *fairness* question as well as a statistical one, and how the **Nigeria Data Protection Act 2023** bears on monitoring: monitor aggregate feature distributions, not individual customer records, and do not log personal identifiers in monitoring stores. Cite only what you are sure the Act provides, and say when you are unsure.

### D.4 Optional enhancements

- Add a multivariate detector (for example a domain classifier trained to separate reference from current data) and compare its power with the per-feature tests.
- Add alarm de-duplication and a severity level that uses both PSI and KS.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/lendstream.py`](resources/lendstream.py): `make_stream(seed, days=240, drift_day=None, ramp_days=1, share=0.35, batch=400, low_volume=())` returns `(batches, names)` where `batches` is a list of `(day, X)` |
| **Provenance** | **Synthetic**, deterministic given the seed (each day depends only on seed and day); no real applicant or lender |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Recommended protocol** | Reference = days 0 to 89; monitor days 90 to 239; the new channel begins at `drift_day` (160 in the tests; the monitor never receives this value) |
| **Size** | Nothing is committed; `python resources/lendstream.py --out DIR --seed 3` writes a CSV of about 20 MB |

Hidden tests use other seeds, batch sizes of 200, a longer horizon, a gradual ramp, a reference window that does not start at day 0, and different quiet days.

**Seasonality note.** The brief tells you that alarms cluster at month-end. It does not tell you the exact period or which features move. Finding out is part of the task.

**Setup**

```bash
cd assessments/ml-engineering/tier-2/units/ML-13-ml-pipelines-mlops-and-monitoring/ML-T2-026-payday-is-not-drift
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `driftwatch/` package | Statistics, monitor and evaluation harness |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Includes causality, quiet-day and calibration tests |
| 3 | `experiments.py` | Reproduces the comparison and ablation (5 or more seeds) |
| 4 | `REPORT.md` (at most 1,800 words plus tables), from the [template](submission-template/REPORT.md) | Monitor design memo for the data team lead; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `psi` and `ks_stat` match the hand-computed values, including empty bins, ties and binary features.
3. ⚙ `calibrate_threshold` keeps the empirical null alarm rate at or below the target and is not wastefully conservative (within 0.01 on a 700-point null in the hidden test).
4. ⚙ **False alarms.** On no-drift streams of 150 monitored days that include salary weeks and low-volume days, `n_false_alarms` is at most **2** per stream in the public tests (at most 5 in total over five hidden seeds). *Justification:* the operating requirement is one per 100 days; the reference produces 0, and a bar of 2 per 150 days leaves room for honest, less conservative designs.
5. ⚙ **Detection.** On the abrupt new channel the first alarm falls within **7 days** of onset on every public seed and on at least 4 of 5 hidden seeds; on a 30-day gradual ramp within **25 days** on at least 2 of 3 public and 3 of 5 hidden seeds. *Justification:* the reference detects abrupt shifts on day 0 and ramps in 3 to 10 days; the bars allow for weaker but still useful designs.
6. ⚙ **Causality and purity.** Alarms for the first 30 days are identical whether or not later days are ever shown; inputs are not mutated.
7. ✍ The report shows the naive PSI monitor's false alarms, explains each design element, includes an ablation, and states what the monitor cannot see (drift in label relationship, drift inside the reference window).

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

1. **Create your own private repository** named `clbg-ML-T2-026-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `driftwatch/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Seasonality discovery.** Estimate the period automatically from the reference and show it works on a stream with a 28-day cycle.
2. **Sequential test.** Replace per-day tests with a CUSUM or sequential probability ratio test, and compare delay at a matched false-alarm budget.
3. **Label delay.** Add outcome labels that arrive 45 days later and show what performance monitoring can and cannot add to your covariate monitor.
4. **Alarm triage.** Rank alarms by expected effect on the score distribution rather than by feature.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why a PSI threshold of 0.2 has no stated error rate and what yours does; (2) ask what happens to your false-alarm rate if you add 20 more features; (3) give an unseen modification, for example a 7-day weekly cycle added to the stream or a batch size of 20, and ask which part of your design breaks first.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | ECDFs, quantiles and the idea of a null distribution. No sequential analysis or process control theory. |
| **New skill developed** | Designing an alarm, not just computing a statistic: reference, multiplicity and sample size together decide whether a monitor is usable. |
| **Decisions the member must make** | Reference design under seasonality; statistic; per-test level; how thresholds scale with batch size; how to evaluate. |
| **What must be investigated independently** | Which features carry the seasonality, its period, and how much null noise a given batch size produces. |
| **Why it is interesting** | The popular PSI-0.2 rule fails here in a way the member can measure and then fix. |
| **Evidence of competence** | Zero-to-few false alarms across re-seeded streams, fast detection, a causal implementation, and an ablation showing what each element contributes. |
| **Misconceptions exposed** | 'PSI above 0.2 means drift.' 'Any change in a feature is drift.' 'One threshold fits every batch size.' |
| **Preparation for later work** | Leads into ML-13 Tier 3 retraining policy, where alarms drive costly actions, and into ML-09 and ML-05 evaluation under shift. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
