# DS-T2-009: Small Schools, Big Swings

> *The ministry wants to reward its ten best schools. The raw league table's "best" schools have six candidates each. Build an estimator that knows the difference between excellent and lucky, and prove it is better.*

![Format: Comparative](https://img.shields.io/badge/format-comparative-e36209) ![Tier 2](https://img.shields.io/badge/tier-2-dbab09) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-009` |
| **Title** | Small Schools, Big Swings: Empirical Bayes for School Pass Rates |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Engineering and Independent Problem-Solving |
| **Unit** | [DS-05: Probability and Statistics](../README.md) |
| **Format** | Comparative (secondary: Implementation) |
| **Difficulty** | Technical 3 · Mathematical 4 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 20–35 hours over 2–3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | Binomial and beta distributions; maximum likelihood; Bayes' theorem for a conjugate pair; pandas group-by; one of the DS-05 Tier 1 assessments, or equivalent experience with simulation and intervals |
| **Skills developed** | Hierarchical thinking; empirical Bayes and shrinkage; marginal likelihood estimation; covariate-informed priors; evaluation against noisy held-out data; ranking and selection under uncertainty; communicating "regression to the mean" to policy makers |
| **Technologies** | Python 3.10+, NumPy, SciPy, pandas, matplotlib, pytest. Optional: a probabilistic programming library (PyMC, NumPyro or CmdStanPy) for a full-Bayes comparison |

---

## B. Problem Statement

A state Ministry of Education (fictional, with 16 LGAs and 600 senior secondary schools) publishes an annual league table of the share of candidates who obtain **five credits including English and Mathematics** in the senior school certificate examination. This year the ministry plans to:

- give a **"School of Excellence" award** and a grant to the **top 10** schools; and
- enrol the **bottom 20** schools in a teacher-support **intervention programme**.

You have three years of results (2022–2024) for every school, together with its LGA, ownership (public, private or mission) and location (urban or rural). Cohort sizes range from **2 to over 250 candidates a year**. When the desk officer sorted the raw three-year pass rates, the top of the table was full of schools with six or eight candidates and a perfect record, and the bottom was full of small rural schools with zero passes. The Commissioner asks whether those are really the best and worst schools in the state, or the luckiest and unluckiest.

Your brief:

1. Build an estimator of each school's **long-run pass rate** (the rate it would achieve in a typical year) with an honest uncertainty interval.
2. **Compare** it fairly against the raw rate and at least one other principled alternative, using an evaluation design you choose and justify.
3. Recommend the award list and the intervention list, and explain the change to the Commissioner, who will have to defend it to principals whose schools "dropped".

What makes it hard:

- **The truth is never observed.** Next year's results are themselves noisy, especially for small schools. If you evaluate against them naively, every estimator looks bad and the differences between them shrink.
- **Small schools are not a random subset.** Look at who has small cohorts before you choose what to shrink towards.
- **Shrinkage is a modelling decision with consequences.** It moves some schools *up* and some *down*. A principal whose school drops out of the award list will want to know why a school with a worse raw record ranks above theirs.
- **Interval honesty.** A posterior interval from a model that ignores year-to-year variation can be confidently wrong for the largest schools.

**What you may assume:** results are recorded correctly (no data errors are planted in this assessment); a school's long-run rate is stable over the period apart from ordinary year-to-year variation; candidates within a school-year are exchangeable.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Formulate** a hierarchical (beta-binomial or logit-normal) model for many small binomial units and explain shrinkage as a precision-weighted compromise.
2. **Estimate** prior hyperparameters by marginal likelihood (empirical Bayes), and extend the prior to use covariates when the data justify it.
3. **Design an evaluation** that compares estimators fairly when the target is latent, for example a held-out year with an adjustment for the binomial noise in the held-out rates, or simulation from a fitted model, and **beat the raw baseline by a margin you can quantify**.
4. **Reason about ranking and selection**: what the award and intervention lists should optimise, and how uncertainty changes them.
5. **Communicate** regression to the mean and shrinkage to a non-technical decision-maker, including the fairness implications for particular kinds of school.

---

## D. Technical Requirements

### D.1 The contract (mandatory)

You design your package, but the automated evaluation imports this contract from `smallarea/__init__.py` (see [`starter/smallarea/__init__.py`](starter/smallarea/__init__.py)):

| ID | Requirement |
|---|---|
| **R1** | `estimate_rates(results, schools, level=0.90)` returns one row per school (sorted by `school_id`) with `school_id, estimate, lower, upper`: your **recommended** estimator of the long-run rate and a central interval at `level`. It must work for any subset of years and for a school with no results rows. |
| **R2** | `select_schools(results, schools, k, which)` returns the k schools you recommend for the award (`"top"`) or the intervention (`"bottom"`). You decide the selection rule, and you must justify it. |

### D.2 The study (mandatory)

| ID | Requirement |
|---|---|
| **R3** | **Exploration.** Show how cohort size, ownership, location and LGA relate to raw rates, and what that implies for the choice of prior. Include a funnel plot (raw rate against cohort size, with binomial control limits). |
| **R4** | **At least three estimators**, implemented in your package and compared: (a) the raw pooled rate (the baseline), (b) empirical Bayes with a single common prior, and (c) at least one estimator that uses school characteristics or the LGA, whether a stratified or regression prior, a logit-normal mixed model, or full Bayes. Derive the posterior for (b) and state the marginal likelihood you maximise. |
| **R5** | **Evaluation design.** Choose and justify metrics and a validation design that does not use information unavailable at decision time. The design must account for the noise in any held-out "truth". At minimum, report a squared-error comparison with an interval or a paired bootstrap for the difference against the raw baseline, the calibration of your intervals, and the quality of the top-10 and bottom-20 lists under your design. |
| **R6** | **Interval calibration.** Check the coverage of your intervals by school size, and either fix any miscalibration you find (for example, by modelling year-to-year variation) or document it with numbers. |
| **R7** | **Sensitivity.** Show how the award list changes under each estimator and under at least one alternative selection rule (for example the posterior probability of being in the top 10, or a lower credible bound). Explain what each rule rewards. |
| **R8** | **Commissioner's brief** (at most 600 words, in plain language): the recommended lists, why tiny perfect schools are not on the award list, what the intervals mean, and the fairness implications for any group of schools (for example small rural public schools) that the method treats systematically differently. |

### D.3 Engineering requirements (mandatory)

- **Modular and tested.** Estimators share one interface, so the comparison code doesn't care which estimator it runs. At least **12 member tests** in `tests/test_member_*.py`, including tests of the posterior update on a hand-computed case and of the marginal-likelihood fit on data simulated from known hyperparameters.
- **Reproducible.** One command reproduces every number and figure in the report.
- **Robust.** No failures on zero-pass or all-pass schools, schools with one year of data, or a school with no results. Fitting must not depend on row order.
- **Dependencies.** [`starter/requirements.txt`](starter/requirements.txt), plus at most one probabilistic programming library if you add a full-Bayes comparison. Set it up so that `pytest` passes without it.

### D.4 Ethics and privacy

The data are **synthetic**: there are no real schools, and the identifiers are sequence numbers. Real league tables affect funding, reputations and staff careers, and small-school results can identify individual candidates (a school with 3 candidates and a 0% rate tells the community what each of them scored). In the report: (a) recommend a minimum-cohort rule or another disclosure control for publishing school-level rates; (b) state who could be harmed by a shrinkage-based ranking, and how you would explain it to them.

### D.5 Optional enhancements (not required for full marks)

- A full-Bayes logit-normal model with LGA random effects, compared against your empirical Bayes estimator, including whether hyperparameter uncertainty changes the intervals.
- An explicit year-to-year variance component (school-year random effects).
- Ranking by expected rank or by the posterior probability of being in the top k, with a loss function you justify.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Files** | [`resources/data/schools.csv`](resources/data/schools.csv) (600 rows) and [`resources/data/results_2022_2024.csv`](resources/data/results_2022_2024.csv) (1,800 rows); about 52 KB together |
| **Provenance** | **Synthetic**, generated by CLBG from a documented hierarchical model with a fixed seed. The generator and the latent truth are held in the assessor kit, because they are the answer key for the hidden evaluation. No real schools, candidates or results are represented. |
| **Licence** | CC BY 4.0 (same as this repository's content) |
| **Integrity** | SHA-256 checksums are in `tests/test_contract.py`. Don't edit the files. |

| File | Columns |
|---|---|
| `schools.csv` | `school_id` (SCH-NNNN), `lga` (LGA-01 … LGA-16), `ownership` (public, private, mission), `location` (urban, rural) |
| `results_2022_2024.csv` | `school_id`, `year`, `candidates`, `credit_passes` (candidates with five credits including English and Mathematics) |

**Hidden evaluation (what the assessors measure).** Your contract functions are run on this state and on two re-generated states drawn from the same kind of process with different seeds. They are scored against the **latent long-run rates** and against a held-out 2025 year. You cannot see either, so your own evaluation design (R5) is how you find out whether you are ready.

**Known limitations (by design).** Three years per school. School characteristics are coarse. The data contain no information on why some schools are small.

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-05-probability-and-statistics/DS-T2-009-small-schools-big-swings
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract      # passes immediately
pytest                  # behavioural tests fail until you implement the contract
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `smallarea/` package (contract plus your estimators) | The estimators being compared |
| 2 | `tests/test_member_*.py` (≥ 12 tests) | Evidence that the estimators are correct, not just plausible |
| 3 | `study.ipynb` **or** `study.py` | Exploration, comparison, calibration and sensitivity (R3–R7), reproducible end to end |
| 4 | `outputs/estimates.csv`, `outputs/award_list.csv`, `outputs/intervention_list.csv` | The artefacts the ministry would use |
| 5 | `REPORT.md` (at most 3,000 words plus figures, tables and derivations) | Model, derivations, evaluation design, results with uncertainty, limitations, ethics |
| 6 | `COMMISSIONER_BRIEF.md` (≤ 600 words) | R8 |
| 7 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 8 | A 10–20 minute live defence | Justify and debug (see §K) |

---

## G. Acceptance Criteria

Criteria marked ⚙ are checked automatically with the public and hidden test suites; criteria marked ✍ are checked by the assessor.

1. ⚙ The public behavioural tests and your own tests pass from a clean environment.
2. ⚙ **Accuracy against the latent truth.** On the official state and two re-generated states, the mean squared error of `estimate` against the latent long-run rates is **at most 70% of the raw rate's**. *Justification:* on data generated like this, a well-specified small-area estimator reduces MSE by roughly 45–55% (assessor reference), so 30% leaves a wide margin. Estimators that ignore structure the data reveal do not reach it reliably.
3. ⚙ **No systematic stratum bias.** Within every ownership × location stratum, the mean error is below 0.045 in absolute value. *Justification:* this is about one third of the typical difference between strata, and about twice the reference's worst stratum (0.019); it fails estimators that pull a whole class of schools in one direction.
4. ⚙ **Calibration.** 90% intervals cover the latent rate for between 82% and 97% of schools. *Justification:* the Monte Carlo SE of coverage over 600 schools is about 0.012. The band allows for plug-in hyperparameters and modest year-to-year variation, while failing intervals that ignore shrinkage uncertainty (too narrow) or are uninformative (too wide).
5. ⚙ **Award list.** The mean latent rate of your top 10 exceeds that of the raw top 10 by at least 0.015. **Intervention list:** the mean latent rate of your bottom 20 is no higher than that of the raw bottom 20. *Justification:* the reference's award list gains 0.025–0.043 over raw across the three states, so 0.015 is a conservative floor. For the bottom list, exact overlap with the true bottom 20 is very noisy, so the criterion is the true rate of the schools you would actually help.
6. ⚙ **Held-out year.** Your estimates predict the 2025 rates with lower mean squared error than the raw rates do.
7. ⚙ **Robustness.** The results do not depend on row order, and the contract handles a school with no results.
8. ✍ The evaluation design (R5) is justified, does not leak future information, and corrects for the noise in held-out rates. The comparison reports uncertainty in the *difference* between estimators.
9. ✍ The derivations (R4) are correct: the beta-binomial marginal likelihood, the posterior, and shrinkage written as a weight on the raw rate that depends on n.
10. ✍ The calibration analysis (R6) reports coverage by school size and explains any shortfall.
11. ✍ The Commissioner's brief is accurate, plain and fair, and names the groups of schools that move most under shrinkage.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 15 |
| Implementation quality | 15 |
| Methodology: model choice and evaluation design | 20 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create a private repository** named `clbg-DS-T2-009-<your-github-username>` with your `smallarea/` package at the top level, plus `tests/`, `resources/` and `submission-template/`.
2. **Expected structure:**
   ```text
   clbg-DS-T2-009-<username>/
   ├── README.md                 # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── smallarea/                # contract in __init__.py + your modules
   ├── tests/                    # provided tests + test_member_*.py
   ├── resources/                # unchanged
   ├── study.ipynb | study.py
   ├── outputs/
   ├── figures/
   ├── REPORT.md
   ├── COMMISSIONER_BRIEF.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** The history is part of the evidence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue with the repository URL and commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Full Bayes.** Fit a logit-normal model with LGA and school effects in a probabilistic programming language, and compare its intervals with your empirical Bayes intervals for the smallest schools.
2. **Stein's paradox.** Show by simulation that James–Stein shrinkage on the arcsine-transformed rates dominates the raw rates in total squared error, and connect it to your estimator.
3. **Loss-based selection.** Define a loss for the award (for example, the grant wasted on a school outside the true top 30) and choose the list that minimises posterior expected loss.
4. **Value-added.** If you had candidates' junior-school results, how would the model and the policy question change?

---

## K. Assessment Integrity

**AI tools are permitted** for learning and code review. **They must not do the assessment for you:** you must be able to derive, justify and change your estimators live.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`. Disclosed, reasonable use is not penalised.
- **Cite** what you used, for example Efron's *Large-Scale Inference* (2010), chapter 1, Efron and Morris (1975) on Stein's estimator, or Gelman et al., *Bayesian Data Analysis*, chapter 5.
- **Collaboration:** you may discuss general ideas. You may not share code, numbers, lists or report text.
- **How your understanding is verified (10–20 minutes):**
  1. derive the posterior mean for one school as a weighted average of its raw rate and the prior mean, and say what the weight depends on;
  2. pick a school that moved a lot in your ranking and explain exactly why;
  3. an **unseen modification**, for example "the ministry adds a 2025 results file", "use only the latest year", or "the award must go to schools with at least 30 candidates", which you implement and interpret live;
  4. defend your evaluation design against the objection "next year's results are noisy, so your comparison proves nothing".

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Binomial and beta distributions, maximum likelihood, conjugate Bayes, pandas. |
| **New skill developed** | Borrowing strength across units, and evaluating estimators of quantities that are never observed. |
| **Decisions the member must make** | What to shrink towards; which covariates to use; how to evaluate against noisy held-out data; which selection rule the award and intervention should use; how to explain the trade-offs. |
| **What must be investigated independently** | Who the small schools are, and how that interacts with shrinkage; whether intervals are calibrated for large schools; how lists change across estimators and rules. |
| **Why it's interesting** | The data reveal a confounder, size against type, that makes the textbook grand-mean estimator biased in opposite directions for two groups of schools, and the "right" bottom-20 list depends on what the intervention is for. |
| **Evidence of competence** | Hidden-truth MSE and calibration on three states; derivations reproduced live; a coherent evaluation design; an honest brief. |
| **Misconceptions exposed** | "The top of a league table is the best schools." "Shrinkage is always towards the overall mean." "Held-out MSE differences directly measure estimator quality." "A Bayesian interval is automatically calibrated." "Ranking by posterior mean answers every selection question." |
| **Preparation for later work** | Hierarchical models and MCMC (DS-T3-007, DS-T3-008), multilevel regression in causal inference, recommender-system cold start, and small-area estimation in official statistics. |

**Suggested approach** (optional): explore first (R3), above all a funnel plot coloured by school type. Then implement the common-prior estimator and test it on simulated data with known hyperparameters. Build the evaluation harness *before* trying improvements, so that every change is measured.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
