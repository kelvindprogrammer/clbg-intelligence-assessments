# DS-T2-006: The Feed That Breaks

> *Every morning a partner drops yesterday's agent-banking transactions into your inbox. Some mornings the file is wrong in ways no schema check will catch. Design the data contract, the validator, the quarantine path and the alerts, and prove they work on twenty deliveries you didn't choose.*

![Format: System design](https://img.shields.io/badge/format-system%20design-5319e7) ![Tier 2](https://img.shields.io/badge/tier-2-fbca04) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-006` |
| **Title** | The Feed That Breaks: A Data Contract and Validation Framework for a Partner Feed |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Engineering and Independent Problem-Solving |
| **Unit** | [DS-03: Data Cleaning and Data Quality](../README.md) |
| **Format** | System design (secondary: Implementation) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 4 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 20–35 hours over 2–3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Solid pandas; Python packaging and pytest fixtures; YAML or JSON configuration; basic descriptive statistics (medians, ratios); file-system I/O. [DS-T1-008](../../../../tier-1/units/DS-03-data-cleaning-and-quality/DS-T1-008-stuck-drifting-spiking/README.md) is good preparation. |
| **Skills developed** | Writing a data contract with owners and severities; schema, semantic, freshness, volume and distribution checks; delivery-level vs row-level quarantine; calendar-aware baselines; learning baselines only from trusted data; alert design; fault-injection testing |
| **Technologies** | Python 3.10+, pandas, PyYAML, pytest. Optional: a validation library such as `pandera` or Great Expectations, declared and justified |

---

## B. Problem Statement

A Nigerian fintech runs an agent-banking reconciliation service. One of its data partners, a super-agent network with about 150 agents across eight states, delivers each business day's transactions as a CSV file plus a `manifest.json`, dropped into an inbox folder at around 02:15 the following morning. Downstream, the file feeds agent commission payments, fraud monitoring and a daily report to the partner's regulator-facing team. **A bad delivery that gets through costs real money.** Commissions are paid on wrong amounts, fraud rules fire on phantom spikes, and a regulator report understates volume.

The partner's interface document fixes the column list and nothing else. The fintech's data team has kept an incident log over the past year. Their deliveries have, at various times:

- renamed a column without notice;
- been re-sent from the previous day under a new date;
- been cut off part-way through the export, with a manifest that agreed with the truncated file;
- started writing timestamps in UTC;
- arrived with a manifest that promised more rows than the file contained;
- been written with the wrong delimiter by a new export tool;
- **changed units silently**, with amounts suddenly in kobo but the same column header;
- contained a few individually bad rows (unknown transaction types, negative amounts, fees larger than the amount, duplicated IDs, agents that don't exist).

And some deliveries look alarming but are **fine**. Volume drops sharply on public holidays and Sundays, and a validator that pages the on-call engineer every public holiday will soon be ignored.

You are asked to design and build the **data contract and validation framework** that sits between the inbox and everything downstream. You will be given twenty consecutive deliveries to develop against. The framework will then be judged on **two other twenty-day sequences** that you will never see, with different dates, different holidays and faults on different days.

**Fixed policy (agreed with the business):**

| Status | When | What happens |
|---|---|---|
| `accepted` | The delivery passes every delivery-level check and every row passes the row rules | All rows go downstream |
| `accepted_with_quarantine` | The delivery passes every delivery-level check, and some rows fail row rules, but **no more than 5%** of rows | Good rows go downstream; failing rows go to the quarantine area with reasons |
| `quarantined` | Any delivery-level check fails (unreadable, schema, manifest, freshness, duplicate delivery, volume, unit or distribution shift), **or more than 5%** of rows fail row rules | Nothing goes downstream; the whole delivery is held with reasons for a human |

The 5% line exists because when that many rows are bad, the export process itself is suspect, and it would be wrong to trust the "good" 95%. For duplicated `txn_id`s, the first occurrence is the good one and later occurrences fail.

---

## C. Objectives

You should be able to show that you can:

1. **Write a data contract** that a partner could sign: schema, row-level semantic rules, delivery-level rules, freshness, volume and distribution expectations, each with an owner and a severity.
2. **Implement** a validator driven by that contract rather than by hard-coded checks.
3. **Detect problems a schema can't see**: silent unit changes, re-sent deliveries, truncation, by comparing each delivery with a baseline.
4. **Build baselines that don't lie**: calendar-aware, and learned only from deliveries you accepted.
5. **Route** failures correctly: quarantine rows or whole deliveries, with explanations a human can act on, and alerts at the right severity.
6. **Prove** the framework with fault-injection tests that you construct, and evaluate it honestly against the sequence you were given.

---

## D. Technical Requirements

### D.1 Mandatory requirements

| ID | Requirement |
|---|---|
| **R1** | **Contract.** `contract/contract.yaml` (or JSON), loaded by your code, declares at minimum: the schema (columns, delimiter, encoding); row rules for every column; delivery rules (manifest agreement, freshness, duplicate delivery, the 5% row-failure line); volume expectations; and a distribution expectation that would catch a unit change. Every rule has an **owner** (partner or data team) and a **severity**. Every numeric threshold carries a one-line justification in a comment or in `DESIGN.md`. |
| **R2** | **Readability and schema.** Undecodable files, wrong delimiters and header mismatches lead to `quarantined` with a finding that names the problem precisely (for example "missing column amount_ngn; unexpected column amount"). |
| **R3** | **Row rules.** Each row is checked against the contract. Failing rows carry their failed rule IDs. |
| **R4** | **Delivery rules.** Manifest row count, freshness (share of rows on the business date), duplicate delivery (overlap with recently accepted `txn_id`s), and the 5% line. |
| **R5** | **Baselines.** Volume and amount-distribution checks compare each delivery with a baseline built **only from previously accepted deliveries**, adjusted for the type of day using [`public_holidays.csv`](resources/reference/public_holidays.csv) and the day of the week. Explain how your design behaves before enough history exists. |
| **R6** | **Outputs** (fixed, because the tests read them). `process_inbox(inbox, out, contract_path=None, agents_path=None, holidays_path=None)` processes deliveries in business-date order and writes: `out/ledger.csv` (one row per delivery, columns `business_date, status, n_rows, n_accepted, n_quarantined, findings`, where `findings` is `;`-separated rule IDs); `out/accepted/<date>.csv` for every non-quarantined delivery (good rows, original columns); `out/quarantine/<date>/` for every delivery with anything quarantined (failing rows with reasons, or the whole delivery plus a reason file); and `out/alerts.jsonl` (one JSON object per finding with at least `business_date`, `rule`, `severity`, `message`). It returns the ledger. Rerunning on the same inbox gives the same outputs. |
| **R7** | **Alerting design.** Define your severity levels and who gets which alert (for example: page on-call for a quarantined delivery on a payout day; email the partner for row-level failures; log-only for an accepted holiday). The code emits severities; `DESIGN.md` documents the routing. |
| **R8** | **Evaluation.** Run on the 20 public deliveries and present the ledger with your reasoning for each non-accepted delivery. Then build at least **six fault-injection fixtures of your own** (small synthetic deliveries or mutations of public ones) covering faults the public sequence does or doesn't contain, and show your framework's verdict on each. |

### D.2 Engineering requirements

- Contract-driven: changing a threshold or an allowed value is a contract edit, not a code edit.
- Modular: reading, row rules, delivery rules, baselines, routing and alerting are separately testable.
- **At least 15 tests of your own**, including the R8 fixtures and at least one "good but unusual" delivery that must be accepted.
- Processing the 20 deliveries takes under 60 seconds.
- Bounded dependencies in `requirements.txt`. If you use a validation library, explain what it does and what you still had to build.

### D.3 Security, privacy and operations

The data is **synthetic**, with fictional agents and transactions. Real transaction feeds are personal and financial data under the Nigeria Data Protection Act 2023 and sector rules. In `DESIGN.md`, cover:

- **Least privilege:** what can read the inbox, write the accepted area, and read the quarantine area? Quarantine often holds the *most* sensitive anomalies.
- **Retention:** how long quarantined deliveries are kept, and who may release or delete them.
- **Trust boundary:** the partner's file is untrusted input. What could a malicious or broken file do to your process (huge files, formula injection when someone opens a CSV in a spreadsheet, path tricks in `manifest.json`'s `file` field), and what you guard against.
- **Human approval:** releasing a quarantined delivery is a consequential action. Describe the release procedure and its audit trail. You don't need to implement it.

### D.4 Optional enhancements

- An incremental mode: persist state so that each morning processes only the new delivery.
- A `release` command that re-admits a quarantined delivery after human sign-off, and updates baselines.
- A partner-facing summary generated from `alerts.jsonl`.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Deliveries** | [`resources/inbox/`](resources/inbox/): 20 folders (`2026-06-01` … `2026-06-20`), each with `transactions.csv` and `manifest.json`. About 1 MB in total. |
| **Reference** | [`agents.csv`](resources/reference/agents.csv) (150 agents) · [`public_holidays.csv`](resources/reference/public_holidays.csv) (Nigeria's fixed-date 2026 holidays plus Easter; movable Islamic holidays are deliberately omitted because their dates are only confirmed close to the day, so think about how your design would handle them) |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed. The partner, agents, terminals and transactions are fictional. The generator is kept in the assessor kit because it reveals which days are faulty. |
| **Licence** | CC BY 4.0 (same as this repository's content) |
| **Integrity** | The contract test checks a SHA-256 over the whole inbox. Don't modify it; build your fault fixtures elsewhere (for example in `tests/fixtures/`). |

**Partner interface (all the partner has documented):**

| Column | Partner's description |
|---|---|
| `txn_id` | Unique transaction ID, `TX` + 8 digits |
| `agent_id` | Agent code, `AG` + 5 digits; see the agent register |
| `txn_time` | Local time, ISO 8601 with offset `+01:00` |
| `txn_type` | `cash_in`, `cash_out`, `transfer`, `bill_payment`, `airtime` |
| `amount_ngn` | Amount in naira, 2 dp |
| `fee_ngn` | Fee in naira, 2 dp |
| `status` | `success`, `failed`, `reversed` |
| `terminal_id` | POS terminal, 8 digits starting with `2` |
| `state` | Agent's state |

`manifest.json` contains `business_date`, `file`, `row_count`, `generated_at`, `partner` and `schema_version`.

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-03-data-cleaning-and-quality/DS-T2-006-the-feed-that-breaks
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract
pytest
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `contract/contract.yaml` | The contract, readable by the partner and executable by your code |
| 2 | `feedguard/` package | The validation framework |
| 3 | `tests/` (provided plus ≥ 15 of your own, including `tests/fixtures/`) | Fault-injection evidence |
| 4 | `outputs/` from a run on the public inbox | The ledger, accepted and quarantine areas, and alerts |
| 5 | `DESIGN.md` (≤ 2,500 words plus diagrams), from the [template](submission-template/DESIGN.md) | Architecture, contract rationale, thresholds, alert routing, security and operations, evaluation |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 7 | 15-minute defence | Justify and debug (see §K) |

---

## G. Acceptance Criteria

⚙ = automated (public tests, plus the hidden suite on **two unseen 20-day sequences**); ✍ = assessor judgement.

1. ⚙ All provided tests and your own tests pass in a clean environment.
2. ⚙ **Policy correctness:** on both hidden sequences, **every** delivery receives the status the fixed policy requires (40 of 40). *Justification:* each injected fault is unambiguous under the policy. They range from total schema failure to a 100× unit change or a 55–65% volume drop, and holidays are listed in the calendar. The reference gets 80 of 80 across four sequences. A miss here means a bad file reaches payments, or a holiday pages someone, both of which the business has ruled out.
3. ⚙ **Row quarantine is exact:** on `accepted_with_quarantine` days, no injected bad row is accepted, each duplicated ID is accepted exactly once, and **no good row** is quarantined. *Justification:* row rules are deterministic checks against a contract, so anything less than exact is a bug, not a trade-off.
4. ⚙ **Holidays** are accepted, and **quarantined deliveries** leave nothing in the accepted area.
5. ⚙ No `txn_id` is accepted twice across deliveries, and every accepted row satisfies the contract.
6. ✍ The contract has an owner, a severity and a justification for every rule and threshold, and changing one doesn't need a code change.
7. ✍ Baselines learn only from accepted deliveries. `DESIGN.md` explains what goes wrong otherwise, with a concrete example from the public sequence.
8. ✍ The R8 fault-injection fixtures cover at least six distinct faults, including one the public sequence lacks and one good-but-unusual delivery.
9. ✍ The alert routing and the security/operations section are specific and actionable.

---

## H. Evaluation Rubric

Full rubric: **[rubric.md](rubric.md)**.

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Architecture and implementation quality | 20 |
| Methodology (contract and threshold design) | 10 |
| Testing and evaluation (fault injection) | 15 |
| Documentation and operations | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

---

## I. Submission Instructions

1. A private repository named `clbg-DS-T2-006-<your-github-username>`, built from this assessment's `starter/`, `tests/`, `resources/` and `submission-template/`.
2. Expected structure:
   ```text
   clbg-DS-T2-006-<username>/
   ├── README.md              # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── contract/contract.yaml
   ├── feedguard/
   ├── tests/                 # including tests/fixtures/
   ├── resources/             # unchanged
   ├── outputs/
   ├── DESIGN.md
   └── AI_USE_AND_SOURCES.md
   ```
3. Commit as you work.
4. Submit through the **Assessment submission** issue template with the repository URL and commit SHA, and add the assessor account as a read-only collaborator.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Movable holidays.** Eid dates are confirmed only days in advance. Design and implement a way for operations to declare an expected low-volume day at short notice, with an audit trail.
2. **Timestamp sanity beyond format.** Suppose the partner's clock is off by one hour but the offset still says `+01:00`. Which statistic would reveal it? Implement it as a warning.
3. **Incremental and idempotent.** Make the framework process one new delivery per run using persisted state, and prove that replaying a day changes nothing.
4. **Contract versioning.** The partner announces `schema_version` 1.3 with a new optional column. Design how the contract and validator handle versioned schemas without accepting silent renames.

---

## K. Assessment Integrity

**AI tools are permitted** for learning and for reviewing your design or code. **They are not permitted to design the contract or write the framework for you.** Disclose every use in `AI_USE_AND_SOURCES.md`.

- **Cite** any data-contract or data-quality material you used.
- **Collaboration:** you may discuss general approaches. You may not share contracts, thresholds, code or ledgers.
- **How understanding is verified (15 minutes):**
  1. The assessor hands you a **new delivery** you haven't seen (for example an extra column, or amounts multiplied by 1,000) and asks you to predict your framework's verdict *before* running it, then run it.
  2. You walk through how a public-holiday delivery flows through your volume check, and what would happen if the holiday were missing from the calendar.
  3. **Live change:** tighten or relax a threshold, or add a rule (for example "fee must follow the published fee schedule"), as a contract edit, and show the effect.
  4. "Your baseline uses accepted deliveries only. Show me the line of code that enforces that."

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | pandas, pytest fixtures, configuration files, medians and ratios. |
| **New skill developed** | Treating data quality as an **interface agreement with operations attached**: a contract with owners, checks that run every day, and a clear path for what happens when they fail. |
| **Decisions the member must make** | Contract structure; each threshold and its justification; baseline design under calendar effects and short history; what goes to row versus delivery quarantine beyond the fixed policy; alert severities and routing. |
| **What must be investigated independently** | What each public delivery's problem is; why a schema check alone misses the unit change and the truncation; how the holiday looks without a calendar; what a poisoned baseline would do. |
| **Why it's interesting** | The hardest faults (kobo amounts, truncation with a matching manifest, a re-sent file) pass every schema check. The most alarming-looking delivery (the holiday) is fine. Getting both right requires baselines that are calendar-aware and learned only from trusted data, which is exactly the judgement production data teams need. |
| **Evidence of competence** | 40/40 policy outcomes and exact row quarantine on unseen sequences; the member's own fault-injection suite; live prediction of verdicts on new deliveries. |
| **Misconceptions exposed** | "Schema validation is data validation." "If the manifest agrees, the file is complete." "Low volume means a broken delivery." "Baselines should learn from everything." "Alerts are free." |
| **Preparation for later work** | It leads into DS-11 data pipelines with validation gates, ML monitoring (drift and data contracts for features), and any partner-integration role in fintech, health or telecoms. |

**Suggested approach** (optional): before writing code, open all twenty deliveries and write one line about each. Draft the contract next, then the reading and schema checks, then row rules, then delivery rules, and baselines last. Write a fault fixture for each failure you implement.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
