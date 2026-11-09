# AI-T2-006: Needles in the Circular: Chunking and Hybrid Search for a Compliance Desk

> *Sixty long regulatory circulars, each hiding one decisive sentence. Reference-code lookups want exact words, topic questions want meaning. Build the retriever that serves both, and prove it on held-out queries.*

![Format: Comparative (secondary: Optimization)](https://img.shields.io/badge/format-comparative-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T2-006` |
| **Title** | Needles in the Circular: Chunking and Hybrid Search for a Compliance Desk |
| **Subtrack** | AI Engineering |
| **Tier** | 2: Applied Engineering and Independent Problem-Solving |
| **Unit** | [AI-04: Embeddings and Semantic Search](../README.md) |
| **Format** | Comparative (secondary: Optimization) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14–20 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. Full test run under 2 minutes |
| **Recommended prerequisites** | Cosine similarity and top-k search; recall and MRR. Recommended: AI-T1-008 |
| **Skills developed** | Chunking with overlap; BM25 from scratch; reciprocal rank fusion and score fusion; tuning on development queries and evaluating on held-out ones; diagnosing why a fusion helps or hurts per query type |
| **Technologies** | Python 3.10+, numpy, pytest |

---

## B. Problem Statement

The compliance desk of *Apex Microfinance Bank* (fictional) searches 60 long circulars from regulators. Each is about 280 words, mostly background text on two topics, with **one decisive sentence** buried at a random position. That sentence carries a unique reference code such as `cir-4471` and several words about the circular's key topic. Five circulars share each of twelve key topics. Analysts ask two kinds of question:

- **id queries**: "cir-4471 plus one topic word". Exactly one circular is relevant. These need exact-token matching; the code is a rare string that an embedding treats as noise.
- **topic queries**: four words about a topic that are **not** the words used in the decisive sentence (synonyms, in the planted structure of the toy embedder). All five circulars on that topic are relevant. Lexical search has nothing to match and gets misled by incidental background words; an embedding sees the shared topic, but only if the decisive sentence is not diluted by 280 words of background.

The first prototype embedded whole documents and used cosine similarity. Lookups by code failed, topic queries failed, and the team concluded embeddings were useless. The second used BM25 alone, which fixed codes and nothing else. You are asked to build something better and show **why** it is better. The embedder is a deterministic **toy** (`resources/toyembed.py`); text is embedded as the sum of its word vectors, so long texts dilute rare signals. Everything is synthetic and offline.

The task is partially specified. The tests fix interfaces, the exact behaviour of the small components, and acceptance bars. **You decide** the chunk size and overlap, how lexical and dense evidence are combined, whether and how to treat very common or very rare query terms differently, and how to tune on the development queries without touching the test queries.

> **Why this matters beyond this task.** Almost every production search or retrieval-augmented system combines lexical and dense retrieval. Teams often get the combination wrong because they tune on a handful of examples or one query type; naive fusion can make a system worse than its best component.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** word-window chunking with overlap, BM25 and reciprocal rank fusion to exact specifications.
2. **Build** a retriever that combines lexical and dense evidence over chunks and returns document ids.
3. **Choose** chunk size, fusion rule and weights using development queries only, then evaluate on held-out queries.
4. **Diagnose** per query type why each single method fails and what the fusion must protect.
5. **Compare** fairly against whole-document BM25 and whole-document dense baselines and report the margin.
6. **Write** a decision memo with the failure cases you could not fix.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `hybridsearch` package in [`starter/hybridsearch/core.py`](starter/hybridsearch/core.py). Use only numpy and the standard library. Use `toyembed.tokenize` as your tokenizer for BM25 so that tokens match the embedder's.

| ID | Requirement |
|---|---|
| **R1** | `chunk_text(text, size, overlap)`: split on whitespace into windows of `size` words advancing by `size - overlap`; windows start at word 0; stop after the first window whose end reaches the last word; empty text gives `[]`; chunks are re-joined with single spaces; raise `ValueError` unless `0 <= overlap < size`. |
| **R2** | `BM25(docs_tokens, k1=1.5, b=0.75).score(query_tokens)`: Okapi BM25 with `idf = ln(1 + (N - df + 0.5)/(df + 0.5))`; each **distinct** query term counts once; unknown terms are ignored. Returns a numpy array with one score per document. |
| **R3** | `rrf(rankings, k=60, weights=None)`: reciprocal rank fusion with 1-based ranks; items missing from a ranking add nothing; ties go to the smaller id. |
| **R4** | `evaluate(searcher, queries, relevant, k=5)` returns `recall` (mean `|top-k ∩ relevant| / |relevant|`), `mrr` (over the first 20 results) and `n_queries`, skipping queries with no relevant document. |
| **R5** | `build_searcher(docs, embed, dev_queries, dev_relevant)` returns an object with `search(query, k=5) -> list[int]` of **document** ids, best first, without duplicates. It may chunk, use BM25 and dense scores, fuse them, and tune any parameters on the development queries. A document's score from chunks is up to you; justify it. |

### D.2 Engineering requirements (mandatory)

- Deterministic and offline; no scikit-learn, no search libraries, no network.
- No use of the test queries (`world["test"]`) for any decision. Tuning code must receive only the development split.
- At least **10 tests of your own** in `tests/test_member_*.py`, including a chunking boundary test and a test that your searcher gives the same results for the same input.
- `experiments.py` regenerates every table in `REPORT.md` on **at least 3 world seeds**, including: whole-document BM25, whole-document dense, chunked BM25, chunked dense, and your hybrid, reported separately for id and topic queries.

### D.3 Responsibility

Regulatory and customer documents can contain personal or confidential details. In the report, write one paragraph on what a compliance team should not send to a third-party embedding service, how a local or self-hosted embedder changes the risk, and what the Nigeria Data Protection Act 2023 implies for storing derived vectors. The data here is synthetic.

### D.4 Optional enhancements

- Add query-type routing (detect codes) and compare to your fusion.
- Add a second-stage reranker over the top 10 and measure when it helps.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Toy embedder** | [`resources/toyembed.py`](resources/toyembed.py): topic words share a centroid; unknown tokens (such as reference codes) get hashed character-trigram vectors; a text embeds as the sum of its token vectors, unnormalised |
| **World** | [`resources/circulars.py`](resources/circulars.py): `make_circular_world(seed=2026)` returns `docs` (60), `dev` and `test` as `(queries, relevant, kinds)` (80 and 120 queries) and `embed`; `python resources/circulars.py --out DIR` writes a JSON file of about 200 KB |
| **Provenance** | **Synthetic and deterministic**; pseudo-words, fictional bank and circular codes, no personal data |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Splits** | Use `dev` for all tuning; `test` only for final evaluation. The hidden tests use other seeds and other documents |

Because the corpus is small, differences of a few MRR points are within noise; the acceptance bars are chosen with that in mind.

**Setup**

```bash
cd assessments/ai-engineering/tier-2/units/AI-04-embeddings-and-semantic-search/AI-T2-006-needles-in-the-circular
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `hybridsearch/` package | Chunking, BM25, fusion, evaluation and the tuned retriever |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Includes chunk-boundary and determinism tests |
| 3 | `experiments.py` | Reproduces the per-query-type comparison on 3 or more seeds |
| 4 | `REPORT.md`, at most 1,500 words plus tables, from the [template](submission-template/REPORT.md) | Decision memo and AI-use declaration |
| 5 | A 5-minute technical defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `chunk_text`, `BM25`, `rrf` and `evaluate` match the written definitions, including a differential test of BM25 on random corpora (hidden).
3. ⚙ **Performance.** On the public test queries the retriever's MRR is at least **0.65** and at least **0.15** above the better of whole-document BM25 and whole-document dense; recall@5 is at least 0.5; MRR on id queries is at least 0.85 and on topic queries at least 0.5. *Justification:* the reference reaches about 0.77 overall (0.73 to 0.84 across seeds), against 0.49 for the better whole-document baseline; the ceiling is limited because topic queries have five relevant documents and the toy embedder's topic signal is noisy. Hidden worlds use 0.6, +0.1, 0.8 and 0.45.
4. ⚙ Results are deterministic; documents are not repeated in a result list.
5. ✍ The report shows, per query type and over 3 or more seeds, what chunking contributes, what each component contributes and what fusing adds, including any case where a naive fusion is worse than its best component, and why.
6. ✍ The report states how the development queries were used, that the test queries were not, and how large the noise in a 120-query evaluation is.

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

1. **Create your own private repository** named `clbg-AI-T2-006-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `hybridsearch/` (your package), `tests/` (provided tests plus your own), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Real embedder.** Replace the toy embedder with a small open-weight sentence-embedding model run locally and re-run the table. Optional; the graded path is offline.
2. **Learned fusion.** Fit fusion weights per query type with a tiny logistic model on the development queries and test for overfitting.
3. **Chunk context.** Prepend the document title to each chunk and measure the change.
4. **Failure taxonomy.** Categorise every test failure of your system and decide which are fixable.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why plain reciprocal rank fusion can be worse than the best single component on topic queries, and how your design avoids it; (2) ask what you would do differently with 60,000 circulars instead of 60; (3) give an unseen modification, for example "codes are written without the hyphen" or "the decisive sentence is now 4 words long", and ask what changes in your retriever and in the metrics.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Cosine similarity, top-k search, recall and MRR. No ranking-model theory. |
| **New skill developed** | Combining retrieval signals and proving the combination helps, per query type and out of sample. |
| **Decisions the member must make** | Chunk size and overlap; document score from chunks; fusion rule and weights; treatment of rare terms; what to tune on. |
| **What must be investigated independently** | Why plain fusion fails on one query type, which the brief hints but does not explain. |
| **Why it is interesting** | The obvious hybrid (rank fusion of two retrievers) loses to a single dense retriever on half the queries, and the repair is a principled gate on rare terms. |
| **Evidence of competence** | Held-out MRR on re-seeded worlds above the bars, per-type results and clean dev/test discipline. |
| **Misconceptions exposed** | 'Hybrid always beats its parts.' 'Embeddings understand identifiers.' 'Bigger chunks are safer.' 'One overall number is enough.' |
| **Preparation for later work** | Leads into AI-04 Tier 3 (indexes and drift), AI-05 RAG chunking and reranking, and AI-10 evaluation. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
