# DS-T1-027: Run It Twice

> *A pipeline that gives a different answer the second time you run it is not a pipeline, it is a gamble with other people's money.*

![Format: implementation](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-027` |
| **Title** | Run It Twice: An Idempotent, Auditable Loader for Daily Market-Levy Files |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-11: Analytical Pipelines and Data Engineering](../README.md) |
| **Format** | Implementation (secondary: Debugging and Forensics) |
| **Difficulty** | Technical 2 · Mathematical 1 · Research 1 · Engineering 3 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 8–14 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Python functions, files and the `csv` module; basic SQL (`CREATE TABLE`, `INSERT`, `SELECT`, primary keys); running `pytest`. |
| **Skills developed** | Idempotent loading; transactions and atomicity; row-level validation with reasons; quarantine tables; content-hash file tracking; reconciliation invariants |
| **Technologies** | Python 3.10+ standard library (`sqlite3`, `csv`, `hashlib`) and pytest. No third-party packages are needed. |

---

## B. Problem Statement

A local government revenue office collects daily market levies from stallholders. Twelve collectors record payments on handsets, and every evening a file arrives: `levies_<date>.csv` with one row per payment. The office loads these files into a database that produces the monthly revenue report.

Right now the loading is done by a clerk running a script by hand. Three things keep going wrong, and each has cost the office money or credibility:

- **Double loading.** When the evening upload is retried, or when the clerk clicks the script twice, payments are counted twice and revenue is overstated.
- **Half loading.** When the script crashes in the middle of a file (the laptop sleeps, the disk fills), some rows are in and some are not, and nobody knows which. Re-running it double-counts the first half.
- **Silent loss.** Rows with a bad amount or an unknown collector code are simply skipped. At month end the report is lower than the cash handed in, and no one can say why.

The files are untidy in ordinary ways: amounts like `12,500.00`, `N12,500` and `₦12500`; dates in ISO form or as `DD/MM/YYYY`; one file with its columns in a different order, one with upper-case headers, one with a byte-order mark and stray blank lines. Collectors resend yesterday's rows "to be safe", so the same payment arrives in several files, and occasionally the resend carries a **different amount**.

Your task is to build the loader the office should have had: a small, boring, trustworthy piece of data engineering. Its promises are simple to state and demanding to keep:

1. **Idempotent:** loading the same file again, even under a different name, changes nothing.
2. **Atomic:** a file is loaded completely or not at all, and a crash leaves the database as it was.
3. **Accountable:** every non-blank input row ends up in exactly one place (loaded, counted as a harmless duplicate, or quarantined with a reason), and the loader can prove it.
4. **Conservative:** a conflicting resend never silently overwrites the first value.

At Tier 1 the contract of every function is exact. The assessment checks that you can turn precise reliability requirements into correct code, and that you can test the unhappy paths, not only the happy one.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Parse messy amounts and dates with strict, documented rules and no silent guessing.
2. Design a three-table SQLite schema (data, quarantine, load log) that supports audit and replay.
3. Make a load idempotent by keying on file content rather than file name.
4. Use transactions so that failure leaves no partial state.
5. Classify every rejected row with a reason and keep it, instead of dropping it.
6. Write invariant checks and tests for failure paths.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Seven small requirements define the loader exactly. Implement the `levyload` package in [`starter/levyload/`](starter/levyload/). The function signatures are fixed because the automated tests import them. The internals are yours.

| ID | Requirement |
|---|---|
| **R1** | `parse_amount(text) -> int | None`: naira text to integer **kobo**. Accept an optional leading `N` or `₦`, thousands commas in groups of three, at most two decimals. Reject empty, negative, zero, letters, several dots, three or more decimals. |
| **R2** | `parse_date(text) -> str | None`: strict `YYYY-MM-DD` or `DD/MM/YYYY` real calendar dates to ISO; everything else `None`. |
| **R3** | `validate_row(row, collectors) -> (clean, None) | (None, reason)`, with checks in this order: required fields present (`missing_field`), amount (`bad_amount`), date (`bad_date`), collector known (`unknown_collector`). Whitespace is stripped. |
| **R4** | `read_drop(path) -> [(line_no, row_dict)]`: handle a BOM, header order and case, quoted commas and blank lines; `line_no` is the file line number with the header at line 1. |
| **R5** | `init_db(conn)`: create `levies(txn_id PRIMARY KEY, collector_id, paid_on, amount_kobo, source_file)`, `quarantine(source_file, line_no, reason, raw)` and `load_log(file_sha256 PRIMARY KEY, source_file, rows_in, rows_loaded, rows_rejected, rows_duplicate)`, idempotently. |
| **R6** | `load_file(conn, path, collectors, fail_after=None) -> LoadResult`: atomic and idempotent by SHA-256 of the file bytes; first value seen wins; identical resend counts as a duplicate; resend with a different amount is quarantined as `conflicting_duplicate`; on any exception roll back everything and re-raise (`fail_after=n` raises `RuntimeError` after `n` rows, for tests). |
| **R7** | `load_all(conn, folder, collectors)` loads `*.csv` in sorted filename order. `check_invariants(conn) -> list[str]` returns problems: for each logged file `rows_in == loaded + rejected + duplicate`, and the `levies` and `quarantine` tables contain exactly the logged counts for that file. |

### D.2 Engineering requirements (mandatory)

- **Standard library only.** `sqlite3`, `csv`, `hashlib`, `re`.
- **Read-only inputs.** The loader never modifies or moves the drop files.
- **Determinism.** No timestamps or random values in the tables; two clean loads of the same folder give identical databases.
- **Tests.** Keep the provided tests passing and add **at least 8 tests of your own** in `tests/test_member_*.py`, including edge cases you found yourself.
- **Dependencies.** Use only the packages in [`starter/requirements.txt`](starter/requirements.txt). If you add one, justify it in your report.

### D.3 Privacy and responsibility

The data is **synthetic**: collector codes and transaction IDs are fictional, and no stallholder is named. Real levy records identify traders and can be personal data under the Nigeria Data Protection Act 2023. In your report, add a paragraph on what you would do differently with real data: who may read the quarantine table (which keeps raw rows), how long it is retained, and why raw rows should not be pasted into tickets.

### D.4 Optional enhancements (not required for full marks)

- A `--dry-run` mode that reports what a load would do without writing.
- A command-line entry point `python -m levyload <folder> <db>` that prints a reconciliation summary.
- A short design note on how you would add a second source system with different columns.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/drops/`](resources/data/drops/): six daily files (`levies_2026-03-02.csv` to `levies_2026-03-07.csv`), about 200 rows each, about 66 KB in total; [`resources/data/collectors.csv`](resources/data/collectors.csv): 12 fictional collectors |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed. All identifiers are fictional. No real trader, market or local government is described. |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Integrity** | The contract test checks a SHA-256 over all six drop files, so do not edit them |

**Known limitations (by design).** The files are small so that they can be inspected by eye, but your design must not depend on that. There is no real clock, no concurrency and no schema evolution here; discuss them in your report as things the loader does not handle.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-11-analytical-pipelines-and-data-engineering/DS-T1-027-run-it-twice
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract        # should pass immediately: checks data and scaffold
pytest                    # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `levyload/` package (the completed starter) | The core technical evidence |
| 2 | `tests/test_member_*.py` | Shows you can pin behaviour down and think about edge cases |
| 3 | `outputs/load_summary.md` (per-file counts and the quarantine breakdown by reason, generated by a script) | The reconciliation a revenue officer would read |
| 4 | `load_demo.py` | Loads the six drops twice and shows the second run changing nothing |
| 5 | `REPORT.md` (from the [template](submission-template/REPORT.md)), with the AI-use declaration inside | Communicates decisions and limits; integrity declaration (see §K) |
| 6 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites, the rest by hand.

1. ⚙ Provided and member tests pass from a clean environment.
2. ⚙ Parsing rules accept and reject exactly the specified inputs, including three-decimal amounts and malformed thousands groups.
3. ⚙ Loading the six drops twice leaves the database identical, and a renamed copy of a file is skipped by content.
4. ⚙ A crash part-way through a file (`fail_after`) leaves all three tables unchanged, and a later full load equals a clean load.
5. ⚙ On freshly generated hidden drops, loaded, duplicate and per-reason quarantine counts, and the loaded total in kobo, **equal the ground truth exactly**. *Justification:* every rule is deterministic, so there is no tolerance to grant.
6. ⚙ `check_invariants` returns `[]` after a full load and reports a problem if rows are removed from `levies`.
7. ✍ The report explains how each of the four promises is kept and which test would fail if it were broken.
8. ✍ The report states one failure the loader still does not handle.

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

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-DS-T1-027-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` into it. Your package sits at the repository top level.
2. Commit as you work. Your commit history is part of the evidence (see §K); a single "final" commit will be questioned at defence.
3. Add your outputs and `REPORT.md`, then run `pytest` from a clean environment built from your `requirements.txt`.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository, using the **Assessment submission** template. Include the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never stand in for the core requirements.

1. **Concurrency.** Explain what happens if two loaders run at once on the same file, and make it safe with SQLite locking.
2. **Replay.** Add a function that re-validates the quarantine table after a rule change and loads the rows that now pass.
3. **Hash the rows, not the file.** Detect a re-exported file with different bytes but the same rows, and decide what the right behaviour is.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept, suggest an idiom or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: which tool, what for, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources, with a link.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers, thresholds or report text.
- **How your understanding is verified.** In the 5-minute defence the assessor will: 
  1. picks a quarantined row and asks you to trace how it got there and where you would look to find it again;
  2. asks what happens if the process is killed between inserting the last row and writing the `load_log` row, and why;
  3. gives you an unseen modification, for example a new reason code or a new date format, and asks you to change the code and tests live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python files and the csv module, basic SQL, pytest. No prior pipeline experience. |
| **New skill developed** | Thinking in guarantees: idempotency, atomicity and accountability, and turning each into a test. |
| **Decisions the member must make** | What to key idempotency on; what a duplicate is; what to do with conflicts; what to store in quarantine. |
| **What must be investigated independently** | The defects in the six files: formats, resends, conflicts, header variants, blank lines. |
| **Why it's interesting** | Revenue offices really do double count or lose rows; the fix is small, rigorous engineering, not a framework. |
| **Evidence of competence** | Exact counts against hidden ground truth, a crash-and-retry test, an idempotency test and a passing invariant check. |
| **Misconceptions exposed** | Re-running is harmless. Skipping bad rows is acceptable. File name identifies a file. A conflicting resend should overwrite. |
| **Preparation for later work** | Leads to DS-T2 incremental processing with late data and DS-T3 data contracts and drift gates. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
