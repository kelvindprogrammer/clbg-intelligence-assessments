# DS-T2-004: Rain, Grain and Granularity

> *Daily satellite-era climate, annual national crop statistics and World Bank indicators were never designed to fit together. Fuse them for Nigeria, and find out how much the answer to "does rainfall drive cereal yields?" depends on choices nobody writes down.*

![Format: Comparative](https://img.shields.io/badge/format-comparative-0e8a16) ![Tier 2](https://img.shields.io/badge/tier-2-fbca04) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20small%20downloads-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-004` |
| **Title** | Rain, Grain and Granularity: Fusing Open Climate, Crop and Development Data at Mismatched Scales |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Engineering and Independent Problem-Solving |
| **Unit** | [DS-02: Data Acquisition and Sourcing](../README.md) |
| **Format** | Comparative (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 3 · Engineering 2 · Ambiguity 4 · Resources 2 (each out of 5) |
| **Estimated time** | 20–35 hours over 2–3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop. Downloads total under 10 MB (about 7–15 NASA POWER point series, a 4 MB FAOSTAT zip and a few World Bank API calls) |
| **Recommended prerequisites** | [DS-T1-004](../../../../tier-1/units/DS-02-data-acquisition-and-sourcing/DS-T1-004-every-page-exactly-once/README.md) or equivalent API experience; pandas time series (`resample`, `groupby` by year); correlation and simple regression; the idea of a confidence interval |
| **Skills developed** | Multi-source acquisition; temporal and spatial aggregation; coverage accounting; flag-aware use of official statistics; detrending; sensitivity analysis across alignment designs; bootstrap uncertainty; honest reporting of null results |
| **Technologies** | Python 3.10+, pandas, numpy, scipy or statsmodels, matplotlib, pytest |

---

## B. Problem Statement

A state agricultural development programme wants to know whether a poor rainy season is visible in Nigeria's cereal yields, and whether it could use free climate data as an early warning. A consultant's slide says *"rainfall explains Nigeria's cereal yields: r = −0.17"*. Nobody knows which rainfall, where, over which months, or against which yield series. (Yes, the slide's coefficient is negative, and nobody asked why.)

You will rebuild the analysis properly from three real, open sources that were **never designed to fit together**:

| Source | Granularity | Registry |
|---|---|---|
| **NASA POWER** daily point API: precipitation (`PRECTOTCORR`), maximum temperature (`T2M_MAX`) | Daily; ~0.5° × 0.625° grid cells; any point you choose | `DSET-022` |
| **FAOSTAT** Crops and livestock products: production, area harvested and yield of maize, sorghum, millet and rice | Annual; **national** only; each value flagged official (`A`), estimated (`E`), imputed (`I`) or external (`X`) | `DSET-021` |
| **World Bank WDI**: e.g. `AG.YLD.CREL.KG` (cereal yield), `AG.LND.PRCP.MM` (average precipitation) | Annual; national | `DSET-019` |

Fusing them forces decisions that change the answer:

- **Where?** Nigeria spans humid forest to Sahel. One centroid point? Several points across the cereal belt? Weighted how, when FAOSTAT gives you no state-level production?
- **When?** Calendar year, or a growing season? Which months? The season differs between north and south.
- **What counts as data?** POWER has fill values. A season with missing days is not a dry season. FAOSTAT's recent years are largely `X` or `E`-flagged.
- **What is the signal?** Yields trend upwards with technology and area changes. Correlating two trending series measures the trends.
- **Are the sources independent?** Read the WDI metadata for `AG.YLD.CREL.KG` and check where it comes from. Check what `AG.LND.PRCP.MM` actually contains, year by year.

There is no answer key for the headline question. The assessors' own calibration run found that the sign of the correlation **changes** between reasonable designs, and that every 95 % interval they computed contained zero. Your job is not to find a big effect. It is to **show how robust (or fragile) the conclusion is**, design by design, and to say what these data can and cannot support.

---

## C. Objectives

You should be able to show that you can:

1. **Acquire** three open sources reproducibly, with recorded versions, licences and access dates.
2. **Align** daily gridded, annual national and indicator data on one annual key, with explicit, tested rules for seasons, coverage, leap years and fill values.
3. **Compare** at least four alignment designs against a stated baseline, quantifying how the estimated climate–yield association changes, with bootstrap uncertainty.
4. **Use flags and metadata critically**: identify estimated or imputed years, and non-independent or non-observational series, and show their effect.
5. **Report** a defensible conclusion, including a null one, with threats to validity and what extra data would change it.

---

## D. Technical Requirements

### D.1 Mandatory requirements

The package `climfuse` ([`starter/climfuse/`](starter/climfuse/)) has six fixed primitives, which the tests import. Everything built on top of them is your design.

| ID | Requirement |
|---|---|
| **R1** | `read_power(path)` reads a POWER daily point JSON into `[date, parameter, value]`. The fill value declared in `header.fill_value` (and the documented `-999`) becomes `NaN`. |
| **R2** | `season_aggregate(daily, start="MM-DD", end="MM-DD", how="sum"\|"mean"\|"max"\|"min", min_coverage=0.9)` returns `[year, value, n_days, n_valid, coverage]`. `n_days` comes from the **calendar** (leap years included), so absent rows and `NaN`s are both missing, and duplicate dates count once. A season that crosses 31 December belongs to the year in which it **ends**. If `coverage < min_coverage`, `value` is `NaN`. For `how="sum"` the value is the mean of the valid days × `n_days`. *Justification:* this keeps seasons comparable when a few days are missing, and the 0.9 floor stops one rainy week from being scaled up into a "season". |
| **R3** | `weighted_mean({name: Series(year→value)}, {name: weight})` returns `[year, value, weight_used]`, renormalising the weights over the points available each year. `weight_used` is the share of the total weight present. Negative weights raise `ValueError`, and zero-weight points are ignored. |
| **R4** | `read_faostat_wide(path, area, items, element)` converts FAOSTAT's bulk wide format (`Y####`, `Y####F`, `Y####N`) to `[year, item, value, unit, flag]`. Empty cells become `NaN`, and the flag is kept. |
| **R5** | `detrend(series, method="linear"\|"first_difference")`: OLS linear residuals fitted on the non-missing years, or first differences. `NaN`s stay `NaN`. |
| **R6** | `align({name: frame}, how="inner")` gives one row per year. Value columns are named `<name>` and every other column becomes `<name>__<column>`, so coverage and flags travel with the values. Duplicate years raise `ValueError`. |
| **R7** | **Acquisition script** (`acquire.py`) that downloads every source you use into `data/raw/` and writes `data/raw/MANIFEST.json`: URL, access timestamp, SHA-256, bytes, and the version or `lastupdated` value where the source provides one. It must be re-runnable, skip files already present, and be polite (sequential, with a delay, and a contact in the User-Agent). |
| **R8** | **Baseline:** reproduce the consultant's style of number: one national-centroid POWER point, calendar-year total rainfall, the raw (not detrended) national cereal yield, and a Pearson correlation. |
| **R9** | **Comparison:** at least **four further designs**, each changing one documented decision from the baseline or a previous design (season definition, spatial sampling or weighting, detrending, flag filtering, a temperature variable, crop choice). For each design, report the estimate with a **bootstrap 95 % interval** and `n`. At least one design must use a multi-point spatial aggregate built with R3. |
| **R10** | **Source audit:** use the WDI metadata and the values themselves to decide whether `AG.YLD.CREL.KG` and `AG.LND.PRCP.MM` add independent information to FAOSTAT and POWER, and show the evidence. |

### D.2 Engineering requirements

- Keep the provided tests passing, and add **at least 10** member tests for your own alignment code: point selection, flag filtering and the design runner.
- **One command** (`python run_designs.py`) regenerates every number and figure from `data/raw/` without network access.
- Raw data is never edited. Derived data goes to `data/derived/`.

### D.3 Data ethics and licensing

- Attribute every source as its terms require: FAOSTAT and WDI under CC BY 4.0, and NASA POWER according to its referencing guide. Put the attributions in `SOURCES.md`.
- **Don't overclaim.** A national-annual correlation from about 30 years of data cannot support farm-level advice. The programme's decision is about where to invest in early warning, and an overconfident answer could misdirect it.
- Commit only small derived data and your manifest, not bulk downloads. The `MANIFEST.json` and the SHA-256 values make the raw data verifiable without redistributing it.

### D.4 Optional enhancements

- Zone-specific seasons (e.g. April–October in the Guinea savanna, June–September in the Sudan–Sahel), with points weighted by zone.
- Block or moving-block bootstrap, with an argument about serial correlation.
- A state-level extension using another open source (with its own licence check).

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **NASA POWER** (`DSET-022`) | `https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR,T2M_MAX&community=AG&latitude=..&longitude=..&start=19910101&end=20231231&format=JSON`. About 390 KB per point for 33 years. Cite it as the [referencing guide](https://power.larc.nasa.gov/docs/referencing/) asks. |
| **FAOSTAT QCL** (`DSET-021`) | Africa bulk file: `https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_Africa.zip` (4.3 MB zipped, 1961–2024; verified 2026-11-03). Licence CC BY 4.0 ([terms](https://www.fao.org/contact-us/terms/db-terms-of-use/en/)). Yield is in **kg/ha** in this release. |
| **World Bank WDI** (`DSET-019`) | `https://api.worldbank.org/v2/country/NGA/indicator/<CODE>?format=json&date=1991:2023`, plus indicator metadata at `https://api.worldbank.org/v2/indicator/<CODE>?format=json`. CC BY 4.0. |
| **Recorded fixtures** (for tests only) | [`resources/fixtures/power_kaduna_2020.json`](resources/fixtures/power_kaduna_2020.json): a real POWER response for 10.52°N 7.44°E, 2020 (a leap year), recorded 2026-11-08. [`resources/fixtures/faostat_nigeria_cereals_wide.csv`](resources/fixtures/faostat_nigeria_cereals_wide.csv): a real 12-row extract (Nigeria; maize, sorghum, millet and rice; production, area and yield) from the FAOSTAT bulk file dated 2025-12-23. Both are © their providers, redistributed under their open terms with attribution. |

**Known limitations (by design).** FAOSTAT is national, so any spatial weighting of climate is an assumption you must state. POWER is reanalysis and satellite data, not gauge observations. About 30 annual observations give wide intervals. That is a finding, not a failure.

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-02-data-acquisition-and-sourcing/DS-T2-004-rain-grain-and-granularity
python -m venv .venv && source .venv/bin/activate
pip install -r starter/requirements.txt
pytest -m contract          # passes: fixtures and API surface
pytest                      # the alignment tests fail until you implement climfuse
python acquire.py           # yours: downloads the raw data and writes MANIFEST.json (internet needed once)
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `climfuse/` plus your analysis modules | Tested alignment logic |
| 2 | `acquire.py` and `data/raw/MANIFEST.json` | Reproducible, verifiable acquisition |
| 3 | `run_designs.py` | Regenerates every result offline |
| 4 | `tests/test_member_*.py` (at least 10) | Pins your design choices |
| 5 | `ALIGNMENT_DECISIONS.md` (at most 1,000 words) | Every alignment decision, the alternatives considered, and the reason for the choice |
| 6 | `COMPARISON_REPORT.md` (at most 2,000 words plus tables and at most 4 figures), using the [template](submission-template/COMPARISON_REPORT.md) | Designs, estimates with intervals, the source audit, conclusion and threats to validity |
| 7 | `SOURCES.md` and `AI_USE_AND_SOURCES.md` | Attribution and integrity |
| 8 | A 10–20 minute defence | §K |

---

## G. Acceptance Criteria

1. ⚙ All provided tests and at least 10 member tests pass. The hidden suite checks `season_aggregate`, `weighted_mean`, `detrend` and the parsers against brute-force computations on re-seeded data.
2. ⚙/✍ `acquire.py` reruns without re-downloading, and `MANIFEST.json` hashes match the files.
3. ✍ `run_designs.py` regenerates every number in the report offline, in under 5 minutes on a laptop.
4. ✍ The baseline (R8) and at least four designs (R9) are reported with point estimates, 95 % bootstrap intervals and `n`. Each design differs from another by one documented decision.
5. ✍ The report states whether the conclusion's **sign and significance** are robust across designs. *Justification:* the decision the programme faces depends on whether the association is reliable, not on its size under one arbitrary design.
6. ✍ The source audit (R10) reaches an evidence-based verdict on each WDI series.
7. ✍ The flags are handled explicitly: the report gives the share of non-`A` values in the yield series used, and shows the effect of excluding them.
8. ✍ The conclusion matches the evidence. Claiming a robust effect when the intervals include zero across designs fails this criterion.

There are no accuracy thresholds, because there is no ground truth for the headline question. The criteria judge the robustness analysis, which is the competence being assessed.

---

## H. Evaluation Rubric

Full rubric: **[rubric.md](rubric.md)**.

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 15 |
| Implementation quality and reproducibility | 15 |
| Methodology: designs, baseline and uncertainty | 25 |
| Testing and evaluation | 10 |
| Source critique and licensing | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates ([placement framework](../../../../../../docs/placement-framework.md)).

---

## I. Submission Instructions

1. Create a **private** repository named `clbg-DS-T2-004-<your-github-username>`.
2. **Expected structure:**
   ```text
   clbg-DS-T2-004-<username>/
   ├── README.md                 # setup, acquire, run, in 15 lines or fewer
   ├── requirements.txt
   ├── climfuse/  (+ your modules)
   ├── acquire.py
   ├── run_designs.py
   ├── data/raw/MANIFEST.json    # raw files are git-ignored; small derived CSVs may be committed
   ├── data/derived/
   ├── tests/
   ├── ALIGNMENT_DECISIONS.md
   ├── COMPARISON_REPORT.md
   ├── SOURCES.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** The order in which you added designs should be visible.
4. **Submit** with an **Assessment submission** issue (repository URL and commit SHA), after adding the CLBG assessor account as a read-only collaborator.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Specification curve.** Run every combination of your decisions (for example 3 seasons × 3 spatial schemes × 2 detrend methods × 2 flag rules) and plot the sorted estimates with their intervals.
2. **Power analysis.** With about 30 years of data, how large a true correlation could you reliably detect? Simulate it.
3. **Out-of-sample early warning.** Using only data available by 30 September, does any design predict whether the next FAOSTAT yield is below trend better than chance? Use leave-one-year-out evaluation.
4. **Vintage check.** Compare the FAOSTAT bulk file with the WDI cereal-yield series year by year, and explain any differences.

---

## K. Assessment Integrity

**AI tools are permitted** for explanations and code review, but not to produce the analysis or the report. You must be able to defend every decision.

- Disclose AI use in `AI_USE_AND_SOURCES.md`. Undisclosed use discovered at defence is a breach.
- **Collaboration:** you may discuss general methods (for example "what is a block bootstrap?"). Don't share code, designs, results or text.
- **How understanding is verified (10–20 minutes):**
  1. **Justify:** "Why that season and those points? What would a farmer in Sokoto say about your June–September window?"
  2. **Debug:** the assessor gives you a POWER file with a two-week gap in August and asks what your pipeline produces for that year, and why.
  3. **Modify live:** add a design (for example "rice only", "April–October season" or "exclude the X-flagged years") and run it through `run_designs.py` during the defence.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | API acquisition, pandas time series, correlation and regression, confidence intervals. |
| **New skill developed** | Treating data *alignment* as a set of analytical decisions whose consequences must be measured, and reporting an honest robustness analysis rather than one convenient number. |
| **Decisions the member must make** | Points and weights; season windows; coverage rules; detrending; flag policy; which crops; which uncertainty method; what to conclude. |
| **What must be investigated independently** | Each source's documentation and flags; whether the WDI series are independent evidence; how sensitive the result is. |
| **Why it's interesting** | The answer is not known in advance and turns out to be fragile: the assessors' own designs flip the sign, and every interval includes zero. Two WDI series look useful and aren't: one is FAO-derived, and one is a constant long-run average. |
| **Evidence of competence** | Tested primitives that pass brute-force hidden checks; a reproducible design runner; a calibrated conclusion; live addition of a new design. |
| **Misconceptions exposed** | "More sources means more evidence." "A correlation of trending series means something." "Missing days are dry days." "An indicator with a value every year is observed every year." "No significant effect means no effect." |
| **Preparation for later work** | It leads into DS-T3-001 (constructing documented datasets), DS-05 and DS-07 inference work, and ML-09 climate and agriculture modelling, where alignment choices silently drive results. |

**Suggested approach** (optional): get `acquire.py` and the manifest working first. Implement and test the primitives. Reproduce the baseline. Then change one decision at a time, keeping a design log as you go. Write the report last, starting from the table of designs.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
