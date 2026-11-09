# ML-T2-014: The Camera the Farmer Actually Owns: Leaf-Disease Triage Under Camera Shift

> *A maize disease classifier is trained on good photos and will run on cheap phones. Make it work on the camera that matters, with 90 labelled field photos to go on.*

![Format: Investigation (secondary: Comparative)](https://img.shields.io/badge/format-investigation-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-014` |
| **Title** | The Camera the Farmer Actually Owns: Leaf-Disease Triage Under Camera Shift |
| **Subtrack** | ML Engineering |
| **Tier** | 2: Applied Engineering and Independent Problem-Solving |
| **Unit** | [ML-07: Computer Vision](../README.md) |
| **Format** | Investigation (secondary: Comparative) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14–20 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Logistic regression and random forests at the level of using scikit-learn; macro-averaged F1; image arrays in numpy. Recommended: ML-T1-015 |
| **Skills developed** | Diagnosing dataset shift between cameras; photometric augmentation; exposure-invariant features; selecting a model on a tiny target-domain validation set; per-class and per-domain reporting |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Savanna Agro Extension (a fictional programme) wants a phone app that tells smallholder maize farmers whether a leaf looks **healthy**, shows **blight** (a few large dark-brown lesions) or **rust** (many tiny orange pustules). The model was developed on photos taken by programme staff with a good camera in even light. Farmers will use cheap phones outdoors: the photos are darker, tinted, softer and noisier.

You have 400 labelled lab images and 90 labelled field images (a small validation set you may also learn from). A hidden test uses many more field images. The programme's previous attempt trained a logistic regression on raw pixels using lab data only. It scored 0.36 macro-F1 on field photos: it called almost everything one class.

Four complications are built in:

1. **Camera shift.** Field photos are darker (by 20 to 60 percent), have a colour cast, are blurred and carry more noise. The shift is not described numerically; you must characterise it from the 90 field images.
2. **Tiny target validation.** 90 images (about 30 per class) cannot separate models that differ by a few points. Choosing among candidates from it is itself a risk.
3. **Confusable evidence.** Healthy leaves sometimes carry dust specks that look like rust pustules, and blur erases small pustules. Aggressive blur augmentation can therefore hurt.
4. **Do no harm to the lab camera.** The programme keeps using the lab camera for training events; a model that is good on field phones but worse on the lab camera is not acceptable.

The task is partially specified: the tests fix interfaces and acceptance bars; the augmentation recipe, the features, the model family and the way you use the 90 field images are yours to choose and defend.

> **Why this matters beyond this task.** Most deployed vision models fail on the camera nobody trained on. Deciding what the deployment device looks like, simulating it, and measuring on it honestly is the core applied-vision skill.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Diagnose** a failure as dataset shift, with per-camera and per-class evidence, before changing the model.
2. **Design** augmentation that mimics the target camera and show each component's contribution.
3. **Engineer** per-image features that are robust to exposure and colour cast, without batch statistics.
4. **Select** a model using 90 target-domain images, and quantify how much that selection can be trusted.
5. **Report** results per camera and per class, and show the lab camera has not regressed.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `leafscout` in [`starter/leafscout/`](starter/leafscout/). Interfaces are fixed; design choices are yours. Use only numpy and scikit-learn.

| ID | Requirement |
|---|---|
| **R1** | `augment(images, rng, copies=3)` returns `copies * n` altered images (copy `k` of image `i` at row `k*n + i`), values clipped to [0, 1], without mutating the input and deterministic given the `numpy` generator. Augmented images must stay recognisably the same leaf and, on average, be at least 15 percent darker than the lab originals. |
| **R2** | `extract_features(images)` returns a finite `(n, d)` matrix with `d <= 200`. Each row may depend only on its own image (no batch statistics). |
| **R3** | `confusion_matrix(y_true, y_pred, k=3)` (rows are true classes), `macro_f1(y_true, y_pred, k=3)` (a class with no support and no predictions scores 0) and `per_class_recall(y_true, y_pred, k=3)`. |
| **R4** | `fit_triage(X_lab, y_lab, X_val, y_val, seed=0)` returns a model with `predict`, `predict_proba`, `chosen_` and `report_`: a dict of at least three candidates, one of which is `"raw_pixels_logreg"` (raw pixels, lab data only), mapping to macro-F1 on the field validation set. You decide candidates, augmentation, and whether the final model also learns from `X_val`. |

### D.2 Engineering requirements (mandatory)

- Deterministic: every random choice uses an explicit generator or `random_state`.
- No fitting, scaling or selecting with test images; augmentation is applied to training data only.
- At least **8 tests of your own** in `tests/test_member_*.py`, including a non-mutation test for `augment` and a row-independence test for `extract_features` and `predict`.
- `experiments.py` regenerates every number in `REPORT.md`: per-camera and per-class results over **at least 5 seeds** of the generator, an ablation of the augmentation components (gain, colour cast, blur, noise) one at a time, and a bootstrap interval for the validation comparison.

### D.3 Responsibility

The data are synthetic. Write one paragraph on what a wrong 'healthy' verdict costs a farmer (a missed treatment window) and what a wrong 'blight' verdict costs (unnecessary fungicide spending), which error you chose to minimise, and how you would check that the model works across the phone models and lighting conditions of different regions rather than only the ones in the training pool.

### D.4 Optional enhancements

- A cost-weighted decision rule where missing blight costs three times a false alarm.
- A drift monitor that flags when incoming photos look unlike the training pool using the features alone.
- Test-time augmentation and its effect on the weakest class.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_leaves(n=300, seed=0, camera='lab' | 'field')` returns `images (n,24,24,3)` in [0,1] and `labels (n,)` with 0 healthy, 1 blight, 2 rust |
| **Provenance** | **Synthetic**, procedurally drawn and deterministic given the seed; no real plant, farm or photograph |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Public protocol** | Train on 400 lab images (seed 1), validate on 90 field images (seed 2), test on 600 field images (seed 3) |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes two small `.npz` files (about 1 MB each) |

Hidden tests use other seeds, a validation set of 60 images, and a test on the lab camera.

**Setup**

```bash
cd assessments/ml-engineering/tier-2/units/ML-07-computer-vision/ML-T2-014-the-camera-the-farmer-actually-owns
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `leafscout/` package | Augmentation, features, metrics and model selection |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Includes non-mutation and row-independence tests |
| 3 | `experiments.py` | Reproduces the tables, ablation and figures (5 or more seeds) |
| 4 | `REPORT.md` (at most 1,600 words plus tables), from the [template](submission-template/REPORT.md) | Decision memo for the programme lead; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `augment` honours shape, range, determinism and non-mutation, keeps image identity (each copy correlates with its source more than with another image) and darkens by at least 15 percent on average.
3. ⚙ `extract_features` is finite, at most 200 columns and row-independent; `macro_f1`, `confusion_matrix` and `per_class_recall` match hand-computed values.
4. ⚙ `report_` has at least three candidates including `raw_pixels_logreg`, and `chosen_` is a key.
5. ⚙ **Performance.** On the public field test set (600 images) macro-F1 is at least **0.85**, at least **1.5 times** that of a raw-pixel logistic regression trained on the lab images, and the weakest class has recall at least **0.75**. *Justification:* the reference reaches about 0.95 against a baseline of 0.36; the bars leave room for simpler but reasonable pipelines.
6. ⚙ **Robustness.** On hidden seeds with a 60-image validation set the macro-F1 bar is 0.82 and 1.4 times the baseline; on the lab camera macro-F1 stays at least 0.85.
7. ⚙ Predictions for an image do not change when the batch is reordered or truncated.
8. ✍ The report diagnoses the failure per camera and class, and shows with the ablation how much each augmentation component and the feature design contributes.
9. ✍ The report quantifies the uncertainty of choosing among candidates with 90 validation images and says how that affected the choice.

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

1. **Create your own private repository** named `clbg-ML-T2-014-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `leafscout/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `experiments.py`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Camera estimation.** Estimate the field camera's gain, cast and blur from the 90 images and drive the augmentation from the estimates; compare with hand-set ranges.
2. **Second camera.** Add a different shift (for example over-exposed) and test whether your recipe generalises.
3. **Small CNN.** If you have PyTorch, train a small CNN with the same augmentation and compare it with your classical pipeline on accuracy and cost.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why the baseline fails on field photos and what the evidence for that is; (2) ask whether the gap between your top two candidates on the 90 validation images is larger than the noise; (3) give an unseen change, for example a second phone model that over-exposes, and ask which part of your pipeline you would change first.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Using scikit-learn classifiers; macro-F1; image arrays. No CNN theory. |
| **New skill developed** | Simulating a deployment device with augmentation and verifying the result on a small target-domain sample. |
| **Decisions the member must make** | Which shift components to simulate and how strongly; hand features or raw pixels; which model; whether to refit on the validation images; how to report uncertainty. |
| **What must be investigated independently** | What the field camera does to the images and which components of the shift cost the most accuracy. |
| **Why it is interesting** | The largest gain comes from teaching the model what the farmer's camera looks like, not from a bigger model, and the brief never says so. |
| **Evidence of competence** | Field macro-F1 above the bar on re-seeded data, lab performance preserved, and an ablation that attributes the gain. |
| **Misconceptions exposed** | 'High lab accuracy means deployment accuracy.' 'More augmentation is always better.' 'Pick the best of four on 90 images.' |
| **Preparation for later work** | Leads into ML-07 Tier 3 label-efficiency and spatial validity, ML-05 evaluation and ML-10 drift monitoring. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
