# ML-T2-009: Which Loan Model Ships?

> *Pick a model and a cut-off for a lender whose past is not a fair picture of its future.*

![Format: Comparative](https://img.shields.io/badge/format-comparative-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-009` |
| **Title** | Which Loan Model Ships? Time-Aware Model Selection for Mobile-Money Micro-Loans |
| **Subtrack** | ML Engineering |
| **Tier** | 2: Applied Proficiency |
| **Unit** | [ML-05: Evaluation, Validation and Model Selection](../README.md) |
| **Format** | Comparative |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 2 (each out of 5) |
| **Estimated time** | 14–22 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | scikit-learn pipelines, cross-validation, the idea of a decision threshold; ML-T1-011 is helpful but not required. |
| **Skills developed** | Time-aware validation; label maturity; leakage auditing; cost-sensitive thresholding; uncertainty of a model-selection estimate |
| **Technologies** | Python 3.10+, numpy, pandas, scikit-learn, pytest |

---

## B. Problem Statement

**NairaFlex** is a (fictional) mobile-money lender that gives airtime-and-wallet-based micro-loans through agents in six Nigerian cities. Loans last 14 to 90 days. Until now approvals followed a simple rule of thumb. The credit team has 18 months of history, **2,708 loans**, and has to choose a default-prediction model and an approval cut-off to run next quarter.

The money maths is asymmetric. Approving a loan that then defaults loses **60%** of its amount; refusing a loan that would have been repaid loses **8%** in forgone fees. So the right cut-off is not 0.5, and "accuracy" is irrelevant. The team's data scientist, who has left, handed over a notebook that scored 0.7% cost with random 5-fold cross-validation and a note saying "ready to ship".

Three things make that notebook untrustworthy, and you have to find and fix them without being told which is which. First, some columns are recorded *after* a loan goes bad. Second, the newest 213 loans have not reached their due date, so their `defaulted` value is **missing, not zero**. Third, the business changed on 1 July 2025: a new agent network opened in Maiduguri, SIM-swap fraud rose, and the old affordability signal weakened. A random split mixes past and future and flatters any model that memorises the old world.

Your job is to deliver a `Recommendation`: a fitted model, a threshold, and an estimate of cost per naira lent with an honest interval, produced by a validation design you can defend. The assessor will then test your recommendation on a **fully labelled quarter that you never see**.

## C. Objectives

When you finish, you should be able to show that you can:

- Build a forward-chaining validation scheme with a label-maturity embargo, and show why it differs from random k-fold on this data.
- Audit features for post-outcome leakage and justify each inclusion or exclusion.
- Treat unmatured loans as unknown, not as repaid.
- Choose a decision threshold from a cost matrix, without using data from the period you evaluate on.
- Compare at least two candidate model families and quantify the uncertainty of the comparison.
- Communicate to a credit committee what the estimate means, what it does not, and what monitoring would catch drift.

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `loanselect` package in [`starter/loanselect/`](starter/loanselect/). Signatures are fixed. Libraries are free (scikit-learn, pandas, numpy). **Method choices are yours and must be justified in `REPORT.md`.**

| ID | Requirement |
|---|---|
| **R1** | `usable_features(df)`: columns that could legitimately be known at the moment of disbursement. Exclude identifiers, the label, dates used only for splitting, and any leaky column you find. |
| **R2** | `matured(df)`: rows whose outcome is known, with a fresh `0..n-1` index. Missing labels must never be imputed as 0. |
| **R3** | `forward_splits(df, n_splits=4, val_days=45)`: consecutive validation windows of `val_days` ending at the latest disbursement; training loans must have **due dates** (`disbursed_on + term_days`) on or before the window's first day. |
| **R4** | `expected_cost(y, p, amount, threshold, fn_rate=0.6, fp_rate=0.08)`: total cost divided by total amount lent; a loan is approved when `p < threshold`. |
| **R5** | `best_threshold(y, p, amount, ...)` returns `(threshold, cost)` minimising R4 over candidates you choose. |
| **R6** | `bootstrap_ci(values, n_boot=1000, seed=0, alpha=0.05)`: percentile bootstrap interval for a mean; deterministic for a seed. |
| **R7** | `select_and_fit(train_df, seed=0) -> Recommendation`. Compare at least two candidates by forward-chaining cost, choose the threshold without future data, fit on all matured loans, and fill `cv_cost` and `cv_ci` from your forward-chaining folds. `model.predict_proba(df)` must accept raw frames, including a region never seen in training. |
| **R8** | `analysis.py` or notebook that reproduces the tables in `REPORT.md`: the leak audit, the maturity effect, random-versus-forward CV for each candidate, and the candidate comparison with intervals. |

### D.2 Engineering requirements (mandatory)

- Deterministic: the same input and seed give identical recommendations.
- No test-period information in model fitting, feature engineering or threshold choice. Scaling, encoding and imputation are fitted inside the training folds only.
- Keep the provided tests passing and add **at least 8 tests of your own** in `tests/test_member_*.py` (at least two for edge cases such as an empty validation window or all-same labels).
- Total runtime of `select_and_fit` on the provided data should stay under 3 minutes on a laptop.

### D.3 Privacy and responsibility

The data is **synthetic**; there is no real borrower. Credit scoring is high-stakes: under the Nigeria Data Protection Act 2023, automated decisions with significant effect call for transparency and a route to human review. In the report, state which features a regulator or customer could reasonably object to (for example region or device changes as proxies for protected groups), and what monitoring and human override you would require before deployment.

---

## E. Dataset and Resources

All data is **synthetic**, generated by a deterministic generator held in the assessor kit. Borrowers are fictional.

| File | Content |
|---|---|
| [`resources/data/loans.csv`](resources/data/loans.csv) | 2,708 loans disbursed 2024-07-01 to 2025-12-31. Columns: `loan_id, customer_id, disbursed_on, term_days, amount_ngn, avg_monthly_inflow_ngn, wallet_age_days, airtime_topups_30d, device_changes_90d, agent_region, prior_loans, prior_defaults, collection_calls_made, defaulted`. `defaulted` is empty for 213 loans whose due date is after the snapshot date 2025-12-31. About 9% of matured loans default. 176 KB. |

Licence: CC BY 4.0. Customers repeat (about three loans each), so rows are not independent. The hidden evaluation uses a separate, fully labelled quarter (Jan-Mar 2026) drawn from the same post-July-2025 regime.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `loanselect/` (completed starter) | The evaluation and selection code |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Guards for the leakage, maturity and threshold logic |
| 3 | `analysis.py` or `analysis.ipynb` | Reproduces every table and number in the report |
| 4 | `outputs/recommendation.json` | Chosen model, features, threshold, cost estimate and interval |
| 5 | `REPORT.md` (at most 1,500 words plus tables), from the [template](submission-template/REPORT.md) | Decision memo for the credit committee; includes the AI-use declaration |
| 6 | A short live defence | Verifies understanding (§K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Criteria marked ⚙ are checked automatically by the public and hidden test suites; the rest are checked by hand.

1. ⚙ Public and your own tests pass from a clean environment.
2. ⚙ No post-outcome column is used; unmatured loans are excluded; training loans in every fold had matured before the validation window began.
3. ⚙ Hidden test, three re-seeded loan histories: on the unseen quarter, realised cost with your recommended threshold is **at most 97% of the best trivial policy** (approve all or refuse all). *Justification:* the reference achieves 73-88% on these seeds, so 97% rules out a model that adds nothing while tolerating sampling noise.
4. ⚙ Your threshold's realised cost is within 1.4 times the cost of the oracle threshold chosen on the unseen quarter. *Justification:* the reference reaches 1.0-1.2 times; a larger gap means the threshold was fitted to noise.
5. ⚙ `cv_cost` lies between 0.55 and 1.5 times the realised cost. *Justification:* an honest estimate may be somewhat optimistic because of selection; an estimate from a model that sees the leaky column is about 0.15 times.
6. ✍ The report quantifies the effect of each of three corrections (leak removal, maturity, forward-versus-random validation) on the estimated cost.
7. ✍ The candidate comparison reports intervals and states whether the winner is distinguishable from the runner-up.
8. ✍ The report names the monitoring signal and the retraining trigger you would set.

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

1. **Create your own private repository** named `clbg-ML-T2-009-<your-github-username>` from this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `loanselect/` (your package), `tests/` (provided tests plus your own `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `outputs/recommendation.json`, `analysis.ipynb` or `analysis.py`, `REPORT.md` (from the template, including the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core requirements.

1. Replace the fixed 45-day windows with an expanding-versus-sliding training window comparison, and say when forgetting the old regime helps.
2. Evaluate fairness across `agent_region`: compare approval rates and cost, and discuss what an NDPA-compliant disclosure would say.
3. Add a conformal or isotonic recalibration step and test whether calibrated probabilities make the theoretical threshold 0.08/(0.08+0.6) work.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn (explain a concept, review your code). **They may not do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: tool, purpose, example prompt, how you verified the output. Undisclosed use that emerges at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code or method adapted from documentation or papers, with a link.
- **Collaboration:** discuss *general techniques* only. Do not share code, numbers or report text.
- **Verification of understanding.** In the short defence the assessor will ask you to (1) explain why a training loan disbursed three days before the validation window can still be illegal, (2) show where the threshold would move if the false-approval cost rose to 80%, and (3) rerun your selection with the leaky column deliberately added and explain the size of the change.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | scikit-learn pipelines, cross-validation, basic decision theory (cost-weighted thresholds), bootstrap resampling. |
| **New skill developed** | Designing validation that mimics deployment: time order, label maturity and leakage control, with an uncertainty-aware comparison. |
| **Decisions the member must make** | Which columns are legitimate, how to split in time, how wide the validation windows are, which candidates to compare, how to choose and justify the threshold, and how to express uncertainty. |
| **What must be investigated independently** | Which column leaks, what the 213 empty labels mean, and how the relationships changed in July 2025. None is flagged in the data. |
| **Why it's interesting** | A hand-over notebook says "ready to ship" and is wrong in three separate ways; the final check is a quarter of real outcomes you never see. |
| **Evidence of competence** | Realised cost on the unseen quarter, honest estimate-versus-realised agreement, and a report that attributes each correction's effect. |
| **Misconceptions exposed** | "Random k-fold is the default." "Missing labels are non-events." "Higher AUC means lower cost." "0.5 is the threshold." |
| **Preparation for later work** | Leads into ML-T3 nested validation and leaderboard overfitting, and ML-09 time-series modelling. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
