# DS-T1-007: Bags, Basins and Tonnes

> *A state's harvest estimate is only as good as its weakest unit conversion. Harmonise a smallholder survey recorded in bags, basins, mudus and tonnes, flag what is implausible with rules you can defend, and show how much the answer moves.*

![Format: Investigation](https://img.shields.io/badge/format-investigation-0e8a16) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-007` |
| **Title** | Bags, Basins and Tonnes: Harmonising a Smallholder Harvest Survey |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-03: Data Cleaning and Data Quality](../README.md) |
| **Format** | Investigation (secondary: Implementation) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 10–16 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Python functions and modules; pandas `groupby`, `merge` and `value_counts`; medians, quartiles and logarithms; running `pytest` |
| **Skills developed** | Unit-of-measure harmonisation; conversion with uncertainty bounds; robust outlier rules (MAD, IQR) and domain limits; separating "implausible" from "unusual"; sensitivity of totals to cleaning decisions; investigative reporting |
| **Technologies** | Python 3.10+, pandas, NumPy, pytest |

---

## B. Problem Statement

A state Agricultural Development Programme (ADP) in the North Central and North West zones ran a post-harvest survey of **2,400 smallholder plots** across Kaduna, Niger and Benue in late 2024. Sixteen enumerators visited farmers and recorded, for one crop per plot, *how much was harvested* and *how big the plot was*. The ADP will use the results to estimate production, compare yields between LGAs, and decide where to send extension officers and subsidised inputs next season.

The trouble is that farmers do not think in kilograms. They report harvests in **100 kg bags, 50 kg bags, basins (kwano), mudus, paint buckets** and occasionally tonnes, and they report plot sizes in hectares, acres or square metres. Enumerators typed what they heard. The result is a file in which `harvest_unit` has dozens of spellings, a few units have no known weight, the "same" bag weighs different amounts for different crops, and a handful of records produce yields that no farm on earth could achieve.

The ADP's monitoring officer did the obvious thing first: she summed the harvest column after converting what she could, and got a state total so large it would make these three states the most productive grain producers in Africa. Her question to you is simple:

> **What did these farms actually produce, how sure can we be, and which records should we not trust?**

This is a **Tier 1 investigation**. The interfaces, the conversion table and the flagging rules are fixed for you, so the challenge is to implement them correctly and then *use* them to investigate the data. You must find where the implausible values come from and quantify how much each cleaning decision changes the totals.

**What makes it hard:**

- **A unit is not a weight.** A "100 kg bag" of rice paddy weighs about 75 kg because paddy is less dense than grain. A basin is whatever size the market sells. You must use crop-specific factors and carry their uncertainty through to the totals.
- **Outliers are not all errors, and errors are not all outliers.** A 30-hectare farm produces a huge harvest with a perfectly ordinary yield. A plot where 1,450 kg was typed as "1,450 tonnes" has an absurd yield. A rule applied to the wrong quantity, or on the wrong scale, will flag the first and miss the second.
- **Some records cannot be converted at all.** "3 carts" or "5 mudus of paddy" have no factor in the table. Inventing one is not allowed.
- **The defects are not random.** Once your flags are in place, look at *where* they fall. The pattern tells you something the ADP needs to know.

**Known facts from the ADP** (treat these as the only documentation you get):

- `bag` with no size stated means a **100 kg bag** (ADP convention). "Half bag" and "small bag" mean a 50 kg bag.
- Harvests are recorded as shelled grain for maize, sorghum and cowpea, and as **paddy** (unmilled) for rice.
- The conversion factors in [`unit_conversions.csv`](resources/reference/unit_conversions.csv) are the ADP's best current estimates, with a plausible range and a reliability grade: **A** (by definition), **B** (weighed samples) or **C** (enumerator recall workshop). They are illustrative factors compiled for this assessment, not official statistics.
- The sampling frame contained only holdings **under 50 ha**. A plot area above 50 ha cannot be correct.
- A harvest of `0` is a genuine report of crop failure (2024 had localised flooding in parts of Benue and Niger), not a missing value.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Profile** the unit and area columns systematically, and build an auditable mapping from every observed spelling to a canonical unit.
2. **Convert** quantities to kilograms with crop-specific factors, carrying the factor's low/high range so that each total has an uncertainty interval.
3. **Implement** two robust outlier rules (a MAD-based modified z-score and Tukey's IQR fences, both on log yield) and a domain ceiling, and explain why each is computed on yield within a crop rather than on raw quantity.
4. **Distinguish** unconvertible, missing, implausible and unusual-but-genuine records, and represent each explicitly.
5. **Quantify** how the production total changes under four defined scenarios, and explain which scenario the ADP should publish and why.
6. **Investigate** where the implausible values concentrate (by unit, enumerator, LGA or crop) and give the ADP an evidence-based explanation.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `yield_harmonizer` package in [`starter/yield_harmonizer/`](starter/yield_harmonizer/). The signatures are fixed because the tests import them. The output formats are fixed in [`resources/output_schema.md`](resources/output_schema.md).

| ID | Requirement |
|---|---|
| **R1** | `is_missing(value) -> bool` is `True` for `None`, NaN and the survey's missing tokens (`""`, whitespace-only, `NA`, `N/A`, `-`, `nil`, `null`, `none`, case-insensitive) and nothing else. `"0"` is **not** missing. |
| **R2** | `parse_quantity(value) -> float \| None` parses plain numbers (`"12"`, `"3.5"`), thousands separators (`"1,200"`, `"12,345.5"`), mixed fractions (`"2 1/2"`, `"2½"`, `"1/2"`) and zero. It returns `None` for missing tokens, negatives, malformed values and **ambiguous decimal commas** such as `"3,5"` (is it 3.5 or 35?). |
| **R3** | `normalize_unit(value) -> str \| None` maps every harvest-unit spelling to one of `kg`, `tonne`, `bag_100`, `bag_50`, `basin`, `mudu`, `paint_bucket`, or returns `None` for units with no defined weight (for example `cart`, `heap`). It must be case-, whitespace- and trailing-punctuation-insensitive. |
| **R4** | `normalize_area_unit(value) -> str \| None` maps to `ha`, `acre` or `m2`. `parse_area_ha(value, unit) -> float \| None` returns hectares (1 acre = 0.40468564224 ha; 1 m² = 0.0001 ha), and `None` if the value or unit is missing or unrecognised, or the area is not positive. |
| **R5** | `to_kg(quantity, unit, crop, table=None) -> Conversion \| None` returns `Conversion(kg, kg_low, kg_high, grade)` using the factor for **that crop and unit**. It returns `None` when the quantity or unit is `None`, or when the table has no factor for the pair. It never falls back to another crop's factor. |
| **R6** | `mad_flags(values, k=3.5)` and `iqr_flags(values, k=1.5)` each return a boolean Series with the input's index. Both work on `x = log(v)` for **strictly positive** `v` only; zeros, negatives and NaN are never flagged and are excluded from the statistics. **MAD rule:** `z = 0.6745 · (x − median(x)) / MAD`, where `MAD = median(|x − median(x)|)`; flag `|z| > k`. If MAD is 0 or fewer than 3 positive values exist, flag nothing. **IQR rule:** with Q1 and Q3 from `numpy.percentile` (default linear interpolation), flag `x < Q1 − k·IQR` or `x > Q3 + k·IQR`; flag nothing for fewer than 3 positive values. |
| **R7** | `harmonise(raw_df) -> HarmoniseResult(records, issues)` produces one row per input record and an issues log, exactly as in the [output schema](resources/output_schema.md). Plot areas above 50 ha are `invalid_area`. `domain_high` uses [`crop_limits.csv`](resources/reference/crop_limits.csv). `robust_outlier` applies `mad_flags` with k = 3.5 to `yield_kg_ha` **within each crop**. |
| **R8** | `production_totals(records) -> DataFrame` returns the 20-row totals table (4 crops plus `ALL`, × 4 scenarios: `unit_blind`, `all_converted`, `usable_only`, `imputed`) defined in the output schema. The `ALL` row of each scenario equals the sum of the crop rows. |
| **R9** | `python -m yield_harmonizer <survey.csv> --out <dir>` writes `harmonised.csv`, `issues.csv` and `totals.csv`. The CLI is provided. |
| **R10** | **Investigation.** Your report answers the six questions in the [report template](submission-template/HARVEST_QUALITY_REPORT.md), with every number regenerated by your analysis script or notebook. At minimum: how many records each rule flags and how the rules overlap; which scenario total you recommend and its low–high range; and where the implausible values concentrate, with a table or chart as evidence. |

### D.2 Engineering requirements (mandatory)

- **No record is lost.** `harmonised.csv` has exactly 2,400 rows.
- **No invented factors.** Every kg value must come from `unit_conversions.csv`. If you believe a factor is missing or wrong, say so in the report. Don't edit the table.
- **The raw file is read-only.** All outputs are new files.
- **Determinism.** Two runs produce byte-identical outputs.
- **Tests.** Keep the provided tests passing and add **at least 10 tests of your own** in `tests/test_member_*.py`. At least three must be cases you found while profiling (a spelling, a quantity format, an edge case in the flags).
- **Dependencies.** pandas, NumPy and pytest only, plus matplotlib if you want charts.
- **Analysis code.** The investigation (R10) must live in `analysis.py` or `analysis.ipynb` and run end to end after the pipeline.

### D.3 Privacy and responsibility

The survey is **synthetic**. Enumerator and farmer identifiers are random codes, and no names are recorded. Real farm surveys do contain personal and location data. In one paragraph of your report, explain how you would handle enumerator-level findings responsibly: an enumerator whose records are systematically wrong needs retraining, not public naming, and an individual farmer's yield is commercially sensitive.

### D.4 Optional enhancements (not required for full marks)

- A comparison of k values (2.5, 3.0, 3.5, 4.0) for the MAD rule, with the flag count at each.
- Flagging *low* implausible yields with a domain floor, with your justification for the floor.
- A chart of log-yield distributions by crop with the MAD and IQR fences drawn on.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/harvest_survey.csv`](resources/data/harvest_survey.csv): 2,400 rows × 10 columns, about 165 KB, UTF-8 |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed. States and LGAs are real place names, but every record, enumerator code and yield is fictional. The generator is kept in the assessor kit because it would reveal which records are defective. |
| **Licence** | CC BY 4.0 (same as this repository's content) |
| **Integrity** | SHA-256 `c21b88a24fa7f8da19b0be1ce522f37c25df24b5d0966060c4cbfc5c3809e9cf`. The contract test checks it. |
| **Reference tables** | [`unit_conversions.csv`](resources/reference/unit_conversions.csv) (crop, unit, kg_per_unit, kg_low, kg_high, grade, basis) · [`crop_limits.csv`](resources/reference/crop_limits.csv) (maximum plausible yield per crop) · [`area_units.csv`](resources/reference/area_units.csv) |
| **Output schema** | [`resources/output_schema.md`](resources/output_schema.md) |

**Input schema.** Every column is read as **text**.

| Column | Meaning | What you should expect |
|---|---|---|
| `record_id` | Survey record, unique | Clean |
| `state`, `lga` | Location | Clean |
| `enumerator_id` | Who collected the record | Clean codes `EN01`–`EN16` |
| `interview_date` | ISO date | Clean |
| `crop` | Crop | Clean: `maize`, `sorghum`, `cowpea`, `rice_paddy` |
| `harvest_qty` | Quantity harvested, in `harvest_unit` | Several number formats, missing tokens, zeros |
| `harvest_unit` | Unit as typed | Many spellings; some units have no weight |
| `plot_area` | Plot size, in `area_unit` | Several formats, missing tokens |
| `area_unit` | Area unit as typed | Several spellings |

**Known limitations (by design).** The table's factors are uncertain, especially grade C, so your totals must carry a range. There is no sampling weight. Treat totals as totals over the sampled plots, not state estimates, and say so in your report. You can't check any individual record against a scale; the evidence you have is distributional.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-03-data-cleaning-and-quality/DS-T1-007-bags-basins-and-tonnes
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract      # passes immediately: checks data, tables and API
pytest                  # most tests fail until you implement the package
```

> **A pandas trap worth knowing:** `df.flags` is a built-in pandas attribute, not your column. Always write `df["flags"]`.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `yield_harmonizer/` package (the completed starter) | The conversion and flagging logic: the core technical evidence |
| 2 | `tests/test_member_*.py` (≥ 10 tests) | Shows you can pin rules down, including cases found while profiling |
| 3 | `analysis.py` **or** `analysis.ipynb` | Regenerates every number and figure in the report |
| 4 | `outputs/harmonised.csv`, `outputs/issues.csv`, `outputs/totals.csv` | The artefacts the ADP would use |
| 5 | `HARVEST_QUALITY_REPORT.md` (at most 1,500 words plus tables and figures), from the [template](submission-template/HARVEST_QUALITY_REPORT.md) | Answers the investigation questions for a non-specialist ADP manager |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 7 | A 5–10 minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Assessors check ⚙ criteria with the public and hidden test suites, and ✍ criteria by hand.

1. ⚙ `pytest` passes all provided tests and all of your own tests in a clean environment built from your `requirements.txt`.
2. ⚙ `python -m yield_harmonizer resources/data/harvest_survey.csv --out outputs/` finishes in under 60 seconds and writes the three files in the required schema.
3. ⚙ **Traceability:** `harmonised.csv` contains every input `record_id` exactly once.
4. ⚙ **Correct conversion:** on the hidden truth, at least **99.5%** of convertible records have `kg` equal (within 0.1%) to quantity × the table factor. *Justification:* the factors are given, so conversion is deterministic. The 0.5% margin allows for one or two rare spellings you could not have seen, but no systematic error.
5. ⚙ **No invented conversions:** records with unknown units or no crop factor have empty `kg`, on the official survey and on re-seeded surveys.
6. ⚙ **Implausible values are caught:** every unit slip that produces an impossible yield is flagged `domain_high`, and at least **90%** of the records affected by the survey's systemic defect are not `usable`. This holds on re-seeded surveys where different records and a different source carry the defects. *Justification:* the defects are orders of magnitude away from typical yields, so a correctly implemented rule finds nearly all of them. The 10% margin covers records where the defect happens to land in the plausible range.
7. ⚙ **Genuine records survive:** at most **2%** of defect-free records are flagged unusable, and no genuinely large farm and no zero harvest is made unusable. *Justification:* the reference rule flags under 0.2% of clean records. 2% leaves room for reasonable variation while catching a rule applied to the wrong quantity (Tukey fences on raw kg pooled across crops flag 5–6% of clean records, including every large farm). The same MAD rule on linear rather than log yields flags 1–2%, all on the high tail; it passes this bar but not the report criterion, because you must explain why the skew makes the log scale the right one.
8. ⚙ **Totals:** on the hidden truth, the `ALL / imputed` total lies within **15%** of the true production of all sampled plots. *Justification:* the reference lands within 2% on the official and two re-seeded surveys. 15% allows for legitimate differences in how flagged records are handled while rejecting a total still dominated by unit slips (the `all_converted` total is 4.6–8.8 times the truth on the same surveys).
9. ⚙ The pipeline is deterministic.
10. ✍ The report compares the MAD, IQR and domain rules (counts and overlap), and explains why they are applied to log yield within a crop.
11. ✍ The report identifies where the implausible values concentrate, shows the evidence, and recommends a concrete action to the ADP.
12. ✍ The report recommends one total with its low–high range, and explains in plain language what the range does and does not capture.
13. ✍ Every number in the report is regenerated by the analysis code.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Investigation methodology and evidence | 20 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible pipeline and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-DS-T1-007-<your-github-username>`, and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` into it.
2. **Expected structure:**
   ```text
   clbg-DS-T1-007-<username>/
   ├── README.md                    # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── yield_harmonizer/            # your package (from starter/)
   ├── tests/                       # provided tests + your test_member_*.py
   ├── resources/                   # unchanged
   ├── analysis.py | analysis.ipynb
   ├── outputs/harmonised.csv
   ├── outputs/issues.csv
   ├── outputs/totals.csv
   ├── HARVEST_QUALITY_REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** Your history is part of the evidence. A single final commit will be questioned at defence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue in the CLBG assessments repository with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines).
6. Full guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback but never replace the core requirements.

1. **Which factor matters most?** For the `imputed` total, compute how much of the low–high range comes from each (crop, unit) factor. Which single weighing exercise should the ADP fund next season to narrow the range most?
2. **Rule-choice sensitivity.** Recompute the totals with k = 2.5, 3.0, 3.5 and 4.0 and with the IQR rule instead of MAD. Plot the `imputed` total against the rule. Is the recommended total robust to this choice?
3. **Correct, don't just flag?** For one class of flagged records, argue whether a correction (rather than a flag) is justified, implement it as a separate opt-in function, and show its effect. State what evidence would be needed to make it the default.
4. **A data-entry validator.** Write a function that an enumerator's tablet could run at entry time to warn about implausible yields before the interview ends. Which of your rules can run on a single record, and which need the whole dataset?

---

## K. Assessment Integrity

**AI tools are permitted** for learning, for example to explain the modified z-score, suggest pandas idioms or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`: the tool, the purpose and an example prompt. Disclosed, reasonable use is not penalised. Undisclosed use that becomes apparent at defence is an integrity breach.
- **Cite** adapted code and any source for outlier-rule definitions (for example the original description of the modified z-score).
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, mappings, counts, findings or report text.
- **How your understanding is verified.** In the defence, the assessor will:
  1. choose two records from your `issues.csv`, one flagged and one not, and ask you to trace every step from raw strings to the `usable` decision;
  2. ask you to compute the modified z-score of a given log yield by hand from the crop's median and MAD, and explain the 0.6745 constant;
  3. give you an **unseen modification** to make live, for example a new unit spelling, a new local measure with a factor, or a change to k, and ask you to predict its effect on the totals *before* running it.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | pandas basics, medians and quartiles, logarithms, and `pytest`. |
| **New skill developed** | Treating units and plausibility as *data-quality decisions with measurable consequences*: every conversion carries uncertainty, every flag is a rule that can be defended, and every decision moves the headline number by an amount you can state. |
| **Decisions the member must make** | Which spellings map to which unit, and which must be refused. How to explain the gap between scenarios. Which total to recommend. How to present an enumerator-level finding without blaming a person. |
| **What must be investigated independently** | The unit census, the overlap of the three rules, the source of the implausible values and the drivers of the uncertainty range. None of this is listed in the brief. |
| **Why it's interesting** | The naive total is wrong by almost an order of magnitude, and fewer than 1% of the records cause most of the error. One source of error is systemic, and it only becomes visible when you look at *where* the flags fall. The right rule on the wrong scale flags real large farms, so the choice of statistic visibly matters. |
| **Evidence of competence** | Exact rule implementations pinned by tests; hidden-truth conversion accuracy and flag recall on re-seeded data; an investigation whose numbers regenerate; live hand computation of a robust z-score. |
| **Misconceptions exposed** | "A bag is a bag." "Outliers are the biggest numbers." "Mean ± 3 SD is a safe outlier rule." "Flagged records can simply be dropped from a total." "If a factor is missing I can borrow another crop's." |
| **Preparation for later work** | It leads into DS-T2 data-contract work (validating recurring feeds), DS-T3 multiverse analysis (how cleaning choices change conclusions), and any survey or sensor work where measurement error must be separated from real variation. |

**Suggested approach** (optional):

1. Begin with `value_counts()` on `harvest_unit` and `area_unit`, and a regex census of `harvest_qty` formats. Write your mapping from this evidence.
2. Implement and test the parsers, then `to_kg`, then the flag rules on small hand-made Series, then the pipeline.
3. Only then run the investigation: cross-tabulate flags by unit, enumerator, LGA and crop, and look at the yield distributions on a log scale.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
