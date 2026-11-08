# DS-T2-013: The Slow Meter Report: Making Five Analytical Queries Fast Without Making Them Wrong

> *Five reports that take minutes at scale. Rewrite them, choose your indexes, and prove with counted work, not a stopwatch, that you won.*

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-013` |
| **Title** | The Slow Meter Report: Making Five Analytical Queries Fast Without Making Them Wrong |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Competence |
| **Unit** | [DS-07: SQL and Database Analytics](../README.md) |
| **Format** | Optimisation (secondary: comparative) |
| **Difficulty** | Technical 3 · Mathematical 1 · Research 2 · Engineering 3 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 10-16 hours over 1-2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM; no GPU; no network after setup |
| **Recommended prerequisites** | Joins, aggregation and subqueries (DS-T1-018 level); a first look at window functions; running `pytest`. |
| **Skills developed** | Window functions, frame semantics (ROWS vs RANGE), index design, query plans, deterministic benchmarking, scaling experiments |
| **Technologies** | SQLite 3.25+ (bundled with Python 3.10+), Python, pytest, matplotlib optional for the scaling plot |

---

## B. Problem Statement

A Nigerian electricity distribution company sells prepaid energy: a customer buys a token, the sale is logged as a **vend** against a **meter**, and each meter hangs off a **feeder**. The revenue-assurance team runs five reports every morning. They were written years ago by someone who loved correlated subqueries. On last year's data they took seconds. On this year's they take minutes, and the data will triple when the company adds three more zones.

You have a 6-feeder, 150-meter, 3,000-vend extract and the five existing queries (the **baselines**, in `resources/baseline/`). The baselines are *correct*; they are just wasteful. Your task is to rewrite each as `queries/s1.sql` ... `s5.sql` so that it returns **exactly the same rows** while doing a small fraction of the work, and to explain, with measurements, why your design is fast and where it would stop being fast.

Four things make this more than "use window functions":

- **Ties and ordering.** Vends are ordered by `(vended_on, vend_id)`. Rewrites that order only by date silently change results when a meter vends twice in a day.
- **Frames.** A trailing 7-*day* sum is not a 7-*row* sum when a feeder has days with no vends. `ROWS` and `RANGE` frames differ exactly there.
- **Indexes cost something.** An index that helps a read slows every insert. You may add at most three, and you must argue they are worth it.
- **Measurement.** Wall-clock timings on a student laptop are noise. The tests count SQLite virtual-machine steps via a progress handler, which is deterministic. You must learn what that number does and does not capture.

**The five reports** (exact columns and ordering are in each stub's header):

| Query | Report |
|---|---|
| s1 | Latest vend per meter (meters that never vended are absent) |
| s2 | Running kWh per meter, in vend order |
| s3 | Days since the same meter's previous vend (NULL for the first) |
| s4 | Top 3 vends per feeder by amount, ties to the lower `vend_id`, with rank |
| s5 | Trailing 7-day revenue per feeder (the day and the 6 before it), one row for each date on which the feeder vended |

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Rewrite correlated subqueries as window-function queries and justify each frame and ordering choice.
2. Prove behavioural equivalence with the baseline, including on tie cases and on days with no activity.
3. Choose and defend at most three indexes, quantifying the read benefit and discussing the write cost.
4. Measure query cost deterministically, and explain what a VM-step count captures and what it misses (I/O, caching, sorting memory).
5. Run a scaling experiment and report the empirical growth of baseline versus rewritten work, with an honest statement of its limits.

---

## D. Technical Requirements

### D.1 Mandatory requirements

| ID | Requirement |
|---|---|
| **R1-R5** | `queries/s1.sql` ... `s5.sql`: one read-only statement each (`SELECT` or `WITH`), same columns, order and rows as the corresponding baseline `resources/baseline/b1.sql` ... `b5.sql`. |
| **R6** | `indexes.sql`: at most three `CREATE INDEX` statements and nothing else. The tests apply them to an in-memory copy before measuring. |
| **R7** | Work: each rewritten query uses at most **10%** of the corresponding baseline's work (VM steps, see §G). |
| **R8** | `scaling.py` (or notebook) that builds databases of at least three sizes with `resources/generate_vends.py` and reports steps for baseline and rewrite for each. |
| **R9** | `REPORT.md` covering the questions in the template. |

### D.2 Engineering requirements

- Your queries must be correct on **other data**: hidden tests use larger, re-seeded databases and compute the baseline live.
- Do not special-case the data (no literal dates, IDs or feeder numbers).
- Do not alter the database file; the tests open it read-only and apply your indexes to a copy.

### D.3 Privacy and responsibility

The data is synthetic and contains no customers. In real vend data a meter ID can identify a household and its consumption pattern. In two sentences in `REPORT.md`, say what you would aggregate or pseudonymise before sharing s2 or s3 outside the revenue-assurance team (NDPA 2023 data-minimisation).

### D.4 Optional enhancements

Compare a window-function design with a self-join design for s4 and s5 under the same step metric; try `WITHOUT ROWID` or a covering index and report the effect.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/vends.db`](resources/data/vends.db) (about 110 KB): `feeders(feeder_id, name, zone)`, `meters(meter_id, feeder_id, band)`, `vends(vend_id, meter_id, vended_on, kwh, amount_ngn)` |
| **Baselines** | [`resources/baseline/`](resources/baseline/) `b1.sql` ... `b5.sql` |
| **Generator** | [`resources/generate_vends.py`](resources/generate_vends.py): `python generate_vends.py --out DIR --seed N --meters M --vends V`; deterministic |
| **Provenance** | **Synthetic**; feeder names echo real network naming but no real data is used. Amounts follow typical vend denominations. |
| **Licence** | CC BY 4.0 (data), MIT (code) |
| **Integrity** | The contract test checks the database SHA-256 |

**Known limitations.** Vend dates are generated with bursts, so feeders have quiet days (deliberate). `vend_id` order is unrelated to date. Ten meters never vend. Real vends have timestamps and many more columns; there are no timezone issues here.

**How work is measured.** `tests/conftest.py` sets SQLite's progress handler to fire every 100 VM instructions and counts calls. This is a deterministic proxy for CPU work inside SQLite. It does not capture disk reads, page cache effects or the cost of building an index.

**Setup**
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract
pytest
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `queries/s1.sql` ... `s5.sql`, `indexes.sql` | The optimised, equivalent reports |
| 2 | `scaling.py` and its output table | Evidence about growth, not just a single measurement |
| 3 | `REPORT.md` from the [template](submission-template/REPORT.md) | Plan comparisons, trade-offs, limitations, scaling interpretation |
| 4 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 5 | A 5-minute live defence | Verifies you understand frames, plans and trade-offs |

---

## G. Acceptance Criteria

Criteria marked ⚙ are checked by the public and hidden test suites. Criteria marked ✍ are checked by an assessor.

1. ⚙ s1-s5 return rows identical to the baseline on the public database (columns, values, order).
2. ⚙ Each rewrite uses ≤ 10% of the baseline's steps on the public database. *Justification:* the reference reaches 0.5% (s1-s4) to 4.1% (s5), so 10% leaves room for correct but less tuned designs, while an un-indexed correlated rewrite stays near 100%.
3. ⚙ Hidden tests on two larger re-seeded databases: identical rows to the live baseline and ≤ 10% of its steps, using your `indexes.sql`.
4. ⚙ `indexes.sql` has at most three statements, all `CREATE INDEX`.
5. ✍ `REPORT.md` shows `EXPLAIN QUERY PLAN` before and after for at least two queries and explains the change (scan to search, temp B-tree, etc.).
6. ✍ The scaling table has at least three sizes spanning a factor of at least 4 and interprets growth (roughly quadratic for the baseline versus near-linear or n log n for the rewrite), and states one condition under which your rewrite would stop being fast.
7. ✍ `REPORT.md` states one concrete tie or empty-day case that breaks a plausible-but-wrong rewrite, with the rows that show it.

---

## H. Evaluation Rubric

The full rubric with performance levels is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 10 |
| Methodology and experimentation | 20 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates (passing defence, reproducible run, integrity declaration). See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. Create a **private** GitHub repository named `clbg-DS-T2-013-<your-github-username>` from this assessment's `starter/`, `tests/` and `resources/` folders and the `submission-template/` files.
2. Expected structure:
   ```text
   clbg-DS-T2-013-<username>/
   ├── queries/s1.sql ... s5.sql
   ├── indexes.sql
   ├── tests/            # provided tests
   ├── resources/        # unchanged (database, baseline queries, generator)
   ├── scaling.py        # your scaling experiment (script or notebook)
   ├── REPORT.md         # includes the AI-use declaration
   └── AI_USE_AND_SOURCES.md
   ```
3. Commit as you work. Your commit history is evidence of authorship (see §K); a single "final" commit will be questioned at defence.
4. Add the CLBG assessor account as a read-only collaborator and file a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core requirements.

1. Add a fifth index and show it makes no difference to the step count, then explain why.
2. Reproduce the comparison on DuckDB and discuss what changes (vectorised execution, no progress-handler analogue).
3. Use `ANALYZE` and show how statistics change a plan.

---

## K. Assessment Integrity

**AI tools are permitted** to explain concepts, suggest idioms or review your code. They may not do the assessment for you, and you must be able to explain and modify every line you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md` (template in `submission-template/`): tool, purpose and an example prompt. Undisclosed use discovered at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** adapted code and any papers or documentation you relied on, with links.
- **Collaboration:** discuss *general techniques* only. Do not share code, results or report text.
- **How understanding is verified.** At the defence the assessor will (1) ask you to explain one frame clause line by line and what would change with `ROWS` instead of `RANGE`; (2) pick one index and ask what it costs on insert; (3) set an unseen modification, for example "make s5 a 14-day window" or "break ties by amount in s1", to be implemented and re-measured live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Joins, aggregation, subqueries; first exposure to window functions. |
| **New skill developed** | Measuring and reasoning about query cost, and optimising without changing results. |
| **Decisions the member must make** | Window versus join design per query; the three indexes; frame type; how to build a fair scaling experiment. |
| **What must be investigated independently** | Why the baselines are slow (plans), what ties and empty days do, how step counts behave as data grows. |
| **Why it is interesting** | A realistic utility reporting problem; correctness traps hidden inside optimisation; a deterministic benchmark instead of folklore. |
| **Evidence of competence** | Hidden-data equivalence, work ratios, plan reading, and a scaling interpretation that admits limits. |
| **Misconceptions exposed** | "Window functions are always faster"; "more indexes are better"; "RANGE and ROWS are the same"; "timing it once is a benchmark". |
| **Preparation for later work** | Leads to DS-T3-011 (analytical model design) and DS-11 pipelines where query cost matters at scale. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
