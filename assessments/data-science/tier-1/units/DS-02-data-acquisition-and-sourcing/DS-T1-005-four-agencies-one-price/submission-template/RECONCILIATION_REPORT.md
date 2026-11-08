# Reconciliation Report: DS-T1-005

**Member:** `<name>`  **Commit:** `<sha>`

> Limit: 1,500 words plus tables. Every count must be produced by `profiling.py` or `profiling.ipynb`. Note which cell or function produces each one. All prices in this assessment are synthetic, so don't present them as real market prices.

## 1. Format traps found
| Agency | Trap | How you found it | Rule in code (function) | Test that pins it |
|---|---|---|---|---|
| | | | | |

Where a file contradicted `agency_formats.md`, say so here.

## 2. Canonical table summary
- Rows per source, and `ok` / `estimated` / `missing` counts:
- Keys covered by 1, 2, 3 and 4 sources:
- The `spread_ratio` distribution (median, 90th and 99th percentiles) and how it compares with the desk's "about 5 %":

## 3. Anomalies
For each anomaly found by `discrepancies()`, `stale_runs()` or your own exploration:

| # | Market / commodity / weeks | Source(s) | Evidence (numbers) | Classification: parsing error, source defect or real event | Action taken | Question for the agency |
|---|---|---|---|---|---|---|
| | | | | | | |

## 4. What you did NOT change, and why

## 5. Limitations
What can't the files tell you? What size of defect would your 15 % tolerance miss?
