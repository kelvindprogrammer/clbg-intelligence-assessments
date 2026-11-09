# ML-T3-013: Which Roof, and Whose Village? Label-Efficient Roof Mapping with Honest Spatial Validation

> *A rural electrification planner can label about 90 aerial tiles from ten villages. Learn from thousands of unlabelled ones, and say how far a 90 percent claim can be trusted.*

![Format: Open-ended (secondary: Investigation)](https://img.shields.io/badge/format-open-ended-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-013` |
| **Title** | Which Roof, and Whose Village? Label-Efficient Roof Mapping with Honest Spatial Validation |
| **Subtrack** | ML Engineering |
| **Tier** | 3: Advanced and Research-Grade |
| **Unit** | [ML-07: Computer Vision](../README.md) |
| **Format** | Open-ended (secondary: Investigation) |
| **Difficulty** | Technical 4 · Mathematical 2 · Research 4 · Engineering 3 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 24–32 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Logistic regression and k-means in scikit-learn; cross-validation; image arrays; the idea of dataset shift. Recommended: ML-T2-014 and ML-05 Tier 2 |
| **Skills developed** | Spatially blocked validation; cluster bootstrap intervals; unsupervised patch-dictionary features; nuisance removal by local white balance; label-efficiency curves; ablation design; stating the validity limits of a synthetic study |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

The Rural Energy Access Programme (fictional) plans solar mini-grids. Metal-sheet roofs can host panels, thatch cannot, and concrete tile sits in between. Ground surveys that label a roof cost money, but aerial imagery is cheap: the programme has thousands of unlabelled 20 by 20 pixel colour tiles from 30 villages, and can pay surveyors to label about **90 tiles in ten villages** (30 per class is a typical plan). The director asks four questions and wants a recommendation she can defend to funders:

1. How accurate will a roof classifier be in villages nobody surveyed?
2. How much of the accuracy a standard tile-level split reports is real?
3. Can the thousands of unlabelled tiles help, and if so how?
4. How many labels are enough, and is a 90 percent claim defensible?

The tiles come from a generator in which every village has its own lighting gain, colour tint, ground colour, sensor noise and a dominant roof material (80 percent of its roofs). Roofs are drawn on bare ground: corrugated metal has regular ridges, thatch a fine brown texture, concrete flat grey with coarse seams. You are not told which village effects matter or how to remove them. Reading the generator is permitted, but your report must show how an analyst without it could have found each effect from data.

This is deliberately open: the tests fix interfaces and minimum bars; the study design (what to compare, which budgets, which ablations), the feature design and the claims you make are yours. Strong submissions behave like a short research report: baselines, ablations, intervals and a clear statement of what the synthetic evidence cannot show.

> **Why this matters beyond this task.** Remote-sensing and survey data are spatially clustered. Tile-level splits, tile-level intervals and tile-level claims are the most common way geospatial machine-learning results turn out to be wrong in the field.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Design** a spatially blocked evaluation and measure how much a random tile split overstates accuracy.
2. **Quantify** uncertainty with a cluster bootstrap over villages, and explain why the effective sample size is about the number of villages.
3. **Learn** features from unlabelled tiles (patch dictionary) and compare them with raw pixels and with nuisance-normalised variants.
4. **Identify** the nuisance structure (village lighting, tint, ground colour) from data and test whether removing it helps and what it costs.
5. **Plan** a label budget from a label-efficiency study and state what the evidence does and does not support.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `roofmap` in [`starter/roofmap/`](starter/roofmap/). Interfaces are fixed. Use only numpy and scikit-learn. The patch normalisation for R3 and R4 is: subtract the mean of each flattened patch (over positions and channels) and divide by `sqrt(mean(patch**2) + 0.01)`.

| ID | Requirement |
|---|---|
| **R1** | `village_block_split(village, test_frac, seed) -> (train_idx, test_idx)`: whole villages go to one side; exactly `max(1, round(test_frac * n_villages))` villages are held out; both index arrays are sorted and deterministic given `seed`. |
| **R2** | `cluster_bootstrap_ci(correct, groups, n_boot=1000, seed=0, alpha=0.05) -> (mean, lo, hi)`: the pooled mean of the 0/1 array and a percentile interval obtained by resampling whole groups with replacement and recomputing the pooled mean. |
| **R3** | `patch_dictionary(images, n_atoms, patch=5, seed=0)`: k-means atoms of shape `(n_atoms, patch*patch*3)` over normalised patches (a subsample of at most 15,000 patches, stride 2). |
| **R4** | `encode(images, dictionary, patch=5)`: for each stride-1 patch compute the normalised patch's distance to every atom, activation `max(0, mean_distance - distance)`, and average activations over the four image quadrants, returning `(n, 4 * n_atoms)`. Adding a constant to every pixel must not change the output. |
| **R5** | `fit_roof_classifier(X_lab, y_lab, g_lab, X_unlab, seed=0)` returns a model with `predict`, `predict_proba`, `chosen_` and `report_`: at least three candidates, one `"raw_pixels_logreg"`, mapping to **village-blocked** cross-validated accuracy on the labelled set. `X_unlab` is unlabelled and may come from any villages except the held-out ones. |

### D.2 Engineering requirements (mandatory)

- Deterministic: explicit seeds everywhere.
- No statistic (dictionary, normalisation constants, scaler) may be computed from held-out villages.
- At least **10 tests of your own** in `tests/test_member_*.py`, including a leakage test (a model must not be able to recover village identity better after your normalisation than before, or you must document why) and a test that your cluster bootstrap is wider than a tile-level bootstrap on clustered data.
- `experiments.py` regenerates every number and figure: random-split versus village-blocked accuracy; a label-efficiency curve (at least 10, 20, 30 and 50 labels per class, at least 5 label draws each) for at least three methods; and at least three ablations of your own design.
- `REPORT.md` (at most 2,500 words plus tables) written as a technical memo with a separate validity section.

### D.3 Responsibility

The tiles are synthetic and show no real settlement. Real roof-mapping maps people's homes: write one paragraph on consent and community engagement, on the risk that a roof-material map is read as a wealth map and used to exclude households, and on who should hold and see such a map.

### D.4 Optional enhancements

- A small convolutional network with augmentation, if PyTorch is available, compared on equal label budgets.
- An active-learning loop that chooses which villages to survey next, evaluated by the learning curve.
- A test of spatial autocorrelation in the residuals.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_tiles(n_villages=24, per_village=40, seed=0)` returns `X (N,20,20,3)`, `y (N,)` (0 metal, 1 thatch, 2 concrete) and `village (N,)`; `label_budget(...)` draws a labelled set |
| **Provenance** | **Synthetic**, procedurally drawn and deterministic given the seed; no real imagery or settlement |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Public protocol** | 30 villages of 40 tiles (seed 0); 10 held-out villages; 10 label villages with 30 labelled tiles per class; 600 unlabelled tiles |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes an `.npz` of about 0.5 MB |

Hidden tests use other seeds, other label budgets (25 to 40 per class) and other held-out villages.

**Setup**

```bash
cd assessments/ml-engineering/tier-3/units/ML-07-computer-vision/ML-T3-013-which-roof-and-whose-village
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `roofmap/` package | Blocked splits, cluster intervals, patch features and the classifier |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Includes the leakage and interval-width tests |
| 3 | `experiments.py` | Reproduces the random-versus-blocked gap, the label-efficiency curves and the ablations |
| 4 | `REPORT.md` (at most 2,500 words plus tables), from the [template](submission-template/REPORT.md) | Memo to the director plus a validity section; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `village_block_split` never splits a village, holds out the right number of villages and is deterministic; `cluster_bootstrap_ci` returns the exact pooled mean, is deterministic, is much wider than a tile-level interval on perfectly clustered data and collapses to a point for constant outcomes.
3. ⚙ `patch_dictionary` and `encode` have the right shapes, are finite and non-negative (`encode`), invariant to a uniform brightness offset and row-independent.
4. ⚙ `report_` has at least three candidates including `raw_pixels_logreg`, `chosen_` is a key and the reported blocked estimate for the chosen model is not more than 0.15 above its accuracy on unseen villages.
5. ⚙ **Performance.** On the public protocol accuracy on the ten held-out villages is at least **0.82** and at least **0.12** above a raw-pixel logistic regression trained on the same labels. *Justification:* the reference reaches about 0.86 to 0.96 across eight draws against 0.5 to 0.75 for raw pixels; with ten test villages the accuracy varies by about ±0.05, so the bar sits below the reference minimum.
6. ⚙ **Robustness.** On three hidden re-seeded worlds with 25 to 40 labels per class the accuracy bar is 0.78.
7. ✍ The report quantifies the gap between a random tile split and a village-blocked split of the same labelled set, with intervals.
8. ✍ The label-efficiency study covers at least four budgets and five draws per budget for at least three methods, and states where each method stops improving and how many labels a raw-pixel classifier would need.
9. ✍ At least three ablations isolate which element (dictionary, white balance, centre statistics, unlabelled pool size) delivers the gain, including one that tests whether the model now leans on ground colour.
10. ✍ A validity section states what the synthetic design can and cannot show about real imagery.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 15 |
| Implementation quality | 10 |
| Methodology and evidence | 25 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T3-013-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `roofmap/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `experiments.py`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Label-selection strategy.** Compare random label selection with spreading labels across more villages for a fixed budget.
2. **Transfer.** Train on villages with one dominant material and test on villages with another; discuss when the method fails.
3. **Uncertainty.** Calibrate predicted probabilities and use abstention to route uncertain tiles back to surveyors.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why your random-split number is higher than your village-blocked number and which one you would put in a funding proposal; (2) ask how many independent observations your accuracy estimate really rests on; (3) give an unseen change, for example a village with a white-painted thatch roof or a budget cut to 10 labels per class, and ask which results change and why.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Using scikit-learn classifiers and k-means; the idea of cross-validation; bootstrap. No CNN theory. |
| **New skill developed** | Designing a study whose validity does not depend on tiles being independent, and arguing what the evidence supports. |
| **Decisions the member must make** | Evaluation protocol; which methods and budgets to compare; how to use unlabelled tiles; how to remove village nuisance; what ablations answer the director's questions. |
| **What must be investigated independently** | Which village effects drive the errors, how large the random-split optimism is, and how many labels are enough. |
| **Why it is interesting** | The headline gain comes from a one-line white-balance idea, not from a bigger model, and a random split would have hidden that by flattering the baseline. |
| **Evidence of competence** | Held-out-village accuracy above the bar on re-seeded worlds, a reproduced random-versus-blocked gap, and ablations that attribute the gain. |
| **Misconceptions exposed** | 'Random k-fold is fine for images.' 'Tile-level intervals are valid.' 'More labelled tiles from the same villages is as good as more villages.' |
| **Preparation for later work** | Leads into ML-05 evaluation design, ML-07 segmentation and detection work, and responsible geospatial AI in AI-13. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
