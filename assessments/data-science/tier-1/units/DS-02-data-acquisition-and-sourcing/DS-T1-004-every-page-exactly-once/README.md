# DS-T1-004: Every Page, Exactly Once

> *Build a World Bank Indicators API client that survives flaky networks, never invents or duplicates a record, and can prove where every number came from.*

![Format: Implementation](https://img.shields.io/badge/format-implementation-0366d6) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline%20tests-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-004` |
| **Title** | Every Page, Exactly Once: A Resilient, Provenance-Logging Client for the World Bank Indicators API |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-02: Data Acquisition and Sourcing](../README.md) |
| **Format** | Implementation |
| **Difficulty** | Technical 3 · Mathematical 1 · Research 1 · Engineering 3 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 10–16 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU and no paid services. Internet is needed only for the short live run in deliverable 4. All tests run offline |
| **Recommended prerequisites** | Python functions, classes and dataclasses; `try`/`except`; reading JSON; basic HTTP (methods, status codes, headers); pandas `DataFrame` basics; running `pytest` |
| **Skills developed** | Paginated API acquisition; retry and backoff design; idempotent caching; data provenance; testing network code with fakes; reasoning about data vintages |
| **Technologies** | Python 3.10+, standard library (`urllib`, `json`, `hashlib`), pandas, pytest |

---

## B. Problem Statement

A policy research group at a Nigerian university tracks access to electricity across the fifteen ECOWAS countries. Its analysts pull the numbers from the [World Bank Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation) with a script that one of them wrote years ago. Last month a briefing note claimed that regional access had "fallen sharply". It hadn't. On the day the script ran, the API had a short outage. The script quietly retried the failed page, received the next page instead, and treated the missing years as `0`. Nobody could reconstruct which responses the published figure was built from.

Your job is to replace that script with a small, well-tested client library, `wbclient`, that the group can trust. Getting data from an API is easy. Getting **exactly the data the API holds, once, with a record of how you got it** is the real problem, and the API has several real behaviours that make it harder than it looks. Every one of these was observed on the live API when this assessment was written (2026-11-03):

- **Errors arrive as HTTP 200.** Ask for an indicator that does not exist and the API returns status 200 with the body `[{"message":[{"id":"120","key":"Invalid value",...}]}]`. A client that only checks the status code will treat an error as an empty dataset.
- **Omit `format=json` and you get XML**, still with status 200.
- **Results are paginated.** The first element of every response is metadata (`page`, `pages`, `per_page`, `total`, `lastupdated`), and the second is the list of records. Asking for a page beyond the last returns an empty list, not an error.
- **Metadata types are inconsistent between endpoints.** `/v2/sources` sends `"page":"1"` (a string), and the indicator endpoint sends `"page":1` (an integer).
- **Missing observations are `null`, not absent.** Liberia's electricity-access series is `null` for 2000–2006. `null` means "no estimate", and it is not zero.
- **The data changes.** The World Development Indicators are revised and republished. The `lastupdated` field tells you which vintage you hold. If the database is republished while you are halfway through paging, page 3 can belong to a different snapshot from page 1.

The client must also be **polite and safe**. It retries only failures that can succeed on retry, backs off with jitter so that many clients don't retry in lockstep, honours `Retry-After`, refuses to wait absurdly long, caches responses so that re-running an analysis doesn't hammer a free public service, and writes a provenance log entry for every attempt.

**What you are given:** a fixed public interface (the tests import it), real API responses recorded on 2026-11-03, an in-memory scripted transport, and a local fake server, `tests/fakes.py`, that reproduces the API's paging, error envelope and XML default, and can inject outages, dropped connections and mid-pagination republishing. **No test touches the real internet.**

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** paginated acquisition that retrieves every record of a query exactly once, and detects when the pages do not describe one consistent snapshot.
2. **Classify failures** into retryable and non-retryable ones, and justify each classification from HTTP semantics and from the API's observed behaviour.
3. **Implement** exponential backoff with full jitter that honours `Retry-After`, and explain why jitter matters for a shared public service.
4. **Build** an on-disk cache whose keys are canonical, whose writes are atomic, and whose entries are integrity-checked, so that it never serves an error or a corrupted body.
5. **Record provenance** that is detailed enough to reconstruct exactly which bytes, from which URL and which data vintage, produced a dataset.
6. **Test network code offline** with injected transports, clocks and sleeps, and without real waiting.
7. **Explain** why `null` must stay missing, and show the effect on an aggregate if it doesn't.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `wbclient` package in [`starter/wbclient/`](starter/wbclient/). `types.py` and `transport.py` are provided plumbing and must not change their public names. Every other module contains stubs that raise `NotImplementedError("R<n>: ...")`. The signatures are fixed because the tests import them.

| ID | Requirement |
|---|---|
| **R1** | `build_url(indicator, countries, *, date=None, page=1, per_page=1000, base=DEFAULT_BASE) -> str` returns the **canonical** URL `"{base}/country/{CODES}/indicator/{indicator}?{query}"`. `CODES` are the country codes upper-cased, de-duplicated, sorted and joined by `;`. `query` is `urllib.parse.urlencode` of the parameters **sorted by name**: `date` (only if given), `format=json`, `page` and `per_page`. Example: `.../country/GHA;NGA/indicator/EG.ELC.ACCS.ZS?date=2000%3A2024&format=json&page=2&per_page=100`. Raise `ValueError` for an indicator that is not `^[A-Za-z0-9][A-Za-z0-9._]*$`, a country code that is not 2–3 alphanumerics, an empty country list, a date that is not `YYYY` or `YYYY:YYYY`, or a non-positive page or per_page. (These checks stop path injection such as `EG/../x`.) `canonical_key(url) -> str` returns the SHA-256 hex digest of the URL with the scheme and host lower-cased and the query parameters sorted. |
| **R2** | `parse_page(body: bytes) -> Page`. A body that isn't JSON, or isn't a two-element `[metadata, records]` list, raises `MalformedResponse`. The error envelope (`[{"message": [...]}]`) raises `WorldBankAPIError(code, key, message)`. Metadata integers are coerced from strings. A `records` element of `null` means an empty page. Each record becomes `Observation(indicator_id, country_iso3, date, value, obs_status)`: `country_iso3` falls back to `country.id` if `countryiso3code` is empty, `date` stays a string, `value` is a `float` or **`None`** (never `0`), and an empty `obs_status` becomes `None`. |
| **R3** | `is_retryable(status, error=None) -> bool`. With an `error`, return `True` for `TransportError` and `MalformedResponse` (a CDN maintenance page or a truncated body is transient), and `False` otherwise (including `WorldBankAPIError`). With a status only, return `True` exactly for 408, 429, 500, 502, 503 and 504. Set `RETRYABLE_STATUSES` accordingly. |
| **R4** | `parse_retry_after(value, now) -> float \| None` handles both RFC 9110 forms: delay-seconds (`"7"`) and HTTP-date (`"Tue, 03 Nov 2026 12:00:30 GMT"`, relative to `now`, floored at 0). Anything unparseable gives `None`. `backoff_delay(attempt, policy, rng, retry_after=None) -> float`: if `retry_after` is given, return it. Otherwise use **full jitter**: `rng.uniform(0, min(policy.max_delay, policy.base_delay * 2 ** (attempt - 1)))`, where `attempt` is 1-based. |
| **R5** | `ResponseCache(root, clock)` with `put(key, body, meta)` and `get(key, max_age) -> bytes \| None`. Writes are **atomic** (write a temporary file, then `os.replace`), and no temporary files are left behind. `get` returns `None` when the entry is absent, older than `max_age` seconds by `clock` (`max_age=None` means never expire), or when the body's SHA-256 doesn't match the one stored at `put` time. |
| **R6** | `ProvenanceLog(path, clock)` appends one JSON line per `record(...)` call, containing at least `ts` (ISO 8601 UTC), `url`, `attempt`, `outcome` (one of `ok`, `retry`, `fail`, `cache_hit`), `status`, `sha256`, `bytes` and `lastupdated`. Extra keyword fields (for example `error`, `delay`) are kept. `entries()` reads the log back. |
| **R7** | `WorldBankClient.fetch_page(url, *, use_cache=True) -> Page`. If caching is on and the cache holds a fresh, valid entry, return it and log `cache_hit` (attempt 0). Otherwise call `transport.get` up to `policy.max_attempts` times. A 200 that parses is cached and logged `ok`. A 200 with the error envelope is logged `fail` and raised **without retry and without caching**. A non-retryable status raises `HTTPStatusError` after one attempt. A retryable failure is logged `retry`, then the client calls `self.sleep(backoff_delay(...))` using `Retry-After` for 429 and 503 when present. If `Retry-After` exceeds `policy.max_retry_after`, or attempts run out, log `fail` and raise `RetryExhausted`. **Every attempt is logged.** The client never calls `time.sleep` directly, only the injected `sleep`. |
| **R8** | `fetch_indicator(indicator, countries, *, date=None, per_page=1000) -> FetchResult`. Fetch page 1, then pages 2…`pages`. The result is **consistent** only if every page reports the requested `page` number and the same `pages`, `total` and `lastupdated` as page 1, no `(indicator, country, date)` key appears twice, and the record count equals `total`. If it is inconsistent, discard everything and **restart once with the cache bypassed** (`use_cache=False`), setting `restarted=True`. If the restart is also inconsistent, raise `InconsistentPagination`. A query with `total == 0` returns an empty result. |
| **R9** | `to_frame(observations) -> DataFrame` with exactly the columns `indicator_id, country_iso3, year, value, obs_status`. `year` is `int64`, `value` is `float64` with `NaN` for missing values, and rows are sorted by indicator, country and year. A non-annual date (e.g. `2020Q1`) raises `ValueError`. |
| **R10** | CLI: `python -m wbclient fetch INDICATOR --countries A,B --date 2000:2024 --out data.csv --cache DIR --provenance FILE [--per-page N] [--offline] [--base-url URL]`. It writes the R9 frame as CSV and exits 0. In `--offline` mode it makes **no network request**: it rebuilds from the cache (ignoring age) and exits non-zero with a clear message if any page is missing. An online run followed by an offline run must give byte-identical CSVs. |

### D.2 Engineering requirements (mandatory)

- **No real waiting and no real network in tests.** Inject `sleep`, `clock` and `rng`. Your own tests must use `ScriptedTransport` or `FakeWorldBank`.
- **Standard library and pandas only** for the package. `requests`/`httpx` are not needed, and adding them would hide the behaviour you're meant to understand.
- **Tests.** Keep the provided tests passing and add **at least 10 tests of your own** in `tests/test_member_*.py`. At least three must be fault scenarios that the provided tests don't cover (for example: a 503 on the *last* page, a body of `[]`, or a cache directory that is read-only).
- **Determinism.** The same cache always gives the same CSV.
- **Type hints** on every public function.

### D.3 Security, ethics and terms of use

- World Bank data is published under **CC BY 4.0**. Your report must attribute it correctly (see §E).
- **Be a good citizen of a free service.** Set a descriptive `User-Agent` with a contact (the provided transport uses an `example.ng` placeholder, so replace it with your own contact for the live run). Use the cache. Never run retry loops without a cap.
- **Validate inputs** before they reach a URL (R1). Never build URLs from untrusted strings by concatenation alone.
- No personal data is involved. If you adapt this client to an API that returns personal data, the provenance log must not store response bodies. It stores hashes for exactly this reason.

### D.4 Optional enhancements (not required for full marks)

- Conditional requests (`If-None-Match` / `ETag`) if you can show from a live run whether the API supports them.
- A `--explain` flag that prints the provenance chain behind one CSV row.
- A token-bucket rate limiter shared across pages, with a test.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data source** | World Bank Indicators API v2, `https://api.worldbank.org/v2`. Documentation: [API basic call structures](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures). Registry ID `DSET-019` |
| **Licence** | [Creative Commons Attribution 4.0 (CC BY 4.0)](https://datacatalog.worldbank.org/public-licenses). Attribute it as: *World Bank, World Development Indicators, indicator EG.ELC.ACCS.ZS, accessed <date>, CC BY 4.0.* |
| **Recorded fixtures** | [`resources/fixtures/`](resources/fixtures/), all recorded from the live API on 2026-11-03 (WDI `lastupdated` 2026-10-08). The contract test checks their SHA-256 values, so don't edit them. |
| | `EG.ELC.ACCS.ZS__ecowas__2000-2024.json`: access to electricity (% of population), 15 ECOWAS countries, 2000–2024, 375 records, 9 `null`s (82 KB) |
| | `raw_page2_per100.json`: page 2 of 4 of the same query at `per_page=100`, exactly as served |
| | `error_invalid_indicator.json`: the HTTP-200 error envelope |
| | `sources_2_string_meta.json`: `/v2/sources/2`, showing string-typed metadata |
| | `no_format_param.xml`: what the API returns without `format=json` |
| **Test doubles** | [`tests/fakes.py`](tests/fakes.py): `ScriptedTransport` and `FakeWorldBank` (a real HTTP server on `127.0.0.1` with scriptable faults) |

**Record schema (one element of the records list):**

| Field | Example | Meaning |
|---|---|---|
| `indicator.id` | `EG.ELC.ACCS.ZS` | Indicator code |
| `country.id` / `countryiso3code` | `NG` / `NGA` | ISO2 / ISO3 code |
| `date` | `"2023"` | Period, always a string |
| `value` | `61.2` or `null` | Observation; `null` means no estimate |
| `obs_status` | `""` | Observation status flag, usually empty |

**Known limitations.** The fixtures are one vintage. The live API may by now hold revised values, which is what deliverable 4 asks you to investigate. The fake server only implements the endpoints the tests need.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-02-data-acquisition-and-sourcing/DS-T1-004-every-page-exactly-once
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract        # passes immediately: fixtures, fake server and API surface
pytest                    # the requirement tests fail until you implement wbclient
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `wbclient/` package (the completed starter) | The core technical evidence: correct, resilient acquisition |
| 2 | `tests/test_member_*.py` (at least 10 tests, at least 3 new fault scenarios) | Shows you can test network code without a network |
| 3 | `data/ecowas_electricity.csv`, `data/provenance.jsonl` and the cache directory, produced by one live CLI run of `EG.ELC.ACCS.ZS` and `EG.ELC.ACCS.RU.ZS` for ECOWAS, 2000–2024 | A real, reproducible acquisition with its audit trail |
| 4 | `ACQUISITION_REPORT.md` (at most 1,200 words plus tables), using the [template](submission-template/ACQUISITION_REPORT.md) | Explains your retry classification, compares the live vintage with the recorded fixture, quantifies coverage, and shows what `fillna(0)` would have done to the regional mean |
| 5 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 6 | A 5–10 minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. ⚙ = checked automatically by the public and hidden suites; ✍ = checked by the assessor.

1. ⚙ `pytest` passes all provided tests and all of your own from a clean environment, in under 2 minutes, with no real network access and no real sleeping.
2. ⚙ **Exactly once:** on an indicator and page sizes you haven't seen, `fetch_indicator` returns every record exactly once, makes exactly `pages` requests when there are no faults, and keeps every `null` as `None`/`NaN`.
3. ⚙ **Failure classification:** non-retryable statuses (400, 401, 403, 404, 410) are attempted exactly once. The HTTP-200 error envelope is never retried or cached. Truncated JSON and dropped connections are retried.
4. ⚙ **Backoff:** delays without `Retry-After` lie in `[0, min(max_delay, base·2^(n−1))]` and vary between draws. `Retry-After` is honoured in both forms. A `Retry-After` above `max_retry_after` raises immediately without sleeping.
5. ⚙ **Snapshot consistency:** a republish mid-pagination triggers exactly one cache-bypassing restart, and persistent inconsistency (including duplicated or short pages) raises `InconsistentPagination`.
6. ⚙ **Cache:** keys don't depend on country order or parameter order, expired and corrupted entries are misses, and an offline rebuild is byte-identical to the online run and makes zero requests.
7. ⚙ **Provenance:** the log has one entry per attempt and per cache hit, with all eight required fields. On a clean online-then-offline run, the number of `ok` entries equals the number of `cache_hit` entries.
8. ✍ The report justifies every retryable status, with a sentence each, and explains why 404 is *not* retried even though "it might come back".
9. ✍ The report compares the live vintage (`lastupdated`) with the fixture's `2026-10-08`, and lists any revised values, or states that none were found, with the code that checked.
10. ✍ The report quantifies the error from treating `null` as `0` in the 2000–2010 ECOWAS mean for at least one year. *Justification:* this is the defect that caused the false briefing in §B, and computing it shows you understand why R2 insists on `None`.

The thresholds in criteria 2–7 are behavioural (exact counts and bounds), not tuned scores, so the reference implementation meets all of them exactly. The 2-minute test budget (criterion 1) is about five times the reference suite's runtime (about 20 seconds) on a typical laptop, which leaves room for slower machines while still catching any real sleeping.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 15 |
| Methodology (failure analysis → design → evidence) | 10 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible offline rebuild, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create a private repository** named `clbg-DS-T1-004-<your-github-username>` and copy in this assessment's `starter/` contents, `tests/`, `resources/` and `submission-template/`.
2. **Expected structure:**
   ```text
   clbg-DS-T1-004-<username>/
   ├── README.md                 # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── wbclient/
   ├── tests/                    # provided tests + test_member_*.py
   ├── resources/                # unchanged
   ├── data/ecowas_electricity.csv
   ├── data/provenance.jsonl
   ├── data/cache/               # the cache from your live run (it is small)
   ├── ACQUISITION_REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** Your history is evidence. One giant final commit will be questioned at defence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue in the CLBG assessments repository with your repository URL and commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback, but never stand in for the core requirements.

1. **Vintage diffing.** Add `wbclient diff OLD.csv NEW.csv` that reports revised, added and removed observations between two vintages, and run it against the fixture.
2. **Measure the thundering herd.** Simulate 50 clients that all hit a 503 at the same moment, with and without jitter, and plot how many requests the server receives per 100 ms. Explain the result.
3. **ETag support.** Find out from the live API whether conditional requests are honoured, implement them if they are, and quantify the bytes saved.
4. **Second API.** Point the same retry, cache and provenance layers at a different free API with different paging (for example cursor-based), and say what had to change.

---

## K. Assessment Integrity

**AI tools are permitted** for learning: explaining HTTP semantics, reviewing your code, or suggesting test ideas. **They are not permitted to write the assessment for you.** You must be able to explain and modify every line.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`: the tool, what you used it for, and an example prompt. Disclosed, reasonable use is not penalised. Undisclosed use that becomes apparent at defence is an integrity breach.
- **Cite** adapted code (documentation, Stack Overflow, blog posts) with links.
- **Collaboration:** you may discuss general ideas such as "what is full jitter?" You may not share code, tests or report text.
- **How your understanding is verified.** In the defence, the assessor will:
  1. pick one line of your `provenance.jsonl` and ask you to show which code path wrote it, and why its `attempt` has that value;
  2. ask you to trace what your client does when page 3 of 4 returns `503` with `Retry-After: 600` under the default policy;
  3. give you an **unseen modification** to implement live with a test, for example "treat 404 on page > 1 as the end of data", "add a `max_total_wait` budget across all retries", or "log the `Content-Type` header".

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Python classes, exceptions, JSON, HTTP status codes and headers, pandas basics, pytest. |
| **New skill developed** | Treating acquisition as engineering with guarantees ("every record exactly once, from one snapshot, with an audit trail") rather than "the script ran". You also learn to test network code deterministically by injecting time, randomness and transport. |
| **Decisions the member must make** | How to structure the retry loop so every attempt is logged. Where caching sits relative to parsing. What "consistent" means for paged data. Which failures are transient. How to keep `null` intact from JSON to CSV. |
| **What must be investigated independently** | The API's real behaviours: you are told about them, but you must confirm them on the live API and in the fixtures, and find out whether the live vintage differs from the recorded one. |
| **Why it's interesting** | The API's traps are real and observed: errors with status 200, XML by default, string-typed metadata, `null` gaps and republished vintages. The §B incident is exactly what happens when they're ignored. |
| **Evidence of competence** | Hidden tests on an unseen indicator and unseen fault scripts; a byte-identical offline rebuild; a provenance log the member can trace live; a quantified `fillna(0)` error. |
| **Misconceptions exposed** | "Status 200 means success." "Retry everything." "Retry immediately." "A cache is just a dict on disk." "Missing means zero." "If every page returned, the data is complete." |
| **Preparation for later work** | It leads into DS-T2-003 (polite collection at scale, change detection), DS-T2-004 (fusing several sources and their vintages) and DS-11 pipelines, where idempotent, auditable ingestion is the foundation. |

**Suggested approach** (optional): implement and test R1–R4 as pure functions first. Then do R5 and R6. Then do R7 with `ScriptedTransport` only. Move to `FakeWorldBank` for R8. Do the live run last, once everything passes offline.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
