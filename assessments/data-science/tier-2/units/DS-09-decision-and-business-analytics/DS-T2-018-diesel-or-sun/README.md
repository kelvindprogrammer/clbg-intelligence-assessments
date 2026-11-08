# DS-T2-018: Diesel or Sun? A Ten-Year Power Decision for a Rural Health Centre

> *The spreadsheet says diesel. The spreadsheet assumed the price would never move.*

![Format: Comparative](https://img.shields.io/badge/format-comparative-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-018` |
| **Title** | Diesel or Sun? A Ten-Year Power Decision for a Rural Health Centre |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Competence |
| **Unit** | [DS-09: Decision and Business Analytics](../README.md) |
| **Format** | Comparative (secondary: Optimization) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 2 · Engineering 2 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14–22 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | Log returns and random walks; present value; percentiles; numpy vectorisation; `pytest` |
| **Skills developed** | Stochastic price modelling; Monte Carlo cost simulation; Parameter-uncertainty propagation; Risk measures (CVaR); Sensitivity and break-even analysis; Decision memo writing |
| **Technologies** | Python 3.10+, numpy, pandas, scipy, pytest |

---

## B. Problem Statement

**Ilesa Community Health Centre** (fictional) runs a small maternity ward and a vaccine cold room. The national grid supplies power only a few hours a day, so the centre depends on a **diesel generator** that burns about 600 litres a month. The board must choose a 10-year power strategy:

- **Diesel only.** Cheap to install (₦1.8m), costly to run, and exposed to the diesel price.
- **Solar plus battery.** ₦14.5m up front, a ₦4m battery replacement in year 6, and a small genset as backup (75 litres a month).
- **Hybrid.** ₦9m up front and a smaller genset load (380 litres a month).

A board member has run the obvious spreadsheet: today's diesel price, held constant for ten years, discounted at 20%. **Diesel wins.** The centre's treasurer disagrees. Diesel in this region has gone from ₦230 to about ₦400 a litre in eight years, and she says the spreadsheet assumes the one thing that has never happened: a flat price.

Your job is to replace the single-number spreadsheet with a **decision analysis under uncertainty**: fit a stochastic model to the 96-month price history, simulate thousands of 10-year futures, compare the three options on expected cost *and* on tail risk, find the break-even diesel price, and show which assumptions the answer is most sensitive to. A key subtlety: the drift in the price history is estimated from only 95 monthly changes, so it is itself uncertain, and over 120 months that uncertainty matters as much as the monthly volatility. Your model must carry it.

You will build the `powercost` library, then write a **board memo** that recommends an option, says how sure you are, and states what would change your recommendation. The data is **synthetic**; no real facility is described.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Fit** a geometric random-walk model to a price history and simulate future paths reproducibly.
2. **Propagate parameter uncertainty**, not just random shocks, and explain why it widens long-horizon risk.
3. **Compute** the present value of a stream of costs, including a one-off replacement.
4. **Compare** options by expected cost, percentile range, conditional value at risk and probability of being cheapest.
5. **Derive** a break-even price and run a one-at-a-time sensitivity (tornado) analysis.
6. **Contrast** a static baseline with a stochastic analysis and explain any reversal.
7. **Recommend** an option under uncertainty, with a stated risk attitude and decision triggers.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `powercost` package in [`starter/powercost/`](starter/powercost/). Options are dicts with keys `capex, monthly_fixed, litres_per_month, replacement_month, replacement_cost` (see [`options.json`](resources/data/options.json)). Costs are in naira, monthly, with discount factor `(1+m)^-t` for month `t = 1..T`, where `m = (1 + annual_rate)^(1/12) - 1`.

| ID | Requirement |
|---|---|
| **R1** | `fit_price_process(prices) -> (mu, sigma)`: the mean and sample standard deviation (`ddof=1`) of monthly log returns. |
| **R2** | `simulate_paths(p0, mu, sigma, months, n_paths, seed)`: draw `z = default_rng(seed).standard_normal((n_paths, months))` and return `p0 * exp(cumsum(mu + sigma * z, axis=1))`. |
| **R3** | `simulate_paths_param_uncertainty(prices, months, n_paths, seed)`: fit R1; with `rng = default_rng(seed)` first draw `mu_i = mu + sigma/sqrt(n) * rng.standard_normal(n_paths)` (n = number of returns), then `z = rng.standard_normal((n_paths, months))`; paths start from the last observed price with per-path drift `mu_i`. |
| **R4** | `pv_cost(option, paths, annual_rate) -> array (n_paths,)`: `capex` + discounted `monthly_fixed` + discounted `litres_per_month * price_t` + `replacement_cost` discounted at `replacement_month` if that month is within the horizon. |
| **R5** | `compare(options, paths, annual_rate) -> DataFrame` with columns `option, mean, p05, p95, cvar95, prob_cheapest`, rows in input order. `cvar95` is the mean of the highest `ceil(0.05 * n_paths)` costs; `prob_cheapest` is the share of paths on which the option has the lowest cost (ties to the first). |
| **R6** | `breakeven_price(opt_a, opt_b, months, annual_rate) -> float`: the constant diesel price at which the two present-value costs are equal; `nan` if the options use the same litres. |
| **R7** | `tornado(opt_a, opt_b, base, ranges, months=120) -> DataFrame` with columns `param, low_diff, high_diff, swing`, sorted by `swing` descending (ties by name). The deterministic path is `p0 * exp(mu * t)` using `base = {"p0", "mu", "annual_rate"}`. `ranges` maps a parameter name to `(low, high)`; supported names: `p0, mu, annual_rate, litres_a, litres_b, capex_b`. `diff = PV(opt_a) - PV(opt_b)`; vary one parameter at a time. |

### D.2 Engineering requirements

- Vectorise R2–R5. No mutation of inputs.
- Write **at least 10 tests of your own** in `tests/test_member_*.py`, including a loop-based check of `pv_cost`.
- Put the decision analysis in `analysis.py`: static baseline; Monte Carlo with fixed parameters; Monte Carlo with parameter uncertainty (R3); tornado; break-even; at least 20,000 paths.

### D.3 Method-choice requirement

The model choices are partly yours: the discount rate (state your argument for 20%, and show 12% and 30%), the horizon, and whether to trust the historical drift. Show how each changes the recommendation. A model that cannot change the decision is not a sensitivity analysis.

### D.4 Privacy and responsibility

All data is synthetic. In a real health facility, power failure risks lives; your memo should say explicitly which risks the cost model **does not** capture (reliability, vaccine cold-chain loss, theft of panels).

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/diesel_prices.csv`](resources/data/diesel_prices.csv): 96 monthly prices (₦ per litre), about 2 KB; [`resources/data/options.json`](resources/data/options.json): the three options |
| **Provenance** | **Synthetic**, generated with a fixed seed from a geometric random walk with drift. Option costs are illustrative, not quotations. |
| **Licence** | CC BY 4.0 (as this repository) |
| **Integrity** | SHA-256 checked by the contract test. Do not edit the files. |
| **Hidden data** | Assessors run your code on a regenerated price history with different drift and volatility and different options. |

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-09-decision-and-business-analytics/DS-T2-018-diesel-or-sun
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks data and scaffold
pytest                       # fails until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `powercost/` package | The core technical evidence |
| 2 | `tests/test_member_*.py` (≥ 10 tests) | Pins behaviour |
| 3 | `analysis.py`, its output tables and at least two figures | The decision analysis |
| 4 | `REPORT.md` (≤ 1,200 words plus tables) from the [template](submission-template/REPORT.md) | A board memo and the AI-use declaration |
| 5 | A 7-minute defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Assessors check the criteria marked ⚙ with the public and hidden test suites, and the rest by hand.

1. ⚙ All public tests and your own tests pass from a clean environment.
2. ⚙ R1–R7 match independent loop-based or closed-form implementations in hidden tests on a **regenerated** history and different options.
3. ⚙ The long-horizon dispersion of R3 exceeds R2's by a factor in (1.3, 1.7) for 120 months. *Justification:* theory gives `sqrt(1 + T/n)` = 1.5, and 20,000 paths put the Monte Carlo error well under 0.05.
4. ⚙ On the official history the static baseline favours diesel while the stochastic mean favours solar, reproducing the reversal described in §B.
5. ✍ The memo reports the static baseline, fixed-parameter simulation and parameter-uncertainty simulation side by side and explains the differences.
6. ✍ The memo states a recommended option, a risk attitude (for example "minimise CVaR95 subject to expected cost within 10% of the best"), and at least two measurable triggers that would change the recommendation.
7. ✍ The sensitivity analysis shows which input has the largest swing, and the memo comments on whether that input can be influenced by the board.
8. ✍ The memo lists what the model does not capture.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Method choices and sensitivity analysis | 20 |
| Testing | 10 |
| Documentation and reproducibility | 5 |
| Critical thinking and limitations | 20 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private GitHub repository** named `clbg-DS-T2-018-<your-github-username>` and copy in this assessment's `starter/powercost/`, `tests/`, `resources/` and `submission-template/`. Put `powercost/` at the repository root.
2. **Commit as you work.** Commit history is part of the evidence. A single "final" commit will be questioned at defence.
3. Include `REPORT.md` (from the [template](submission-template/REPORT.md)), which contains your AI-use declaration, and a short top-level `README.md` (at most 10 lines) saying how to run everything.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never replace the core requirements.

1. **Mean reversion.** Fit a model in which prices revert to a trend and show how the CVaR comparison changes.
2. **Value of information.** Compute the expected value of learning the true drift before deciding (EVPI) and compare it with the cost of waiting a year.
3. **Staged investment.** Evaluate "diesel now, hybrid in year 3" as a real option.
4. **Reliability.** Add a probabilistic outage cost for the diesel supply chain and see whether it changes the ranking.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a statistical idea or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration inside `REPORT.md`: tool, purpose, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** code or methods adapted from documentation, papers or forums.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers or report text.
- **Defence (7 minutes).** The assessor asks you to explain in one minute why your recommendation differs from the static spreadsheet; asks what you would need to observe to switch options; then gives an **unseen modification**, for example a different discount rate for the battery or a naira devaluation shock in year 2, to be implemented and re-run live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Log returns, random walks, discounting and percentiles; numpy vectorisation. |
| **New skill developed** | Turning a spreadsheet comparison into a risk-aware decision analysis with explicit uncertainty in the parameters. |
| **Decisions the member must make** | Which discount rate, which risk measure, whether to trust historical drift, and what recommendation fits the board's risk appetite. |
| **What must be investigated independently** | How a decision flips between static and stochastic analyses, and which input drives it. |
| **Why it's interesting** | Fuel prices and power choices are a real, high-stakes Nigerian decision, and the 'obvious' answer reverses. |
| **Evidence of competence** | Correct implementations against independent checks, and a memo whose recommendation survives its own sensitivity analysis. |
| **Misconceptions exposed** | 'Use today's price.' 'The fitted drift is the true drift.' 'Expected cost is all that matters.' |
| **Preparation for later work** | Leads to the DS-09 Tier 3 decision memo and to ML-era simulation and uncertainty quantification. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
