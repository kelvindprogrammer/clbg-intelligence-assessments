# ML-T1-001: The Score That Overflowed: Numerically Stable Softmax and Logistic Loss from Scratch

> *A telecom churn model prints NaN at 2 a.m. Rebuild its loss functions so they survive extreme scores, and prove the gradients are right.*

![Format: Implementation (secondary: Debugging & Forensics)](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T1-001` |
| **Title** | The Score That Overflowed: Numerically Stable Softmax and Logistic Loss from Scratch |
| **Subtrack** | ML Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [ML-01: Mathematical and Computational Foundations](../README.md) |
| **Format** | Implementation (secondary: Debugging & Forensics) |
| **Difficulty** | Technical 2 · Mathematical 3 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8–12 hours over 1 week |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | numpy broadcasting and axis arguments; the definition of softmax and cross-entropy; derivative of a function of one variable. Helpful but optional: a first course in linear algebra |
| **Skills developed** | Floating-point reasoning; log-sum-exp trick; stable sigmoid and binary cross-entropy; analytic gradients and finite-difference checking; gradient descent on a convex loss |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Kasuwa Mobile (a fictional Nigerian mobile operator) scores 2 million subscribers a night for churn risk. The scoring job uses a hand-written softmax over three outcomes (stay, downgrade, leave) and a hand-written logistic loss for a retention-offer model. Last Tuesday the job wrote `NaN` for 14,000 subscribers and the retention team sent no offers to a region that includes Lagos Mainland. The post-mortem found no bug in the model. It found that a handful of subscribers with unusually large raw feature values (airtime spend recorded in kobo, data usage in megabytes) produced scores near ±1000, and the code did `np.exp(score)` directly.

You are the engineer asked to fix the numerical core. You will rebuild a small library, `stablemath`, whose pieces are the same ones every ML framework quietly provides: `logsumexp`, `softmax`, `log_softmax`, a stable sigmoid, binary cross-entropy from logits, softmax cross-entropy with its gradient, and a gradient-descent logistic regression that is stable on the raw, badly scaled data. You will also write the evidence: tests that the naive code fails and yours does not, and gradient checks that show the maths is right.

This is a *from scratch* assessment. You may use numpy, but not `scipy.special`, `sklearn` losses, or any ready-made `logsumexp`/`softmax`. The point is to know exactly why those functions are written the way they are.

> **Why this matters beyond this task.** Almost every NaN loss in a training run traces back to an `exp` or `log` that was applied without thought. The habits here (rewrite expressions so the dangerous quantity never appears, then verify with a numerical check) are the foundation of every later ML engineering unit.

**Facts you can rely on.**

- Features may be on wildly different scales, so raw scores of ±1000 are realistic in production.
- The job runs in float32 on the scoring cluster and float64 in training. Your functions must give finite, correct results in both.
- Labels are integers `0..K-1` (softmax) or `{0, 1}` (binary).

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Explain** how overflow, underflow and catastrophic cancellation arise in `exp`, `log` and their compositions.
2. **Implement** log-sum-exp, softmax and log-softmax with a shift that makes overflow impossible, for any axis.
3. **Rewrite** sigmoid and binary cross-entropy so that neither `exp` of a large positive number nor `log` of zero ever occurs.
4. **Derive and implement** the gradient of softmax cross-entropy with respect to the logits, and **verify** it with central finite differences.
5. **Fit** a logistic regression by gradient descent on badly scaled features, keeping the loss finite and non-increasing.
6. **Test numerical code** by constructing inputs that the naive version gets wrong and by comparing against an independent identity.
7. **Communicate** a numerical failure in plain language, with measured evidence.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `stablemath` package in [`starter/stablemath/`](starter/stablemath/). Signatures are fixed; internals are yours. All functions must accept `float32` and `float64` arrays and return the same dtype as the input unless stated.

| ID | Requirement |
|---|---|
| **R1** | `logsumexp(a, axis=-1, keepdims=False)` returns `log(sum(exp(a)))` along `axis`, finite whenever the true value is finite in float64, including rows that are entirely `-inf` (result `-inf`, no warning-as-error, no NaN). |
| **R2** | `softmax(z, axis=-1)` returns probabilities that sum to 1 along `axis` and never contain NaN for finite input of any magnitude, including `±1e4`. |
| **R3** | `log_softmax(z, axis=-1)` equals `log(softmax(z))` where that is finite, and stays finite where `softmax` underflows to 0 (do **not** compute `log(softmax(z))`). |
| **R4** | `sigmoid(z)` is finite and in `[0, 1]` for every finite `z` and emits no overflow warning. |
| **R5** | `bce_with_logits(z, y)` returns the elementwise binary cross-entropy of logits `z` against labels `y` in `{0,1}`. It must be exact (relative error below `1e-9` in float64) for `|z|` up to `1e4`, and must not call `sigmoid` followed by `log`. |
| **R6** | `softmax_cross_entropy(logits, labels)` returns `(mean_loss, grad)`, where `grad` has the shape of `logits` and is the gradient of `mean_loss` with respect to `logits`. `labels` are integer class ids. |
| **R7** | `numeric_grad(f, x, eps=1e-6)` returns the central finite-difference gradient of a scalar function `f` at array `x`. |
| **R8** | `LogisticRegression(l2=0.0, lr=0.5, steps=500)` with `fit(X, y)`, `predict_proba(X)`, `predict(X)` and attribute `loss_history_`. It must standardise features internally (store the means and standard deviations), use `bce_with_logits`, and produce a finite, non-increasing training-loss history on the provided churn data in its **raw, unscaled** form. |

### D.2 Engineering requirements (mandatory)

- No Python loop over samples or classes in R1 to R6 (loops over `steps` are fine).
- Do not mutate inputs.
- Provide at least **8 tests of your own** in `tests/test_member_*.py`, at least three of which are numerical edge cases that the provided `naive.py` implementations get wrong.
- Produce `report_numbers.py` that regenerates every number quoted in `REPORT.md`.

### D.3 Responsibility

The churn data is synthetic and describes no real subscriber. In `REPORT.md`, write one paragraph on what could go wrong, for real subscribers, if a scoring job silently emitted NaN or saturated probabilities (who is not offered a retention package, and how would you detect it before customers notice?).

### D.4 Optional enhancements

- A `temperature` argument for softmax and an analysis of how it interacts with your shift.
- A float16 study: at what magnitude does each function degrade?

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated on demand by [`resources/datagen.py`](resources/datagen.py): `make_churn(n, seed)` and `make_logits(n, k, seed, scale)` |
| **Provenance** | **Synthetic**, deterministic given a seed. No real subscriber is described. Features mimic raw telecom exports: airtime spend in kobo (about 10^5), data usage in MB (about 10^3 to 10^4), tenure in days, dropped calls |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Provided code** | `stablemath/naive.py` holds the failing implementations used in the post-mortem; use it for your evidence, do not edit it |
| **Size** | Nothing is committed; the largest generated array is under 1 MB |

The official evaluation seed is 2026. Hidden tests use other seeds and larger scales, so hard-coded values will fail.

**Setup**

```bash
cd assessments/ml-engineering/tier-1/units/ML-01-mathematical-and-computational-foundations/ML-T1-001-the-score-that-overflowed
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `stablemath/` package (completed starter) | Core technical evidence |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Shows you can target numerical edge cases |
| 3 | `report_numbers.py` | Reproducible evidence for the report |
| 4 | `REPORT.md` (at most 1,200 words), from the [template](submission-template/REPORT.md) | Explains each failure, each fix and its limits, and carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes all provided tests and your own tests from a clean environment created from `requirements.txt`.
2. ⚙ **Exactness:** `logsumexp`, `log_softmax` and `bce_with_logits` match a high-precision identity (shift-invariance, and the closed forms at `z = ±1000`) to relative error below `1e-9` in float64 and `1e-5` in float32. *Justification:* these are the tolerances at which float64 and float32 arithmetic can still be distinguished from an algorithmic error.
3. ⚙ **No NaN or warnings:** every function runs with `np.errstate(over='raise', invalid='raise', divide='raise')` on inputs up to magnitude `1e4`. *Justification:* a stable algorithm should never trigger overflow, so promoting warnings to errors detects silent failure.
4. ⚙ **Gradients:** `softmax_cross_entropy`'s gradient agrees with `numeric_grad` to a maximum absolute difference below `1e-6` on random logits of scale 5, and its rows sum to zero within `1e-12`.
5. ⚙ **Model:** `LogisticRegression` reaches a final training loss within `0.01` of scikit-learn's unpenalised optimum on the churn data and agrees with it on at least 97% of predictions on a re-seeded held-out set. *Justification:* gradient descent for 500 steps on a standardised convex problem is achievable to this tolerance with `lr=0.5`; the reference reaches 0.003.
6. ⚙ The loss history is finite and non-increasing (tolerance `1e-12`).
7. ✍ The report explains the mechanism of each naive failure, shows measured naive-versus-stable behaviour, and states honestly what remains imperfect.
8. ✍ `report_numbers.py` regenerates every number in the report.

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

1. **Create your own private repository** named `clbg-ML-T1-001-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `stablemath/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Stability of the gradient itself.** Show that `softmax(z) - onehot` is stable but a gradient obtained by differentiating `log(softmax(z))` term by term is not, with a failing input.
2. **float16.** Find the largest logit magnitude each function tolerates in float16 and explain the breakdown point.
3. **Second order.** Implement the Hessian-vector product for logistic loss and verify it with finite differences of your gradient.
4. **Compensated summation.** Compare naive, pairwise and Kahan summation for the loss over 10^6 samples.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask you to show on paper why `logsumexp` with the max subtracted cannot overflow; (2) ask which line of your binary cross-entropy would break first without the `log1p` form, and for which input; (3) give an unseen modification, for example a temperature parameter in softmax or a clipped loss, and ask you to adapt your code live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | numpy basics, the definitions of softmax and cross-entropy, and a derivative. No optimisation theory. |
| **New skill developed** | Treating floating point as a design constraint: algebraically rewrite so the dangerous quantity never exists, then confirm with an independent numerical check. |
| **Decisions the member must make** | How to shift, which form of BCE to use, what step size and tolerance a finite-difference check deserves, how to treat `-inf` rows, and how to keep dtypes honest. |
| **What must be investigated independently** | Exactly which inputs break the naive code and why; the starter shows the failures but not the mechanism. |
| **Why it is interesting** | The bug is real, the fix is three lines, and understanding why it works takes genuine mathematical care. |
| **Evidence of competence** | Exact agreement at extreme inputs under `errstate(over='raise', invalid='raise', divide='raise')`, verified gradients, and a defence that adapts the code live. |
| **Misconceptions exposed** | 'Clip the logits to ±30 and move on.' 'log(softmax) is fine.' 'float64 means I do not need to care.' 'A loss that prints a number is a loss that is correct.' |
| **Preparation for later work** | Leads into ML-01 optimisation tier-2 work, ML-02 implementations of boosting losses, and ML-05 training diagnostics. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
