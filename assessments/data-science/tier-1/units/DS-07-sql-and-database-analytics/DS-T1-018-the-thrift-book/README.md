# DS-T1-018: The Thrift Book: Ten Questions for a Market Cooperative

> *Ten precise questions, one small SQLite ledger, and three places where a plausible query quietly returns the wrong number.*

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-018` |
| **Title** | The Thrift Book: Ten Questions for a Market Cooperative |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-07: SQL and Database Analytics](../README.md) |
| **Format** | Implementation (secondary: debugging) |
| **Difficulty** | Technical 2 · Mathematical 1 · Research 1 · Engineering 1 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 6-10 hours over 1 week |
| **Collaboration** | Individual |
| **Compute** | Any laptop; no GPU, no network after setup |
| **Recommended prerequisites** | SELECT/WHERE/ORDER BY; reading an entity-relationship diagram; running `pytest`. No prior JOIN or window-function experience is assumed beyond what the unit teaches. |
| **Skills developed** | Joins, aggregation, NULL handling, pre-aggregation, anti-joins, tie handling, verifying results against the data |
| **Technologies** | SQLite 3 (bundled with Python), Python 3.10+, pytest |

---

## B. Problem Statement

A market thrift cooperative (*ajo* or *esusu* in Yoruba and Igbo trading communities) collects weekly contributions from traders in a group and lends to members from the pool. The cooperative's treasurer keeps everything in a small SQLite database, `thrift.db`: **groups, members, contributions, loans and repayments**. The committee meets on Saturday and has ten questions it needs answered precisely, because the answers decide who is eligible for the next loan cycle and which group leaders are called in.

The questions are easy to *state* and easy to answer *wrongly*. This ledger was exported by hand, so it behaves like real operational data:

- some contributions have **no payment channel** (NULL), and `channel <> 'cash'` does not mean what it looks like;
- some members **never contributed** and must still appear where the question says so;
- members hold **several loans and several repayments**, so joining everything at once multiplies rows (a *fan-out*) and inflates totals;
- some contributions were **double-posted** (same member, day and amount on two rows), and some loans were **overpaid**.

Your job is to write ten SQL queries to an exact specification, then check each result against the data until you trust it. A query that runs is not a query that is right.

**Known facts.** Amounts are whole naira. Dates are ISO text (`YYYY-MM-DD`). `loans.status` is `active`, `cleared` or `defaulted`. Each repayment belongs to one loan. A member belongs to exactly one group.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Write joins (inner, left and anti-joins) that keep the rows the question requires.
2. Aggregate correctly with `GROUP BY` and `HAVING`, and explain when `WHERE` is the wrong place for a condition.
3. Handle `NULL` deliberately with `IS NULL` and `COALESCE` instead of by accident.
4. Recognise and remove join fan-out by aggregating child tables before joining.
5. Use `NOT EXISTS` / anti-joins and correlated or CTE subqueries for "for each group, the best member" questions, including ties.
6. Verify a result independently (row counts, spot checks, reconciliation) and report what the data's defects mean for each answer.

---

## D. Technical Requirements

### D.1 Mandatory requirements

Put one SQL file per question in `queries/` (the starter has the ten stubs with the exact column list and ordering in each file's header comment). Each file holds **one read-only statement** (`SELECT`, optionally with a `WITH` clause) and returns exactly the named columns, in the named order.

| ID | Query | Question |
|---|---|---|
| **R1** | `q01.sql` | Total contributions per group, including groups with none (total 0). |
| **R2** | `q02.sql` | Members who never contributed. |
| **R3** | `q03.sql` | Members with at least 20 contribution rows: count and average amount (2 decimals). |
| **R4** | `q04.sql` | Net position per member: contributions minus outstanding balance on non-cleared loans (per-loan balance floored at 0). Must not be distorted by multiple loans/repayments. |
| **R5** | `q05.sql` | Monthly contribution totals for calendar year 2025. |
| **R6** | `q06.sql` | Loans whose repayments exceed the principal. |
| **R7** | `q07.sql` | Groups in which no member holds a `defaulted` loan. |
| **R8** | `q08.sql` | Contribution counts per channel, NULL reported as `unknown`. |
| **R9** | `q09.sql` | Suspected double postings (same member, date and amount on more than one row), with the number of copies. |
| **R10** | `q10.sql` | Top saver(s) per group, returning every member tied for the top. |

### D.2 Engineering requirements

- Queries are **read-only**: no `INSERT`, `UPDATE`, `DELETE`, DDL or `PRAGMA`. The tests open the database in read-only mode.
- Readable formatting: one clause per line, meaningful aliases, a one-line comment per query explaining any non-obvious choice.
- No hard-coded results or member/loan IDs. Hidden tests run your files on **differently seeded databases**.
- `REPORT.md` (template provided) answers the reasoning questions in §F.

### D.3 Privacy and ethics

The data is fictional (no real people; phone numbers are synthetic). Treat it as if it were real: cooperative finance data reveals who is in debt. Under the Nigeria Data Protection Act 2023 a real treasurer would need a lawful basis, would limit who sees member-level results, and would not publish named defaulters. In `REPORT.md` write three sentences on how you would restrict q04 and q07 if this were real.

### D.4 Optional enhancements

Add an index and show with `EXPLAIN QUERY PLAN` that q03 or q10 uses it; or write q10 a second way (window function) and show both agree.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/thrift.db`](resources/data/thrift.db), a SQLite database (about 80 KB): 8 groups, 110 members, about 2,600 contributions, loans and repayments |
| **Provenance** | **Synthetic**, produced by a deterministic CLBG generator (seed 2026). Names are random combinations of common Nigerian given names and surnames; some namesakes are deliberate. Market names are real trading places; the groups are fictional. |
| **Licence** | CC BY 4.0 |
| **Integrity** | The contract test checks the database's SHA-256. Do not modify it. |

Tables: `groups(group_id, name, market, weekly_target_ngn)`, `members(member_id, full_name, group_id, joined_on, phone)`, `contributions(contribution_id, member_id, paid_on, amount_ngn, channel)`, `loans(loan_id, member_id, issued_on, principal_ngn, status)`, `repayments(repayment_id, loan_id, paid_on, amount_ngn)`.

**Known limitations.** One year of data; amounts are not inflation-adjusted; `phone` has NULLs. Double postings are *suspected*, not proven.

**Setup**
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract      # passes immediately
pytest                  # fails until your queries are right
```
Inspect the database with the `sqlite3` shell, DB Browser for SQLite or Python's `sqlite3` module.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `queries/q01.sql` ... `q10.sql` | The evidence of SQL fluency |
| 2 | `REPORT.md` from the [template](submission-template/REPORT.md) | Shows how you checked each answer and what the data defects imply |
| 3 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 4 | A 5-minute live defence | Verifies you understand your own queries |

---

## G. Acceptance Criteria

Criteria marked ⚙ are checked by the public and hidden test suites. Criteria marked ✍ are checked by an assessor.

1. ⚙ All ten public query tests pass: exact columns, order and rows.
2. ⚙ Queries are single read-only statements and contain no pasted results.
3. ⚙ Hidden tests: your files return the reference results on two re-seeded databases (same schema, different data).
4. ⚙ q04 equals the reference for every member. Naively joining contributions, loans and repayments in one `FROM` changes the totals, and the tests will detect it.
5. ✍ `REPORT.md` explains, for q04, q08 and q10, what the naive query would have returned and why it is wrong, with one number from the data.
6. ✍ `REPORT.md` states how many contributions are suspected double postings and what the treasurer should do before relying on q01 and q05, with a justification for not deleting them yourself.
7. ✍ The privacy paragraph (§D.3) is present and specific.

---

## H. Evaluation Rubric

The full rubric with performance levels is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 15 |
| Methodology and verification | 15 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates (passing defence, reproducible run, integrity declaration). See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. Create a **private** GitHub repository named `clbg-DS-T1-018-<your-github-username>` from this assessment's `starter/`, `tests/` and `resources/` folders and the `submission-template/` files.
2. Expected structure:
   ```text
   clbg-DS-T1-018-<username>/
   ├── queries/q01.sql ... q10.sql
   ├── tests/            # provided tests
   ├── resources/        # unchanged
   ├── REPORT.md         # includes the AI-use declaration
   └── AI_USE_AND_SOURCES.md
   ```
3. Commit as you work. Your commit history is evidence of authorship (see §K); a single "final" commit will be questioned at defence.
4. Add the CLBG assessor account as a read-only collaborator and file a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core requirements.

1. Write q10 with a window function (`RANK() OVER`) and prove it matches your join version.
2. Show with `EXPLAIN QUERY PLAN` the difference an index on `contributions(member_id)` makes to q03.
3. Find members whose loan was issued before they joined and explain what that could mean.

---

## K. Assessment Integrity

**AI tools are permitted** to explain concepts, suggest idioms or review your code. They may not do the assessment for you, and you must be able to explain and modify every line you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md` (template in `submission-template/`): tool, purpose and an example prompt. Undisclosed use discovered at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** adapted code and any papers or documentation you relied on, with links.
- **Collaboration:** discuss *general techniques* only. Do not share code, results or report text.
- **How understanding is verified.** At the defence the assessor will (1) pick one of your queries and ask you to explain every clause; (2) ask what would happen to q04 if a member had a second loan with two more repayments; (3) give a small unseen modification, such as "exclude the double postings from q01", and ask you to make it live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Basic SELECT; reading a schema. |
| **New skill developed** | Verifying SQL against the data, not against whether it runs. Spotting fan-out and NULL traps. |
| **Decisions the member must make** | Where to pre-aggregate; join type per question; how to treat ties and NULL; how to floor a per-loan balance. |
| **What must be investigated independently** | Which queries return plausible-but-wrong numbers, and how to prove it with a reconciliation. |
| **Why it is interesting** | A familiar Nigerian savings institution, and traps that are realistic: hand-exported ledgers really do contain double postings. |
| **Evidence of competence** | Exact result match on differently seeded databases, plus the explanation of the naive wrong answers. |
| **Misconceptions exposed** | "If it runs it is right"; `INNER JOIN` everywhere; `AVG` and `COUNT` treat NULL the same; `WHERE` and `HAVING` are interchangeable. |
| **Preparation for later work** | Leads to DS-T2-013 (performance and window functions) and DS-T3-011 (analytical model design). |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
