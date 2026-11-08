# DS-T1-001: The Price Watch Bulletin

> *A statistics office publishes food prices as a spreadsheet built for printing, not for analysis. Turn it into tidy data, then use the tidy data to find out how the headline averages were really computed, and where they are wrong.*

![Format: Implementation](https://img.shields.io/badge/format-implementation-0366d6) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-001` |
| **Title** | The Price Watch Bulletin: From Spreadsheet Export to Tidy Data |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-01: Python and Data Wrangling](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 1 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 8–14 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Python basics: functions, lists, dictionaries, `for` loops, string methods, and raising exceptions. You have opened a CSV in pandas and selected columns. You can run `pytest`. **No previous CLBG assessment is needed: this is the entry point for the Data Science subtrack.** |
| **Skills developed** | Reading irregular files; string parsing and validation; the tidy-data model; `melt`, `merge`, `groupby` and `concat`; explicit missing values; calendar-aware time arithmetic; reconciling published aggregates; unit testing of data code |
| **Technologies** | Python 3.10+, pandas, NumPy, pytest |

---

## B. Problem Statement

Every month, a (fictional) national statistics office publishes the **State Food Price Watch**: the average retail price of staple foods in each of Nigeria's 36 states and the FCT. Journalists quote it, NGOs use it to target food assistance, and commodity traders watch it. It is published as a spreadsheet that was designed to be **printed and read by a person**, so it looks nothing like the table an analyst needs.

You have been given [`price_watch_bulletin.csv`](resources/data/price_watch_bulletin.csv), the CSV export of the January 2024 to June 2025 bulletin. Open it in a text editor before you do anything else. You will see:

- **Several tables stacked on top of each other**, one per food item, each with its own title line and unit line.
- **A two-row header with merged cells.** The year is printed once, above the first month of that year, and the cells to its right are blank.
- **A vertically merged Zone column.** The geopolitical zone is printed only on the first state of each zone.
- **Summary rows mixed in with the data:** a zone average after each zone's states, and a national average at the end of each table.
- **Tables that break across pages.** A table can stop half-way, then continue as "Table N (continued)" with its header repeated.
- **Footnote notation inside the numbers:** `*` for a revised figure, `p` for provisional, `-` for not collected and `..` for not available.
- **Presentation formatting:** thousands separators (in most tables, but not all), stray spaces, state names with footnote markers, and more than one way of writing the FCT.

The task has two halves.

**First, build a reliable reshaping pipeline.** The analyst's table is *tidy*: one row per item, state and month, one column per variable, and missing values kept as explicit rows with a reason, not silently dropped. You will build it as a small, tested Python package with fixed function signatures.

**Second, use the tidy table to check the bulletin against itself.** The office has never written down how its averages are computed. Once your data is tidy, you can recompute every published average and test hypotheses: is a zone average the mean of its states? Is the national average the mean of all 37 states, or the mean of the six zone averages? These are **not** the same number, because the zones contain different numbers of states. And do all the printed averages agree with the printed state figures? (Not all of them do. Finding out which ones, and proposing why, is part of the assessment.)

**Why this matters.** Most real data does not arrive tidy. Statistical bulletins, bank statements, school result sheets and procurement reports are all formatted for people. The analyst who can turn them into correct, tested, tidy tables quickly is worth a great deal, and the analyst who does it *wrongly* is dangerous: a mis-aligned header shifts every price by one month, and a dropped "not collected" row silently changes an average. This assessment is the foundation for the whole Data Science subtrack. Almost every later assessment assumes you can do what this one asks.

**What makes it hard.** No single line is difficult, but the pieces only work if each one is exactly right, and an error in an early step quietly corrupts everything after it. The pandas function you reach for first (`read_csv` with default settings) will misread this file. Averages that look plausible can be wrong, and the only way to know is to test.

**Known facts from the statistics office** (the only documentation you get):

- Prices are in Naira and are printed with two decimal places.
- A figure marked `*` replaces the figure printed in an earlier bulletin. A figure marked `p` is provisional and may change next month.
- `-` means the price was not collected (no enumerator visit). `..` means it was collected but cannot be published (for example, too few market quotes).
- "Zone average" and "National average" rows are computed by the office, and are rounded to two decimal places.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Read an irregular file faithfully,** treating every cell as text until you have decided what it means, so that nothing is lost or misinterpreted on load.
2. **Write small, validated parsing functions** that accept every legitimate format in the data and *reject* everything else with a clear error.
3. **Reshape wide, multi-header tables into a tidy long table** with a fixed schema, explicit missing values and a defined sort order.
4. **Use `groupby`, `merge` and calendar-aware period arithmetic correctly,** including the common traps: averaging over missing values, comparing a month with the wrong "previous" month, and joins that silently duplicate or lose rows.
5. **Reconcile published aggregates with their inputs,** and so test a hypothesis about how a figure was computed.
6. **Pin your behaviour down with unit tests,** including edge cases you found by reading the data.
7. **Explain what you found** in plain language for a non-technical reader.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

You must implement the `price_watch` package in [`starter/price_watch/`](starter/price_watch/). Function names, parameters, return types and column names are **fixed** because the tests import them. The internals are entirely yours. [`schema.py`](starter/price_watch/schema.py) is provided and must not change. It holds the output column lists, the 37 states and their zones, the `RawTable` type and the `load_raw()` loader.

| ID | Requirement |
|---|---|
| **R1** | `parse_price(cell) -> (float, str)` returns the value and a status: `"ok"`, `"revised"` (`*` suffix), `"provisional"` (`p` suffix), `"not_collected"` (`-`) or `"not_available"` (`..`). Missing cells return `nan`. It ignores surrounding whitespace and accepts values with or without correctly placed thousands separators. **Anything else raises `ValueError`**, including an empty cell, a misplaced separator (`1,23.4`) or a negative number. |
| **R2** | `parse_periods(year_cells, month_cells) -> list[str \| None]` turns a table's two header rows into one `"YYYY-MM"` label per price column, and `None` for every other column. It must handle merged year cells and month labels in abbreviated (`Sep`), four-letter (`Sept`) or full (`September`) form, in any letter case. An unknown month label, or a month before any year, raises `ValueError`. |
| **R3** | `classify_label(label) -> (kind, name)` classifies a body row as `("state", <canonical name>)`, `("zone_average", <zone>)` or `("national_average", "National")`. It must strip footnote markers such as `(a)` or `(b)`, map the different ways of writing the FCT (for example `FCT, Abuja` or `Abuja`) to `FCT`, and raise `ValueError` for any label it cannot classify with certainty. A misspelt state is an error, not a guess. |
| **R4** | `parse_unit(unit) -> (quantity, base_unit)` with `base_unit` in `kg`, `litre` or `piece`. It converts grams to kg and millilitres or centilitres to litres, and reads `crate of N` as N pieces. Trailing words such as `bag`, `tin` or `bottle` are ignored. Anything else raises `ValueError`. |
| **R5** | `split_tables(raw) -> list[RawTable]` finds every table in the grid returned by `load_raw()`. It returns one `RawTable` per table **number**, in bulletin order, with continuations merged in. Its `body` has the columns `["label", "zone"] + periods` and holds every state and average row, in printed order, with the cell text untouched. A continuation whose header differs from the original table's raises `ValueError`. |
| **R6** | `tidy_bulletin(raw) -> DataFrame` with exactly the columns in `TIDY_COLUMNS`: one row per item, state and period, for **every** state cell, missing ones included. Average rows are excluded. `zone` comes from `STATE_ZONES`, not from the printed column. `price`, `unit_qty` and `price_per_base` are `float64`, and `price_per_base = price / unit_qty`. Rows are sorted by `item`, `state` and `period`, and the index is `0..n-1`. |
| **R7** | `published_averages(raw) -> DataFrame` with the columns in `PUBLISHED_COLUMNS`: one row per printed average, with `area` set to the zone name or `"National"`. Rows are sorted by `item`, `area` and `period`. |
| **R8** | `reconcile_averages(tidy, published) -> DataFrame` with the columns in `RECONCILE_COLUMNS`. It recomputes, for every published row, `state_mean` (the mean of the *reported* state prices in that area) and, for national rows only, `mean_of_zone_means`. It sets `match` to `"state_mean"`, `"mean_of_zone_means"`, `"both"` or `"neither"`, depending on which recomputed value lies within `TOLERANCE` (₦0.01) of the published figure. There is one output row per input row, sorted like R7. |
| **R9** | `month_on_month(tidy) -> DataFrame` returns a **copy** of `tidy` with one extra column, `mom_pct = 100 × (price / previous − 1)`. "Previous" means the same item and state in the **immediately preceding calendar month**. The value is `NaN` when either price is missing or the previous month is absent. It never compares with "the previous row". |
| **R10** | Run as `python -m price_watch <bulletin.csv> --out <dir>`, the package writes `tidy_prices.csv` (the R9 output), `published_averages.csv` and `reconciliation.csv`. This CLI is provided in [`__main__.py`](starter/price_watch/__main__.py) and works once R1–R9 do. |
| **R11** | `ANALYSIS.md` (at most 1,000 words plus tables, using the [template](submission-template/ANALYSIS.md)) answers the four questions in the template, using numbers your code regenerates. |

### D.2 Engineering requirements (mandatory)

- **The raw file is read-only.** Never edit the CSV, by hand or in code. The contract test checks its checksum.
- **No silent loss.** Your tidy table must contain exactly 37 rows per item and period that the bulletin prints. If your code would drop or duplicate a row, it must raise an error instead. Use `merge(..., validate=...)` or explicit checks.
- **Fail loudly.** Every parser raises `ValueError` on input it does not recognise. Never return a default value just to keep going.
- **No hard-coding of the layout.** Do not hard-code row numbers, table counts, item names or which tables break across pages. The hidden tests regenerate the bulletin with a different layout.
- **Tests.** Keep the provided tests passing, and add **at least 10 tests of your own** in `tests/test_member_*.py`. At least three must be edge cases you found by reading the file.
- **Dependencies.** Use only the packages in [`starter/requirements.txt`](starter/requirements.txt).
- **Determinism.** Two runs of the CLI produce byte-identical outputs.

### D.3 Privacy and responsibility

The bulletin is **entirely synthetic**. It contains no personal data, and the prices are simulated: do not quote them as real statistics. Real price bulletins often feed decisions about who receives food assistance, so in `ANALYSIS.md`, say in two or three sentences what could go wrong if someone used the published national average, rather than your recomputed figures, to compare states or zones.

### D.4 Optional enhancements (not required for full marks)

- A `--check` CLI flag that exits with a non-zero status when the reconciliation finds any `"neither"` rows, so the pipeline could guard a publication process.
- A line chart of one item's price per kg by zone, with provisional months marked.
- A short note on how you would read the same bulletin if it arrived as `.xlsx` with real merged cells (for example, with `openpyxl`), and what would change.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/price_watch_bulletin.csv`](resources/data/price_watch_bulletin.csv): 319 lines × 20 columns, about 50 KB, UTF-8 |
| **Provenance** | **Synthetic.** It was generated by CLBG with a fixed seed from a simple price simulation (item base price × zone effect × state effect × monthly inflation × noise), then laid out like a printed bulletin. It is not official data. |
| **Licence** | CC BY 4.0, the same as this repository's content |
| **Integrity** | SHA-256 `da5170648d618e8d8f45bb1c1182add1115be821ab37d2e334a69afdcca0ce38`. The contract test checks it. |
| **Reference data** | `STATE_ZONES` and `ZONES` in [`schema.py`](starter/price_watch/schema.py): the 36 states plus FCT, mapped to the six geopolitical zones |
| **Generator** | Kept in the assessor kit, because it writes the answer key. The hidden tests use it to create new bulletins with different seeds. |

**Output schema** (`TIDY_COLUMNS`):

| Column | Type | Meaning |
|---|---|---|
| `item` | str | Item name exactly as printed in the table title, e.g. `Palm oil` |
| `unit` | str | Unit text exactly as printed after `Unit: `, e.g. `50 kg bag` |
| `state` | str | Canonical state name (a key of `STATE_ZONES`) |
| `zone` | str | Zone from `STATE_ZONES` |
| `period` | str | `YYYY-MM` |
| `price` | float64 | Printed price in Naira, `NaN` if missing |
| `status` | str | `ok`, `revised`, `provisional`, `not_collected` or `not_available` |
| `unit_qty`, `unit_base` | float64, str | From `parse_unit(unit)` |
| `price_per_base` | float64 | `price / unit_qty`, for example Naira per kg |

**Known limitations (by design).** You can see that some published averages disagree with the state figures, but nothing in the bulletin tells you the "right" earlier figure. Say what you can infer and what you cannot. The last two months of every table are provisional, so treat conclusions about them with care.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-01-python-and-data-wrangling/DS-T1-001-the-price-watch-bulletin
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract      # passes immediately: checks the data and the scaffold
pytest                  # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `price_watch/` package (the completed starter) | The reshaping logic: the core technical evidence |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Shows you can pin behaviour down and think about edge cases |
| 3 | `outputs/tidy_prices.csv`, `outputs/published_averages.csv`, `outputs/reconciliation.csv` | The artefacts an analyst would actually use, produced by the CLI |
| 4 | `ANALYSIS.md`, from the [template](submission-template/ANALYSIS.md) | Shows you can use tidy data to answer a real question, and explain it |
| 5 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 6 | A 5–10 minute live defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Assessors check the ⚙ criteria automatically with the public and hidden test suites, and the ✍ criteria by hand.

1. ⚙ `pytest` passes all provided tests and all your own tests in a clean environment created from `starter/requirements.txt`.
2. ⚙ `python -m price_watch resources/data/price_watch_bulletin.csv --out outputs/` finishes in **under 30 seconds** and writes the three files. *Justification:* the file is 50 KB. A straightforward pandas solution runs in about one second, so 30 seconds allows for slow laptops while still catching accidental quadratic behaviour.
3. ⚙ **Exact tidy table.** On the official bulletin **and** on freshly generated bulletins with different layouts, **every** row of your tidy table matches the hidden answer key: the same keys, statuses and zones, and prices within 1e-9. *Justification:* the format is fully specified and has no ambiguity, so any mismatch is a bug, and a single mis-aligned column shifts hundreds of prices. Partial credit for "mostly right" would reward exactly the error this assessment exists to prevent.
4. ⚙ **Exact published averages.** Every printed average is extracted with the correct item, area and period.
5. ⚙ **Reconciliation.** On every generated bulletin, the zone rows marked `"neither"` are **exactly** the zone averages that are inconsistent with the printed state figures, and every other national row matches `"mean_of_zone_means"` (or `"both"`). *Justification:* ₦0.01 is the largest gap that rounding to two decimal places, applied at most twice, can create. Any larger gap is a real inconsistency.
6. ⚙ **Month-on-month.** `mom_pct` equals the calendar-month definition (to within 1e-9) on every row, including across gaps and table boundaries.
7. ⚙ **Fail loudly.** The parsers raise `ValueError` on the hidden set of malformed cells, units, months and labels.
8. ⚙ **No mutation.** `tidy_bulletin` and `published_averages` leave their input unchanged.
9. ✍ `ANALYSIS.md` answers all four questions with numbers your code regenerates. It states correctly how the national average is built, and gives a reasoned (not certain) explanation of the inconsistent averages.
10. ✍ At least three member tests come from edge cases visible in the real file, and each test's name or docstring says which one.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 15 |
| Methodology: read, parse, reshape, verify | 10 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible pipeline and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own repository.** Copy this assessment's `starter/` contents, `tests/`, `resources/` and `submission-template/` into a new **private** GitHub repository named `clbg-DS-T1-001-<your-github-username>`.
2. **Expected structure:**
   ```text
   clbg-DS-T1-001-<username>/
   ├── README.md                  # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── price_watch/               # your package (from starter/)
   ├── tests/                     # provided tests + your test_member_*.py
   ├── resources/                 # unchanged
   ├── outputs/tidy_prices.csv
   ├── outputs/published_averages.csv
   ├── outputs/reconciliation.csv
   ├── ANALYSIS.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** Your history is part of the evidence. A sensible history has a commit per requirement or per bug found. A single final commit will be questioned at defence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator, then filing a submission issue in the CLBG assessments repository with the **Assessment submission** template. Include the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback, but they never replace the core requirements.

1. **Weighting matters.** The national average is a mean of zone means. Compute a population-weighted national average instead (use any public population estimate, and cite it). Show for which items and months the ranking of zones changes.
2. **Revision tracking.** Suppose next month's bulletin arrives. Design a function that takes two tidy tables and reports every revised figure, including the size of the revision and whether it changes a published average.
3. **Round-trip.** Write `render_bulletin(tidy, published) -> list[list[str]]` that rebuilds the printed layout from your tidy table. Show that `tidy_bulletin(render(...))` returns the same table. This "round-trip" test is a powerful way to check a parser.
4. **Profile the parser.** Time each step on a bulletin 100 times larger (generate it by repeating tables) and find where the time goes.

---

## K. Assessment Integrity

**AI tools are permitted for learning:** to explain what `melt` does, to suggest how to test for a `ValueError`, or to review your code. **They must not write the package for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`: which tool, what for, and an example prompt. Undisclosed use that becomes apparent at the defence is treated as an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** any code you adapted from documentation, Stack Overflow or other sources, with a link.
- **Collaboration:** you may discuss *general techniques* with other members (for example, "how do you forward-fill a header row?"). You may not share code, tests, outputs or analysis text.
- **How your understanding is verified.** In the 5–10 minute defence, the assessor will:
  1. point at one cell in the raw CSV and ask you to trace it to its row in `tidy_prices.csv`, naming the function that handled each step;
  2. ask you to explain, without notes, why the mean of zone means differs from the mean of states, and which way the difference goes for this bulletin;
  3. give you a small **unseen change** to the format, such as a new status marker, a new month spelling, or a new unit, and ask you to handle it live, with a test, while you explain your reasoning.

  Your commit history and tests are also checked for consistency with what you say.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python basics (functions, strings, lists, dictionaries, exceptions), opening a CSV in pandas, and running `pytest`. Nothing more is assumed. |
| **New skill developed** | Treating a messy file as a format to be *specified, parsed and tested*, rather than "cleaned by eye", and then using tidy data to check published numbers. |
| **Decisions the member must make** | How to read the file without losing information. How to detect table boundaries and continuations without hard-coding them. What counts as a valid price cell. How to represent missing values. How to define "previous month". How to compute averages over missing values. |
| **What must be investigated independently** | The full set of layout quirks. The README lists their kinds, not every instance. And which hypothesis explains the published averages, and why a few averages fit neither. |
| **Why it's interesting** | The file looks trivial and is not. The analysis half has a real answer that is not given: the national average is a mean of means (and so leans towards the zones with fewer states), and a handful of averages were never updated after a revision. |
| **Evidence of competence** | Exact agreement with a hidden answer key on bulletins the member has never seen; parsers that reject bad input; a reconciliation that finds exactly the inconsistent cells; live tracing and modification at the defence. |
| **Misconceptions exposed** | "`read_csv` with defaults is fine." "Missing rows can be dropped." "The previous row is the previous month." "An average of averages is an average." "If it parses, it's right." |
| **Preparation for later work** | Every later Data Science assessment assumes tidy data and tested wrangling code: data cleaning (DS-03), exploratory analysis (DS-04) and pipelines (DS-11). The reconciliation habit (recompute what you are given before you trust it) carries straight into forensic work. |

**Suggested approach**, for members who want it (you may ignore it):

1. Spend your first hour reading the raw file in a text editor and listing every quirk you see. Turn each one into a test before you write the code.
2. Build R1–R4 first. They are pure functions of one string, and easy to test.
3. Write `split_tables` next, and check it by printing each table's shape. Every table should have 44 body rows.
4. Only then `melt` and `merge`. Check row counts after every step.
5. For R8, compute both candidate averages by hand for one month in a spreadsheet before you write the code.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
