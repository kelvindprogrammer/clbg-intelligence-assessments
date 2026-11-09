# AI-T1-015: The Forgotten Account Number: Context Budgeting for a Bank Support Chat

> *Forty messages into a dispute chat, the assistant asks the customer for the account number again. Build the context-window arithmetic that decides what stays, what is summarised and what is lost.*

![Format: Implementation (secondary: Investigation)](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T1-015` |
| **Title** | The Forgotten Account Number: Context Budgeting for a Bank Support Chat |
| **Subtrack** | AI Engineering |
| **Tier** | 1: Foundation |
| **Unit** | [AI-08: Context Engineering and Memory Systems](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 1 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8-12 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. The graded path uses a deterministic mock; the full test run takes under a minute |
| **Recommended prerequisites** | Python lists, dictionaries and regular expressions; pytest. No model knowledge is needed. |
| **Skills developed** | Token budgeting; newest-first truncation with pinning; extractive summary compaction; fact-retention measurement; explaining why summaries lose facts |
| **Technologies** | Python 3.10+, pytest (standard library only in your package) |

---

## B. Problem Statement

A bank's support assistant (fictional) runs on a model with a small context window. A customer opens a chat with "my account ends with 4821, I want to dispute a transfer of NGN 15000 on 3 May", and then the conversation drifts: waiting messages, "please hold on", "can you check again", status updates. By message forty the early lines no longer fit, the oldest messages are dropped, and the assistant asks for the account number again. The customer, on a bad mobile network at a market stall, gives up. Nothing in the model failed; the **context engineering** did.

You will build the arithmetic that decides what goes into each request. The brief fixes a token rule, a per-message overhead and a reply reserve, so every number is exact and testable. Starting from that you implement: a window fitter that keeps pinned messages and the newest unbroken run of history; a compaction step that replaces the dropped history by one bounded summary produced by a deterministic mock summariser (`resources/chat_mock.py`); a metric for how many key facts survive; and a report of where the tokens went. Then you measure, on seeded synthetic chats, what plain truncation, summarisation and pinning each forget, and explain the differences.

The summariser is deliberately lossy: it keeps only the first sentence of each message and cuts the result at a token limit. That is not a flaw in the mock; it is the lesson. A summary is a lossy compression chosen by someone, and you have to know what it dropped.

> **Why this matters beyond this task.** Every chat, agent and retrieval system eventually runs out of room. Whether the user's key facts survive that moment is decided by a few lines of budgeting code, not by the model.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. ****Implement** an explicit token rule and a window budget with a reply reserve.**
2. ****Fit** history into the window keeping pinned messages and the newest contiguous run, with explicit errors.**
3. ****Compact** dropped history into a bounded summary and show it stays inside the budget.**
4. ****Measure** fact retention for truncation, summarisation and pinning.**
5. ****Explain** what each strategy forgets and why, with evidence.**

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `ctxbudget` in [`starter/ctxbudget/`](starter/ctxbudget/). Interfaces are fixed; where the brief is silent the choices are yours to make and defend. Stubs raise `NotImplementedError("R<n>: ...")`.

A message is `{"id", "role", "text", "pin"}`; `system` is a string. Every message costs its text tokens plus `OVERHEAD = 4`. The system prompt costs the same way. The mock's interface is in [`resources/chat_mock.py`](resources/chat_mock.py).

| ID | Requirement |
|---|---|
| **R1** | `count_tokens(text) -> int`: the number of matches of the regular expression `\w+\|[^\w\s]` (words, and single punctuation marks). |
| **R2** | `message_cost(msg) -> int`: `count_tokens(text) + 4`. |
| **R3** | `fit_window(system, messages, budget, reply_reserve) -> {"kept", "dropped", "used"}`. Available space is `budget - reply_reserve - cost(system)`; raise `ValueError("system_too_large")` if that is negative. Pinned messages are always kept and charged first; raise `ValueError("pinned_overflow")` if they do not fit. Then walk the unpinned messages from newest to oldest, keeping each while it fits and **stopping at the first that does not** (no holes). `kept` and `dropped` are message ids in original order; `used` is the tokens of system, pinned and kept messages. Do not mutate the input. |
| **R4** | `compact(system, messages, budget, reply_reserve, summariser) -> {"messages", "summarised", "used"}`. If everything fits, return the messages unchanged, `summarised == []`. Otherwise let `allow = available // 4` (integer division, available as in R3), run R3 with `budget - allow`, and put the dropped unpinned messages' texts through `summariser.summarise(texts, allow - 4 - 3)`. Prepend one message `{"id": "summary", "role": "system", "text": "[summary] " + summary, "pin": False}` (omit it if there is nothing dropped or `allow - 7 <= 0`). `summarised` lists the dropped ids; `used` is the real token total of system plus the returned messages, and must never exceed `budget - reply_reserve`. |
| **R5** | `facts_retained(context, facts) -> float`: the fraction of fact strings that occur (case-insensitive) in the text of at least one context message; `1.0` for an empty fact list. |
| **R6** | `budget_report(system, messages, budget, reply_reserve) -> dict` with `system` (cost), `pinned` (cost of pinned messages), `history` (cost of the others), `reserve`, `free` (`budget - reserve - system - pinned - history`, possibly negative) and `over_by` (`max(0, -free)`). |

### D.2 Engineering requirements (mandatory)

- Deterministic: no wall-clock time, no global random state, no network. Everything randomised takes an explicit seed.
- At least **8 tests of your own** in `tests/test_member_*.py`: including an empty message list, a message longer than the whole budget, and a conversation where every message is pinned.
- Do not import names beginning with an underscore from `resources/` or read the mock's internals; the mock is a stand-in for an opaque service.
- `REPORT.md` (from the [template](submission-template/REPORT.md)) carries every number you cite, reproducible with one command you document.

### D.3 Responsibility

Support chats contain account fragments, amounts and sometimes full names, which are personal and financial data under the Nigeria Data Protection Act 2023. In the report, write one paragraph on what a summary may keep (and what it must redact), how long summaries and dropped history should be retained, and why a summary that lost the amount can cause a wrong action rather than just an annoyed customer. State what you would pin and why.

### D.4 Optional enhancements

- Pin only the messages that contain digits and measure the retention against the cost in tokens.
- Add a second summariser that keeps the last sentence instead of the first and compare retention.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Mock** | [`resources/chat_mock.py`](resources/chat_mock.py): `ExtractiveSummariser().summarise(texts, max_tokens)` and `make_conversation(seed, n_turns)` returning messages and the planted facts |
| **Data** | `make_conversation(seed, n_turns=30)`: a fictional dispute chat whose first message states an account suffix, an amount and a date, followed by filler turns |
| **Provenance** | **Synthetic**; fictional names and amounts, no real person, account or business |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing committed beyond a few KB of Python |
| **Model access** | None. No network, key, GPU or download |

Hidden tests use other seeds and budgets, pinned messages in the middle, tiny budgets, awkward punctuation, and invariants over many conversations.

**Setup**

```bash
cd assessments/ai-engineering/tier-1/units/AI-08-context-engineering-and-memory/AI-T1-015-the-forgotten-account-number
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

Nothing in the graded path calls a hosted model. Trying your code against a real local open-weight model or a Model Context Protocol server afterwards is an optional extension; never put keys or outputs from such runs into the repository.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `ctxbudget/` package | R1 to R6 |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Your own scripted-behaviour tests |
| 3 | `REPORT.md` (at most 700 words), from the [template](submission-template/REPORT.md) | The retention table and the answers to its questions; carries the AI-use declaration |
| 4 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked (T) are checked by the public and hidden test suites; the rest are checked by hand.

1. (T) `pytest` passes the provided tests and your own from a clean environment.
2. (T) `count_tokens`, `message_cost` and `budget_report` return the exact specified values, including on empty and punctuated text.
3. (T) `fit_window` keeps pinned messages, never leaves a hole in the history, never exceeds the budget, raises the two specified errors and does not mutate its input.
4. (T) `compact` returns the input unchanged when it fits, and otherwise a single leading summary message with `used <= budget - reply_reserve` for every seed and budget tested, including tiny budgets.
5. (T) Over 20 hidden seeds at budget 300 and reserve 40, mean fact retention is exactly 0 for truncation, strictly between 0 and 1 for summarisation and exactly 1 for pinning the first message. *Justification:* the reference gives these values because the facts live only in the first user message and the summariser keeps only first sentences.
6. The report presents the retention table for at least 3 budgets and explains in words why the summary kept some facts and lost others.

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

1. **Create your own private repository** named `clbg-AI-T1-015-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `ctxbudget/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Smarter summary.** Write a summariser that keeps every number and date and measure retention against tokens spent.
2. **Priority eviction.** Replace newest-first with a score (recency plus pins plus digits) and show when it beats it.
3. **Real tokeniser.** Compare your rule with a real tokeniser on Yoruba and Pidgin text; optional, never graded.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why `fit_window` stops at the first message that does not fit rather than skipping it; (2) ask what the reply reserve protects against; (3) give an unseen change, such as the summary taking `allow = available // 3`, and ask you to make it live and say what changes in the retention table.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python lists, regular expressions and pytest. No model internals. |
| **New skill developed** | Treating the prompt as a budgeted resource with a reply reserve, and measuring what each budgeting strategy loses. |
| **Decisions the member must make** | How to order the checks, what to charge to pinned messages, how to keep the summary inside the budget and what facts to measure. |
| **What must be investigated independently** | Why the summary keeps the account suffix but not the amount, and what that implies for the summariser design. |
| **Why it is interesting** | The failure is silent: the model answers fluently with a missing fact, and the customer pays for it. |
| **Evidence of competence** | Exact budget arithmetic, no holes, no overflow, and a retention table that matches the explanation. |
| **Misconceptions exposed** | 'Summaries keep what matters.' 'Truncation is harmless if the model is smart.' 'Bigger windows remove the problem.' |
| **Preparation for later work** | Leads into AI-T2-015 (retrieval-backed memory with eviction) and AI-T3-011 (evaluating compaction strategies). |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
