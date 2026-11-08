# AI-T1-008: The Longer Complaint Wins: Building and Evaluating Similarity Search from Scratch

> *A thrift-app help desk matches complaints to FAQ answers with embeddings, and the longest document keeps winning. Find out why, in numpy, with exact metrics.*

![Format: Implementation (secondary: Investigation)](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T1-008` |
| **Title** | The Longer Complaint Wins: Building and Evaluating Similarity Search from Scratch |
| **Subtrack** | AI Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [AI-04: Embeddings and Semantic Search](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8–12 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. Full test run under 2 minutes |
| **Recommended prerequisites** | Numpy arrays and broadcasting; dot products; running pytest. No machine-learning knowledge |
| **Skills developed** | Row normalisation; dot, cosine and Euclidean scoring; deterministic top-k with tie-breaking; recall@k, MRR and nDCG@k; explaining norm bias in embedding search |
| **Technologies** | Python 3.10+, numpy, pytest |

---

## B. Problem Statement

*Ajo Circle* (fictional) is a savings-group app used across Nigeria. Its help desk has 64 FAQ answers on twelve topics (contributions, payouts, KYC and so on) and receives short complaints such as a few words typed on a phone. The team embeds every FAQ and every complaint and returns the five nearest FAQs. A pilot looked fine on three hand-picked examples. In production, support agents report the same four answers appearing for almost every complaint, and they are always the long ones, such as the terms and conditions.

You will build the search layer yourself, with no vector library, and the metrics that would have caught the problem. The embeddings come from a deterministic **toy embedder** (`resources/toyembed.py`): words from the same topic have similar vectors, and a text's embedding is the **sum** of its word vectors, so its length (norm) grows with the number of words. FAQs differ in length, and four boilerplate documents are very long and mention every topic. Everything is synthetic and runs offline.

This is a Tier 1 task: every function has an exact specification, and the interesting part is seeing what those exact functions reveal. Write the functions, make the tests pass, then use them to explain the failure in a one-page report.

> **Why this matters beyond this task.** Embedding search is the retrieval layer of most RAG and search systems. A wrong similarity metric or an unchecked evaluation can look fine on a demo and fail silently in production.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** dot, cosine and negative-L2 scoring with correct handling of zero vectors.
2. **Return** exact top-k results with deterministic tie-breaking, including when `k` exceeds the corpus.
3. **Compute** recall@k, MRR and nDCG@k to the stated conventions, skipping queries with no relevant document.
4. **Measure** how often one long document appears in the top results under each metric.
5. **Explain**, with your own numbers, why vector length matters for dot-product search and what normalisation changes.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `simsearch` package in [`starter/simsearch/core.py`](starter/simsearch/core.py). Use only numpy and the standard library.

| ID | Requirement |
|---|---|
| **R1** | `normalize_rows(M)`: divide each row by its L2 norm; all-zero rows stay all-zero (no NaN); the input is not modified. |
| **R2** | `scores(Q, D, metric)` returns an `(n_queries, n_docs)` matrix where higher is always better: `"dot"` is the inner product; `"cosine"` is the cosine similarity with 0 whenever either vector is zero; `"l2"` is the **negative** Euclidean distance. An unknown metric raises `ValueError`. |
| **R3** | `top_k(Q, D, k, metric) -> (indices, scores)`, both of shape `(n_queries, min(k, n_docs))`, best first. Equal scores are ordered by **lower document index first**. |
| **R4** | `recall_at_k(retrieved, relevant, k)`: mean over queries that have at least one relevant document of `|top-k ∩ relevant| / |relevant|`. `mrr(retrieved, relevant)`: mean reciprocal rank (1-based) of the first relevant document in the whole retrieved list, 0 if absent, skipping queries with no relevant document. `ndcg_at_k(retrieved, relevant, k)`: binary gain, discount `1/log2(rank + 1)` for 1-based `rank`, ideal list holding `min(k, |relevant|)` hits, same skipping rule. Empty input returns 0.0. |
| **R5** | `evaluate(Q, D, relevant, metrics=("dot","cosine","l2"), k=5)` returns `{metric: {"recall", "mrr", "ndcg", "n_queries"}}` where `mrr` is computed on the full ranking and `n_queries` counts queries with relevant documents. |

### D.2 Engineering requirements (mandatory)

- Numpy only. No scikit-learn, faiss or other search libraries.
- No Python loop over documents in `scores` (vectorise with matrix operations); your L2 must not return NaN when rounding makes a squared distance slightly negative.
- At least **8 tests of your own** in `tests/test_member_*.py`, including a tie-breaking test and a zero-vector test.
- `experiments.py` prints the table of §G item 6.

### D.3 Responsibility

Support complaints can contain personal information. In the report, write a short paragraph on what should be removed before complaint text is embedded or sent to any external embedding service, and why stored embeddings can still reveal personal information. The data in this assessment is synthetic.

### D.4 Optional enhancements

- Add a `hub_rate(retrieved, hub_ids, k)` helper and plot it against document length.
- Implement maximum-inner-product search by augmenting vectors so that L2 search returns the same ranking as dot product.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Toy embedder** | [`resources/toyembed.py`](resources/toyembed.py): topic words share a centroid; unknown tokens get hashed character-trigram vectors; a text embeds as the sum of its token vectors, unnormalised |
| **FAQ world** | [`resources/faqs.py`](resources/faqs.py): `make_faq_world(seed=2026, ...)` returns `docs`, `queries`, `relevant`, `embed` and `boiler_ids`; `python resources/faqs.py --out DIR` writes a JSON file of about 100 KB |
| **Provenance** | **Synthetic and deterministic**; pseudo-words, a fictional company, no personal data |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Relevance** | A complaint is relevant to every FAQ of its topic (5 per topic); boilerplate documents are relevant to nothing |

Hidden tests use other seeds, a different number of boilerplate documents, brute-force oracles and edge cases (duplicates, zero vectors, huge offsets).

**Setup**

```bash
cd assessments/ai-engineering/tier-1/units/AI-04-embeddings-and-semantic-search/AI-T1-008-the-longer-complaint-wins
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `simsearch/` package | Normalisation, scoring, top-k, metrics and evaluation |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Includes tie-breaking and zero-vector tests |
| 3 | `experiments.py` | Prints the metric comparison and the long-document statistic |
| 4 | `REPORT.md`, at most 800 words plus a table, from the [template](submission-template/REPORT.md) | Explanation and AI-use declaration |
| 5 | A 5-minute technical defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `scores` and `top_k` match a brute-force implementation on random data with duplicates, zero rows and short corpora (hidden test).
3. ⚙ `recall_at_k`, `mrr` and `ndcg_at_k` match hand-computed values, including queries with no relevant document and relevant sets larger than `k`.
4. ⚙ On the public world, cosine reaches MRR above 0.95 while dot product stays below 0.6, and the four boilerplate documents fill more than half of the dot-product top-5 but fewer than 2% of the cosine top-5.
5. ⚙ On hidden worlds (other seeds, 2 and 6 boilerplate documents) cosine MRR exceeds 0.9 and beats dot by more than 0.2.
6. ✍ **Table.** The report contains, for dot, cosine and L2, recall@5, MRR, nDCG@5 and the share of top-5 slots taken by boilerplate documents.
7. ✍ **Explanation.** The report explains in your own words, using the formula for the dot product, why length changes the ranking, why L2 on unnormalised vectors is also affected, and when dot product would nevertheless be a sensible choice.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 15 |
| Technical correctness | 30 |
| Implementation quality | 10 |
| Methodology and evidence | 10 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 8 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 7 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-AI-T1-008-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `simsearch/` (your package), `tests/` (provided tests plus your own), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Hubness.** Measure how unevenly documents are retrieved (skewness of the retrieval-count distribution) before and after normalisation.
2. **Real embeddings.** Swap the toy embedder for a small open-weight sentence-embedding model run locally and repeat the table. Optional; never required, and the graded path is offline.
3. **Reranking.** Add a second stage that reranks the top 20 and show when it helps.
4. **Metric choice.** Show a case where dot product is the right choice and explain what the norm is encoding.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why the same four documents win under dot product and what would happen if the boilerplate were half as long; (2) ask what each metric does with a query that has no relevant document and why that convention is chosen; (3) give an unseen modification, for example "documents are normalised but queries are not" or "scores must be bounded in [0, 1]", and ask which results change and which do not.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Numpy and the dot product. No machine-learning background. |
| **New skill developed** | Building and evaluating a retrieval layer from exact definitions, and reading a failure off the metrics. |
| **Decisions the member must make** | How to vectorise; how to keep L2 numerically safe; how to test ties and zeros. |
| **What must be investigated independently** | Why the same documents win, which the brief only describes. |
| **Why it is interesting** | Three correct-looking metrics give very different results on identical vectors. |
| **Evidence of competence** | Exact agreement with brute-force oracles and a correct, explained comparison table. |
| **Misconceptions exposed** | 'Embeddings from the same model are comparable by dot product.' 'Higher similarity means more relevant.' 'One good demo means good search.' |
| **Preparation for later work** | Leads into hybrid and chunked retrieval (AI-04 Tier 2), ANN indexes (AI-04 Tier 3) and RAG evaluation (AI-05). |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
