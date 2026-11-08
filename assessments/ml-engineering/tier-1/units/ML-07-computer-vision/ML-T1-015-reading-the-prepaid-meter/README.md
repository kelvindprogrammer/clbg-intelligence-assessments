# ML-T1-015: Reading the Prepaid Meter: Convolution, Pooling and Gradient Histograms from Scratch

> *A utility wants phones to read the digits on prepaid-meter displays. Build the image operations by hand, then show why edges beat raw pixels.*

![Format: Implementation (secondary: Investigation)](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T1-015` |
| **Title** | Reading the Prepaid Meter: Convolution, Pooling and Gradient Histograms from Scratch |
| **Subtrack** | ML Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [ML-07: Computer Vision](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8–12 hours over 1 week |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 2 minutes |
| **Recommended prerequisites** | Python and numpy array slicing; what a classifier and an accuracy score are. No deep-learning library knowledge is needed |
| **Skills developed** | Sliding-window arithmetic (stride, padding, output size); convolution as cross-correlation; max pooling; Sobel gradients; orientation histograms; nearest-centroid classification; reject options |
| **Technologies** | Python 3.10+, numpy, pytest |

---

## B. Problem Statement

Savanna Power (a fictional utility) sells prepaid electricity. When a customer loads a token, field agents photograph the meter display to confirm that the credit appeared. Agents use cheap phones in poor light, so the photographed digit is dimmed, unevenly lit, noisy and rarely centred. The utility wants a tiny on-device reader that needs no deep-learning framework, and it asks you for the building blocks.

You will implement the primitives that every convolutional network is made of, in plain numpy: a **2-D convolution** (in the cross-correlation convention used by CNN libraries) with stride and zero padding, **max pooling**, **Sobel gradients**, and a **gradient-orientation histogram** feature (a simplified HOG). You will then use them in a **nearest-centroid digit reader** that can also refuse to answer when it is unsure.

The task is fully specified: every function has a precise contract and the tests check exact values. What makes it more than a coding exercise is the explanation you owe: a nearest-centroid reader on raw pixels scores about 0.49 on the same data, while the same reader on your features scores about 0.86. You must show *why* with an experiment, not an assertion.

Datasets are generated procedurally: 12 by 8 pixel seven-segment glyphs placed at a random offset (up to 2 pixels) in a 16 by 12 frame, scaled by a random brightness, lit by a vertical gradient and corrupted by Gaussian noise.

> **Why this matters beyond this task.** Convolution arithmetic, pooling and gradient features are the vocabulary of every vision system. Getting the output-size formula and the no-flip convention right by hand is what lets you debug a real network's shape errors later.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Compute** the output size of a sliding window for any kernel, stride and padding, and reject kernels that do not fit.
2. **Implement** 2-D convolution (cross-correlation), max pooling and Sobel gradients and verify them against an independent naive implementation.
3. **Build** a brightness-scale-invariant, shift-tolerant feature from gradient orientation histograms.
4. **Classify** with per-class centroids and add a margin-based reject option.
5. **Explain** with a controlled experiment why gradient histograms beat raw pixels under shift and noise, and where the reader still fails.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `meterlens` in [`starter/meterlens/`](starter/meterlens/). Interfaces are fixed. Use only numpy (scikit-learn, scipy, OpenCV and scikit-image are not allowed in the package).

| ID | Requirement |
|---|---|
| **R1** | `conv_output_size(n, k, stride=1, pad=0)` returns `(n + 2*pad - k)//stride + 1` and raises `ValueError` when the padded input is smaller than the kernel. `conv2d(img, kernel, stride=1, pad=0)` returns the cross-correlation (the kernel is **not** flipped) of the zero-padded image with the kernel, sampled every `stride` pixels. |
| **R2** | `maxpool2d(img, size, stride=None)` returns the maximum over each `size` by `size` window; `stride` defaults to `size`; incomplete windows at the border are dropped; no padding is added (an all-negative image must stay negative). |
| **R3** | `sobel_gradients(img)` returns `(gx, gy)`, the responses to the standard 3 by 3 Sobel kernels (`gx` responds to horizontal intensity change), with the same shape as `img`, using zero padding and your own `conv2d`. |
| **R4** | `hog_features(img, cell=4, bins=8)` computes gradient magnitude and *unsigned* orientation (`arctan2(gy, gx)` modulo pi), splits the image into non-overlapping `cell` by `cell` cells, accumulates a magnitude-weighted orientation histogram of `bins` bins in each, concatenates them row-major and L2-normalises the result. An all-zero image gives an all-zero vector, never NaN. |
| **R5** | `DigitReader` with `fit(images, labels)` (stores `classes_` and `centroids_`, one mean feature vector per class), `predict(images)` (nearest centroid in Euclidean distance) and `predict_with_reject(images, min_margin)` (returns -1 where the second-best distance minus the best distance is below `min_margin`). |

### D.2 Engineering requirements (mandatory)

- Python loops over *output positions* are fine; the inner window arithmetic must use numpy slicing. No vision or signal-processing library in the package.
- Deterministic: no hidden randomness in any function.
- At least **6 tests of your own** in `tests/test_member_*.py`, including one that compares `conv2d` with an independent implementation on random inputs and one that shows `conv2d` is not true convolution (an asymmetric kernel).
- `REPORT.md` (at most 900 words plus tables) answering the questions in the template, with the numbers produced by a short script you include.

### D.3 Responsibility

The data are synthetic and contain no real meter, customer or account number. In a real deployment, meter photographs can include account numbers and addresses: write two sentences on what you would crop, blur or discard before storage, referring to the Nigeria Data Protection Act 2023 principles of data minimisation and purpose limitation.

### D.4 Optional enhancements

- A vectorised `conv2d` using `sliding_window_view`, with a timing comparison and a correctness check.
- Show that Sobel is separable and that two 1-D passes equal your 2-D result.
- Overlapping cells or block normalisation, and its effect on accuracy.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_digits(n=600, seed=0, noise=0.25, max_shift=2)` returns `images (n,16,12)` and `labels (n,)` |
| **Provenance** | **Synthetic**, deterministic given the seed; no real meter, photograph or customer |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Public protocol** | Train on seed 1 (600 images), test on seed 2 (800 images), noise 0.25 |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes a compressed `.npz` of well under 1 MB |

Hidden tests use other seeds, a lower noise level, odd kernel shapes and a training set with a missing digit.

**Setup**

```bash
cd assessments/ml-engineering/tier-1/units/ML-07-computer-vision/ML-T1-015-reading-the-prepaid-meter
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `meterlens/` package | R1 to R5 implemented with numpy only |
| 2 | `tests/test_member_*.py` (at least 6 tests) | Includes the independent-implementation and no-flip checks |
| 3 | `analysis.py` | Reproduces the numbers and the shift-sweep figure in the report |
| 4 | `REPORT.md` (at most 900 words plus tables), from the [template](submission-template/REPORT.md) | Explanations and experiment; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `conv_output_size`, `conv2d` and `maxpool2d` agree with an independent implementation for stride 1 to 3, padding 0 to 2 and non-square inputs; invalid sizes raise `ValueError`.
3. ⚙ `sobel_gradients` has the right sign and magnitude on a step edge and respects the input shape.
4. ⚙ `hog_features` has the right length, unit norm, no NaN on a blank image, is unchanged when the image is multiplied by 3, and places vertical and horizontal stripe energy in the correct orientation bins.
5. ⚙ **Performance.** `DigitReader` reaches accuracy at least **0.80** on the public protocol and at least **1.4 times** the accuracy of a nearest-centroid reader on raw pixels. *Justification:* the reference reaches about 0.86 against 0.49; a bar of 0.80 leaves room for a different but reasonable cell size, and the ratio ensures the gain comes from the features.
6. ⚙ **Robustness.** On hidden seeds and noise 0.20 to 0.25 the accuracy bar is 0.78 (accuracy on 800 test images varies by about ±0.02 across seeds).
7. ⚙ `predict_with_reject` returns exactly `predict` at margin 0, rejects everything at a huge margin, and the accuracy on accepted images is higher than the overall accuracy at a moderate margin.
8. ✍ The report explains the output-size formula, why the kernel is not flipped, why gradient histograms tolerate a shift and a brightness change, and contains the shift-sweep experiment and an error analysis.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 15 |
| Methodology and evidence | 15 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 5 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T1-015-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `meterlens/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Strided pooling in features.** Pool the gradient magnitude by 2 before computing cells and report the accuracy and cost trade-off.
2. **Rotation.** Test how far the reader tolerates a 5 degree tilt and what you would add to survive it.
3. **Learned filters.** Replace Sobel with kernels learned by a tiny linear model and compare.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask you to compute the output shape and parameter count of a given convolution layer on paper; (2) ask why the reader survives a two-pixel shift and a dim photo and where it would not; (3) give an unseen change, for example 20 by 14 images or 6 bins, and ask what in your code and your results changes.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Numpy slicing, vector norms, the idea of a classifier. No CNN theory. |
| **New skill developed** | Reasoning about image operations as exact arithmetic on shapes and windows, and testing them against an independent implementation. |
| **Decisions the member must make** | How to structure the loops, how to handle a blank image, what to put in the shift-sweep experiment. |
| **What must be investigated independently** | Why gradient histograms are shift-tolerant and brightness-invariant, shown by experiment. |
| **Why it is interesting** | A reader built from forty lines of arithmetic beats raw pixels by a wide margin, and the member can see exactly why. |
| **Evidence of competence** | Exact values on hand-built cases, agreement with an independent implementation, and an accuracy gain that survives re-seeding. |
| **Misconceptions exposed** | 'Convolution flips the kernel in CNNs.' 'Pooling pads with zeros.' 'More pixels means better features.' |
| **Preparation for later work** | Leads into ML-07 Tier 2 robustness to camera shift, ML-06 CNN training and later detection work. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
