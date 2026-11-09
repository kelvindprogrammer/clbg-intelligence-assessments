# ML-T1-020: Ranking Metrics and Nollywood Neighbours: Implementing Item-Based Recommendation from Scratch

> *Recall, NDCG, a chronological split and cosine neighbours: build the whole small recommender yourself and find out how much better than 'most watched' it really is.*

![Format: Implementation (secondary: Comparative)](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T1-020` |
| **Title** | Ranking Metrics and Nollywood Neighbours: Implementing Item-Based Recommendation from Scratch |
| **Subtrack** | ML Engineering |
| **Tier** | 1: Foundations |
| **Unit** | [ML-10: Recommender and Ranking Systems](../README.md) |
| **Format** | Implementation (secondary: Comparative) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8-12 hours over 1-2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 1 minute |
| **Recommended prerequisites** | Python and numpy arrays, dot products and cosine similarity, the idea of a train/test split. No recommender experience needed |
| **Skills developed** | Ranking metrics and their conventions; chronological evaluation; item-item similarity; baselines for recommendation |
| **Technologies** | Python 3.10+, numpy, pytest |

---

## B. Problem Statement

NaijaWatch (fictional) is a streaming app with 120 titles across six genres: Nollywood drama, Afrobeats concerts, comedy skits, faith and family, football and documentaries. Each of its 600 sampled viewers has a handful of favourite genres, and the log records which titles they watched and when. The product team wants a "watch next" row. Their first idea is **most watched titles** for everybody. Their second is **people who watched this also watched that**. They need to know whether the second is worth the engineering.

You will build the evaluation and the recommender from scratch: three ranking metrics (recall, hit rate, NDCG at k), a leave-last-out split that holds out each viewer's most recent title, item-item cosine similarity on the binary viewer-by-title matrix, a recommender that scores unseen titles by summed similarity to titles the viewer has watched, a popularity recommender, and an evaluation loop. The tests fix every convention that usually hides a bug: the ideal DCG is capped by the number of relevant items, ties go to the lower index, the last item is the latest in time, and a title the viewer has already seen is never recommended. The final test asks whether neighbours beat popularity by at least a factor of two on the official data.

> **Why this matters beyond this task.** Recommender metrics are conventions, and a convention applied inconsistently makes every later comparison meaningless. Getting the small things exactly right (what is held out, what is excluded, how ties break) is what makes a recommender evaluation credible at any scale.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** recall@k, hit rate@k and NDCG@k with exact, documented conventions.
2. **Split** an interaction log chronologically, holding out each user's last item, with a minimum-history rule.
3. **Compute** item-item cosine similarity from a binary matrix, handling empty items and the diagonal.
4. **Recommend** top-k unseen items with deterministic tie-breaking, for neighbours and for popularity.
5. **Evaluate** both on held-out items and explain the gap.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `titlerank` in [`starter/titlerank/`](starter/titlerank/). Interfaces are fixed; vectorisation is yours. Use only numpy.

| ID | Requirement |
|---|---|
| **R1** | `recall_at_k(recommended, relevant, k)`, `hit_rate_at_k(recommended, relevant, k)` and `ndcg_at_k(recommended, relevant, k)` for a ranked list and a set of relevant items. NDCG uses binary gain and a `log2(rank + 1)` discount (rank starts at 1); the ideal list has `min(k, len(relevant))` hits; an empty relevant set scores 0.0. |
| **R2** | `leave_last_out(user, item, t, min_views=3) -> (train_mask, held_out)`: for each user with at least `min_views` interactions, hold out the interaction with the latest `t` (ties go to the later row); `held_out` maps user to item. Users below the threshold stay wholly in training and have no held-out item. |
| **R3** | `item_cosine(M) -> (n_items, n_items)`: cosine similarity of the columns of a binary user-by-item matrix, with a zero diagonal and zeros (never NaN) for items nobody watched. |
| **R4** | `recommend(user_row, sim, k) -> list[int]`: the `k` highest-scoring items not already seen, where an item's score is the sum of its similarity to the seen items; ties go to the lower index; fewer than `k` items are returned only if fewer exist. |
| **R5** | `popularity_recommend(M, user_row, k) -> list[int]`: the same, scored by the item's training popularity. |
| **R6** | `evaluate(M, held_out, rec_fn, k) -> (mean_hit_rate, mean_ndcg)` over the held-out users, with `rec_fn(user_row, k)` returning a ranked list. On the official data item neighbours must reach hit rate@10 of at least 0.45 and at least twice popularity's hit rate and NDCG. |

### D.2 Engineering requirements (mandatory)

- Deterministic: no randomness anywhere in the package.
- No python loop over items inside `item_cosine`.
- The held-out item must never appear in the matrix used for similarity or popularity.
- At least **6 tests of your own** in `tests/test_member_*.py`, including a test that the held-out item is absent from the training matrix and a test that recommending with an empty history is well defined.
- `experiments.py` regenerates every number and figure in `REPORT.md`, comparing neighbours with popularity at k = 5, 10 and 20 across at least 5 generator seeds.

### D.3 Responsibility

The data is synthetic. In the report, write one short paragraph on what a 'watch next' row does to what people see (popularity feeds itself) and which genres or creators could be starved of attention by a neighbour model that learns only from past viewing.

### D.4 Optional enhancements

- Compare cosine with Jaccard and with a shrunk cosine.
- Add a genre-diversity measure to the top-10 lists.
- Evaluate separately for light and heavy viewers.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_views(n_users=600, n_items=120, seed=2026)` returns `user, item, t, item_genre` |
| **Provenance** | **Synthetic**, deterministic given the seed; no real person, transaction, market or institution |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Contents** | 6 genres; each viewer favours 1 or 2 genres (about 30 times the weight); item popularity is heavy-tailed; 8 to 25 titles per viewer; no repeats |
| **Split used by the tests** | Leave-last-out with `min_views = 3`, `k = 10` |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes a three-column CSV of about 100 KB |

Hidden tests use other seeds and a smaller catalogue.

**Setup**

```bash
cd assessments/ml-engineering/tier-1/units/ML-10-recommender-and-ranking-systems/ML-T1-020-ranking-metrics-and-nollywood-neighbours
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `titlerank/` package | Metrics, split, similarity, recommendation and evaluation |
| 2 | `tests/test_member_*.py` (at least 6 tests) | Includes a no-leak and an empty-history test |
| 3 | `experiments.py` | Reproduces every table and figure in the report |
| 4 | `REPORT.md` (at most 1200 words plus tables), from the [template](submission-template/REPORT.md) | Comparison of neighbours and popularity with a short discussion of conventions; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ The three metrics match hand-computed values, including the capped ideal DCG and empty relevant sets.
3. ⚙ `leave_last_out` matches the hand case (ties to the later row, short histories stay in training) and the held-out item is never in the training matrix.
4. ⚙ `item_cosine` is symmetric with a zero diagonal and no NaN; `recommend` excludes seen items and breaks ties to the lower index; `popularity_recommend` does the same.
5. ⚙ On the official data, item neighbours reach hit rate@10 of at least **0.45** and at least **twice** popularity's hit rate and NDCG. *Justification:* the reference reaches about 0.55 against about 0.20 (ratio 2.8) and NDCG about 0.30 against 0.10; hidden seeds use 0.40 and 1.8 times.
6. ✍ The report compares both at three values of k over 5 seeds with spread, and states which convention choices could change the numbers.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 15 |
| Methodology and evidence | 10 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T1-020-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `titlerank/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `experiments.py`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Shrinkage.** Add a similarity shrinkage term and tune it on a validation slice built from each user's second-last item.
2. **Coverage.** Report the share of the catalogue that ever appears in a top-10.
3. **Session order.** Use only the most recent 5 titles to score and compare.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why a recommender with a high hit rate can still be useless and what that metric hides; (2) ask what evaluating on the last item only conceals; (3) give an unseen change, for example removing titles launched after a viewer's last view from the candidates, and ask which function changes.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Arrays, cosine similarity, a train/test split. No recommender theory. |
| **New skill developed** | Treating evaluation conventions as part of the specification: what is held out, what is excluded, how ties break. |
| **Decisions the member must make** | How to vectorise cosine, how to handle empty items, how to report variation across seeds. |
| **What must be investigated independently** | How popularity can look strong in raw terms yet lose clearly once tastes are modelled, and how sensitive the numbers are to the conventions. |
| **Why it is interesting** | A few lines of linear algebra double the quality of a 'most watched' row, and the member can measure it. |
| **Evidence of competence** | All conventions exact; neighbours at least twice popularity; held-out items never leaking. |
| **Misconceptions exposed** | 'Random leave-one-out is fine.' 'NDCG is normalised by the list.' 'Recommending seen items is harmless.' |
| **Preparation for later work** | Leads into ML-T2-020 (cold-start items and time-aware evaluation) and ML-T3-019 (position bias). |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
