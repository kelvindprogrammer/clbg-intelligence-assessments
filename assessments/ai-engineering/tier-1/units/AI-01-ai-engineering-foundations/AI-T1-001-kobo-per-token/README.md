# AI-T1-001: Kobo per Token: Building a Byte-Pair Tokeniser for a Lagos SMS Assistant

> *An SMS assistant bills by the token. Build the tokeniser yourself and find out why a Yoruba message costs several times what the same English message does.*

![Format: Implementation (secondary: Investigation)](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T1-001` |
| **Title** | Kobo per Token: Building a Byte-Pair Tokeniser for a Lagos SMS Assistant |
| **Subtrack** | AI Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [AI-01: AI Engineering Foundations and Model Fundamentals](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8-12 hours over 1 week |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. The graded path uses a deterministic mock; the full test run takes under a minute |
| **Recommended prerequisites** | Python functions, dictionaries and counting with `collections.Counter`; reading a short pytest file. No machine-learning background needed |
| **Skills developed** | Byte-pair encoding from first principles; deterministic tie-breaking; round-trip invariants; token-based pricing; reasoning about multilingual fairness in tokenisation |
| **Technologies** | Python 3.10+, numpy (installed only), pytest |

---

## B. Problem Statement

Eko Connect (fictional) is a Lagos mobile operator. Its SMS assistant answers questions about airtime, data bundles and balances, and the language model behind it bills **per token**: 2,500 kobo per 1,000 tokens. Customers write in English, Nigerian Pidgin and Yoruba. After a month, the finance team notices that Yoruba conversations cost far more per message than English ones, even when the messages say the same thing, and that some Yoruba users abandon sessions that cost them more than a recharge.

A tokeniser splits text into pieces before the model sees it, and the number of pieces is what gets billed. You will build the simplest widely used trainable tokeniser, **byte-pair encoding (BPE)**, from scratch. You learn merges from a small corpus, encode and decode text, build a vocabulary, and price messages. Then you use your own tool to investigate the finance team's observation: what happens when the training corpus is dominated by English, and what a rebalanced corpus changes.

This is a Tier 1 assessment: the rules are precise and fully specified, and your first job is to implement them exactly. The second job is to explain what you measured, in your own words, in a one-page report.

> **Why this matters beyond this task.** Context limits, latency and price are all counted in tokens. Anyone building on language models needs to know what a token is, why it is not a word, and why the same sentence can cost very different amounts in different languages.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** byte-pair-encoding training with exact, reproducible tie-breaking.
2. **Encode and decode** text so that decoding inverts encoding, and test that property.
3. **Build** a vocabulary with stable ids from a corpus and a merge list.
4. **Price** a message in integer kobo and compute fertility (tokens per word).
5. **Measure** how the training mix changes cost across languages, and explain the result without overclaiming.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `tokenlab` in [`starter/tokenlab/`](starter/tokenlab/). Interfaces are fixed; where the brief is silent the choices are yours to make and defend. Stubs raise `NotImplementedError("R<n>: ...")`.

| ID | Requirement |
|---|---|
| **R1** | `train_bpe(corpus, num_merges) -> list[(str, str)]`. Words are the whitespace-separated pieces of each line. Each word becomes its characters plus the end marker `"</w>"` as a final separate symbol. Word counts are corpus frequencies. Repeat up to `num_merges` times: count adjacent symbol pairs weighted by word frequency; pick the pair with the highest count, **ties broken by the lexicographically smallest pair `(left, right)`**; merge it left to right, without overlapping, in every word. Stop early if no pairs remain or the best count is below 2. Do not modify the input. |
| **R2** | `encode(text, merges) -> list[str]`. Split on whitespace, start each word as characters plus `"</w>"`, apply the merges **in learned order**, and concatenate the words' symbols. Characters never seen in training stay as single-character tokens. |
| **R3** | `decode(tokens) -> str` returns the text with single spaces: `decode(encode(t, m)) == " ".join(t.split())` for every `t`. `decode([])` is the empty string. |
| **R4** | `build_vocab(corpus, merges) -> dict[str, int]`. The base symbols (every character and `"</w>"` appearing in the corpus words) sorted ascending get ids `0..k-1`; each merged token then follows in merge order (skipping duplicates). |
| **R5** | `token_cost(text, merges, kobo_per_1k_tokens) -> int`: `ceil(n_tokens * price / 1000)` using integer arithmetic only. |
| **R6** | `fertility(texts, merges) -> float`: total tokens divided by total whitespace-separated words over all texts. |

### D.2 Engineering requirements (mandatory)

- Deterministic: no wall-clock time, no global random state, no network. Everything randomised takes an explicit seed.
- At least **8 tests of your own** in `tests/test_member_*.py`; include a round-trip test on Yoruba text and a tie-break test you hand-computed.
- No third-party tokeniser or NLP library; standard library and numpy only.
- `REPORT.md` (from the [template](submission-template/REPORT.md)) carries every number you cite, reproducible with one command you document.

### D.3 Responsibility

The corpus is synthetic and no real message is used. In the report, write one paragraph on who pays when a tokeniser is trained mostly on one language: name the customers affected, the harm (cost, truncated context, worse answers) and one mitigation you could check with your tool. Say what you could *not* conclude from a synthetic corpus of a few hundred lines. Real SMS logs are personal data under the Nigeria Data Protection Act 2023: say in one sentence what you would require before training on them.

### D.4 Optional enhancements

- Compare the number of merges needed for each language to reach fertility below 1.5.
- Add a `<unk>` policy and show what it does to the round-trip guarantee.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/corpus.py`](resources/corpus.py): `make_corpus(seed=2026, n_en=400, n_pcm=100, n_yo=40)` returns `{"en": [...], "pcm": [...], "yo": [...]}` (lists of lines) |
| **Provenance** | **Synthetic**: random word sequences from three small hand-written vocabularies, with Yoruba tone-marked characters; no real message, customer or operator |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing is committed; `python resources/corpus.py --out DIR --seed 2026` writes about 60 KB of JSON |
| **Model access** | None. Tokenisation is implemented from scratch; no model is called |

Hidden tests use other random corpora and unseen Unicode text.

**Setup**

```bash
cd assessments/ai-engineering/tier-1/units/AI-01-ai-engineering-foundations/AI-T1-001-kobo-per-token
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
| 1 | `tokenlab/` package | R1 to R6 |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Round-trip, tie-break and cost tests of your own |
| 3 | `experiments.py` | Reproduces the fertility and cost table in the report |
| 4 | `REPORT.md` (at most 700 words plus a table), from the [template](submission-template/REPORT.md) | One-page explanation; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked (T) are checked by the public and hidden test suites; the rest are checked by hand.

1. (T) `pytest` passes the provided tests and your own from a clean environment.
2. (T) `train_bpe` reproduces the specified merge order, including ties and the early stop, on corpora it has never seen (hidden tests compare to an independent implementation).
3. (T) `encode`/`decode` round-trip on unseen text, including characters absent from training and multiple spaces.
4. (T) `build_vocab`, `token_cost` and `fertility` follow R4 to R6 exactly (integer kobo, no float rounding).
5. (T) With 200 merges learned from the English lines only, Yoruba fertility is at least 3.0 times English fertility. *Justification:* the reference gives about 4.6; most characters in Yoruba words are never merged. With a balanced training mix (60 English, 60 Pidgin, all Yoruba lines) the ratio is at most 1.6 (reference about 1.0).
6. The report presents the fertility and cost table by language for both training mixes and explains the gap without claiming more than a synthetic corpus supports.

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

1. **Create your own private repository** named `clbg-AI-T1-001-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `tokenlab/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Byte fallback.** Operate on UTF-8 bytes instead of characters and show that nothing is ever unknown, at what cost in fertility.
2. **Merge budget.** Plot fertility against number of merges per language and find where extra merges stop paying.
3. **Real tokeniser comparison.** Run the same texts through a tokeniser of a local open-weight model and compare the shape of the gap (optional; not required or graded).

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask you to trace the first three merges on a tiny corpus by hand; (2) ask why `decode(encode(x))` loses double spaces and whether that matters; (3) give an unseen change, such as breaking ties by the rightmost pair or pricing per 1,000 characters, and ask what in your outputs would change.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python data structures and counting. No linear algebra, no neural networks. |
| **New skill developed** | Turning a written algorithm into exact code, and treating a tokeniser as a measurable component with properties you can test. |
| **Decisions the member must make** | Data structures for pair counting; how to merge non-overlapping occurrences; how to organise the experiment and what to claim from it. |
| **What must be investigated independently** | Why a tokeniser trained on English leaves Yoruba characters unmerged, and how much rebalancing fixes it. |
| **Why it is interesting** | The pricing complaint is real for many deployed systems; the member reproduces its mechanism in about 80 lines. |
| **Evidence of competence** | Merge lists identical to an independent implementation on unseen corpora; a defensible fertility table. |
| **Misconceptions exposed** | 'A token is a word.' 'Tokenisation is neutral across languages.' 'More merges is always better.' |
| **Preparation for later work** | Leads into AI-01 Tier 2 sampling internals, AI-02 prompt budgets and cost control, and ML-08 language-model work. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
