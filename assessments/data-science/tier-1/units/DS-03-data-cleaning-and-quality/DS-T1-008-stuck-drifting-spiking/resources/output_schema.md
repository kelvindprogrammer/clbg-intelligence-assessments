# DS-T1-008 Output Schema

All files are UTF-8 with a header row, `\n` line endings and an empty string for null values. Timestamps are ISO 8601 in UTC with a `Z` suffix, rounded to the nearest second.

## `readings_qc.csv` (long format)

One row per **(input row, variable)**: exactly `3 × number of input rows`. Within a device and variable, rows are in **measurement order** (by corrected timestamp), followed by any `CLOCK_STEP` rows in input order. Devices are sorted by `device_id`, and variables in the order `pm25`, `temp_c`, `rh_pct`.

| Column | Type | Rule |
|---|---|---|
| `reading_id` | string | From the input. |
| `device_id` | string | From the input. |
| `device_time` | string | The raw device timestamp, verbatim. |
| `timestamp_utc` | ISO or empty | The corrected measurement time. **Empty** for `CLOCK_STEP` readings. Equal to `device_time` when the device's clock is not corrected. |
| `variable` | enum | `pm25`, `temp_c`, `rh_pct`. |
| `value` | float (1 dp) or empty | The raw value, never altered. Flags describe it; they do not change it. |
| `qc_flags` | int | Bitwise OR of the flag bits (see README §D, "Flag scheme"). |
| `qc_level` | enum | `qc_level(qc_flags)`: `missing`, `bad`, `suspect` or `good`. |

## `gaps.csv`

One row per gap in the **trustworthy** timeline of a device: consecutive non-`CLOCK_STEP` readings, in corrected-time order, more than 1.5 × the expected interval apart. Sorted by `device_id`, then `gap_start`.

| Column | Type | Rule |
|---|---|---|
| `device_id` | string | |
| `gap_start` | ISO | Timestamp of the reading before the gap. |
| `gap_end` | ISO | Timestamp of the reading after the gap. |
| `missing_samples` | int | `round((gap_end − gap_start) / interval) − 1`. |

## `clocks.csv`

One row per device, sorted by `device_id`.

| Column | Type | Rule |
|---|---|---|
| `device_id` | string | |
| `offset_s` | float (1 dp) | Fitted offset (`received_at − device_time`) at the first trustworthy reading. |
| `drift_s_per_day` | float (2 dp) | Fitted slope of that offset. |
| `n_clock_step` | int | Number of rows flagged `CLOCK_STEP`. |
| `corrected` | `True`/`False` | Whether timestamps were corrected (`|drift| ≥ 5 s/day` or `|offset| ≥ 60 s`). |

## `hourly.csv`

One row per device, variable and clock hour, from the device's first to its last trustworthy hour, **including hours with no readings at all**. Sorted by `device_id`, `variable`, `hour_utc`.

| Column | Type | Rule |
|---|---|---|
| `device_id`, `variable` | string | |
| `hour_utc` | ISO | Start of the hour, e.g. `2026-03-02T07:00:00Z`. |
| `n_good` | int | Number of `good` readings in the hour. `suspect` readings are **not** counted. |
| `coverage` | float (4 dp) | `n_good / 12`, capped at 1. |
| `mean` | float (2 dp) or empty | Mean of the good values, only if `coverage ≥ 0.75`. |
| `status` | enum | `ok` or `insufficient`. |
