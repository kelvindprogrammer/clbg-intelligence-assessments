# DS-T1-012: The Fuel Queue

> *Five evenings of a filling-station log during a fuel scarcity, one formula that looks right, and a staffing decision that depends on knowing when the formula is wrong.*

![Format: Implementation](https://img.shields.io/badge/format-implementation-0366d6) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-012` |
| **Title** | The Fuel Queue: Simulating a Filling Station During Scarcity |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-05: Probability and Statistics](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 3 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 10–16 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, no internet after setup. The full pipeline runs in under a minute |
| **Recommended prerequisites** | Python functions and modules; NumPy arrays and `numpy.random.Generator`; the exponential and Poisson distributions; what a confidence interval is; running `pytest` |
| **Skills developed** | Discrete-event simulation; queueing theory (M/M/c, Erlang C, Little's law); validating a simulator against theory; output analysis for correlated series (warm-up, batch means); input modelling from operational logs; decisions under simulation and input uncertainty |
| **Technologies** | Python 3.10+, NumPy, SciPy (`scipy.stats.t` only), pandas, pytest |

---

## B. Problem Statement

It is the third week of a petrol scarcity. A filling station on a busy road in Port Harcourt (fictional, but typical) opens only **four** of its pumps in the evening peak, from 16:00 to 20:00, because it is short of attendants. Queues stretch onto the road. Some drivers look at the line and drive off. Okada riders and keke drivers wait beside motorists, and a steady stream of people arrive with stacks of jerrycans that take a long time to fill.

The station manager has a budget to bring in casual attendants for the next scarcity and asks one question:

> **How many pumps must be staffed in the evening peak so that no more than 1 driver in 10 waits more than 10 minutes before reaching a pump?**

The supervisor logged five scarcity evenings: every arrival, its vehicle type, whether the customer was served or **balked** (left without joining the queue), and the service time of each customer served. You have that log.

A colleague has already answered the question in a spreadsheet: "Mean service is about 3.9 minutes, arrivals about 1 a minute, so plug it into the Erlang C formula: 5 pumps." Your job is to build the tools that check that answer properly, and to say how sure you are.

What makes it hard:

- **The textbook model is almost right.** The M/M/c queue assumes exponential service times. Jerrycan customers make service times far more variable than an exponential distribution allows, and the tail of the waiting-time distribution is where the decision is made.
- **The log measures throughput, not demand.** Drivers who balked were part of the demand the station must plan for, even though they never reached a pump.
- **Simulation output is correlated.** Consecutive customers' waits are strongly dependent, so the usual `mean ± 1.96·sd/√n` interval is far too narrow.
- **An unstable system still produces numbers.** Simulate a queue whose load exceeds its capacity for a finite time and you get a finite, plausible-looking average wait. It means nothing.
- **Two kinds of uncertainty.** Simulation noise (reduced by running longer) and input uncertainty (only five evenings of data) are different things, and only one of them goes away with more computing.

**Known facts from the station** (the only documentation you get):

- Each evening's observation window is exactly 240 minutes; `arrival_min` is minutes after 16:00.
- All open pumps are identical and any customer can use any pump. Customers are served first come, first served.
- Arrivals in the peak are believed to be roughly steady (no strong trend within the four hours).
- The manager's service standard is *P(wait in queue > 10 minutes) ≤ 0.10*. "Wait" means the time from arriving to reaching a pump, not including the time at the pump.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Derive** the M/M/c steady-state results (the Erlang C probability of waiting, the mean wait and the waiting-time tail) from the birth–death balance equations, and state the assumptions each step needs.
2. **Implement** a correct discrete-event simulation of a first-come-first-served multi-server queue and prove its correctness with tests against hand calculations and an independent recursion.
3. **Validate** a simulator against theory, using confidence intervals that are honest about autocorrelation (warm-up deletion and batch means).
4. **Estimate model inputs** from an operational log, distinguishing demand from throughput and testing the exponential-service assumption with evidence.
5. **Make and defend a decision** under uncertainty, separating simulation error from input (data) uncertainty, and explaining when and why the analytical shortcut fails.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `fuel_queue` package in [`starter/fuel_queue/`](starter/fuel_queue/). Signatures and dataclasses are fixed because the tests import them; internals are yours. `load_log` and `poisson_arrivals` are provided.

| ID | Requirement |
|---|---|
| **R1** | `erlang_b(c, a)` and `erlang_c(c, a)` for offered load `a = λ/μ`. They must be numerically stable for `c` up to at least 500, so naive factorials and powers are not acceptable. `erlang_c` raises `ValueError` when `a ≥ c` (unstable), when `a ≤ 0`, or when `c` is not a positive integer. |
| **R2** | `mmc_metrics(lam, mu, c) -> QueueMetrics` with utilisation, P(wait), `Lq`, `Wq`, `W`, `L`, and `QueueMetrics.p_wait_exceeds(t)` returning P(Wq > t). Your report must include the **derivation** of P(wait) from the balance equations of the birth–death chain, of `Wq` (using Little's law), and of P(Wq > t) = C(c, a)·e^{−(cμ−λ)t} (conditioning on all pumps being busy on arrival). |
| **R3** | `simulate_fcfs(arrival_times, service_times, c)` returns each customer's queueing delay for a FCFS queue with `c` identical pumps that starts empty. It is a pure function of its inputs (no randomness). It validates input as the docstring says. |
| **R4** | `simulate_mmc(lam, mu, c, n, rng)` and `simulate_empirical(lam, service_sample, c, n, rng)`. All randomness comes from the `rng` argument, so results are reproducible from a seed. |
| **R5** | `batch_means_ci(x, n_batches, level)` returns a Student-t confidence interval for a steady-state mean from non-overlapping batch means, as the docstring specifies. |
| **R6** | `estimate_inputs(log, window_min)` estimates the **demand** arrival rate per minute over all days in the log, and the service-time sample, mean and coefficient of variation (sample sd with `ddof=1`, divided by the mean) from customers who were served. |
| **R7** | `validate_against_mmc(...)` simulates an M/M/c queue, discards a warm-up, and reports whether the analytical `Wq` and P(Wq > t) both fall inside their batch-means intervals. In the report, show this validation for **at least three** (λ, μ, c) settings, including one with utilisation above 0.9, and explain what happens to the required run length as utilisation rises. |
| **R8** | `recommend_pumps(log, ...)` returns the smallest `c` whose **upper** 95% batch-means bound for P(Wq > 10 min) is at most 0.10, using Poisson arrivals at the estimated demand rate and service times resampled from the log. It also returns what the M/M/c formula alone would recommend (`c_mmc`) and a table with one row per `c` considered. Unstable values of `c` are flagged and never simulated as though they had a steady state. |
| **R9** | `python -m fuel_queue resources/data/station_log.csv --out outputs/` writes `recommendation.json` and `pump_table.csv`. The CLI is provided; it must work with your implementation. |
| **R10** | **Input-uncertainty analysis** (in code and the report). Resample the log (for example, bootstrap customers, or resample whole evenings) at least 30 times, re-run the decision each time, and report how often each pump count is recommended. Explain why this is a different question from the batch-means interval. |
| **R11** | **Exponential-service check** (report). Show, with a plot and at least one quantitative statistic, whether the service times are consistent with an exponential distribution, and explain *which direction* the M/M/c error goes and why. |

### D.2 Engineering requirements (mandatory)

- **Reproducibility.** Every number in your report comes from code in your repository, run with stated seeds.
- **Tests.** Keep the provided tests passing and add **at least 10 tests of your own** in `tests/test_member_*.py`. At least three must test the simulator against something you computed independently (by hand, from a recursion, or from a formula).
- **Dependencies.** Only the packages in [`starter/requirements.txt`](starter/requirements.txt) plus matplotlib for figures. No queueing or simulation libraries (such as `simpy` or `queueing-tool`) in the core package; you may use one in an optional cross-check.
- **Performance.** The CLI finishes in under 60 seconds on a typical laptop.

### D.3 Data responsibility

The log is **synthetic** and contains no personal data: customers are identified only by a day and sequence number. In practice, station logs can include vehicle plate numbers or CCTV timestamps. In one paragraph, say what you would remove before sharing such a log, and why aggregate service-time distributions are usually enough for this analysis.

### D.4 Optional enhancements (not required for full marks)

- Compare your simulation with the Allen–Cunneen or Kingman approximation for M/G/c, using your measured service-time coefficient of variation.
- Model balking explicitly and estimate how many drivers the station loses with four, five and six pumps.
- A priority lane for jerrycan buyers: does separating them reduce the probability of a long wait for everyone else?

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/station_log.csv`](resources/data/station_log.csv): 1,303 rows, 6 columns, about 47 KB, UTF-8 |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed from a documented stochastic model of a fictional station. The generator is held in the assessor kit because it reveals the true service distribution. |
| **Licence** | CC BY 4.0 (same as this repository's content) |
| **Integrity** | SHA-256 `9e72e2ff93d829a1d6d902c6fcb872b49c63b21c26863f7e22e8b946d52da1c9`. The contract test checks it, so don't edit the file. |

**Schema**

| Column | Meaning |
|---|---|
| `customer_id` | `D<day>-<sequence>`, unique |
| `day` | Evening 1–5 |
| `arrival_min` | Minutes after 16:00 when the customer arrived (0–240) |
| `vehicle_type` | `car`, `keke`, `bus` or `jerrycan` (customer on foot or okada with containers) |
| `status` | `served`, or `balked` (left without joining the queue) |
| `service_min` | Minutes at the pump; empty for balked customers |

**Known limitations (by design).** Balked customers have no service time, so you must assume their service would have looked like everyone else's of the same mix. The five evenings are a small sample, which is the point of R10. The log was recorded with four pumps open, so it says nothing directly about what waits look like with six.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-05-probability-and-statistics/DS-T1-012-the-fuel-queue
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract      # passes immediately: checks data and scaffold
pytest                  # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `fuel_queue/` package (the completed starter) | The analytical and simulation tools: the core technical evidence |
| 2 | `tests/test_member_*.py` (≥ 10 tests) | Shows you can verify a simulator independently |
| 3 | `analysis.ipynb` **or** `analysis.py` | Input modelling, validation runs, the decision and the input-uncertainty study, reproducible end to end |
| 4 | `outputs/recommendation.json`, `outputs/pump_table.csv` | The artefacts the manager would receive |
| 5 | `REPORT.md` (at most 1,800 words plus derivations, tables and figures) | Derivations (R2), validation (R7), the exponential check (R11), the decision with both kinds of uncertainty (R8, R10), limitations, and a one-paragraph answer for the manager in plain language |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 7 | A 5–10 minute live defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

Criteria marked ⚙ are checked automatically with the public and hidden test suites; criteria marked ✍ are checked by the assessor.

1. ⚙ `pytest` passes all provided public tests and your own tests from a clean environment built from your `requirements.txt`.
2. ⚙ `erlang_c` matches an independent formula to a relative error of 1e-9 for small `c`, and returns a finite probability for `c = 500`. *Justification:* both are exact computations, so the only tolerance needed is floating-point error.
3. ⚙ `simulate_fcfs` matches the Lindley recursion exactly for one pump and a brute-force FCFS implementation for several pumps, including simultaneous arrivals.
4. ⚙ **Validation:** for M/M/c settings not in the public tests, the analytical `Wq` and P(Wq > t) lie inside your 95% batch-means intervals from 200,000 customers after a 10,000-customer warm-up. *Justification:* a correct simulator fails this check about 5–10% of the time for a single fixed seed only through bad luck, and the hidden tests use seeds where the reference passes with margin; a wrong simulator, or a naive i.i.d. interval, fails systematically.
5. ⚙ **Decision:** on the official log `recommend_pumps` returns 6 pumps and `c_mmc` returns 5. On three re-generated logs with different demand levels, it returns the decision the reference returns. *Justification:* the hidden logs were chosen so that the decision is not borderline. At the reference's answer `c*`, the upper bound of P(Wq > 10) is at most 0.055; at `c* − 1` the lower bound is at least 0.16. Any correct implementation reaches the same decision whatever its random seed.
6. ⚙ The demand rate counts balked customers (it equals all arrivals divided by the total observed minutes).
7. ⚙ No unstable pump count (ρ ≥ 1) is ever recommended.
8. ✍ The report derives Erlang C and P(Wq > t) correctly from the balance equations, with each assumption named (Poisson arrivals, exponential service, FCFS, infinite waiting room, steady state).
9. ✍ The report quantifies how far the service-time distribution is from exponential (for example its coefficient of variation with a bootstrap interval, or a Q–Q plot plus a test) and explains why this makes M/M/c **optimistic** about long waits.
10. ✍ The input-uncertainty study (R10) reports the share of resamples that recommend each pump count, and the plain-language recommendation to the manager reflects it. For example: "6 pumps; with only five evenings of data, there is roughly a 1-in-10 chance that 5 would have been enough, but recommending 5 risks breaking the standard on most evenings."
11. ✍ The report explains, with a number, what would have happened had demand been estimated from served customers only.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 10 |
| Methodology: validation and input modelling | 15 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates: a passing defence, a reproducible analysis and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create a private repository** named `clbg-DS-T1-012-<your-github-username>` containing this assessment's `starter/` contents at the top level, plus `tests/`, `resources/` and `submission-template/`.
2. **Expected structure:**
   ```text
   clbg-DS-T1-012-<username>/
   ├── README.md                 # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── fuel_queue/
   ├── tests/                    # provided tests + test_member_*.py
   ├── resources/                # unchanged
   ├── analysis.ipynb | analysis.py
   ├── outputs/recommendation.json
   ├── outputs/pump_table.csv
   ├── figures/                  # anything the report shows
   ├── REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** The history is part of the evidence. A single final commit containing everything will be questioned at defence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue in the CLBG assessments repository with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core.

1. **M/G/c approximations.** Implement the Allen–Cunneen approximation and report where it agrees with your simulation and where it breaks down (at low and at high utilisation).
2. **Lost customers.** Add balking to your simulator, calibrate the balking rule from the log, and estimate lost sales per evening against the number of pumps open.
3. **Non-stationary arrivals.** Test whether the arrival rate really is constant over the four hours (for example by counting arrivals in 30-minute bins), and if not, simulate with a piecewise-constant rate. Does the decision change?
4. **Common random numbers.** Use the same random streams across different values of `c` and show how much narrower the interval for the *difference* in P(Wq > 10) becomes.

---

## K. Assessment Integrity

**AI tools are permitted** for learning, for example to explain the Erlang formulas, review your code, or suggest plotting idioms. **They must not do the assessment for you.** You must be able to derive, explain and change everything you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`: which tool, for what, and an example prompt. Disclosed, reasonable use is not penalised; undisclosed use that becomes apparent at defence is an integrity breach.
- **Cite** any derivation or code you adapted (textbooks, lecture notes, Stack Overflow), with a link or reference.
- **Collaboration:** you may discuss general ideas (what is batch means?) with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In the defence the assessor will:
  1. ask you to derive P(wait) for M/M/2 on paper from the balance equations;
  2. pick a customer index in a short simulation and ask you to trace why their wait is what it is;
  3. give you an **unseen modification** to implement live, such as reporting the 90th percentile of the wait with an interval, or adding a pump that only serves cars;
  4. ask why your interval is batch means and not `1.96·sd/√n`, and what goes wrong at ρ = 0.98.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Exponential and Poisson distributions, conditional probability, a basic confidence interval, NumPy. |
| **New skill developed** | Using simulation as a measuring instrument that must itself be validated, and treating simulation output as statistical data with its own correlation structure. |
| **Decisions the member must make** | What counts as demand; how long a warm-up and run to use; how to tell whether exponential service is a reasonable assumption; how to present two different kinds of uncertainty to a non-technical manager. |
| **What must be investigated independently** | The service-time distribution and its consequences, the effect of balking on demand estimation, and the stability boundary. |
| **Why it's interesting** | A trusted formula gives a confidently wrong answer for a reason the data shows, and the "obvious" demand estimate is biased by the very congestion being studied. |
| **Evidence of competence** | Exact agreement with independent recursions; validation intervals that cover theory; the correct decision on re-generated logs at other demand levels; derivations reproduced live. |
| **Misconceptions exposed** | "Simulation output is i.i.d." "Served customers are the demand." "A finite simulated average wait means the system is stable." "If the mean is right, the model is right." "More replications remove all uncertainty." |
| **Preparation for later work** | DS-T2 work on uncertainty and decision analysis, MCMC output analysis (ESS and autocorrelation reappear in later Tier 3 work), capacity planning in ML serving systems, and A/B testing, where correlated observations break naive intervals. |

**Suggested approach**, if you want guidance (you may ignore it):

1. Write the derivation first. Implement R1–R2 and test them on M/M/1 and M/M/2 by hand.
2. Build `simulate_fcfs` and test it against the Lindley recursion before you touch randomness.
3. Validate on M/M/c (R7). Only then load the log.
4. Profile the log: service time by vehicle type, the share who balked, and arrivals per evening.
5. Make the decision, then ask how it would change with a different five evenings (R10).

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
