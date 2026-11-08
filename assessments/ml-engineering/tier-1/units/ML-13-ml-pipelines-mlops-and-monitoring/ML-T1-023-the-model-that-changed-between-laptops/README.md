# ML-T1-023: The Model That Changed Between Laptops: Fingerprints, Seeds and a Versioned Artifact Store

> *Two analysts trained 'the same' model and got different numbers. Build the layer that makes that impossible to miss.*

![Format: Implementation (secondary: Debugging-Forensics)](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T1-023` |
| **Title** | The Model That Changed Between Laptops: Fingerprints, Seeds and a Versioned Artifact Store |
| **Subtrack** | ML Engineering |
| **Tier** | 1: Foundations |
| **Unit** | [ML-13: ML Pipelines, MLOps and Monitoring](../README.md) |
| **Format** | Implementation (secondary: Debugging-Forensics) |
| **Difficulty** | Technical 2 · Mathematical 1 · Research 1 · Engineering 3 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 8-12 hours over 1 week |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Python functions and classes, numpy arrays, scikit-learn LogisticRegression, hashlib. No MLOps tooling is needed or allowed. |
| **Skills developed** | Canonical hashing; deterministic training; content-addressed storage; run provenance; reading a run-diff |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Kurmin Grid (fictional) runs solar mini-grids in Kaduna State. Customers buy prepaid energy tokens by transfer. The data team predicts which customers will **lapse** (go 30 days without a top-up) so field agents can visit them first. Last month two analysts reported different accuracies for 'the same' model. One had re-exported the customer table from a spreadsheet (same numbers, different column order and a few `-0.0` values), one had used a different seed for the split, and a third copy of the model file had been edited by hand to 'fix' a coefficient. Nobody could say which model was in production or why they differed.

Your job is the smallest reproducibility layer that would have caught all three problems. You will implement, from scratch and with only numpy, scikit-learn and the standard library, six small pieces:

1. a **fingerprint of a data table** that ignores irrelevant representation (memory layout, `-0.0`, integer versus float storage of the same value) but changes whenever any value, row order, column name or column order changes;
2. a **fingerprint of a configuration** that ignores dictionary key order and numpy scalar types but changes with any real value;
3. a **deterministic split** and a **deterministic training run** that returns a record whose `run_id` is derived from data, configuration and code version;
4. an **artifact store** that saves each run once (idempotently), loads it back exactly, lists runs, and *detects* edits to either the manifest or the weights;
5. a **run diff** that says whether two runs differ in data, configuration (and which keys), code version or learned model.

This is a precisely specified implementation task: the tests fix every behaviour. The learning is in the details that bite in production, such as `hash()` randomisation, byte order, shapes that share bytes, and the difference between a model that *looks* the same and one that *is* the same.

> **Why this matters beyond this task.** Every model-governance practice, including audit trails, rollback and 'which model made this decision?', rests on being able to say exactly which data, configuration and code produced an artifact. Tools such as DVC or MLflow do this at scale; this task makes you build the core idea once so that you can judge them.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** canonical fingerprints for tables and configurations and state exactly which differences they ignore and which they detect.
2. **Make** a training run bit-for-bit repeatable, including across separate Python processes.
3. **Derive** a run identifier from the inputs that determine a model, and explain why timestamps must not be part of it.
4. **Store** artifacts so that identical runs are saved once and edited artifacts are detected on verification.
5. **Diagnose** why two models differ by decomposing the difference into data, configuration, code and learned parameters.
6. **Explain** in writing three realistic sources of non-reproducibility and how your design handles each.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the package [`repropipe`](starter/repropipe/). The `Run` record and `CODE_VERSION` are provided in `records.py`. Use only the standard library, numpy and scikit-learn.

| ID | Requirement |
|---|---|
| **R1** | `table_fingerprint(X, y, names) -> str` returns a 64-character lowercase hex SHA-256. Identical for the same values regardless of memory order (C or Fortran), regardless of whether the values were stored as ints or floats, and regardless of `-0.0` versus `0.0`. It must differ when any single value, the row order, the column order, any column name, the labels, or the shape changes (a 4x6 and a 6x4 table with the same flat values must differ). NaNs must hash identically. |
| **R2** | `config_fingerprint(config) -> str` returns a SHA-256 hex digest of a nested dict. Independent of key order at any depth; lists and tuples are equivalent; numpy scalars hash like the equivalent Python value; any real value change changes the digest. Raises `TypeError` for unsupported values (sets, arrays, objects). |
| **R3** | `split_indices(n, seed, test_frac) -> (train_idx, test_idx)`: take `np.random.default_rng(seed).permutation(n)`, let `k = round(test_frac * n)`, test is the first `k` entries of the permutation and train the rest; both arrays returned sorted. |
| **R4** | `train(config, X, y, names) -> Run`. `config` has `seed`, `test_frac` and `C`. Split with R3; standardise using **training rows only**; fit scikit-learn `LogisticRegression(C=C, solver="lbfgs", max_iter=500)`; fill `Run` with the weights in the standardised space plus `mean` and `scale`; set `data_fp`, `config_fp`, `code_version`; `run_id` is the first 16 hex characters of `sha256(data_fp + config_fp + code_version)`; `metrics` has `accuracy` and `log_loss` on the test rows. `predict_proba(run, X)` returns P(class 1) from the run alone. Two calls with the same inputs return bit-identical weights, in the same or a different process. |
| **R5** | `ArtifactStore(root)` with `save(run)`, `load(run_id)`, `verify(run_id) -> bool` and `list_runs()`. `save` is idempotent (saving the same run twice leaves one entry and does not rewrite it) and returns the run's directory. `load` returns a `Run` equal to the saved one (arrays bit-identical). `verify` returns `False` if the weights file or the manifest has been edited in any way that changes the weights, the metrics-independent identity fields, or the run id, and `True` otherwise; it never raises. `list_runs` returns sorted ids. |
| **R6** | `diff_runs(a, b) -> dict` with keys `data`, `config`, `code`, `model` (booleans) and `config_keys` (sorted list of top-level keys whose values differ). |

### D.2 Engineering requirements (mandatory)

- Deterministic: no timestamps, no `hash()`, no unseeded randomness, no dependence on dictionary insertion order.
- Do not name any dataset column in your code; the hidden tests use another table.
- At least **8 tests of your own** in `tests/test_member_*.py`, including one that proves your fingerprint is stable across two processes started with different `PYTHONHASHSEED` values.
- `experiments.py` retrains the model twice, and with three controlled perturbations (reordered columns, a different seed, a hand-edited coefficient), and prints the `diff_runs` result and the `verify` result for each; the output is quoted in `REPORT.md`.

### D.3 Responsibility

The data are synthetic and fictional. In the report, write one paragraph on how versioned runs help with accountability under the **Nigeria Data Protection Act 2023** (for example showing which data a decision-making model was trained on, supporting accuracy and accountability obligations, and enabling an audit of automated decisions), and one sentence on what a fingerprint must never contain: raw personal data or customer identifiers. Cite only what you are sure the Act provides, and say if you are not sure.

### D.4 Optional enhancements

- Add a `lineage(run_id)` that follows a chain of runs (a model fine-tuned from another) and detects a broken link.
- Make the fingerprint of a large table streaming (chunked) and prove it equals the one-shot digest.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/gridgen.py`](resources/gridgen.py): `make_topups(n=1500, seed=11)` returns `X, y, names` |
| **Provenance** | **Synthetic**, deterministic given the seed; no real customer, meter or operator |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Columns** | `avg_daily_kwh, topup_gap_days, last_topup_ngn, tenure_months, appliances, rainy_season`; label `y = 1` means the customer lapsed within 30 days |
| **Size** | Nothing is committed; `python resources/gridgen.py --out DIR --seed 11` writes a CSV of about 260 KB |

Hidden tests use other seeds, other table shapes and column names, Fortran-ordered and float32-derived copies, and separate processes with different hash seeds.

**Setup**

```bash
cd assessments/ml-engineering/tier-1/units/ML-13-ml-pipelines-mlops-and-monitoring/ML-T1-023-the-model-that-changed-between-laptops
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `repropipe/` package | Fingerprints, deterministic training, artifact store and run diff |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Includes the cross-process stability test |
| 3 | `experiments.py` | Reproduces the perturbation table in the report |
| 4 | `REPORT.md` (at most 900 words plus tables), from the [template](submission-template/REPORT.md) | Explains what is and is not detected, and carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ **Fingerprint equivalences.** Fortran-ordered, int-stored and `-0.0` variants of a table give the same digest; every single-value, row, column, name, label and shape change gives a different one. Justification: these are the representation changes a real export pipeline introduces, and the value changes are the ones that matter.
3. ⚙ **Config fingerprint.** Key order and numpy scalars are ignored; any value change is detected; unsupported types raise `TypeError`.
4. ⚙ **Determinism.** Two runs are bit-identical (`np.array_equal`, not `allclose`), including across processes with different `PYTHONHASHSEED`. Held-out accuracy on the official data (`seed=11`, `C=1.0`, `test_frac=0.25`) is at least **0.66**. Justification: the reference reaches about 0.73 and the majority-class rate is about 0.51, so 0.66 catches broken pipelines (for example no standardisation bug can hide, but a wrong split or label misalignment falls to chance); because a scaler fitted on test rows would barely move accuracy, the tests also check the scaler statistics exactly.
5. ⚙ **Store.** Round trip is exact, `save` is idempotent, and editing the weights or the manifest identity fields makes `verify` return `False`.
6. ⚙ **Run diff.** Each of data, config, code and model differences is reported independently.
7. ✍ The report names the three failures in §B, shows the `diff_runs` output that exposes each, and states at least one thing the design cannot detect (for example a library upgrade that changes lbfgs output).

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

1. **Create your own private repository** named `clbg-ML-T1-023-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `repropipe/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Environment capture.** Add numpy and scikit-learn versions to the run identity and show a run that is repeatable on your machine but flagged on another version.
2. **Garbage collection.** Add a retention policy to the store that never deletes a run referenced by a promoted model.
3. **Compare with a real tool.** Reproduce your core idea with DVC or MLflow on your machine (setup-only internet) and list what your layer does not provide.
4. **Streaming digest.** See D.4.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why `run_id` must not contain a timestamp and what would break; (2) show a table with one value changed by 1e-12 and ask whether your fingerprint treats it as the same data, and whether it should; (3) give an unseen modification, for example adding a feature column or a new config key, and ask which of your outputs change.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Using scikit-learn and numpy; what a hash is. No MLOps background. |
| **New skill developed** | Turning 'it works on my machine' into evidence: content-addressed identity for data, configuration and models. |
| **Decisions the member must make** | What the table fingerprint canonicalises; how to treat int versus float; what goes into the run id; how `verify` decides. |
| **What must be investigated independently** | Why identical-looking arrays can hash differently (strides, dtype, byte order, `-0.0`, NaN payloads) and why `hash()` is unusable. |
| **Why it is interesting** | The task looks trivial until a Fortran-ordered copy or a 4x6 versus 6x4 table breaks a naive hash. |
| **Evidence of competence** | Exact equalities on re-seeded, re-shaped data; tamper detection; a report that distinguishes detected from undetectable differences. |
| **Misconceptions exposed** | 'Same accuracy means same model.' 'Setting the seed is enough.' 'A hash of the file name versions the data.' |
| **Preparation for later work** | Leads into ML-13 Tier 2 drift monitoring and Tier 3 retraining policy, and into ML-12 deployment, where an artifact's identity must be checked at load time. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
