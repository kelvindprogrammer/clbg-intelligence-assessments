# DS-T2-001: Feeder Hours, Out of Core

> *Eight million smart-meter readings, an 8 GB laptop, and a question regulators care about: did each feeder really get the hours of electricity its tariff band promises? Answer it with pandas, Polars and DuckDB, and find out which tool wins under which constraint.*

![Format: Comparative](https://img.shields.io/badge/format-comparative-1f6feb) ![Tier 2](https://img.shields.io/badge/tier-2-dbab09) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%208%20GB-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-001` |
| **Title** | Feeder Hours, Out of Core: Comparing pandas, Polars and DuckDB on Smart-Meter Data Under a Memory Budget |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Engineering and Independent Problem-Solving |
| **Unit** | [DS-01: Python and Data Wrangling](../README.md) |
| **Format** | Comparative (secondary: Optimization) |
| **Difficulty** | Technical 4 · Mathematical 2 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 3 (each out of 5) |
| **Estimated time** | 20–35 hours over 2–3 weeks |
| **Collaboration** | Individual |
| **Compute** | A laptop with 8 GB RAM and about 2 GB of free disk. No GPU, no paid services. Free path: a Google Colab or Kaggle CPU notebook (both have more than 8 GB RAM, so state the RAM you had) |
| **Recommended prerequisites** | Fluent pandas (`groupby`, `merge`, dtypes); basic SQL (`GROUP BY`, `JOIN`, `DISTINCT`); comfort with the command line. Recommended: [DS-T1-001](../../../../tier-1/units/DS-01-python-and-data-wrangling/DS-T1-001-the-price-watch-bulletin/README.md) and [DS-T1-003](../../../../tier-1/units/DS-01-python-and-data-wrangling/DS-T1-003-rain-onset-at-scale/README.md) |
| **Skills developed** | Out-of-core processing; streaming and partition-aware design; lazy query plans; embedded analytical SQL; memory measurement; benchmark design; validity of a derived metric; writing a recommendation under trade-offs |
| **Technologies** | Python 3.10+, pandas, Polars, DuckDB, psutil, pytest |

---

## B. Problem Statement

Nigeria's electricity tariffs are tied to **service bands**. A customer on a Band A feeder pays the highest tariff and is promised at least **20 hours** of supply a day. Bands B, C, D and E promise at least 16, 12, 8 and 4 hours. Whether feeders actually deliver their band is a live public question, and distribution companies (DisCos) are increasingly expected to show evidence from metering, not from operators' logbooks.

A (fictional) DisCo's analytics team has 30-minute interval readings from about 2,000 smart meters on 50 feeders for one quarter: **about 8.3 million rows**, 317 MB of CSV, in one file per day. They want a feeder-by-day table of **supply hours** and a compliance summary per band. Their analysts work on 8 GB laptops. The first attempt, "read everything into pandas", either runs out of memory or leaves the machine unusable for a minute. They have heard that Polars and DuckDB "solve this", and they want an evidence-based recommendation, not a blog post.

**Your job has three parts:**

1. **Implement the same computation four ways** behind one fixed interface: an in-memory pandas **baseline**, a **chunked** pandas pipeline, a **Polars** pipeline and a **DuckDB** pipeline. All four must produce *identical* results.
2. **Design and run a fair benchmark** of time and peak memory, across at least two data sizes and under a memory budget. Then **explain the results**: which engine wins, in which regime, and why.
3. **Answer the domain question and question the metric.** Which feeders met their band this quarter? How sensitive is that answer to the way "supplied" is defined, given that meters sometimes fail to report?

**What makes it hard.**

- **Duplicates cross file boundaries.** The meter head-end re-sends some readings, and some re-sends arrive in the **next day's file**. A pipeline that processes one file at a time and de-duplicates within each file silently double-counts energy. The partitioning you choose must respect where duplicates can be.
- **The fastest engine is not the leanest.** Out of the box, the most convenient plan in one library is several times faster than pandas but uses *more* memory than the baseline. Tuning, restructuring or a different storage format changes the picture. The "winner" depends on the constraint, which is exactly what your report must show.
- **Benchmarks lie easily:** a warm file cache, a single run, timing that leaves out I/O, memory measured with the wrong tool, or comparing engines that do not compute the same thing.
- **The metric has a validity problem.** "Supplied" is inferred from meters that report energy, and a meter that fails to communicate is not the same as a meter without power.

**Fixed definitions** (the contract, in [`meterflow/contract.py`](starter/meterflow/contract.py)):

- A **reading** is a row of `readings/*.csv` after removing **exact duplicates**: the same `meter_id`, `interval_start` and `kwh`, wherever they appear.
- A reading's **date** is the local (WAT) date of `interval_start`, *not* the file it arrived in.
- For a feeder and a 30-minute interval, a meter is **reporting** if it has a reading. The interval is **supplied** if at least one meter reports **and at least half** of the reporting meters have `kwh > 0`.
- **Feeder-day table:** one row per feeder and date with at least one reading. `reporting_meters` is the number of distinct meters with a reading that day, `energy_kwh` the sum of their readings, `supplied_intervals` the number of supplied intervals, and `supply_hours = supplied_intervals / 2`.
- **Compliance:** per feeder, the number of days, the mean supply hours, the share of days meeting the band minimum, and `compliant = mean supply hours ≥ band minimum`.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement one computation in three data-processing paradigms:** eager dataframes, lazy query plans and embedded SQL. Prove that they agree exactly.
2. **Design a partition-aware out-of-core pipeline** whose correctness does not depend on how the data happen to be split.
3. **Design and run a fair benchmark,** including isolation, repeats, sizes, memory measurement and environment, and quantify its uncertainty.
4. **Explain performance differences mechanistically:** parsing, string handling, hashing for `DISTINCT` and `n_unique`, parallelism, spilling and materialisation.
5. **Make and justify a recommendation** for a specific team and constraint, and say when it would change.
6. **Assess the validity of a derived metric** (supply hours) and its sensitivity to definitional choices and missing data.

---

## D. Technical Requirements

### D.1 Mandatory requirements

| ID | Requirement |
|---|---|
| **R1** | `meterflow.compute_feeder_daily(data_dir, engine, *, memory_limit_mb=None)` supports the four engines in `ENGINES`: `pandas_inmemory` (the baseline: read everything, then compute), `pandas_chunked` (never holds the whole dataset), `polars` and `duckdb`. It returns `FEEDER_DAILY_COLUMNS` with `FEEDER_DAILY_DTYPES`, sorted by `feeder_id` and `date`. All four engines return **identical** tables (energy within 1e-6). |
| **R2** | `memory_limit_mb` is honoured: through the library's own setting where one exists, and through your design (chunk size, window, partitioning) where it does not. You must document how each engine uses it. |
| **R3** | Correctness does not depend on file boundaries. A re-sent reading may appear in the same file or **the next day's file**, never later (a fact from the head-end vendor). Your chunked designs must use this fact explicitly, and say so in a comment. |
| **R4** | You may add a **storage-conversion step** (for example, CSV to Parquet, or to a DuckDB database). If you do, the benchmark reports its cost separately **and** amortised over a stated number of reruns, and correctness tests cover the converted path. |
| **R5** | `meterflow.compute_compliance(feeder_daily, feeders)` returns `COMPLIANCE_COLUMNS` exactly as its docstring specifies. |
| **R6** | A benchmark harness (`bench/`) that implements a protocol **you design and justify**, which must at least: run every engine in a **fresh process** for every repeat; use at least **3 repeats** and report the median and range; use at least **two data sizes** (one of them the benchmark set below); measure **wall time end-to-end from CSV** and **peak resident memory** (RSS, sampled; for example, with `psutil`); record the hardware and library versions; and write `outputs/benchmark.csv`. |
| **R7** | `outputs/compliance.csv` for the benchmark dataset, plus a **sensitivity analysis**: how the number of compliant feeders changes if "supplied" requires 40%, 50% or 60% of reporting meters, and if intervals with fewer than *k* reporting meters are treated as unknown rather than unsupplied. (Implement the variants as parameters of a separate analysis function. The contract function keeps the fixed definition.) |
| **R8** | `COMPARISON_REPORT.md` (at most 2,500 words plus tables and figures, from the [template](submission-template/COMPARISON_REPORT.md)): the protocol and its threats to validity, results with uncertainty, a mechanistic explanation, a **recommendation for the DisCo analytics team**, the compliance findings and the metric's limitations. |

### D.2 Engineering requirements (mandatory)

- **Modular code:** one module per engine, with shared definitions in one place. Each engine is a few dozen lines, not a copy-paste of the others.
- **Tests:** keep the provided tests passing, and add at least **8 tests of your own**. These include engine-equality tests on a generated dataset you choose, adversarial file-boundary cases, and a test of your conversion path if you have one.
- **Error handling:** clear errors for an unknown engine, a missing directory, malformed files and an impossible memory budget.
- **Reproducibility:** one command regenerates the benchmark dataset, and one command runs the whole benchmark.
- **Do not commit** the benchmark dataset or any converted copy of it.

### D.3 Privacy and responsibility

The data is **synthetic**: meter IDs are random, and no customer or real feeder is described. Real interval meter data is **personal data** under the Nigeria Data Protection Act 2023. Half-hourly consumption reveals when people are at home, asleep or away. In the report, add a short paragraph on how a DisCo should handle real AMI data in this kind of analysis: aggregate to the feeder as early as possible, minimise retention of meter-level data, control access, and decide whether supply-hour results can be published per feeder without exposing individuals on small feeders.

### D.4 Optional enhancements (not required for full marks)

- A fifth engine of your choice (for example, PyArrow `dataset` or Dask). Justify why it belongs in the comparison.
- A scaling curve across four or more sizes, with a fitted model of time against rows for each engine.
- A note on how results change on Linux compared with Windows, or on a different CPU count.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Sample** | [`resources/sample/`](resources/sample/): 60 meters, 4 feeders, 7 days (about 0.7 MB), with the expected outputs in [`resources/sample_expected/`](resources/sample_expected/) |
| **Benchmark set** | Generated locally: `python resources/generate_meters.py --out data_bench --seed 2026 --meters 2000 --days 90`. That gives about 8.3 million readings, about 317 MB and 90 files, in about 1–2 minutes |
| **Generator** | [`resources/generate_meters.py`](resources/generate_meters.py), public and deterministic (`--out DIR --seed INT [--meters N --days D]`) |
| **Provenance** | **Synthetic.** Feeders have a band and a true mean supply (some deliberately under-deliver), daily load-shedding blocks and occasional faults. Meters have a load profile, communication failures (single readings and whole days), zero readings with no load, and head-end re-sends (1%, about 40% of them in the next day's file). Rows are unsorted. |
| **Licence** | CC BY 4.0, the same as this repository's content |
| **Integrity** | The contract tests check a SHA-256 over the sample tree, and that the generator reproduces it byte for byte. |

**Files.** `readings/YYYY-MM-DD.csv`: `meter_id`, `interval_start` (ISO 8601 with `+01:00`), `kwh` (3 decimals). `meters.csv`: `meter_id`, `feeder_id`, `customer_class`. `feeders.csv`: `feeder_id`, `disco`, `band`.

**Known limitations (by design).** The band minimums are the public NERC band thresholds, but the feeders, DisCos and supply patterns are invented. Supply hours inferred from meters are an *estimate* of true supply. The generator knows the truth, and you do not. Part of R7 is reasoning about how the estimate could be biased.

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-01-python-and-data-wrangling/DS-T2-001-feeder-hours-out-of-core
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract
python resources/generate_meters.py --out data_bench --seed 2026 --meters 2000 --days 90
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `meterflow/` package (four engines plus compliance) | The implementations being compared |
| 2 | `tests/` (provided plus at least 8 of your own) | Evidence that the engines compute the same thing |
| 3 | `bench/` and `outputs/benchmark.csv` | A reproducible, fair measurement |
| 4 | `outputs/compliance.csv` and the sensitivity analysis code and output | The domain answer and its robustness |
| 5 | `COMPARISON_REPORT.md` | The recommendation, the evidence and the limitations |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 7 | A 10–20 minute live defence | Verifies understanding and judgement (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. ⚙ marks automated checks, and ✍ marks checks done by hand.

1. ⚙ `pytest` passes all provided and member tests in a clean environment.
2. ⚙ **Exact agreement.** On hidden, freshly generated datasets (new seeds, more meters, a year boundary) and on adversarial file-boundary cases, every engine's output equals the assessors' reference implementation, with and without a memory budget. *Justification:* a comparison of engines that compute different things is meaningless. Exact agreement is the precondition for every performance claim.
3. ✍ **Memory budget.** On the benchmark set with `memory_limit_mb=1500`, `pandas_chunked`, `polars` and `duckdb` each peak **at or below 2,000 MB RSS** in the assessor's rerun of your harness. *Justification:* an 8 GB laptop running an operating system, a browser and an IDE leaves roughly 2–3 GB for analysis, and the 500 MB margin above the budget allows for interpreter and library overhead. The reference meets this with all three engines (about 0.1, 0.7 and 1.6 GB). The baseline is exempt: showing that it cannot be kept within budget is part of the finding.
4. ✍ **Speed.** Your fastest engine within the budget is at least **3× faster** than your `pandas_inmemory` baseline on the benchmark set (median of at least 3 fresh-process runs). *Justification:* the reference reaches about 6× with a straightforward within-budget design. Below 3×, the recommendation to switch tools would not be worth the migration cost for this team.
5. ✍ The benchmark protocol meets every point in R6, and `outputs/benchmark.csv` regenerates within the run-to-run spread you report.
6. ✍ The report's recommendation follows from its evidence, names the regime in which it would change, and states at least three threats to the validity of the benchmark.
7. ✍ The sensitivity analysis (R7) is present, and the report interprets the direction of bias that missing meter reports introduce.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 15 |
| Methodology: benchmark design and fairness | 20 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 5 |
| Critical thinking: trade-offs, validity, recommendation | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own repository.** Copy `starter/` contents, `tests/`, `resources/` and `submission-template/` into a new **private** GitHub repository named `clbg-DS-T2-001-<your-github-username>`. Add `data_bench/` and any converted data to `.gitignore`.
2. **Expected structure:**
   ```text
   clbg-DS-T2-001-<username>/
   ├── README.md                 # setup, regenerate data, run tests, run benchmark: 15 lines or fewer
   ├── requirements.txt          # pinned versions
   ├── meterflow/                # engines, shared definitions, compliance, sensitivity analysis
   ├── bench/                    # harness and protocol
   ├── tests/
   ├── resources/                # unchanged
   ├── outputs/benchmark.csv
   ├── outputs/compliance.csv
   ├── outputs/sensitivity.csv
   ├── COMPARISON_REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** The history should show the baseline first, then each engine, then the benchmark.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator, then filing a submission issue in the CLBG assessments repository with the **Assessment submission** template. Include the repository URL and the commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback, but never replace the core requirements.

1. **Incremental refresh.** Tomorrow's file arrives. Design an update that recomputes only the affected dates (remember the late re-sends) and benchmark it against a full rerun.
2. **Truth recovery.** Modify a copy of the generator to export each feeder's *true* supplied intervals, then measure the bias and error of the meter-based estimate as a function of the communication-failure rate.
3. **Parquet layout.** Compare partitioning the converted data by date, by feeder, or not at all, for this query and for a "one feeder, whole quarter" query.
4. **Explain a plan.** Use `EXPLAIN ANALYZE` in DuckDB and Polars' `explain()` to show where each spends its time, and connect it to your benchmark.

---

## K. Assessment Integrity

**AI tools are permitted** for learning library APIs, for example "how do I set DuckDB's memory limit?" or "what is Polars' streaming engine?", and for reviewing your code. **They must not design your benchmark or write your report.** The judgement is what is being assessed.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`: which tool, what for, and an example prompt. Undisclosed use that becomes apparent at the defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** documentation, blog posts and published benchmarks you relied on, and say where your results differ from theirs.
- **Collaboration:** you may discuss tools and general benchmarking practice with other members. You may not share code, results or report text.
- **How your understanding is verified.** In the 10–20 minute defence, the assessor will:
  1. rerun one engine of your benchmark live, and ask you to explain any difference from your reported numbers;
  2. ask why your chunked design is correct for late re-sends, and what would break if re-sends could arrive **two** days late, then ask you to change it;
  3. change the budget, for example to 600 MB, and ask which engine you would now recommend, and why;
  4. ask how a feeder with many silent meters could appear more or less compliant than it really is.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Fluent pandas, basic SQL, and the ideas of memory and CPU at a practical level. |
| **New skill developed** | Choosing data tooling by **measurement under a stated constraint**, and building out-of-core pipelines whose correctness survives partitioning. |
| **Decisions the member must make** | How to partition and de-duplicate safely; whether to convert storage; how to apply a memory budget per engine; the benchmark protocol; how to present uncertainty; which engine to recommend, to whom, and when that changes. |
| **What must be investigated independently** | Each library's memory controls and streaming behaviour; why `DISTINCT` and `n_unique` are expensive; how to measure RSS correctly; and how silent meters bias the metric. |
| **Why it's interesting** | The answer depends on the regime: the fastest plan is the hungriest, and the leanest is slow. Cross-file duplicates punish naive chunking. The domain question (do feeders deliver their band?) is socially important, and its metric is genuinely debatable. |
| **Evidence of competence** | Exact agreement with a hidden reference on unseen data; a reproducible benchmark that the assessor reruns; a recommendation that survives a changed constraint at the defence. |
| **Misconceptions exposed** | "Polars and DuckDB are always faster and leaner." "One run is a benchmark." "Chunking is just reading in pieces." "Python's `tracemalloc` measures a process's memory." "A meter that sends nothing had no power." |
| **Preparation for later work** | Data pipelines and orchestration (DS-11), feature computation at scale for ML (ML units), and any Tier 3 work where tooling choices must be defended. |

**Suggested approach**, for members who want it (you may ignore it):

1. Write the baseline first, and make it match `sample_expected` exactly. It becomes your oracle.
2. Generate a medium dataset (for example, 300 meters × 20 days) for development, so that every run takes seconds.
3. Build the chunked pandas engine next, and break it on purpose with a re-send that crosses a file boundary.
4. Write the benchmark harness **before** you tune anything, so that every tuning step is measured.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
