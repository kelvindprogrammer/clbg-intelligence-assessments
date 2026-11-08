# DS-T2-001 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Why cross-file re-sends break naive chunking; why `DISTINCT`/`n_unique` dominate cost; what "peak RSS" means and why `tracemalloc` is not enough here. |
| 2 | Technical correctness | 20 | All four engines equal the hidden reference on unseen datasets and adversarial file-boundary cases, with and without a budget; compliance exactly as specified. |
| 3 | Implementation quality | 15 | Shared definitions in one place; each engine short and idiomatic for its library; budget handling documented per engine; clear errors; no committed benchmark data. |
| 4 | Methodology: benchmark design and fairness | 20 | Fresh process per run, at least 3 repeats, median and range, at least two sizes, end-to-end timing from CSV, sampled RSS, environment recorded, conversion cost reported separately and amortised; the assessor's rerun lands within your reported spread. |
| 5 | Testing and evaluation | 10 | At least 8 meaningful member tests: engine equality on generated data, boundary re-sends, minority-positive intervals, the conversion path if any. |
| 6 | Documentation and reproducibility | 5 | One command each to regenerate data, run tests and run the benchmark; pinned requirements. |
| 7 | Critical thinking: trade-offs, validity, recommendation | 15 | A recommendation tied to this team's constraint and the regime where it flips; at least three threats to validity; the sensitivity analysis interpreted, including the direction of bias from silent meters. |
| 8 | Presentation and communication | 5 | Clear tables or figures with uncertainty; a report a DisCo analytics lead could act on. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exact agreement everywhere; a benchmark the assessor reproduces; a mechanistic explanation backed by plans or profiles; a recommendation that holds up when the budget changes at the defence. |
| **Proficient** | 70–89% | Correct engines, a sound protocol and a justified recommendation, with minor gaps in uncertainty or validity discussion. |
| **Developing** | 50–69% | Engines mostly agree but fail an adversarial boundary case, or the benchmark has a major flaw (single run, warm in-process runs, no memory measurement). |
| **Beginning** | 0–49% | Engines disagree, measurements are not reproducible, or the recommendation is asserted rather than evidenced. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** the assessor regenerates the benchmark set and reruns your harness.
3. **Defence:** the member adapts the chunked design to two-day-late re-sends and re-argues the recommendation under a changed budget.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Engines compared while computing different results | Up to −10 from dimension 4 |
| Benchmark dataset or converted data committed | −2 from dimension 6 |
| Benchmark numbers that the harness does not regenerate within the reported spread | Up to −8 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
