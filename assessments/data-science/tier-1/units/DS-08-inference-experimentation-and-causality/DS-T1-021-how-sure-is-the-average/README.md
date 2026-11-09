# DS-T1-021: How Sure Is the Average? Confidence Intervals for Mobile-Money Cash-Outs

> *Build confidence intervals from first principles, then test whether they deserve the word 'confidence'.*

![Format: Implementation](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-021` |
| **Title** | How Sure Is the Average? Confidence Intervals for Mobile-Money Cash-Outs |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-08: Statistical Inference, Experimentation and Causal Thinking](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8–14 hours over 1 week |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | Python functions and numpy arrays; mean, standard deviation and the idea of sampling variation; pandas groupby; running `pytest` |
| **Skills developed** | Confidence interval construction; Reproducible bootstrap resampling; Coverage simulation; Sample size planning; Communicating uncertainty |
| **Technologies** | Python 3.10+, numpy, pandas, scipy, pytest |

---

## B. Problem Statement

Mobile-money agents in six Nigerian regions record every customer cash-out. The product team at a fictional fintech, **PaySabi**, has a spreadsheet of average cash-out values per region and wants to decide where to pre-position float (physical cash). The spreadsheet shows only means: "Lagos ₦4,630, Kano ₦3,010, Gombe ₦2,310." Nobody has said how much those numbers could move if the data were collected again.

Your job is to replace single numbers with **honest ranges**. You will build a small library, `interval_lab`, that computes confidence intervals two ways (the textbook t-interval and the percentile bootstrap), tests whether those intervals deserve their "95%" label by simulation, and produces the regional table PaySabi needs.

Cash-out values are **right-skewed**: most transactions are a few thousand naira, a few are very large. That is exactly the situation where textbook formulas quietly stop being accurate, and where small regions (Gombe has fewer than ten observations in the export) deserve to be treated differently from Lagos. Alongside the code you will write a one-page note for the product team: which regions can safely be compared, which cannot, and how many transactions they would need to collect to say more.

All data is **synthetic**. No real agent or customer is described.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Compute** a t-interval and a percentile-bootstrap interval for a mean and for a median, and say what each one assumes.
2. **Implement** resampling reproducibly, with a seed and a stated order of random draws.
3. **Test an interval procedure by simulation**, measuring its real coverage against its nominal 95%.
4. **Explain** why skewed data and small samples break the textbook interval, with your own simulation evidence.
5. **Compare two groups** with an interval for the difference, and avoid the "do the intervals overlap?" shortcut.
6. **Plan a sample size** from a target margin of error.
7. **Communicate uncertainty** to a non-statistician without false precision.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `interval_lab` package in [`starter/interval_lab/`](starter/interval_lab/). The signatures are fixed because the tests import them. All randomness uses `numpy.random.default_rng(seed)`, and the **order of draws is part of the specification** so that results are reproducible across solutions.

| ID | Requirement |
|---|---|
| **R1** | `t_interval(x, level=0.95) -> (lo, hi)`: the Student-t interval for the mean, `mean ± t(1-α/2, n-1) · s/√n` with `s` the sample standard deviation (`ddof=1`). Raise `ValueError` for fewer than 2 values or a level outside (0, 1). Return plain floats. |
| **R2** | `bootstrap_ci(x, stat=np.mean, level=0.95, n_boot=2000, seed=0) -> (lo, hi)`: percentile bootstrap. Draw **one index matrix** `rng.integers(0, n, size=(n_boot, n))` from `default_rng(seed)`, apply `stat` to each resample, and return the `α/2` and `1-α/2` quantiles (`np.quantile`, linear interpolation). Same `ValueError` rules as R1. |
| **R3** | `coverage(sampler, true_value, interval_fn, n, reps, seed) -> float`: create `rng = default_rng(seed)`, and for each of `reps` repetitions draw `sampler(rng, n)`, compute `interval_fn(sample)` and record whether `lo <= true_value <= hi`. Return the fraction covered. |
| **R4** | `summarise_regions(df, n_boot=2000, seed=0) -> DataFrame`, one row per region (alphabetical), columns exactly `region, n, mean, t_lo, t_hi, boot_lo, boot_hi, median, med_lo, med_hi, reliable`. The bootstrap columns use R2 (mean and median, same `seed`); `reliable` is `n >= 30`. |
| **R5** | `diff_means_ci_bootstrap(a, b, level=0.95, n_boot=2000, seed=0)`: percentile interval for `mean(a) - mean(b)`. From `default_rng(seed)`, draw the index matrix for `a` first, then for `b`, each `(n_boot, size)`. |
| **R6** | `required_n(sd, margin, level=0.95) -> int`: the smallest integer `n` with `z(1-α/2)·sd/√n <= margin` (normal approximation). Raise `ValueError` for non-positive inputs. |

### D.2 Engineering requirements

- Vectorise the resampling index draw (R2, R5). A Python loop over resamples for the *statistic* is acceptable.
- Never modify input arrays or the DataFrame.
- Write **at least 8 tests of your own** in `tests/test_member_*.py`, including two that would fail if the order of draws changed.
- `pytest` must finish in under 60 seconds.

### D.3 Analysis requirement

Using your library, run the simulation study described in the [report template](submission-template/REPORT.md): coverage of the t-interval and of the bootstrap for normal and lognormal samples at `n` = 10, 30 and 100 (at least 1,000 repetitions for the t-interval and 300 for the bootstrap). Put the script in `analysis.py` and quote its output.

### D.4 Privacy and responsibility

The data is synthetic. Treat the *habit* seriously: real agent-level transaction data is personal and commercially sensitive under the Nigeria Data Protection Act 2023. Report aggregates only, never individual agent IDs.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/agent_transactions.csv`](resources/data/agent_transactions.csv): about 370 rows × 4 columns (`txn_id, region, agent_id, amount_ngn`), about 8 KB |
| **Provenance** | **Synthetic**, generated with a fixed seed. Cash-out values are lognormal per region; agent IDs are fictional. |
| **Licence** | CC BY 4.0 (as this repository) |
| **Integrity** | SHA-256 checked by the contract test. Do not edit the file. |
| **Known limitation** | One seed gives one realisation. Your simulation study is what tells you about the *procedure*, not about this single table. |

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-08-inference-experimentation-and-causality/DS-T1-021-how-sure-is-the-average
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks data and scaffold
pytest                       # fails until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `interval_lab/` package | The core technical evidence |
| 2 | `tests/test_member_*.py` (≥ 8 tests) | Pins behaviour, including draw order |
| 3 | `analysis.py` and its output | The coverage study (D.3), reproducible |
| 4 | `outputs/regional_summary.csv` | The table PaySabi would use |
| 5 | `REPORT.md` from the [template](submission-template/REPORT.md) (≤ 700 words plus tables) | A note for the product team and your AI-use declaration |
| 6 | A 5-minute defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Assessors check the criteria marked ⚙ with the public and hidden test suites, and the rest by hand.

1. ⚙ All public tests and your own tests pass from a clean environment.
2. ⚙ R1–R6 behave exactly as specified, including draw order, verified on hidden tests with **regenerated data** and random arrays.
3. ⚙ Your t-interval agrees with `scipy.stats.t.interval` to 1e-9. *Justification:* both compute a closed-form quantity.
4. ⚙ The coverage of your t-interval for normal data at n = 25 lies in [0.935, 0.965] over 2,000 repetitions. *Justification:* Monte Carlo standard error is about 0.005, so a correct implementation falls inside with margin; a wrong degrees-of-freedom or `ddof` falls outside.
5. ⚙ The t-interval's coverage on lognormal samples (σ = 1.2, n = 8) is below 0.90, which a correct implementation reproduces (the reference gets about 0.78).
6. ✍ `analysis.py` regenerates every coverage figure quoted in the report.
7. ✍ The report states, for each region, whether a comparison is supportable, and never describes a 95% interval as "a 95% chance the true mean is inside" for a fixed computed interval.
8. ✍ The report gives the sample size PaySabi would need per region for a ±₦500 margin on the mean, using a justified `sd`.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Methodology of the simulation study | 20 |
| Testing | 10 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private GitHub repository** named `clbg-DS-T1-021-<your-github-username>` and copy in this assessment's `starter/interval_lab/`, `tests/`, `resources/` and `submission-template/`. Put `interval_lab/` at the repository root.
2. **Commit as you work.** Commit history is part of the evidence. A single "final" commit will be questioned at defence.
3. Include `REPORT.md` (from the [template](submission-template/REPORT.md)), which contains your AI-use declaration, and a short top-level `README.md` (at most 10 lines) saying how to run everything.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never replace the core requirements.

1. **Bias-corrected intervals.** Implement the bootstrap-t or BCa interval and show whether it repairs coverage at n = 10 for lognormal data.
2. **Trimmed means.** Compare the mean, median and 10% trimmed mean as summaries of cash-out value: which has the narrowest honest interval?
3. **Cluster the agents.** Transactions from one agent are not independent. Resample agents instead of transactions and report how the intervals change.
4. **Overlap myth.** Construct a pair of regions whose 95% intervals overlap but whose difference interval excludes zero, and explain why.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a statistical idea or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration inside `REPORT.md`: tool, purpose, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** code or methods adapted from documentation, papers or forums.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers or report text.
- **Defence (5 minutes).** The assessor picks one region from your table and asks you to explain each interval in plain language; asks what would change if transactions were clustered by agent; then gives an **unseen modification** such as switching to a 90% level or a trimmed mean, to be done live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Means, standard deviations, the idea of a sampling distribution, basic numpy. No prior bootstrap experience. |
| **New skill developed** | Treating an interval as a *procedure* with a measurable long-run property, and measuring that property. |
| **Decisions the member must make** | How to structure vectorised resampling, how to design the simulation study, and what to say about regions with tiny samples. |
| **What must be investigated independently** | Why the t-interval under-covers for skewed data at small n, and how much that matters in practice. |
| **Why it's interesting** | The 'reliable' regions and the tiny ones give a concrete, local reason to distrust a spreadsheet of means. |
| **Evidence of competence** | Exact agreement with specified draw order, simulated coverage in the expected bands, and a report that does not overclaim. |
| **Misconceptions exposed** | '95% interval means 95% probability for this interval.' 'Bootstrap fixes small samples.' 'Non-overlapping intervals are required for a difference.' |
| **Preparation for later work** | Leads to DS-T2 A/B-testing work with robust metrics, and to ML evaluation where confidence intervals on metrics are routine. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
