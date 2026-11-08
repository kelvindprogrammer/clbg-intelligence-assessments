# DS-T3-016: Lower the Cut-off? A Credit Decision Where Outcomes Exist Only for the Approved

> *You can only study the borrowers you chose to lend to. The director wants to lend to others.*

![Format: Open-Ended](https://img.shields.io/badge/format-open%20ended-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T3-016` |
| **Title** | Lower the Cut-off? A Credit Decision Where Outcomes Exist Only for the Approved |
| **Subtrack** | Data Science |
| **Tier** | 3: Advanced Practice |
| **Unit** | [DS-09: Decision and Business Analytics](../README.md) |
| **Format** | Open Ended (secondary: Optimization) |
| **Difficulty** | Technical 4 · Mathematical 4 · Research 4 · Engineering 3 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 25–40 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | Logistic regression and maximum likelihood; bootstrap; expected-value decisions; numpy/pandas. Helpful: DS-05 and the DS-09 Tier 2 assessment |
| **Skills developed** | Sample-selection and reject-inference reasoning; Inverse-propensity weighting; Profit-based threshold optimisation; Decision-level uncertainty quantification; Minimax-regret robust choice; Experiment ethics in lending |
| **Technologies** | Python 3.10+, numpy, pandas, scipy, pytest |

---

## B. Problem Statement

**Sabi Credit** (fictional) is a Nigerian digital lender making 90-day micro-loans of about ₦100,000. Its credit score runs from 300 to 850, and for three years its policy has been simple: **approve at 600 or above, decline below**. The commercial director now wants to grow the book and asks a clear question: *"Our cut-off is too conservative. Lower it to 520. How much extra profit do we make?"*

An analyst has produced an answer. She fitted a logistic regression of default on score using the loans the company actually made (every loan was approved, so every loan was scored 600 or higher) and used it to predict default rates for scores down to 520. Her model says default stays below the break-even rate until about **score 500**, and she projects a substantial profit increase if the cut-off is cut to 520.

The trap is built into the data. **Outcomes are observed only for funded loans.** The curve is being extrapolated into exactly the region where the lender has never lent, and a logistic curve fitted on safe borrowers has no way of knowing whether risk rises gradually or falls off a cliff at 580. Statisticians call this *reject inference* or *sample selection*; it is the central problem of credit scoring and of any decision system trained on its own past decisions.

Fortunately, the company ran a small pilot: **8% of applicants below 600 were approved at random** ("explored" loans), with the sampling probability recorded in `propensity`. These randomly approved loans are the only unbiased window into the region of interest, and they are few. Your task is a full decision analysis:

1. Show quantitatively that approved-only modelling is biased and over-optimistic.
2. Use the exploration sample properly (inverse-propensity weighting) to estimate the default curve and the profit-maximising cut-off.
3. Quantify how uncertain that cut-off is, and what the uncertainty means for the decision.
4. Account for the possibility that a macro shock raises default rates across the board, and choose a cut-off that you can defend if you are wrong.
5. Decide whether the company should extend its random-approval pilot, and say what that costs.
6. Write a recommendation memo for the director, including the fairness and regulatory considerations of lending experiments.

There is no single correct memo. The code is checked against specified behaviour, and the memo is assessed on the quality of the argument. The data is **synthetic**; no real borrower is described.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Recognise** sample-selection bias in a decision system trained on its own past decisions.
2. **Estimate** default risk in an unobserved region using a randomised exploration sample and inverse-propensity weights.
3. **Translate** a risk curve into a profit-maximising policy through explicit gain and loss terms.
4. **Quantify** the uncertainty of the *decision* (not just the parameters) with a bootstrap of the entire pipeline.
5. **Choose robustly** under scenario uncertainty using minimax regret, and compare with expected-value optimisation.
6. **Evaluate** the value and cost of collecting more exploration data.
7. **Argue** the ethics and regulatory fit of a lending experiment in a short professional memo.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `cutoff_lab` package in [`starter/cutoff_lab/`](starter/cutoff_lab/). `DefaultCurve` (a logistic polynomial in `z = (score - 600) / 100`, with `.predict(score)`) is provided. A loan that is repaid earns `terms["gain"]` (25 per 100 of principal); a default loses `terms["loss"]` (70). An applicant is funded if `defaulted` is not missing.

| ID | Requirement |
|---|---|
| **R1** | `default_rate_by_band(df, edges=None) -> DataFrame` with columns `band, n_apps, n_funded, naive_rate, ipw_rate`. Bands are `[lo, hi)` from `edges` (default `[300,500,550,575,600,650,700,851]`), labelled `"lo-(hi-1)"`. `naive_rate` is the mean default rate over historically approved loans only (`approved == 1` and `explored == 0`); `NaN` if none. `ipw_rate` is `sum(d / propensity) / sum(1 / propensity)` over all funded loans in the band; `NaN` if none. |
| **R2** | `fit_default_curve(df, method, degree=2) -> DefaultCurve`: maximum-likelihood logistic regression of `defaulted` on `[1, z, ..., z^degree]`. `method="approved_only"` uses historically approved loans with unit weights; `method="ipw"` uses all funded loans with weights `1/propensity`. Other methods raise `ValueError`. |
| **R3** | `expected_profit(cutoff, df, curve, terms)`: expected profit **per applicant in `df`**: the sum over applicants with `score >= cutoff` of `(1 - p) * gain - p * loss`, divided by `len(df)`, where `p = curve.predict(score)`. |
| **R4** | `best_cutoff(df, curve, terms, grid=None) -> (cutoff, profit)`: maximise R3 over `grid` (default `range(300, 851, 5)`); ties go to the lowest cutoff. |
| **R5** | `bootstrap_cutoff(df, method, degree, terms, n_boot=100, seed=0)`: with `rng = default_rng(seed)`, each replicate resamples `df` rows with `df.iloc[rng.integers(0, n, n)]`, refits R2 and applies R4. Returns `{"cutoffs", "median", "ci_low", "ci_high"}` (5th and 95th percentiles). |
| **R6** | `scenario_profits(df, curve, terms, cutoffs, multipliers) -> DataFrame` with columns `cutoff, multiplier, profit`: R3 when the default probability is `min(1, multiplier * p)`. |
| **R7** | `minimax_regret(table) -> int`: regret of a cutoff in a scenario is the best profit in that scenario minus its profit; return the cutoff with the smallest maximum regret (ties to the lowest). |
| **R8** | `recommend(df, terms, multipliers=(1.0, 1.3, 1.6), n_boot=100, seed=0) -> dict` with keys `ipw_cutoff` (R2 `ipw`, degree 2), `naive_cutoff` (`approved_only`, degree 1), `ci_low`, `ci_high` (R5, `ipw`, degree 2), `robust_cutoff` (R7 over cutoffs 500 to 700 in steps of 5), `naive_claimed_profit` (what the naive curve says its own cut-off earns) and `naive_cutoff_profit_under_ipw` (what the IPW curve says that cut-off earns). |

### D.2 Analysis and memo requirements

- `analysis.py` must reproduce: the band table; the cut-offs and profit claims of the naive and IPW methods for degrees 1, 2 and 3; the bootstrap interval; the scenario table; and a simulation of the effect of tripling the exploration rate on the width of the cut-off interval (generate your own synthetic book with a different exploration rate; document the assumed true curve).
- Your memo (≤ 2,000 words plus tables and figures) must contain: the answer to the director's question; why the analyst's number is wrong, with evidence; what the pilot data can and cannot tell you (for example, how many explored loans fall between 560 and 600, and what an interval for the default rate there looks like); a robust recommendation; an exploration plan with a cost estimate; and an ethics-and-regulation section covering fair treatment of borrowers selected into a lending experiment, transparency, and data protection under the Nigeria Data Protection Act 2023.
- Read about reject inference and sample selection (for example Heckman's 1979 *Econometrica* paper on sample selection bias, and the credit-scoring literature on reject inference such as Hand and Henley's 1997 survey of statistical classification methods in consumer credit) and cite what you used. Verify every citation yourself.
- **Write at least 10 tests of your own** in `tests/test_member_*.py`.

### D.3 Privacy and responsibility

All data is synthetic. With real data, credit scores and repayment histories are sensitive personal data. Experiments that deliberately lend to high-risk applicants affect real people and need documented governance, caps on exposure, and regulatory clearance; say what you would require before running one.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/applications.csv`](resources/data/applications.csv): 8,000 applicants × 6 columns (`app_id, score, approved, explored, propensity, defaulted`), about 180 KB |
| **Provenance** | **Synthetic**, generated with a fixed seed. Scores are normally distributed around 610; the default curve is hidden and not logistic in the unobserved region. Applicants below 600 were randomly funded with probability 0.08 (the `propensity` column). |
| **Licence** | CC BY 4.0 (as this repository) |
| **Integrity** | SHA-256 checked by the contract test. Do not edit the file. |
| **Hidden data** | Assessors run your code on regenerated books (same selection structure, different seeds). The true default curve is never revealed. |
| **Known limitation** | Approximately 260 explored loans exist on the official book, so any estimate below 600 is noisy. This is deliberate. |

**Setup**

```bash
cd assessments/data-science/tier-3/units/DS-09-decision-and-business-analytics/DS-T3-016-lower-the-cutoff
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks data and scaffold
pytest                       # fails until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `cutoff_lab/` package | The decision pipeline |
| 2 | `tests/test_member_*.py` (≥ 10 tests) | Pins the pipeline |
| 3 | `analysis.py`, its tables and at least three figures | Evidence behind the memo |
| 4 | `REPORT.md` (≤ 2,000 words plus tables) from the [template](submission-template/REPORT.md) | The recommendation memo and AI-use declaration |
| 5 | A 10-minute defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Assessors check the criteria marked ⚙ with the public and hidden test suites, and the rest by hand.

1. ⚙ All public tests and your own tests pass from a clean environment.
2. ⚙ On three regenerated books, the IPW cut-off (degree 2) is within 25 points of the true optimum and the approved-only linear cut-off is at least 50 points below it. *Justification:* the reference lands within 10 points on the hidden seeds checked, and the naive linear method misses by 85 to 130.
3. ⚙ The naive method's claimed profit exceeds its true profit by more than 2 units per applicant on a regenerated book.
4. ⚙ R3, R6 and R7 match closed-form computations against the true curve in hidden tests.
5. ⚙ `bootstrap_cutoff` follows the specified draw order (verified by public replication) and its interval covers the true cut-off (± 15) on a regenerated book.
6. ✍ `analysis.py` reproduces every number in the memo, including the exploration-rate simulation.
7. ✍ The memo explains in plain language why the analyst's extrapolation is biased and shows the evidence from the explored loans.
8. ✍ The recommendation states a cut-off or a range, a rule for choosing between expected-profit and minimax-regret answers, and the evidence that would change it.
9. ✍ The ethics section addresses borrower consent and harm limits in the pilot, and what the lender must disclose.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and reasoning | 15 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Methodology: baselines, ablations, robustness | 20 |
| Testing | 5 |
| Documentation and reproducibility | 5 |
| Critical thinking, ethics and limitations | 20 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private GitHub repository** named `clbg-DS-T3-016-<your-github-username>` and copy in this assessment's `starter/cutoff_lab/`, `tests/`, `resources/` and `submission-template/`. Put `cutoff_lab/` at the repository root.
2. **Commit as you work.** Commit history is part of the evidence. A single "final" commit will be questioned at defence.
3. Include `REPORT.md` (from the [template](submission-template/REPORT.md)), which contains your AI-use declaration, and a short top-level `README.md` (at most 10 lines) saying how to run everything.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never replace the core requirements.

1. **Parametric versus flexible curves.** Compare degree 2, degree 3 and a monotone-spline fit on the exploration region; show how the cut-off interval changes.
2. **Doubly robust estimation.** Combine an outcome model with IPW weights and compare variance.
3. **Optimal exploration design.** Choose where to explore (not uniformly): stratify the pilot by score band to minimise the cut-off interval for a fixed budget.
4. **Bounds.** Compute worst-case (Manski) bounds on the default rate between 560 and 600 using no model, and show what they imply for the decision.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a statistical idea or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration inside `REPORT.md`: tool, purpose, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** code or methods adapted from documentation, papers or forums.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers or report text.
- **Defence (10 minutes).** The assessor asks you to explain, without notes, why approved-only extrapolation is biased and what the explored loans identify; asks how your recommendation changes if the pilot probability were 2%; then gives an **unseen modification**, for example a cost of 5 per applicant for manual review in the 560-600 band, to implement and re-run live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Logistic regression, bootstrap, expected value; comfort with numpy/pandas. |
| **New skill developed** | Reasoning about data that exist only because of past decisions, and designing decisions robust to that. |
| **Decisions the member must make** | Model flexibility, how much to trust the exploration sample, how to treat scenario uncertainty, whether to invest in more exploration. |
| **What must be investigated independently** | Why the analyst's number is wrong, how wrong, and how uncertain the corrected number is. |
| **Why it's interesting** | The pattern appears in credit, hiring, recommender systems and public programmes: models trained on selected data are confidently wrong outside the selection. |
| **Evidence of competence** | Recovery of the true cut-off on unseen books, a bootstrap interval that is neither falsely precise nor useless, and a memo that makes a decision under stated uncertainty. |
| **Misconceptions exposed** | 'A good fit on observed data validates extrapolation.' 'More data fixes selection bias.' 'The profit-maximising cut-off is a single number.' |
| **Preparation for later work** | Leads to causal-inference and off-policy evaluation work in ML units, and to responsible-AI discussions of feedback loops. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
