# ML-T3-003: Do Ensembles Cure Overfitting? A Bias-Variance Replication Study with Bagging and Boosting

> *A cocoa-yield modelling team repeats three slogans about ensembles. Build a decomposition instrument you can trust, then find out when each slogan holds, and when it does not.*

![Format: Replication (secondary: Open-ended research)](https://img.shields.io/badge/format-replication-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-003` |
| **Title** | Do Ensembles Cure Overfitting? A Bias-Variance Replication Study with Bagging and Boosting |
| **Subtrack** | ML Engineering |
| **Tier** | 3: Advanced and Research-Grade |
| **Unit** | [ML-02: Supervised Learning and Ensembles](../README.md) |
| **Format** | Replication (secondary: Open-ended research) |
| **Difficulty** | Technical 4 · Mathematical 4 · Research 4 · Engineering 3 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 24–36 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Decision trees, bagging and gradient boosting as used in scikit-learn; expected value and variance; the squared-error decomposition; Monte Carlo estimation and bootstrap standard errors. Recommended: ML-T1-004 and ML-T2-003 |
| **Skills developed** | Building and validating a Monte Carlo bias-variance instrument; designing factorial ablations; correcting estimator bias; attaching uncertainty to every comparison; separating what depends on noise, sample size and irrelevant features; stating the scope of an empirical claim |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

The Cocoa Research Programme of a (fictional) southwestern Nigerian state wants to model plot yield from rainfall, temperature, a soil index and shade cover. Its analysts keep repeating three slogans:

1. "Bagging cures overfitting."
2. "Boosting always beats bagging, because it keeps reducing error."
3. "More trees can never hurt."

Each slogan is partly true, and the programme will spend money on data collection based on them: if variance is the problem, more plots help; if bias is the problem, better features help. Your task is to **replicate the classical bias-variance analysis** (Breiman 1996 for bagging; the squared-loss decomposition for boosting) in a controlled setting where the true yield function and the noise level are known, and to determine under which conditions each slogan holds.

Because the truth is known, you can measure the three terms of the expected squared error directly: squared bias, variance, and irreducible noise. The tool you build, `bvlab`, trains each model on many independent training sets, averages predictions, and separates the components. The instrument must be *right* before it is used: a naive implementation overstates the bias by the variance divided by the number of rounds, and it will give wrong conclusions if you do not notice. You will validate it with models whose bias and variance you know exactly.

Then you will use it. The questions are deliberately open: which hyper-parameters, which grid, how many rounds, and how big a difference counts as real are your decisions, and the standard of evidence is the point. You will pre-state the claims, run factorial ablations (tree depth, number of estimators, learning rate, training-set size, noise level, number of irrelevant features), attach uncertainty to every number, and write a verdict on each slogan with its scope.

> **Why this matters beyond this task.** Practitioners choose between collecting more data, improving features, and changing models on the basis of folklore. The bias-variance decomposition is the clearest way to ask which of those will help, and the habits of validating the instrument and quantifying noise carry into every empirical ML study.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Estimate** bias, variance and noise by repeated resampling with a known truth, and verify the decomposition identity.
2. **Correct** the finite-round bias of the squared-bias estimate and show, with a known-answer model, that the correction is needed.
3. **Attach** bootstrap standard errors to each term and use them to decide which differences are real.
4. **Design** factorial ablations over depth, ensemble size, learning rate, sample size, noise and irrelevant features.
5. **Test** three folk claims about ensembles as falsifiable statements about the decomposition, with a verdict on each.
6. **State** the scope of the evidence: one truth function, squared loss and specific hyper-parameters, and what would change the conclusion.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `bvlab` in [`starter/bvlab/`](starter/bvlab/). The generator `datagen.sample(n, seed, n_irrelevant=0, noise_sd=0.5)` returns noisy training data and `datagen.f_true(X)` returns the noiseless truth.

| ID | Requirement |
|---|---|
| **R1** | `bias_variance(make_model, n_train=300, rounds=40, seed=0, noise_sd=0.5, n_irrelevant=0, n_eval=1000, n_boot=40) -> dict`. `make_model()` returns a fresh unfitted object with `fit(X, y)` and `predict(X)`. For each round `r`, train on a fresh independent sample `datagen.sample(n_train, seed*1000 + r, ...)`. Evaluate on a fixed set `datagen.sample(n_eval, 10**6 + seed, ...)` whose noiseless values are `f_true`. Return keys `bias2, variance, noise, mse, se_bias2, se_variance, se_mse`. |
| **R2** | `variance` is the mean over evaluation points of the **unbiased** (`ddof=1`) variance of predictions across rounds. `bias2` is the mean squared difference between the round-averaged prediction and `f_true`, **minus the finite-round correction** `variance / rounds`. `noise = noise_sd²`. `mse` is the mean squared error of the round predictions against the noisy evaluation targets. |
| **R3** | Standard errors come from a bootstrap over **rounds** (resample the rows of the prediction matrix with replacement, `n_boot` times, using a generator seeded from `seed`), returning the standard deviation of each recomputed term. |
| **R4** | `grid_study(specs, **kwargs) -> list[dict]`, where `specs` is a list of `(label, make_model, overrides)`; each result merges `label`, the `overrides` and the R1 output. `overrides` can change `n_train`, `noise_sd` or `n_irrelevant` for that spec. |

### D.2 Engineering requirements (mandatory)

- `PLAN.md` first: the three claims as falsifiable statements about the decomposition, the grid, the number of rounds, the decision rule for a "real" difference, committed before the experiments.
- Deterministic and seeded; no global random state.
- At least **12 tests of your own** in `tests/test_member_*.py`, including a constant-prediction model (zero variance), a model that outputs the truth plus independent noise (zero bias, known variance), and the identity `mse ≈ bias2 + variance + noise`.
- `experiments.py` regenerates all tables and figures in under 15 minutes. Report standard errors with every term.
- Use at least `rounds=40` in the final study, and justify that number by showing how the standard errors depend on it.

### D.3 Responsibility

The data is synthetic. In the report, write one paragraph on how a wrong "more trees can never hurt" conclusion could lead a programme to spend on data collection that does not address the real error source, and what you would require before recommending a spending decision.

### D.4 Optional enhancements

- Replace the truth function with a different one and test whether your verdicts transfer.
- Add random forests (feature subsampling) and explain where they sit between bagging and boosting.
- Estimate the bias-variance trade-off for out-of-bag error and compare.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `sample(n, seed, n_irrelevant, noise_sd)` and `f_true(X)`; four informative features in [0,1] (rainfall, temperature, soil index, shade) plus optional irrelevant ones |
| **Truth** | `f(x) = 4 sin(2.5 x0) + 3 [x1 > 0.5] x2 + 16 (x3 − 0.5)²`: smooth, with an interaction and a threshold |
| **Provenance** | **Synthetic**, deterministic given the seed; no real plots or farmers |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing is committed; the generator writes a CSV of about 100 KB with `--out DIR --seed 1` |
| **Reference behaviour** | With 300 training rows and 40 rounds the reference gives, for a depth-1 tree, bias² 2.4 and variance 0.17; for a fully grown tree, bias² 0.13 and variance 0.87; for 50 bagged trees, 0.20 and 0.18; for 200 boosted depth-3 stages at rate 0.1, 0.05 and 0.16 |

Hidden tests use other seeds, other noise levels and other sample sizes.

**Setup**

```bash
cd assessments/ml-engineering/tier-3/units/ML-02-supervised-learning-and-ensembles/ML-T3-003-do-ensembles-cure-overfitting
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `PLAN.md`, committed before the experiments | Claims, grid, rounds and the decision rule |
| 2 | `bvlab/` package | The validated instrument and grid runner |
| 3 | `tests/test_member_*.py` (at least 12 tests) | Known-answer validation of the instrument |
| 4 | `experiments.py` and outputs (`results/*.csv`, figures) | Reproducible evidence with standard errors |
| 5 | `REPORT.md` (at most 2,500 words plus figures), from the [template](submission-template/REPORT.md) | Technical note with verdicts, scope and the AI-use declaration |
| 6 | An 8-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ **Instrument validity.** A constant-prediction model gives `variance < 1e-12` and `bias2` equal to its direct value; a model returning the truth plus independent unit-variance noise gives `variance` within 0.05 of 1 and `|bias2| < 0.01` at 40 rounds (the uncorrected estimate would be about 0.025). *Justification:* the correction removes exactly `variance / rounds`.
3. ⚙ **Identity.** For a fully grown tree, `mse` and `bias2 + variance + noise` agree within 5% of `mse`.
4. ⚙ **Standard errors.** All `se_*` are positive and finite; the `se_variance` at 160 rounds is below 0.75 of that at 40 rounds. *Justification:* bootstrap standard errors shrink as `1/√rounds`, giving a ratio near 0.5.
5. ⚙ **Determinism.** Two calls with the same arguments return the same dictionary (to relative tolerance `1e-9`).
6. ⚙ **Known laws reproduced.** Using your instrument with scikit-learn models at 300 training rows: a depth-1 tree has `bias2` above 3 times its `variance`; a fully grown tree has `variance` above 4 times its `bias2`; 50 bagged fully grown trees have less than half the variance of one and a `bias2` within 0.2 of it; and boosting from 10 to 100 stages lowers `bias2` while raising `variance`. *Justification:* these are the textbook effects and the reference shows all of them with margins of at least a factor of 1.5 over these thresholds.
7. ⚙ The same bars hold on hidden re-seeded settings (other seeds, noise 0.3 to 1.0, 200 to 600 rows).
8. ✍ `PLAN.md` predates the experiments and states a decision rule for a real difference.
9. ✍ The report gives a verdict on each slogan, supported by ablations and standard errors, states conditions under which it fails (for example boosting versus bagging at high noise), and states the scope of the evidence.
10. ✍ The report explains the finite-round correction and shows its effect on one number.

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

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T3-003-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `bvlab/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Transfer.** Swap in a second truth function and report which verdicts survive.
2. **Random forests.** Add feature subsampling and place it on the bias-variance map.
3. **Early stopping.** Show how validation-based early stopping changes the boosting trade-off.
4. **Irreducible-noise estimate.** Estimate the noise level from data alone (no known truth) and compare with the true value.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In an 8-minute defence the assessor will (1) ask why the raw squared-bias estimate is biased upward and by how much for your number of rounds; (2) pick one cell of your ablation table and ask whether its difference from its neighbour exceeds the standard error; (3) give an unseen modification, for example a different truth function or a different base learner, and ask you to predict the direction of change in variance before running it.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Fitting tree, bagging and boosting regressors; expected value and variance; the idea of a bootstrap. |
| **New skill developed** | Building an instrument, validating it against cases with a known answer, and then using it to test claims with calibrated uncertainty. |
| **Decisions the member must make** | Grid and number of rounds; how to decide that a difference is real; what to ablate; how to scope the verdicts. |
| **What must be investigated independently** | Whether boosting still beats bagging as noise rises, and whether irrelevant features affect bagging and boosting differently; the brief does not say. |
| **Why it is interesting** | The folklore is half right, and the interesting part is exactly where it fails. |
| **Evidence of competence** | An instrument that passes known-answer tests, ablation tables with standard errors, and verdicts that match the data and respect its limits. |
| **Misconceptions exposed** | 'Bagging fixes everything.' 'Boosting never overfits.' 'Squared bias estimated from a finite number of models is unbiased.' 'A difference in the third decimal is a finding.' |
| **Preparation for later work** | Leads into ML-06 evaluation methodology and ML-10 monitoring, and into research-style work across the ML track. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
