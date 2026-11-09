# ML-T3-023: The Month Before the Labels Arrive: Designing a Safe Rollout for a Replacement Credit Model

> *A new credit model looks better offline. Loan outcomes take seven days to mature. In between, a share of real customers will be scored by it. Design the shadow, canary and rollback policy that decides when to trust it, and defend how much harm you are willing to risk to find out.*

![Format: System design](https://img.shields.io/badge/format-System%20design-0366d6) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-023` |
| **Title** | The Month Before the Labels Arrive: Designing a Safe Rollout for a Replacement Credit Model |
| **Subtrack** | ML Engineering |
| **Tier** | 3: Advanced and Research-Grade |
| **Unit** | [ML-12: Model Deployment and Serving](../README.md) |
| **Format** | System design |
| **Difficulty** | Technical 4 · Mathematical 3 · Research 4 · Engineering 4 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 24–36 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Two-proportion tests and confidence intervals; A/B testing concepts; what a champion/challenger deployment is; basic sequential-testing awareness (peeking). Recommended: ML-T1-021 and ML-T2-024 |
| **Skills developed** | Designing a staged rollout (shadow, canary, ramp, rollback) under delayed labels; choosing immediate guardrails versus lagged outcome tests; segment-level safety; non-inferiority testing; sequential-testing risk; quantifying harm and delay as a trade-off; writing auditable automated decisions |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

A lender serving agent-banking customers across the Niger Delta (fictional "Delta Agent Credit") has trained a replacement credit-scoring model. Offline, it looks better. The business wants it live, but the company's last model swap lowered approvals for new-to-credit customers for six weeks before anyone noticed, because the overall default rate looked fine. This time the data science lead wants an **automated rollout controller** and a design the risk committee can sign off.

The difficulty is built into how credit works. A loan approved today shows whether it defaults only **seven days later** (the label lag; ten in some products). Meanwhile traffic must be routed. The stages are fixed: **shadow** (the candidate scores every request but decides nothing), then **2%**, **10%**, **50%** and **100%** of traffic. At each daily check the controller sees only noisy observations and chooses `hold`, `advance` or `rollback`. A candidate can fail in four ways:

- **Uniformly worse:** default rates rise about 18% in every segment, sometimes with a visible rise in approval rate and sometimes with no trace in it.
- **Hidden segment harm:** established customers (75% of traffic) improve by 10%, but new-to-credit customers (25%) default 40% more often. The overall rate looks almost flat.
- **Slow:** latency exceeds the 300 ms SLO although accuracy is fine.
- **Neutral or good:** the candidate is no worse, or 12% better, and should be promoted without unnecessary delay. (Neutral ones may go either way.)

You are given a deterministic test bench (`resources/datagen.py`) that runs a controller against hundreds of hidden candidates and scores it on three things: whether harmful candidates are rolled back, whether good ones are promoted in reasonable time, and the total **harm** (expected excess defaults among exposed approved loans, plus 0.02 incident-equivalents for each request that hits a candidate that breaches the latency SLO) compared with a naive fixed schedule that advances every four days.

This is a system-design task. The tests fix the statistical instruments, the controller's interface and the bars it must clear. **Everything else is yours to design and defend:** the evidence required to enter each stage, how immediate proxies and lagged outcomes are combined, how segments are protected, how many looks you can afford before peeking inflates false alarms, what a rollback means operationally, and what the controller must log so a human can audit it.

> **Why this matters beyond this task.** Most model failures in production are not caught by a pre-deployment metric. They are caught (or missed) by the rollout process. A good rollout design converts "we hope the new model is better" into a bounded, measurable risk.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Design** a staged rollout (shadow, canary, ramp) with explicit entry criteria and a bounded exposure at each stage.
2. **Combine** immediate proxy signals (latency, approval rate) with lagged outcome evidence and explain what each can and cannot detect.
3. **Protect** a minority segment whose harm the overall metric hides, with a stated minimum sample and decision rule.
4. **Test** non-inferiority with an explicit margin rather than significance of a difference, and quantify the effect of repeated looks.
5. **Evaluate** the design with a simulator, reporting harm, delay and missed-detection rates with uncertainty across worlds you did not tune on.
6. **Document** an auditable decision record and an operational runbook for rollback, including who is notified and what happens to in-flight loans.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `rolloutlab` in [`starter/rolloutlab/`](starter/rolloutlab/). Use only the standard library, numpy and scipy.

**Observation passed to `decide(obs)` each day** (cumulative counts; the index is the segment, 0 for established customers and 1 for new-to-credit):

| Key | Meaning |
|---|---|
| `day`, `stage`, `days_in_stage`, `frac` | Day number, stage index (0 = shadow, 1 to 4 = 2%, 10%, 50%, 100%), days spent in this stage so far, traffic share of the candidate |
| `champ` | Per segment: `n` requests served by the champion, `app` approvals, `n_m` approvals whose outcome has matured, `d_m` defaults among them |
| `cand` | The same for requests served by the candidate (zero while in shadow) |
| `shadow` | `n` and `app`: for requests the champion served, how many the candidate **would** have approved |
| `lat_cand`, `lat_champ` | Today's noisy p95 latency in ms (candidate's is available in shadow too) |

`advance` at stage 4 ends the rollout as **promoted**; `rollback` ends it as **rolled back**; a rollout that is neither by day 60 is **stalled** (its exposure and harm continue to accrue).

| ID | Requirement |
|---|---|
| **R1** | `two_prop_z(x1, n1, x2, n2) -> float`: the pooled two-proportion z statistic for `p1 − p2`; `0.0` if either sample is empty or the variance is zero. |
| **R2** | `noninferior(d_c, n_c, d_k, n_k, margin_rel, z) -> bool`: True iff `(p_c − p_k) + z·se ≤ margin_rel·p_k` with the unpooled `se = sqrt(p_c(1−p_c)/n_c + p_k(1−p_k)/n_k)`; False if either sample is empty (no evidence is not safety). |
| **R3** | `RolloutController(info)` with `decide(obs) -> "hold" | "advance" | "rollback"` and a non-empty string `last_reason` updated on every call. `info` has `stages`, `label_lag`, `slo_ms` and `horizon`. The controller must not read anything but `obs` and `info`, and must work when the lag, base rates, traffic and the approval-rate signature of failures change. |

### D.2 Study and engineering requirements (mandatory)

- **Design document first.** `DESIGN.md` states, before you run the bench, the stage gates, the guardrails with thresholds and their justification, the segment rule, the false-alarm budget (how often you accept rolling back a good model) and the harm budget. Changes after seeing bench results are logged in the report.
- **Ablations**, each over **at least 5 seeds of `evaluate`** (n at least 150 candidates each): (a) no approval-rate proxy; (b) no per-segment checks (pooled only); (c) no minimum dwell or sample requirements per stage; (d) a different number of stages (for example, skip the 2% stage); (e) peeking sensitivity, comparing your per-day thresholds with a conservative sequential boundary. Report harm, delay, `caught` and `good_promoted` with intervals.
- **Operating curve.** A figure of harm against median time-to-promote for at least five threshold settings, with the fixed-schedule baseline on it.
- **Robustness.** Report performance in at least three worlds that differ from the default (lag, base rates, traffic level, signature rate) and say which assumption of yours is most fragile.
- Deterministic; at least **10 tests of your own** in `tests/test_member_*.py` (including a no-evidence-no-advance test and a rollback-is-terminal test); `experiments.py` regenerates every number and figure.

### D.3 Responsibility

An automated rollback or a stalled rollout affects real customers. In the report, write one paragraph on who bears the cost of a *false* rollback (customers who would have benefited from a better model) and of a *missed* one (customers who default or are wrongly declined), on why new-to-credit customers need an explicit rule, and on the human approval you require before a model reaches 50% and 100%. State what you would log to answer a regulator's question about a specific customer's decision, consistent with NDPA 2023 data-minimisation.

### D.4 Optional enhancements

- A Bayesian or alpha-spending sequential test and a comparison with your fixed thresholds.
- A cost-of-delay model: each day the better model is not live loses value, so the threshold is chosen to minimise expected total cost.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Test bench** | [`resources/datagen.py`](resources/datagen.py): `make_candidates(n, seed, mix, approval_shift)`, `run_rollout(factory, candidate, seed, params)`, `evaluate(factory, n, seed, params, mix, approval_shift)` and the baseline `ScheduleController` |
| **Provenance** | **Synthetic**; a stochastic simulator of two customer segments, delayed outcomes and candidate effects. No real lender, customer or loan |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Default world** | 3,000 requests a day, 75% / 25% segments, champion default rates 8% / 14% among approved, approval rates 55% / 45%, label lag 7 days, SLO 300 ms, horizon 60 days |
| **Candidate kinds** | Good (35%), neutral (15%), bad (20%), segment-bad (20%), slow (10%) |
| **Failure signatures** | Half of the bad and segment-bad candidates raise the approval rate by `approval_shift` (4 points by default); the rest leave no trace in it. Slow candidates breach the latency SLO |
| **Scoring** | `evaluate` returns `caught` (harmful candidates rolled back), `harmful_promoted`, `good_promoted`, `good_median_days`, `harm`, `baseline_harm`, `harm_ratio` and per-kind detail |
| **Size** | Nothing committed; a 150-candidate evaluation takes about a second |

Hidden tests use other seeds, lags (5 to 10 days), base rates, traffic levels, segment shares, failure mixes, and a world in which no failure leaves an approval-rate trace.

**Setup**

```bash
cd assessments/ml-engineering/tier-3/units/ML-12-model-deployment-and-serving/ML-T3-023-the-month-before-the-labels-arrive
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `rolloutlab/` package | Statistics (R1, R2) and the controller (R3) |
| 2 | `DESIGN.md`, committed before the first bench run | Stage gates, guardrails, thresholds, false-alarm and harm budgets |
| 3 | `tests/test_member_*.py` (at least 10 tests) | Includes no-evidence-no-advance and rollback-terminal tests |
| 4 | `experiments.py` | Reproduces the ablations (5 or more seeds), operating curve and robustness table |
| 5 | `REPORT.md` (at most 3,000 words plus tables), from the [template](submission-template/REPORT.md) | Rollout design, evidence and runbook; carries the AI-use declaration |
| 6 | A 10-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `two_prop_z` and `noninferior` match the hand-computed values, including the empty-sample cases, and the hidden values.
3. ⚙ The controller returns only valid actions, sets a non-empty `last_reason` on every call, and is deterministic.
4. ⚙ **Safety and speed.** On the public bench (150 candidates, seed 2026): at least **90%** of harmful candidates are rolled back, at most **5%** are promoted, at least **75%** of good candidates are promoted with a median of at most **40 days**, and total harm is at most **35%** of the fixed four-day schedule's. *Justification:* the reference rolls back 97% of harmful candidates, promotes 100% of good ones with a median of 26 days, and has a harm ratio of about 0.12; the silent half of the harmful candidates can only be caught by lagged outcomes, which sets a floor on harm, so 0.35 leaves room for a more cautious design.
5. ⚙ **Robustness.** In worlds with other lags, base rates and traffic, the bars are at least 85% caught, at least 65% of good candidates promoted and a harm ratio at most 0.45; in the world with no approval-rate signature the bars are 75% caught and 0.5.
6. ✍ `DESIGN.md` predates bench runs in the commit history and every threshold in the controller is justified there or in the report.
7. ✍ The ablations show which component buys which part of the safety (proxy guardrail, segment checks, sample minimums, stages, peeking control) with intervals over 5 or more seeds, and the report names the one that matters most.
8. ✍ The report has an operating curve, a robustness table, a runbook (what a rollback does, who is told, what happens to loans approved by the candidate) and an honest statement of which assumption is most fragile.

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

1. **Create your own private repository** named `clbg-ML-T3-023-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `rolloutlab/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Cost of delay.** Add a per-day value for a good model being live and choose thresholds that minimise expected total cost; compare with your fixed-bars design.
2. **Sequential tests.** Replace the per-day z thresholds by an alpha-spending boundary and quantify the change in false rollbacks and detection time.
3. **Adaptive stages.** Let the controller choose the next traffic share from the evidence so far and show whether it beats the fixed ladder.
4. **Compound failures.** Extend the bench with a candidate that is good for six weeks and then degrades, and design the post-promotion monitor that would catch it.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why your controller does not simply wait for full outcome evidence at 2%, and what that costs in days and in how many more customers ultimately see a bad model; (2) ask which failure kind your design catches latest and how many customers are exposed before it does; (3) give an unseen modification, for example a label lag of 30 days or a segment of only 3% of traffic, and ask which gates and sample minimums break first and how you would change the design.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Two-proportion tests, confidence intervals and the idea of A/B testing. No MLOps platform or cloud service. |
| **New skill developed** | Turning a deployment from a leap of faith into a bounded, measurable risk with explicit gates, guardrails and a rollback runbook. |
| **Decisions the member must make** | Evidence required at each stage; which proxy guardrails to trust; how to protect the minority segment; false-alarm and harm budgets; how to treat repeated looks; what to log. |
| **What must be investigated independently** | Why half the harmful candidates are invisible to proxies, why pooled outcomes hide segment harm, and how peeking inflates false rollbacks. |
| **Why it is interesting** | Every safety measure costs time, and time costs customers. The design is an explicit trade-off, measurable on a simulator. |
| **Evidence of competence** | Exact statistics, safety and speed bars met on public and hidden worlds, ablations that attribute safety to components, and a runbook. |
| **Misconceptions exposed** | 'If offline metrics improved, a quick canary is enough.' 'A flat overall default rate means no one is harmed.' 'Proxy metrics are enough.' 'Wait for significance of improvement.' |
| **Preparation for later work** | Leads into ML-13 monitoring and drift detection, ML-14 subgroup performance, and capstone work on production ML. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
