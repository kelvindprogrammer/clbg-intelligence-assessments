# DS-T1-003: Rain Onset at Scale

> *A rainfall-onset analysis that farmers' advisory services depend on takes hours to run. Make it fast, using NumPy and pandas, without changing a single answer, and prove both claims.*

![Format: Optimization](https://img.shields.io/badge/format-optimization-e36209) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-003` |
| **Title** | Rain Onset at Scale: Vectorising an Agro-Climate Pipeline Without Changing Its Answers |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-01: Python and Data Wrangling](../README.md) |
| **Format** | Optimization (secondary: Implementation) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 2 (each out of 5) |
| **Estimated time** | 10–18 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | A laptop with 8 GB RAM for the full benchmark (4 GB is enough for everything else). No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | NumPy arrays, boolean masks and `np.cumsum`; pandas `groupby` and `merge`; dates in pandas. Recommended: [DS-T1-001](../DS-T1-001-the-price-watch-bulletin/README.md) |
| **Skills developed** | Profiling with `cProfile`; vectorisation with NumPy; cumulative-sum window tricks; run-length encoding; complete-calendar reindexing; equivalence testing against an oracle; NaN semantics in aggregation; a sound benchmarking protocol |
| **Technologies** | Python 3.10+, NumPy, pandas, pytest, `cProfile`, `time.perf_counter`, `tracemalloc` |

---

## B. Problem Statement

In much of Nigeria, farmers decide when to plant by watching for the **onset of the rains**. Plant too early, on a "false start", and a dry spell kills the seedlings. Agricultural advisory services therefore compute an agronomic onset date for every rain gauge and every year. A common family of definitions, used here in simplified form, requires a few days of substantial rain *and* no long dry spell in the following month. The same pipeline also produces monthly totals, the longest dry spell of the season, and monthly anomalies against each station's own climate.

A (fictional) state agro-met unit has a pipeline, [`rainfall/legacy.py`](starter/rainfall/legacy.py), written for a handful of stations. It is **correct**: it has been checked by hand against gauge records, and its answers are trusted. But it is written as nested Python loops over stations, years and days, and the unit now has 400 stations with 30 years of records each, which is more than 4 million rows. The legacy code would take many hours. One function, `standardised_anomalies`, gets slower faster than the data grows, so the full run would take longer still.

Your task is to write [`rainfall/fast.py`](starter/rainfall/fast.py): four functions with the **same signatures and the same answers** as the legacy ones, built from NumPy and pandas operations rather than Python loops over days. Then **prove** two things:

1. **The answers did not change.** For any valid input, not just the sample, the fast functions return what the legacy functions return, under the precise equivalence rule in §D.1.
2. **It is actually faster,** by an amount you have measured with a fair, reproducible protocol.

**What makes it hard.** Vectorising the easy parts takes an afternoon. The difficulty is in the details that the legacy code handles implicitly, and a vectorised version silently gets wrong:

- **An absent day is not the same as no rain.** The record has gaps: days with a blank reading, and days with no row at all. The legacy code treats both as missing. A vectorised "next three days" that looks at the next three *rows* is wrong whenever a row is absent.
- **`sum()` skips NaN.** pandas' `groupby(...).sum()` happily returns a monthly total for a month with missing days. The legacy rule says that total must be NaN.
- **Forward-looking windows.** The onset rule looks *forward* 30 days for a 7-day dry run. That is a nested condition that does not map onto a single `rolling()` call.
- **Boundaries:** leap years, stations that start in July, years with no onset, a look-ahead that runs past the end of the record, and dtypes (`Int64` with `<NA>`, `datetime64[ns]` with `NaT`).

Speed you cannot trust is worthless here: an onset date one week wrong is a planting recommendation one week wrong.

**Known facts** (the definitions are in the legacy docstrings and code, which are the specification):

- A **wet day** has at least 1 mm of rain. The **onset** is the first day from 1 March to 31 July with at least 20 mm over three days, starting on a wet day, and no run of 7 or more non-wet-or-missing days in the next 30 days, provided the record extends 30 days beyond it.
- The **dry-spell season** is 1 April to 31 October. A missing day ends a dry run.
- The **climatology** for a station and month needs at least 3 years with complete totals.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Profile** slow Python code and identify where the time goes, with evidence.
2. **Re-express loop logic as array operations:** masks, cumulative sums, run-length encoding, grouped reductions and complete-calendar reindexing.
3. **Preserve exact semantics** while doing so, including NaN handling, absent rows, boundaries and dtypes.
4. **Test equivalence against an oracle** on adversarial, randomly generated inputs as well as hand-built edge cases.
5. **Benchmark fairly:** warm-up, repeats, medians and spread, input sizes, environment recorded, and memory measured.
6. **Explain the scaling behaviour** of both versions, including why one legacy function is super-linear.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

**Equivalence rule.** For an input `df` that follows the input contract in [`legacy.py`](starter/rainfall/legacy.py) (any row order, absent days allowed, at most one row per station and date), `fast.f(df)` is **equivalent** to `legacy.f(df)` when it has the same columns in the same order, the same number of rows in the same order, the same dtypes, identical integer, date and missing-value positions, and float values within an absolute difference of `1e-9`. *Justification:* the order of floating-point additions can legitimately differ between a loop and a vectorised sum. At these magnitudes (thousands of mm), that produces differences around `1e-12`. Anything above `1e-9` is a logic error, not rounding. This is the rule in `tests/conftest.py::assert_equivalent`.

| ID | Requirement |
|---|---|
| **R1** | `fast.monthly_totals(df)` is equivalent to `legacy.monthly_totals(df)`. |
| **R2** | `fast.longest_dry_spell(df)` is equivalent to `legacy.longest_dry_spell(df)`. |
| **R3** | `fast.onset_dates(df)` is equivalent to `legacy.onset_dates(df)`. |
| **R4** | `fast.standardised_anomalies(df)` is equivalent to `legacy.standardised_anomalies(df)`. |
| **R5** | **No Python loop over rows, days or station-years** in `fast.py`. That includes `iterrows`, `itertuples`, `apply` with a Python function per group or row, and `for` loops over stations. Loops over a handful of constants (for example, the four functions in a benchmark) are fine. `fast.py` must not call `legacy.py` functions. |
| **R6** | `profile_legacy.py` runs `cProfile` on each legacy function using the committed sample and writes the top 15 entries by cumulative time to `outputs/profile_legacy.txt`. |
| **R7** | `bench.py` implements the protocol in §D.2 and writes `outputs/benchmark.csv` with the columns `function, implementation, dataset, rows, repeats, median_s, p25_s, p75_s, peak_mem_mb`. |
| **R8** | `PERFORMANCE.md` (at most 1,200 words plus tables, from the [template](submission-template/PERFORMANCE.md)) reports the profile, the speed-ups, the scaling, and the equivalence evidence. |

### D.2 Benchmark protocol (mandatory)

- **Datasets:** `sample` (the committed file), `medium` (`--seed 2026 --stations 40 --years 12`, about 170,000 rows) and `full` (`--seed 2026 --stations 400 --years 30`, about 4.3 million rows), all made with the provided generator. Do not commit `medium` or `full`: they are regenerated.
- **Legacy:** run on `sample` (3 repeats) and `medium` (1 repeat). Do not run legacy on `full`. Instead, estimate its time from your scaling measurements, and say how you estimated it.
- **Fast:** run on all three datasets with 1 warm-up and at least 5 timed repeats. Report the median and the interquartile range.
- **Timing:** `time.perf_counter()` around the function call only, never around loading the file.
- **Memory:** peak traced memory with `tracemalloc` for one call of each fast function on `full`.
- **Environment:** record CPU, RAM, OS, and the Python, NumPy and pandas versions in `PERFORMANCE.md`, and close other heavy programs while you measure.

### D.3 Engineering requirements (mandatory)

- **Do not edit `legacy.py`.** It is the oracle.
- **Tests:** keep the provided tests passing, and add **at least 8 tests of your own** in `tests/test_member_*.py`. At least 3 must be hand-built edge cases you found by **reading the legacy code** (each test's docstring names the line or rule it pins down). At least one must be a randomised equivalence test that uses a different input generator from the provided `random_case`.
- **Dependencies:** NumPy, pandas and pytest only. No numba, Cython, Polars or multiprocessing. This assessment is about what vectorisation alone can do.
- **Readability:** every non-obvious array trick has a comment saying what it computes.

### D.4 Privacy and responsibility

The data is **synthetic**: no real gauge or station is described, so do not use the numbers to advise anyone. In `PERFORMANCE.md`, add two or three sentences on the responsibility that comes with optimising a decision-support pipeline: what evidence would you want before replacing the legacy code in production?

### D.5 Optional enhancements (not required for full marks)

- A chunked mode that processes stations in batches, to keep peak memory under 1 GB on `full`.
- A comparison of your onset function with a `numba`-compiled loop. This is outside the core rules, so report it separately.
- A sensitivity table: how onset dates shift if the 20 mm threshold becomes 15 mm or 25 mm. That is cheap now that the code is fast.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Sample** | [`resources/data/rainfall.csv`](resources/data/rainfall.csv) (51,354 rows, 24 stations, 2019–2024, about 1.1 MB) and [`resources/data/stations.csv`](resources/data/stations.csv) |
| **Generator** | [`resources/generate_rainfall.py`](resources/generate_rainfall.py), public and deterministic: `python resources/generate_rainfall.py --out DIR --seed INT [--stations N --years Y]` |
| **Provenance** | **Synthetic.** A two-state Markov chain for wet and dry days with gamma-distributed amounts, and a wet season that shortens from south to north, plus deliberate damage: blank readings, absent rows, multi-week outages, mid-year starts and shuffled row order. It is not calibrated to any real station. |
| **Licence** | CC BY 4.0, the same as this repository's content |
| **Integrity** | SHA-256 `rainfall.csv` `f1f5921badfd4a234ef396709ce08c74f5f3a05af132f75a196573a3fd0a986a`; `stations.csv` `e0836c40167e96050159d98cf5b50482bf195d2517df50df75b8450af39d9580`. A contract test also checks that the generator reproduces the sample exactly. |

**Schema** (`rainfall.csv`): `station_id` (str), `date` (`YYYY-MM-DD`), `rain_mm` (one decimal place, blank when the reading is missing). Use the provided `load_rainfall()`, which returns `datetime64[ns]` dates and `float64` rain with NaN for blanks.

**Known limitations (by design).** The onset definition is a simplified teaching version of agronomic definitions used in West African agro-climatology. The legacy code is the authority for this assessment, even where you would design the rule differently. If you think a rule is questionable, say so in `PERFORMANCE.md`, but do not change it.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-01-python-and-data-wrangling/DS-T1-003-rain-onset-at-scale
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract                     # passes immediately
pytest                                  # requirement tests fail until fast.py is written
python resources/generate_rainfall.py --out data_medium --seed 2026 --stations 40 --years 12
python resources/generate_rainfall.py --out data_full --seed 2026 --stations 400 --years 30   # ~90 MB, ~30 s
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `rainfall/fast.py` | The optimised implementation: the core evidence |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Shows that the equivalence claim is tested beyond the sample |
| 3 | `profile_legacy.py` and `outputs/profile_legacy.txt` | Shows that optimisation was driven by measurement |
| 4 | `bench.py` and `outputs/benchmark.csv` | A reproducible speed and memory measurement |
| 5 | `PERFORMANCE.md`, from the [template](submission-template/PERFORMANCE.md) | Explains the bottlenecks, techniques, results and scaling |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 7 | A 5–10 minute live defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. ⚙ marks automated checks, and ✍ marks checks done by hand.

1. ⚙ `pytest` passes all provided and member tests in a clean environment.
2. ⚙ **Equivalence on unseen inputs.** All four functions are equivalent to legacy (§D.1) on the hidden suite: 25 freshly seeded adversarial records per function (years from 1896 to 2029, very wet and very dry regimes, heavy missingness, partial years), plus targeted edge cases. *Justification:* the legacy code is the trusted reference, so a single non-equivalent output means the optimisation changed an answer.
3. ⚙ **Speed on a medium benchmark** regenerated with a seed you have not seen (40 stations × 12 years): each of R1–R3 is at least **4×** faster than legacy, and R4 is at least **10×** faster. *Justification:* the reference reaches about 10–11× on R1–R3 and about 33× on R4 at this size, on a mid-range laptop. The bars sit at roughly 40% and 30% of that, which leaves room for slower hardware, timing noise and different valid designs. They cannot be met while a Python-level loop over days remains.
4. ✍ **Full-scale run.** On `full` (about 4.3 million rows), all four fast functions together complete in **under 120 seconds**, with peak traced memory **under 2 GB** for each call, as reported in `benchmark.csv`. *Justification:* the reference takes about 18 seconds and peaks at about 0.6 GB. 120 seconds allows a laptop several times slower, and 2 GB keeps the job comfortable on an 8 GB machine running an operating system and a browser.
5. ✍ No Python loops over rows, days or station-years in `fast.py` (R5), checked by reading the code.
6. ✍ `outputs/profile_legacy.txt` and `outputs/benchmark.csv` regenerate from the scripts, and `PERFORMANCE.md` quotes them accurately.
7. ✍ `PERFORMANCE.md` explains *why* `standardised_anomalies` scales worse than linearly in the legacy code, using profile evidence.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness (equivalence) | 25 |
| Implementation quality | 15 |
| Methodology: profile, optimise, verify | 15 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 5 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own repository.** Copy this assessment's `starter/` contents, `tests/`, `resources/` and `submission-template/` into a new **private** GitHub repository named `clbg-DS-T1-003-<your-github-username>`.
2. **Expected structure:**
   ```text
   clbg-DS-T1-003-<username>/
   ├── README.md                  # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── rainfall/                  # legacy.py unchanged, fast.py yours
   ├── tests/                     # provided tests + your test_member_*.py
   ├── resources/                 # unchanged; do NOT commit data_medium/ or data_full/
   ├── profile_legacy.py
   ├── bench.py
   ├── outputs/profile_legacy.txt
   ├── outputs/benchmark.csv
   ├── PERFORMANCE.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work:** one function at a time, with its equivalence tests. Your history should show the profiling before the optimising.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator, then filing a submission issue in the CLBG assessments repository with the **Assessment submission** template. Include the repository URL and the commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback, but never replace the core requirements.

1. **Memory diet.** Bring peak memory on `full` below 1 GB without losing more than 25% of the speed, and explain the trade-off.
2. **Where is the floor?** Estimate the time to simply *read* every value once (for example, `np.sum` over the rain column), and express each function's time as a multiple of it. Which function has most room left?
3. **Second opinion.** Write an independent implementation of the onset rule in a different style (for example, with `sliding_window_view`) and use the three implementations to cross-check each other.
4. **Onset climatology.** Using `full`, map the mean onset day of year against latitude, and comment on whether the synthetic gradient behaves as the generator intends.

---

## K. Assessment Integrity

**AI tools are permitted for learning:** to explain `np.cumsum` tricks, how `tracemalloc` works, or why `groupby().sum()` returns 0 for an all-NaN group. **They must not write `fast.py` for you.** You must be able to derive every array trick in your code on a whiteboard.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`: which tool, what for, and an example prompt. Undisclosed use that becomes apparent at the defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** any technique adapted from a source (for example, a Stack Overflow answer on run-length encoding), with a link.
- **Collaboration:** you may discuss general vectorisation techniques with other members. You may not share code, tests or benchmark results.
- **How your understanding is verified.** In the 5–10 minute defence, the assessor will:
  1. ask you to explain, on a 10-day example drawn on paper, how your onset code decides that a candidate day fails the dry-spell condition;
  2. show you a failing equivalence case they have built and ask you to diagnose it;
  3. ask for a **live change:** for example, "the dry-spell rule becomes 10 days in the next 40", or "missing days in the look-ahead should now count as wet". Make it in both the legacy and fast versions, and keep them equivalent.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | NumPy arrays and masks, pandas `groupby`, basic dates, `pytest`. |
| **New skill developed** | Optimising *safely*: measure first, transform loops into array operations, and prove equivalence against an oracle on adversarial inputs, then measure again fairly. |
| **Decisions the member must make** | How to represent absent days (a complete calendar or something else). How to express forward-looking windows. Which pandas operations silently change NaN semantics. How to design a benchmark that is fair to both versions. |
| **What must be investigated independently** | Where the legacy time actually goes (the profile), and every implicit rule in the legacy code that a vectorised version must reproduce. |
| **Why it's interesting** | The easy speed-up is easy to get and easy to get wrong. The provided randomised harness catches errors the sample never shows, and the onset rule needs a genuinely clever array formulation. |
| **Evidence of competence** | Equivalence on hidden adversarial records; speed-ups on an unseen benchmark seed; a profile-driven write-up; live modification of both versions at the defence. |
| **Misconceptions exposed** | "Faster code with the same output on the sample is equivalent." "`groupby().sum()` respects missing data." "The next row is the next day." "One timing run is a benchmark." "Optimise first, profile later." |
| **Preparation for later work** | The Tier 2 out-of-core comparison (DS-T2-001) assumes this vectorisation fluency, as do data pipelines (DS-11) and any ML feature engineering on time series. |

**Suggested approach**, for members who want it (you may ignore it):

1. Profile all four legacy functions first, and read the output. Why is one of them so much worse?
2. Build a complete daily calendar per station-year once. Most of the difficulty disappears when "the next k days" becomes "the next k positions".
3. Learn one trick well: `c = np.cumsum(x)` makes the sum of any window `c[j] - c[i]` in one subtraction.
4. Get `monthly_totals` and `standardised_anomalies` equivalent first, then the dry spell (run lengths), then the onset.
5. Run `random_case` with hundreds of seeds before you trust anything.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
