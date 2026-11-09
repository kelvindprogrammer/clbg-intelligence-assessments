# ML-T3-001: Does Adam Excuse Unscaled Features? An Experimental Study of Conditioning, Momentum and Second-Order Steps

> *A credit-scoring team says an adaptive optimiser makes feature scaling unnecessary. Design the experiments that decide the claim, and say exactly what they show and do not show.*

![Format: Open-ended research (secondary: Investigation)](https://img.shields.io/badge/format-open--ended%20research-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-001` |
| **Title** | Does Adam Excuse Unscaled Features? An Experimental Study of Conditioning, Momentum and Second-Order Steps |
| **Subtrack** | ML Engineering |
| **Tier** | 3: Advanced and Research-Grade |
| **Unit** | [ML-01: Mathematical and Computational Foundations](../README.md) |
| **Format** | Open-ended research (secondary: Investigation) |
| **Difficulty** | Technical 4 · Mathematical 4 · Research 4 · Engineering 3 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 24–36 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Gradient descent and its step size; the Hessian and what its eigenvalues mean; condition number; logistic regression; basic bootstrap; experiment design and reporting uncertainty. Recommended: ML-T1-001 |
| **Skills developed** | Posing a testable version of a vague claim; designing controlled optimiser experiments; handling right-censored runs; estimating scaling exponents with uncertainty; separating sources of ill-conditioning; defending validity and generality limits |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Mushin Microfinance Bank (fictional) is rebuilding the logistic-regression scorecard that ranks small-business loan applicants. The model uses raw features straight from the core-banking export: loan amount in naira (about 10⁶), tenure in months, number of mobile-money transactions (about 10³), a ratio between 0 and 1, and so on. During review a senior engineer wrote:

> "We train with Adam now. Adaptive optimisers handle badly scaled features by design, so the standardisation step in the old pipeline is dead weight. It also trains faster than plain gradient descent. Remove it."

Another engineer replied that standardisation "is not only about speed", and a third pointed out that Newton's method does not care about scaling at all. Nobody has measured anything. The risk manager would like to know whether removing the step is safe, in particular whether the model will train to the same answer within the nightly batch window, and how this changes as new, differently scaled features are added.

You have been asked for a technical note that settles what can be settled. The claim as stated is not precise enough to test. **Part of the task is making it testable**: what does "handle", "faster" and "need" mean? Faster in iterations, in passes over the data, in wall-clock time? Faster to what accuracy? For which sources of bad conditioning: columns on different scales, or columns that are correlated?

You will build a small optimisation laboratory, `optlab`, with five optimisers on logistic loss: plain gradient descent (optionally with a diagonal column-scale preconditioner), Nesterov-accelerated gradient descent with restart, damped Newton with backtracking, and Adam. You will pre-register a plan, run controlled experiments on synthetic problems whose condition number you control and whose source of ill-conditioning you can switch between *scale* and *correlation*, and write the note.

Two known results anchor the study, and your experiments should reproduce them: on a well-behaved smooth, strongly convex problem the iteration count of gradient descent grows roughly linearly with the condition number κ, and that of accelerated descent roughly with √κ. Whether Adam fits either pattern is for you to find out. The data is synthetic and the problems are small, so you must also argue what the results do and do not tell the bank.

> **Why this matters beyond this task.** Engineering folklore about optimisers is often stated without a cost model, a regime, or an interval. The habit of converting a slogan into a controlled experiment, and reporting a verdict with its scope, is the core research skill of ML engineering.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Operationalise** a vague engineering claim into hypotheses, metrics, a cost model and falsification criteria, written before any experiment.
2. **Implement** gradient descent, Nesterov with restart, damped Newton, a diagonal preconditioner and Adam correctly for logistic loss, and verify each against a reference optimum.
3. **Reproduce** known scaling laws (iterations versus condition number) with an exponent estimate and a bootstrap interval.
4. **Separate** ill-conditioning caused by feature scale from ill-conditioning caused by correlation, and show which interventions fix which.
5. **Handle censored runs** (those that did not converge within the budget) without biasing the comparison.
6. **Define fair cost** across first-order and second-order methods and show how the ranking depends on that definition.
7. **Argue validity**: what the synthetic study can and cannot say, and what additional evidence would change the verdict.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `optlab` in [`starter/optlab/`](starter/optlab/). The interfaces are fixed; the design of the study is yours. Logistic loss is the mean binary cross-entropy `f(w) = mean(softplus(z) − y z)` with `z = Xw`, plus `l2/2 · ‖w‖²`. Evaluate it stably (see ML-T1-001). Let `f*` be the optimal value.

| ID | Requirement |
|---|---|
| **R1** | `loss_grad(w, X, y, l2=0.0) -> (f, g)` and `hessian(w, X, y, l2=0.0)`, stable for large `|z|`. |
| **R2** | `solve_reference(X, y, l2=0.0) -> (w_star, f_star)`: damped Newton with backtracking, to gradient norm below `1e-12`. This is the ground truth for every convergence test. |
| **R3** | `gradient_descent(X, y, f_star, l2=0.0, precond=None, target=1e-6, max_iter=100000) -> Trace`. Step size is `1/L` with `L = 0.25 · λmax(XᵀX/n) + l2`. With `precond="diag"`, columns are divided by their root-mean-square before optimising and the returned `w` is in original coordinates. Stops when `f − f* ≤ target`. |
| **R4** | `nesterov(...)` with the same signature: accelerated descent with momentum `(k−1)/(k+2)` and **function-value restart**. |
| **R5** | `newton(X, y, f_star, l2=0.0, target=1e-6, max_iter=100) -> Trace`: damped Newton with backtracking line search. |
| **R6** | `adam(X, y, f_star, lr=0.01, l2=0.0, target=1e-6, max_iter=20000, beta1=0.9, beta2=0.999, eps=1e-8) -> Trace`. |
| **R7** | `Trace` (provided dataclass) carries `w, f, iters, evals, converged`. `evals` is the **cost in data passes**: one per `loss_grad` call, and `d` per `hessian` call (the Hessian costs about `d` gradient evaluations to form). A run that hits `max_iter` has `converged=False` and `iters == max_iter`. |
| **R8** | `run_study(kappas, methods, seeds, kind="scale", n=1500, d=8, max_iter=None, l2=0.0) -> list[dict]` returns one record per (method, κ, seed) with keys `method, kappa, seed, kind, iters, evals, converged`. `methods` are names from `{"gd", "gd_diag", "nesterov", "nesterov_diag", "newton", "adam"}`. Records are deterministic. Problems come from `datagen.make_logistic`. |
| **R9** | `loglog_slope(x, y, n_boot=500, seed=0) -> (slope, lo, hi)`: least-squares slope of `log y` on `log x` with a 95% percentile bootstrap interval resampling the (x, y) pairs. |

### D.2 Engineering requirements (mandatory)

- **`PLAN.md` first.** Commit it before running any experiment (the commit history is checked). It states hypotheses, metrics, the cost model, the grid, the number of seeds, and what result would falsify each hypothesis.
- No global random state. All randomness flows from explicit seeds.
- Provide **at least 12 tests of your own** in `tests/test_member_*.py`, including known-answer tests for every optimiser.
- `experiments.py` regenerates all tables and figures in under **10 minutes** on a laptop CPU.
- The Adam learning rate used in the study must be justified by a small, reported tuning protocol, not chosen once and forgotten.

### D.3 Responsibility

This is a synthetic study with no personal data. Credit scoring affects people's access to finance: in the report, add one paragraph on why training instability can silently change who gets a loan (for example two runs with different early-stopping behaviour producing different rankings of applicants), and what you would monitor.

### D.4 Optional enhancements

- Add a cheap quasi-Newton method (BFGS or L-BFGS from scratch) to the comparison.
- Study the effect of `l2 > 0` on the scaling exponents and explain it.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_logistic(n, d, kappa, seed, kind)` returns `X, y` |
| **Provenance** | **Synthetic**, deterministic given the seed. Columns are Gaussian with geometrically spaced scales from 1 to √κ; `kind="rotated"` multiplies by a random orthogonal matrix, which keeps κ but spreads it across correlated columns. Labels are drawn from a logistic model, so the problem is not separable and has a finite optimum |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing is committed. `python resources/datagen.py --out DIR --kappa 100 --seed 1` writes a CSV of about 200 KB |
| **Reference behaviour** | On the official settings (n = 1500, d = 8, target 1e-6) the reference gives log-log slopes of about 0.93 for GD and 0.54 for Nesterov on `kind="scale"`, and about 0 for any method with the diagonal preconditioner on `scale` but about 1 on `rotated` |

The Hessian condition number of these problems is close to, but not exactly, `kappa` (the logistic weights shrink some directions). The slopes are what matter.

**Setup**

```bash
cd assessments/ml-engineering/tier-3/units/ML-01-mathematical-and-computational-foundations/ML-T3-001-does-adam-excuse-unscaled-features
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `PLAN.md`, committed before any experiment | Pre-registration of hypotheses, metrics, cost model and falsification criteria |
| 2 | `optlab/` package | The optimisers and study harness: the technical evidence |
| 3 | `tests/test_member_*.py` (at least 12 tests) | Known-answer tests for every optimiser and the exponent estimator |
| 4 | `experiments.py` and its outputs (`results/*.csv`, figures) | Reproducible evidence |
| 5 | `REPORT.md` (at most 2,500 words plus figures), from the [template](submission-template/REPORT.md) | Technical note with verdict, scope and the AI-use declaration |
| 6 | An 8-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ Gradient, Hessian and reference optimum are correct: the gradient matches finite differences to `1e-6`, the Hessian matches finite differences of the gradient to `1e-5`, and `solve_reference` agrees with scikit-learn's unpenalised logistic regression to `1e-7` in `f*`.
3. ⚙ **Known rates reproduced.** On `kind="scale"` with κ in {4, 16, 64, 256} (2 or more seeds), the GD slope lies in **[0.8, 1.1]**, the Nesterov slope in **[0.4, 0.7]**, `gd_diag` has slope below **0.15**, and `newton` converges in at most 15 iterations at every κ. *Justification:* theory predicts exponents 1, 1/2 and 0; the windows are ±0.2 wide to allow for the logistic Hessian varying along the path. The reference measures 0.93, 0.54, 0.00 and 7 iterations.
4. ⚙ **Source of conditioning.** On `kind="rotated"` the `gd_diag` slope is above **0.6** (the reference measures 0.73, against 0.00 on `scale`), showing a diagonal preconditioner cannot remove correlation-induced ill-conditioning.
5. ⚙ **Censoring.** `run_study` with a small `max_iter` marks non-converged runs `converged=False` with `iters == max_iter`; `loglog_slope` recovers a known exponent (0.5 ± 0.05) from noiseless synthetic data and its interval covers the truth in at least 85% of noisy simulations.
6. ⚙ The same bars hold on hidden re-seeded problems with a different `d` and `n`.
7. ✍ `PLAN.md` predates the experiments (history check) and each hypothesis names its falsifier.
8. ✍ The report gives a verdict on each part of the team's claim ("handles scale", "faster", "no need to scale"), supported by intervals and with the cost model stated, and discusses where the claim is not testable by this study.
9. ✍ Adam's behaviour is reported honestly, including censored runs and the sensitivity to its learning rate.

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

1. **Create your own private repository** named `clbg-ML-T3-001-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `optlab/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Third cause.** Add a source of ill-conditioning from nearly separable classes (very small label noise) and explain what happens to the exponents.
2. **Wall-clock versus passes.** Time the methods and explain where the cost model and the stopwatch disagree.
3. **Stochastic version.** Repeat with mini-batch gradients and a decaying learning rate; what part of the picture survives?
4. **Transfer test.** State a prediction for a different loss (squared error) before running it, then check.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 8-minute defence the assessor will (1) ask what result would have made you accept the team's claim and where that threshold came from; (2) pick one point in your plot and ask how many of its runs were censored and what you did about it; (3) give an unseen modification, for example a different step rule for Adam or a third source of ill-conditioning, and ask you to predict the outcome before running it.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Gradient descent, Hessians, condition number, logistic regression and a bootstrap. No convergence proofs are needed, though the expected rates are given. |
| **New skill developed** | Converting an engineering slogan into a pre-registered, controlled, uncertainty-aware experiment, and writing a verdict whose scope matches its evidence. |
| **Decisions the member must make** | What 'faster' means; the cost model; the grid and number of seeds; Adam's learning-rate protocol; how to treat censored runs; which ablations to run; how far to generalise. |
| **What must be investigated independently** | Whether diagonal scaling and Adam's per-coordinate adaptation fix scale and correlation equally; the brief deliberately does not say. |
| **Why it is interesting** | The slogan is partly right and partly wrong, and the way it fails depends on the cause of ill-conditioning, which most practitioners never separate. |
| **Evidence of competence** | Reproduced textbook exponents with intervals, a clean scale-versus-correlation ablation, correct censoring, a plan that predates the results and a verdict with explicit limits. |
| **Misconceptions exposed** | 'Adaptive means scale-free.' 'Faster' without a cost model. 'Averaging iteration counts of runs that did not finish.' 'Newton is always cheapest because it takes fewer steps.' |
| **Preparation for later work** | Leads into ML-05 training diagnostics, ML-10 experiment tracking and research-style evaluation across the ML track. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
