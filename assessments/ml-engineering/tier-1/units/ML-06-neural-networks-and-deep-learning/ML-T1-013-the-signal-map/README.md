# ML-T1-013: The Signal Map

> *Derive the gradients, prove them numerically, then break the network on purpose.*

![Format: Implementation](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T1-013` |
| **Title** | The Signal Map: Backpropagation From Scratch for a 4G Coverage Classifier |
| **Subtrack** | ML Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [ML-06: Neural Networks and Deep Learning](../README.md) |
| **Format** | Implementation |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 10–16 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | The chain rule, numpy matrix operations, logistic regression and cross-entropy; no deep-learning framework experience needed. |
| **Skills developed** | Backpropagation; softmax cross-entropy gradients; numerical gradient checking; initialisation; mini-batch SGD with momentum |
| **Technologies** | Python 3.10+, numpy, pandas, pytest |

---

## B. Problem Statement

A telecom operator is planning rural 4G expansion in a (fictional) district. Engineers drove a van through a 10 km by 10 km area and recorded **1,000 samples**: a map position `(x_km, y_km)` and whether the phone held a 4G connection. Two masts serve the area. Each covers a roughly circular footprint, so the covered region is the *union of two discs*, which no straight line can separate from the uncovered region. About 3% of readings are wrong because a phone briefly dropped to 3G.

The network planner wants a model that, for any point on the map, says whether 4G is available, so that she can decide where a third mast is needed. A logistic regression only reaches about 70% accuracy, because the boundary is curved. A small neural network can learn it. You could call a framework in three lines, but the planner's team has been burned by black-box training runs that silently learned nothing, and the department wants engineers who can *see inside* training.

Your task is to build the network yourself with numpy only: initialisation, forward pass, loss, **hand-derived backward pass**, a gradient checker that proves the backward pass is right, and mini-batch SGD with momentum. Then you use it on the coverage map, and you deliberately break it, by initialising all weights to zero, to explain why training fails. No framework (PyTorch, TensorFlow, JAX) and no sklearn models may be used inside `tinynet`.

## C. Objectives

When you finish, you should be able to show that you can:

- Derive the gradient of softmax cross-entropy and of a ReLU hidden layer, and implement both with matrices.
- Verify an analytic gradient against central finite differences and interpret the relative error.
- Implement mini-batch SGD with classical momentum exactly as specified.
- Explain, with an experiment, why zero initialisation prevents learning and what He initialisation fixes.
- Read training-loss curves to diagnose a learning rate that is too high or too low.
- Write tests that would catch a wrong gradient or an off-by-one in batching.

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `tinynet` in [`starter/tinynet/net.py`](starter/tinynet/net.py). Signatures and conventions are fixed by the docstrings. `params` is a list of `(W, b)` tuples. Only numpy (and pandas for loading data) may be used in the package.

| ID | Requirement |
|---|---|
| **R1** | `init_params(layer_sizes, seed, scheme)`: He (`N(0, 2/fan_in)`), Xavier (`N(0, 2/(fan_in+fan_out))`) or zeros; biases zero; reproducible from the seed. |
| **R2** | `forward(params, X)` returns `(probs, cache)`: ReLU hidden layers, softmax output, numerically stable (inputs of size 1e4 must not overflow). |
| **R3** | `loss(probs, y, params, l2)`: mean cross-entropy plus `0.5 * l2 * sum(W**2)` over weights only. |
| **R4** | `backward(params, cache, y, l2)`: gradients of R3 for every `(W, b)`. Must match finite differences to relative error below `1e-4` per entry. |
| **R5** | `gradient_check(params, X, y, l2, eps)`: the largest relative error over all parameters; must restore parameters. A correct network scores below `1e-6`. |
| **R6** | `train(...)`: mini-batch SGD with classical momentum `v = mu*v - lr*g; w += v`, one permutation per epoch from a single `default_rng(seed)`, last batch possibly smaller, per-epoch full-data loss in `history`. Reproducible. |
| **R7** | `predict(params, X)`: integer labels. |
| **R8** | `experiments.py` and `REPORT.md`: (a) gradient-check table for three architectures; (b) the coverage map learned with your best settings and held-out accuracy; (c) the zero-init experiment and its explanation; (d) loss curves for three learning rates (too small, good, too high); (e) a one-paragraph answer on what the network would need to learn a third mast. |

### D.2 Engineering requirements (mandatory)

- Vectorised numpy (no per-sample Python loops in forward or backward; `gradient_check` may loop over parameters).
- Keep the provided tests passing and add **at least 6 tests of your own** in `tests/test_member_*.py`, including one that fails if the ReLU mask is dropped from backward.
- Do not modify the raw data. Inputs are scaled to [0, 1] by dividing coordinates by 10 before training.

### D.3 Privacy and responsibility

The data is **synthetic**: no real subscriber or location is involved. Real drive-test data combined with device identifiers can reveal where individuals travel, which is personal data under the Nigeria Data Protection Act 2023. In `REPORT.md`, state in two sentences what you would strip or aggregate before sharing real drive-test logs.

---

## E. Dataset and Resources

All data is **synthetic** (fictional district and masts), produced by a deterministic generator in the assessor kit.

| File | Content |
|---|---|
| [`resources/data/coverage.csv`](resources/data/coverage.csv) | 1,000 samples: `sample_id, x_km, y_km, covered_4g, split` (750 train, 250 test). About 3% label noise. 26 KB. |

Licence: CC BY 4.0. The held-out `test` rows must be used only for the final accuracy you report. Choosing hyperparameters on them is an integrity breach.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `tinynet/` (completed starter) | The network, backward pass and trainer |
| 2 | `tests/test_member_*.py` (at least 6 tests) | Guards against wrong gradients and batching bugs |
| 3 | `experiments.py` and `outputs/` | Reproduces the report numbers and figures |
| 4 | `REPORT.md` (at most 1,000 words plus figures), from the [template](submission-template/REPORT.md) | Explains results and the failure experiment; includes the AI-use declaration |
| 5 | A short live defence | Verifies understanding (§K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Criteria marked ⚙ are checked automatically by the public and hidden test suites; the rest are checked by hand.

1. ⚙ Public and your own tests pass from a clean environment.
2. ⚙ `backward` agrees with finite differences to relative error below `1e-4` per sampled entry; `gradient_check` is below `1e-6` on the test nets. *Justification:* central differences with `eps=1e-5` in float64 are accurate to about `1e-9` here, so a larger gap means a real bug.
3. ⚙ Two hand-computed momentum steps match your `train` to `1e-10`.
4. ⚙ Held-out accuracy on the coverage map is **at least 0.90** with a `[2, 16, 16, 2]` network. *Justification:* about 3% of labels are flipped, so the ceiling is near 0.97; the reference reaches 0.93, and a linear model reaches about 0.70.
5. ⚙ Hidden tests on a re-seeded map (different mast positions and radii), other architectures and three classes also pass.
6. ✍ The report explains the zero-init failure: why ReLU gradients vanish, what symmetry means, and why He scaling uses `2/fan_in`.
7. ✍ Loss curves for three learning rates are shown, and each is diagnosed.
8. ✍ Every number in the report is regenerated by `experiments.py`.

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

1. **Create your own private repository** named `clbg-ML-T1-013-<your-github-username>` from this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `tinynet/` (your package), `tests/` (provided tests plus your own `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `outputs/` (figures), `REPORT.md` (from the template, including the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core requirements.

1. Add Adam and compare convergence speed with momentum SGD on the same architecture.
2. Plot the learned decision boundary over the map and use it to propose where a third mast would add the most coverage.
3. Implement dropout and show whether it helps given 3% label noise, with an honest comparison across seeds.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn (explain a concept, review your code). **They may not do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: tool, purpose, example prompt, how you verified the output. Undisclosed use that emerges at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code or method adapted from documentation or papers, with a link.
- **Collaboration:** discuss *general techniques* only. Do not share code, numbers or report text.
- **Verification of understanding.** In the short defence the assessor will ask you to (1) derive `dL/dz` for softmax cross-entropy on a blackboard, (2) explain what your gradient checker would print if you forgot the ReLU mask, and (3) change `train` live to use Nesterov momentum or a learning-rate decay.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Chain rule, matrix products in numpy, logistic regression and cross-entropy. |
| **New skill developed** | Opening the box: deriving, implementing and verifying backpropagation, then using the same tools to diagnose training failures. |
| **Decisions the member must make** | How to cache values for backward, how to structure vectorised code, which hyperparameters to use on validation data, and how to read loss curves. |
| **What must be investigated independently** | Why zero initialisation fails with ReLU, and what a wrong gradient looks like in the checker output. |
| **Why it's interesting** | A realistic network-planning question that a linear model cannot answer, and a failure experiment that makes an abstract idea (symmetry breaking) visible. |
| **Evidence of competence** | Gradient agreement to 1e-6, exact momentum behaviour, held-out accuracy, and live derivation at the defence. |
| **Misconceptions exposed** | "Backprop is magic." "Initialisation is a detail." "A decreasing loss means the model is correct." "Frameworks make understanding unnecessary." |
| **Preparation for later work** | Leads into ML-T2 training-diagnostics work and ML-T3 deep-learning replication; also CNN and sequence units. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
