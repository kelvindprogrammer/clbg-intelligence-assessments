# DS-T2-004 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You can explain why each granularity mismatch (daily vs annual, grid vs national, season vs calendar) can change the result, and what each design is meant to test. |
| 2 | Technical correctness | 15 | The primitives pass public and hidden checks (calendar-based coverage, leap years, cross-year seasons, fill values, renormalised weights, flag-preserving FAOSTAT parsing). The baseline is reproduced faithfully. |
| 3 | Implementation quality and reproducibility | 15 | `acquire.py` is idempotent with a verifiable manifest. `run_designs.py` regenerates everything offline. Designs are data (configuration), not copy-pasted scripts. |
| 4 | Methodology: designs, baseline and uncertainty | 25 | At least four designs, each varying one documented decision, all compared with the baseline using bootstrap intervals and `n`. A sensible spatial aggregate. A justified detrending choice. Flag effects shown. |
| 5 | Testing and evaluation | 10 | At least 10 member tests pinning your own choices: the point list, the season per zone, the flag filter, and the design runner's output schema. |
| 6 | Source critique and licensing | 10 | The R10 audit is decided from evidence (WDI metadata and the values themselves). Every source is correctly attributed. No bulk redistribution. |
| 7 | Critical thinking and limitations | 10 | The conclusion matches the intervals. Threats are named: reanalysis versus gauges, national aggregation, serial correlation, about 30 data points, and estimated or external values. You say what data would change the conclusion. |
| 8 | Presentation and communication | 5 | One clear table of designs and one figure of estimates with intervals, in a report the programme manager could follow. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | A specification curve, power analysis or out-of-sample check that sharpens the conclusion. Zone-aware seasons. A block bootstrap with justification. |
| **Proficient** | 70–89% | All requirements met, with a well-calibrated conclusion and minor gaps. |
| **Developing** | 50–69% | Designs are run, but uncertainty is missing or decisions are undocumented. The conclusion overreaches. |
| **Beginning** | 0–49% | One design reported as "the answer". Trending series correlated. Missing days treated as zero rain. Flags ignored. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** `run_designs.py` regenerates the report's numbers offline from the files listed in the manifest.
3. **Defence:** you justify the decisions and add a design live.

## Automatic deductions

| Issue | Deduction |
|---|---|
| A claim of a robust effect that the intervals do not support | Up to −8 from dimension 7 |
| Raw bulk data committed to the repository | −3 from dimension 6 |
| Missing attribution for any source | −2 per source from dimension 6 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
