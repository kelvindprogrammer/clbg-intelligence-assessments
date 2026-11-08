# DS-T3-011: The Agent Ledger Model: Point-in-Time Analytics for a Mobile-Money Network

> *Agents change tier, transactions get amended and reversed, exchange rates skip weekends. Design the analytical model whose numbers you can defend a year later.*

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T3-011` |
| **Title** | The Agent Ledger Model: Point-in-Time Analytics for a Mobile-Money Network |
| **Subtrack** | Data Science |
| **Tier** | 3: Advanced and Research-Informed |
| **Unit** | [DS-07: SQL and Database Analytics](../README.md) |
| **Format** | System design (secondary: debugging-forensics) |
| **Difficulty** | Technical 4 · Mathematical 1 · Research 3 · Engineering 4 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 18-28 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM; DuckDB is embedded; no GPU or network after setup |
| **Recommended prerequisites** | Window functions, CTEs and joins (DS-T2-013 level); star-schema vocabulary (fact, dimension, grain); comfort reading DuckDB documentation (ASOF joins, QUALIFY). |
| **Skills developed** | Dimensional modelling, temporal SQL, data-quality controls, reconciliation, architecture decision records |
| **Technologies** | DuckDB 1.0+, Python 3.10+, pytest |

---

## B. Problem Statement

A mobile-money operator in West Africa sells cash-in, cash-out and transfer services through a network of **agents**: small shops and kiosks that hold float and earn commission. Agents are rated **bronze, silver or gold**, and the tier changes over time as an agent's performance changes, and so does the agent's **region** when an agent relocates. Tier drives commission: a gold agent earns more per naira of fee.

Finance wants a monthly view of **fee revenue by agent tier in naira**. The operator also runs corridors into Ghana and Kenya, so transactions are in NGN, GHS and KES. That innocent request is a minefield:

- The transaction system is **event-sourced**. Each transaction has a `create` event, sometimes an `amend` (corrected amount) and sometimes a `reverse`. Events arrive out of order, and some are delivered twice. The truth is the **latest version**, and a reversed transaction is not revenue.
- An agent's tier **at the time of the transaction** is what the commission contract uses. Joining to the agent's *current* tier is the classic Type 1 mistake: it quietly rewrites history every time someone is promoted.
- Agent history contains **no-op rows** (tier and region unchanged), **corrections** (two rows for the same effective date, the later-recorded one wins), and **stale rows** that were superseded.
- Exchange rates exist for weekdays, with holes. A Saturday transaction uses **the latest rate on or before** its date. Two corridors start publishing rates late in the period, so some early transactions have **no rate at all**.
- A few transactions belong to agents that appear in **no history**, and a few predate an agent's first recorded state.

You are the analytics engineer. Build the model in **DuckDB** so that every naira in the finance view can be traced to source events, every transaction that cannot be valued is **listed with a reason rather than silently dropped**, and the whole thing reconciles to the raw event count. Then write the design records that justify your choices, including the ones the tests cannot check.

Nobody tells you the schema beyond the five object names in §D; the grain, keys, intermediate tables and build order are yours to decide and defend. That is the point of Tier 3.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Declare grain, keys and the temporal semantics of each table before building them, and defend them.
2. Build a correct SCD2 dimension from noisy change events, including corrections, no-ops and open-ended current rows.
3. Resolve an event-sourced fact to its latest version, net reversals and tolerate duplicate deliveries.
4. Perform as-of joins (rates and agent states) and handle "no match" explicitly with an exceptions table.
5. Make a model idempotent and reconcilable, and prove that the control totals close.
6. Quantify the impact of a modelling shortcut (Type 1 attribution) on a business number and compare at least two alternative architectures with their costs.

---

## D. Technical Requirements

### D.1 Mandatory requirements

Implement `analytics_model.build(con)` for a DuckDB connection in which the raw tables `raw_agent_history`, `raw_txn_events` and `raw_fx_rates` already exist (the test `conftest.py` loads them; see §E for columns). `build` creates the objects below (tables or views; your choice) and may create any helper objects.

| ID | Object | Required semantics |
|---|---|---|
| **R1** | `dim_agent(agent_id, tier, region, valid_from, valid_to, is_current)` | SCD Type 2. Per `(agent_id, effective_from)` the row with the latest `recorded_at` wins. Consecutive states with identical tier **and** region collapse into one. `valid_from` is inclusive, `valid_to` exclusive and equal to the next state's `valid_from`; the current state has `valid_to = DATE '9999-12-31'` and `is_current = TRUE`. No gaps or overlaps. |
| **R2** | `fact_txn(txn_id, agent_id, txn_date, currency, amount, fee, fx_rate_date, fx_rate, amount_ngn, fee_ngn, tier, region)` | One row per transaction whose **latest event** (highest `version`, ties by latest `recorded_at`) is not a `reverse` and which can be fully valued. `tier` and `region` are the agent's state **on `txn_date`**. NGN transactions use rate 1 and `fx_rate_date = txn_date`. Otherwise the rate is the **latest `rate_date` on or before `txn_date`** for that currency (no staleness cut-off; see §D.2). `amount_ngn` and `fee_ngn` are rounded to 2 decimals after multiplying by the rate. |
| **R3** | `dq_exceptions(txn_id, issue)` | One row for every non-reversed transaction that cannot enter `fact_txn`. `issue` is `ORPHAN_AGENT` (agent in no history), else `NO_AGENT_AT_DATE` (date before the agent's first state), else `NO_FX_RATE` (no rate on or before the date). First matching reason wins. |
| **R4** | `v_tier_daily(txn_date, tier, n_txn, volume_ngn, fee_ngn)` | Daily totals by tier at transaction time from `fact_txn`. |
| **R5** | `v_reconciliation(n_txn_ids, n_reversed, n_exceptions, n_fact)` | One row; `n_txn_ids` = distinct `txn_id` in the raw events, and the identity `n_txn_ids = n_reversed + n_exceptions + n_fact` must hold. |
| **R6** | Idempotence | Calling `build(con)` repeatedly yields identical results and never touches the `raw_*` tables. A late event inserted into `raw_txn_events` is reflected by the next `build`. |

### D.2 Engineering and design requirements

- Do not hard-code dates, agents or currencies. Hidden tests rebuild on **differently seeded raw data**, with different agents, corrections and rate holes.
- `DESIGN.md` must contain at least **five decision records** (context, options, decision, consequences), covering at least: (a) grain and keys of `fact_txn`; (b) SCD2 versus daily-snapshot versus a temporal-table approach for agents; (c) full rebuild versus incremental build and what breaks incrementally (late amendments, reversals, back-dated agent corrections); (d) a **rate-staleness policy** (the tests allow unlimited staleness; what would you require in production, and what would it do to `NO_FX_RATE`?); (e) star schema versus one-big-table versus a vault-style model for this workload.
- `REPORT.md` quantifies, from your own build, the **error a Type 1 shortcut would introduce** into the tier revenue view (in naira and in percent per tier), and lists the exception counts by reason.
- Add at least six tests of your own in `tests/test_member_*.py`, including at least two on constructed edge cases (for example a transaction exactly on a `valid_from` date; an amendment after a reversal).

### D.3 Privacy and responsibility

Everything is synthetic; agent IDs are integers and there are no names or phone numbers. In a real deployment agent identity, location and float are commercially sensitive and, for sole traders, personal data under the NDPA 2023. In `DESIGN.md` add a short note on what you would pseudonymise, who should see exception rows, and how long raw events must be retained for audit versus erased.

### D.4 Optional enhancements

Add constraints and assertions (`CHECK`, unique keys) as build-time controls; compare timings of ASOF join versus a window-based rewrite; add a `v_commission` view if you state the commission rates you assume.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | [`resources/data/`](resources/data/): `agent_history.csv`, `txn_events.csv` (about 116 KB), `fx_rates.csv` |
| **Provenance** | **Synthetic**, from a deterministic CLBG generator (seed 2026). No real operator, agent or customer. Currency pairs and rate magnitudes are plausible but invented. |
| **Licence** | CC BY 4.0 (data), MIT (code) |
| **Integrity** | SHA-256 of each file is checked by the contract test |

**Raw columns** (loaded by `conftest.load_raw`):
- `raw_agent_history(agent_id INTEGER, effective_from DATE, tier, region, recorded_at TIMESTAMP)`
- `raw_txn_events(event_id, txn_id, version INTEGER, event_type {create|amend|reverse}, agent_id, txn_ts TIMESTAMP, amount DECIMAL(18,2), fee DECIMAL(18,2), currency, recorded_at TIMESTAMP)`
- `raw_fx_rates(rate_date DATE, currency, ngn_per_unit DECIMAL(18,4))`

**Known limitations.** One half-year, 1,100 transactions and 40 agents (the model must scale conceptually, not in this data). Transaction time is a plain timestamp with no time zone. Fee is given on every event and is taken as-is. Rates are one daily mid-rate with no spread.

**Setup**
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract     # passes on the starter
pytest                 # fails until build(con) is implemented
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `analytics_model/` package | The executable model |
| 2 | `tests/test_member_*.py` (≥ 6 tests, ≥ 2 constructed edge cases) | Evidence you test the semantics, not just the happy path |
| 3 | `DESIGN.md` with ≥ 5 decision records | The architecture reasoning the tests cannot check |
| 4 | `REPORT.md` from the [template](submission-template/REPORT.md) | Impact quantification, exception analysis, limitations |
| 5 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 6 | A 10-minute live defence | Verifies understanding and the ability to modify the model |

---

## G. Acceptance Criteria

Criteria marked ⚙ are checked by the public and hidden test suites. Criteria marked ✍ are checked by an assessor.

1. ⚙ Public tests: `dim_agent`, `fact_txn`, `dq_exceptions`, `v_tier_daily` and `v_reconciliation` match the expected results exactly (amounts within 0.01 NGN per transaction, since rounding conventions differ by at most one kobo).
2. ⚙ Hidden tests: the same objects match an independent ground truth on two re-seeded raw datasets, and a late amendment appended after the first build is reflected by the next `build` with no duplicate rows.
3. ⚙ The reconciliation identity holds, `dim_agent` has no gaps or overlaps, and `fact_txn` has one row per `txn_id`.
4. ⚙ Point-in-time attribution: `fact_txn.tier` differs from the agent's current tier for at least one transaction (a Type 1 join fails this).
5. ✍ `DESIGN.md` has at least five decision records with real alternatives and stated costs, including the staleness policy and incremental-load analysis.
6. ✍ `REPORT.md` reports the Type 1 error per tier in naira and percent, regenerated by a query in the repository, and the exception counts by reason.
7. ✍ The privacy note in `DESIGN.md` is specific to this domain.

---

## H. Evaluation Rubric

The full rubric with performance levels is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 10 |
| Methodology and experimentation | 15 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates (passing defence, reproducible run, integrity declaration). See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. Create a **private** GitHub repository named `clbg-DS-T3-011-<your-github-username>` from this assessment's `starter/`, `tests/` and `resources/` folders and the `submission-template/` files.
2. Expected structure:
   ```text
   clbg-DS-T3-011-<username>/
   ├── analytics_model/    # your package (from starter/); build(con)
   ├── tests/              # provided tests + your own test_member_*.py
   ├── resources/          # unchanged
   ├── DESIGN.md           # architecture decision records (see §F)
   ├── REPORT.md           # findings, impact, AI-use declaration
   └── AI_USE_AND_SOURCES.md
   ```
3. Commit as you work. Your commit history is evidence of authorship (see §K); a single "final" commit will be questioned at defence.
4. Add the CLBG assessor account as a read-only collaborator and file a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core requirements.

1. Implement an incremental build keyed on `recorded_at` and prove equivalence with the full rebuild on both datasets.
2. Add a `v_commission` view with documented contract rates and reconcile commission to fee.
3. Port the model to a second engine (SQLite or Postgres) and report which features you could not reproduce (ASOF join, QUALIFY).
4. Design the controls that would page someone if `n_exceptions / n_txn_ids` exceeded a threshold, and justify the threshold from this data.

---

## K. Assessment Integrity

**AI tools are permitted** to explain concepts, suggest idioms or review your code. They may not do the assessment for you, and you must be able to explain and modify every line you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md` (template in `submission-template/`): tool, purpose and an example prompt. Undisclosed use discovered at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** adapted code and any papers or documentation you relied on, with links.
- **Collaboration:** discuss *general techniques* only. Do not share code, results or report text.
- **How understanding is verified.** At a 10-minute defence the assessor will (1) pick two `txn_id`s, one amended and one on a tier-change boundary, and ask you to trace them through every table; (2) ask which of your decision records you are least sure of and what evidence would change it; (3) set an unseen modification, such as a 5-day staleness limit for FX or a new event type `chargeback`, to be implemented live with a test.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Window functions and CTEs; the vocabulary of dimensional modelling; what a join does to row counts. |
| **New skill developed** | Temporal modelling: treating time as a first-class part of keys and joins, and building controls that make errors visible. |
| **Decisions the member must make** | Grain; SCD2 construction; how to resolve versions; staleness policy; build strategy; where exceptions live; how to reconcile. |
| **What must be investigated independently** | Which noise patterns the raw data contains (corrections, no-ops, duplicates, rate holes), and how large the Type 1 error is. |
| **Why it is interesting** | A realistic fintech reporting problem where each shortcut produces a plausible, wrong revenue figure, and a hidden test set that checks the semantics. |
| **Evidence of competence** | Exact agreement with independent ground truth on unseen data; a closed reconciliation; quantified shortcut error; decision records with real alternatives. |
| **Misconceptions exposed** | "The latest row is the truth for history"; "a left join is safe"; "drop what we cannot value"; "rates are daily"; "a model that runs is a model that reconciles". |
| **Preparation for later work** | Leads to DS-11 pipeline and orchestration work, DS-12 research reproducibility, and any analytics-engineering role. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
