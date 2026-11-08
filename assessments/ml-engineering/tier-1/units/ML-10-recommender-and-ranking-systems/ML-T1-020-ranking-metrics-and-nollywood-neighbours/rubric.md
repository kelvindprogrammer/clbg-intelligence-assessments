# ML-T1-020 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report explains how each convention (ideal DCG, chronological holdout, seen-item exclusion) affects the numbers. |
| 2 | Technical correctness | 25 | Public and hidden tests pass: exact conventions and the neighbour-versus-popularity bar. |
| 3 | Implementation quality | 15 | Short, vectorised, deterministic functions; clear handling of edge cases. |
| 4 | Methodology and evidence | 10 | Comparison across k and seeds with spread; popularity always reported alongside. |
| 5 | Testing and evaluation | 15 | At least 6 own tests including no-leak and empty-history tests. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces the report's numbers; seeds fixed. |
| 7 | Critical thinking and limitations | 10 | Honest about what a leave-last-out hit rate cannot say (diversity, novelty, long-term effects). |
| 8 | Presentation and communication | 5 | A product manager could decide from the summary whether to ship neighbours. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90-100% | Exceeds the requirement with insight, for example by quantifying uncertainty or testing a claim the brief did not ask about. |
| **Proficient** | 70-89% | Fully meets the requirement with minor gaps that do not affect trust in the result. |
| **Developing** | 50-69% | Partly meets the requirement; some choices are unjustified or untested. |
| **Beginning** | 0-49% | Missing, incorrect or unexplained. |

## Gates (pass/fail, independent of points)

1. **Integrity:** the AI-use declaration is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns the tests and experiments from a clean environment and gets your reported numbers.
3. **Defence:** you explain your code and handle an unseen modification with sound reasoning.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Held-out item present in the matrix used for similarity or popularity | Up to -10 from dimension 2 |
| Random rather than chronological hold-out | Up to -6 from dimension 4 |
| Seen items recommended | Up to -5 from dimension 2 |
| NDCG normalised by the recommended list instead of the ideal | Up to -4 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
