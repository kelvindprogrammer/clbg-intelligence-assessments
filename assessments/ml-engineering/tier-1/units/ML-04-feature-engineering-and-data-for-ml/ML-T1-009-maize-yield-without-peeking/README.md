# ML-T1-009: Maize Yield Without Peeking

> *Build the imputer, scaler, one-hot and target encoders yourself, so that nothing the model is tested on ever leaks into how it was trained.*

![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T1-009` |
| **Title** | Maize Yield Without Peeking: Leakage-Safe Preprocessing Built from Scratch |
| **Subtrack** | Machine Learning Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [ML-04: Feature Engineering and Data for ML](../README.md) |
| **Format** | Implementation (secondary: Debugging & Forensics) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 8-14 hours over 1-2 weeks |
| **Collaboration** | Individual |
| **Compute** | CPU only, 4 GB RAM, no GPU, no paid services, no internet after setup. The whole suite runs in about a minute |
| **Recommended prerequisites** | numpy masks and broadcasting; what a train/test split is; running `pytest`. No prior preprocessing-library knowledge is assumed. |
| **Skills developed** | Leakage-safe preprocessing; imputation; scaling; categorical encoding; out-of-fold target encoding; leakage testing |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

An agritech startup advises smallholder maize farmers in six states on seed and fertiliser choices. It holds 800 farm records: rainfall, soil pH, fertiliser rate, plot size, state, the supplier of the seed, and the yield in tonnes per hectare. About one rainfall reading in six is missing, and it is missing more often in dry places because farmers there are less likely to own a rain gauge. The seed supplier column has 40 distinct values, a few suppliers sell to hundreds of farms and many sell to only a handful. The startup's data scientist has built a model that looks excellent on the team's laptop, but it fails in the field, and the suspicion is that the preprocessing "peeked": statistics, encodings and even labels from the rows used for testing were allowed to influence the training features.

Your task is to build the preprocessing components from scratch, in numpy, with a precise specification, and to assemble them into a pipeline that provably does not peek. You will implement a median imputer that records which values were missing, a standard scaler, a one-hot encoder that survives categories it has never seen, and a smoothed target encoder that uses out-of-fold statistics so a row's own label never leaks into its own feature. Tests that deliberately perturb the test set and the labels check that nothing leaks, and a final check measures the model quality you get from honest features. This is a Tier 1 assessment: the behaviour of every component is specified exactly, and what you are tested on is precision and understanding.

---

## C. Objectives

When you finish, you should be able to show that you can:

- Implement fit/transform components that learn only from training data and apply them unchanged to new data.
- Handle missing values with a median and an indicator that preserves the information that a value was missing.
- Encode high-cardinality categories with smoothed target statistics and explain why in-sample target encoding overstates performance.
- Write tests that detect leakage by perturbing the test set and the labels.
- Explain which statistic each component learns, from which rows, and what happens to unseen categories.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the classes and function in `safeprep/core.py`. Each stub raises `NotImplementedError("R<n>: ...")` and its docstring is the exact specification. Only numpy may be imported inside the package.

| # | Requirement |
|---|---|
| R1 | `MedianImputer`: medians from `fit` only; NaN filled with them at `transform`; optional 0/1 indicator columns for columns that had NaN at fit time; an all-NaN column raises `ValueError`. |
| R2 | `StandardScaler`: population mean and standard deviation ignoring NaN, zero spread becomes scale 1.0, with `inverse_transform`. |
| R3 | `OneHotEncoder(min_count)`: sorted categories seen at least `min_count` times; unknown or rare categories give an all-zero row. |
| R4 | `SmoothedTargetEncoder(smoothing)`: `(n_c * mean_c + smoothing * global_mean) / (n_c + smoothing)`; unseen categories get the global mean; `fit_transform` returns out-of-fold encodings with the fold rule in the docstring, so that a row's own label never influences its own encoding. |
| R5 | `make_features(train, test)`: imputed and scaled numeric columns, one-hot state, target-encoded supplier; everything learned from train only; returns `(Xtr, Xte, ytr, yte)`. |

Then write a short `REPORT.md` comparing the held-out R-squared of a ridge model on (a) your honest features, (b) the same pipeline with the encoder fitted in-sample on train, and (c) a deliberately leaky version in which the scaler and imputer are fitted on train plus test.

### D.2 Engineering requirements (mandatory)

- `pytest` passes from a clean environment built from `requirements.txt`; the package imports only numpy.
- No component may modify its inputs, and none may read a global; results depend only on arguments and seeds.
- Row-wise transforms must be vectorised (no Python loop over rows except in the target encoder lookup).
- At least 5 of your own tests in `tests/test_member_*.py`, including one leakage test you design yourself.

### D.3 Privacy and responsibility

The farm records are synthetic and fictional. Real farm data can identify a household through its location and plot size and is personal data under the NDPA 2023; encodings such as supplier means can also expose small groups. Say in your report what minimum group size you would require before publishing an encoded or aggregated table.

### D.4 Optional enhancements (not required for full marks)

- Add a `fit_transform` convenience to the other components and show it equals `fit` then `transform`.
- Implement a rare-category bucket in `OneHotEncoder` and show its effect on R-squared.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/farms.csv`](resources/data/farms.csv): 800 farms, 8 columns, about 40 KB, with blanks for missing values |
| **Provenance** | **Synthetic**, generated with a fixed seed by a generator in the assessor kit. Supplier and state effects are simulated; no real farmers |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Loader** | `load_farms` in the starter returns a dict of column arrays |
| **Setup** | `pip install -r starter/requirements.txt` (numpy, scikit-learn for the tests, pytest) |

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `safeprep/` package (completed starter) | Core technical evidence for R1-R5 |
| 2 | `tests/test_member_*.py` (at least 5 tests) | Pins behaviour and detects leakage |
| 3 | `REPORT.md` (at most 600 words plus a small table) from the [template](submission-template/REPORT.md) | Honest versus leaky comparison and AI-use declaration |
| 4 | A 5-minute live defence | Verifies understanding (section K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Criteria marked (auto) are checked by the public and hidden test suites; the rest are checked by hand.

1. (auto) All public tests pass from a clean environment, and your own tests pass.
2. (auto) Perturbing the test rows or test labels never changes the training matrix; transforming a single test row gives the same output as inside the full test set.
3. (auto) The target encoder matches the formula exactly, its leave-one-out limit is exact, and a row's own label never changes its out-of-fold encoding.
4. (auto) On public data, ridge on your features reaches held-out R-squared of at least 0.55. *Justification:* the reference reaches this comfortably; the bar mainly guards against a broken encoder.
5. (auto) On hidden re-seeded farms with 60 suppliers, R-squared is at least 0.5 and the supplier encoding improves R-squared by at least 0.03 over dropping it; unseen suppliers and states do not crash the pipeline.
6. The report states the three R-squared values and explains the ordering in terms of what each version learned from which rows.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 15 |
| Methodology and validation | 10 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, reproducible results and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T1-009-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders into it.
2. **Expected structure:**
   ```text
   clbg-ML-T1-009-<username>/
   ├── requirements.txt
   ├── safeprep/            # your package
   ├── tests/               # provided tests + your test_member_*.py
   ├── resources/           # unchanged
   └── REPORT.md
   ```
3. **Commit as you work.** A single "final" commit containing everything will be questioned at defence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** set by the cohort coordinator. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback but never stand in for the core requirements.

1. **Smoothing sweep.** Plot held-out R-squared against the smoothing constant and explain the shape for rare suppliers.
2. **Missingness signal.** Show whether the rainfall indicator helps, and why in this data it might.
3. **Time split.** Re-split by something other than random order and show how an honest estimate changes.
4. **Leakage detective.** Write a function that takes any fitted pipeline and tests it for dependence on held-out labels.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration inside `REPORT.md`. Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** adapted code with a link. **Collaboration** is limited to general techniques; never share code, numbers or report text.
- **How understanding is verified.** In a short defence the assessor will:

1. Draw which rows each statistic in your pipeline is computed from, for training and for test rows.
2. Explain why in-sample target encoding inflates training performance and what the out-of-fold version changes.
3. Handle an unseen modification live, such as a new category in test data or a column that is all missing in training.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | numpy masks and axes, the purpose of a held-out set, a basic regression model. |
| **New skill developed** | Making preprocessing a learned, fitted object, and reasoning about exactly which rows each learned value comes from. |
| **Decisions the member must make** | How to structure fit and transform, how to build out-of-fold folds, how to treat unseen categories, and how to test for leakage. |
| **What must be investigated independently** | Which perturbations of test data and labels would expose a leaky pipeline, and what the in-sample versus out-of-fold gap looks like. |
| **Why it is interesting** | Leakage produces models that look brilliant and fail in the field, and the fix is a small amount of precise code. |
| **Evidence of competence** | Perturbation tests pass, the encoder matches its formula and its leave-one-out limit, and hidden farms with unseen categories run cleanly. |
| **Misconceptions exposed** | "Scale first, then split." "Target encoding is safe if I just average." "Unseen categories are an edge case." "Missing values carry no information." |
| **Preparation for later work** | Leads to leakage forensics in realistic pipelines (ML-T2-007), label-quality work at Tier 3, and the model-evaluation units. |

**Suggested approach**, for members who want guidance (you may ignore it):

1. Start with R2 and R3, which are short, then the imputer.
2. Write the target encoder formula test before the out-of-fold code.
3. Assemble `make_features` last and run the perturbation tests.
4. Produce the three-way R-squared comparison.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
