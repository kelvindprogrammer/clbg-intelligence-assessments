# ML-T3-019 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links the logging policy, the examination curve and the exposure outcome, and names who gains and loses. |
| 2 | Technical correctness | 15 | Public and hidden tests pass; estimation and ranking bars met on unseen seeds. |
| 3 | Implementation quality | 10 | One harness for all variants; no use of generator truth in training; clean and deterministic. |
| 4 | Methodology and evidence | 20 | Ablations (clipping, normalisation, slice size, training rows) isolate effects with spread over seeds; assumptions are tested. |
| 5 | Testing and evaluation | 10 | At least 10 own tests including hand-built IPS, position-independence and no-bias cases. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces every table and figure; seeds fixed. |
| 7 | Critical thinking and limitations | 20 | Honest treatment of the position-based assumption, trust bias, the cost of exposure targets and feedback loops. |
| 8 | Presentation and communication | 5 | A marketplace product lead could act on the recommendation and the monitoring plan. |
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
| Use of `true_relevance` or `TRUE_EXAM` in estimation, training or selection | Up to -15 from dimension 2 |
| Examination curve estimated from non-randomised rows with no argument | Up to -6 from dimension 2 |
| Evaluating the ranker on clicks from the same biased log | Up to -6 from dimension 4 |
| Exposure change claimed without stating its cost | Up to -4 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
