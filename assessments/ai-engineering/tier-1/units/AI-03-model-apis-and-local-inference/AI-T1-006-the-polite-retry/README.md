# AI-T1-006: The Polite Retry: A Resilient Client for a Flaky Model API

> *A hosted model fails in five different ways. Only some of them deserve a second attempt, and none deserve a stampede.*

![Format: Implementation (secondary: Investigation)](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T1-006` |
| **Title** | The Polite Retry: A Resilient Client for a Flaky Model API |
| **Subtrack** | AI Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [AI-03: Model APIs and Local Inference](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 1 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8–12 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. Full test run under 2 minutes |
| **Recommended prerequisites** | Python exceptions, classes and dictionaries; reading JSON; running pytest. No prior API experience |
| **Skills developed** | Retry with exponential backoff and jitter; honouring Retry-After; classifying errors as retryable or not; tolerant parsing of model output; token and cost accounting; handling broken streams |
| **Technologies** | Python 3.10+, the standard library only, pytest |

---

## B. Problem Statement

*Sauki Pay* (fictional) is a Lagos wallet app. Its support assistant sends each customer message to a hosted language model and expects a small JSON object back: `{"intent": ..., "reply": ...}`. During a salary-day surge the model provider misbehaves in ways the team has seen before:

- **429 rate limits** that carry a `retry_after` hint (seconds).
- **Timeouts**, where no reply ever arrives.
- **5xx server errors**, usually brief.
- **Malformed replies**: the model returns JSON cut off halfway, or wraps correct JSON in a markdown code fence.
- **400 bad requests**, caused by the app's own bug, which will never succeed however often they are retried.

The current client retries every failure immediately, three times, in a tight loop. On salary day every client retried at the same instant, the provider's rate limiter tripped again, and the app produced a 40-minute outage that began as a 90-second blip. You will write the replacement client.

Everything runs against a **deterministic mock provider** (`resources/mockllm.py`). It follows a *script* of events such as `["timeout", "rate:7", "malformed", "ok"]`, uses a virtual clock so nothing really sleeps, and records every call. There is no network, no key and no cost. The mock's behaviour is documented in its module docstring and in §E. This is a Tier 1 task: the policy is fully specified below, and your job is to implement it exactly and then explain what you saw.

> **Why this matters beyond this task.** Every production system that calls a model API needs this layer. Most real incidents with hosted models are caused by the *client's* reaction to errors, not by the errors themselves.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** exponential backoff with full jitter exactly as specified, using an injected random source so behaviour is reproducible.
2. **Classify** provider failures: retry rate limits, timeouts, server errors and malformed replies; never retry a bad request.
3. **Honour** a provider's `Retry-After` hint without ever waiting less than the backoff you computed.
4. **Parse** model output that is sometimes fenced, sometimes truncated, and decide when that is a failure.
5. **Account** for tokens and money, including the surprising case where a useless reply is still billed.
6. **Explain**, with numbers from your own runs, why synchronised retries make an outage worse.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `llmclient` package in [`starter/llmclient/client.py`](starter/llmclient/client.py). Signatures are fixed. Use only the standard library.

| ID | Requirement |
|---|---|
| **R1** | `backoff_delay(attempt, base, cap, rng) -> float` returns `rng.random() * min(cap, base * 2**attempt)`, where `attempt` is the 0-based index of the attempt that just failed. This is "full jitter". |
| **R2** | `parse_json_reply(text) -> dict` strips surrounding whitespace and one optional markdown fence (` ``` ` or ` ```json `, case-insensitive), parses JSON, and returns the result. Anything that is not a JSON **object** (truncated text, a list, a string, an empty fence) raises `MalformedReply`, a subclass of `ValueError`. |
| **R3** | `ResilientClient(provider, clock, max_attempts=5, base=0.5, cap=30.0, seed=0, ledger=None).complete(prompt, max_tokens=64) -> Reply(data, attempts)`. Each attempt calls `provider.complete`. A returned response is parsed with R2. **Retry** on `RateLimitError`, `ProviderTimeout`, `ServerError` and `MalformedReply`. **Do not retry** `BadRequestError`: re-raise it at once, with no sleep. After a retryable failure that is *not* the last attempt, compute `delay = backoff_delay(attempt, ...)` using one draw from a `random.Random(seed)` created in the constructor, and call `clock.sleep(delay)`; for a rate limit, sleep `max(delay, retry_after)` instead. Never sleep after the final failed attempt. When all attempts fail raise `RetriesExhausted(attempts, last_error)`. A fenced reply is a success, not a failure. |
| **R4** | `collect_stream(chunks) -> StreamResult(text, complete)` joins an iterator of text chunks. If the iterator raises a `ProviderError` part-way, return the text received so far with `complete=False`; never let that error escape. |
| **R5** | `CostLedger(price_in, price_out)` with `record(response)` and `cost_kobo`. Prices are kobo per 1,000 tokens: `cost_kobo = (prompt_tokens * price_in + completion_tokens * price_out) / 1000`. The client records **every response the provider delivered**, including malformed ones (the provider billed you for them), and nothing else (errors and timeouts deliver no response). |

### D.2 Engineering requirements (mandatory)

- Deterministic: all randomness comes from the `random.Random(seed)` you create; the same seed and script must give the same sleeps.
- No real sleeping and no network. All waiting goes through `clock.sleep`.
- At least **8 tests of your own** in `tests/test_member_*.py`, including one that proves a bad request is not retried and one that proves no sleep follows the final failed attempt.
- `experiments.py` prints a table that answers the §G question on retry storms (see §F).

### D.3 Responsibility

The mock data contains no personal information. In your report, add one short paragraph on what a real support assistant must not send to a third-party model provider (account numbers, BVNs, full chat histories) under the Nigeria Data Protection Act 2023, and why a retry layer that logs full prompts on every failure could itself leak personal data. Keep API keys out of code and logs.

### D.4 Optional enhancements

- Add a `max_total_wait` budget that stops retrying when the cumulative sleep would exceed it.
- Add a circuit breaker that fails fast after N consecutive exhausted calls.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Mock provider** | [`resources/mockllm.py`](resources/mockllm.py): `MockProvider(script, clock, price_in, price_out)`, `VirtualClock`, the error classes and `Response` |
| **Provenance** | **Synthetic and deterministic**; there is no real model, customer or provider behind it |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Events** | `ok`, `fence`, `malformed`, `rate:<s>`, `timeout`, `server`, `bad`, and `cut` (streams only). One event is consumed per call; an empty script means `ok` |
| **Time** | Virtual. `clock.sleep(s)` advances `clock.now()` and appends to `clock.sleeps`; a timeout costs 10 virtual seconds |
| **Tokens** | Whitespace-separated words. Failed calls deliver no response and are not billed; a `malformed` reply *is* billed |
| **Size** | Nothing is committed beyond the code |

Hidden tests use other scripts, seeds, prices and a different provider object with the same interface, so rely on the interface, not on the mock's internals.

**Setup**

```bash
cd assessments/ai-engineering/tier-1/units/AI-03-model-apis-and-local-inference/AI-T1-006-the-polite-retry
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `llmclient/` package | Backoff, parser, retrying client, stream collector, cost ledger |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Your own evidence, including the two named in §D.2 |
| 3 | `experiments.py` | Reproduces the storm comparison table |
| 4 | `REPORT.md`, at most 900 words plus tables, from the [template](submission-template/REPORT.md) | Explanations and AI-use declaration |
| 5 | A 5-minute technical defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `backoff_delay` and `parse_json_reply` match the specification on all provided and hidden cases, including the cap and empty fences.
3. ⚙ The client's sequence of sleeps equals the sequence derived from `random.Random(seed)` for any script (hidden tests use other scripts, seeds, base and cap).
4. ⚙ `BadRequestError` is raised after exactly one provider call; `RetriesExhausted` reports the true attempt count and last error; there is never a sleep after the last attempt.
5. ⚙ The ledger bills malformed replies and never bills errors; costs match hand computation at other prices.
6. ⚙ A stream cut part-way returns the partial text with `complete=False`.
7. ✍ **Storm experiment.** Simulate 200 clients that all fail at the same virtual instant. Compare (a) immediate retries, (b) backoff without jitter and (c) your full jitter, and report how many retry requests land in each one-second window. The report must show that (c) spreads the load and say why (b) does not.
8. ✍ The report explains in your own words why a truncated reply is retried but a fenced one is not, and what the malformed reply cost in kobo.

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

1. **Create your own private repository** named `clbg-AI-T1-006-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `llmclient/` (your package), `tests/` (provided tests plus your own), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Retry budgets.** Limit retries to a fraction of recent traffic and show why that protects the provider.
2. **Idempotency.** Explain what extra care is needed if the call had side effects, such as sending money.
3. **Real provider.** Point the same client at a local open-weight model server (for example via Ollama) and compare the failure modes you can and cannot reproduce. Not required, never graded on the offline path.
4. **Hedged requests.** Send a second request after a latency threshold and measure the cost trade-off on the mock.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why a deterministic backoff without jitter is dangerous when thousands of clients fail together; (2) ask why a `malformed` reply appears on the invoice and a `timeout` does not; (3) give an unseen modification, for example "treat rate limits as non-retryable once `retry_after` exceeds 60 seconds" or "cap total wait at 20 seconds", and ask you to describe the code change and its test.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python exceptions, JSON, pytest. No networking or machine-learning knowledge. |
| **New skill developed** | Treating a model API as an unreliable dependency and writing the client layer that makes it dependable. |
| **Decisions the member must make** | How to structure the attempt loop; where to count a billed response; what to test. |
| **What must be investigated independently** | Why the storm happens; the brief only reports that it did. |
| **Why it is interesting** | The most expensive failure in the mock is a reply that arrives, is useless and is billed anyway. |
| **Evidence of competence** | Exact sleep sequences, error classification and ledger totals on hidden scripts. |
| **Misconceptions exposed** | 'Retry everything quickly.' 'Backoff alone prevents storms.' 'A failed call costs nothing.' |
| **Preparation for later work** | Leads into provider abstraction and fallbacks (AI-03 Tier 2), serving trade-offs (AI-03 Tier 3) and agent reliability (AI-07, AI-13). |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
