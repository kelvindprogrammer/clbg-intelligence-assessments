# DS-T1-006: The Registry That Lies

> *Forensic cleaning of a student-records export: recover what can be recovered, flag what cannot, and prove which is which.*

![Format: Debugging & Forensics](https://img.shields.io/badge/format-debugging%20%26%20forensics-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-006` |
| **Title** | The Registry That Lies: Forensic Cleaning of a Student Records Export |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-03: Data Cleaning and Data Quality](../README.md) |
| **Format** | Debugging & Forensics (secondary: Implementation) |
| **Difficulty** | Technical 2 · Mathematical 1 · Research 1 · Engineering 2 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 10–16 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Python functions and modules; pandas `DataFrame` basics (selecting, filtering, `groupby`); regular expressions at the level of `re.sub` and `re.fullmatch`; running `pytest`. Helpful but optional: [DS-T1-001](../../DS-01-python-and-data-wrangling/README.md) |
| **Skills developed** | Data profiling; missing-value semantics; canonicalisation of categorical values; date and phone parsing; duplicate detection; defensive validation; data-quality reporting |
| **Technologies** | Python 3.10+, pandas, pytest. Optional: `rapidfuzz` for fuzzy matching |

---

## B. Problem Statement

A Nigerian university's Academic Records Office is moving to a new student information system. Before the migration, the old system was "exported" by three different offices over four years. Each office used its own habits for typing names, dates, phone numbers and state names. Some records were exported twice, and some students were re-entered by hand after a server failure. One department's export tool quietly wrote CGPAs on the wrong scale.

You have been given `registry_export.csv`: **1,245 rows describing roughly 1,150 real students**. Nobody can tell you exactly how many students there are, which rows are duplicates, or which values are wrong. That's what you are being asked to find out.

The new system will use this data to decide things that matter: who is eligible to graduate, who receives scholarship letters, and which phone number gets the SMS saying a student's result is withheld. Bad cleaning has real consequences:

- **Merging two different students** who happen to share a name (Nigeria has many students called Zainab Bello) can attach one student's academic record to another person.
- **Silently "fixing" an ambiguous date** creates a false record that looks trustworthy.
- **Dropping every row with a missing value** quietly removes students from the registry.

So this assessment is **not** "make the CSV look tidy." It asks you to work like a data forensic analyst:

1. **Profile** the export and discover its defects. Nobody will hand you a list.
2. **Recover** every value that can be recovered with justified confidence.
3. **Flag**, rather than guess, every value that cannot be recovered.
4. **Consolidate** duplicate records into one row per student without merging different people.
5. **Prove** your claims with tests and a data-quality report that a records officer could act on.

> **Why this matters beyond this dataset.** Industry surveys of data practitioners consistently report that preparing and cleaning data takes a large share of their working time. More importantly, cleaning decisions shape every analysis that follows. The habits you build here (be explicit, be reversible, quantify uncertainty) are the habits of trustworthy data work.

**Known facts from the Records Office** (treat these as the only "documentation" you get):

- The official date convention is **DD/MM/YYYY**, but *one* data-entry office is believed to have used US-style **MM/DD/YYYY** for dates of birth for a period.
- Valid UTME (JAMB) scores range from **0 to 400**. Admission into this university needs at least **180**.
- CGPA is meant to be on the Nigerian **5.0 scale**.
- Matriculation numbers have the form `YY/DEP/NNNN`.
- Phone numbers are Nigerian mobile numbers. The canonical form is **E.164** (`+234` followed by 10 digits).

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Profile** an unfamiliar tabular dataset systematically and produce an evidence-based inventory of its defects, by column, by type and by frequency.
2. **Distinguish missing, invalid, ambiguous and valid values**, and represent each explicitly instead of collapsing them into `NaN`.
3. **Canonicalise** inconsistent categorical values (states, departments) with a transparent, auditable mapping.
4. **Parse** heterogeneous date and phone formats into canonical forms, refusing to guess where the evidence doesn't support a guess.
5. **Detect and consolidate duplicate records** using a defensible matching rule, and show that the rule doesn't merge distinct people.
6. **Detect a systemic (non-random) defect** from distributional evidence and correct it with a stated justification.
7. **Write unit tests** that pin down your cleaning rules, including edge cases.
8. **Communicate** what was fixed, what was flagged, and what remains uncertain, in a concise data-quality report.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

You must implement the `registry_cleaner` package in [`starter/registry_cleaner/`](starter/registry_cleaner/). The function signatures are fixed because the automated tests import them. The internals are entirely yours.

| ID | Requirement |
|---|---|
| **R1** | `is_missing(value) -> bool` treats the export's missing-value tokens as missing (`""`, whitespace-only, `NA`, `N/A`, `-`, `null`, `nil`, case-insensitive) and nothing else. **`"0"` is not a missing token in general.** You must decide, and justify, whether a JAMB score of `0` is plausible. |
| **R2** | `normalize_state(value) -> str \| None` returns one of the 37 canonical names in [`resources/reference/nigerian_states.txt`](resources/reference/nigerian_states.txt) (36 states plus `FCT`), or `None` if the value is missing or cannot be mapped confidently. It must handle case, whitespace, punctuation, "State" suffixes, common abbreviations (e.g. `C/River`), and the multiple names for the FCT. |
| **R3** | `normalize_department(value) -> str \| None` maps to the canonical department names in [`resources/reference/departments.txt`](resources/reference/departments.txt). |
| **R4** | `normalize_phone(value) -> str \| None` returns E.164 (`+234XXXXXXXXXX`, 10 digits after `+234`) for valid Nigerian mobile numbers in any of the formats present, and `None` for missing **or invalid** numbers. Truncated numbers must not be "repaired". |
| **R5** | `parse_name(value) -> tuple[str, str] \| None` returns `(first_name, last_name)` in title case, handling `"SURNAME, Given"` and stray whitespace. |
| **R6** | `parse_date(value, *, field) -> ParsedDate` returns a `ParsedDate(value: date \| None, status: str)` whose `status` is one of `"ok"`, `"missing"`, `"ambiguous"` or `"invalid"`. Rules: ISO, `DD/MM/YYYY`, `DD-MM-YYYY` and `D Mon YYYY` must parse. A slash date that is only valid as MM/DD (for example `03/25/2004`) must parse as MM/DD with status `"ok"`. For `field="date_of_birth"`, a slash date where both readings are valid **and different** (e.g. `04/07/2004`) gets status `"ambiguous"`. Its `value` is the DD/MM reading, so downstream code can use it while the uncertainty stays visible. |
| **R7** | `parse_score(value) -> int \| None` returns a valid JAMB score or `None`. Out-of-range values are `None` and are recorded as issues, never clipped. |
| **R8** | `find_duplicate_groups(df) -> list[set[str]]` takes the raw export and returns groups of `record_id`s that refer to the same student. Every record appears in exactly one group, and singletons are groups of size 1. **Two records with the same name but different identifying evidence must not be merged.** |
| **R9** | `clean_registry(raw_df) -> CleanResult` returns `clean` (one row per inferred student, matching the [output schema](resources/output_schema.md)) and `issues` (one row per detected defect: `record_id, column, issue_type, original_value, action`). |
| **R10** | Run as `python -m registry_cleaner <input.csv> --out <dir>`, it writes `clean_registry.csv` and `issues.csv` to `<dir>`. |
| **R11** | Systemic defect: your pipeline must detect that one department's CGPA values come from a different scale, using **distributional evidence you can show**. Rescale them and record the action in `issues`. The department must **not** be hard-coded by name. Your detection rule must find it from the data. |
| **R12** | Rows whose date of birth is on or after their admission date get `dob_status = "invalid"` and an issue record. They are never silently dropped. |

### D.2 Engineering requirements (mandatory)

- **No row is silently lost.** Every input `record_id` must appear in exactly one `source_record_ids` cell of the clean output.
- **Raw data is never modified in place.** The original export is read-only. All outputs are new files.
- **Determinism.** Running the pipeline twice on the same input gives byte-identical outputs.
- **Tests.** You must keep the provided tests passing and add **at least 12 tests of your own** in `tests/test_member_*.py`. At least four must be edge cases you found while profiling.
- **Dependencies.** Use only the packages in [`starter/requirements.txt`](starter/requirements.txt), plus optionally `rapidfuzz`. If you add `rapidfuzz`, list it in your requirements.
- **Profiling notebook or script.** Your defect inventory must be reproducible from a notebook or script in your submission, not typed in by hand.

### D.3 Privacy and responsibility

The data is **entirely synthetic**. No real student is described. You should still treat it as if it were real personal data. Under the Nigeria Data Protection Act 2023, names, dates of birth, phone numbers and emails are personal data.

- Don't paste rows into public AI tools, issue trackers or chat groups. Describe patterns instead.
- Your report should show **aggregate counts and redacted examples** (e.g. `0803 *** **67`), not full records.
- In one paragraph, explain how your process would change if the data were real: access control, minimisation, and retention of the issues log.

### D.4 Optional enhancements (not required for full marks)

- Fuzzy matching for misspelt names, with a measured false-merge rate.
- A `--explain RECORD_ID` CLI flag that prints every transformation applied to one record.
- Data validation with a schema library (e.g. `pandera`), with a justification for the choice.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/registry_export.csv`](resources/data/registry_export.csv) (1,245 rows × 12 columns, about 140 KB, UTF-8) |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed. Every name, number and email is fictional. Names are random combinations of common Nigerian given names and surnames. Emails use the non-routable `example.ng` pattern. |
| **Licence** | CC BY 4.0 (same as this repository's content). Free to reuse with attribution. |
| **Integrity** | SHA-256 `2ab65751f0f228df66c0f0ad7575777ddd133aeb3ed643206c6c0ca38f289b5f`. The contract test checks it, so don't edit the file. |
| **Reference lists** | [`nigerian_states.txt`](resources/reference/nigerian_states.txt), [`departments.txt`](resources/reference/departments.txt) |
| **Output schema** | [`resources/output_schema.md`](resources/output_schema.md) |

**Input schema.** Every column is read as **text**, and you decide how to type it.

| Column | Meaning | What you should expect |
|---|---|---|
| `record_id` | Export row identifier, unique per row | Clean. Use it for traceability. |
| `matric_no` | Matriculation number | Mostly `YY/DEP/NNNN`, with some separator variants |
| `full_name` | Student's name | Several formats |
| `date_of_birth` | Date of birth | Mixed formats, missing tokens, some impossible values |
| `state_of_origin` | State of origin | Many spellings |
| `phone` | Mobile number | Many formats, some invalid |
| `email` | Email | Case variants |
| `jamb_score` | UTME score | Missing tokens, out-of-range values |
| `admission_date` | Date of admission | Mixed formats |
| `department` | Department | Abbreviations and variants |
| `level` | Current level (100–500) | Some with an `L` suffix |
| `cgpa` | Cumulative GPA | Supposedly on the 5.0 scale |

**Known limitations (by design).** Some dates cannot be disambiguated from the data alone. The ground truth for those is unknowable to you, and you'll be assessed on whether you **flag** them, not on whether you guess them correctly. There are deliberately no free-text notes or audit columns.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-03-data-cleaning-and-quality/DS-T1-006-the-registry-that-lies
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # should pass immediately: checks data and scaffold
pytest                       # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `registry_cleaner/` package (the completed starter) | The cleaning logic: the core technical evidence |
| 2 | `tests/test_member_*.py` (≥ 12 tests) | Shows you can pin behaviour down and think about edge cases |
| 3 | `profiling.ipynb` **or** `profiling.py` | A reproducible defect inventory that justifies every rule you wrote |
| 4 | `outputs/clean_registry.csv`, `outputs/issues.csv` | The artefacts the Records Office would actually use |
| 5 | `DATA_QUALITY_REPORT.md` (at most 1,500 words plus tables), using the [template](submission-template/DATA_QUALITY_REPORT.md) | Communicates findings, decisions and residual uncertainty to a non-technical owner |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 7 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Assessors check the criteria marked ⚙ automatically with the public and hidden test suites, and check the rest by hand.

1. ⚙ `pytest` passes all provided public tests and all of your own tests from a clean environment created from your `requirements.txt`.
2. ⚙ `python -m registry_cleaner resources/data/registry_export.csv --out outputs/` completes in under 60 seconds on a typical laptop and writes both files in the required schema.
3. ⚙ **Traceability:** every one of the 1,245 input `record_id`s appears exactly once across `clean_registry.csv`'s `source_record_ids`.
4. ⚙ **Canonical values:** every non-empty `state_of_origin` and `department` in the output belongs to the reference lists, and every non-empty `phone_e164` matches `^\+234[789][01]\d{8}$`.
5. ⚙ **No invented data:** no output value comes from a value the rules say is unrecoverable. Truncated phones, out-of-range scores and ambiguous dates are flagged, not repaired.
6. ⚙ **Duplicate handling:** on the hidden ground truth, the pairwise precision of your duplicate grouping is **≥ 0.98** and recall is **≥ 0.90**. *Justification:* a false merge corrupts a student's academic record and is far more harmful than a missed duplicate, so precision gets the stricter bar. All duplicates in this export are recoverable from identifying fields, so 0.90 recall is achievable without fuzzy matching.
7. ⚙ **Systemic defect:** the rescaled department is detected from data. Hidden tests run your pipeline on a re-seeded export where a *different* department has the defect.
8. ⚙ The pipeline is deterministic: two runs give byte-identical outputs.
9. ✍ The data-quality report quantifies each defect type, states the rule used for each, and gives an honest estimate of residual error, including how many dates of birth remain ambiguous and why.
10. ✍ The profiling notebook or script regenerates every count quoted in the report.
11. ✍ No full personal record appears in the report or the notebook outputs.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 15 |
| Methodology (profiling → rules → evidence) | 15 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible pipeline, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own repository** from the starter: copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders into a new **private** GitHub repository named `clbg-DS-T1-006-<your-github-username>`.
2. **Expected structure:**
   ```text
   clbg-DS-T1-006-<username>/
   ├── README.md                  # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── registry_cleaner/          # your package (from starter/)
   ├── tests/                     # provided tests + your test_member_*.py
   ├── resources/                 # unchanged
   ├── profiling.ipynb | profiling.py
   ├── outputs/clean_registry.csv
   ├── outputs/issues.csv
   ├── DATA_QUALITY_REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** Your commit history is part of the evidence (see §K). A single "final" commit containing everything will be questioned at defence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository, using the **Assessment submission** issue template. Include the repository URL and the exact commit SHA you are submitting.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines).
6. Full general guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback and can strengthen a placement case, but they never stand in for the core requirements.

1. **The namesake audit.** Estimate how many same-name pairs in the export are *different* people. Then design a test set that would catch a matching rule that over-merges. Report your rule's false-merge rate on it.
2. **Probabilistic ambiguity.** For ambiguous dates of birth, use the rest of the dataset (age at admission, level) to estimate the probability that each reading is correct. Calibrate it: does "80% likely" really hold about 80% of the time on records whose true format you *can* determine?
3. **Contract the next export.** Write a short data contract (column types, allowed values, formats, and the owner of each rule) that the new system's export must satisfy. Implement it as a validation function that rejects the original export with useful messages.
4. **Explain one record.** Implement `--explain RECORD_ID`, producing a human-readable audit trail of every transformation.

---

## K. Assessment Integrity

**AI tools are permitted** to help with your learning, for example to explain regex syntax, suggest pandas idioms, or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`: which tool, what for, and an example prompt. Undisclosed use that becomes apparent at defence is treated as an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** any code you adapted from documentation, Stack Overflow or other sources, with a link.
- **Collaboration:** you may discuss *general techniques* (for example "how do people usually parse mixed date formats?") with other members. You may not share code, rules, counts or report text.
- **How your understanding is verified.** In the 5-minute defence, the assessor will:
  1. choose two `record_id`s from your output and ask you to trace exactly what happened to them;
  2. ask why you chose your duplicate-matching rule and what it would get wrong;
  3. give you a small **unseen modification**, such as a new phone format or a new missing-value token, and ask you to handle it live while explaining your reasoning.

  Your commit history and profiling notebook are also reviewed for consistency with your report.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Basic pandas, functions, regex, and `pytest` mechanics. No statistics beyond counts and comparing distributions. |
| **New skill developed** | Treating cleaning as an *evidence-producing* activity: each rule is justified by profiling and pinned by a test, and each change is logged. |
| **Decisions the member must make** | Which tokens are missing. Whether `0` is a plausible score. When to refuse to parse. What counts as "the same student". How to detect a systemic defect without hard-coding it. What to report as uncertain. |
| **What must be investigated independently** | The defect inventory. The starter gives no list of defects. You only get the Records Office's "known facts", which are incomplete by design. |
| **Why it's interesting** | The dataset contains traps that reward thinking over tidying: namesakes that look like duplicates, dates that look valid but are ambiguous, and a department whose grades are "too good" for a mundane reason. |
| **Evidence of competence** | Hidden-truth precision and recall for deduplication; correct refusal behaviour on unrecoverable values; a report whose numbers can be regenerated; live tracing of records at defence. |
| **Misconceptions exposed** | "`dropna()` is cleaning." "A parsed date is a correct date." "Same name means same person." "Outliers should be clipped." "Hard-coding the broken department is fine." |
| **Preparation for later work** | It leads into DS-T2 data-quality work at scale (record linkage, data contracts), DS-11 pipelines with validation gates, and ML-04, where leakage and label noise come from exactly these defects. |

**Suggested approach**, for members who want guidance (you may ignore it):

1. Spend the first 2–3 hours **only profiling**: `value_counts()` for every column, regex-based format census, cross-tabs.
2. Write the inventory first, then the rules, then the tests.
3. Build the pipeline last. Each normaliser should already be tested on its own.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
