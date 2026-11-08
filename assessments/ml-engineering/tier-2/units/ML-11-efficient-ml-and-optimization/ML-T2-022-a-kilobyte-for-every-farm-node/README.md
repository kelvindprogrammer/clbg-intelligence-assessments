# ML-T2-022: A Kilobyte for Every Farm Node: Quantising and Pruning a Small Network to a Byte Budget

> *A solar-powered soil node in Kano has a few kilobytes of flash for its model. Shrink a trained network to a fifth of its size, prove it still decides correctly, and show which of your choices bought the saving.*

![Format: Optimization](https://img.shields.io/badge/format-Optimization-0366d6) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-022` |
| **Title** | A Kilobyte for Every Farm Node: Quantising and Pruning a Small Network to a Byte Budget |
| **Subtrack** | ML Engineering |
| **Tier** | 2: Applied Competence |
| **Unit** | [ML-11: Efficient ML and Model Optimization](../README.md) |
| **Format** | Optimization |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14–20 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | A multilayer perceptron as matrices and ReLU; fitting an MLP in scikit-learn; accuracy on a held-out set; numpy broadcasting |
| **Skills developed** | Symmetric integer quantisation; per-tensor versus per-channel scales; global magnitude pruning; honest storage accounting; choosing a configuration on calibration data without touching the test set |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Farmers' cooperatives around Kano (fictional "Kano Tomato Growers Network") are deploying low-cost soil nodes that read 24 sensor channels (moisture at several depths, electrical conductivity, temperature, battery voltage and derived ratios) and decide among four actions: `wait`, `irrigate_now`, `salinity_alert` or `sensor_fault`. The node's microcontroller has no network at the field edge and only a few kilobytes of flash set aside for the model. The data science team has trained a small network (24-64-32-4, ReLU) that makes good decisions, but its float32 weights take about 15 KB, and the firmware team says the budget is **20% of that**.

You are asked to compress the network and defend the result. No library does it for you: you implement symmetric integer quantisation, global magnitude pruning and a storage-cost model, then write `compress`, which chooses the bit width, the scaling granularity and the sparsity using **only a calibration set**. The test set is for the final claim, and using it to choose anything is a methodological failure.

The specification is partial on purpose. Three things are fixed: the quantiser's exact arithmetic, the storage model, and the acceptance bars. Everything else is open: whether per-channel scales are worth their overhead, whether pruning pays for its index storage at this size, whether different layers should get different precision, and what to do when the calibration set cannot separate two configurations. Part of the task is finding out that the obvious recipe (int8 everywhere) does not meet the budget, and that the clever recipe (heavy pruning) may fit the bytes once you pay for indices but wreck the decisions.

> **Why this matters beyond this task.** Edge ML is decided by bytes and milliseconds, not by leaderboard accuracy. Teams that cannot account for storage honestly ship models that do not fit, or compress blindly and discover the accuracy cost in the field.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** symmetric integer quantisation with per-tensor and per-channel scales, and bound its round-trip error.
2. **Prune** a network globally by weight magnitude and explain why global differs from per-layer pruning.
3. **Account** for storage honestly: packed bits, scales, biases and sparse indices, and decide when sparse storage wins.
4. **Select** a configuration on calibration data and report its test performance once.
5. **Compare** your recipe against naive baselines (uniform int8, per-tensor int4) and attribute the savings.
6. **Reason** about which layers and which classes lose accuracy first, and why.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `squeeze` in [`starter/squeeze/compression.py`](starter/squeeze/compression.py). The forward pass, accuracy helper, `float32_bytes` and the `CompressedModel` container in `core.py` are provided. A model is a list of weight matrices `Ws` (shape `(n_in, n_out)`) and bias vectors `bs`. Use numpy only.

| ID | Requirement |
|---|---|
| **R1** | `quantize_tensor(W, bits, per_channel=True) -> (Q, scales)`: symmetric, `qmax = 2**(bits-1) - 1`, `scale = max|W| / qmax` (per output column when `per_channel`, else one scalar), `Q = clip(rint(W / scale), -qmax, qmax)` as an integer array. A zero tensor or column gets scale 1. `dequantize(Q, scales)` returns `Q * scales`. |
| **R2** | `magnitude_prune(Ws, sparsity) -> list`: zero the `round(sparsity * total_weights)` smallest-magnitude weights **globally** across all matrices (biases are never pruned). Ties break by flat order. Inputs are not modified. |
| **R3** | `layer_bytes(shape, nnz, bits, n_scales) -> int`: storage of one layer in bytes, `min(dense, sparse) + 4*n_scales + 4*n_out`, where dense is `ceil(n_in*n_out*bits/8)` and sparse is `ceil(nnz*(bits+16)/8)` (value plus a 16-bit index per nonzero). Biases stay float32. |
| **R4** | `compress(Ws, bs, X_cal, y_cal, budget_ratio=0.20, max_drop=0.025) -> CompressedModel` with `.bytes` (by your R3 accounting, summed over layers) at most `budget_ratio * float32_bytes(Ws, bs)`, `.predict(X)`, and `.config` describing what you chose. Choose bits, scaling, sparsity and per-layer settings from `X_cal`/`y_cal` only. If the budget cannot be met, raise `ValueError`. |

### D.2 Engineering requirements (mandatory)

- Deterministic; the inputs `Ws`, `bs` are never mutated.
- Every candidate configuration is scored by one shared function, so comparisons are fair.
- At least **8 tests of your own** in `tests/test_member_*.py`, including a round-trip error bound and a test that zero-sparsity pruning is the identity.
- `experiments.py` regenerates every number and figure in `REPORT.md`, including results on **at least 5 different seeds** of `train_float_model`.

### D.3 Responsibility

The data is synthetic. In the report, write one paragraph on the cost of a wrong decision at the farm (a missed `salinity_alert` damages a season's yield; a spurious `irrigate_now` wastes scarce water and battery) and on how you would test that compression does not degrade the rarest class disproportionately.

### D.4 Optional enhancements

- Per-layer bit widths found by a sensitivity sweep.
- Quantisation-aware fine-tuning of the surviving weights for a few epochs in numpy.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_task(seed)` and `train_float_model(seed, hidden=(64, 32))` return the float weights and train, calibration (800) and test (2,000) splits |
| **Provenance** | **Synthetic**, deterministic given the seed; labels come from a fixed random tanh network plus noise; no real farm or sensor |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Features** | 24 standardised sensor channels, 4 classes (`wait`, `irrigate_now`, `salinity_alert`, `sensor_fault`) |
| **Size** | Nothing committed; training the float model takes a few seconds on a laptop |

Hidden tests use other seeds, other architectures (for example 96-48) and other budgets and accuracy-drop limits.

**Setup**

```bash
cd assessments/ml-engineering/tier-2/units/ML-11-efficient-ml-and-optimization/ML-T2-022-a-kilobyte-for-every-farm-node
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `squeeze/` package | Quantiser, pruner, storage model and `compress` |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Includes round-trip and identity tests |
| 3 | `experiments.py` | Reproduces the comparison table (5 or more seeds) and figures |
| 4 | `REPORT.md` (at most 1,500 words plus tables), from the [template](submission-template/REPORT.md) | Design memo for the firmware team; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ Quantiser, pruner and storage model match the hand-computed values in the public tests, including rounding, global pruning and the dense/sparse switch.
3. ⚙ **Budget.** `compress(..., budget_ratio=0.20)` returns a model whose `.bytes` is at most 20% of the float32 size, and a 12% budget is also met.
4. ⚙ **Accuracy.** On the official test split (seed 2026) the compressed model loses at most **3.0 percentage points** against the float model. *Justification:* the calibration set has 800 samples, so its accuracy has a standard error near 1.1 points; a limit of 2.5 on calibration plus 0.5 slack is the smallest the reference meets on all seeds tried; the reference loses about 0.5 to 1.5 points.
5. ⚙ **Robustness.** Hidden models (other seeds and a 96-48 architecture) meet their budgets with accuracy loss at most 3.5 to 4.0 points.
6. ⚙ Inputs are not mutated and no test data is used by `compress`.
7. ✍ The report compares your recipe with uniform per-tensor int8 and per-tensor int4 at equal or lower size and states which choices contributed what (bit width, per-channel scales, pruning).
8. ✍ The report states the uncertainty of the accuracy differences (at least 5 seeds, plus a binomial standard error) and does not claim a ranking that the noise cannot support.

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

1. **Create your own private repository** named `clbg-ML-T2-022-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `squeeze/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Mixed precision.** Give each layer its own bit width using a sensitivity sweep and test whether it beats the best uniform choice beyond the noise.
2. **Fine-tuning.** Recover accuracy by retraining surviving weights for a few epochs in numpy with the quantiser in the loop.
3. **Outlier handling.** Clip weights at a percentile before computing the scale and analyse the effect on 4-bit accuracy.
4. **Rare-class audit.** Report per-class recall before and after compression and propose a safeguard for `salinity_alert`.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why per-channel scales usually help at 4 bits and what they cost in bytes; (2) ask at what sparsity sparse storage starts to beat dense for a 4-bit layer under the R3 model; (3) give an unseen modification, for example a budget of 10% or a 16-bit index, and ask which of your choices change and why.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | A ReLU MLP as matrix products; numpy; what a held-out set is for. No prior compression background. |
| **New skill developed** | Treating model size as a first-class constraint, with exact accounting and selection that does not touch the test set. |
| **Decisions the member must make** | Bit width; per-channel versus per-tensor; whether to prune; per-layer settings; how to break calibration ties. |
| **What must be investigated independently** | Where quantisation error enters (first layer, outlier columns), and when index overhead cancels the benefit of sparsity. |
| **Why it is interesting** | The obvious fix (int8) misses the budget and the fashionable one (heavy pruning) pays an index tax. The answer lies between them. |
| **Evidence of competence** | Exact arithmetic on hand cases, budgets met on re-seeded models, an ablation that attributes the saving. |
| **Misconceptions exposed** | 'Sparsity always saves bytes.' 'int8 means a quarter of the size.' 'Choose on the test set, it is only a little.' 'Lower bits always lose accuracy.' |
| **Preparation for later work** | Leads into ML-11 Tier 3 (distillation and latency-accuracy-size frontiers) and ML-12 serving constraints. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
