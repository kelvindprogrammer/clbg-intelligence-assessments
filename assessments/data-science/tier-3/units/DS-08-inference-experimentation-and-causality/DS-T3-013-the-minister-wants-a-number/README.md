# DS-T3-013: The Minister Wants a Number: Auditing a Staggered Solar Mini-Grid Evaluation

> *A regression produced one number. Prove what it means, or that it means nothing.*

![Format: Comparative](https://img.shields.io/badge/format-comparative-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T3-013` |
| **Title** | The Minister Wants a Number: Auditing a Staggered Solar Mini-Grid Evaluation |
| **Subtrack** | Data Science |
| **Tier** | 3: Advanced Practice |
| **Unit** | [DS-08: Statistical Inference, Experimentation and Causal Thinking](../README.md) |
| **Format** | Comparative (secondary: Investigation) |
| **Difficulty** | Technical 4 · Mathematical 4 · Research 4 · Engineering 3 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 25–40 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | Linear regression with fixed effects; potential outcomes and the difference-in-differences idea; bootstrap; pandas and numpy. Helpful: DS-05 and the DS-08 Tier 2 assessments |
| **Skills developed** | Estimand definition for staggered adoption; Group-time difference-in-differences; Cluster bootstrap inference; Pre-trend diagnostics; Ablation design; Causal validity argumentation |
| **Technologies** | Python 3.10+, numpy, pandas, scipy, pytest |

---

## B. Problem Statement

In 2023 a (fictional) state energy agency began installing subsidised **solar mini-grids** in local government areas (LGAs) in three waves. The 80 LGAs in the evaluation panel were treated in quarter 5 (20 LGAs), quarter 7 (15) and quarter 9 (15); 30 LGAs were never treated during the 12-quarter window. For each LGA and quarter, an analyst compiled an index of **small-business turnover** (`outcome`).

The agency's analyst ran the textbook regression: outcome on a "treated yet?" dummy with LGA and quarter fixed effects (two-way fixed effects, TWFE), and reported a single number as "the programme effect". The minister wants to put that number in a budget request. You are asked to audit it.

The audit is not a formality. In staggered designs, TWFE compares already-treated units with later-treated units as if they were controls. When effects **grow over time** and **differ across waves**, this produces a weighted average with distorted, sometimes negative, weights, so the single number can be far from any meaningful average effect. A careful analyst needs:

- a **transparent estimand** (average effect on the treated, by wave and by time since adoption);
- an estimator that compares each wave only with units that were not yet treated;
- **uncertainty** that respects clustering (the LGA, not the LGA-quarter, is the unit);
- **diagnostics** for the identifying assumption of parallel trends, which the data can partly test and partly cannot;
- an honest **validity argument**: why wave timing might not be as good as random, whether neighbouring LGAs could be affected, and what the estimate does and does not license.

This is an open methodological problem. The tests check your estimators against specified behaviour, but the memo is where the assessment is decided. The data is **synthetic**; no real LGA is described.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **State** a causal estimand for a staggered rollout and the assumptions that identify it.
2. **Implement** TWFE and a group-time (Callaway-Sant'Anna-style) estimator from first principles.
3. **Demonstrate**, with a noiseless construction, that TWFE is biased under heterogeneous dynamic effects.
4. **Aggregate** group-time effects into overall, event-time and cohort summaries.
5. **Quantify uncertainty** with a unit-level cluster bootstrap and justify the clustering level.
6. **Diagnose** violations of parallel trends with pre-period placebo estimates, and show their effect on the estimate.
7. **Run ablations** (control group choice, excluded waves, event window) and report which conclusions are robust.
8. **Argue validity** in writing, including spillovers and endogenous timing.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `staggered_did` package in [`starter/staggered_did/`](starter/staggered_did/). The panel has columns `unit_id, period, cohort, outcome`; `cohort` is the first treated period, or `0` for never-treated. A unit is treated at period `t` when `cohort > 0` and `t >= cohort`.

| ID | Requirement |
|---|---|
| **R1** | `twfe_att(df) -> float`: the coefficient on the treatment dummy in the regression with unit and period fixed effects. The panel must be balanced; otherwise raise `ValueError`. (Hint: two-way demeaning gives the OLS coefficient exactly in a balanced panel. You may also use dummies or `statsmodels`.) |
| **R2** | `group_time_att(df, controls="never") -> DataFrame` with columns `g, t, att, n_g, n_c`. For each cohort `g > 0` and each period `t != g-1` (skip a cohort if `g-1` is not in the data): `att = [mean_g(t) - mean_g(g-1)] - [mean_c(t) - mean_c(g-1)]`. With `controls="never"` the comparison group is the never-treated; with `"not_yet"` it is units never treated or first treated **after** `max(t, g-1)`, excluding cohort `g`. Sort by `g, t`. Pre-period cells (`t < g-1`) are included as placebos. Other `controls` values raise `ValueError`. |
| **R3** | `aggregate_att(gt, how="simple")`: `"simple"` returns the `n_g`-weighted average of post-treatment cells (`t >= g`) as a float; `"event"` returns a DataFrame `e, att` (e = t - g, all cells including pre-periods), with `att` the `n_g`-weighted average within each `e`; `"cohort"` returns `g, att`, the unweighted average of each cohort's post cells. Anything else raises `ValueError`. |
| **R4** | `cluster_bootstrap(df, estimator, n_boot=200, seed=0) -> {"estimate", "se"}`: with `rng = default_rng(seed)` and the sorted unit IDs, each replicate draws `rng.integers(0, n_units, n_units)`, builds a panel from the drawn units (relabelled so repeats are distinct units), and applies `estimator`. `se` is the standard deviation (`ddof=1`, per component) of the replicate estimates; `estimate` is `estimator(df)`. The estimator may return a float or a 1-D array, and `estimate` and `se` then have the same type. |
| **R5** | `pretrend_test(df, n_boot=200, seed=0) -> {"estimate", "se", "p_value"}`: for each cohort that has pre-period placebo cells (`t < g-1`, from R2 with `controls="never"`), the mean of those cells. `estimate` and `se` are dicts keyed by cohort (the standard errors from one vector-valued R4 call). `p_value` is the smallest two-sided normal-approximation p-value across cohorts times the number of cohorts, capped at 1 (a Bonferroni-adjusted minimum, which is sensitive to a trend in a single wave). |
| **R6** | `analyze(df, n_boot=200, seed=0) -> dict` with keys `twfe, cs_simple, cs_not_yet, cs_se, event, pretrend_p, twfe_minus_cs`. |

### D.2 Memo and analysis requirements

- `ablation.py` must regenerate a table with at least: TWFE; CS with never-treated controls; CS with not-yet-treated controls; CS excluding the last wave; CS with the event window limited to e in [0, 3]. Include bootstrap standard errors.
- Include a figure of the event-study (estimates with intervals) and of the TWFE-versus-CS difference.
- Your memo (see [F](#f-deliverables)) must contain: the estimand; the assumptions; a plain-language explanation of why TWFE fails here; a validity section covering parallel trends, anticipation, spillovers between neighbouring LGAs and the possibility that waves were assigned to LGAs expected to grow; and a recommendation for the minister.
- **Write at least 10 tests of your own** in `tests/test_member_*.py`, including a noiseless construction that exposes TWFE bias.

### D.3 Privacy and responsibility

All data is synthetic aggregates at LGA level. With real data, report only aggregate effects and avoid language that ranks named communities; discuss the risk of withholding a programme from a community because of a noisy estimate.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/minigrid_panel.csv`](resources/data/minigrid_panel.csv): 960 rows × 4 columns (80 LGAs × 12 quarters), about 25 KB |
| **Provenance** | **Synthetic**, generated with a fixed seed. LGA identifiers are fictional codes. Effects start at a wave-specific level and grow with time since adoption. |
| **Licence** | CC BY 4.0 (as this repository) |
| **Integrity** | SHA-256 checked by the contract test. Do not edit the file. |
| **Hidden panels** | Assessors also run your code on regenerated panels, including one where the earliest wave was already on a steeper trend. You are not told the true effect of any panel. |

**Setup**

```bash
cd assessments/data-science/tier-3/units/DS-08-inference-experimentation-and-causality/DS-T3-013-the-minister-wants-a-number
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks data and scaffold
pytest                       # fails until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `staggered_did/` package | The estimators and inference |
| 2 | `tests/test_member_*.py` (≥ 10 tests) | Pins the estimators, including the noiseless-bias construction |
| 3 | `ablation.py`, its output table and figures | Robustness evidence |
| 4 | `REPORT.md` (≤ 1,800 words plus tables) from the [template](submission-template/REPORT.md) | The audit memo and AI-use declaration |
| 5 | A 10-minute defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Assessors check the criteria marked ⚙ with the public and hidden test suites, and the rest by hand.

1. ⚙ All public tests and your own tests pass from a clean environment.
2. ⚙ On three regenerated panels, `cs_simple` is within 0.35 of the true simple ATT. *Justification:* the reference estimator's absolute error on these panels is 0.1 to 0.2 (bootstrap SE about 0.27), so 0.35 passes a correct implementation and fails a wrong base period or control group.
3. ⚙ `twfe_att` equals OLS with unit and period dummies (relative tolerance 1e-7).
4. ⚙ `cluster_bootstrap` follows the specified draw order, verified by replicating the standard error in a hidden test.
5. ⚙ `pretrend_test` returns p > 0.02 on the clean hidden panel and p < 0.01 on the panel with a differential trend, and `cs_simple` on the trended panel is shown to be at least 0.4 higher than on the clean one.
6. ⚙ The event-study shows growth with time since adoption and near-zero pre-period estimates on clean panels.
7. ✍ `ablation.py` regenerates all reported numbers, with standard errors, and the memo states which conclusions are and are not robust to each ablation.
8. ✍ The memo explains the TWFE bias mechanism in your own words with a numerical illustration from your noiseless test.
9. ✍ The validity section addresses all four threats named in D.2 and states what additional data (for example neighbour exposure) would test each.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and causal reasoning | 15 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Methodology: ablations and baselines | 20 |
| Testing | 10 |
| Documentation and reproducibility | 5 |
| Critical thinking and validity argument | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private GitHub repository** named `clbg-DS-T3-013-<your-github-username>` and copy in this assessment's `starter/staggered_did/`, `tests/`, `resources/` and `submission-template/`. Put `staggered_did/` at the repository root.
2. **Commit as you work.** Commit history is part of the evidence. A single "final" commit will be questioned at defence.
3. Include `REPORT.md` (from the [template](submission-template/REPORT.md)), which contains your AI-use declaration, and a short top-level `README.md` (at most 10 lines) saying how to run everything.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never replace the core requirements.

1. **Bacon decomposition.** Decompose the TWFE estimate into its 2×2 comparisons and weights, and identify the forbidden comparisons.
2. **Sensitivity to violations.** Implement a simple "smoothest-trend" sensitivity analysis: how much differential trend would erase the estimate?
3. **Doubly robust covariates.** Add a covariate (baseline electrification) and implement outcome regression or inverse-probability weighting for each group-time cell.
4. **Spillovers.** Simulate a contaminated control group (neighbouring never-treated LGAs benefit 30% as much) and measure the bias.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a statistical idea or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration inside `REPORT.md`: tool, purpose, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** code or methods adapted from documentation, papers or forums.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers or report text.
- **Defence (10 minutes).** The assessor asks you to explain, without notes, why TWFE is biased in your noiseless example; to say which of your results would change if neighbouring LGAs were affected; and gives an **unseen modification**, for example a fourth wave or a switch to not-yet-treated controls for pre-period cells, to implement and test live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Regression with fixed effects, the potential-outcomes idea, bootstrapping, pandas/numpy. |
| **New skill developed** | Auditing a causal claim: stating the estimand, building the estimator from comparisons, and attacking the assumptions. |
| **Decisions the member must make** | Which control group, how to aggregate, how to resample, which sensitivity checks matter, and what to recommend under uncertainty. |
| **What must be investigated independently** | Why TWFE fails here (they must construct the counterexample) and how large the failure is. |
| **Why it's interesting** | The 'official' TWFE number looks reasonable and is wrong. The member has to prove it, not just assert it. |
| **Evidence of competence** | Correct recovery of truth on unseen panels, a working placebo diagnostic, ablations that explain themselves, and a validity argument that identifies untestable assumptions. |
| **Misconceptions exposed** | 'Fixed effects remove all confounding.' 'A significant TWFE coefficient is the programme effect.' 'Flat pre-trends prove parallel trends.' |
| **Preparation for later work** | Leads to synthetic control and instrumental-variable designs, and to policy evaluation in the signature research challenges. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
