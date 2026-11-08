# DS-T1-017: Hot Days, Six Cities

> *"Is it getting hotter?" sounds like one question. For Sokoto, Maiduguri, Kano, Abuja, Lagos and Port Harcourt, answer it with real NASA data and small multiples, and discover that the answer depends on what you mean by "hot".*

![Format: Investigation](https://img.shields.io/badge/format-investigation-e36209) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20internet%20at%20setup-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-017` |
| **Title** | Hot Days, Six Cities: A Small-Multiples Climate Story from NASA POWER |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-06: Data Visualization and Storytelling](../README.md) |
| **Format** | Investigation (secondary: Implementation) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 2 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 10–16 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. About 1.5 MB of downloads once, then offline |
| **Recommended prerequisites** | pandas (`groupby`, datetime columns); matplotlib subplots; percentiles; running `pytest` |
| **Skills developed** | Parsing a real scientific data product; defining indicators (absolute vs relative thresholds); missing-data rules; comparing periods; designing small multiples (shared scales, ordering, annotation); writing a short, honest visual story |
| **Technologies** | Python 3.10+, pandas, numpy, matplotlib, pytest |

---

## B. Problem Statement

A Nigerian newsroom's data desk is preparing a piece for the start of the hot season. The editor's brief is one sentence: *"Show readers whether hot days are becoming more common in our cities."* The desk has chosen six cities along a north–south line: **Sokoto, Maiduguri, Kano, Abuja, Lagos and Port Harcourt**. It will use daily maximum temperature from **NASA POWER**, a free, keyless API that serves MERRA-2 reanalysis data for any point on Earth since 1981.

You will build the analysis and the graphics, and write the story. The core comparison is fixed so that everyone's answers can be checked: **mean hot days per year in 2010–2024 versus 1991–2005**, for each city.

**What makes it hard.**
- **"Hot" has no single definition.** A fixed threshold such as 40 °C is meaningful in Sokoto and meaningless in Lagos, which rarely exceeds 35 °C. A **city-relative** threshold (each city's own 90th percentile of daily maxima in 1991–2005) measures "unusually hot *for here*". The two definitions can tell different stories, and in at least one city they point in **opposite directions**. You will compute both and decide what the honest headline is.
- **Small multiples demand design decisions.** Should panels share a y-axis? (Yes by default, or readers can't compare. Your story must say when you broke this and why.) In what order should panels go? (North to south, so that the gradient reads as geography.) Should years run as bars or as a line?
- **The data is a model, not a thermometer.** MERRA-2 is a *reanalysis* on a grid of about 50 km by 60 km. A "Lagos" cell includes sea, and reanalysis inputs changed over time. A responsible story says what this means for a reader.
- **Missing data must not look like cool weather.** POWER marks missing values as `-999`. A year with many missing days would show *fewer* hot days for the wrong reason, so such years must become "no data", not small counts.

**Known facts:**
- City coordinates are fixed in [`resources/cities.csv`](resources/cities.csv) (city-centre points, two decimals).
- The download period is 1 January 1991 to 31 December 2024 (the provided `fetch.py`).
- Nobody, including the assessors, picks the "right" headline in advance. You are assessed on whether your conclusions follow from your evidence.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Parse** a real scientific data file (header block, day-of-year dates, a fill value) into a clean, typed table, with tests.
2. **Define and compute** climate indicators with explicit rules for thresholds and missing data, and explain how the rules change the answer.
3. **Compare periods** correctly, refusing comparisons that the data cannot support.
4. **Design small multiples** whose ordering, shared scales and annotation make the comparison visible at a glance, verified by tests on the Figure object.
5. **Tell a short visual story** whose headline follows from the evidence, states its uncertainty and data limitations, and does not overclaim.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `climate_story` in [`starter/climate_story/`](starter/climate_story/). `fetch.py` is provided. The signatures and constants are fixed.

| ID | Requirement |
|---|---|
| **R1** | `read_power_csv(path) -> DataFrame` returns a `date` column (datetime64) followed by one float column per parameter, named in lower case (`t2m_max`, `prectotcorr`), sorted by date. It handles the `-BEGIN HEADER-` … `-END HEADER-` block (allowing surrounding whitespace) or no header at all, both the `YEAR,DOY` and `YEAR,MO,DY` layouts, and leap years, and converts `-999` to NaN. |
| **R2** | `annual_hot_days(df, threshold, col="t2m_max", min_coverage=0.9) -> Series` counts days per calendar year with `col ≥ threshold` (inclusive), indexed by year. A year with fewer valid days than `min_coverage × (365 or 366)` gets **NaN**. *Why 0.9:* with 36 or more missing days the count can be wrong by more than a typical year-to-year difference in the drier cities. The WMO's climate-normals guidance also uses completeness rules of this kind. |
| **R3** | `percentile_threshold(df, q=0.9, base=(1991, 2005), col="t2m_max") -> float` returns the q-quantile (numpy default method) of valid daily values in the base years, inclusive. |
| **R4** | `period_change(annual, base=(1991, 2005), recent=(2010, 2024)) -> dict` returns `base_mean`, `recent_mean`, `change` (recent − base), `n_base` and `n_recent`, ignoring NaN years. It raises `ValueError` if either period has fewer than `MIN_YEARS` (10) valid years. *Why 10:* two-thirds of a 15-year window keeps the mean from resting on a handful of years. The 5-year gap between the periods keeps them clearly separated. |
| **R5** | `monthly_climatology(df, years, col="t2m_max") -> Series` returns the mean daily value per calendar month over the given years, indexed 1–12. |
| **R6** | `small_multiples(series_by_city, latitudes, *, title, ylabel, xlabel="", source="NASA POWER", ncols=3, sharey=True, kind="line") -> Figure`: exactly one Axes per city, with unused grid cells removed. Panels run **north to south in reading order** (latitude descending). Each panel's title is the city name. With `sharey`, every panel has identical y-limits that contain all the data, with the lower limit **0 when all values are ≥ 0** and below the minimum otherwise. The figure's suptitle equals `title`. The left-column panels carry `ylabel`. A text starts with `Source:` and includes `source`. Each panel draws its series as a line or (`kind="bar"`) bars with exactly the series values. Unknown latitudes raise `ValueError`. |
| **R7** | `make_story.py` at the repository root reads your downloaded files and writes, to `figures/`: (a) hot days per year at a fixed **40 °C** threshold, as small multiples; (b) hot days per year above each city's own **90th percentile**, as small multiples; (c) the change in monthly mean Tmax (2010–2024 minus 1991–2005), as small multiples; and `figures/results.csv` with one row per city and threshold type: `city, threshold_type, threshold_c, base_mean, recent_mean, change`. |

### D.2 Engineering requirements (mandatory)

- **Data provenance.** Download with `python -m climate_story.fetch --out data/raw`. **Do not commit** the raw files. Commit `data/raw/FETCH_LOG.csv` (URL, UTC time, SHA-256 and size per city) so the assessor can tell whether a later download differs.
- **Tests.** Keep the provided tests passing and add **at least 8 of your own** in `tests/test_member_*.py`, including a year with exactly 90% coverage, a leap year, and a period with exactly 10 valid years.
- **Determinism.** `make_story.py` regenerates `results.csv` and the figures byte-for-byte from the same raw files.
- **Dependencies.** Only those in [`starter/requirements.txt`](starter/requirements.txt).

### D.3 Responsible communication

Climate stories are easy to overclaim. Your story must:
- say plainly that this is reanalysis data for a grid cell, not station measurements, and what that implies for a coastal city;
- avoid attributing changes to causes (for example "climate change made Kano hotter"). A two-period comparison of one indicator cannot show attribution. You may cite published assessments for context;
- report changes as days per year with the periods named, not as unexplained percentages;
- cite NASA POWER as its [referencing guide](https://power.larc.nasa.gov/docs/referencing/) asks.

### D.4 Optional enhancements (not required for full marks)

- A bootstrap interval (resampling years) for each city's change, shown as an interval plot.
- A seventh city of your choice, with a justification of the coordinates.
- A comparison against a second source such as Open-Meteo's historical API for one city.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | NASA POWER daily point API (registry [`DSET-022`](../../../../../../shared/datasets/DATASET_REGISTRY.md)), parameters `T2M_MAX` (MERRA-2 2 m daily maximum temperature, °C) and `PRECTOTCORR` (bias-corrected precipitation, mm/day), community `AG`, 1991-01-01 to 2024-12-31 |
| **Link** | <https://power.larc.nasa.gov/> (API documentation: <https://power.larc.nasa.gov/docs/services/api/>) |
| **Licence and terms** | NASA's open data policy: data produced under NASA sponsorship is freely available to all users. POWER asks users to cite both the POWER reference and the data reference (see its referencing guide). Raw files are downloaded by you at setup and not redistributed in this repository. |
| **Format and size** | CSV with a text header block, columns `YEAR, DOY, T2M_MAX, PRECTOTCORR`, about 250 KB and 12,419 rows per city |
| **Cities** | [`resources/cities.csv`](resources/cities.csv) |
| **Test data** | The tests use **synthetic** files in POWER's layout, written by [`tests/powerfixture.py`](tests/powerfixture.py), so they run offline. |

**Known limitations.** MERRA-2 cells are about 0.5° × 0.625°, so a city point is a cell average, and coastal cells mix land and sea. Reanalysis can contain step changes when the observing system changes, and some city series show a jump in the late 1990s that you should look for and discuss rather than ignore. POWER may revise data, which is why the fetch log records hashes. The current POWER files for these cities have no missing days, but your parser and coverage rule must still be correct, because other sources and parameters do have gaps (the tests check this).

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-06-visualization-and-storytelling/DS-T1-017-hot-days-small-multiples
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract                                  # offline checks: pass immediately
cd starter && python -m climate_story.fetch --out ../data/raw && cd ..   # about 1.5 MB, 6 requests
pytest                                              # most tests fail until you implement the package
```

No internet at home? Run the fetch step once on a campus connection or in a free Colab or Kaggle notebook and copy `data/raw/` across. Everything after that is offline.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `climate_story/` package | Parsing, indicators and plotting: the tested core |
| 2 | `tests/test_member_*.py` (≥ 8 tests) | Pins the boundary rules (coverage, leap years, minimum years) |
| 3 | `make_story.py`, `figures/*.png`, `figures/results.csv` | The reproducible evidence |
| 4 | `figures/chart_specs.json` | For each figure: `file`, `question`, `indicator`, `threshold`, `periods`, `encoding`, `shared_y` (bool), `panel_order`, `source`, `caveat`. A machine-readable record of your design decisions |
| 5 | `STORY.md` (at most 700 words plus the three figures), using the [template](submission-template/STORY.md) | The newsroom piece: a headline, three figure-led paragraphs, a "what this data can't tell you" box |
| 6 | `data/raw/FETCH_LOG.csv` | Provenance of the data you analysed |
| 7 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 8 | A 5–10 minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

⚙ = automated (public and hidden suites), ✍ = assessor.

1. ⚙ `pytest` passes all provided and member tests in a clean environment.
2. ⚙ **Parsing** reproduces unseen synthetic POWER files exactly, in both date layouts, with scattered `-999` gaps and header whitespace variants.
3. ⚙ **Indicators** (R2–R5) match independent computations on unseen files with gaps, at three thresholds, a custom quantile (0.95) and custom periods. The coverage rule turns exactly the years below 90% into NaN.
4. ⚙ **Small multiples** pass every R6 rule on an unseen set of 7 cities in a 2-column grid with signed values, and on independent axes when `sharey=False`.
5. ✍ `results.csv` matches the assessor's rerun of `make_story.py` on the raw files described in your fetch log, and the numbers quoted in `STORY.md` match `results.csv`.
6. ✍ `STORY.md` states, for each city, the 40 °C and the 90th-percentile change, identifies at least one city where the two definitions disagree in sign or size, and explains why.
7. ✍ The story's "what this data can't tell you" box covers reanalysis versus stations, the grid cell for coastal cities, possible step changes, and the absence of attribution.
8. ✍ `chart_specs.json` contains every required key for each figure, and the figures match it (for example `shared_y: true` really is shared).

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Methodology: indicator and design choices | 15 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication (the story) | 15 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates in the rubric. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create a private repository** named `clbg-DS-T1-017-<your-github-username>` from this assessment's `starter/`, `tests/`, `resources/` and `submission-template/`.
2. **Expected structure:**
   ```text
   clbg-DS-T1-017-<username>/
   ├── README.md                 # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── climate_story/
   ├── tests/
   ├── resources/cities.csv
   ├── data/raw/FETCH_LOG.csv    # raw CSVs are NOT committed (add them to .gitignore)
   ├── make_story.py
   ├── figures/                  # 3 PNGs, results.csv, chart_specs.json
   ├── STORY.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.**
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue with the repository URL and commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **How sure is the change?** Bootstrap the years within each period and show 90% intervals for every city's change. Which cities' changes are distinguishable from zero?
2. **Hot nights.** Repeat the analysis with `T2M_MIN` (hot nights matter more for health) and contrast the stories.
3. **Second source.** Compare one city against Open-Meteo's historical archive and quantify the disagreement.
4. **Step-change check.** Test whether a city's series has a level shift around the late 1990s (for example with a simple two-segment fit) and discuss what it would mean for the period comparison.

---

## K. Assessment Integrity

**AI tools are permitted** for learning, for example to explain pandas datetime handling or matplotlib grids. **They may not do the assessment for you.** You must be able to explain and modify every line, and defend every sentence of your story.

- **Disclose** AI use in `AI_USE_AND_SOURCES.md`. **Cite** NASA POWER and any published climate assessment you mention.
- **Collaboration:** you may discuss general ideas with other members. You may not share code, figures, numbers or text. Everyone downloads the same data, so identical prose or figure styling will be compared.
- **How your understanding is verified.** In the defence, the assessor will:
  1. point at one panel and ask what a reader should conclude from it, and what they should *not*;
  2. change the threshold (for example to 38 °C) or the base period live and ask you to predict which cities change most before running `make_story.py`;
  3. ask you to explain the city where the two definitions disagree, and what extra evidence would settle which story is right.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | pandas datetimes and groupby, percentiles, matplotlib subplots. |
| **New skill developed** | Turning a vague editorial question into defined indicators, and choosing a graphic form (small multiples) that makes the comparison honest and fast. |
| **Decisions the member must make** | Bars or lines, the grid shape, when (if ever) to unshare axes, which figure leads, how to word a mixed result, and what goes in the limitations box. |
| **What must be investigated independently** | What MERRA-2 is and why coastal cells behave differently; why fixed and relative thresholds diverge; whether the series contain step changes. |
| **Why it's interesting** | The answer is not known in advance and is not uniform: the fixed and the relative definitions disagree for some cities, and the honest headline has to hold that tension. |
| **Evidence of competence** | Exact indicator checks on unseen files; Figure-level checks on small multiples; numbers in the story that a rerun reproduces; live prediction at defence. |
| **Misconceptions exposed** | "Missing days are just fewer hot days." "Free y-axes make each panel clearer, so they're better." "A gridded value is the temperature in the city." "Two periods prove a trend." "One threshold fits every city." |
| **Preparation for later work** | It leads into DS-10 time-series work (trends, breaks), DS-T2 explorable explanations for non-technical audiences, and DS-T3 replication of published graphics. |

**Suggested approach** (optional): parse one city and plot its raw daily series before writing any indicator code. Implement R1–R5 against the synthetic fixtures. Then produce rough figures for all six cities, decide the story, and only then polish the design.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
