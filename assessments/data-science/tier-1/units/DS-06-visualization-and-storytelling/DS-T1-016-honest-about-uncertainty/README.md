# DS-T1-016: Honest About Uncertainty

> *A farmer in Kano asks one question: "If I store my maize until March, will the price pay me back?" Build the charts that answer honestly, showing what is known, what is likely, and what could still go wrong.*

![Format: Implementation](https://img.shields.io/badge/format-implementation-0366d6) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-016` |
| **Title** | Honest About Uncertainty: Interval Plots, Quantile Dotplots and Fan Charts |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-06: Data Visualization and Storytelling](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 3 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 10–16 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Python and pandas basics; matplotlib (`plot`, `fill_between`, `scatter`, `hlines`); what a quantile and a confidence interval are; running `pytest` |
| **Skills developed** | Binomial intervals (Wald vs Wilson); quantiles and predictive distributions; quantile dotplots and frequency framing; fan charts with nested bands; detecting and repairing crossing quantiles; writing for a non-technical decision-maker |
| **Technologies** | Python 3.10+, numpy, scipy, pandas, matplotlib, pytest |

---

## B. Problem Statement

An agricultural extension programme sends a monthly **market bulletin** to extension officers in northern Nigeria, who read it to farmers' groups, often from a phone screen. Two numbers dominate every bulletin:

1. **Improved-seed adoption by state**, from a small farmer survey. Some states were surveyed properly (400 farmers in Kano), and some barely (4 farmers in Oyo, 6 in Ekiti).
2. **The maize price outlook** for the next six months in four markets, from a forecasting model that outputs **quantiles**, plus 4,000 predictive draws of the March price per market.

Last season's bulletin printed adoption as a bar chart of percentages ("Ekiti: 0%!"), and printed the price forecast as a single line. A farmers' group in Dawanau stored maize on the strength of that line, and prices came in below it. The forecast was not wrong: the price fell inside its 80% interval. **The chart was wrong**, because it hid the interval.

You will build `uncertainty_viz`, a small, tested library that turns estimates and forecasts into displays that show uncertainty honestly. You will then use it to write a one-page bulletin answering the farmer's question.

**What makes it hard.**
- **Small samples break the textbook interval.** The Wald interval *p̂ ± z·√(p̂(1−p̂)/n)* gives Ekiti (0 of 6) an interval of exactly [0, 0], which claims certainty from six farmers. It also gives Katsina (1 of 4) a *negative* lower bound. You must implement the **Wilson** interval and be able to explain why it behaves better.
- **Probabilities are hard to read and frequencies are easier.** "19.4% chance" is abstract, while "4 in 20" can be pointed at. A **quantile dotplot** (Kay et al., 2016; Fernandes et al., 2018) shows 20 equally likely outcomes as 20 dots. But naive binning can draw a dot that is *above* the break-even price on the *wrong side* of the break-even line, so your bins must be aligned to the decision threshold.
- **Quantiles from quick models can cross.** The Bodija forecast was fitted one quantile at a time, and in three months its 75th percentile is *above* its 90th. A fan chart drawn from it would show bands that fold over themselves. Your code must **refuse** to draw it until the table is explicitly repaired.

**Known facts from the programme:**
- The Dawanau farmer's break-even price for storing until March is the November 2026 price plus **₦3,500 per 100 kg bag** for storage, fumigation and losses. This is an illustrative figure for the exercise, not a published cost.
- All data in this assessment is **synthetic**. It is realistic in shape and has no relation to real prices or surveys.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** the Wilson score interval and explain, with the survey's own numbers, where and why the Wald interval fails.
2. **Compute** quantile dots and a stacked-dot layout whose bins respect a decision threshold, and state an exceedance probability as a frequency.
3. **Detect** incoherent (crossing) quantile forecasts and repair them by monotone rearrangement, without ever doing so silently.
4. **Build** interval plots, quantile dotplots and fan charts as matplotlib Figures whose geometry provably matches the numbers (checked by tests that inspect the artists).
5. **Choose and justify** which display best supports a specific decision, and write a bulletin a non-specialist can act on.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `uncertainty_viz` package in [`starter/uncertainty_viz/`](starter/uncertainty_viz/). `data.py`, `QuantileCrossingError`, `level_columns` and `quantile_columns` are provided. The signatures are fixed because the tests import them.

| ID | Requirement |
|---|---|
| **R1** | `wilson_interval(k, n, level=0.95) -> (lo, hi)` returns the Wilson score interval with *z* = Φ⁻¹(½ + level/2), clipped to [0, 1]. It raises `ValueError` unless `0 ≤ k ≤ n`, `n > 0` and `0 < level < 1`. |
| **R2** | `quantile_dots(samples, n_dots=20) -> ndarray` returns the sample quantiles at probabilities `(i + 0.5) / n_dots`, using numpy's default linear method. It raises `ValueError` for `n_dots < 1`, empty input or any NaN. |
| **R3** | `stack_dots(values, bin_width, origin=0.0) -> (x, y)`. Bins are `[origin + j·w, origin + (j+1)·w)`. Values are processed in sorted order, `x` is the bin centre and `y` is the 0-based stack height within the bin. It raises `ValueError` for `bin_width ≤ 0`. |
| **R4** | `prob_exceed(samples, threshold) -> float` returns the share of samples **strictly** greater than the threshold. |
| **R5** | `check_quantiles(df) -> list[int]` returns the 0-based positional rows whose `q<prob>` values decrease anywhere as the probability increases. Columns may arrive in any order, so use `quantile_columns`. `repair_quantiles(df) -> DataFrame` returns a **new** frame with each row's quantile values sorted (monotone rearrangement), leaving other columns untouched. |
| **R6** | `interval_plot(survey, level=0.95, *, title, source) -> Figure` draws one row per state with a point at *k/n* and a horizontal Wilson interval segment (drawn with `hlines`, `errorbar` or 2-point lines), rows ordered by estimate with the **largest at the top** (ties broken alphabetically), tick labels in the form `"<state> (n=<n>)"`, x-limits exactly (0, 1), an x-label, and a text starting `Source:`. |
| **R7** | `quantile_dotplot(samples, n_dots=20, *, threshold=None, bin_width=None, title, xlabel, source) -> Figure` draws exactly `n_dots` dots (scatter markers or `Circle` patches) laid out with `stack_dots(quantile_dots(...))`. When `threshold` is given: bins use `origin=threshold`, so **every dot whose value exceeds the threshold is drawn to its right and no other dot is**; a vertical line is drawn at the threshold; and a text contains `"<k> in <n_dots>"`, where *k* is the number of dots above the threshold. When `bin_width` is `None`, choose a sensible default and justify it in your bulletin. The figure also needs an x-label and a `Source:` text. |
| **R8** | `fan_chart(history, forecast, levels=(0.5, 0.8, 0.95), *, time_col, value_col, title, ylabel, source) -> Figure` draws the observed history as a line, one filled band (`fill_between`) per level spanning exactly the `level_columns(level)` quantiles, the `q0.5` median as a line, and **wider bands lighter** than narrower ones (as composited over white). The legend labels each band with its percentage (e.g. `"80%"`). It raises `QuantileCrossingError` if `check_quantiles(forecast)` is non-empty, and `ValueError` if a needed quantile column (or `q0.5`) is missing. |
| **R9** | `make_figures.py` at your repository root regenerates every figure in your bulletin into `figures/` from `resources/data/`. |

### D.2 Engineering requirements (mandatory)

- **No silent repair.** Nothing may call `repair_quantiles` implicitly. The bulletin must say that the Bodija forecast was repaired and what that means for its reliability.
- **Inputs are read-only.** No function mutates a DataFrame it receives.
- **Tests.** Keep the provided tests passing and add **at least 10 tests of your own** in `tests/test_member_*.py`, including Wilson edge cases (k = 0, k = n, n = 1), a dot exactly on a bin edge, and a crossing table whose columns arrive out of order.
- **Dependencies.** Only those in [`starter/requirements.txt`](starter/requirements.txt).

### D.3 Responsible communication

The bulletin will be read aloud to people deciding whether to store their harvest, so a misleading chart costs real money:
- Never print a point forecast without its interval.
- State the source and the date of the data, and say plainly that the forecast is a model, not a promise.
- Do not recommend a decision. Show the chance of each outcome, and leave the farmer's risk tolerance to the farmer. One paragraph must explain why this boundary matters.

### D.4 Optional enhancements (not required for full marks)

- A **hypothetical outcome plot** (HOP) animation of the March price, saved as a GIF.
- A colour-vision-deficiency check of your band colours.
- An `interval_plot` option that greys out states with `n < 10` and says why.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | [`resources/data/`](resources/data/): `seed_adoption_survey.csv` (14 states), `maize_price_history.csv` (4 markets × 35 months), `maize_price_forecast.csv` (4 markets × 6 months × 7 quantiles), `march_price_samples.csv` (4 markets × 4,000 predictive draws). About 425 KB in total. |
| **Provenance** | **Synthetic**, generated by [`resources/generate_data.py`](resources/generate_data.py) with `--seed 2026`. Market names are real places, used only for realism, and every number is invented. The crossing quantiles in one market and the tiny state samples are deliberate. |
| **Licence** | CC BY 4.0 (data and generator, same as this repository) |
| **Integrity** | The contract tests check a SHA-256 hash of each file and that the generator reproduces them byte-for-byte. A `.gitattributes` file prevents line-ending rewrites. |

**Schemas.** Survey: `state, farmers_surveyed, adopted`. History: `market, month (YYYY-MM), price_ngn_per_100kg`. Forecast: `market, month, q0.025, q0.1, q0.25, q0.5, q0.75, q0.9, q0.975`. Samples: `market, draw, price_ngn_per_100kg`.

**Known limitations (by design).** The predictive draws and the quantile table come from slightly different model runs, so the dotplot's and the fan chart's March ranges do not match exactly. Noticing and explaining this is credited (rubric dimension 7). Survey sizes are fixed per state, and there is no design weighting.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-06-visualization-and-storytelling/DS-T1-016-honest-about-uncertainty
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract       # passes immediately
pytest                   # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `uncertainty_viz/` package (the completed starter) | The tested library: the core technical evidence |
| 2 | `tests/test_member_*.py` (≥ 10 tests) | Pins edge cases: small samples, bin edges, crossing tables |
| 3 | `make_figures.py` and `figures/*.png` | Reproducible figures for the bulletin |
| 4 | `MARKET_BULLETIN.md` (one page: at most 450 words plus 3 figures), using the [template](submission-template/MARKET_BULLETIN.md) | Answers the Dawanau farmer's question for a non-technical reader |
| 5 | `DESIGN_NOTE.md` (at most 900 words), using the [template](submission-template/DESIGN_NOTE.md) | Wald vs Wilson on the real survey; why each display suits or doesn't suit the decision; the bin-width default; the crossing repair |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 7 | A 5–10 minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

⚙ = automated (public and hidden suites), ✍ = assessor.

1. ⚙ `pytest` passes all provided and member tests in a clean environment from your `requirements.txt`.
2. ⚙ **Wilson** matches an independent implementation to within 1e-9 over a grid of *n* ∈ {1, 2, 5, 13, 50, 1000}, edge values of *k* and levels {0.8, 0.9, 0.95, 0.99}. *Justification:* the formula is closed-form, so any larger error is a bug, not rounding.
3. ⚙ **Dots and stacks** match the R2 and R3 definitions exactly on unseen samples and origins.
4. ⚙ **Interval plot** geometry matches the Wilson intervals (to 1e-6) and the estimates on survey data regenerated with unseen seeds, at an unseen level (90%).
5. ⚙ **Threshold alignment.** For every market, three unseen dot counts (10, 20, 50) and unseen thresholds, exactly the dots above the threshold are drawn right of it, and the frequency text is present.
6. ⚙ **Fan charts** for every market on regenerated data: crossing tables raise `QuantileCrossingError`, repaired tables draw three bands spanning exactly their quantiles, wider bands are lighter, and unseen levels (60%, 90%) work.
7. ✍ The bulletin states the March exceedance chance for Dawanau as a frequency (the official data gives **4 in 20**), shows the interval around every forecast, flags that the Bodija forecast was repaired, and makes no recommendation.
8. ✍ The design note uses the survey's own rows (Ekiti 0/6, Katsina 1/4, Taraba 5/5) to show the Wald failures, and justifies the default `bin_width`.
9. ✍ `make_figures.py` regenerates the committed figures exactly.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 15 |
| Methodology: display choice for the decision | 10 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 5 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 10 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates in the rubric. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create a private repository** named `clbg-DS-T1-016-<your-github-username>` from this assessment's `starter/`, `tests/`, `resources/`, `submission-template/` and `.gitattributes`.
2. **Expected structure:**
   ```text
   clbg-DS-T1-016-<username>/
   ├── README.md               # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── uncertainty_viz/
   ├── tests/                  # provided + test_member_*.py
   ├── resources/              # unchanged
   ├── make_figures.py
   ├── figures/*.png
   ├── MARKET_BULLETIN.md
   ├── DESIGN_NOTE.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** The history is part of the evidence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue with the repository URL and commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Coverage experiment.** Simulate 10,000 surveys at *n* = 6 and *p* = 0.1 and compare the actual coverage of the Wald, Wilson and Clopper–Pearson intervals. Plot coverage against *p*.
2. **Hypothetical outcome plots.** Animate 20 draws of the March price and argue whether HOPs or dotplots suit a group reading off one phone.
3. **Read-aloud test.** Read your bulletin to two people outside data science and record what they think "4 in 20" means. Revise and report what changed.
4. **Calibration of the fan.** Using the history, back-test a naive seasonal forecast and check whether its 80% bands contain about 80% of outcomes.

---

## K. Assessment Integrity

**AI tools are permitted** for learning, for example to explain the Wilson derivation or matplotlib's `fill_between`. **They may not do the assessment for you.** You must be able to explain and modify every line.

- **Disclose** all AI use in `AI_USE_AND_SOURCES.md`: tool, purpose, example prompt, and how you verified the output.
- **Cite** the sources of the formulas you implemented (for example Wilson 1927, Agresti & Coull 1998, Kay et al. 2016).
- **Collaboration:** you may discuss general ideas with other members, but not share code, figures or text.
- **How your understanding is verified.** In the defence, the assessor will:
  1. ask you to compute (roughly, on paper) why the Wald interval for 0/6 has zero width, and what Wilson does instead;
  2. change the threshold or `n_dots` live and ask you to predict the frequency text before running it;
  3. give you a new quantile table with a crossing in an unexpected column and ask you to show the check catching it, then explain what repairing it can and cannot fix.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Proportions, quantiles, the idea of an interval; basic matplotlib. |
| **New skill developed** | Designing a display around a decision, and verifying that its geometry encodes the numbers exactly. |
| **Decisions the member must make** | The default bin width; colour and alpha for nested bands; how to label sample sizes; which display leads the bulletin; how to word uncertainty without recommending. |
| **What must be investigated independently** | Why Wald fails at the boundary; how frequency framing aids comprehension; what monotone rearrangement does and doesn't fix. |
| **Why it's interesting** | Three hidden traps (zero-width intervals, threshold-straddling bins, crossing quantiles) that each produce a confident-looking but wrong chart. |
| **Evidence of competence** | Exact geometric checks on regenerated data; a bulletin that a farmer could use; a defence in which the member predicts outputs before running them. |
| **Misconceptions exposed** | "p̂ ± 1.96·SE always works." "A forecast is a line." "Binning is cosmetic." "If the model outputs it, the quantiles are coherent." "Showing uncertainty confuses people." |
| **Preparation for later work** | It leads into DS-T1-015 (honest encodings), DS-10 forecasting and backtesting, and the DS-T3 perception experiments that test which displays people actually read correctly. |

**Suggested approach** (optional): implement R1–R5 with tests first, then R8, R6 and R7, checking each figure with the helpers in [`tests/figinspect.py`](tests/figinspect.py). Draft the bulletin last, and read it aloud before you submit.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
