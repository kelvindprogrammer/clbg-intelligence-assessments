# DS-T3-008: Do the Intervals Cover? A Simulation Study of Confidence Intervals for Clustered Claims

> *A farmers' insurance scheme reports a 95% interval for average claim size. Design the experiment that shows how often that interval is actually right.*

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T3-008` |
| **Title** | Do the Intervals Cover? A Simulation Study of Confidence Intervals for Clustered Claims |
| **Subtrack** | Data Science |
| **Tier** | 3: Advanced and Research-Informed |
| **Unit** | [DS-05: Probability and Statistics](../README.md) |
| **Format** | Comparative simulation study (secondary: replication) |
| **Difficulty** | Technical 3 · Mathematical 4 · Research 4 · Engineering 2 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 16-24 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM; each test runs in seconds; no GPU or network |
| **Recommended prerequisites** | The percentile bootstrap; what a 95% interval is supposed to mean; basic numpy vectorisation. The cluster bootstrap, the design effect and bootstrap-t are part of what you research. |
| **Skills developed** | Coverage simulation, bootstrap variants, ICC estimation, vectorised resampling, experimental design for statistical methods |
| **Technologies** | Python 3.10+, numpy, scipy, pytest; matplotlib optional |

---

## B. Problem Statement

A farmers' index-insurance scheme sells cover through village **cooperatives** across a Nigerian state. After a bad season it pays claims, and the scheme's actuary wants a 95% confidence interval for the **average claim size** to set next year's reserve. Claims are heavy-tailed (a few very large claims), and claims from the same cooperative are alike: the same flood, the same loan officer, the same assessor. In statistical language, observations are **clustered**, with a positive intraclass correlation (ICC).

The actuary has three candidate recipes: a plain **bootstrap** that resamples individual claims, a **cluster bootstrap** that resamples whole cooperatives, and a **normal interval with a design-effect adjustment** that inflates the variance by `1 + (mean cluster size - 1) * ICC`. A colleague who has read a paper says a fourth, a **studentised cluster bootstrap**, is safer when there are few cooperatives. Nobody has checked any of them on data like this.

Your task is a *methods study*, not an estimate of the average claim. You will implement the four methods, build the machinery to run a seeded Monte Carlo experiment on a data-generating process where the truth is known, and answer:

1. How often does each nominal-95% interval actually contain the true mean (its **coverage**), with an honest statement of Monte Carlo error?
2. How does that change as the number of cooperatives **k** falls from many to few, as clustering strengthens, and as claims become heavier-tailed?
3. Where does the standard cluster bootstrap break, why, and does the studentised version repair it at what cost (interval width)?
4. How many replications does your study need, and how do you know your conclusions are not Monte Carlo noise?
5. What would you tell the actuary to use, and under which conditions would you change that advice?

The data-generating process is provided and fixed (`coverage_lab/dgp.py`): log-claims are normal with a cooperative random effect, so the true mean is known exactly. That is what makes a coverage study possible. It is also a limitation: real claims will not be exactly log-normal, and your report must say how that affects what you can claim.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Implement ICC estimation and four interval methods for clustered data, vectorised.
2. Design a Monte Carlo coverage experiment with a known truth, fixed seeds, and a justified number of replications.
3. Quantify and report Monte Carlo error alongside every coverage figure.
4. Identify the regimes (few clusters, strong clustering, heavy tails) in which each method fails, and explain the mechanism.
5. Compare methods on both coverage and width, so that an over-wide interval cannot masquerade as a good one.
6. Make a method recommendation whose scope is limited by what the simulation can and cannot show.

---

## D. Technical Requirements

### D.1 Mandatory requirements

Implement the package in [`starter/coverage_lab/`](starter/coverage_lab/). `dgp.py` is provided and must not change (the contract test hashes it). `rng` arguments are `numpy.random.Generator` objects; all intervals are `(lower, upper)` for level `1 - alpha`.

| ID | Function | Requirement |
|---|---|---|
| **R1** | `estimate_icc(y, cluster)` | One-way ANOVA estimator, valid for **unbalanced** clusters (use the adjusted average cluster size `n0`). May be negative in small samples. |
| **R2** | `iid_bootstrap_ci(y, B, alpha, rng)` | Percentile bootstrap resampling observations. |
| **R3** | `cluster_bootstrap_ci(y, cluster, B, alpha, rng)` | Percentile bootstrap resampling whole clusters with replacement. The statistic is the overall mean (total over resampled clusters divided by their total size). |
| **R4** | `design_effect_ci(y, cluster, alpha)` | Normal interval `mean +/- z * s / sqrt(n / deff)` with `deff = 1 + (n/k - 1) * max(icc, 0)` and `z` the standard normal quantile. |
| **R5** | `cluster_bootstrap_t_ci(y, cluster, B, alpha, rng)` | Studentised cluster bootstrap. Studentise with a cluster-robust standard error that you derive and document. |
| **R6** | `coverage_study(method, k, m, sigma_u, sigma_e, reps, B, seed, alpha=0.05)` | For each of `reps` datasets from `dgp.simulate`, build the interval with `method` (one of `METHODS`) and return `{"coverage", "mcse", "mean_width", "reps"}`. `mcse = sqrt(p(1-p)/reps)`. Deterministic given `seed`. `m` may be an integer or a list of cluster sizes. Unknown `method` raises `ValueError`. |
| **R7** | `reps_needed(target_mcse, p=0.95)` | Smallest integer number of replications for which the Monte Carlo standard error of a coverage near `p` is at most `target_mcse`. |

### D.2 Study design requirements (assessed in the report)

Your `study.py` (or notebook) must run a designed experiment and produce, from a single command:

- a **grid** over at least `k in {8, 20, 40, 80}`, at least two clustering strengths (`sigma_u`) and at least two tail weights (`sigma_e`), with the cluster size chosen by you and stated;
- coverage **with Monte Carlo error bars** for all four methods, and mean width, in one table and one figure;
- a **replication-count justification**: how many replications you used and why, using `reps_needed`;
- a **common-random-numbers** discussion: did you compare methods on the same simulated datasets, and what does that buy you?
- an **ablation**: one deliberate change (for example `B`, the number of bootstrap draws, or the clipping of the ICC at zero) with a measured effect on coverage;
- a stated **scope**: for which parameter region do your conclusions hold, and which two ways could the true mechanism differ from the simulation (for example non-log-normal claims, or unequal cluster effects)?

Add at least **six tests of your own** in `tests/test_member_*.py`, including one hand-checkable cluster-bootstrap case and one test that the studentised interval handles a bootstrap draw with zero standard error.

### D.3 Privacy and responsibility

The study uses simulated claims; no personal data. A real insurer's claim data identifies farmers and their losses. In two sentences in `REPORT.md`, say what you would need (consent, data-sharing agreements, minimisation under NDPA 2023) before running this study on real claims, and how you would report cooperative-level results without exposing small cooperatives.

### D.4 Optional enhancements

Add a BCa or wild-cluster bootstrap and compare; estimate the ICC's own sampling variability and show how it feeds into the design-effect interval's failure at small k; add a regime where cluster sizes vary by a factor of 10 and report whether the weighting matters.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | None is distributed. Datasets are generated by [`starter/coverage_lab/dgp.py`](starter/coverage_lab/dgp.py), a fixed data-generating process with known truth |
| **DGP** | `simulate(k, m, sigma_u, sigma_e, rng)`: `log y_ij = u_i + e_ij`, `u_i ~ N(0, sigma_u^2)`, `e_ij ~ N(0, sigma_e^2)`. The true mean is `exp((sigma_u^2 + sigma_e^2)/2)` (`true_mean`). `simulate_normal` generates Gaussian data with a specified ICC for testing estimators |
| **Provenance** | Synthetic; the cooperative setting is illustrative. No real insurer or claims are represented |
| **Licence** | CC BY 4.0 (text), MIT (code) |
| **Integrity** | `dgp.py` is hash-checked by the contract test |
| **Suggested reading** | Efron and Tibshirani, *An Introduction to the Bootstrap* (percentile and bootstrap-t intervals); Cameron, Gelbach and Miller (2008) on bootstrap-based improvements for clustered errors; Morris, White and Crowther (2019) on reporting simulation studies |

**Known limitations.** The truth is available only because the DGP is parametric. The log-normal law has moments of all orders yet very heavy practical tails; other heavy-tailed laws (Pareto) would be worse. One level of clustering only.

**Setup**
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract
pytest
```
Each public test runs in a few seconds on a 4 GB laptop; a full grid with several thousand replications may take minutes, which is why vectorising the bootstrap matters.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `coverage_lab/` package | The four methods, ICC estimator and coverage machinery |
| 2 | `tests/test_member_*.py` (≥ 6) | Evidence of independent verification, including hand-checkable cases |
| 3 | `study.py` or notebook with outputs (table and figure) | The designed experiment, reproducible with one command |
| 4 | `REPORT.md` from the [template](submission-template/REPORT.md) (≤ 1,800 words plus tables) | Design, results with Monte Carlo error, mechanism, recommendation, scope |
| 5 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 6 | A 10-minute live defence | Verifies understanding and the ability to modify the study |

---

## G. Acceptance Criteria

Criteria marked ⚙ are checked by the public and hidden test suites. Criteria marked ✍ are checked by an assessor.

1. ⚙ Public tests pass (ICC estimates, interval basics, cluster width matching the cluster-robust SE, nominal coverage without clustering, iid failure under clustering, recovery by cluster-aware methods, bootstrap-t improvement, determinism, `reps_needed`).
2. ⚙ Coverage thresholds, each with the reference value and the Monte Carlo reasoning: with no clustering, iid bootstrap coverage ≥ 0.90 (reference 0.93, MCSE 0.013); with strong clustering (k=20, m=25, sigma_u=1, sigma_e=1) iid coverage < 0.60 (reference 0.44), cluster bootstrap ≥ 0.80 (reference 0.85), design-effect ≥ 0.78 (reference 0.84), bootstrap-t ≥ 0.885 and above the percentile version (reference 0.92 versus 0.87). Floors sit about three Monte Carlo standard errors below the reference so that a correct independent implementation passes.
3. ⚙ Hidden tests: other regimes (unbalanced clusters, moderate clustering, k=8 with heavy tail, level alpha=0.10 and 0.01) match the reference behaviour; the bootstrap-t beats the percentile cluster bootstrap by at least 5 points at k=8; the design-effect interval scales exactly with the normal quantile.
4. ✍ The report's grid satisfies §D.2, shows Monte Carlo error bars, and explains why the number of replications is sufficient to separate methods whose coverages differ by the amount you claim.
5. ✍ The report explains the **mechanism** of the cluster bootstrap's undercoverage at small k (few resampling units, skewed sampling distribution, underestimated variance) with evidence from your own runs, not only from the literature.
6. ✍ The recommendation to the actuary is conditional and quantified (which method, for which k and clustering strength, at what width cost), with the scope limits of §D.2.

---

## H. Evaluation Rubric

The full rubric with performance levels is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Methodology and experimentation | 25 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 5 |
| Critical thinking and limitations | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates (passing defence, reproducible run, integrity declaration). See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. Create a **private** GitHub repository named `clbg-DS-T3-008-<your-github-username>` from this assessment's `starter/` and `tests/` folders and the `submission-template/` files.
2. Expected structure:
   ```text
   clbg-DS-T3-008-<username>/
   ├── coverage_lab/           # your package (from starter/); dgp.py unchanged
   ├── tests/                  # provided tests + your own test_member_*.py
   ├── study.py | study.ipynb  # the experiment that produced your report's tables and figures
   ├── REPORT.md               # study design, results, recommendation, AI-use declaration
   └── AI_USE_AND_SOURCES.md
   ```
3. Commit as you work. Your commit history is evidence of authorship (see §K); a single "final" commit will be questioned at defence.
4. Add the CLBG assessor account as a read-only collaborator and file a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core requirements.

1. Add a Pareto-tailed DGP and show which methods survive.
2. Implement the wild cluster bootstrap and compare coverage at k = 8.
3. Study the ICC estimator's bias and variance as k falls, and trace it into the design-effect interval.
4. Replace the percentile cluster bootstrap with a bias-corrected one and measure the gain.

---

## K. Assessment Integrity

**AI tools are permitted** to explain concepts, suggest idioms or review your code. They may not do the assessment for you, and you must be able to explain and modify every line you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md` (template in `submission-template/`): tool, purpose and an example prompt. Undisclosed use discovered at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** adapted code and any papers or documentation you relied on, with links.
- **Collaboration:** discuss *general techniques* only. Do not share code, results or report text.
- **How understanding is verified.** At a 10-minute defence the assessor will (1) ask you to explain in one minute why the iid bootstrap undercovers here, with the design effect for your grid; (2) ask what the Monte Carlo error of your headline coverage figure is and how you would halve it; (3) set an unseen modification, for example a different alpha or a regime with unequal cluster sizes, to be run live and interpreted.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Confidence intervals and the bootstrap; variance of a mean; the idea of intraclass correlation. |
| **New skill developed** | Evaluating statistical methods by simulation: designing the experiment, controlling Monte Carlo error, comparing methods fairly. |
| **Decisions the member must make** | Grid design; replication count; common random numbers; which standard error to studentise by; what ablation to run; how to bound the claims. |
| **What must be investigated independently** | Why the cluster bootstrap undercovers at small k and heavy tails, and how bootstrap-t addresses it. |
| **Why it is interesting** | The intervals look reasonable and can be badly wrong. The experiment turns a vague worry into numbers. |
| **Evidence of competence** | Reference-matching coverage in unseen regimes, calibrated thresholds, and a report where every figure carries Monte Carlo error. |
| **Misconceptions exposed** | "The bootstrap fixes everything"; "more clusters than 8 is enough"; "a wider interval is a better interval"; "a simulation result is a fact about the world". |
| **Preparation for later work** | Leads to DS-08 (inference, experiments), DS-12 (research methods and reproducibility) and ML evaluation work where interval validity matters. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
