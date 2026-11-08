# DS-T2-025: Robust or Fragile?

> *Any single analysis of observational data is one path through a garden of forking paths. Walk them all, mark the ones that lead off a cliff, and say how strong a hidden confounder would have to be.*

![Format: investigation](https://img.shields.io/badge/format-investigation-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-025` |
| **Title** | Robust or Fragile? A Specification-Curve and Sensitivity Analysis of a Mobile-Banking Training Programme |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Competence and Method Selection |
| **Unit** | [DS-12: Applied Research and Reproducible Communication](../README.md) |
| **Format** | Investigation (secondary: Replication) |
| **Difficulty** | Technical 3 · Mathematical 4 · Research 4 · Engineering 3 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 16–26 hours over 2–3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Linear regression and robust standard errors; logistic regression; the idea of confounding and of conditioning on a mediator or collider (DS-T1-029 helps); bootstrap standard errors. |
| **Skills developed** | Specification-curve analysis; robustness versus fragility; bad controls (mediators and colliders); inverse-probability weighting; HC1 robust inference; E-values; writing an honest research summary for decision-makers |
| **Technologies** | Python 3.10+, pandas, NumPy, pytest. SciPy is permitted. Regression and propensity code must be your own (no statsmodels or scikit-learn for the estimators). |

---

## B. Problem Statement

A financial-inclusion NGO trained smallholder farmers to use mobile banking and now wants to say the training "raised household savings". Households chose whether to attend, and the data come from a survey twelve months later: 1,600 households, 11 variables, **synthetic** but built from the structure of real surveys. A consultant ran one regression and reported a large effect. A second consultant, with a different set of controls, reported a much smaller one. Both are "correct" in the sense that each ran what they ran. The NGO wants to know which to believe.

This is the **forking-paths** problem. Between the raw data and a reported number an analyst makes many defensible choices: transform the outcome or not, drop extreme values or not, which covariates to adjust for, how to adjust (regression or weighting). Each reasonable combination is a *specification*. A **specification curve** (Simonsohn, Simmons and Nelson) computes the estimate for every defensible specification and shows the whole distribution rather than the analyst's favourite.

But the curve is only informative if you are careful about which specifications are *defensible*. Two of the survey variables were measured **after** the training and are traps:

- `loan_taken` lies on a causal path from training to savings (training makes loans more likely, and loans reduce savings). Adjusting for it removes part of the very effect you want, answering a different question.
- `visited_agent` is influenced by both training and savings. Conditioning on a common effect of treatment and outcome (a **collider**) manufactures a spurious association and biases the estimate.

The estimand here is the **total** effect of attending the training. Your analysis must decide, and justify with causal reasoning rather than with whichever set gives the answer you like, which specifications are defensible, show that the answer survives (or not) across them, and then ask the question the curve cannot answer: how strong would an **unmeasured confounder** have to be to explain the result away? The E-value (VanderWeele and Ding, 2017) puts a number on that.

You will implement the estimators and the curve yourself, because the point is to see exactly where each number comes from. At Tier 2 the interfaces are specified and the numerical definitions are exact, but the analytical judgement (the defensible set, the interpretation, the proportionate conclusion) is yours, and part of the assessment is whether you keep your conclusion within what the evidence supports.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Implement OLS with HC1 robust errors and logistic regression from their equations.
2. Estimate an average treatment effect by inverse-probability weighting with a bootstrap standard error.
3. Construct and summarise a specification curve across outcome, control, method and sample choices.
4. Identify mediators and colliders among candidate controls and state their effect on the estimate.
5. Quantify sensitivity to unmeasured confounding with an E-value and interpret it in context.
6. Write a research summary whose strength of claim matches the robustness of the evidence.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Estimator definitions and the curve's construction are exact; the analytical judgement is open. Implement the `speccurve` package in [`starter/speccurve/`](starter/speccurve/). The function signatures are fixed because the automated tests import them. The internals are yours.

| ID | Requirement |
|---|---|
| **R1** | `ols(X, y) -> (beta, se)` with HC1 robust standard errors `V = n/(n-k)·(X'X)⁻¹X'diag(e²)X(X'X)⁻¹`. |
| **R2** | `logit_fit(X, t, tol, max_iter)`: Newton/IRLS logistic regression from zero; converges to the score equations. |
| **R3** | `estimate(df, spec, n_boot, seed) -> {effect, se, n}` in standard-deviation units, for a specification `{outcome, controls, method, trim}`: z-scored controls; OLS coefficient with HC1 se, or Hajek IPW with propensities clipped to [0.05, 0.95] and a bootstrap se (`default_rng(seed)`, `n_boot` resamples). Trimming drops rows above the 99th percentile of savings in the full sample. |
| **R4** | `spec_curve(df, space, n_boot, seed) -> DataFrame` over all combinations in `itertools.product` order with columns `outcome, controls, method, trim, effect, se, lo, hi, sig`. |
| **R5** | `summarise_curve(curve) -> dict` with `n_specs, share_positive, share_sig_positive, median_effect, min_effect, max_effect, sign_flips`. |
| **R6** | `defensible(curve, bad_controls)`: keep specifications whose control set avoids every variable in `bad_controls`. |
| **R7** | `e_value(d, d_ci_bound)`: `RR = exp(0.91|d|)`, `E = RR + sqrt(RR(RR-1))`; with a CI bound, its E-value (1.0 if the bound crosses 0). |

### D.2 Engineering requirements (mandatory)

- **Own estimators.** Do not call a statistics library for the regressions or the propensity model; you may use one in your own tests to cross-check.
- **Determinism.** All randomness comes from the seeded generator; the full curve at the default settings runs in well under a minute.
- **Pre-registration discipline.** Write your list of bad controls and your reasoning in the report **before** you look at how it changes the curve; the report must say that you did.
- **Tests.** Keep the provided tests passing and add **at least 10 tests of your own** in `tests/test_member_*.py`, including edge cases you found yourself.
- **Dependencies.** Use only the packages in [`starter/requirements.txt`](starter/requirements.txt). If you add one, justify it in your report.

### D.3 Privacy and responsibility

The data is **synthetic**: no household, region or programme is real. Real household finance surveys are sensitive personal data under the Nigeria Data Protection Act 2023: savings and loans can expose individuals, so only aggregates should be published, and small cells suppressed. In your report, say how you would present results for a small region.

### D.4 Optional enhancements (not required for full marks)

- Add region fixed effects as another control dimension and report what changes.
- A leave-one-control-out analysis showing which single control moves the estimate most.
- Report the curve as a standard plot (sorted effects with a marker panel below) and describe what a reader should see.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/households.csv`](resources/data/households.csv): 1,600 rows × 11 columns, about 79 KB, UTF-8. [`resources/data_dictionary.md`](resources/data_dictionary.md) states what each column is and **when it was measured**. |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed: confounders (income, education, distance) drive both training and savings; training raises savings, partly offset through loans; a collider is affected by training and savings; about 1% of savings values are extreme outliers. No real survey is described. |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Integrity** | The contract test checks the SHA-256, so do not edit the file |

**Key references.** Simonsohn, Simmons and Nelson (2020), *Specification curve analysis*, Nature Human Behaviour. VanderWeele and Ding (2017), *Sensitivity analysis in observational research: introducing the E-value*, Annals of Internal Medicine. Cinelli, Forney and Pearl (2022), *A crash course in good and bad controls*, Sociological Methods & Research. Cite what you use.

**Known limitations (by design).** Treatment effects are constant by construction, there is one outcome, and the confounders are all measured, so the "truth" is easier to approach than in real life. The hidden tests regenerate households with different seeds and effect sizes.

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-12-applied-research-and-communication/DS-T2-025-robust-or-fragile
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract        # should pass immediately: checks data and scaffold
pytest                    # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `speccurve/` package (the completed starter) | The core technical evidence |
| 2 | `tests/test_member_*.py` | Shows you can pin behaviour down and think about edge cases |
| 3 | `outputs/spec_curve.csv` and a specification-curve figure | The full curve, with the defensible and indefensible specifications distinguished |
| 4 | `analysis.py` or `analysis.ipynb` | Runs the curve, the defensible subset, the E-values and any extra checks |
| 5 | `REPORT.md` (from the [template](submission-template/REPORT.md)), with the AI-use declaration inside | Communicates decisions and limits; integrity declaration (see §K) |
| 6 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites, the rest by hand.

1. ⚙ Provided and member tests pass from a clean environment.
2. ⚙ `ols` and `logit_fit` match independent computations (HC1 formula; score equations to 1e-6); OLS and IPW point estimates match independent implementations on hidden data (OLS to 1e-6 relative, IPW to 2e-4).
3. ⚙ The curve has 48 specifications in the stated order, and `defensible` removes exactly those whose control set contains a bad control.
4. ⚙ **Bias structure:** on hidden households, the median effects by control set show the expected pattern: no-control above core controls (confounding), core-plus-collider more than 0.02 SD below core (collider bias), core-plus-mediator above core, and core versus core-plus-demographics within 0.05. *Justification:* these orderings follow from the generating structure and held on every tested seed and effect size (3000, 5000, 6500, 8000).
5. ⚙ On the defensible subset every specification is positive and at least 90% are significantly positive, and the subset's range is no wider than the full curve's.
6. ⚙ `e_value` reproduces the published formula and example.
7. ✍ The report states and justifies the list of bad controls on causal grounds, not on the basis of results.
8. ✍ The report gives the E-value for the point estimate and the confidence bound in plain words, and says which real-world confounders would need to be that strong.
9. ✍ The conclusion is proportionate: it separates what is robust (sign and approximate size across defensible specifications) from what is not, and does not claim a causal effect larger than the evidence allows.

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

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-DS-T2-025-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` into it. Your package sits at the repository top level.
2. Commit as you work. Your commit history is part of the evidence (see §K); a single "final" commit will be questioned at defence.
3. Add your outputs and `REPORT.md`, then run `pytest` from a clean environment built from your `requirements.txt`.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository, using the **Assessment submission** template. Include the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never stand in for the core requirements.

1. **Heterogeneity.** Does the effect differ by region or education? Test it without creating a new garden of forking paths.
2. **Negative control.** Find an outcome the training should not affect and check that your pipeline estimates about zero.
3. **Permutation check.** Shuffle `trained` among households with similar propensity and show that the curve collapses towards zero.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept, suggest an idiom or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: which tool, what for, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources, with a link.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers, thresholds or report text.
- **How your understanding is verified.** In the 5-minute defence the assessor will: 
  1. picks one specification from your curve and asks you to reproduce its number by hand from the equations;
  2. asks why adjusting for `visited_agent` can make an effect look smaller, with a diagram or a two-line argument;
  3. gives you an unseen modification, for example adding a new candidate control or a different trimming rule, and asks you to extend the curve and interpret the change live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Regression, robust standard errors, logistic regression, confounding. DS-T1-029 helps but is not required. |
| **New skill developed** | Treating an analysis as a distribution over defensible choices, and reasoning causally about which choices are defensible. |
| **Decisions the member must make** | Which controls are bad and why; how to summarise the curve; how to word a conclusion; how to read an E-value. |
| **What must be investigated independently** | How each control set moves the estimate and why; whether the answer depends on method, scale or trimming. |
| **Why it's interesting** | Two plausible regressions giving different answers is the everyday reality of observational analysis; the curve plus the E-value is a principled response. |
| **Evidence of competence** | Estimators matching independent computations, the expected bias structure reproduced on hidden data, and a report whose claims match its robustness. |
| **Misconceptions exposed** | More controls are always better. The significant specification is the finding. A p-value measures how sure we are of causation. |
| **Preparation for later work** | Leads to DS-T3 referee-style review of published analyses and to the causal-inference unit's identification strategies. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
