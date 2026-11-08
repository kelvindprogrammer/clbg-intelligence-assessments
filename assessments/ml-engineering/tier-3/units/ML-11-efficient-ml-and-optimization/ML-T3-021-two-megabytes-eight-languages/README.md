# ML-T3-021: Two Megabytes, Eight Languages: A Compression Study for On-Device Language Identification Under Distribution Shift

> *A language-ID model for a messaging app must fit in a few kilobytes on a feature phone. Clean test accuracy says every compression method works. The messages people actually send say otherwise. Design the study, build the instruments, and defend the model you would ship.*

![Format: Open-ended research](https://img.shields.io/badge/format-Open--ended%20research-0366d6) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-021` |
| **Title** | Two Megabytes, Eight Languages: A Compression Study for On-Device Language Identification Under Distribution Shift |
| **Subtrack** | ML Engineering |
| **Tier** | 3: Advanced and Research-Grade |
| **Unit** | [ML-11: Efficient ML and Model Optimization](../README.md) |
| **Format** | Open-ended research |
| **Difficulty** | Technical 4 · Mathematical 3 · Research 4 · Engineering 4 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 24–36 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Linear models on sparse features; ridge regression; quantisation and pruning at the level of ML-T2-022; train, validation and test discipline; basic experimental design. Recommended: ML-T2-022 |
| **Skills developed** | Designing a compression study with a defensible protocol; knowledge distillation by logit regression on an unlabelled transfer set; Pareto analysis across size, compute and accuracy; evaluation under distribution shift; selection under small-validation uncertainty; honest storage and compute accounting |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

A messaging start-up in Abuja (fictional "Gbagyi Chat") wants to route each incoming message to the right language-specific spam and safety filter, on the user's phone. The target devices are feature phones and low-end Androids with a few megabytes of spare memory, no reliable connectivity and a CPU that cannot afford much more than a couple of thousand multiply-adds per message. A language-identification model exists: a multinomial logistic regression on 2^16 hashed character n-gram features over **eight** languages, about **2 MB** as a dense float32 matrix. The device allows **10 KB** and **2,000 multiply-adds**.

The languages here are synthetic stand-ins: four cousin pairs of fictional languages, built so that each pair shares about 70% of its syllables (see [E](#e-dataset-and-resources)). No real language, speaker or message appears. The structure is realistic: close cousins are confusable, and real traffic is not the clean text the teacher was trained on.

On clean, well-formed messages every size from 256 to 65,536 hashed features reaches 96 to 98% accuracy, so compression looks free. But real messages are **short** (one to four words), **misspelt** (about 15% of characters), and **code-switched** (words from another language). On that distribution the 2 MB teacher scores only about two-thirds, and the compressed models lose ground in ways clean accuracy hides. The team has a large **unlabelled** pool of messages of both kinds, only 1,200 labelled clean messages (which trained the teacher), and **150 labelled shifted messages** to validate with. A standard error on 150 samples is about four percentage points, so the validation set cannot separate close candidates.

You are the engineer asked to recommend a model and the evidence for it. This is a research problem, not a recipe, and the brief does not say which compression method wins. Three parts are fixed, because the instruments must be exact for results to be comparable:

1. **Instruments.** A Pareto-front function, a size and compute cost model, a ridge distillation routine, and a selection rule that respects validation uncertainty.
2. **A candidate set.** At least eight candidates across at least three families (for example hard-label students, distilled students, a pruned teacher, a low-rank teacher, and bit-width variants), each reporting honest weights that the tests recompute accuracy and size claims from.
3. **A study.** A written protocol with hypotheses stated *before* you run them, controls, ablations (at least: transfer-pool composition, student feature dimension, bit width, ridge strength), and an explicit validity argument.

What counts as the "right" model, which objectives belong on the frontier, how much accuracy loss on shifted data is acceptable, and whether distillation earns its complexity are for you to decide and defend.

> **Why this matters beyond this task.** Compression results quoted on in-distribution benchmarks are routinely optimistic. The honest question is not "how small can we go" but "what do we lose, on the traffic we will actually see, with what confidence, for each byte we save".

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Build** exact cost models for size and multiply-adds, including sparse index overhead and low-rank factorisation.
2. **Distil** a teacher into smaller students using an unlabelled transfer set, and analyse what the transfer set's composition does.
3. **Construct** Pareto frontiers across size, compute and shifted accuracy, and explain why a frontier from clean accuracy misleads.
4. **Select** a deployable model under device limits with a rule that accounts for validation uncertainty.
5. **Design** a study with pre-stated hypotheses, controls and ablations, and report negative results honestly.
6. **Argue** the validity and limits of the conclusion: synthetic data, a small validation set, and shift types not covered.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `langsqueeze` in [`starter/langsqueeze/`](starter/langsqueeze/). The quantiser `quantise_cols` and the accuracy helper `accuracy` (which **recomputes** accuracy from a candidate's weights) are provided in `core.py`. A candidate is a dict `{name, family, spec, W, b}` where `W` is the effective weight matrix (features by classes) and `spec` is what you claim for `cost_model`. numpy, scipy and scikit-learn only.

| ID | Requirement |
|---|---|
| **R1** | `pareto_front(points, minimize, maximize) -> list[int]`: indices (ascending) of non-dominated points. A point is dominated if another is at least as good on every listed key and strictly better on at least one; of exact duplicates only the lowest index survives. Works for any number of keys and for an empty list. |
| **R2** | `cost_model(spec, avg_active) -> {"size_bytes": int, "macs": float}`. Kind `"linear"` (`n_features` F, `n_classes` C, `bits`, optional `nnz`): dense bytes `ceil(F·C·bits/8)`; sparse bytes `ceil(nnz·(bits + ceil(log2(F·C)))/8)`; the layer costs the smaller; add `4·C` for float32 biases and, if `bits < 32`, `4·C` for per-class scales; `macs = avg_active · nnz / F` (default `nnz = F·C`). Kind `"lowrank"` (adds `rank` r): two dense factors `F×r` and `r×C`, each `ceil(size·bits/8)`, plus `4·C` biases and, if `bits < 32`, `4·(r+C)` for scales; `macs = avg_active·r + r·C`. |
| **R3** | `distill_ridge(X, T, alpha) -> (W, b)`: minimise `‖XW + 1bᵀ − T‖² + α‖W‖²` with an **unpenalised** intercept, where `X` is sparse or dense and `T` holds the teacher's logits. |
| **R4** | `build_candidates(task, teacher_W, teacher_b) -> list[dict]`: at least 8 candidates from at least 3 families, one of which is the float32 teacher itself. Specs must be honest: `bits` bounds the distinct values per class column, `nnz` bounds the non-zeros, and `rank` bounds the matrix rank of `W`. The tests recompute accuracy and cost from `W`, `b` and `spec`; they never trust a number you report. |
| **R5** | `choose(rows, max_bytes, max_macs, n_val) -> str`: among rows (`name, size_bytes, macs, val_acc`) that satisfy both device limits, find the best `val_acc`, compute its binomial standard error `sqrt(p(1−p)/n_val)`, and return the name of the **smallest** (then fewest macs, then name) row whose `val_acc` is within one standard error of the best. Raise `ValueError` if nothing is feasible. |

### D.2 Study and engineering requirements (mandatory)

- **Protocol before data.** A `PROTOCOL.md` committed *before* your first comparison run lists hypotheses (for example "distilled students beat hard-label students of equal size on shifted data"), the metric and test set for each, and the result that would refute it. Deviations are listed, not hidden.
- **Ablations**, each over **at least 5 seeds** of `make_task`: transfer-pool composition (clean only, shifted only, both), student feature dimension (2^7 to 2^13), bit width (2 to 8), ridge `alpha` (over two decades), and one more of your choice (for example per-class thresholds, a rank sweep, pruning granularity).
- **Uncertainty everywhere.** Every reported difference carries a standard error or an interval, and no ranking is claimed within one standard error.
- A frontier figure with **shifted** accuracy on the vertical axis and size and compute on the others, with clean accuracy shown for contrast.
- Deterministic, with all randomness seeded; at least **10 tests of your own** in `tests/test_member_*.py`; `experiments.py` regenerates every number and figure.

### D.3 Responsibility

Language identification gates which safety filter a message goes through. In the report, write one paragraph on who is harmed when short, misspelt or code-switched messages (typical of everyday speech and of speakers of minority languages) are misrouted more than formal text, how that interacts with compression, and what per-language and per-length breakdown you would require before shipping. Do not infer anything about real languages from this synthetic task.

### D.4 Optional enhancements

- A per-language error analysis showing which cousin pairs account for the loss.
- A device-limit sweep that plots the best achievable shifted accuracy as a function of the byte budget.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_task(seed)` returns labelled clean training texts (1,200), an unlabelled transfer pool (9,000 clean and 6,000 shifted), 150 labelled shifted validation texts and 3,000 labelled test texts each of the clean and shifted kinds; `train_teacher(task)` returns the teacher `(W, b)`; `vectorizer(n)` is the hashing featuriser; `avg_active(texts)` measures non-zero features per message |
| **Provenance** | **Synthetic**: eight fictional languages generated from fixed syllable inventories in four cousin pairs (each pair shares about 70% of syllables). No real language, speaker or message is represented, and nothing about real languages should be concluded from the results |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Shift** | Clean: 3 to 9 words, 4% character noise. Shifted: 1 to 4 words, 15% noise, about 15% of words from a random other language |
| **Teacher** | Multinomial logistic regression on 2^16 hashed character 1 to 4-grams; 2,097,152 bytes as a dense float32 matrix (about 0.64 MB under the R2 cost model, because hashed features never seen in training have exactly-zero weights and sparse storage wins). Training takes under half a minute |
| **Device limits (public tests)** | 10,000 bytes and 2,000 multiply-adds per message |
| **Size** | Nothing committed; `python resources/datagen.py --out DIR` writes a small preview |

Hidden tests use other seeds and other device limits (for example 20 KB and 1,000 multiply-adds).

**Setup**

```bash
cd assessments/ml-engineering/tier-3/units/ML-11-efficient-ml-and-optimization/ML-T3-021-two-megabytes-eight-languages
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `langsqueeze/` package | Instruments (R1 to R3), candidate builder and selection rule (R4, R5) |
| 2 | `PROTOCOL.md`, committed before the first comparison run | Hypotheses, metrics, refutation criteria; checked against commit history |
| 3 | `tests/test_member_*.py` (at least 10 tests) | Includes a Pareto brute-force check and a cost-model audit |
| 4 | `experiments.py` | Reproduces all ablations (5 or more seeds) and the frontier figure |
| 5 | `REPORT.md` (at most 3,000 words plus tables), from the [template](submission-template/REPORT.md) | Study report and deployment recommendation; carries the AI-use declaration |
| 6 | A 10-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `pareto_front`, `cost_model`, `distill_ridge` and `choose` match the hand-computed values and, in the hidden tests, brute-force checks and other specs.
3. ⚙ `build_candidates` returns at least 8 honest candidates from at least 3 families, including the float32 teacher; the frontier of size, compute and **shifted** accuracy has at least 3 points.
4. ⚙ **Deployability.** Under the 10 KB and 2,000 multiply-add limits, the model returned by `choose` has clean accuracy at least **0.94** and shifted accuracy within **0.08** of the teacher's. *Justification:* the reference's chosen model reaches about 0.98 clean and loses about 1 to 2 points on shifted data, while the smallest students lose 6 to 7; the 150-sample validation set (standard error near 4 points) can steer a one-standard-error rule towards a smaller model, so 0.08 admits that choice without admitting the broken ones (the low-rank candidates lose 20 to 35 points). The hidden seeds and limits use 0.09 and 0.93.
5. ⚙ The teacher's shifted accuracy is at least 15 points below its clean accuracy, confirming the shift is present in the data you are tested on.
6. ✍ `PROTOCOL.md` predates the comparison runs in the commit history, lists refutation criteria, and the report states which hypotheses were refuted.
7. ✍ Each ablation has at least 5 seeds with intervals; claims are limited to differences exceeding the noise, and null results are reported as such.
8. ✍ The report contains a validity section covering at least: synthetic data, a 150-message validation set, one shift type, and what a real deployment would need to check.

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

1. **Create your own private repository** named `clbg-ML-T3-021-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `langsqueeze/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Better students.** Replace ridge-on-logits by a temperature-scaled soft-label cross-entropy student and test whether it beats ridge beyond the noise.
2. **Shift taxonomy.** Separate the three shift components (length, noise, code-switching) and find which one drives the loss for each family.
3. **Calibrated abstention.** Add a reject option that routes low-confidence messages to a conservative filter and plot coverage against shifted accuracy.
4. **Structured pruning.** Prune hashed feature columns instead of individual weights and re-derive the cost model.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why a distilled student cannot be better than its teacher on the transfer set and what could still make it better on test data; (2) ask you to explain from your own ablations which factor moves shifted accuracy most and how sure you are, given the standard errors; (3) give an unseen modification, for example a byte budget of 4 KB or a new shift type with heavy transliteration, and ask which candidates leave the frontier and why.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Linear models on hashed features, ridge regression, quantisation and pruning basics, binomial standard errors. No deep-learning background. |
| **New skill developed** | Running a compression study as an experiment: protocol first, controls, noise-aware conclusions, and a recommendation under device limits. |
| **Decisions the member must make** | Which families to include; the objectives on the frontier; transfer-pool composition; ablation ranges; how much shifted-accuracy loss is acceptable; how to use a 150-sample validation set. |
| **What must be investigated independently** | Whether distillation helps at all in this setting; why low-rank factorisation of an 8-class model is both larger and worse than the alternatives; how the transfer pool's composition shapes student behaviour on shifted text. |
| **Why it is interesting** | Clean accuracy says compression is free. Shifted accuracy says it is not, and the ranking of methods can change with the traffic they are tested on. |
| **Evidence of competence** | Exact instruments, honest candidates, a model that meets the limits on re-seeded tasks, and a protocol-first study with calibrated claims. |
| **Misconceptions exposed** | 'Distillation always beats training small.' 'Low-rank saves bytes.' (here it costs bytes and accuracy) 'Fewer bytes at equal accuracy means equal quality.' 'A validation set of 150 can pick the best model.' |
| **Preparation for later work** | Leads into ML-12 serving and rollout (a smaller model still needs a safe rollout) and ML-14 responsible ML (subgroup performance under shift). |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
