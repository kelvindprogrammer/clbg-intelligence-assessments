# AI-T1-010: Ask the Ajo Handbook: Chunk, Retrieve, Cite

> *A thrift cooperative wants members to ask its handbook questions in plain English and get answers that point at the rule they came from. Build the pipeline without a framework, so you can see every place it can lie.*

![Format: implementation](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T1-010` |
| **Title** | Ask the Ajo Handbook: Chunk, Retrieve, Cite |
| **Subtrack** | AI Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [AI-05: Retrieval-Augmented Generation and Knowledge Systems](../README.md) |
| **Format** | implementation |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8-12 hours over 1 week |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. Everything graded runs against a deterministic mock and a small generated corpus; the full test run takes under a minute |
| **Recommended prerequisites** | Python basics, dictionaries, regular expressions and pytest. No machine-learning background is needed. |
| **Skills developed** | Chunking with overlap; BM25 scoring; context budgeting; citation extraction and verification; abstention; retrieval metrics |
| **Technologies** | Python 3.10+, pytest (standard library only in your package) |

---

## B. Problem Statement

Harmony Thrift Cooperative (fictional) runs an *ajo* savings and loan scheme for about 900 members in Ibadan. Its handbook has ten sections: contributions, loan eligibility, interest, guarantors, exit, meetings, welfare, dividends, audit and disputes. Members keep asking the secretary the same questions on WhatsApp, and the executive wants an assistant that answers from the handbook and **shows which section the answer came from**. The council has one rule: an answer that cites a section it was never shown, or states rules with no citation, must not reach a member.

You will not use a vector database or a framework. You will build the five parts every RAG system has, and then check them:

1. **Chunking.** Handbook sections are cut into overlapping windows of words so that a rule is rarely sliced in half.
2. **Retrieval.** A BM25 index ranks chunks for a question. You implement the scoring formula, because an off-by-one in a length normaliser is invisible until you compute one score by hand.
3. **Context.** The best chunks are packed into a prompt context under a word budget, each labelled with its chunk id.
4. **Answer checking.** The (mock) model must cite chunk ids in square brackets. You extract those citations and compare them with the chunks the model was actually shown. A forged citation, an uncited sentence or an answer with no citation is withheld.
5. **Evaluation.** You measure whether the right section came back, using recall at k and mean reciprocal rank.

The model is `resources/handbook.py::make_model`, a deterministic mock with four behaviours: *faithful* (quotes the top chunk and cites it), *forger* (cites a chunk that was never retrieved), *uncited* and *mixed* (one cited and one uncited sentence). The handbook is generated, fictional text with seeded numbers.

> **Why this matters beyond this task.** A cited answer is only evidence if the citation is checked. Most production failures in RAG are not the model "being wrong" but the pipeline trusting a citation it never verified.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** overlapping word-window chunking with stable chunk ids.
2. **Compute** BM25 scores from the formula and verify them against hand calculations.
3. **Assemble** a context under a word budget without cutting chunks in half.
4. **Verify** citations against the retrieved set and withhold unverified answers.
5. **Explain**, with a small experiment, how chunk size and overlap change what a retriever can return.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `ragkit` in [`starter/ragkit/`](starter/ragkit/). Every function is specified exactly, so the public tests can check it exactly. Stubs raise `NotImplementedError("R<n>: ...")`.

| ID | Requirement |
|---|---|
| **R1** | `tokenize(text) -> list[str]`: lowercase, take maximal runs of `[a-z0-9]`, drop every token in `STOP` (provided). No stemming. |
| **R2** | `chunk_text(doc_id, text, size, overlap) -> list[{"id", "text", "start"}]`: split on whitespace; windows of `size` words advance by `size - overlap`; ids are `"<doc_id>#<i>"` from 0; `start` is the word offset. Stop at the window that reaches the last word, so no window lies wholly inside its predecessor. Empty text gives `[]`. `ValueError` if `size <= 0`, `overlap < 0` or `overlap >= size`. |
| **R3** | `BM25Index(chunks, k1=1.5, b=0.75)` with `score(query) -> {chunk_id: score}` and `search(query, k) -> [(chunk_id, score)]`. Per distinct query term *t* present in the corpus: `idf = ln(1 + (N - df + 0.5) / (df + 0.5))` and the term adds `idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / avgdl))`, where `dl` counts tokens after R1 and `avgdl` is their mean over all chunks. Repeated query words count once. `score` includes only chunks with a positive score; `search` sorts by score descending then id ascending. |
| **R4** | `build_context(hits, chunks_by_id, budget_words) -> (context, used_ids)`: walk `hits` in order; each chunk becomes `"[<id>] <text>"`; blocks are joined by a blank line; stop at the first chunk whose words would push the total above `budget_words` (do not skip ahead). |
| **R5** | `extract_citations(answer)` returns markers matching `[<letters/digits/_/->#<digits>]` in order of first appearance without duplicates. `check_answer(answer, used_ids)` returns `{"cited", "unsupported", "uncited_sentences", "verdict"}`. Sentences are split after `.`, `!` or `?` followed by whitespace; a sentence is uncited if it holds no marker. Verdict: `"forged"` if any cited id is not in `used_ids`; else `"grounded"` if there is at least one citation and no uncited sentence; else `"uncited"`. |
| **R6** | `answer_question(model, index, question, k, budget) -> {"answer", "used", "verdict", "abstained"}`. No hits, or a budget that fits no chunk, gives `"I don't know."` with verdict `"abstained"`. Otherwise call `model(question, context)`; if the check is not `"grounded"` return the fixed answer `"I could not verify an answer."` with the check's verdict. |
| **R7** | `evaluate(index, qa, k) -> {"recall_at_k", "mrr"}` at **document** level: a hit is a retrieved chunk whose id before `#` equals `gold`; the reciprocal rank uses the first such chunk. Empty `qa` gives zeros. |

### D.2 Engineering requirements (mandatory)

- Deterministic: no wall-clock time, no global random state, no network.
- Standard library only inside `ragkit`.
- At least **8 tests of your own** in `tests/test_member_*.py`, including a hand-computed BM25 score, a chunking edge case, and one test per answer-checking verdict.
- Do not import underscore-prefixed names from `resources/`. `REPORT.md` (from the [template](submission-template/REPORT.md)) carries every number you cite, reproducible with one command you document.

### D.3 Responsibility

The handbook is fictional, but a real cooperative's rules and member questions would include personal financial data under the Nigeria Data Protection Act 2023. In the report, write one short paragraph on what an assistant like this must not log (for example member names and balances typed into questions), and why an answer that cannot be verified should be refused rather than softened.

### D.4 Optional enhancements

- Add a second retriever (for example, character trigrams) and compare recall and MRR.
- Add a `--explain` function that prints, for one question, the top chunks, their scores and the verdict.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Mock model** | [`resources/handbook.py`](resources/handbook.py): `make_model(mode)` with modes `faithful`, `forger`, `uncited`, `mixed`; callable as `model(question, context)` |
| **Data** | `make_handbook(seed=7)` returns ten sections `{"id", "title", "text"}`; `make_questions(seed=7, vague=False)` returns 20 questions with the gold section id |
| **Provenance** | **Synthetic**, template-generated text with seeded numbers; no real cooperative, member or rule |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing committed beyond a 7 KB module |
| **Model access** | None. No network, key, GPU or download |

Hidden tests use other handbook seeds, other chunking and BM25 parameters, and an independent scoring oracle.

**Setup**

```bash
cd assessments/ai-engineering/tier-1/units/AI-05-rag-and-knowledge-systems/AI-T1-010-ask-the-ajo-handbook
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

Nothing in the graded path calls a hosted model. If you want to try your code against a real local open-weight model (for example through Ollama) or a hosted API afterwards, that is an optional extension; never put keys or outputs from such runs into the repository.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `ragkit/` package | R1 to R7 |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Your own checks, including a hand-computed BM25 score |
| 3 | `REPORT.md`, at most 900 words plus tables, from the [template](submission-template/REPORT.md) | Chunking experiment and short explanations; carries the AI-use declaration |
| 4 | A 5-minute walkthrough (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked (T) are checked by the public and hidden test suites; the rest are checked by hand.

1. (T) `pytest` passes the provided tests and your own from a clean environment.
2. (T) `BM25Index.score` matches the formula to 9 significant digits on the public tiny corpus and on hidden handbooks with other `k1`, `b` and chunk sizes.
3. (T) Chunking never produces a window longer than `size`, always ends on the last word, and advances by exactly `size - overlap`.
4. (T) With the `forger`, `uncited` and `mixed` mocks no answer text reaches the caller; with `faithful` every answer on 8 hidden-seed questions is `grounded`.
5. (T) On an unseen handbook seed, recall at 3 is at least 0.9 and MRR at least 0.8 (the reference scores 1.0 on both; the margin allows for a different but valid chunk size).
6. The report's chunking experiment is reproduced by one documented command, and its table and explanations agree with the code.

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

1. **Create your own private repository** named `clbg-AI-T1-010-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `ragkit/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Parameter sweep.** Vary `k1` and `b` and show when length normalisation helps or hurts on long versus short chunks.
2. **Query noise.** Use `make_questions(7, vague=True)` and add typos. Find where BM25 breaks and propose a fix that still runs offline.
3. **Real model check.** Replace the mock with a local open-weight model and see whether citations survive (optional; never graded).

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a short defence the assessor will (1) ask you to compute one BM25 score on a two-chunk corpus by hand; (2) ask why `build_context` stops at the first chunk that does not fit instead of skipping to a smaller one, and what would go wrong with skipping; (3) give an unseen change, such as citations written as `(S01#0)`, and ask which functions change and which tests would catch a mistake.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python, regular expressions, a first look at a ranking formula. |
| **New skill developed** | Seeing RAG as a chain of small, checkable functions, with the citation check as the control that makes answers evidence. |
| **Decisions the member must make** | Chunk size and overlap for the experiment, how to count fact sentences cut by a boundary, and what to log. |
| **What must be investigated independently** | How chunk boundaries cut fact sentences, and what the word budget does to the context. |
| **Why it is interesting** | The pipeline is tiny, yet it contains the real failure points: boundaries, ranking, truncation and forged citations. |
| **Evidence of competence** | Exact scores, correct edge cases, a verifier that withholds forged answers, and an experiment explained in the member's own words. |
| **Misconceptions exposed** | 'A citation means the answer is supported.' 'Bigger chunks are always better.' 'Retrieval quality is the model's job.' |
| **Preparation for later work** | Leads into AI-T2-008 (hybrid retrieval and injection in documents) and AI-T3-005 (evaluating RAG systems). |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
