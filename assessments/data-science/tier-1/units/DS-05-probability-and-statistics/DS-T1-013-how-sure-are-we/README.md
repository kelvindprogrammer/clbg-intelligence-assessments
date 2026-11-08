# DS-T1-013: How Sure Are We?

> *A 213-agent survey, three numbers the regional manager wants, and a simulation experiment that shows which "95%" intervals actually deliver 95%.*

![Format: Comparative](https://img.shields.io/badge/format-comparative-e36209) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-013` |
| **Title** | How Sure Are We? Bootstrap and Analytical Intervals Under a Coverage Experiment |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-05: Probability and Statistics](../README.md) |
| **Format** | Comparative (secondary: Implementation) |
| **Difficulty** | Technical 2 · Mathematical 3 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 10–16 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU or paid services, and no internet after setup. The full coverage study runs in about 2 minutes |
| **Recommended prerequisites** | NumPy broadcasting and `numpy.random.Generator`; the sampling distribution of a mean; the central limit theorem at an introductory level; normal and t quantiles; running `pytest` |
| **Skills developed** | Confidence intervals (t, Wald, Wilson, Clopper–Pearson); nonparametric bootstrap (percentile, basic, BCa); jackknife; designing a Monte Carlo coverage experiment with its own error bars; choosing an interval for skewed and rare-event survey data |
| **Technologies** | Python 3.10+, NumPy, SciPy (`scipy.stats` distributions only, no `scipy.stats.bootstrap` in your package), pandas, matplotlib, pytest |

---

## B. Problem Statement

A Nigerian payments company runs a network of POS and mobile-money agents: the kiosks and shopfronts where people withdraw cash, pay bills and send money. Its research team surveyed **213 agents across six local government areas (LGAs)** in Kano, Lagos and Rivers states. For each agent they recorded the typical daily transaction value and whether the agent experienced a **fraud attempt** in the last 30 days (a fake transfer alert, a reversed transaction, or a cloned card).

The regional manager wants three numbers per LGA, each with "a 95% confidence interval":

1. the **mean** daily transaction value, to size cash-float credit lines;
2. the **median** daily transaction value, to describe the typical agent;
3. the **proportion** of agents reporting a fraud attempt, to prioritise anti-fraud training.

The analyst before you used `mean ± 1.96 × sd/√n` for everything, including the proportions, and reported "0% fraud, 95% CI [0%, 0%]" for two LGAs. The manager is now suspicious of all the intervals, and asks you directly: **how sure are we, really?**

You can answer that question in a way that does not depend on anyone's opinion. Every interval method makes a promise: "if you repeated the survey many times, 95% of my intervals would contain the true value." You can **test the promise by simulation**, by drawing thousands of synthetic surveys from a population whose true values you know and counting how often each method is right. That is a coverage experiment, and it is the core of this assessment.

What makes it hard:

- **Transaction values are heavily skewed.** A few agents near markets or motor parks handle many times the typical value. With 20–60 agents per LGA, the sampling distribution of the mean is far from normal. Intervals can fail, and when they fail it is almost always on the same side.
- **Fraud attempts are rare.** At a true rate of about 4% and 40 agents, you often see 0, 1 or 2 events. Some textbook intervals fall apart exactly there.
- **The bootstrap is not magic.** It is a powerful idea, but some versions inherit the very small-sample problems you might hope it solves. You have to measure which ones, not assume.
- **A coverage estimate is itself an estimate.** "Coverage 0.93" from 200 simulations and from 4,000 simulations are different claims. Your experiment needs error bars too.

**Fixed facts for the study** (you may not change them): the simulation population for daily value is lognormal with median ₦120,000 and log-scale standard deviation 1.1. The fraud-attempt indicator is Bernoulli with p = 0.04. All intervals are two-sided at the 95% level. These are defined as constants in [`starter/sure_ci/study.py`](starter/sure_ci/study.py).

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** the t, Wald, Wilson and Clopper–Pearson intervals, and **derive** the Wilson interval by inverting the score test.
2. **Implement** the nonparametric bootstrap from scratch, including percentile, basic and BCa intervals with a jackknife acceleration, and explain what each one corrects for.
3. **Design and run** a Monte Carlo coverage experiment, reporting coverage, its Monte Carlo standard error, mean width and *which side* the misses fall on.
4. **Compare** methods fairly across sample sizes and estimands, and state which method you would trust for which survey quantity, and why.
5. **Communicate** interval estimates to a non-specialist manager without overstating certainty.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `sure_ci` package in [`starter/sure_ci/`](starter/sure_ci/). Signatures, constants and output columns are fixed because the tests import them; internals are yours. The CLI in `__main__.py` is provided.

| ID | Requirement |
|---|---|
| **R1** | `t_interval(x, level)`: the Student-t interval for a mean. |
| **R2** | `wald_interval`, `wilson_interval` and `clopper_pearson_interval(k, n, level)` for a binomial proportion, clipped to [0, 1]. Wald must be the plain formula. Do not "fix" it, because its failure is part of what you are measuring. The report must include the **derivation of the Wilson interval** from the inequality \|p̂ − p\| ≤ z·√(p(1−p)/n), solved as a quadratic in p. |
| **R3** | `bootstrap_replicates(x, stat, B, rng)`, `percentile_interval` and `basic_interval`. The statistic is vectorised (`stat(arr, axis=-1)`), and all randomness comes from `rng`. `scipy.stats.bootstrap` may not be used in the package, though you may use it in your tests. |
| **R4** | `jackknife_values(x, stat)` and `bca_interval(...)`, following Efron (1987): the bias correction z₀ from the share of replicates strictly below the estimate, the acceleration from the jackknife, and the adjusted percentiles. A constant sample returns `(value, value)`; endpoints must be finite even when no replicate falls below the estimate. The report explains, in your own words, what z₀ and the acceleration each correct for. |
| **R5** | `coverage_experiment(sampler, true_value, method, n, reps, rng) -> CoverageResult`, reporting coverage, Monte Carlo SE √(ĉ(1−ĉ)/reps), mean width, `miss_below` (the interval lies entirely below the truth) and `miss_above`. |
| **R6** | `run_study(reps, B, seed, ns)` runs the full grid: estimands mean (t, percentile, basic, BCa), median (percentile, basic, BCa) and proportion (Wald, Wilson, Clopper–Pearson), at n ∈ {10, 20, 40, 160}, and returns `STUDY_COLUMNS`. It is reproducible from `seed`. For the official run use `reps = 1000`, `B = 1000`, `seed = 2026`. |
| **R7** | `analyse_survey(df, B, seed)` returns one row per LGA with `SURVEY_COLUMNS`: the mean with t and BCa intervals, the median with a BCa interval, and the fraud proportion with a Wilson interval. |
| **R8** | `python -m sure_ci resources/data/agent_survey.csv --out outputs/` writes `survey_intervals.csv` and `coverage_study.csv`. |
| **R9** | **Comparison report.** One figure per estimand showing coverage against n for every method, with ±2 Monte Carlo SE bars and a reference line at 0.95, and one figure of miss-below and miss-above shares. From these, give a **recommendation table**: for each survey quantity at the survey's sample sizes, which method you would report and why, citing your own numbers. |
| **R10** | **The manager's table.** Present the survey results for all six LGAs, using your recommended methods, with a short plain-language explanation of what the intervals mean and do not mean. Pay particular attention to the LGAs with zero fraud reports and the LGAs whose mean is dominated by a few agents. |

### D.2 Engineering requirements (mandatory)

- **Reproducibility.** Every number in the report comes from code in the repository with stated seeds. `run_study` with the official settings must regenerate `coverage_study.csv` exactly.
- **Tests.** Keep the provided tests passing and add **at least 10 tests of your own** in `tests/test_member_*.py`, including at least two hand-computed cases (for example a jackknife or Wilson interval worked on paper) and one test that would catch a bootstrap that resamples *without* replacement.
- **Vectorisation.** The bootstrap must not loop in Python over the B resamples. The official study must finish in under 5 minutes on a typical laptop.
- **Dependencies.** Only [`starter/requirements.txt`](starter/requirements.txt).

### D.3 Privacy and responsibility

The survey is **synthetic**: agent IDs are sequence numbers, and there are no names, phone numbers or locations finer than an LGA. Real agent surveys contain commercially sensitive revenue figures and fraud reports that could expose an agent to reputational harm. In one paragraph, state how you would publish LGA-level results from a real survey without making any individual agent identifiable. Consider small LGAs, extreme values and the zero-event cells. Refer to the Nigeria Data Protection Act 2023's principle of data minimisation.

### D.4 Optional enhancements (not required for full marks)

- Add the bootstrap-t (studentised) interval and see whether it fixes the mean's one-sided failure.
- Add the Agresti–Coull interval and the Jeffreys interval, and compare them with Wilson.
- Plot the *actual* coverage of the Wald interval as a function of p at n = 40. It oscillates, and explaining why is a good exercise.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/agent_survey.csv`](resources/data/agent_survey.csv): 213 rows × 5 columns, about 7 KB |
| **Provenance** | **Synthetic**, generated by [`resources/generate_survey.py`](resources/generate_survey.py) with `--seed 2026`. Values are lognormal by LGA; fraud attempts are Bernoulli. The agents are fictional. |
| **Licence** | CC BY 4.0 (same as this repository's content) |
| **Integrity** | SHA-256 `fc1b2a2c10f9923f6f3890e1ecc24bc786b5ecf9eb0204bcc4ab7087c8736d83`. The contract test checks it and checks that the generator reproduces it byte for byte. |

| Column | Meaning |
|---|---|
| `agent_id` | `AG-NNNN`, a sequence number |
| `lga` | One of six LGAs |
| `daily_value_ngn` | Typical daily transaction value in naira, rounded to ₦100 |
| `fraud_attempt_30d` | 1 if the agent reported a fraud attempt in the last 30 days, else 0 |
| `months_operating` | Months since the agent started (context only; not needed for the requirements) |

**Known limitations (by design).** LGA samples are small (18–60). The survey design is treated as a simple random sample within each LGA, which a real survey rarely is. The population used in the coverage study is chosen to resemble the survey, but it is not identical to any one LGA. Part of your critical-thinking mark is saying what that implies.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-05-probability-and-statistics/DS-T1-013-how-sure-are-we
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract     # passes immediately
pytest                 # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `sure_ci/` package | The interval methods and the experiment harness: the core technical evidence |
| 2 | `tests/test_member_*.py` (≥ 10 tests) | Shows you can verify statistical code against hand calculations |
| 3 | `outputs/coverage_study.csv`, `outputs/survey_intervals.csv` | The evidence and the deliverable for the manager |
| 4 | `figures/` | Coverage and miss-side figures (R9) |
| 5 | `REPORT.md` (at most 1,800 words plus tables, figures and derivations) | The Wilson derivation, the BCa explanation, the comparison and recommendation (R9), the manager's table (R10), limitations |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 7 | A 5–10 minute live defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

Criteria marked ⚙ are checked automatically with the public and hidden test suites; criteria marked ✍ are checked by the assessor.

1. ⚙ `pytest` passes all public tests and your own tests from a clean environment.
2. ⚙ The t, Wilson and Clopper–Pearson intervals match `scipy.stats` to 1e-10 at several levels, including k = 0 and k = n. *Justification:* these are closed-form or exact computations, so only floating-point tolerance applies.
3. ⚙ The percentile and BCa intervals agree with `scipy.stats.bootstrap` (20,000 resamples, different random stream) to within 4% (percentile) and 8% (BCa) of the interval width, on smooth statistics. *Justification:* with 20,000 resamples, the Monte Carlo noise in a 2.5% quantile of the replicate distribution is about 1–3% of the interval width (checked on the reference). BCa's adjusted percentiles sit further into the tails, so they get a wider band. A wrong z₀ sign or a missing acceleration moves the endpoints by much more than this.
4. ⚙ Your coverage harness reproduces the t-interval's coverage on exponential data at n = 10 (0.899 from 40,000 reference replications) within four combined standard errors, and shows that misses fall overwhelmingly below the truth. *Justification:* four standard errors gives a false-failure rate below 1 in 10,000 for a correct harness, while an off-by-one in the miss accounting or a coverage formula that counts endpoints wrongly fails it.
5. ⚙ On the official grid at n = 40, Wald's coverage for p = 0.04 is below 0.88 and Wilson's is above 0.92. For the lognormal mean, the t-interval's coverage is below 0.93, with misses below more than four times as common as misses above. *Justification:* the reference values are 0.80, 0.98, 0.89 and a ratio of about 35, so every bar holds with a wide margin at the test's 400 replications, and any correct implementation will meet it.
6. ⚙ `run_study` is reproducible from its seed, and the bootstrap is vectorised (the official study finishes within 5 minutes).
7. ✍ The report derives the Wilson interval correctly and explains z₀ and the acceleration without reciting a formula.
8. ✍ The comparison (R9) shows Monte Carlo error bars, and its conclusions do not claim differences smaller than about 2 MC SE.
9. ✍ The recommendation table names a method for each quantity at the survey's sample sizes and justifies it **with your own coverage numbers**, including the direction of the misses.
10. ✍ The manager's table (R10) never reports a zero-width interval for a zero-event LGA, and explains in plain language why a skewed mean's interval is less trustworthy than its nominal 95%.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Methodology: experiment design and comparison | 20 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create a private repository** named `clbg-DS-T1-013-<your-github-username>` with this assessment's `starter/` contents at the top level, plus `tests/`, `resources/` and `submission-template/`.
2. **Expected structure:**
   ```text
   clbg-DS-T1-013-<username>/
   ├── README.md                 # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── sure_ci/
   ├── tests/                    # provided tests + test_member_*.py
   ├── resources/                # unchanged
   ├── outputs/coverage_study.csv
   ├── outputs/survey_intervals.csv
   ├── figures/
   ├── REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** The history is part of the evidence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue with the repository URL and commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Bootstrap-t.** Implement the studentised bootstrap for the mean and check whether it repairs the one-sided failure at n = 20. What does it cost in width?
2. **How many reps?** Work out how many coverage replications you would need to tell a method with true coverage 0.93 from one with 0.95, with 90% power. Then check your answer by simulation.
3. **Log scale.** Build an interval for the lognormal mean from a t-interval on the log scale (Cox's method). Compare it with BCa, and explain the assumption it adds.
4. **Survey weights.** Suppose Ikeja agents were sampled at twice the rate of other LGAs. How would you build a state-level mean and its bootstrap interval?

---

## K. Assessment Integrity

**AI tools are permitted** for learning, for example to explain the jackknife, check your algebra or review code. **They must not do the assessment for you.** You must be able to explain and modify everything you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`. Disclosed, reasonable use is not penalised.
- **Cite** sources for the BCa formulas (for example Efron and Tibshirani, *An Introduction to the Bootstrap*, 1993, chapter 14) and any adapted code.
- **Collaboration:** you may discuss general ideas with other members. You may not share code, coverage numbers or report text.
- **How your understanding is verified.** In the defence the assessor will:
  1. ask you to compute a Wilson interval for k = 0, n = 20 on paper (or with a calculator) and explain why its upper limit is not zero;
  2. ask why the t-interval for a skewed mean misses mostly on one side, and which side;
  3. give you an **unseen modification**, such as adding a new estimand (the 90th percentile) to the study, or a new method, and ask you to run it live and interpret the result;
  4. ask how many replications your study used and what the Monte Carlo error of one coverage cell is.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Sampling distributions, the CLT, quantiles of the normal and t distributions, vectorised NumPy. |
| **New skill developed** | Testing a statistical method's promise empirically, by treating "95% confidence" as a falsifiable claim with its own Monte Carlo error. |
| **Decisions the member must make** | How many replications are enough, how to present coverage with error bars, which method to recommend for each quantity, and how to say "we don't know" to a manager honestly. |
| **What must be investigated independently** | Which methods fail, where and on which side, and whether the bootstrap's reputation is earned at n = 20. |
| **Why it's interesting** | The answer depends on the regime. The bootstrap works well for the median but disappoints for a skewed mean at small n; Wald is fine at n = 160 but useless at n = 10 with a rare event. The manager's suspicion turns out to be justified, and quantifiable. |
| **Evidence of competence** | Exact agreement with `scipy` on closed forms; agreement within Monte Carlo error on bootstrap endpoints; reproducible coverage tables; a defensible recommendation table; live computation at defence. |
| **Misconceptions exposed** | "A 95% interval contains the truth 95% of the time, whatever the data." "The bootstrap fixes small samples." "0 events means a rate of 0." "Coverage 0.93 versus 0.94 is a real difference." "Interval failures are symmetric." |
| **Preparation for later work** | DS-T2 shrinkage and small-area estimation, DS-08 A/B testing and power, simulation-based calibration in DS-T3-008, and evaluating ML metrics with bootstrap intervals. |

**Suggested approach** (optional):

1. Implement and test R1–R2 against `scipy.stats` first. Derive Wilson on paper.
2. Write `bootstrap_replicates` with an index matrix, then test it on a tiny sample where you can enumerate all resamples.
3. Build the coverage harness and check it on normal data with the t-interval, which should give 0.95 ± MC error, *before* running the full grid.
4. Run the grid, plot it, and only then write the recommendation.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
