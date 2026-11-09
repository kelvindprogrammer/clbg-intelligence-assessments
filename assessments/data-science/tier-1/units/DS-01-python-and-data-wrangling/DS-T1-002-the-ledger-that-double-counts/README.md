# DS-T1-002: The Ledger That Double-Counts

> *A POS agent-banking settlement script has paid agents the wrong commission for months, and nobody knows why. Find every defect, prove each one with a failing test, fix it, and put a Naira figure on what each one cost.*

![Format: Debugging & Forensics](https://img.shields.io/badge/format-debugging%20%26%20forensics-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-002` |
| **Title** | The Ledger That Double-Counts: Debugging a Mobile-Money Settlement Pipeline |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-01: Python and Data Wrangling](../README.md) |
| **Format** | Debugging & Forensics |
| **Difficulty** | Technical 2 · Mathematical 1 · Research 1 · Engineering 2 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 8–14 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | pandas `merge`, `groupby` and boolean filtering; reading a traceback; writing a `pytest` test. Recommended: [DS-T1-001](../DS-T1-001-the-price-watch-bulletin/README.md) |
| **Skills developed** | Reading code against a specification; minimal reproducing examples; regression testing; join cardinality; effective-dated lookups; deduplication on a business key; time zones; interval boundaries; pandas copy semantics; impact measurement |
| **Technologies** | Python 3.10+, pandas, NumPy, pytest |

---

## B. Problem Statement

A (fictional) Lagos fintech runs a network of about 140 **POS agents**: shops, kiosks and pharmacies where customers withdraw cash, deposit, transfer and pay bills on a card terminal. Every night, an aggregator receives the day's transaction messages from the payment switch and runs `daily_settlement()`. That script decides how much **commission** each agent earns. For many agents, the commission is a large part of their income.

The finance team has noticed that the network totals "never quite match the switch". Agents in Kano complain that they are paid less than their terminals show. A tier upgrade in one region seemed to *double* some agents' commission. The contractor who wrote the code has left. You have been asked to investigate.

You have:

- [`starter/settlement/pipeline.py`](starter/settlement/pipeline.py): the **legacy code**, in production since 2024. Every function has a docstring that states what it is **supposed** to do (the specification, agreed with finance). The code is what it **actually** does.
- Two weeks of data in [`resources/data/`](resources/data/): the switch feed as received (`transactions.csv`), the agent tier history (`agents.csv`), and the switch's **own** daily control totals (`switch_control_totals.csv`), which are known to be correct.

**Your job is forensic.** Nobody will tell you how many defects there are, or where. You must:

1. **Find** every place where the code does not meet its specification.
2. **Prove** each defect with a small, failing test *before* you fix it.
3. **Fix** it, without changing any function's name, parameters or specification.
4. **Measure** what each defect cost, in transactions, Naira of value, fees and agent commission, on the real data.
5. **Explain** your findings to the finance team, who are not programmers.

**What makes it hard.** The legacy code runs without errors and produces plausible numbers. Some defects only affect a few rows. Some *partly cancel each other out*, so fixing one can make the network total look worse before it gets better. And at least one line looks correct to most people who read it. The control totals tell you that something is wrong, but not what. Reading code against a specification, and building minimal examples that isolate one behaviour, is the core skill of debugging data code, and the one this assessment develops.

**Settlement policy** (the rules finance agreed; they are encoded in [`rules.py`](starter/settlement/rules.py), which is correct):

- A transaction settles only if its **final** status is `SUCCESS`. `FAILED` and `REVERSED` transactions contribute nothing.
- The switch **resends** a message when it gets no acknowledgement in time, and sends a **new message for the same `txn_ref`** when a status changes later (for example, a customer dispute reverses a cash-out hours afterwards). The message received **latest** is authoritative.
- The **business date** is the calendar date in **West Africa Time** (WAT, UTC+1, no daylight saving). The switch's timestamps are in UTC.
- Fees apply to `CASH_OUT` and `TRANSFER` only: ₦50 up to and **including** ₦5,000; ₦100 above ₦5,000 up to and including ₦20,000; ₦200 above ₦20,000.
- The agent receives a share of the fee that depends on their tier **on the business date**: Bronze 40%, Silver 50%, Gold 60%. An agent's tier history has one row per period (`valid_from` inclusive, `valid_to` exclusive, blank for the current row). Agents not yet in the tier file are reported as `UNASSIGNED` and earn no commission, but their transactions still count.
- Agent IDs are `AG` followed by four digits. Some terminal firmware sends them in lower case or with stray spaces.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Read code against a written specification** and identify every behaviour that deviates from it.
2. **Isolate a defect with a minimal example:** a DataFrame of a few rows that demonstrates exactly one wrong behaviour.
3. **Write regression tests** that fail on the defective code and pass on the fixed code, and show the red-then-green sequence in your commit history.
4. **Explain the pandas behaviours behind the defects:** join cardinality and fan-out, inner versus left joins, deduplication keys, copy semantics and chained assignment, time-zone conversion, and interval boundaries.
5. **Measure the impact** of each defect in isolation, and explain why the isolated impacts do not add up to the combined error.
6. **Reconcile** your output with an independent control total.
7. **Communicate** the findings and their financial consequences to a non-technical owner.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Function names, parameters, docstrings and [`rules.py`](starter/settlement/rules.py) are **fixed**. Fix the bodies.

| ID | Requirement |
|---|---|
| **R1** | Every function in [`pipeline.py`](starter/settlement/pipeline.py) meets its docstring specification. This includes the sentences about **not modifying the input** and **every input row appearing exactly once**. |
| **R2** | **One regression test per defect** in `tests/test_member_regressions.py`. Each test is minimal (it builds its own small DataFrame), targets one defect, and is named after it (for example `test_d3_...`). Each must fail on the legacy code and pass on yours. Your commit history must show the test committed **before** the fix for at least four of the defects. |
| **R3** | Implement `reconcile_with_switch(settlement, control)` in [`reconcile.py`](starter/settlement/reconcile.py), exactly as its docstring says. |
| **R4** | `impact.py` (a script in your repository root) writes `outputs/impact.csv`, with one row per defect plus one row for the full legacy pipeline. Its columns are `defect, description, txn_count_delta, value_ngn_delta, fees_ngn_delta, commission_ngn_delta, agent_days_delta`. Each delta is **legacy behaviour minus correct behaviour**, on the official data, computed by re-introducing **that one defect alone** into your fixed pipeline. The script keeps a copy of the legacy code (for example under `legacy/`) so that it can do this. |
| **R5** | `python -m settlement resources/data --out outputs/` (the CLI is provided) writes `settlement.csv` and `reconciliation.csv`, and every business day matches the switch. |
| **R6** | `FORENSICS.md` (at most 1,500 words plus tables, using the [template](submission-template/FORENSICS.md)) gives, for each defect: the symptom, the root cause in one or two sentences, the minimal example, the fix, and the measured impact. It also explains why the isolated impacts do not sum to the full-legacy row, and which agents were underpaid and which overpaid. |

### D.2 Engineering requirements (mandatory)

- **Do not rewrite from scratch.** Fix the legacy functions in place. The assessors compare your diff with the original, and a small, explained diff is better evidence than a rewrite.
- **No new dependencies** beyond [`starter/requirements.txt`](starter/requirements.txt).
- **No hard-coding.** No agent IDs, dates or totals in the code. The hidden tests regenerate the ledger.
- **No warnings.** Running the fixed pipeline on the official data emits no pandas warnings.
- **Data is read-only.** The contract tests check the checksums.
- **Tests.** Keep the provided tests passing. Besides the regression tests, add at least four other tests of your own.

### D.3 Privacy and responsibility

The data is **synthetic**. Agents are fictional shop codes, and there are no customers or personal details. Real settlement data is financial data about identifiable small businesses, and customer-level transaction data is personal data under the Nigeria Data Protection Act 2023. In `FORENSICS.md`, add one paragraph on how you would handle a real investigation: who may see agent-level figures, how corrected payments would be communicated to agents, and why a forensic copy of the data should be access-controlled and deleted when the investigation closes.

### D.4 Optional enhancements (not required for full marks)

- A `--explain AGENT_ID` CLI flag that prints every transaction counted for one agent on one day, with its fee and tier.
- A data-contract check that runs before settlement and rejects malformed input (unknown statuses, unparseable timestamps, overlapping tier periods) with clear messages.
- A note on which defects would also appear in pandas 2.x, which only in pandas 3.x, and why. Copy-on-Write is the key topic.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | [`transactions.csv`](resources/data/transactions.csv) (12,346 messages, about 1.2 MB), [`agents.csv`](resources/data/agents.csv) (tier history), [`switch_control_totals.csv`](resources/data/switch_control_totals.csv) (14 business days, 1 to 14 September 2026) |
| **Provenance** | **Synthetic.** It was generated by CLBG with a fixed seed from a simple simulation of agent activity, retries and reversals. Agents are random shop codes, and no person or real business is described. |
| **Licence** | CC BY 4.0, the same as this repository's content |
| **Integrity** | SHA-256: `transactions.csv` `d51ecf1c191c3d99d35774999692a9c25d14072497200cf4e8dbc1fe1c9a498d`; `agents.csv` `3e1f18cb08ac476f45acf556a4681ceb3ad1dc19cae20fb7d36ebc33bdaff469`; `switch_control_totals.csv` `60c7aff5f397e268c2a85563fce1d73b7da943e7053db1a8b091e70496037650` |
| **Generator** | Kept in the assessor kit, because it writes the ground truth. |

**`transactions.csv`**: `txn_ref` (the business key), `agent_id`, `terminal_id`, `channel` (`CARD`, `USSD`, `QR`), `txn_type` (`CASH_OUT`, `CASH_IN`, `TRANSFER`, `BILL_PAY`), `amount_ngn`, `status` (`SUCCESS`, `FAILED`, `REVERSED`), `switch_time_utc` (when the transaction happened, ISO 8601 UTC), `received_at_utc` (when the aggregator received this message). Rows are in arrival-batch order, not time order.

**`agents.csv`**: `agent_id`, `state`, `tier`, `valid_from`, `valid_to` (ISO dates, `valid_to` blank for the current row).

**`switch_control_totals.csv`**: `business_date` (WAT), `successful_count`, `successful_value_ngn`. These are network-wide totals of transactions whose final status is `SUCCESS`, computed by the switch. They are **correct**, but they say nothing about fees, commission or individual agents.

**Known limitations (by design).** The control totals check counts and value only. A defect that changes only fees or commission cannot be detected from them, and you must find it by reading the code against the policy. That is deliberate.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-01-python-and-data-wrangling/DS-T1-002-the-ledger-that-double-counts
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract      # passes on the legacy code: checks data and API
pytest                  # several tests fail: they describe the specification
python -m settlement resources/data --out /tmp/legacy_out   # fails until R3 is implemented
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | The fixed `settlement/` package | The corrected logic, judged on correctness and on the size and clarity of the diff |
| 2 | `tests/test_member_regressions.py` plus at least four other member tests | Proof that each defect existed and is now fixed |
| 3 | `impact.py` and `outputs/impact.csv` | A measured, reproducible cost for each defect |
| 4 | `outputs/settlement.csv`, `outputs/reconciliation.csv` | The corrected settlement and its reconciliation with the switch |
| 5 | `FORENSICS.md`, from the [template](submission-template/FORENSICS.md) | Communicates the findings to finance |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 7 | A 5–10 minute live defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. ⚙ marks automated checks, and ✍ marks checks done by hand.

1. ⚙ `pytest` passes all provided and member tests in a clean environment.
2. ⚙ **Exact settlement.** On the official ledger **and** on two regenerated ledgers, every `(agent_id, business_date)` row matches the hidden ground truth: identical keys, counts and tiers, and money within ₦0.005. *Justification:* settlement is a payment. A one-kobo error repeated across thousands of agent-days is a real liability, and the policy has no ambiguity, so the only acceptable error is rounding.
3. ⚙ **Reconciliation.** `reconcile_with_switch` reports a match on every business day for all three ledgers, and detects a deliberately perturbed settlement.
4. ⚙ **Specification sentences.** The hidden suite tests each docstring sentence with its own minimal examples. That includes "the input is not modified", "every input row appears exactly once", status corrections arriving in either order, tier boundaries and fee boundaries.
5. ⚙ The CLI runs in **under 30 seconds** on the official data. *Justification:* the reference takes about 4 seconds including Python start-up, and 30 seconds is generous for any vectorised fix, but would catch a fix that loops over rows calling pandas.
6. ✍ Every defect has a regression test that fails on the legacy code. At least four were committed before their fix.
7. ✍ `impact.csv` reproduces when the assessor runs `python impact.py`. Its isolated deltas are plausible and correctly signed, and `FORENSICS.md` explains the interaction between defects.
8. ✍ The diff from the legacy code is small and every change is explained. A rewrite with no explanation fails this criterion.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 15 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Methodology: isolate, prove, fix, measure | 20 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 5 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own repository.** Copy this assessment's `starter/` contents, `tests/`, `resources/` and `submission-template/` into a new **private** GitHub repository named `clbg-DS-T1-002-<your-github-username>`. **Make your first commit before you change any code**, so the legacy version is in your history.
2. **Expected structure:**
   ```text
   clbg-DS-T1-002-<username>/
   ├── README.md                       # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── settlement/                     # the fixed package
   ├── legacy/                         # an untouched copy of the legacy pipeline, used by impact.py
   ├── impact.py
   ├── tests/                          # provided tests + test_member_regressions.py + others
   ├── resources/                      # unchanged
   ├── outputs/settlement.csv
   ├── outputs/reconciliation.csv
   ├── outputs/impact.csv
   ├── FORENSICS.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** For each defect, a "test: reproduce D<n>" commit followed by a "fix: D<n>" commit is ideal.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator, then filing a submission issue in the CLBG assessments repository with the **Assessment submission** template. Include the repository URL and the commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback, but never replace the core requirements.

1. **Back-pay schedule.** Using your corrected settlement and the legacy one, produce the list of agents owed money (and agents overpaid), with amounts. Discuss how a company should handle overpayments made to small businesses because of its own bug.
2. **Property-based testing.** Without new dependencies, write a test that generates random small ledgers and checks invariants: the settled count never exceeds the number of unique `txn_ref`s; the sum over agents equals the network total; commission ≤ 60% of fees.
3. **Make it impossible to recur.** Add the minimum set of runtime assertions (join cardinality, row counts, key uniqueness) that would have caught every defect in production. Show that each assertion fires on the legacy code.
4. **The pandas 2 vs 3 question.** Investigate how Copy-on-Write changed the behaviour of the patterns in this code, with a short demonstration in both versions.

---

## K. Assessment Integrity

**AI tools are permitted for learning:** to explain what `validate="one_to_one"` does, how `tz_convert` works, or what chained assignment is. **They must not find or fix the defects for you.** Pasting `pipeline.py` into an AI tool and asking "what's wrong with this?" is not permitted. That is the assessment. You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`: which tool, what for, and an example prompt. Undisclosed use that becomes apparent at the defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** any code you adapted, with a link.
- **Collaboration:** you may discuss general pandas behaviour with other members. You may not share defects found, tests, code, impact figures or report text.
- **How your understanding is verified.** In the 5–10 minute defence, the assessor will:
  1. pick one defect and ask you to reproduce it live on a three-row DataFrame, without your notes;
  2. ask you why two of your isolated impacts do not add up to the combined legacy error;
  3. introduce a **new, unseen defect** into your fixed code (for example a changed join type, an off-by-one boundary, or a timezone slip) and ask you to find it using your tests and reconciliation, explaining as you go.

  Your commit history is checked for the red-then-green pattern described in R2.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | pandas filtering, `merge` and `groupby`; Python functions; reading tracebacks and warnings; basic `pytest`. |
| **New skill developed** | Debugging data code methodically: specification, minimal reproduction, failing test, fix, impact measurement. And the habit of treating every join, deduplication and timestamp as a hypothesis to check. |
| **Decisions the member must make** | Which behaviours violate the specification. How to isolate each one. How to fix it with the smallest change. How to attribute impact when defects interact. How to explain financial consequences. |
| **What must be investigated independently** | The number, location and nature of the defects. Nobody says how many there are. The control totals reveal only some of them. |
| **Why it's interesting** | The code runs cleanly and the totals look plausible. Defects mask each other: one join loses rows while another duplicates them. One defect is invisible to the control totals and can only be found by reading the policy. One line looks right to most readers. |
| **Evidence of competence** | Exact agreement with hidden ground truth on regenerated ledgers; per-sentence specification tests; red-then-green commit history; a reproducible impact table; live reproduction of a defect and diagnosis of an injected one at the defence. |
| **Misconceptions exposed** | "If it runs without errors, it's right." "`drop_duplicates()` removes duplicates." "A merge returns one row per left row." "Assigning to a filtered frame updates the original." "A timestamp's date is its business date." "`pd.cut` boundaries are obvious." |
| **Preparation for later work** | Reconciliation and defensive joins underpin data pipelines (DS-11) and data-quality work (DS-03). Effective-dated lookups recur in feature engineering, where getting them wrong causes leakage (ML-04). |

**Suggested approach**, for members who want it (you may ignore it):

1. Implement R3 first, run the legacy pipeline, and look at the reconciliation. Where are the differences, and on which days?
2. Then read each function's docstring and code side by side. For each sentence of the docstring, ask: "what three-row DataFrame would show whether this is true?"
3. Fix one defect at a time, rerunning the reconciliation after each. Write down what changed, and be surprised when it gets worse.
4. Build `impact.py` last, from a fixed pipeline plus a copy of the legacy functions.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
