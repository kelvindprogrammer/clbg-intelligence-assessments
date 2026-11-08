# DS-T1-003 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You can explain why absent rows, NaN-skipping sums and forward-looking windows break naive vectorisation, and why the legacy anomaly function scales super-linearly. |
| 2 | Technical correctness (equivalence) | 25 | All four fast functions are equivalent to legacy on the hidden adversarial records and edge cases, with dtypes, NaT/`<NA>` positions and row order exactly right. |
| 3 | Implementation quality | 15 | No Python loops over rows, days or station-years; one clear representation of the calendar reused by all functions; every array trick commented; meets the speed bars on the unseen medium benchmark. |
| 4 | Methodology: profile, optimise, verify | 15 | Profiling before optimising, with the profile quoted; one function at a time, each with equivalence tests; a benchmark that follows the protocol (warm-up, repeats, median and IQR, memory, environment). |
| 5 | Testing and evaluation | 15 | At least 8 member tests; at least 3 edge cases traced to specific legacy lines; an independent randomised equivalence generator; tests that would catch NaN-skipping and row-versus-day errors. |
| 6 | Documentation and reproducibility | 5 | `profile_legacy.py` and `bench.py` regenerate the submitted outputs; the README explains how to recreate `medium` and `full`. |
| 7 | Critical thinking and limitations | 10 | An honest scaling analysis, including the estimated legacy time on `full` and how it was estimated; timing noise acknowledged; any doubts about the onset rule stated without changing it. |
| 8 | Presentation and communication | 5 | `PERFORMANCE.md` is concise, with one clear speed-up table and one scaling figure or table. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Equivalent everywhere, well above the speed bars, with a benchmark you could publish and a clear explanation of every trick and every scaling curve. |
| **Proficient** | 70–89% | Equivalent everywhere and above the speed bars, with minor gaps in the protocol or the write-up. |
| **Developing** | 50–69% | Fast and equivalent on the sample, but fails some hidden adversarial cases (typically absent rows or look-ahead boundaries), or the benchmark is a single timing. |
| **Beginning** | 0–49% | Not equivalent, still loop-bound, or unmeasured. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Oracle untouched:** `legacy.py` is unchanged from the starter.
3. **Reproducibility:** the assessor reruns the tests, `profile_legacy.py` and `bench.py` (on `sample` and `medium`) from a clean environment.
4. **Defence:** the member explains the onset formulation on paper and makes the live rule change in both versions.

## Automatic deductions

| Issue | Deduction |
|---|---|
| `fast.py` calls `legacy.py` functions | Gate fail (R5) |
| Python loop over days, rows or station-years in `fast.py` | Up to −10 from dimension 3 |
| Benchmark numbers that `bench.py` does not regenerate | Up to −5 from dimension 4 |
| Medium or full data committed to the repository | −2 from dimension 6 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
