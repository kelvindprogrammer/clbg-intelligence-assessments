# DS-T1-008: Stuck, Drifting, Spiking

> *Five cheap air-quality monitors, twelve days of Lagos air, and every way a low-cost sensor can lie. Implement tested validation rules and a quality-flag scheme that a city could publish data on.*

![Format: Implementation](https://img.shields.io/badge/format-implementation-1f6feb) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-008` |
| **Title** | Stuck, Drifting, Spiking: Validation Rules for a Low-Cost Air-Quality Network |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-03: Data Cleaning and Data Quality](../README.md) |
| **Format** | Implementation (secondary: Debugging & Forensics) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 12–18 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | pandas time series (`to_datetime`, sorting, `groupby`); NumPy arrays; medians and the median absolute deviation; bitwise operators (`&`, `|`); running `pytest` |
| **Skills developed** | Rule-based time-series validation; robust spike detection (Hampel filter); run-length logic; clock-drift estimation with a robust regression; gap analysis; designing and applying a bitmask quality-flag scheme; completeness rules for aggregates |
| **Technologies** | Python 3.10+, pandas, NumPy, SciPy (`scipy.stats.theilslopes`), pytest |

---

## B. Problem Statement

Lagos does not have enough reference-grade air-quality monitors, and they cost tens of thousands of dollars each. Low-cost monitors that use a laser-scattering PM2.5 sensor and a digital temperature/humidity sensor cost a few hundred dollars. Universities, NGOs and community groups across Nigeria are deploying them on school roofs, by roadsides and in markets. The data is valuable, and it is also notoriously unreliable. Sensors freeze, firmware writes sentinel values like `6553.5`, clocks drift because the device has no time server, a brownout resets the clock to the year 2000, and humid nights make optical PM2.5 sensors over-read.

A university air-quality group has deployed **five monitors** (LAG-01 to LAG-05) that report every five minutes through a cellular gateway. Before the group publishes hourly PM2.5 for its sites, every reading must carry a **quality flag** that says what is known to be wrong with it. Your job is to implement the validation rules exactly as specified, apply them to twelve days of data, and produce flagged readings, a gap report, a clock report and hourly means that respect a completeness rule.

This is a **Tier 1 implementation**: the rules, their parameters and the flag scheme are fixed below. The challenge is to implement them **correctly**, which is harder than it sounds, and to understand why each rule exists. Several traps reward understanding over procedure-following:

- **The file is in arrival order, not measurement order.** When the cellular network drops, the device buffers its readings and uploads them later. Any rule that looks at neighbouring readings must first put them in measurement order.
- **A late upload is not a clock fault.** Rules that treat a large gap between `received_at` and `device_time` as suspicious will flag hours of good data.
- **A real pollution episode is not a spike.** A burning dump or a traffic jam raises PM2.5 for hours. A spike rule with the wrong window or no robust scale flags it.
- **Flags describe values; they don't change them.** You never clip, interpolate or delete a reading. You record what is wrong with it.

**Known facts from the field team** (the only documentation you get):

- Device clocks are configured to **UTC** at installation on **2026-02-23** (see [`devices.csv`](resources/reference/devices.csv)). They have no network time sync. `received_at` is stamped by the gateway, which is synchronised, so it is trustworthy, but it includes network latency and occasional buffered uploads.
- Readings are expected every **300 seconds**.
- The PM2.5 sensor's specified range is 0–1000 µg/m³. The temperature/humidity sensor reports −10 to 60 °C and 0–100 % RH in this climate. Values outside these limits are firmware errors.
- Optical PM2.5 sensors are known to over-read when relative humidity is high, because particles absorb water and grow. The group's convention is to mark PM2.5 as **suspect** above 85 % RH.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** range, stuck-value and Hampel spike rules exactly to a specification, and prove it with tests on hand-built series.
2. **Estimate** a device's clock offset and drift with a robust regression that is not fooled by late uploads, and identify readings whose timestamp cannot be trusted.
3. **Order** time-series data correctly before applying sequence rules, and explain what goes wrong if you don't.
4. **Apply** a bitmask flag scheme in which one reading can carry several flags, and derive a single quality level from it.
5. **Aggregate** to hourly means with a completeness rule, so that gaps and bad data are visible rather than averaged away.
6. **Explain** each rule's purpose, its failure modes and what it cannot detect.

---

## D. Technical Requirements

### D.1 Flag scheme (fixed)

The bits are defined in [`starter/sensorqc/types.py`](starter/sensorqc/types.py). A reading's `qc_flags` is the bitwise OR of every bit that applies.

| Bit | Name | Meaning | Level |
|---|---|---|---|
| 1 | `MISSING` | No value | `missing` |
| 2 | `RANGE` | Outside the range in `qc_config.json` | `bad` |
| 4 | `STUCK` | Part of a run of identical values of length ≥ `stuck_min_run` | `bad` |
| 8 | `SPIKE` | Isolated departure from the local median (Hampel rule) | `bad` |
| 16 | `CLOCK_STEP` | Device timestamp is untrustworthy for this reading | `bad` |
| 32 | `HUMIDITY` | PM2.5 only: measured while a valid RH reading is > 85 % | `suspect` |
| 64 | `DRIFT_CORRECTED` | Timestamp was corrected for clock drift | informational |

**Level precedence:** `missing` if `MISSING` is set; otherwise `bad` if any of `RANGE`, `STUCK`, `SPIKE` or `CLOCK_STEP` is set; otherwise `suspect` if `HUMIDITY` is set; otherwise `good`.

### D.2 Mandatory functional requirements

Implement the `sensorqc` package in [`starter/sensorqc/`](starter/sensorqc/). Signatures are fixed. Parameters come from [`qc_config.json`](resources/reference/qc_config.json). Output formats are fixed in [`resources/output_schema.md`](resources/output_schema.md).

| ID | Requirement |
|---|---|
| **R1** | `range_flags(values, lo, hi)`: `True` where a value is present and `< lo` or `> hi`. NaN is never flagged. |
| **R2** | `stuck_flags(values, min_run)`: `True` for **every** element of a maximal run of ≥ `min_run` consecutive, identical, non-NaN values. A NaN ends a run. |
| **R3** | `spike_flags(values, half_window, k, min_abs)` (Hampel rule). For each non-NaN value `x_i`, take the window `values[i−h : i+h+1]` (h = `half_window`, truncated at the edges) and drop NaNs. If fewer than `h + 1` values remain, don't flag. Otherwise let `med` be the window median and `MAD` the median of `|w − med|` over the window. Flag when `|x_i − med| > max(k · 1.4826 · MAD, min_abs)`. |
| **R4** | `find_gaps(times, expected_interval_s)`: sort the timestamps. Every consecutive difference `> 1.5 × expected_interval_s` is a gap with `missing_samples = round(diff / interval) − 1`. |
| **R5** | `estimate_clock(device_time, received_at, deployed_on, future_tolerance_s=300)` for one device. Let `offset = received_at − device_time` in seconds, and let `days` be the elapsed device time in days since the earliest reading at or after `deployed_on`. (1) Readings with `device_time` before `deployed_on` are steps. (2) Fit `offset = a + b · days` with **Theil–Sen** (`scipy.stats.theilslopes`) on the non-step readings. You may fit on an evenly spaced subsample of up to 1,500 points for speed. (3) Readings whose residual `offset − (a + b·days)` is **below** `−future_tolerance_s` are also steps, because the device claims a time well ahead of the fitted clock. (4) Refit on the remaining readings. Return `ClockEstimate(offset_s=a, drift_s_per_day=b, step_mask)`. |
| **R6** | `qc_level(flags)` implements the precedence in D.1. |
| **R7** | `run_qc(raw, config) -> QCResult(readings, gaps, clocks)`. Per device: estimate the clock. Correct timestamps (`device_time + a + b·days`, flag `DRIFT_CORRECTED`) when `|b| ≥ drift_correct_min_s_per_day` or `|a| ≥ offset_correct_min_s`. Steps get `CLOCK_STEP` and an empty `timestamp_utc`. Per variable, in this order: `MISSING`; `RANGE`; `CLOCK_STEP`. Then, on the series in **measurement order** with missing, range-failed and step readings set to NaN, apply `STUCK`. Then, with stuck readings also set to NaN, apply `SPIKE`. Finally, for `pm25`, set `HUMIDITY` where the same row's RH is present, passes the range check and is `> humidity_suspect_rh`. Gaps are computed on each device's non-step corrected timestamps. |
| **R8** | `hourly_means(readings, min_coverage=0.75, expected_interval_s=300)` follows the output schema: only `good` readings count, coverage is `n_good / 12`, the mean is reported only when coverage ≥ 0.75, and hours with no readings appear as `insufficient`. |
| **R9** | `python -m sensorqc <readings.csv> --out <dir>` writes the four output files. The CLI is provided. |

**Why these parameters?** 12 identical PM2.5 values is one hour, which is implausible for a sensor with 0.1 µg/m³ resolution in a city. Temperature and RH change more slowly, so their limit is two hours. In the Hampel rule, the factor 1.4826 makes the MAD consistent with a standard deviation for normal data, and `min_abs` stops the rule firing when the local MAD is tiny. The 75 % completeness rule for hourly means matches common regulatory practice for averaging periods (for example, the US EPA's data-completeness conventions). You should explain each of these in your own words in the report.

### D.3 Engineering requirements (mandatory)

- **Values are never modified.** `value` in the output equals the raw value.
- **Completeness.** `readings_qc.csv` has exactly one row per (input row, variable).
- **Determinism.** Two runs give identical outputs.
- **Performance.** The CLI finishes in under **120 seconds** on a typical laptop. Vectorise the spike rule if a Python loop is too slow.
- **Tests.** Keep the provided tests passing and add **at least 12 tests of your own** in `tests/test_member_*.py`, including at least one for each of R1–R6 on hand-built inputs, and at least two that reproduce a trap from §B (for example, arrival-order processing).
- **Dependencies.** pandas, NumPy, SciPy and pytest only.

### D.4 Privacy and responsibility

The data is **synthetic** and contains no personal data. Air-quality data is still public-interest information. Publishing an unflagged PM2.5 spike can trigger a false alarm in a school community, and suppressing a real episode hides a health risk. In one paragraph, explain which of your rules could hide a real pollution event, and what the group should do before publishing.

### D.5 Optional enhancements (not required for full marks)

- A `--plot DEVICE` option that draws PM2.5 for one device with flagged readings highlighted.
- A sensitivity table: how many readings each rule flags as `k`, `half_window` and `stuck_min_run` vary.
- A cross-device consistency check: flag a device whose hourly PM2.5 departs strongly from the network median.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/sensor_readings.csv`](resources/data/sensor_readings.csv): 17,068 rows × 7 columns, about 1.2 MB, UTF-8 |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed from a simple model of diurnal PM2.5, temperature and humidity, plus documented injected faults. Site names are real Lagos districts, but no real monitor is described. The generator is kept in the assessor kit because it would reveal the faults. |
| **Licence** | CC BY 4.0 (same as this repository's content) |
| **Integrity** | SHA-256 `b61cf56051806bb936129a913edf19d14979feaf77157c33b655b031b712f42a`. The contract test checks it. |
| **Reference files** | [`qc_config.json`](resources/reference/qc_config.json) (all rule parameters) · [`devices.csv`](resources/reference/devices.csv) (device register) |
| **Output schema** | [`resources/output_schema.md`](resources/output_schema.md) |

**Input schema** (every column read as text):

| Column | Meaning | What you should expect |
|---|---|---|
| `reading_id` | Gateway row ID, in arrival order | Clean |
| `device_id` | Monitor | `LAG-01` to `LAG-05` |
| `device_time` | The device's own clock, UTC, no suffix | Drift, steps |
| `received_at` | Gateway receipt time, UTC with `Z` | Trustworthy, but includes latency and buffered uploads |
| `pm25` | PM2.5, µg/m³, 0.1 resolution | Spikes, sentinels, stuck runs, empty strings |
| `temp_c` | Air temperature, °C | Same kinds of fault |
| `rh_pct` | Relative humidity, % | Same kinds of fault |

**Known limitations (by design).** There is no co-located reference monitor, so you can't calibrate the sensors, only validate them. Humidity bias is flagged, not corrected. Some faults, such as a slow calibration drift in PM2.5 itself, are undetectable with these rules. Say so.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-03-data-cleaning-and-quality/DS-T1-008-stuck-drifting-spiking
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract      # passes immediately
pytest                  # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `sensorqc/` package (the completed starter) | The rule implementations: the core technical evidence |
| 2 | `tests/test_member_*.py` (≥ 12 tests) | Pins every rule on hand-built inputs, including the traps |
| 3 | `outputs/readings_qc.csv`, `gaps.csv`, `clocks.csv`, `hourly.csv` | The artefacts the group would publish from |
| 4 | `QC_REPORT.md` (at most 1,200 words plus tables and figures), from the [template](submission-template/QC_REPORT.md) | Explains each rule, what it found and what it cannot detect |
| 5 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 6 | A 5–10 minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

Assessors check ⚙ criteria with the public and hidden suites (official feed plus two re-seeded feeds in which every fault sits on a different device), and ✍ criteria by hand.

1. ⚙ All provided tests and your own tests pass in a clean environment built from your `requirements.txt`.
2. ⚙ `python -m sensorqc resources/data/sensor_readings.csv --out outputs/` finishes in under 120 seconds and writes the four files in the required schema.
3. ⚙ **Range faults:** every injected out-of-range value carries `RANGE`. *Justification:* the rule is deterministic, so anything less is a bug.
4. ⚙ **Spikes:** at least **95%** of injected spikes are `bad`. *Justification:* every injected spike is at least three times `min_abs` away from its local median. The reference catches 97–98% through the `SPIKE` bit, and 99–100% as `bad` once overlaps with other flags are counted. The margin allows for spikes that land next to gaps or other faults.
5. ⚙ **Stuck runs:** at least **95%** of injected stuck readings carry `STUCK`. *Justification:* the injected runs are 4–9 hours long, far above the thresholds. The reference catches 100%. Missing them usually means the series was not in measurement order or NaNs were not handled.
6. ⚙ **Clock faults:** at least **99%** of readings with a reset or jumped clock carry `CLOCK_STEP`, and **no** buffered late upload does. *Justification:* the reset lands decades before deployment and the jump is 24 times the tolerance, so both are unambiguous. Late uploads are by definition not clock faults.
7. ⚙ **No false alarms:** at most **1%** of fault-free readings are `bad`, and at most **5%** of readings during genuine pollution episodes are `bad`. *Justification:* the reference marks under 0.1% and 0% respectively on all three feeds. 1% is the error rate at which the group's hourly means would start losing whole hours to false flags.
8. ⚙ **Time:** at least **99%** of non-step corrected timestamps are within **60 s** of the true measurement time, and each device's drift estimate is within **±5 s/day** of the truth, with correction applied only to the drifting device. *Justification:* latency is around 10 s, so 60 s separates a correct correction from none at all (the drifting device is 18 minutes off by day 12). The reference's drift error is under 1 s/day.
9. ⚙ The device outage is reported in `gaps.csv`, and hourly means follow the 75% rule.
10. ⚙ Deterministic outputs.
11. ✍ The report explains each rule's purpose and at least one thing it cannot detect, and quantifies what each rule flagged per device.
12. ✍ The report demonstrates, with numbers, at least one trap from §B: what happens if you process in arrival order, or treat late uploads as clock faults.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 15 |
| Methodology (rules → evidence) | 10 |
| Testing and evaluation | 20 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 5 |
| Presentation and communication | 5 |
| **Total** | **100** |

Outcome rules: [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create a private repository** named `clbg-DS-T1-008-<your-github-username>`, and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` into it.
2. **Expected structure:**
   ```text
   clbg-DS-T1-008-<username>/
   ├── README.md                # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── sensorqc/                # your package (from starter/)
   ├── tests/                   # provided tests + your test_member_*.py
   ├── resources/               # unchanged
   ├── outputs/                 # the four CSVs
   ├── QC_REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** Your history is evidence, and a single final commit will be questioned.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue with the repository URL and commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work).
6. Full guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Rule sensitivity.** Plot readings flagged against `k` (2–6) and `half_window` (2–6) for the spike rule. Where does it start flagging genuine episodes?
2. **Network consistency.** Five monitors in one city should rise and fall together. Design a cross-device check and report what it finds that the single-device rules miss.
3. **Humidity correction.** Read about published humidity-correction approaches for optical PM sensors, and explain what extra data would be needed to apply one here. Don't implement a correction without that data.
4. **Streaming.** Which of your rules can run on a live stream reading by reading, and which need future values? Rewrite one to run online and show where its output differs.

---

## K. Assessment Integrity

**AI tools are permitted** for learning, for example to explain the Hampel filter, Theil–Sen regression or bitwise operations, or to review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`. Disclosed, reasonable use is not penalised.
- **Cite** any source you used for rule definitions or adapted code.
- **Collaboration:** you may discuss general techniques. You may not share code, counts or report text.
- **How your understanding is verified.** In the defence, the assessor will:
  1. give you a `qc_flags` integer (for example `42`) and ask you to decode it and give its level;
  2. give you a seven-value window and ask you to apply the spike rule by hand;
  3. ask you to make an **unseen modification** live, for example adding a new flag bit for a rate-of-change rule, or changing the stuck rule so that runs at the sensor's minimum value are ignored, and to update the tests.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | pandas time series, NumPy, medians and MAD, bitwise operators, `pytest`. |
| **New skill developed** | Implementing validation rules *exactly*, and understanding that the order of operations (sorting, masking, which rule sees which values) is part of the specification. |
| **Decisions the member must make** | How to vectorise without changing the rule's meaning; how to order data before sequence rules; how to test each rule on inputs that isolate it; how to explain each rule's blind spots. |
| **What must be investigated independently** | Why late uploads exist and how they look in the data; which devices carry which faults; what each rule *cannot* detect. |
| **Why it's interesting** | Every fault is a real failure mode of low-cost sensors deployed in Nigerian cities (power cuts and clock resets, patchy cellular coverage, humid nights), and several naive implementations look correct but quietly flag good data or miss bad data. |
| **Evidence of competence** | Exact unit tests on hand-built series; per-fault recall and false-alarm rates on re-seeded feeds; timestamp accuracy against truth; live decoding of flags and hand application of the Hampel rule. |
| **Misconceptions exposed** | "The file order is the time order." "A big latency means a broken clock." "A spike is any big value." "Bad data should be deleted or interpolated." "An hourly mean of whatever readings exist is fine." |
| **Preparation for later work** | It leads into DS-T2 data contracts for recurring feeds, ML-track monitoring and drift detection, and any IoT or sensor pipeline where data quality must be computed, not assumed. |

**Suggested approach** (optional): implement and test R1–R4 and R6 on tiny hand-built series first; then R5 on synthetic clocks; then plot one device's offset against time to *see* the drift, the step and the late uploads before writing `run_qc`.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
