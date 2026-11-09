# ML-T2-024: Salary Day at the Loan Desk: Micro-Batching a Scoring Service Under a Latency SLO

> *On the 25th, a digital lender's credit-scoring endpoint sees five times its normal traffic and a burst of push-notification clicks. Build the simulator, calibrate the cost curve from noisy timings, and choose a batching policy that holds a 100 ms promise.*

![Format: Optimization](https://img.shields.io/badge/format-Optimization-0366d6) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-024` |
| **Title** | Salary Day at the Loan Desk: Micro-Batching a Scoring Service Under a Latency SLO |
| **Subtrack** | ML Engineering |
| **Tier** | 2: Applied Competence |
| **Unit** | [ML-12: Model Deployment and Serving](../README.md) |
| **Format** | Optimization |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 4 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14–20 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Python (lists, deques, dataclasses); percentiles and latency; the idea of a queue; linear regression. No web framework needed |
| **Skills developed** | Discrete-event simulation of a serving queue; fitting a batch cost curve robustly; micro-batching trade-offs (throughput versus tail latency); load shedding; tuning a policy that generalises to unseen traffic |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

A digital lender in Lagos (fictional "Naira Quick Credit") scores every loan request with a gradient-boosted model behind a single CPU worker. The product promise is that a decision appears **within 100 ms for 99% of served requests**. Traffic is calm at 60 requests per second, but on the 25th of the month salaries land: for 30 seconds the rate jumps to about 300 per second, and at one moment a push notification sends 150 requests in 20 ms.

Scoring one request costs about 12 ms of fixed overhead plus a small cost per row, so serving requests one at a time (batch size 1) cannot keep up with the surge: the queue grows without bound and latency explodes. The obvious fix is **micro-batching**: wait briefly for several requests and score them together. But waiting adds latency, a big batch makes every member wait for the slowest, and an unbounded queue turns a burst into minutes of delay. A **queue cap** that sheds excess requests (the app falls back to a rules-based decision) protects the SLO at a price in shed requests, and finance allows at most 0.5% shed.

You will not deploy anything. You will build the instruments an engineer would use first:

1. A **cost-curve calibrator**: timings from the production CPU (batch sizes 1 to 64) contain occasional garbage-collection spikes three to six times the normal value. Fit `time = a + b·size` so spikes do not corrupt it.
2. An **exact simulator** of a single worker with a FIFO queue, a `max_batch`, a `max_wait_ms` timer and a `queue_cap`.
3. **Metrics** that mean what the SLO means.
4. A **tuner** that chooses a policy using one training trace and must then hold the SLO on traffic it has not seen, including a surge 25% bigger than anything in the training trace.

The simulator's semantics are specified exactly so the tests can check hand-computed traces. The choice of policy, the search, and what counts as "robust" are yours.

> **Why this matters beyond this task.** Serving is a queueing problem before it is an ML problem. Teams that tune batch size on average latency, or test on the same traffic they tuned on, discover on pay day that p99 is a property of the tail and of the next surge.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Fit** a linear cost curve to noisy timings with a method that tolerates outliers, and quantify the error.
2. **Simulate** a micro-batching worker exactly, including timers, full batches, busy servers and shedding.
3. **Measure** service quality with percentiles over served requests and a separate shed rate, and explain why mixing them hides failure.
4. **Trade** throughput against tail latency by choosing batch size, wait time and queue cap.
5. **Validate** a tuned policy on traces and surge levels it was not tuned on.
6. **Explain** which naive policies fail and why (batch 1; long wait; unbounded queue).

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `servesim` in [`starter/servesim/sim.py`](starter/servesim/sim.py). `Policy(max_batch, max_wait_ms, queue_cap)` is provided in `core.py`. Time is in milliseconds. Use numpy and the standard library.

| ID | Requirement |
|---|---|
| **R1** | `calibrate_cost(sizes, times_ms) -> (a, b)`: fit `time = a + b * size` with `a, b >= 0`. It must be exact on clean data and within 10% relative error of the truth on `datagen.make_timings` for any seed (3% of points are 3 to 6 times too large). The method is yours. |
| **R2** | `simulate(arrivals, policy, cost) -> dict` with keys `latency` (array, `nan` for shed requests), `shed` (bool array), `batches` (list of `(dispatch_ms, size, service_ms)`) and `arrivals`. Semantics: one worker, FIFO. When the worker is free and requests wait, the next batch is dispatched at the earliest time `d >= free_time` at which either `max_batch` requests are waiting or the oldest waiting request has waited `max_wait_ms`. Requests arriving at or before `d` and while fewer than `queue_cap` requests are waiting join the queue; otherwise they are shed at arrival. The batch is the first `min(waiting, max_batch)` requests and takes `a + b * size`. Latency is completion minus arrival. `max_batch` and `queue_cap` below 1 raise `ValueError`. |
| **R3** | `summarize(result, slo_ms) -> dict` with `p50`, `p99` (over **served** requests, `np.percentile(..., method="higher")`), `shed_rate`, `mean_batch`, `utilisation` (total service time divided by the span from first to last arrival) and `slo_ok` (a `bool`: `p99 <= slo_ms`). |
| **R4** | `tune_policy(arrivals, cost, slo_ms=100.0, max_shed=0.005) -> Policy`. It receives one training trace and the **calibrated** cost. The returned policy is judged on unseen traces simulated with the **true** cost. Raise `ValueError` if nothing is feasible. |

### D.2 Engineering requirements (mandatory)

- Deterministic; `simulate` must not modify its inputs and must run in under one second on a 13,000-request trace.
- A single metrics function is used for every candidate policy.
- At least **8 tests of your own** in `tests/test_member_*.py`, including a conservation test (served + shed equals arrivals) and a test that a one-worker server never runs two batches at once.
- `experiments.py` regenerates every number and figure in `REPORT.md`: the latency-versus-shed trade-off over a grid of policies, with **at least 5 different seeds**.

### D.3 Responsibility

The data is synthetic. In the report, write one paragraph on who is affected when requests are shed during the surge (the fallback rules may decline creditworthy applicants or approve riskier ones), whether shedding falls evenly on users, and how you would monitor the fallback's decisions.

### D.4 Optional enhancements

- A second worker (cost: twice the compute) and the break-even traffic at which it beats a tuned single worker.
- A dynamic policy that shortens `max_wait_ms` as the queue grows.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_arrivals(seed, surge=1.0)` (about 13,000 arrival times in ms over 90 s) and `make_timings(seed)` (84 noisy batch timings plus the true `(a, b)`) |
| **Provenance** | **Synthetic**, deterministic given the seed; no real lender, customer or request |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Traffic** | 60 req/s for 30 s, 300 req/s times `surge` for 30 s, 60 req/s for 30 s, plus a 150-request burst at 45 s |
| **Cost curve** | Truth `a` in [9, 15] ms, `b` in [0.6, 1.2] ms per row, drawn per seed |
| **SLO** | `datagen.SLO_MS = 100`, shed at most 0.5% on the tuning trace |
| **Size** | Nothing committed; generators are instant |

Hidden tests use other seeds, a 120 ms SLO and 25% heavier surges.

**Setup**

```bash
cd assessments/ml-engineering/tier-2/units/ML-12-model-deployment-and-serving/ML-T2-024-salary-day-at-the-loan-desk
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `servesim/` package | Calibrator, simulator, metrics and tuner |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Includes conservation and one-worker tests |
| 3 | `experiments.py` | Reproduces the trade-off table and figures over 5 or more seeds |
| 4 | `REPORT.md` (at most 1,500 words plus tables), from the [template](submission-template/REPORT.md) | Policy recommendation for the platform team; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `simulate` reproduces every hand-computed trace in the public tests, including full-batch dispatch, timeout dispatch, shedding and growing batches on a busy server.
3. ⚙ `calibrate_cost` is exact on clean data and within 10% of the truth for seeds 1 to 3 (and, in the hidden tests, with heavier spikes).
4. ⚙ **Generalisation.** The tuned policy, evaluated with the true cost on fresh seeds, has p99 at most 100 ms and shed rate at most 1%; on a 25% heavier surge, p99 at most 100 ms and shed at most 2%. *Justification:* the reference policy reaches p99 near 30 to 70 ms and shed near 0.3 to 0.7%; the burst of 150 requests means some shedding is unavoidable under any cap that keeps the burst's tail inside the SLO, so 1% leaves room above the 0.5% tuning limit for sampling noise.
5. ⚙ Naive policies (batch 1 with unbounded queue; batch 64 with 200 ms wait) are shown by the tests to violate the SLO.
6. ⚙ Results are deterministic and inputs are never modified.
7. ✍ The report shows the latency-versus-shed trade-off over a policy grid and explains the shape: why a longer wait helps utilisation until it hurts p99, and why a queue cap is the only defence against the burst.
8. ✍ The report states what the tuner assumed about future traffic and how tuning on the stressed trace changed the choice.

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

1. **Create your own private repository** named `clbg-ML-T2-024-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `servesim/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Two workers.** Extend the simulator and find the traffic level at which a second worker beats batching alone.
2. **Adaptive wait.** Let the timer shrink with queue length and compare with the best static policy beyond the noise.
3. **Variable service time.** Add a heavy-tailed service noise and see which policy parameter becomes fragile.
4. **Priority.** Serve returning customers first and measure what it does to new customers' tail.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why a larger `max_wait_ms` can lower p99 during the surge but raise it during calm traffic; (2) ask what happens to your policy if the per-row cost `b` doubles after a model upgrade and how the tuner would detect it; (3) give an unseen modification, for example an SLO of 60 ms or a shed limit of 0.1%, and ask which parameter changes first and what you expect.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Queues, percentiles and a linear fit. No serving framework or cloud account. |
| **New skill developed** | Reasoning about an ML service as a queue with a fixed cost per call and a tail-latency promise. |
| **Decisions the member must make** | How to fit the cost curve robustly; the policy grid; how to make a tuned policy robust to heavier traffic; how to treat shed requests in metrics. |
| **What must be investigated independently** | Why batch 1 fails at 300 req/s, why p99 over served requests needs a separate shed rate, and what the burst does to every cap. |
| **Why it is interesting** | Pay-day traffic punishes policies that were tuned for the average. The tuner has to anticipate a surge it never saw. |
| **Evidence of competence** | Exact hand traces, a calibrator within 10%, a policy that holds the SLO on fresh and heavier traffic. |
| **Misconceptions exposed** | 'Bigger batches are always faster.' 'Average latency is fine.' 'Add a queue and nothing is lost.' 'Tune and test on the same trace.' |
| **Preparation for later work** | Leads into ML-12 Tier 3 (rollout and rollback) and ML-13 monitoring and capacity planning. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
