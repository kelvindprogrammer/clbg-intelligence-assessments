# DS-T1-016 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You can explain why Wald collapses at k = 0 and k = n, why frequency framing helps, and why crossing quantiles make a fan chart meaningless. |
| 2 | Technical correctness | 25 | Hidden-suite results: Wilson to 1e-9; exact dots and stacks; interval-plot geometry; threshold alignment for every market, dot count and threshold; fan bands exact, nested and lighter outside; crossing tables refused. |
| 3 | Implementation quality | 15 | Small pure functions reused by the plotting code (no duplicated maths); no input mutation; no silent repair; clear errors. |
| 4 | Methodology: display choice for the decision | 10 | The design note argues which display answers "store until March?" best and why, and justifies the default bin width with reference to the dot count and the readability of the stacks. |
| 5 | Testing and evaluation | 15 | At least 10 member tests covering k = 0, k = n, n = 1, a value exactly on a bin edge, and out-of-order quantile columns. The tests would catch a Wald regression. |
| 6 | Documentation and reproducibility | 5 | `make_figures.py` regenerates the committed figures, and the run instructions work first time. |
| 7 | Critical thinking and limitations | 10 | Says what repairing the Bodija quantiles cannot fix; notices that the dotplot and fan chart March ranges come from different runs; notes the limits of a 4-farmer survey. |
| 8 | Presentation and communication | 10 | The one-page bulletin can be read aloud, shows an interval for every number, states "4 in 20" style frequencies, gives sources and dates, and makes no recommendation. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight. For example, a coverage simulation backs up the Wilson argument, or the bulletin was read-aloud tested. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps. |
| **Developing** | 50–69% | Partly meets the requirement. For example, dots straddle the threshold, or the bulletin hides an interval. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. For example: Wald intervals, a single forecast line, or silent repair. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** tests and `make_figures.py` run in a clean environment.
3. **Defence:** the member explains the Wald failure and predicts a frequency text correctly.
4. **No silent repair:** no code path repairs quantiles without the caller asking.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Data files modified (checksum mismatch) | Gate fail until corrected |
| The bulletin recommends storing or selling | Up to −4 from dimension 8 |
| A point forecast printed without an interval | Up to −3 from dimension 8 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
