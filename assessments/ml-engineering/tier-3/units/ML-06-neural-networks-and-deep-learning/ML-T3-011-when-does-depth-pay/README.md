# ML-T3-011: When Does Depth Pay?

> *A cooperative asks whether to buy GPUs. You have a laptop and a research question.*

![Format: Investigation](https://img.shields.io/badge/format-investigation-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-011` |
| **Title** | When Does Depth Pay? A Controlled Study of Neural Networks Versus Boosted Trees on Small Agricultural Tables |
| **Subtrack** | ML Engineering |
| **Tier** | 3: Advanced Practice and Research Readiness |
| **Unit** | [ML-06: Neural Networks and Deep Learning](../README.md) |
| **Format** | Investigation |
| **Difficulty** | Technical 4 · Mathematical 3 · Research 5 · Engineering 3 · Ambiguity 5 · Resources 2 (each out of 5) |
| **Estimated time** | 24–36 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | Neural-network training, gradient boosting, AUC and bootstrap intervals; ML-T2-012 is a good preparation. |
| **Skills developed** | Controlled experiment design for model comparison; fair tuning budgets; replication across seeds; paired inference; scoping claims |
| **Technologies** | Python 3.10+, numpy, pandas, scikit-learn, pytest |

---

## B. Problem Statement

A state agricultural extension programme in northern Nigeria classifies smallholder plots as **fertile or not fertile** from soil and weather features, to decide who receives subsidised fertiliser. Today it uses logistic regression in a spreadsheet. A donor has offered funding for "a modern deep-learning stack with GPUs", and the programme director has asked a simple question: *will it be worth it?* Plot tables here are small: a typical district has 150 to a few thousand labelled plots, and several recorded features are known to be uninformative.

Published studies suggest that on small tabular data gradient-boosted trees often match or beat neural networks, and that networks catch up when relationships are smooth, rotation-invariant or when data is plentiful. You cannot lean on that literature blindly: your tables are not their tables. You are given three synthetic **task families** in which the truth is known and controllable (`tasks.py`): **smooth** interactions (favouring networks), **axis-aligned** thresholds (favouring trees) and **rotated** thresholds (the tree-friendly rule, seen through a random rotation). Each has 6 informative and a configurable number of pure-noise features, and 5% label noise.

Design and run a controlled study on a laptop CPU that answers: *under which conditions, if any, does a small numpy neural network earn its place over boosted trees and logistic regression?* Then recommend what the programme should do. The question is deliberately under-specified. You decide which factors to vary (sample size, number of noise features, label noise, task family), how much tuning effort each model deserves, how many seeds are enough, and what claims the evidence supports. The assessor checks the code against fixed behaviour but marks the study design and the recommendation by hand against the rubric.

## C. Objectives

When you finish, you should be able to show that you can:

- Frame a precise, testable research question and the factors, controls and confounds of a model comparison.
- Allocate tuning effort fairly across a neural network, boosted trees and a linear model.
- Replicate over seeds and use paired intervals to separate real differences from noise.
- Locate regime boundaries such as the training size at which one model overtakes another, and say when no clean crossover exists.
- Distinguish what a synthetic generator builds in from what is likely to transfer to real plot data.
- Write a recommendation whose scope is clearly bounded by the evidence.

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `regimes` in [`starter/regimes/core.py`](starter/regimes/core.py). `tasks.py` (the task families) and `nn_core.py` (a working numpy MLP with Adam) are provided; do not modify `tasks.py`. No deep-learning framework; scikit-learn is allowed for `gbm` and `logreg`.

| ID | Requirement |
|---|---|
| **R1** | `fit_predict(model_name, Xtr, ytr, Xte, seed)` for `'mlp'`, `'gbm'`, `'logreg'`: returns probabilities for `Xte`; deterministic; any tuning uses only a validation split carved from the training data; unknown names raise `ValueError`. The MLP design (width, depth, weight decay, early stopping, learning rate) is yours. |
| **R2** | `run_study(kinds, sizes, seeds, n_noise, models, n_test)`: trains on the first `n` rows of `make_task(kind, n + n_test, seed, n_noise)` and returns test AUC in a tidy DataFrame `['model', 'kind', 'n', 'seed', 'auc']`. |
| **R3** | `paired_summary(df, a, b, n_boot, seed)`: pairs models by seed (not by row position) and returns `['kind', 'n', 'mean_diff', 'lo', 'hi', 'n_seeds']` with a 95% percentile bootstrap interval over seeds. |
| **R4** | `crossover(summary, kind)`: the smallest `n` from which model `a` wins at every larger `n`; `None` if it never does or the win flips back. Independent of row order. |
| **R5** | The study (`study/` scripts) and `REPORT.md`: a pre-stated research question and hypotheses; an experimental design table (factors, levels, seeds, budget); main results with paired intervals; **at least three ablations/controls** that test why a result occurs (for example: equal tuning budgets, number of noise features, label noise, or rotating the smooth task); a "what would change my mind" paragraph; and a recommendation to the director. |

### D.2 Engineering requirements (mandatory)

- Everything in `REPORT.md` is regenerated by `study/run_all.py` in under 30 minutes on a laptop CPU (cache intermediate results in `study/results/` and commit them).
- Seeds, versions and the tuning budget given to each model are recorded. A model may not have more tuning effort than the others without that being declared and analysed.
- Keep the provided tests passing and add **at least 8 tests of your own**, including pairing, determinism and a regression test for `crossover`.
- No test-set information may influence tuning. Test AUC is computed once per configuration.

### D.3 Privacy and responsibility

The data is **synthetic**; no farmer or plot is described. Fertiliser subsidy models decide who receives scarce support, so false negatives are not neutral. In `REPORT.md`, state who is harmed by a missed fertile plot versus a wrongly subsidised one, why you would pilot with a human override, and what the Nigeria Data Protection Act 2023 implies for plot-level data tied to named farmers.

---

## E. Dataset and Resources

All data is **synthetic**, drawn on the fly by the deterministic generator `starter/regimes/tasks.py` (no data files are committed). Licence: MIT for code, CC BY 4.0 for text.

| Resource | Content |
|---|---|
| `tasks.make_task(kind, n, seed, n_noise, label_noise)` | Three task families with known structure; 6 informative features plus `n_noise` noise columns; 5% label noise by default. |
| `nn_core.MLP` | A working binary MLP (ReLU, sigmoid output, Adam, sample weights). |

A full study of three kinds, four sizes, five seeds and three models runs in a few minutes on a laptop. Real plot data would differ: feature correlations, missingness, spatial structure and drift are absent here, and your report must say so.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `regimes/` (completed starter) | Tuned models and study utilities |
| 2 | `study/` with `run_all.py` and saved results | The experiments behind the report |
| 3 | `tests/test_member_*.py` (at least 8 tests) | Tests for pairing, determinism and crossover logic |
| 4 | `REPORT.md` (at most 3,000 words plus figures), from the [template](submission-template/REPORT.md) | Research report and recommendation; includes the AI-use declaration |
| 5 | A 10-minute live defence | Probes design choices, controls and claims (§K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Criteria marked ⚙ are checked automatically by the public and hidden test suites; the rest are checked by hand.

1. ⚙ Public and your own tests pass from a clean environment.
2. ⚙ Hidden test, fresh seeds (40-42), training sizes 150 and 1,500, 6 noise features: the gradient-boosted model beats your MLP on the axis-aligned family at n = 1,500; your MLP reaches AUC at least 0.80 on the smooth family at n = 1,500 and is within 0.04 of boosted trees; logistic regression is at least as good as boosted trees on the rotated family at n = 150; more data helps both non-linear models. *Justification:* the reference gives axis 0.83 vs 0.75, smooth 0.83 vs 0.83, rotated n = 150 0.71 vs 0.66; each is a structural property of the generator, not of a particular implementation.
3. ⚙ `paired_summary` pairs by seed and gives a collapsed interval when the paired differences are constant; `crossover` equals a brute-force definition on random summaries in any row order.
4. ✍ The report states a research question, hypotheses and a design table before showing results, and a result that contradicts a hypothesis is reported as such.
5. ✍ At least three controls or ablations isolate *why* a result occurs, including at least one on tuning budget fairness.
6. ✍ Claims are scoped: each is labelled as supported by the experiments, plausible but untested, or unsupported, and none extends to real plot data without an argument.
7. ✍ The recommendation to the director is actionable, conditional on conditions the programme can check (data size, feature types), and costs the GPU purchase honestly.
8. ✍ Every figure and number regenerates from `study/run_all.py`.

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

1. **Create your own private repository** named `clbg-ML-T3-011-<your-github-username>` from this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `regimes/` (your package), `tests/` (provided tests plus your own `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `study/` (scripts and saved results), `REPORT.md` (from the template, including the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core requirements.

1. Fit a learning curve for each model and extrapolate the training size at which the MLP would overtake boosted trees on the smooth family; judge the extrapolation against a larger run.
2. Add a fourth family you design (for example features with strong correlations or missing values) and test whether your recommendation survives.
3. Replace the MLP with an ensemble of five MLPs and estimate how much of the gap to boosted trees is variance.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn (explain a concept, review your code). **They may not do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: tool, purpose, example prompt, how you verified the output. Undisclosed use that emerges at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code or method adapted from documentation or papers, with a link.
- **Collaboration:** discuss *general techniques* only. Do not share code, numbers or report text.
- **Verification of understanding.** In the short defence the assessor will show you a figure from your own report with the intervals hidden and ask what you would conclude; ask which control would most change your recommendation; and give you a new factor (for example 40 noise features) to predict, then run it live and compare.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Training MLPs and boosted trees, AUC, bootstrap intervals, and basic experimental design. |
| **New skill developed** | Running a fair, controlled model comparison as research: factors, budgets, replication, paired inference and scoped claims. |
| **Decisions the member must make** | The research question, the factors and levels, the tuning budget for each model, the number of seeds, the controls, and the recommendation to a non-technical director. |
| **What must be investigated independently** | Where the MLP is competitive, why, and whether the answer depends on tuning effort, sample size, noise features or rotation. |
| **Why it's interesting** | A funding decision rides on a question the literature answers only in general, and the answer here is: it depends, in ways you can measure. |
| **Evidence of competence** | Correct, tested study utilities; a pre-stated design; ablations that isolate mechanisms; honest, scoped conclusions; regenerable results. |
| **Misconceptions exposed** | "Deep learning always wins." "Trees always win on tabular data." "One seed is a result." "Tuning the favourite model harder is a fair comparison." |
| **Preparation for later work** | Leads into research-style projects, experiment tracking (ML-11), and capstones that compare model families. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
