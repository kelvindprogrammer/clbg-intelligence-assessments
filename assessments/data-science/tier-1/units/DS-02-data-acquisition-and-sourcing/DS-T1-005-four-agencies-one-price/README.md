# DS-T1-005: Four Agencies, One Price

> *JSON, XML, a multi-sheet workbook and a legacy fixed-width file all describe the same maize in the same markets. Make them agree, then find out where they genuinely don't, and why.*

![Format: Investigation](https://img.shields.io/badge/format-investigation-e36209) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-005` |
| **Title** | Four Agencies, One Price: Parsing and Reconciling Heterogeneous Food-Price Files |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-02: Data Acquisition and Sourcing](../README.md) |
| **Format** | Investigation (secondary: Implementation) |
| **Difficulty** | Technical 2 · Mathematical 1 · Research 1 · Engineering 2 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 10–16 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. Offline after `pip install` |
| **Recommended prerequisites** | Python dictionaries, loops and functions; pandas basics (`merge`, `groupby`); reading JSON; an idea of what XML elements and attributes are; running `pytest` |
| **Skills developed** | Parsing JSON, XML, Excel and fixed-width formats; unit and currency normalisation; temporal alignment with ISO weeks; reference tables and alias mapping; cross-source reconciliation; distinguishing parsing defects, source defects and real events |
| **Technologies** | Python 3.10+, pandas, openpyxl, `xml.etree.ElementTree`, `json`, pytest |

---

## B. Problem Statement

A food-security desk publishes a weekly staple-food price brief for ten Nigerian markets, from Dawanau in Kano to Mile One in Port Harcourt. No single agency covers every market, so the desk combines four sources. Each source arrives in its own format, with its own units, labels and idea of what "a week" is:

| Agency (fictional) | File | What makes it awkward |
|---|---|---|
| Northern Grain Monitor (NGM) | JSON | Prices in **kobo**. Weeks labelled by their **Saturday**. Its own market labels. |
| Coastal Markets Bureau (CMB) | XML | Prices per **mudu** (a measuring bowl whose weight depends on the grain). `DD/MM/YYYY` dates. Thousands separators. **Corrections are appended** as new revisions. |
| AgriPrice Cooperative (APC) | Excel, one sheet per month | Prices per **bag**, with the bag size stated in a cell on each sheet. Title rows above the header. `n.a.` and blank cells. |
| Legacy Statistical Archive (LSA) | Fixed-width text | **Implied decimal places**. Missing values encoded as **zeros with a flag**. ISO week labels. A trailer record count. |

The desk's previous analyst merged them with a spreadsheet and a lot of copy-and-paste. The brief once reported that maize in one market had "halved in a month". It hadn't. The brief has never been trusted since.

Your job has two halves:

1. **Engineering (precise):** implement `pricerecon`, a package that parses all four files into **one canonical table** (naira per kilogram, one Monday-dated week key, canonical market and commodity IDs), with every rule pinned by a test.
2. **Investigation (the point):** once the formats agree, look at where the *sources* still disagree. You will find a small number of genuine anomalies. For each one, decide whether it is **a parsing error** (yours), **a defect in an agency's data**, or **a real market event**, and support the decision with evidence. Only the first is something you fix in code. The second you report and flag. The third you must *not* "correct".

**Known facts from the desk** (the only documentation you get, besides [`resources/agency_formats.md`](resources/agency_formats.md)):

- Agencies survey different traders, so they will never agree exactly. In the desk's experience they agree **within about 5 %** in a normal week.
- The desk's kilogram equivalents for the mudu and the bag are in `reference/units.csv`, and they are the agreed standard.
- The agencies' own documentation is "mostly right". Where a file contradicts its documentation, believe the file and say so in your report.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Parse** four structurally different formats correctly, including nested JSON, attribute-heavy XML, a multi-sheet workbook with a title block, and a fixed-width layout with implied decimals.
2. **Normalise** currency sub-units, physical units and time keys to one canonical representation, using reference tables rather than hard-coded constants.
3. **Represent missingness explicitly**, telling "observed as missing" apart from "absent", and never turning a missing value into zero.
4. **Handle revisions and integrity checks** (corrections, trailer counts) so that the current figure wins and truncated files are rejected.
5. **Reconcile** sources with a robust cross-source rule, and detect stale (copied-forward) values.
6. **Investigate** each remaining anomaly and classify it as a parsing error, a source defect or a real event, with evidence.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement [`starter/pricerecon/`](starter/pricerecon/). The signatures are fixed because the tests import them. The output schemas are in [`resources/output_schema.md`](resources/output_schema.md).

| ID | Requirement |
|---|---|
| **R1** | `load_reference(ref_dir) -> Reference` builds lookup tables from `markets.csv` (the `market_id`, the `name` and every `|`-separated alias), `commodities.csv` and `units.csv`. `Reference.market(label)`, `.commodity(label)` and `.kg(commodity_id, unit)` look labels up **ignoring case, leading and trailing whitespace and repeated internal whitespace** (`norm_label`), and raise `UnmappedLabel` for anything unknown. Never guess a mapping. An alias that maps to two different IDs is an error at load time. |
| **R2** | `week_start(date) -> date` returns the Monday of that date's ISO week. `iso_week_monday("2025W02") -> date(2025, 1, 6)`. Anything else raises `ValueError`. Every canonical `week_start` is this Monday as a `YYYY-MM-DD` string. |
| **R3** | `parse_ngm(path, ref)`: kobo become naira, divided by the item's unit weight. `null` prices become rows with `flag="missing"` and `NaN` price. The Saturday labels map to their Monday. |
| **R4** | `parse_cmb(path, ref)`: parse `DD/MM/YYYY` dates and prices with thousands separators, and convert per-`uom` prices to per-kg prices using `units.csv`. For each market, item and week keep **only the highest `revision`**, wherever it appears in the file. Two observations with the same key and the same revision are an error. |
| **R5** | `parse_apc(path, ref)`: read **every** month sheet. A sheet is a data sheet if and only if cell `A3` matches `Unit: NGN per <unit>`, so skip the others (e.g. `Notes`). The header is on row 5. Convert using **that sheet's** unit. Blank or `n.a.` cells become `missing` rows. Any other non-numeric cell raises `ValueError`. |
| **R6** | `parse_lsa(path, ref)`: apply the layout in `agency_formats.md` by **column position**. The price has two implied decimals. `M` gives `missing` (`NaN`, never 0), `E` gives `estimated`, and blank gives `ok`. Lines whose trailing spaces were stripped must still parse. A missing trailer, or a trailer count that doesn't match the number of records, raises `ValueError`. |
| **R7** | `load_all(data_dir, ref)` returns all four sources in one canonical table, with no duplicate `(source, market_id, commodity_id, week_start)`, sorted as the schema states. |
| **R8** | `reconcile(df)` returns one row per key with `n_sources`, `median_price`, `min_price`, `max_price` and `spread_ratio`. `discrepancies(df, tol=0.15, min_sources=3)` returns each observation whose relative deviation from the **median of all valid prices for its key** exceeds `tol`, considering only keys with at least `min_sources` valid prices. |
| **R9** | `stale_runs(df, min_run=4)` returns every maximal run of at least `min_run` consecutive valid observations, in one source's market-commodity series, whose prices are identical to 2 decimal places. |
| **R10** | CLI: `python -m pricerecon resources/data --reference resources/reference --out outputs/` writes `canonical.csv`, `reconciled.csv`, `discrepancies.csv` and `stale_runs.csv`. |

**Why these rules?** The median of all sources (R8) is robust to one bad source when there are three or more: the two good sources hold the median in place. Leave-one-out comparisons, by contrast, let one bad value drag the reference and flag innocent sources. The 15 % tolerance is three times the desk's "about 5 %" normal disagreement, so ordinary sampling differences don't trigger it, while unit errors (×2, ×1.4) and swapped commodities (×2) always do. The four-week stale threshold (R9) is used because two or three equal weeks can happen by chance with rounded bag prices, and four almost never do.

### D.2 Engineering requirements (mandatory)

- **No hard-coded markets, months, sheets or rows.** Every rule must come from the reference tables, the file's own metadata (such as the unit cell) or the documented layout. The hidden tests use regenerated files with the defects moved elsewhere.
- **Raw files are read-only.** The contract tests check their SHA-256.
- **Tests.** Keep the provided tests passing and add **at least 12 tests** in `tests/test_member_*.py`. At least one per parser must come from something you discovered by *opening the file*, not from this README.
- **Profiling is reproducible.** The counts in your report come from a script or notebook in your repository.

### D.3 Data ethics

The data is **synthetic**, and the agencies are fictional. The market names are real public places, used only as labels, and the prices are not real observations. Don't present any figure from this assessment as an actual market price. Your report must keep the three anomaly classes separate. In real food-security work, "correcting" a genuine price spike can hide a crisis from the people who need to respond to it.

### D.4 Optional enhancements (not required for full marks)

- A `--explain MARKET COMMODITY WEEK` flag showing each source's raw value, unit, conversion and final per-kg price.
- Validate the canonical table with a schema library (e.g. `pandera`) and justify the choice.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed. Four fictional agencies; ten real market names used as labels; 26 weeks (6 January to 30 June 2025); five staples. The generator is kept in the assessor kit because it would reveal the planted anomalies. |
| **Licence** | CC BY 4.0 (this repository's content licence) |
| **Files** | [`resources/data/`](resources/data/): `ngm_prices.json` (73 KB), `cmb_bulletin.xml` (84 KB), `apc_survey.xlsx` (18 KB), `lsa_extract.txt` (39 KB) |
| **Reference tables** | [`resources/reference/`](resources/reference/): `markets.csv`, `commodities.csv`, `units.csv` |
| **Format notes** | [`resources/agency_formats.md`](resources/agency_formats.md) |
| **Integrity** | The SHA-256 of every file is in `tests/test_contract.py` |

**Canonical table schema** (full detail in [`output_schema.md`](resources/output_schema.md)): `source, market_id, commodity_id, week_start, price_ngn_per_kg, flag`.

**Known limitations (by design).** You do not have the "true" prices, only four noisy views of them. Some anomalies cannot be *explained* from the files alone. In those cases the best answer states what the evidence shows and what it doesn't.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-02-data-acquisition-and-sourcing/DS-T1-005-four-agencies-one-price
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract       # passes immediately
pytest                   # the requirement tests fail until you implement pricerecon
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `pricerecon/` package | The parsing and reconciliation logic: the technical evidence |
| 2 | `tests/test_member_*.py` (at least 12 tests) | Pins every format rule, including the ones you discovered yourself |
| 3 | `profiling.py` or `profiling.ipynb` | Reproduces every count in the report |
| 4 | `outputs/` (the four CLI files) | What the desk would publish from |
| 5 | `RECONCILIATION_REPORT.md` (at most 1,500 words plus tables), using the [template](submission-template/RECONCILIATION_REPORT.md) | Documents each format trap, and each anomaly with its classification and evidence |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 7 | A 5–10 minute defence | Verifies understanding (§K) |

---

## G. Acceptance Criteria

1. ⚙ All provided tests and at least 12 member tests pass from a clean environment.
2. ⚙ **Exact parsing:** on regenerated files, every canonical row matches the ground truth: the same set of keys, the same flags, and prices within ₦0.011/kg (the 2-decimal rounding of the conversion).
3. ⚙ **No invented values:** every missing observation is `NaN` with `flag="missing"`. No `0` prices.
4. ⚙ **Integrity:** revisions are resolved regardless of their order in the file, a tampered or truncated LSA trailer raises, and an unknown label raises `UnmappedLabel`.
5. ⚙ **Reconciliation:** on regenerated files, `discrepancies()` flags only the planted source defect, and `stale_runs()` finds exactly the frozen series. A real market shock that every agency reports is **not** flagged.
6. ⚙ On the official files, at most 1 % of valid observations are discrepant. *Justification:* with correct parsing, the reference implementation flags 5 of 4,063 (0.12 %). A single unit-conversion mistake (for example, assuming every APC sheet uses 100 kg bags) produces about 200 flags, so 1 % separates correct parsing from a format error with a wide margin on either side.
7. ✍ The report lists every format trap you found, with the rule and test that handles each.
8. ✍ Every anomaly is classified as a parsing error, a source defect or a real event, with quantitative evidence such as the ratio to the other agencies, whether every agency shows it, and the time pattern. You also state what you would ask the agency to confirm.
9. ✍ The report includes the `spread_ratio` distribution after correct parsing and relates it to the desk's "about 5 %" claim.

---

## H. Evaluation Rubric

The full rubric is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 15 |
| Methodology: investigation and evidence | 20 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates (defence, reproducibility, integrity). See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. Create a **private** repository named `clbg-DS-T1-005-<your-github-username>` containing the starter package, `tests/`, `resources/` (unchanged) and `submission-template/`.
2. **Expected structure:**
   ```text
   clbg-DS-T1-005-<username>/
   ├── README.md                     # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── pricerecon/
   ├── tests/
   ├── resources/                    # unchanged
   ├── profiling.py | profiling.ipynb
   ├── outputs/{canonical,reconciled,discrepancies,stale_runs}.csv
   ├── RECONCILIATION_REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** The history should show the parsers evolving as you discovered each format's traps.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue with the repository URL and commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Agency bias.** Estimate each agency's systematic bias relative to the cross-source median, with a bootstrap confidence interval. Is any agency consistently high or low?
2. **Best estimate.** Build a weighted weekly price per market and commodity that down-weights estimated and stale values, and justify the weights.
3. **Data contract.** Write a short contract that each agency's next delivery must satisfy, and implement it as a validator that rejects the files' current defects with clear messages.
4. **A fifth source.** Design how a new agency's CSV would plug in without changing the other parsers.

---

## K. Assessment Integrity

**AI tools are permitted** for learning, for example to explain `ElementTree`, openpyxl or fixed-width parsing, or to review your code. **They must not write the assessment for you.** You must be able to explain and change every line.

- **Disclose** AI use in `AI_USE_AND_SOURCES.md` (tool, purpose, example prompt). Disclosed, reasonable use is not penalised. Undisclosed use discovered at defence is an integrity breach.
- **Cite** any adapted code.
- **Collaboration:** you may discuss general techniques. You may not share code, anomaly findings or report text. The anomalies are the assessment.
- **How understanding is verified.** At defence the assessor will:
  1. choose one canonical row and ask you to show the raw value in the original file, and every transformation, live;
  2. ask you to defend your classification of one anomaly: "what evidence would change your mind?";
  3. give an **unseen modification** to implement live, with a test. For example: a new LSA flag `R` (revised), a CMB `uom="derica"` with a new conversion row, or an APC sheet whose header starts on row 6.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Basic Python and pandas, plus elementary knowledge of JSON, XML and spreadsheets. |
| **New skill developed** | Getting *heterogeneous* sources onto a single, defensible footing (units, time keys, identifiers, missingness, revisions), and then separating parsing errors from source defects and real events. |
| **Decisions the member must make** | What counts as the same label. Which week key reconciles Saturday, Monday and ISO labels. What to do with corrections. How to read a unit that changes by sheet. When disagreement is noise and when it is evidence. |
| **What must be investigated independently** | Whether the files match their documentation, and what each surviving anomaly is. Nobody lists them for you. |
| **Why it's interesting** | The traps are mundane but realistic (kobo, mudu, bag sizes, appended corrections, zero-as-missing), and the anomalies need judgement: one must be fixed, one must be reported, and one must be *left alone*. |
| **Evidence of competence** | Exact agreement with hidden ground truth on regenerated files; a correct three-way classification with evidence; live tracing of a value from raw file to canonical row. |
| **Misconceptions exposed** | "One unit per file." "First value wins." "Zero means cheap." "An outlier is an error." "If it parses, it's right." |
| **Preparation for later work** | It leads to DS-T2-004 (fusing real sources at mismatched granularity), DS-03 data-quality work and DS-11 pipelines with data contracts. |

**Suggested approach** (optional): open every file by hand first. Read the JSON in an editor, the XML in a browser, the workbook in a spreadsheet program, and the fixed-width file with a column ruler. Write one parser at a time with its tests. Compare each source to LSA, which covers every market, as a sanity check. Investigate anomalies last, starting from `reconciled.csv` sorted by `spread_ratio`.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
