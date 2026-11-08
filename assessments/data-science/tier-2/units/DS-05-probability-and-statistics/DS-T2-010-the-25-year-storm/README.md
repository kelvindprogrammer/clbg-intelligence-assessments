# DS-T2-010: The 25-Year Storm

> *A drainage engineer needs one number, the 25-year one-day rainfall, to size a culvert that will stand for 40 years. You have 44 years of a gauge record with gaps, clustered storms and a climate that may not be standing still.*

![Format: Investigation](https://img.shields.io/badge/format-investigation-d73a49) ![Tier 2](https://img.shields.io/badge/tier-2-dbab09) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-010` |
| **Title** | The 25-Year Storm: Extreme Value Analysis of Rainfall for Drainage Design |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Engineering and Independent Problem-Solving |
| **Unit** | [DS-05: Probability and Statistics](../README.md) |
| **Format** | Investigation (secondary: Comparative) |
| **Difficulty** | Technical 3 · Mathematical 4 · Research 3 · Engineering 2 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 20–35 hours over 2–3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU or paid services. Internet only for the optional real-data path |
| **Recommended prerequisites** | Maximum likelihood estimation; quantiles; likelihood-ratio tests; the bootstrap (DS-T1-013 or equivalent); pandas time series |
| **Skills developed** | Block maxima and peaks-over-threshold; GEV and GPD fitting; return levels with honest uncertainty; threshold choice and declustering; non-stationary extremes; translating statistics into a design value under deep uncertainty |
| **Technologies** | Python 3.10+, NumPy, SciPy, pandas, matplotlib, pytest. Optional: `pyextremes` for a cross-check (not in the contract functions) |

---

## B. Problem Statement

A state drainage agency in a fast-growing coastal city in southern Nigeria is replacing culverts that flood every rainy season. The design standard says a culvert on a collector road must carry the **25-year one-day rainfall** (the daily total exceeded with probability 1/25 in any year), and a major outfall must carry the **100-year** value. The engineer has asked the data team for those numbers "with error bars", from the city's long-running rain gauge, and has one more question: *"The new culverts will be in service until about 2065. Does it matter that the rains seem heavier now than when I was a student?"*

You have the gauge's daily record from **1981 to 2024**, which is synthetic but realistic (see §E). It has the familiar features of a real West African record:

- two rainy seasons with a short "August break";
- storms that last two or three days, so very wet days come in clusters;
- **gauge outages**: whole months missing in a few years, sometimes during the peak of the rains;
- an open question about whether the extremes are **stationary**.

What makes it hard:

- **Extrapolation.** You must estimate an event rarer than most years in the record (100-year) from 44 years of data. The uncertainty is large, and the shape parameter, which controls tail heaviness, is the hardest thing to estimate and the most consequential.
- **Two families of methods.** Annual maxima with a GEV distribution use one value per year. Peaks over a threshold with a GPD use more data, but need a threshold and declustering, and give different answers if you choose badly.
- **Missing data bias.** A year with its wettest months missing still has a "maximum", and it's wrong in a predictable direction.
- **Non-stationarity is a decision, not just a test.** A trend that fails a significance test at 5% may still matter for a structure designed to last 40 years. A trend that passes may not extrapolate. Your report has to reason about this explicitly.
- **Library conventions.** Some popular libraries parameterise the GEV shape with the opposite sign to the hydrology literature. If you trust them blindly, you can turn a heavy tail into a bounded one.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Fit** GEV distributions to block maxima and GPD distributions to declustered threshold exceedances by maximum likelihood, with the sign convention handled correctly.
2. **Quantify uncertainty** in return levels with a method you justify (profile likelihood, bootstrap or delta method), and show by simulation that it is calibrated enough for the purpose.
3. **Make and defend analysis choices**: the data-coverage rule, the threshold, the declustering run length and the block size, showing how sensitive the answer is to each.
4. **Investigate non-stationarity** with a model (for example, a time-varying GEV location) and a test, and reason about what the evidence does and does not justify for a design lifetime.
5. **Communicate** a design recommendation to an engineer, including what is uncertain and why.

---

## D. Technical Requirements

### D.1 The contract (mandatory)

You design your package, but the tests import these functions from `eva/__init__.py` (see [`starter/eva/__init__.py`](starter/eva/__init__.py)). The shape parameter ξ is **positive for a heavy upper tail**.

| ID | Requirement |
|---|---|
| **R1** | `annual_maxima(df, min_coverage)` returns calendar-year maxima with their data coverage, dropping years below the coverage threshold. |
| **R2** | `fit_gev(x)` (MLE) and `gev_return_level(params, T)`, including the ξ → 0 limit. **Derive** the return-level formula from the GEV distribution function in your report. |
| **R3** | `return_level_ci(x, T, level)`: an interval method of your choice for the stationary T-year level. Justify the choice and check its coverage by simulation for samples of about this record's length (R7). |
| **R4** | `decluster_runs`, `fit_gpd` and `gpd_return_level`, as specified in the docstrings. **Derive** the POT return-level formula from the Poisson–GPD model. |

### D.2 The investigation (mandatory)

| ID | Requirement |
|---|---|
| **R5** | **Data audit.** Identify the outages and quantify their effect on annual maxima. Justify your coverage rule with evidence from the record, not just by convention. |
| **R6** | **Stationary estimates** of the 25-year and 100-year one-day rainfall from (a) GEV on annual maxima and (b) GPD on declustered exceedances, with intervals. Include diagnostic plots (probability, quantile and return-level plots) and a threshold-choice analysis for POT (mean residual life, plus parameter stability across thresholds). Explain any disagreement between (a) and (b). |
| **R7** | **Method check by simulation.** Simulate GEV samples of the record's length from parameters near your estimates, and report the bias and the RMSE of your 25- and 100-year estimates and the coverage of your intervals. Use this to say how much the record can support. |
| **R8** | **Non-stationarity.** Fit at least one non-stationary model (for example, GEV with a location that is linear in year, or POT with a time-varying rate or scale). Compare it with the stationary model by likelihood ratio and AIC, and report the implied 25-year level for 2024 and for 2065 with uncertainty. State what the power of your test is likely to be for a plausible trend, using simulation. |
| **R9** | **Design recommendation** (at most 600 words, for the engineer). A recommended 25-year and 100-year design value, the assumptions behind them, the uncertainty, and how you treated the possibility of a trend over the culverts' lifetime. Any safety margin must be argued, not asserted. |

### D.3 Engineering requirements (mandatory)

- At least **10 member tests** in `tests/test_member_*.py`, including a test that would catch a flipped shape sign, a test of the Gumbel limit, and a declustering edge case.
- One command regenerates every number and figure in the report, with stated seeds.
- If you use a library fit (for example `scipy.stats.genextreme`), wrap it and test the convention. The tests treat ξ > 0 as heavy-tailed.
- Dependencies: [`starter/requirements.txt`](starter/requirements.txt). An extra package such as `pyextremes` may appear only in an optional cross-check that `pytest` doesn't need.

### D.4 Responsibility

Design rainfall determines whether roads flood and homes are damaged. Underestimating it has costs that fall on residents; overestimating it spends public money that could build more drains elsewhere. In your report, state who bears the risk of each kind of error and how your recommendation balances them. Do not present your numbers as an official design standard: they are an analysis to inform one.

### D.5 Optional: the real-data path

Repeat R6 and R8 with NASA POWER daily precipitation (`PRECTOTCORR`, registry `DSET-140`) for the grid cell around your city (for example latitude 4.8, longitude 7.0 for Port Harcourt), from 1981 to the latest full year:

```text
https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR&community=AG&longitude=7.0&latitude=4.8&start=19810101&end=20241231&format=CSV
```

The data are free and need no API key. Cite them as the POWER [referencing page](https://power.larc.nasa.gov/docs/referencing/) asks, with the version and access date. **Critique** the comparison: POWER is a gridded reanalysis, not a gauge, and grid-cell averages smooth convective extremes. What does that imply for a design value? Don't commit the downloaded file. Store your download script instead.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/daily_rainfall.csv`](resources/data/daily_rainfall.csv): 16,071 daily rows (1981–2024), about 260 KB |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed from a stochastic weather model designed to resemble a southern Nigerian coastal climate (bimodal rainy season, clustered storms, gauge outages). The generating model, including whether its extremes change over time, is held in the assessor kit because it is the answer key. It is not a record of any real gauge. |
| **Licence** | CC BY 4.0 (same as this repository's content). The optional real data (`DSET-140`) are free to access and must be cited as their provider requests. |
| **Integrity** | SHA-256 `09e0e2ce3fa3e89c057b48742bfeb224908d81b105ab0ca04cb97bb919b098ae`. Checked by the contract test. |

| Column | Meaning |
|---|---|
| `date` | ISO date |
| `rain_mm` | Daily rainfall total in millimetres, to 0.1 mm. **Empty when the gauge was out of service.** |

**Known limitations (by design).** A single gauge. Daily totals only (no sub-daily intensities, which matter for real culvert design). The record is long enough to be useful and short enough to be humbling.

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-05-probability-and-statistics/DS-T2-010-the-25-year-storm
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract      # passes immediately
pytest                  # behavioural tests fail until you implement the contract
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `eva/` package (contract plus your modules) | The fitting and uncertainty tools |
| 2 | `tests/test_member_*.py` (≥ 10 tests) | Evidence that conventions and edge cases are right |
| 3 | `analysis.ipynb` **or** `analysis.py` | The audit, fits, diagnostics, simulation study and non-stationary analysis (R5–R8) |
| 4 | `figures/` | Diagnostic, threshold-choice and return-level plots |
| 5 | `REPORT.md` (at most 3,000 words plus figures, tables and derivations) | Methods, derivations, results with uncertainty, threats to validity |
| 6 | `DESIGN_NOTE.md` (≤ 600 words) | R9, for the engineer |
| 7 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 8 | A 10–20 minute live defence | Justify and debug (see §K) |

---

## G. Acceptance Criteria

Criteria marked ⚙ are checked automatically with the public and hidden test suites; criteria marked ✍ are checked by the assessor.

1. ⚙ The public tests and your own tests pass from a clean environment.
2. ⚙ `fit_gev` recovers the shape within ±0.04 on samples of 3,000 from heavy, near-Gumbel and bounded tails, using the ξ > 0 heavy-tail convention. *Justification:* the MLE standard error of ξ at n = 3,000 is about 0.013–0.015, so ±0.04 is roughly three standard errors; a flipped sign misses by 0.2–0.3.
3. ⚙ `gev_return_level` and `gpd_return_level` match the closed forms (and the ξ = 0 limits) to 1e-9.
4. ⚙ Your `return_level_ci` covers the true 25-year level in at least 20 of 25 simulated samples of 60 maxima. *Justification:* a calibrated 95% method fails this with probability below 1%. Methods with real coverage around 0.80 or lower (for example a naive normal interval on a skewed estimator) fail it most of the time. 25 replicates keeps the hidden test to about a minute.
5. ⚙ `annual_maxima` applies the coverage rule exactly, and declustering handles the edge cases (no exceedances, a cluster at the end, gaps).
6. ✍ The data audit (R5) quantifies the downward bias of incomplete years and justifies the coverage rule.
7. ✍ GEV and POT estimates (R6) come with intervals and diagnostics; the threshold is justified with stability plots; and the difference between methods is explained.
8. ✍ The simulation check (R7) reports bias, RMSE and coverage, and the report uses them to qualify the 100-year estimate.
9. ✍ The non-stationarity analysis (R8) reports the test result **and** its power, and reasons correctly about a non-significant trend over a 40-year design life, without claiming "no trend" from a non-significant test or presenting a fitted trend as a forecast.
10. ✍ The design note (R9) gives numbers with uncertainty, states its assumptions, and argues any margin.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 15 |
| Implementation quality | 10 |
| Methodology: choices, diagnostics and simulation checks | 25 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create a private repository** named `clbg-DS-T2-010-<your-github-username>` with your `eva/` package at the top level, plus `tests/`, `resources/` and `submission-template/`.
2. **Expected structure:**
   ```text
   clbg-DS-T2-010-<username>/
   ├── README.md                 # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── eva/
   ├── tests/
   ├── resources/                # unchanged (do not commit downloaded POWER data)
   ├── analysis.ipynb | analysis.py
   ├── figures/
   ├── REPORT.md
   ├── DESIGN_NOTE.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** The history is part of the evidence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue with the repository URL and commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Bayesian GEV.** Fit the GEV with a weakly informative prior on ξ (for example, a prior concentrating on −0.2 to 0.4 as regional hydrology suggests) and compare the posterior for the 100-year level with your frequentist interval.
2. **Regional frequency analysis.** Using POWER data for several neighbouring grid cells, explain how an index-flood approach could pool information, and what assumption it needs.
3. **Seasonality.** Fit separate extremes for the first and second rainy seasons. Is the annual-maximum model hiding a mixture?
4. **Design life risk.** Compute the probability that the "25-year" event is exceeded at least once during a 40-year service life, under the stationary and the trend models.

---

## K. Assessment Integrity

**AI tools are permitted** for learning and code review. **They must not do the assessment for you:** you must be able to explain each choice and change it live.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`. Disclosed, reasonable use is not penalised.
- **Cite** your methods sources, for example Coles, *An Introduction to Statistical Modeling of Extreme Values* (2001), chapters 3–6.
- **Collaboration:** you may discuss general ideas. You may not share code, numbers or report text.
- **How your understanding is verified (10–20 minutes):**
  1. derive the GEV return-level formula from F(z) = 1 − 1/T on paper;
  2. explain how your interval method behaves for the 100-year level, and why it is asymmetric;
  3. an **unseen modification**, such as a different threshold, a 3-day accumulation instead of 1-day, or dropping the last 10 years, which you rerun and interpret live;
  4. defend your treatment of the trend against "it wasn't significant, so ignore it" and against "always add 30% for climate change".

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | MLE, quantiles, likelihood-ratio tests, bootstrap, pandas time series. |
| **New skill developed** | Estimating rare-event magnitudes with defensible uncertainty, and making a decision when a trend is plausible but statistically weak. |
| **Decisions the member must make** | The coverage rule, block maxima against POT, threshold and run length, the interval method, the stationary or non-stationary model, and the design margin. |
| **What must be investigated independently** | Outage effects, threshold stability, the calibration of intervals at this record length, the power to detect trends. |
| **Why it's interesting** | Every answer is a range, and the member must still give the engineer a number. The record contains a trend that a 44-year sample can only weakly detect, which is exactly the situation real hydrologists face. |
| **Evidence of competence** | Correct conventions and formulas (automated), a calibrated interval method, sensitivity analyses, and a design note whose reasoning survives challenge at defence. |
| **Misconceptions exposed** | "A 25-year storm happens once every 25 years." "Not significant means no trend." "More decimal places mean more certainty." "All library GEV shapes share a sign." "Incomplete years are harmless." |
| **Preparation for later work** | Risk modelling in insurance and finance (tail risk), reliability engineering, climate-impact analytics, and any ML system whose failure mode lives in the tail. |

**Suggested approach** (optional): audit first; fit a stationary GEV and test your code on simulated data; build the simulation check (R7) early because it informs every later choice; do POT only once declustering is tested; leave the design note to the end.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
