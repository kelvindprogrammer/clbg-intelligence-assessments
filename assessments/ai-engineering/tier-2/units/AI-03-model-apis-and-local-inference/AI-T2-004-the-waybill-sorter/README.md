# AI-T2-004: Six Hundred Waybills, Two Providers, One Outage: Batching, Caching and Failover for a Freight Classifier

> *A logistics firm must label an overnight pile of waybills through two model providers with different limits, prices, quality and an outage. Make it cheap, fast and accurate, and prove the trade-offs.*

![Format: Optimization (secondary: System-design)](https://img.shields.io/badge/format-optimization-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T2-004` |
| **Title** | Six Hundred Waybills, Two Providers, One Outage: Batching, Caching and Failover for a Freight Classifier |
| **Subtrack** | AI Engineering |
| **Tier** | 2: Applied Engineering and Independent Problem-Solving |
| **Unit** | [AI-03: Model APIs and Local Inference](../README.md) |
| **Format** | Optimization (secondary: System-design) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14–20 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. Full test run under 2 minutes |
| **Recommended prerequisites** | Dictionaries, classes and exceptions; JSON; the idea of rate limits. Recommended: AI-T1-006 |
| **Skills developed** | Sliding-window rate limiting; request batching and its quality cost; normalised caching; provider failover with cooldowns; budget enforcement; measuring cost, latency and accuracy together |
| **Technologies** | Python 3.10+, the standard library only, pytest |

---

## B. Problem Statement

*Haulgate Logistics* (fictional) moves goods between Lagos, Kano, Onitsha and Ibadan. Every night 600 free-text waybill descriptions arrive, such as `urgent: 12 ripe plantain` or ` 50 LAND TITLE COPIES, 2 cartons.`, and each must be labelled with one of five categories (electronics, perishables, documents, fashion, building materials) before dispatchers arrive. A language model does the labelling through a hosted API. The current script sends one request per waybill to the cheap provider and takes half an hour and a surprising bill.

Two providers are available, and the **mock** in `resources/mockllm.py` simulates both:

- **fastcheap**: cheap, but limited to 20 requests and 2,500 prompt tokens per sliding minute, and it has a scheduled outage. Its accuracy falls as an item sits later in a batch.
- **steady**: about four times the price, much higher limits, slightly better and flatter accuracy, but slower per call.

The data has three planted properties you must discover rather than be told how to exploit: about a third of the waybills are repeats with different capitalisation, spacing and punctuation; every call carries a fixed instruction overhead that batching amortises; and quality decays with position inside a batch, so bigger batches are cheaper but less accurate. Some replies are truncated JSON (still billed). Each mock window is a true sliding window: a request expires 60 virtual seconds after it was sent.

The task is partially specified. The tests fix the interfaces, the limiter semantics and the acceptance bars. **You choose** the batch size, the failover and cooldown policy, how to treat malformed replies, and how to demonstrate that your choices are good. Nothing here needs a network, a key or money.

> **Why this matters beyond this task.** Cost, throughput and quality of a model-backed pipeline are decided by the layer around the model: limits, batching, caching and fallbacks. Teams routinely pay 3 to 10 times more than necessary because nobody measured this layer.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Mirror** a provider's sliding-window request and token limits in a client-side limiter so that no call is ever rejected.
2. **Deduplicate and cache** work on a normalised key, and quantify what that saves.
3. **Batch** several items per prompt, and *measure* where quality starts to decay instead of guessing.
4. **Fail over** between providers with different prices, limits and reliability, and return to the cheap one when it recovers.
5. **Enforce** a spend budget and reconcile your own accounting with the provider's billing.
6. **Defend** a configuration with a comparison against a naive baseline on cost, time and accuracy.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `gateway` package in [`starter/gateway/core.py`](starter/gateway/core.py). Use only the standard library. Providers are `mockllm.MockProvider` objects (or anything with the same attributes: `name`, `rpm`, `tpm`, `price_in`, `price_out`, `complete(prompt)`), ordered by preference.

| ID | Requirement |
|---|---|
| **R1** | `normalise_key(text)`: lowercase, collapse runs of whitespace to one space, strip the characters ` .,;:!?` from both ends. |
| **R2** | `plan_batches(texts, size)`: unique normalised keys in first-seen order, split into consecutive lists of at most `size`. |
| **R3** | `RateLimiter(rpm, tpm, clock)` with `wait_time(tokens)`, `commit(tokens, at=None)` and `acquire(tokens)`. A committed request is **live** until `now >= sent_at + 60 - 1e-6`. A request is admissible if live requests plus one do not exceed `rpm` and live prompt tokens plus `tokens` do not exceed `tpm`. `wait_time` returns the smallest wait after which it is admissible (0.0 if now); it must raise `ValueError` if `tokens > tpm`. `acquire` sleeps on `clock` then commits. |
| **R4** | `Gateway(providers, clock, batch_size=5, cooldown=30.0, budget_kobo=None).classify_all(texts) -> list[str]` returns one valid label per input, in order. It must dedupe and cache on `normalise_key` (the cache persists across calls), batch uncached keys, respect every provider's limits **proactively** (zero rate-limit rejections), fail over to the next provider on `ServerError` or timeout and probe the preferred provider again after `cooldown`, wait rather than crash if every provider is down, and survive malformed or wrong-length replies. Build prompts with `mockllm.build_prompt`. |
| **R5** | Budget: when `budget_kobo` is set, never start a call once spent cost has reached it; raise `BudgetExceeded`. Spent cost is computed from the usage in each delivered response and the provider's prices, and must reconcile with the provider's own `billed_kobo`. |
| **R6** | `choose_batch_size(make_provider, dev_texts, dev_labels, candidates, min_accuracy)` runs your own gateway on labelled development data using **fresh providers** from `make_provider()` and returns a batch size justified by the measured accuracy. State in the report why you chose your rule, and how the noise in a small development set can mislead it. |

`gateway.stats` must expose `cost_kobo`, `calls` (provider name to accepted calls), `cache_hits` (inputs served without a new call) and `makespan_s` (virtual seconds spent inside `classify_all`, cumulative).

### D.2 Engineering requirements (mandatory)

- Deterministic and offline: all waiting goes through `clock.sleep`; no real time, no network.
- Every provider goes through the same request path; no provider-specific branches except configuration.
- Never read a mock's private attributes in the library (the tests may).
- At least **10 tests of your own** in `tests/test_member_*.py`, including a limiter boundary test (a request is admissible exactly 60 s after it was sent) and a failover-then-recovery test.
- `experiments.py` regenerates every table in `REPORT.md`, including a batch-size sweep, a cache on/off comparison and the naive baseline, on **at least 3 generator seeds**.

### D.3 Responsibility

Waybill text can contain names, phone numbers and addresses. In the report, write one paragraph on what you would strip or hash before sending free text to a third-party provider, what the Nigeria Data Protection Act 2023 implies about sending customer data abroad, and why caching raw prompts to disk could itself create a data store you are responsible for. The mock data is fictional.

### D.4 Optional enhancements

- Cost-aware routing: send easy-looking items to the cheap provider and the rest to the steady one.
- Adaptive batch size that shrinks after a quality alarm from a small audited sample.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Mock providers** | [`resources/mockllm.py`](resources/mockllm.py): `MockProvider(name, truth, clock, rpm, tpm, price_in, price_out, base_s, per_token_s, acc, decay, free, outages, malformed_rate, seed)`, `VirtualClock`, `build_prompt`, `norm`, error classes. The module docstring is the specification of its limits, outages, billing and latency |
| **Data** | [`resources/waybills.py`](resources/waybills.py): `make_waybills(n=600, seed=2026) -> (texts, labels)`; `python resources/waybills.py --out DIR --seed 2026` writes a CSV of about 30 KB |
| **Provenance** | **Synthetic and deterministic**; fictional company and goods, no real customer data |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Reference scenario** | `fastcheap` (20 rpm, 2,500 tpm, 20/60 kobo per 1k tokens, outage from t=80 to t=170) then `steady` (60 rpm, 20,000 tpm, 80/240); the tests build it for you |
| **Tokens** | Whitespace-separated words, in both prompts and replies |

Hidden tests use other seeds, limits, prices, outage windows, steeper quality decay and a foreign provider object that returns wrong-length replies. Rely on the provider interface in §D.1, not on the mock's internals.

**Setup**

```bash
cd assessments/ai-engineering/tier-2/units/AI-03-model-apis-and-local-inference/AI-T2-004-the-waybill-sorter
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `gateway/` package | Normalisation, batching, limiter, gateway, budget and batch-size selection |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Includes the limiter boundary and failover-recovery tests |
| 3 | `experiments.py` | Reproduces the sweep, cache and baseline tables on 3 or more seeds |
| 4 | `REPORT.md`, at most 1,500 words plus tables, from the [template](submission-template/REPORT.md) | Decision memo for the logistics operations lead; carries the AI-use declaration |
| 5 | A 5-minute technical defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `normalise_key`, `plan_batches` and `RateLimiter` match the written semantics, including the 60-second boundary and the token window removing the oldest requests first.
3. ⚙ Across the reference scenario and every hidden scenario, **no provider records a rate-limit rejection** (`violations == 0`), including after an outage and when all providers are down.
4. ⚙ Labels are returned in input order and are valid; repeated descriptions cost nothing extra; the cache persists across calls; wrong-length and truncated replies are survived.
5. ⚙ **Performance.** On the reference scenario your gateway reaches accuracy at least **0.95**, cost at most **0.6x** and makespan at most **0.25x** of the naive one-call-per-waybill loop on the cheap provider. *Justification:* the reference reaches about 0.98 accuracy, 0.37 to 0.5x cost (the fallback provider is dear) and 0.07 to 0.1x time; the bars leave room for different but reasonable policies. Hidden scenarios use bars of 0.93, 0.7x and 0.3x.
6. ⚙ Budget stops spending within one call of the limit and your cost reconciles with the providers' `billed_kobo`.
7. ✍ The report shows, with numbers on 3 or more seeds, how much each lever (cache, batching, failover) contributes to cost, time and accuracy, and where batching stops paying.
8. ✍ The report explains the uncertainty in choosing the batch size from a small labelled sample and what you did about it.

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

1. **Create your own private repository** named `clbg-AI-T2-004-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `gateway/` (your package), `tests/` (provided tests plus your own), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Concurrency.** Extend the virtual-time model with parallel workers and show whether rpm or tpm becomes the binding limit.
2. **Quality audit.** Spend a small fixed budget on re-labelling a random sample on the steady provider to estimate the live error rate, and decide when to shrink batches.
3. **Real local model.** Replace one mock with a small open-weight model served locally (for example through Ollama) and compare measured latency with the mock's assumptions. Optional; never required for grading.
4. **Hedging.** Send the same batch to both providers after a latency threshold and compute when it pays.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why the limiter mirrors the provider's window instead of reacting to 429s, and what could still go wrong if two processes share one key; (2) ask what the cost of a truncated reply is and how your batch-size rule is affected by it; (3) give an unseen modification, for example "the cheap provider's tpm halves" or "the steady provider doubles its price", and ask which of your choices changes and how you would verify it.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python classes and exceptions, JSON, the idea of rate limits. No machine-learning knowledge. |
| **New skill developed** | Engineering the cost, throughput and reliability of a model-backed pipeline from measurements. |
| **Decisions the member must make** | Batch size; how to detect and handle bad replies; cooldown and recovery policy; what to cache; how to run a fair comparison. |
| **What must be investigated independently** | Where batching stops being worth it, which the brief never states. |
| **Why it is interesting** | The cheapest-looking provider becomes expensive during its outage, and the largest batch is not the cheapest once bad replies are re-billed. |
| **Evidence of competence** | Zero rejections across hidden worlds, reconciled billing, and the cost/time/accuracy bars on a re-seeded scenario. |
| **Misconceptions exposed** | 'Bigger batches are always cheaper.' 'Retrying on 429 is fine.' 'A fallback provider is free insurance.' 'Caching needs exact string matches.' |
| **Preparation for later work** | Leads into AI-03 Tier 3 serving trade-offs, AI-05 RAG pipelines, AI-10 evaluation harnesses and AI-13 production operations. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
