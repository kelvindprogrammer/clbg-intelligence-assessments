# DS-T3-022: Referee Report

> *Peer review is a technical skill. Find what is wrong with a confident claim, prove it with the data, and say what can still be believed.*

![Format: open-ended](https://img.shields.io/badge/format-open%20ended-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T3-022` |
| **Title** | Referee Report: Auditing an Industry Whitepaper's Causal Claim and Re-analysing the Data |
| **Subtrack** | Data Science |
| **Tier** | 3: Advanced Practice and Research-Informed Judgement |
| **Unit** | [DS-12: Applied Research and Reproducible Communication](../README.md) |
| **Format** | Open-ended review (secondary: Replication) |
| **Difficulty** | Technical 3 · Mathematical 4 · Research 5 · Engineering 3 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 22–36 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Two-sample proportion tests; multiple-comparisons ideas (Bonferroni, false discovery rate); cohorts, confounding and censoring in observational data; permutation tests; writing a structured critique. DS-T2-025 or DS-T1-029 are good preparation. |
| **Skills developed** | Critical appraisal of a quantitative claim; detecting composition effects (Simpson's paradox), right-censoring bias, subgroup fishing and post-hoc thresholds; false-discovery control; permutation inference; re-analysis; writing a referee report |
| **Technologies** | Python 3.10+, pandas, NumPy, pytest. Standard library `statistics.NormalDist`. |

---

## B. Problem Statement

ScoreWise Lending, a fictional digital lender, has published a whitepaper (`resources/whitepaper.md`) claiming that its new machine-learning credit-scoring model **"halves loan defaults"**: the default rate fell from 12.3% to 6.1% (p < 0.001), the effect is "especially large for farmers", and it is "clearest for borrowers with a bureau score of 60 or more". The whitepaper recommends that regulators recognise a 50% reduction in default risk when setting provisioning rules for lenders. A financial regulator's technical team has asked CLBG to referee it, and to say, with evidence, what in it can be relied on.

You also have the data behind the paper: 2,400 loans (`resources/data/loans.csv`): 1,200 in the quarter before the model and 1,200 in the quarter after. The whitepaper's *numbers* are reproducible from this file. Whether its *conclusions* follow is the question.

A good referee does four things, and this assessment is built around them:

1. **Reproduces before criticising.** Check that the paper's headline numbers come out of the data. If they do not, that is the first finding.
2. **Looks for the mechanisms by which a true-looking number can mislead.** The paper compares two quarters, not randomised groups; it excludes unfinished loans from its default rates; it reports subgroup results after looking at many; and it reports a threshold chosen by scanning. Each has a statistical signature that the data can show.
3. **Re-analyses defensibly and says how much of the claim survives.** Not "the paper is wrong" but "the effect is X, with this uncertainty, under these assumptions, and here is what cannot be known from this design".
4. **Writes it so the editor can act.** A referee report ranks concerns by how much they matter, backs each with evidence the authors can check, and ends with a recommendation.

You will build the analytical tools yourself, in `refereekit`, with exact definitions so that results are comparable and testable: a composition check, Benjamini–Hochberg false-discovery control, a subgroup scanner, a censoring diagnostic, a max-statistic permutation test for the threshold search, and a corrected, standardised effect estimate with a bootstrap interval. The tools run on the public file; the hidden tests run them on freshly generated lending data, including a **null world** in which the model has no effect at all.

The written referee report (`REPORT.md`) is the main deliverable and carries most of the marks. At Tier 3 there is no checklist of flaws to find: the tools show you where to look, but identifying which problems matter most and what the data can support is your judgement.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Reproduce a whitepaper's headline numbers and check each claim against its stated methods.
2. Detect cohort composition differences and report a standardised effect.
3. Diagnose right-censoring bias and compare cohorts over a common observation window.
4. Control false discoveries across many subgroup comparisons with Benjamini–Hochberg.
5. Test a post-hoc threshold with a max-statistic permutation null.
6. Write a prioritised referee report whose recommendation is proportionate to the evidence.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Tool definitions are exact; the review itself is open-ended. Implement the `refereekit` package in [`starter/refereekit/`](starter/refereekit/). The function signatures are fixed because the automated tests import them. The internals are yours.

| ID | Requirement |
|---|---|
| **R1** | `simpson_check(df, outcome, treat, strata) -> dict` with `overall_diff`, `stratum_diffs`, `std_diff` (stratum-size-weighted), `reversal` (signs differ) and `composition_shift` (total-variation distance between arms' stratum distributions). |
| **R2** | `bh_adjust(pvals, q) -> (adjusted, rejected)`: Benjamini–Hochberg step-up adjusted p-values in original order, and `adjusted <= q`. |
| **R3** | `subgroup_scan(df, outcome, treat, cols) -> DataFrame[column, level, n, diff, p]` using pooled two-proportion z-tests; levels missing an arm skipped. |
| **R4** | `censoring_check(df) -> dict` with `matured_share`, `naive_default`, `H` (the longest maturity such that all loans of that maturity or shorter have matured) and `common_window_default`. |
| **R5** | `max_stat_permutation_p(df, outcome, treat, score_col, thresholds, n_perm, seed)`: `{observed, p}` with `p = (1 + #{perm >= observed}) / (n_perm + 1)`, using `default_rng(seed)` and `rng.permutation` of the treatment vector; thresholds with fewer than 30 rows in an arm are ignored. |
| **R6** | `corrected_effect(df, strata, n_boot, seed) -> dict`: restrict to loans with `maturity_days <= H`, compute the stratum-standardised risk difference, and a percentile 95% bootstrap interval (`default_rng(seed)`, `rng.integers(0, n, n)`). Keys: `estimate, lo, hi, n, H`. |

### D.2 Engineering requirements (mandatory)

- **Reproducibility.** Every number in your report must come from a script you submit and regenerate from the CSV.
- **Determinism.** All randomness is seeded as specified.
- **Separation of claim and evidence.** Keep the whitepaper's numbers (as stated) separate from your computed ones in the script output, so the editor can compare.
- **Tests.** Keep the provided tests passing and add **at least 10 tests of your own** in `tests/test_member_*.py`, including edge cases you found yourself.
- **Dependencies.** Use only the packages in [`starter/requirements.txt`](starter/requirements.txt). If you add one, justify it in your report.

### D.3 Privacy and responsibility

The data is **synthetic**: no borrower, lender or region is real. Real loan-performance data is financial personal data under the Nigeria Data Protection Act 2023, and small subgroups (for example young traders in one region) can identify people. In your report, say what you would redact in a review sent to the lender, and why subgroup results with small cells should not be published.

### D.4 Optional enhancements (not required for full marks)

- Reconstruct the whitepaper's reported counts (defaults among matured loans) and say which of its tables you could and could not reproduce.
- Propose a better study design (a randomised or staggered roll-out) and the sample size it would need to detect a 2-point reduction.
- A one-page non-technical note for the regulator: what to believe, what not to, and what to ask the lender for next.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/loans.csv`](resources/data/loans.csv): 2,400 loans × 11 columns, about 172 KB; [`resources/whitepaper.md`](resources/whitepaper.md): the document under review |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed. Loans are originated in two consecutive quarters; `defaulted` is observed only for loans that had matured by 30 September 2025; the true effect of the model on default is a modest uniform reduction. The company and its figures are fictional. |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Integrity** | The contract test checks the SHA-256 of `loans.csv`, so do not edit it |

**Columns.** `cohort` (control = before the model, treated = after), `originated_on`, `region`, `occupation`, `age_band`, `amount_band`, `risk_score` (0 to 100; higher means riskier; the derived `risk_band` is low below 33, medium below 67, else high), `maturity_days` (30, 60, 90 or 180), `matured` (1 if the loan had reached maturity by the cut-off), `defaulted` (missing if not matured).

**Known limitations (by design).** The "before/after" design cannot be repaired into a randomised trial by any amount of statistics; your report must say what it can and cannot identify. The hidden tests regenerate lending data, including a world in which the true effect is zero.

**Setup**

```bash
cd assessments/data-science/tier-3/units/DS-12-applied-research-and-communication/DS-T3-022-referee-report
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract        # should pass immediately: checks data and scaffold
pytest                    # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `refereekit/` package (the completed starter) | The core technical evidence |
| 2 | `tests/test_member_*.py` | Shows you can pin behaviour down and think about edge cases |
| 3 | `review_analysis.py` or `review_analysis.ipynb` | Reproduces the paper's numbers, runs your tools and prints every number in the report |
| 4 | `outputs/` tables: reproduction table, composition, censoring, BH-adjusted subgroup table, permutation result, corrected effect | Evidence the editor can check |
| 5 | `REPORT.md` (from the [template](submission-template/REPORT.md)), with the AI-use declaration inside | Communicates decisions and limits; integrity declaration (see §K) |
| 6 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites, the rest by hand.

1. ⚙ Provided and member tests pass from a clean environment.
2. ⚙ Composition: `simpson_check` equals an independent calculation on hidden data, finds a composition shift above 0.15, and the standardised difference is smaller in magnitude than the raw difference by at least 1 percentage point. *Justification:* the treated cohort is built to be materially safer; the shift is about 0.18–0.23 on all tested seeds.
3. ⚙ Censoring: `H` and the common-window default rates equal independent calculations, and the naive control default rate exceeds the common-window one.
4. ⚙ Corrected effect: on hidden data the estimate is within **2.5 percentage points** of the true effect and closer to it than the raw gap; in a **null world** (true effect zero) the interval contains 0 or the estimate is under 2 points in magnitude. *Justification:* with about 1,900 comparable loans the standard error is about 1.1 points, so 2.5 points is roughly 2 standard errors; the reference errs by 0.2 to 1.9 points on the tested seeds.
5. ⚙ Benjamini–Hochberg matches an independent implementation, and the permutation test reproduces the specified procedure exactly.
6. ✍ The report opens by stating whether the headline numbers reproduce, then ranks concerns (major, minor), each backed by a number from your script.
7. ✍ The report quantifies how much of the claimed 50% reduction survives each correction, and gives a corrected effect with its uncertainty.
8. ✍ The report separates what the data can support from what the before/after design cannot (confounding by time, selection of borrowers), and recommends accept, revise or reject with conditions.

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

1. **Create your own private repository** named `clbg-DS-T3-022-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` into it. Your package sits at the repository top level.
2. Commit as you work. Your commit history is part of the evidence (see §K); a single "final" commit will be questioned at defence.
3. Add your outputs and `REPORT.md`, then run `pytest` from a clean environment built from your `requirements.txt`.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository, using the **Assessment submission** template. Include the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never stand in for the core requirements.

1. **Sensitivity of the correction.** Redo the corrected effect with a different observation window or strata and report how stable the estimate is.
2. **Pre-registration note.** Write the analysis plan the lender should have filed before the roll-out.
3. **Replicate a published error.** Find a real, public correction or retraction involving censoring or subgroup claims, and compare its flaw with those here.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept, suggest an idiom or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: which tool, what for, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources, with a link.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers, thresholds or report text.
- **How your understanding is verified.** In the 5-minute defence the assessor will: 
  1. asks you to take your single most serious concern and show the number, the code and the argument that supports it;
  2. asks what the lender could say in rebuttal to your second concern and whether it would change your recommendation;
  3. gives you an unseen modification, for example a different post-hoc threshold grid or an extra stratifying variable, and asks you to rerun the tools and update the claim live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Proportion tests, confounding and censoring, multiple testing, permutation tests. Writing. |
| **New skill developed** | Refereeing: turning suspicion into reproducible evidence, ranking concerns, and recommending proportionately. |
| **Decisions the member must make** | Which concerns are major; how to correct each; how to describe what is left; accept, revise or reject. |
| **What must be investigated independently** | Which mechanisms inflate the paper's numbers and by how much, given a data file with no list of flaws. |
| **Why it's interesting** | Industry whitepapers and programme evaluations drive regulation; the flaws here (composition, censoring, fishing, thresholds) recur everywhere. |
| **Evidence of competence** | Tools that match independent calculations, hidden-world accuracy including a null world, and a report whose claims all trace to the script. |
| **Misconceptions exposed** | A tiny p-value means a big, real effect. Excluding unfinished cases is harmless. Subgroup results that survive are robust. Re-analysis can fix a non-randomised design. |
| **Preparation for later work** | Prepares for the capstone-level work of reviewing and publishing analyses, and for evaluating ML system claims in the AI Engineering track. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
