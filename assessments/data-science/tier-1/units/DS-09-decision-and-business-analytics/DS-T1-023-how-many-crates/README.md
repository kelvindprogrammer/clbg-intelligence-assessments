# DS-T1-023: How Many Crates? Inventory Decisions with Censored Demand at Mile 12

> *The notebook says she sold nine. It does not say how many wanted to buy.*

![Format: Implementation](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-023` |
| **Title** | How Many Crates? Inventory Decisions with Censored Demand at Mile 12 |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-09: Decision and Business Analytics](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 8–14 hours over 1 week |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | Expected value; the Poisson distribution; numpy and scipy basics; `pytest` |
| **Skills developed** | Newsvendor expected profit and critical ratio; Recognising censored data; Maximum likelihood with censoring; Comparing decision rules by realised profit |
| **Technologies** | Python 3.10+, numpy, pandas, scipy, pytest |

---

## B. Problem Statement

**Mama Chidi** sells tomatoes at the Mile 12 market in Lagos. Each morning she buys crates at **₦12,000**, sells them at **₦20,000**, and anything unsold by evening goes to a processor at **₦5,000**. How many crates should she buy? Too few and she sends customers away; too many and she loses ₦7,000 on every leftover crate.

This is the **newsvendor problem**, one of the oldest results in operations research. If demand were known as a distribution, the answer is a single quantile: buy the smallest number of crates whose chance of covering demand reaches the *critical ratio* `(price - cost) / (price - salvage)`.

Mama Chidi does not know the demand distribution. She has a **240-day notebook** of how many crates she stocked and how many she sold, and her average sales are about 7.6 crates on weekdays and about 9.2 on market days (Friday and Saturday). The trap is in the word *sold*. On a day she stocks 9 crates and sells 9, she does not know whether 9 or 29 customers wanted tomatoes. Sales are **censored demand**: every sell-out hides how much more she could have sold. Averaging sales and planning around that average makes her order too little exactly on the days with the most customers, and then the notebook "confirms" that she was right, because she sold out.

In this assessment you will implement the newsvendor arithmetic exactly, estimate demand properly from censored sales using maximum likelihood, and show how much profit the naive plan leaves on the table. All data is **synthetic**; no real trader is described.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Compute** expected profit for a stocking decision from a demand sample.
2. **Derive and apply** the critical-ratio rule, and check it against brute-force search.
3. **Recognise** censored observations in sales data.
4. **Estimate** a Poisson demand rate by maximum likelihood with censoring.
5. **Compare** a naive and a corrected plan by the profit they earn under the true demand.
6. **Explain** the result to a trader in plain language.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `crate_planner` package in [`starter/crate_planner/`](starter/crate_planner/). Signatures are fixed.

| ID | Requirement |
|---|---|
| **R1** | `critical_ratio(price, cost, salvage)` returns `(price - cost) / (price - salvage)`; `ValueError` unless `salvage < cost < price`. |
| **R2** | `expected_profit(q, demand, price, cost, salvage)`: the mean over demand outcomes of `price * min(q, d) + salvage * (q - min(q, d)) - cost * q`. |
| **R3** | `best_quantity(demand, price, cost, salvage) -> (q, profit)`: the integer `q` in `0..max(demand)` that maximises R2; ties go to the smaller `q`. |
| **R4** | `censored_flags(df) -> bool Series`: `True` where `crates_sold == crates_stocked` and stock is positive. |
| **R5** | `censored_poisson_mle(sold, stocked) -> float`: the Poisson mean maximising the likelihood in which an uncensored day contributes `P(D = sold)` and a censored day contributes `P(D >= stocked)`. |
| **R6** | `poisson_quantity(lam, price, cost, salvage) -> int`: the smallest `q` with `P(D <= q) >= critical ratio`. |
| **R7** | `expected_profit_poisson(q, lam, price, cost, salvage)`: the exact expected profit when `D ~ Poisson(lam)` (sum over the distribution; truncate where the tail mass is below 1e-12). |
| **R8** | `plan_by_day_type(df, price, cost, salvage) -> DataFrame` with columns `day_type, n_days, share_censored, lambda_naive, lambda_mle, q_naive, q_mle`, where `lambda_naive` is the mean of sales, `q_naive` and `q_mle` come from R6, and rows are sorted by `day_type`. |

### D.2 Engineering requirements

- Vectorise R2; do not mutate inputs.
- Write **at least 6 tests of your own** in `tests/test_member_*.py`, including one for a day with zero stock.
- `pytest` must finish in under 30 seconds.

### D.3 Analysis requirement

In `analysis.py`, simulate your own trader (true rates of your choice), generate censored histories, and show for at least three stocking policies how the naive-versus-MLE gap in expected profit depends on how often the trader stocks below demand. Quote one table in the report.

### D.4 Privacy and responsibility

The data is synthetic. In real work, a small trader's sales records are commercially sensitive; ask permission and report aggregates.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/daily_sales.csv`](resources/data/daily_sales.csv): 240 rows × 4 columns (`day, day_type, crates_stocked, crates_sold`), about 5 KB |
| **Provenance** | **Synthetic**, generated with a fixed seed from Poisson demand with different rates for weekdays and market days. Stock levels were chosen at random between 7 and 12. |
| **Licence** | CC BY 4.0 (as this repository) |
| **Integrity** | SHA-256 checked by the contract test. Do not edit the file. |
| **Prices** | Use ₦20,000 sale, ₦12,000 cost, ₦5,000 salvage for the official analysis; hidden tests use other prices. |

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-09-decision-and-business-analytics/DS-T1-023-how-many-crates
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks data and scaffold
pytest                       # fails until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `crate_planner/` package | The core technical evidence |
| 2 | `tests/test_member_*.py` (≥ 6 tests) | Pins behaviour and edge cases |
| 3 | `analysis.py` and its output | The simulation study (D.3) |
| 4 | `REPORT.md` (≤ 600 words plus one table) from the [template](submission-template/REPORT.md) | A plan for Mama Chidi and the AI-use declaration |
| 5 | A 5-minute defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Assessors check the criteria marked ⚙ with the public and hidden test suites, and the rest by hand.

1. ⚙ All public tests and your own tests pass from a clean environment.
2. ⚙ R1–R8 behave as specified on public and hidden tests, with hidden tests using different prices and **regenerated** sales histories (420 days).
3. ⚙ On regenerated histories the MLE is within 8% of the true rate for both day types. *Justification:* with about 120 market days at rate 12–16 the sampling error is about 3–4%, and censoring inflates it somewhat, so 8% is about two standard errors.
4. ⚙ On those histories the naive mean underestimates the market-day rate by more than 8%, and the MLE plan earns at least as much as the naive plan under the true demand.
5. ⚙ `poisson_quantity` agrees with the cdf rule and `expected_profit_poisson` peaks at it on random inputs.
6. ✍ `analysis.py` reproduces the table in the report.
7. ✍ The report states plainly why a sell-out day is not a demand observation and what Mama Chidi should do differently (including one non-statistical change, such as keeping a note of unmet requests).

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 10 |
| Methodology of the simulation study | 15 |
| Testing | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private GitHub repository** named `clbg-DS-T1-023-<your-github-username>` and copy in this assessment's `starter/crate_planner/`, `tests/`, `resources/` and `submission-template/`. Put `crate_planner/` at the repository root.
2. **Commit as you work.** Commit history is part of the evidence. A single "final" commit will be questioned at defence.
3. Include `REPORT.md` (from the [template](submission-template/REPORT.md)), which contains your AI-use declaration, and a short top-level `README.md` (at most 10 lines) saying how to run everything.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never replace the core requirements.

1. **Negative binomial.** Replace Poisson with a negative binomial (market-day demand may be over-dispersed) and compare plans by likelihood.
2. **Learning by stocking higher.** Design a simple experiment in which Mama Chidi deliberately over-stocks on some market days to learn demand, and compute its cost against the information gained.
3. **Bayesian rate.** Put a Gamma prior on the Poisson rate and give a credible interval for the optimal order quantity.
4. **Robustness.** Show how wrong the plan is if the salvage price is off by ₦2,000.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a statistical idea or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration inside `REPORT.md`: tool, purpose, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** code or methods adapted from documentation, papers or forums.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers or report text.
- **Defence (5 minutes).** The assessor asks you to explain what a sell-out day tells you and what it does not; asks what changes if the salvage price rises above the cost price; then gives an **unseen modification**, for example a 2-crate minimum purchase or an extra lost-sale penalty, to implement live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Expected value, the Poisson distribution, basic numpy and scipy. |
| **New skill developed** | Recognising that the data are not the quantity of interest (sales are not demand) and fixing it with likelihood. |
| **Decisions the member must make** | How to structure the optimisation, how to implement the censored likelihood, and what to tell the trader. |
| **What must be investigated independently** | How much profit is lost by naive planning under different stocking habits. |
| **Why it's interesting** | A familiar market-trader decision hides a statistical trap that appears in inventory, ticketing and capacity planning everywhere. |
| **Evidence of competence** | Correct closed forms, MLE recovery on regenerated data, and an analysis that quantifies the cost of censoring. |
| **Misconceptions exposed** | 'Average sales is average demand.' 'More data fixes a biased estimate.' 'Optimal stock equals expected demand.' |
| **Preparation for later work** | Leads to DS-T2 decision analysis under uncertainty and to survival-style censoring in later ML units. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
