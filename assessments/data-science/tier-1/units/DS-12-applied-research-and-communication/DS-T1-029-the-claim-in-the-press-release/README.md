# DS-T1-029: The Claim in the Press Release

> *A before-and-after number in a press release is a hypothesis. Turn it into evidence, with the uncertainty it deserves, in a form someone else can rerun.*

![Format: replication](https://img.shields.io/badge/format-replication-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-029` |
| **Title** | The Claim in the Press Release: Auditing a School-Meals Attendance Claim with Honest Intervals |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-12: Applied Research and Reproducible Communication](../README.md) |
| **Format** | Replication (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 3 · Research 3 · Engineering 2 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 10–16 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Proportions, standard errors and confidence intervals at the level of an introductory statistics course; NumPy random generators; pandas groupby; running `pytest`. |
| **Skills developed** | Confidence intervals for proportions; difference-in-differences; the bootstrap; clustered data and why naive intervals are too narrow; claim-versus-evidence judgement; reproducibility manifests |
| **Technologies** | Python 3.10+, pandas, NumPy, pytest. Standard library `statistics.NormalDist` for the normal quantile. |

---

## B. Problem Statement

A state government's press release announces the success of a school-meals programme: *"Regular attendance in programme schools rose from 70% to 80% after the meals were introduced."* A journalist asks the CLBG data desk whether the figures hold up. The state's evaluation unit has shared the underlying survey: **2,880 pupil records from 24 schools** (12 programme schools and 12 comparison schools that never received meals), 60 pupils sampled per school before the programme and 60 after. Each record says whether the pupil attended at least 80% of school days (`regular = 1`). The data is synthetic but built the way such surveys are built.

Your job is to audit the claim, not to confirm or demolish it. Three questions carry the audit:

1. **Is the number even right, and how precise is it?** The point estimates are easy. The *interval* around them is where methods differ, and for a proportion near the edges the textbook Wald formula misbehaves. You will implement the Wilson interval and the Wald interval for a difference from their formulas.
2. **Is "after the programme" the same as "because of the programme"?** Attendance in the comparison schools may also have moved between the two surveys (a different term, a harvest, a festival). The programme's own effect is the programme schools' change *minus* the comparison schools' change: a **difference-in-differences**.
3. **How sure are we?** Pupils in the same school are not independent: they share a headteacher, a road and a market day. Treating 2,880 pupils as 2,880 independent observations makes the interval too narrow. The honest unit of resampling is the **school**. You will implement a school-level (cluster) bootstrap and compare it with the naive pupil-level interval.

Finally you will give the journalist a verdict in plain words (supported, overstated or inconclusive), derived mechanically from your interval, and you will write a **reproducibility manifest** so that anyone, including the state's evaluation unit, can rerun your numbers and confirm they match.

This is Tier 1: formulas, random-number procedures and decision rules are fully specified, and the tests check them. The skill assessed is careful implementation of standard methods and an honest reading of what they say.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Compute Wilson and Wald confidence intervals for proportions directly from their formulas.
2. Estimate a difference-in-differences and say what it controls for that a before/after change does not.
3. Implement a percentile bootstrap, then a cluster bootstrap that resamples schools.
4. Show, with numbers, how ignoring clustering overstates certainty.
5. Turn an interval into a verdict on a causal claim using a stated rule.
6. Record a reproducibility manifest and rerun the analysis from it.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

All formulas and random-number procedures are specified, so results are comparable. Implement the `claimcheck` package in [`starter/claimcheck/`](starter/claimcheck/). The function signatures are fixed because the automated tests import them. The internals are yours.

| ID | Requirement |
|---|---|
| **R1** | `wilson_ci(k, n, level=0.95)`: the Wilson score interval, with the lower bound exactly 0 when `k = 0` and the upper bound exactly 1 when `k = n`. The normal quantile comes from `statistics.NormalDist`. |
| **R2** | `diff_in_proportions(k1, n1, k2, n2, level=0.95)`: the Wald interval for `p1 - p2` with the unpooled standard error; returns `(difference, lower, upper)`. |
| **R3** | `bootstrap_ci(values, stat, n_boot=2000, seed=0, level=0.95)`: percentile bootstrap with `numpy.random.default_rng(seed)` and `rng.integers(0, n, n)` per iteration. |
| **R4** | `cluster_did(df, n_boot, seed, level)`: the difference-in-differences of the share of regular attenders, with a naive pupil-level Wald interval and a cluster-bootstrap interval that resamples schools within each group (programme first, then comparison, schools sorted by id). It returns the keys `estimate, lo, hi, naive_lo, naive_hi, programme_change, comparison_change, width_ratio`. |
| **R5** | `verdict(result, claimed=None)`: `inconclusive` if the cluster interval contains 0; else `supported` if it contains the claimed effect (default: the programme group's raw change); else `overstated`. |
| **R6** | `write_manifest(path, data_path, seed)`: a sorted-key JSON file with the data SHA-256, seed, row count, Python and pandas versions, which it also returns. |

### D.2 Engineering requirements (mandatory)

- **Determinism.** Same data and seed give identical numbers; results do not depend on row order.
- **No hidden resampling.** All randomness comes from `default_rng(seed)` as specified.
- **Speed.** The cluster bootstrap works on per-school counts, not on 2,880 rows per iteration; 2,000 iterations take well under a few seconds.
- **Tests.** Keep the provided tests passing and add **at least 8 tests of your own** in `tests/test_member_*.py`, including edge cases you found yourself.
- **Dependencies.** Use only the packages in [`starter/requirements.txt`](starter/requirements.txt). If you add one, justify it in your report.

### D.3 Privacy and responsibility

The data is **synthetic**: no pupil, school or state is real. Real school-attendance surveys are children's data, a special concern under the Nigeria Data Protection Act 2023: pupil identifiers should never leave the evaluation unit, and school-level results can identify small schools. In your report, add a short note on what you would publish (aggregates by group) and what you would not (pupil rows, school names with small counts).

### D.4 Optional enhancements (not required for full marks)

- A second interval for the DiD by resampling schools in a different design (for example a permutation test across the 24 schools) and a comment on the agreement.
- A plot of the cluster bootstrap distribution with the naive interval overlaid.
- A one-paragraph correction note a newspaper could print.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/attendance.csv`](resources/data/attendance.csv): 2,880 rows × 5 columns (`school_id`, `group`, `period`, `pupil_id`, `regular`), about 107 KB, UTF-8 |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed: 24 schools with school-level differences in baseline attendance and in how much each school's attendance moved between surveys; a term-time rise common to both groups; and a programme effect for the programme schools. No real survey is described. |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Integrity** | The contract test checks the SHA-256, so do not edit the file |

**Known limitations (by design).** Pupils are a fresh sample each period (no pupil appears twice), schools were not randomised to the programme, and 12 schools per group is small for a bootstrap whose coverage is only approximately nominal. Discuss all three in your report. The hidden tests regenerate the survey with other seeds.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-12-applied-research-and-communication/DS-T1-029-the-claim-in-the-press-release
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract        # should pass immediately: checks data and scaffold
pytest                    # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `claimcheck/` package (the completed starter) | The core technical evidence |
| 2 | `tests/test_member_*.py` | Shows you can pin behaviour down and think about edge cases |
| 3 | `audit.py` or `audit.ipynb` | Runs the whole audit from the CSV and prints every number in the report |
| 4 | `outputs/manifest.json` | The reproducibility manifest produced by `write_manifest` |
| 5 | `REPORT.md` (from the [template](submission-template/REPORT.md)), with the AI-use declaration inside | Communicates decisions and limits; integrity declaration (see §K) |
| 6 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites, the rest by hand.

1. ⚙ Provided and member tests pass from a clean environment.
2. ⚙ Wilson and Wald intervals match the published formulas to 1e-4; the Wilson interval respects 0 and 1 at the edges.
3. ⚙ `cluster_did` returns the estimate equal to the direct computation from the data, a naive interval equal to the formula, and a cluster interval that is deterministic, order-independent and agrees with the specified procedure to within 0.025.
4. ⚙ The cluster interval is wider than the naive one on the public data (width ratio above 1.2) and on hidden data (above 1.0). *Justification:* the school-level variation in change makes pupil-level independence false; the reference ratio is 1.44 on the public file and above 1.0 on all hidden seeds.
5. ⚙ `verdict` follows the stated rule, and on the public data returns `inconclusive` while the naive interval excludes 0.
6. ⚙ The manifest is byte-identical across runs and its hash matches the file.
7. ✍ The report states the verdict in plain words and explains, without jargon, why the press release's number is not the programme's effect.
8. ✍ The report states what 12 schools per group, non-random assignment and fresh pupil samples limit.

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

1. **Create your own private repository** named `clbg-DS-T1-029-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` into it. Your package sits at the repository top level.
2. Commit as you work. Your commit history is part of the evidence (see §K); a single "final" commit will be questioned at defence.
3. Add your outputs and `REPORT.md`, then run `pytest` from a clean environment built from your `requirements.txt`.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository, using the **Assessment submission** template. Include the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never stand in for the core requirements.

1. **Coverage check.** Simulate 200 surveys with a known effect and compare the coverage of the naive and cluster intervals.
2. **Parallel trends.** Discuss what you would need to see in earlier surveys to believe difference-in-differences here.
3. **Intra-school correlation.** Estimate it from the data and compute the design effect it implies, then compare with `width_ratio`.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept, suggest an idiom or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: which tool, what for, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources, with a link.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers, thresholds or report text.
- **How your understanding is verified.** In the 5-minute defence the assessor will: 
  1. picks one number in your report and asks you to reproduce it from the manifest on a clean machine;
  2. asks why resampling schools is different from resampling pupils, and what happens to the interval if you resample pupils;
  3. gives you an unseen modification, for example a 90% interval, a different claimed effect, or stratifying by programme region, and asks you to change the code and tests live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Proportions, confidence intervals, basic NumPy. No prior bootstrap experience. |
| **New skill developed** | Reading a causal claim as a statement about a counterfactual, and bounding it with an honest interval. |
| **Decisions the member must make** | How to word a verdict; how to explain clustering plainly; which limitations to name. |
| **What must be investigated independently** | Whether the comparison schools also changed, and how much school-to-school variation there is in change. |
| **Why it's interesting** | Government programme claims are routinely made from before/after numbers; the audit pattern generalises to any press-release claim. |
| **Evidence of competence** | Exact formulas, deterministic procedures verified against the specification, a wider cluster interval, and a mechanical verdict. |
| **Misconceptions exposed** | A before/after rise is an effect. Pupils are independent. A narrow interval means a precise study. 'Not significant' means 'no effect'. |
| **Preparation for later work** | Leads to DS-T2 robustness and sensitivity analysis and DS-T3 research review of published claims. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
