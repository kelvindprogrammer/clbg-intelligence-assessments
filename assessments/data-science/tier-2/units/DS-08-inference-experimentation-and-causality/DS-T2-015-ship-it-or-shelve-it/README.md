# DS-T2-015: Ship It or Shelve It? Auditing a Fintech A/B Test with Traps

> *Before asking whether the button worked, ask whether the experiment did.*

![Format: Investigation](https://img.shields.io/badge/format-investigation-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-015` |
| **Title** | Ship It or Shelve It? Auditing a Fintech A/B Test with Traps |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Competence |
| **Unit** | [DS-08: Statistical Inference, Experimentation and Causal Thinking](../README.md) |
| **Format** | Investigation (secondary: Comparative) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 2 · Engineering 2 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14–22 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | Hypothesis tests and confidence intervals for proportions; bootstrap or robust statistics; pandas; `pytest`. Helpful: [DS-T1-021](../../../../tier-1/units/DS-08-inference-experimentation-and-causality/DS-T1-021-how-sure-is-the-average/README.md) |
| **Skills developed** | Experiment validity auditing; Robust effect estimation; Multiple-testing control; Simulation of peeking; Decision rules under uncertainty; Experiment memo writing |
| **Technologies** | Python 3.10+, numpy, pandas, scipy, pytest |

---

## B. Problem Statement

**KoboPay**, a fictional Nigerian payments app, ran a two-week experiment on a new "one-tap airtime top-up" button. Half of users (arm A) saw the old screen; half (arm B) saw the button. The product manager has one question: **should we ship it?** The experiment export is `experiment.csv`, one row per user-assignment.

The easy analysis is a t-test on conversion and a t-test on revenue, followed by a green or red light. The experiment contains the traps that make that analysis unsafe. Real A/B tests fail in the same ways:

- **Randomisation can be broken.** If arm sizes are not what the design promised, a "sample ratio mismatch" means something went wrong with assignment or logging, and no effect estimate can be trusted.
- **Users can leak between arms.** A re-install or shared phone puts one user in both arms.
- **Revenue is heavy-tailed.** One very large top-up can turn a null result into a "significant" one.
- **You are testing two metrics.** Declaring victory on whichever looks better inflates the false-positive rate.
- **Peeking is tempting.** Checking daily and stopping when `p < 0.05` is not a 5% test.

You will build `abtest_audit`, a small audit-and-analysis library, and use it to decide, on the supplied export and on other experiments from the same platform, whether to ship, not ship, call it inconclusive, or declare the experiment invalid. Method choices (especially for revenue) are yours to make and defend; the tests check **behaviour**, not a particular algorithm.

The data is **synthetic**; no real user is described.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Audit** an experiment's randomisation and exposure before analysing outcomes.
2. **Estimate** a difference in proportions with an interval and a p-value.
3. **Choose and justify** a robust estimator for a heavy-tailed revenue metric, and compare it against the naive one.
4. **Control** the family-wise error rate across several metrics with Holm's procedure.
5. **Demonstrate by simulation** the false-positive inflation caused by peeking.
6. **Turn** statistical evidence into a decision rule with an explicit "invalid" outcome.
7. **Communicate** a decision, its evidence and its limits in a short memo.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `abtest_audit` package in [`starter/abtest_audit/`](starter/abtest_audit/). Signatures and return keys are fixed.

| ID | Requirement |
|---|---|
| **R1** | `srm_check(df, threshold=0.001) -> dict` with keys `n_a, n_b, p_value, flagged`. Counts are **unique users per arm**; test against an equal split with a chi-square goodness-of-fit test; `flagged = p_value < threshold`. |
| **R2** | `find_contaminated(df) -> set` of `user_id`s that appear in more than one arm. |
| **R3** | `conversion_effect(df, level=0.95)` on a one-row-per-user frame: keys `rate_a, rate_b, lift, ci_low, ci_high, p_value`, with `lift = rate_b - rate_a`, a Wald (unpooled) interval, and a two-sided pooled two-proportion z-test p-value. |
| **R4** | `revenue_effect(df, level=0.95, n_boot=2000, seed=0)`: keys `estimate, ci_low, ci_high, p_value, naive_p_value`. `estimate` is B minus A in revenue **per assigned user** (non-converters count as 0). `naive_p_value` is Welch's t-test on raw revenue. **The other fields come from a method you choose**, which must be robust: one user spending 40,000,000 must not move your estimate by more than 25% (plus a small constant), and a cluster of 14 big spenders (₦250,000 each, all in arm B) must not turn a null result into a significant one. Seeded and reproducible. |
| **R5** | `holm_adjust(pvals) -> list`: Holm-Bonferroni adjusted p-values, in input order, capped at 1 and monotone. |
| **R6** | `peeking_inflation(n_per_look, looks, reps, seed, alpha=0.05) -> float`: simulate `reps` A/A experiments with standard-normal outcomes, `n_per_look` new users per arm per look, a two-sided z-test (known variance 1) on all data so far after each look, stopping at the first rejection. Return the fraction of experiments that rejected at least once. |
| **R7** | `analyze_experiment(df, seed=0) -> dict` with keys `verdict, srm, n_contaminated, conversion, revenue, adjusted_p`. Procedure: run R1 on the raw frame; if flagged, `verdict="invalid"` and `conversion`, `revenue`, `adjusted_p` are `None`. Otherwise drop **all rows** of contaminated users, estimate R3 and R4, Holm-adjust the two p-values (`adjusted_p = {"conversion", "revenue"}`), then: `"do_not_ship"` if either metric is significantly worse (adjusted p < 0.05 and negative); else `"ship"` if conversion is significantly better (adjusted p < 0.05, positive); else `"inconclusive"`. |

### D.2 Engineering requirements

- Never mutate the input frame. Handle empty arms with a clear `ValueError`.
- Write **at least 10 tests of your own** in `tests/test_member_*.py`, including a regression test for each trap.
- Put your whale-robustness experiment in `analysis.py`: compare at least three revenue estimators (raw mean, winsorised, trimmed or log/median-based) on the supplied export and on a version with an injected whale.

### D.3 Privacy and responsibility

User-level payment data is personal data under the Nigeria Data Protection Act 2023. This export is synthetic, but your memo should report aggregates only and say what you would do differently with real user IDs (pseudonymisation, retention).

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/experiment.csv`](resources/data/experiment.csv): about 7,900 rows × 6 columns (`user_id, arm, assign_day, device, converted, revenue_ngn`), about 230 KB |
| **Provenance** | **Synthetic**, generated with a fixed seed. Conversion depends on device; revenue of converters is lognormal. |
| **Licence** | CC BY 4.0 (as this repository) |
| **Integrity** | SHA-256 checked by the contract test. Do not edit the file. |
| **Other scenarios** | Hidden tests run experiments from the same platform with other seeds and outcomes (including a broken-assignment build). Do not assume the supplied export is typical. |

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-08-inference-experimentation-and-causality/DS-T2-015-ship-it-or-shelve-it
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks data and scaffold
pytest                       # fails until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `abtest_audit/` package | The core technical evidence |
| 2 | `tests/test_member_*.py` (≥ 10 tests) | Regression tests for each trap |
| 3 | `analysis.py` and its output | Revenue-estimator comparison and the peeking curve |
| 4 | `REPORT.md` (≤ 900 words plus tables) from the [template](submission-template/REPORT.md) | A ship/no-ship memo for the product manager, plus AI-use declaration |
| 5 | A 7-minute defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Assessors check the criteria marked ⚙ with the public and hidden test suites, and the rest by hand.

1. ⚙ All public tests and your own pass from a clean environment.
2. ⚙ On hidden experiments (six seeds across four scenarios) `analyze_experiment` returns the correct verdict: `ship`, `invalid`, `inconclusive` (whale-driven false positive) and `do_not_ship`.
3. ⚙ `find_contaminated` finds exactly the injected contaminated users.
4. ⚙ On the whale scenario the naive Welch p-value is below 0.05 but your revenue p-value is above 0.05. *Justification:* the whale is the only source of the naive difference.
5. ⚙ `peeking_inflation` with 10 looks lies in [0.14, 0.25] (theory: about 0.19 for equally spaced looks) and with 1 look in [0.035, 0.065] over 4,000 repetitions.
6. ✍ `analysis.py` compares at least three revenue estimators and the report explains why you chose yours.
7. ✍ The memo states the decision, the primary evidence, what was excluded and why, and what you would need to see to change your mind.
8. ✍ The memo explains in plain language why the SRM check outranks every p-value.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and reasoning | 10 |
| Technical correctness | 25 |
| Method choice and justification | 15 |
| Implementation quality | 10 |
| Testing | 15 |
| Documentation and reproducibility | 5 |
| Critical thinking and limitations | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private GitHub repository** named `clbg-DS-T2-015-<your-github-username>` and copy in this assessment's `starter/abtest_audit/`, `tests/`, `resources/` and `submission-template/`. Put `abtest_audit/` at the repository root.
2. **Commit as you work.** Commit history is part of the evidence. A single "final" commit will be questioned at defence.
3. Include `REPORT.md` (from the [template](submission-template/REPORT.md)), which contains your AI-use declaration, and a short top-level `README.md` (at most 10 lines) saying how to run everything.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never replace the core requirements.

1. **Sequential testing done right.** Implement a group-sequential boundary (Pocock or O'Brien-Fleming) and show it holds the false-positive rate at 5% under the peeking simulation.
2. **Variance reduction.** Use `device` as a covariate (CUPED-style or stratification) and report the interval-width gain on conversion.
3. **Diagnose the SRM.** In the SRM scenario, find which segment is under-represented in B and say what bug could cause it.
4. **Power.** Compute the minimum detectable lift for the supplied sample size and for a half-sized experiment.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a statistical idea or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration inside `REPORT.md`: tool, purpose, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** code or methods adapted from documentation, papers or forums.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers or report text.
- **Defence (7 minutes).** The assessor asks why you chose your revenue estimator and what it gives up; asks what you would do if SRM were flagged on the day before launch; then gives an **unseen modification**, for example a third metric or a 70/30 design, to be implemented live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Hypothesis tests for proportions, p-values and intervals, basic bootstrap or robust statistics, pandas. |
| **New skill developed** | Treating experiment analysis as an audit with gates, not a single test. |
| **Decisions the member must make** | Which robust revenue estimator to use, how to handle contaminated users, and how to encode a ship decision. |
| **What must be investigated independently** | How badly a single whale and daily peeking distort results, using their own simulations. |
| **Why it's interesting** | The same export gives different decisions under naive and careful analysis, and other scenarios reverse the answer. |
| **Evidence of competence** | Correct verdicts across re-generated scenarios, behaviour-based robustness tests passing, and a memo that leads with validity. |
| **Misconceptions exposed** | 'Significant means ship.' 'SRM is a nuisance, not a verdict.' 'Outliers are real revenue, so keep them raw.' 'Peeking is harmless if I stop only at p < 0.05.' |
| **Preparation for later work** | Leads to DS-T3 causal inference where randomisation is absent, and to ML-14 style online evaluation. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
