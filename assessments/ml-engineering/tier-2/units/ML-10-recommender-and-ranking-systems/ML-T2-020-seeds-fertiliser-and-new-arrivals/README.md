# ML-T2-020: Seeds, Fertiliser and New Arrivals: A Time-Aware Recommender with Cold-Start Items

> *A third of next month's purchases will be of products that did not exist when you trained. A recommender that only knows history scores them zero.*

![Format: Comparative (secondary: Investigation)](https://img.shields.io/badge/format-comparative-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-020` |
| **Title** | Seeds, Fertiliser and New Arrivals: A Time-Aware Recommender with Cold-Start Items |
| **Subtrack** | ML Engineering |
| **Tier** | 2: Applied Competence |
| **Unit** | [ML-10: Recommender and Ranking Systems](../README.md) |
| **Format** | Comparative (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14-20 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 2 minutes |
| **Recommended prerequisites** | Matrix factorisation or SVD at the level of calling scikit-learn, recall@k, why random splits mislead on time-ordered data. Recommended: ML-T1-020 |
| **Skills developed** | Implicit-feedback factorisation; cold-start handling with item attributes; validation windows that mimic deployment; per-segment evaluation |
| **Technologies** | Python 3.10+, numpy and scikit-learn, pytest |

---

## B. Problem Statement

AgroLink (fictional) is a marketplace where 800 farmers buy seed, fertiliser, agrochemicals, tools, feed and irrigation kit from 150 listed products. Each farmer has stable tastes (crop, scale, soil), the catalogue grows continuously, and in the last month 25 new products were launched and immediately attracted about a third of the purchases. The product team wants a "recommended for you" strip that works from day one of a launch.

You have a purchase log (farmer, product, day) and, for each product, a small attribute vector: a category one-hot, a price tier and two noisy taste coordinates supplied by the catalogue team. The log runs to day 300; days 300 to 334 form the test period, in which the 25 new products appear. A recommender trained on the log alone has no information about them. Your task is to choose and fit a recommender using only data before day 300, decide how to use the attributes, and show with a validation window *built from the training period* that your choice generalises to the test period.

The task is partially specified. The tests fix the interfaces and acceptance bars (overall recall@10 and recall on the new products) but not the model family, the number of factors, how attributes enter, or how validation is built. Plain factorisation looks best on a validation window with no new products, and loses on the test period; spotting why is the heart of the assessment.

> **Why this matters beyond this task.** Catalogues, courses, jobs and loans all change faster than recommenders retrain. The right question is not 'which model has the best offline score' but 'which validation mimics the thing that will actually happen on launch day.'

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Split** purchase logs by time and build binary interaction matrices.
2. **Evaluate** recall@k per user, excluding purchased items, overall and on a subset of items.
3. **Fit** a popularity baseline, a factorisation and an attribute-based hybrid under one code path.
4. **Build** a validation window from the training period that mimics the cold-start share of deployment.
5. **Decide**, and defend with evidence, which model to ship and what to monitor.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `inputrec` in [`starter/inputrec/`](starter/inputrec/). Interfaces are fixed; the model family, number of factors, attribute mapping and selection rule are yours. Use only numpy and scikit-learn.

| ID | Requirement |
|---|---|
| **R1** | `time_split(t, cutoff) -> (train_idx, test_idx)`: train is `t < cutoff`, test is `t >= cutoff`; both sorted. |
| **R2** | `interaction_matrix(users, items, n_users, n_items) -> binary matrix`; repeated purchases stay 1. |
| **R3** | `recall_at_k(scores, train_M, test_M, k, items=None) -> float`: for each user with at least one test item (restricted to the columns in `items` if given), the fraction of those test items found in the top `k` unseen items by score (training items are never recommended); return the mean over such users. Candidates are always the full catalogue. |
| **R4** | `fit_recommender(users, items, t, n_users, n_items, item_attrs, cutoff) -> model` with `score_matrix() -> (n_users, n_items)`, `chosen_` and `report_` (a dict mapping at least three candidate names, one `"popularity"`, to a validation recall@10). It uses only rows with `t < cutoff`, and must give the same scores if rows with `t >= cutoff` are included in the input. |

### D.2 Engineering requirements (mandatory)

- Deterministic: explicit `random_state` for every estimator.
- All candidates are scored by the same `recall_at_k` on the same windows.
- No model selection or tuning on the test period (days 300 and later).
- Item attributes may be used for any item, but not statistics computed from test-period behaviour.
- At least **10 tests of your own** in `tests/test_member_*.py`, including a no-future-data test and a test that a never-purchased item can still be recommended.
- `experiments.py` regenerates every number and figure in `REPORT.md`, including **at least 5 seeds**, and an experiment showing which validation window picks which model.

### D.3 Responsibility

The data is synthetic. In the report, write one paragraph on what a recommendation strip does for smallholders (it nudges spend on inputs with real costs and risks) and on how you would check that new, heavily promoted products are not recommended simply because they are new, or that small sellers are not starved of exposure.

### D.4 Optional enhancements

- Weight recent purchases more strongly and test whether it helps.
- Recommend with a diversity constraint across categories.
- Estimate a monitoring rule that notices when attributes stop predicting taste.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_purchases(n_farmers=800, seed=2026, days=335, cutoff=300)` returns a dict with `user, item, t, item_attrs, launch, cold_items, n_items, n_users, cutoff` |
| **Provenance** | **Synthetic**, deterministic given the seed; no real person, transaction, market or institution |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Contents** | 150 items: 100 launched before day 200, 25 launched in days 265 to 274, 25 launched in days 300 to 309; 4 latent tastes; a 1.5 times boost for items under 30 days old; no repeat purchases |
| **Split used by the tests** | Train on days 0 to 299; test on days 300 to 334; the generator places a set of arrivals in days 265 to 274 so a validation window can mimic the test period |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes a three-column CSV of about 150 KB plus an items CSV |

Hidden tests use other seeds and a smaller farmer base (600).

**Setup**

```bash
cd assessments/ml-engineering/tier-2/units/ML-10-recommender-and-ranking-systems/ML-T2-020-seeds-fertiliser-and-new-arrivals
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `inputrec/` package | Split, matrix, metric and recommender selection |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Includes no-future-data and cold-item tests |
| 3 | `experiments.py` | Reproduces every table and figure in the report |
| 4 | `REPORT.md` (at most 1800 words plus tables), from the [template](submission-template/REPORT.md) | Recommendation memo for the product team; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `time_split`, `interaction_matrix` and `recall_at_k` match hand-computed values, including the item subset and users with no test items.
3. ⚙ `report_` has at least three candidates including `popularity`, `chosen_` is a key, and the scores ignore interactions at or after the cutoff.
4. ⚙ **Performance.** On days 300 to 334 the chosen model's overall recall@10 is at least **0.30** and at least **3 times** popularity, and its recall@10 on the 25 new items is at least **0.40**. *Justification:* the reference reaches about 0.36 overall against 0.08 for popularity and about 0.56 on the new items; seed variation gives 0.27 to 0.45 overall and 0.31 to 0.63 on new items, so hidden seeds use 0.24, 2 times and 0.25.
5. ⚙ **No collateral damage.** Recall@10 on items that existed before the cutoff stays at least 0.15.
6. ✍ The report shows which validation window picks which model, and explains why.

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

1. **Create your own private repository** named `clbg-ML-T2-020-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `inputrec/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `experiments.py`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Temporal weighting.** Decay old purchases and re-tune.
2. **Explore.** Add a small exploration share for new items and estimate the cost.
3. **Cold-start users.** Handle a farmer with no history and compare.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why plain factorisation scores best on an arrival-free validation window and loses on the test period; (2) ask how you would recommend for a brand-new farmer; (3) give an unseen change, for example arrivals with no attributes, and ask which component fails.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Calling a matrix factorisation, recall@k, time-ordered splits. |
| **New skill developed** | Designing validation to resemble deployment, and handling items the model has never seen. |
| **Decisions the member must make** | Number of factors, how attributes map to factors, which items count as cold, how to build the validation window, how to select. |
| **What must be investigated independently** | Why a convincing offline winner can lose, and what share of purchases the cold segment represents. |
| **Why it is interesting** | The model that wins a naive validation loses where it matters; the fix is the validation design, not a bigger model. |
| **Evidence of competence** | Bars met on re-seeded data, a model that ignores post-cutoff rows, and a report that explains the validation trap. |
| **Misconceptions exposed** | 'Highest validation recall is best.' 'Popularity is a strong baseline.' 'New items are a rounding error.' |
| **Preparation for later work** | Leads into ML-T3-019 (position bias and counterfactual evaluation). |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
