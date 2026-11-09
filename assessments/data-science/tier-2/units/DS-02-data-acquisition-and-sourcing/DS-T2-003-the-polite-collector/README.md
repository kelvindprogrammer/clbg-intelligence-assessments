# DS-T2-003: The Polite Collector

> *Design a web-collection pipeline for a public procurement portal that respects robots.txt and the terms, notices amendments and withdrawals, and raises an alarm instead of writing nulls the day the site's template changes.*

![Format: System design](https://img.shields.io/badge/format-system%20design-5319e7) ![Tier 2](https://img.shields.io/badge/tier-2-fbca04) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-003` |
| **Title** | The Polite Collector: Ethical, Change-Aware Collection from a Public Procurement Portal |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Engineering and Independent Problem-Solving |
| **Unit** | [DS-02: Data Acquisition and Sourcing](../README.md) |
| **Format** | System design (secondary: Implementation, Comparative) |
| **Difficulty** | Technical 3 · Mathematical 1 · Research 2 · Engineering 4 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 20–35 hours over 2–3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop. Everything runs against a local mock portal on a **virtual clock**, so no real waiting and no internet |
| **Recommended prerequisites** | [DS-T1-004](../../../../tier-1/units/DS-02-data-acquisition-and-sourcing/DS-T1-004-every-page-exactly-once/README.md) or equivalent experience with HTTP clients; HTML structure; Python packages and testing; basic JSON or SQLite storage |
| **Skills developed** | Robots Exclusion Protocol (RFC 9309); terms-of-use review; rate limiting; conditional HTTP; URL canonicalisation and crawl scoping; change detection; schema-drift detection; data minimisation; measured comparison of collection strategies |
| **Technologies** | Python 3.10+ standard library (`urllib`, `html.parser`, `json`/`sqlite3`), pytest. Optional: BeautifulSoup/lxml, requests/httpx (justify any you add) |

---

## B. Problem Statement

A civic-technology group monitors public procurement in Nigeria's states: which ministries advertise tenders, for how much, and how often closing dates are extended or tenders quietly cancelled. One (fictional) state, **Ajana State**, publishes notices on an e-procurement portal with no API. The group has a script that scrapes it. It works, but it is the kind of script that gets a civic group's IP address blocked and its reputation damaged:

- It ignores `robots.txt` and hits the portal as fast as Python allows.
- It follows every link, including session-tagged duplicates and an archive calendar that goes back forever.
- It downloads every notice again on every run.
- It stores the **contact officer's name, phone and e-mail** for every notice, which the portal's terms forbid harvesting.
- The day the portal changed its template, the script carried on happily and wrote `null` into every value field. That was eventually noticed as "procurement spending fell to zero".

Your task is to design and build its replacement, `collector`, and to **show with measurements** that it is better: more polite, cheaper on quiet days, correct about amendments and withdrawals, and loud when the site changes.

You work against a **local mock portal** ([`tests/mocksite.py`](tests/mocksite.py)) that behaves like a real one: `robots.txt` with agent-specific groups, wildcards and `Crawl-delay`; a terms page; paginated listings whose links carry random session parameters; an infinite archive; detail pages with `ETag`/`Last-Modified` and `304 Not Modified`; a sitemap with `lastmod`; transient 503s with `Retry-After`; 429s if you go too fast; and "days" on which notices are added, amended (some *silently*: the sitemap isn't updated), withdrawn (`410 Gone`), and on which the template drifts. The portal and the client share a `VirtualClock`, so every delay is measured exactly without anyone waiting.

**What makes it hard.** No single strategy is best. Re-fetching everything is simple and catches everything, but it is expensive and impolite. Trusting the sitemap is cheap, but the sitemap lies. Conditional requests are cheap *if* you stored the validators. Detecting template drift needs an explicit schema, and once drift is detected you must decide what to do with pages you can no longer parse. You must choose, justify and measure.

**Real-site scraping is not required.** If you want to try your design on a real Nigerian portal, you may do so only after a written terms review (§D.3) that concludes it is permitted, with the crawl delay set to at least 10 seconds, and without collecting personal data. This is an optional extension and earns no extra points on its own.

---

## C. Objectives

You should be able to show that you can:

1. **Implement RFC 9309 semantics** correctly (group selection, `Allow`/`Disallow` precedence, `*` and `$` wildcards, `Crawl-delay`), and explain where `urllib.robotparser` falls short.
2. **Read terms of use as requirements**, and turn each clause into a design decision and a test.
3. **Design a crawl** that is scoped, bounded, canonicalised and rate-limited, and **prove** its politeness from the server's log.
4. **Detect change** (new, amended, withdrawn) correctly and cheaply, comparing at least two strategies against the provided baseline, with measured requests, bytes, politeness violations and missed changes.
5. **Detect schema drift** with an explicit schema, raise structured alarms, and protect previously good data.
6. **Minimise personal data** by design, and document what you don't collect and why.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

The **only** fixed interface is in [`starter/collector/`](starter/collector/): `contract.py` (`CollectorConfig`, `RunReport`, `RECORD_FIELDS`, `ALARM_KINDS`), plus `Robots`, `canonical_url`, `run_once` and `load_records`. How you structure the rest (modules, storage engine, parser library, strategy plug-ins) is your design, and you must justify it in `DESIGN.md`.

| ID | Requirement |
|---|---|
| **R1** | **Robots.** `Robots(text).allowed(token, path)` and `.crawl_delay(token)` follow RFC 9309: pick the group whose `User-agent` matches the product token (case-insensitive), else `*`; groups don't merge; the longest matching rule wins, with `Allow` winning ties; `*` matches any sequence and `$` anchors the end; `/robots.txt` is always allowed. `run_once` fetches `/robots.txt` **first**, and never requests a disallowed path. |
| **R2** | **Rate.** No two requests (after `robots.txt`) are closer together than `max(cfg.min_delay, Crawl-delay)` on `cfg.clock`. All waiting uses `cfg.sleep`. `429`/`503` responses honour `Retry-After` (bounded). `cfg.max_requests` is a hard per-run budget, and exhausting it is reported in `errors`. |
| **R3** | **Scope.** Follow only listing pages (`/tenders?page=N`) and detail pages (`/tenders/<REF>`), with at most `cfg.max_listing_pages` listing pages per run. `canonical_url` removes fragments and every query parameter except `page`, and lower-cases scheme and host, so that **no page is fetched twice in a run** (except retries). |
| **R4** | **Identification.** Every request carries `cfg.user_agent`, whose product token is `clbg-collector` and which includes a contact address. |
| **R5** | **Change detection.** `RunReport.new`, `updated`, `withdrawn` and `unchanged` are correct for every run, *including amendments that the sitemap doesn't advertise*. A notice that disappears from the listing is marked withdrawn only after the portal confirms it (`404`/`410`). Strategy `"conditional"` (the default) must use stored validators (`If-None-Match`) and report `not_modified`. |
| **R6** | **Records.** `load_records(state_dir)` returns every notice ever seen, with at least `RECORD_FIELDS`. The types are: `estimated_value_ngn` an `int` in naira, `closing_date` ISO `YYYY-MM-DD`, `withdrawn` a `bool`, and `first_seen`/`last_changed` ISO timestamps from `cfg.clock`. State survives between runs and is written atomically. |
| **R7** | **Schema drift.** Validate every detail page against an explicit schema. An unknown field label, a missing required field, an unparseable value, or a listing that suddenly yields no notices produces an entry in `drift_alarms` (`kind` from `ALARM_KINDS`, `field`, `count`, `example_url`). A page that fails validation **never overwrites** the stored record: put it in `quarantined`. A listing failure must never cause a mass withdrawal. |
| **R8** | **Data minimisation.** No contact-officer names, phone numbers or e-mail addresses are stored anywhere in `state_dir`, including logs and caches. |
| **R9** | **Strategies and comparison.** Implement at least **two** change-detection strategies (for example `"conditional"`, `"sitemap"`, `"full"` or a hybrid). Compare them **and the provided baseline** ([`starter/baseline/naive_crawler.py`](starter/baseline/naive_crawler.py)) over a multi-day simulation, with a reproducible script. Measure requests, bytes, politeness violations (from `portal.violations()`), changes missed, and detection latency in days. |

### D.2 Engineering requirements (mandatory)

- **Modular and tested.** Keep the provided tests passing, and add **at least 15** of your own in `tests/test_member_*.py`, covering robots edge cases, rate limiting, drift and storage failure. Tests use only the mock portal and the virtual clock.
- **Deterministic.** The same scenario gives the same report and state, byte for byte.
- **Fail safe.** A crash part-way through a run must not corrupt the state. Say how you guarantee that.
- **Observability.** Each run writes a short run log (counts, alarms, budget used) without personal data.

### D.3 Ethics, terms and privacy (mandatory)

- **`TERMS_REVIEW.md`:** read the portal's `/terms` and map **every clause** to a design decision and a test. Then explain what you would do if the terms and `robots.txt` disagreed.
- **Personal data:** contact officers are real people in the scenario the mock models. Under the NDPA 2023, collecting their details without a lawful basis and a purpose is not acceptable just because they are "public". Explain your minimisation decision.
- **Re-use obligations:** the terms require re-users to reflect amendments and withdrawals. Explain how your data model makes that possible for downstream users.
- Respect the spirit as well as the letter. "The mock portal didn't block me" is not an argument.

### D.4 Optional enhancements

- A hybrid strategy that uses the sitemap for discovery and periodic conditional sweeps to catch silent amendments, with the sweep period chosen from your measurements.
- Alias learning: propose (but don't silently apply) a mapping when a renamed label appears, and require human approval.
- A real-site pilot after a documented terms review (see §B).

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | **Synthetic**, generated at runtime by [`tests/mocksite.py`](tests/mocksite.py) from a fixed seed. The state, portal, notices and people are fictional, and e-mails use `example.ng`. No dataset is downloaded. |
| **Licence** | CC BY 4.0 (repository content); mock code MIT |
| **Mock portal** | `MockPortal(clock, scenario=PUBLIC_SCENARIO, enforce=True)` serves `/robots.txt`, `/terms`, `/sitemap.xml`, `/tenders?page=N`, `/tenders/<REF>` (with `/print` and `/bidders`) and `/tenders/archive/<YYYY-MM>`. Use `set_day(n)` to advance; read `log` and `violations()` to audit; `truth()` gives the live notices for evaluation. `enforce=False` logs rate violations without returning 429, which you need for measuring the baseline. |
| **Public scenario** | 40 notices on day 1; day 2 brings 5 new, 3 amended, 1 *silently* amended and 2 withdrawn; on day 3 the detail template changes. A transient 503 hits on request 7. |
| **Baseline** | `starter/baseline/naive_crawler.py`, the group's current script, to measure against. |
| **RFC 9309** | [Robots Exclusion Protocol](https://www.rfc-editor.org/rfc/rfc9309) |
| **RFC 9110** | [HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110) (conditional requests, `Retry-After`) |

**Record schema** (`RECORD_FIELDS`): `reference, title, ministry, category, estimated_value_ngn, closing_date, status, url, first_seen, last_changed, content_hash, withdrawn`.

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-02-data-acquisition-and-sourcing/DS-T2-003-the-polite-collector
python -m venv .venv && source .venv/bin/activate
pip install -r starter/requirements.txt
pytest -m contract    # passes: the mock portal and contract are in place
pytest                # requirement tests fail until you build the collector
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `collector/` package | The system |
| 2 | `tests/test_member_*.py` (at least 15) | Evidence that each behaviour is pinned |
| 3 | `DESIGN.md` (at most 1,500 words plus one diagram) | Architecture, the storage choice, how failures are contained, and the alternatives you rejected |
| 4 | `TERMS_REVIEW.md` (at most 800 words) | Clause-by-clause mapping of the terms to decisions and tests |
| 5 | `experiments/compare.py` and `EVALUATION.md` (at most 1,500 words plus tables), using the [template](submission-template/EVALUATION.md) | Measured comparison of your strategies and the baseline over at least 5 simulated days |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 7 | A 10–20 minute defence | Justify, debug and modify live (§K) |

---

## G. Acceptance Criteria

1. ⚙ All provided tests and at least 15 member tests pass.
2. ⚙ **Politeness:** across every hidden-scenario run, zero disallowed requests, zero requests faster than the crawl delay, every request identified with a contact, and `Retry-After` honoured.
3. ⚙ **Correct change detection:** on an unseen scenario, `new`, `updated` (including silent amendments) and `withdrawn` exactly match the portal's truth.
4. ⚙ **Drift safety:** after an unseen template change, an alarm names the affected field, no stored value is nulled or guessed, and a listing change causes no mass withdrawal.
5. ⚙ **Minimisation:** no contact data appears anywhere in `state_dir`.
6. ✍ **Cost:** on the public scenario's day 2, your default strategy uses **less than 60 % of day 1's bytes**. *Justification:* about 85 % of notices are unchanged on day 2, so a strategy that revalidates instead of re-downloading should spend well under 60 %. The reference spends about 40 %. Re-downloading everything costs about 108 %.
7. ✍ The evaluation compares at least two strategies and the baseline, on at least five days, with every metric in R9. It names the trade-off honestly: which strategy misses silent amendments, and how quickly each one detects drift.
8. ✍ `TERMS_REVIEW.md` covers every clause and states what you would *not* do even though it is technically possible.
9. ✍ `DESIGN.md` explains how a crash mid-run is contained, and why your storage choice suits the data.

---

## H. Evaluation Rubric

Full rubric with level descriptors: **[rubric.md](rubric.md)**.

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Architecture and implementation quality | 20 |
| Methodology: strategy comparison | 15 |
| Testing and evaluation | 10 |
| Ethics, terms and privacy | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The score **and** the gates decide the outcome ([placement framework](../../../../../../docs/placement-framework.md)).

---

## I. Submission Instructions

1. Create a **private** repository named `clbg-DS-T2-003-<your-github-username>`.
2. **Expected structure:**
   ```text
   clbg-DS-T2-003-<username>/
   ├── README.md                 # how to run tests and experiments, in 15 lines or fewer
   ├── requirements.txt
   ├── collector/
   ├── baseline/naive_crawler.py # unchanged
   ├── tests/                    # provided (including mocksite.py) + test_member_*.py
   ├── experiments/compare.py
   ├── DESIGN.md
   ├── TERMS_REVIEW.md
   ├── EVALUATION.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** Design changes should be visible in the history.
4. **Submit** with an **Assessment submission** issue (repository URL and commit SHA), after adding the CLBG assessor account as a read-only collaborator.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Freshness versus politeness frontier.** Plot detection latency against requests per day for a family of hybrid strategies (sweep every k days), and pick k for this portal.
2. **Human-in-the-loop drift repair.** When a label is renamed, generate a proposed schema patch and a diff of the records it would change, and apply it only after approval.
3. **Real-site pilot.** Run a terms review on a real Nigerian procurement or gazette portal. If permitted, collect one day's notices at a crawl delay of at least 10 s, without personal data, and report what the mock got wrong about the real world.
4. **Audit trail.** Store every version of each notice so downstream users can see *what* changed, not only *that* it changed.

---

## K. Assessment Integrity

**AI tools are permitted** to explain RFCs, review your design or suggest tests, but not to produce the system for you. You must be able to defend every design decision.

- Disclose AI use in `AI_USE_AND_SOURCES.md`. Undisclosed use discovered at defence is a breach.
- Cite adapted code, and any library whose behaviour you relied on.
- **Collaboration:** discuss general approaches only. No sharing of code, measurements or documents.
- **How understanding is verified (10–20 minutes):**
  1. **Justify:** "Why did you choose this storage engine and this default strategy?" Expect to defend them with your own numbers.
  2. **Debug:** the assessor runs your collector against a scenario with a fault you haven't seen (for example `robots.txt` returning 500, or a listing page that links to itself) and asks you to explain the behaviour from your logs.
  3. **Modify live:** for example, add a per-day request budget across runs; treat `Crawl-delay` above 30 s as "don't crawl today"; or add a `new_field` alarm whitelist that requires approval.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | HTTP basics, HTML structure, Python packaging and tests; DS-T1-004-level client skills. |
| **New skill developed** | Designing a *system* for ethical, sustainable collection: politeness, scope, change detection and drift safety. You also prove its properties from the server's point of view, and compare strategies with measurements rather than opinions. |
| **Decisions the member must make** | Architecture and storage; robots implementation; canonicalisation rules; which change-detection strategy is the default and why; what to do with unparseable pages; what personal data *not* to collect. |
| **What must be investigated independently** | RFC 9309 details and the limits of `urllib.robotparser`; the portal's actual behaviour (session parameters, archive trap, sitemap reliability); the terms. |
| **Why it's interesting** | The trade-off is real and visible in the numbers: the sitemap strategy is about 3× cheaper but misses silent amendments, and it detects drift later. The baseline "works" but is throttled to nothing once rate limits are enforced. |
| **Evidence of competence** | Server-side audit logs with zero violations; exact change detection on an unseen scenario; drift alarms that protect data; a defensible measured comparison. |
| **Misconceptions exposed** | "If it's public, I can take it." "robotparser handles robots." "The sitemap tells me what changed." "A parse failure is just a null." "A missing listing means everything was withdrawn." |
| **Preparation for later work** | It leads into DS-11 (production pipelines, data contracts, monitoring), DS-T3-001 (building and documenting datasets) and any applied work that depends on collected data. |

**Suggested approach** (optional): read the terms and `robots.txt` before writing code. Build `Robots` with tests first. Then a fetcher that can only be polite. Then discovery with canonicalisation; then the detail schema and validation; then storage and change detection; and the strategies and experiments last.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
