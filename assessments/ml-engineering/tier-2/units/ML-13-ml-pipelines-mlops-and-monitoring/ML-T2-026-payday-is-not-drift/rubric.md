# ML-T2-026 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report ties each design element to a failure of the naive monitor and to the operating requirement. |
| 2 | Technical correctness | 20 | Public and hidden tests pass: statistics exact, threshold calibration correct, detection and false-alarm bars met on re-seeded streams. |
| 3 | Implementation quality | 15 | Causal, pure, parameterised; the statistic, reference and threshold rule are separable and testable. |
| 4 | Methodology and evidence | 15 | Naive versus designed monitor on 5 or more seeds, with an ablation that removes one element at a time. |
| 5 | Testing and evaluation | 15 | At least 10 own tests including causality, quiet days and a synthetic-null calibration test. |
| 6 | Documentation and reproducibility | 10 | A clean-environment run reproduces every number and figure in the report. |
| 7 | Critical thinking and limitations | 10 | Honest account of what covariate monitoring cannot detect, and of the period and reference assumptions. |
| 8 | Presentation and communication | 5 | A data team lead could deploy or reject the monitor from the report. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90-100% | Exceeds the requirement with insight, for example by testing a claim the brief did not ask about. |
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
| Monitor uses `drift_day` or generator internals | Up to -12 from dimension 2 |
| Hard-coded 30-day period with no estimate from data | Up to -5 from dimension 4 |
| Threshold set by looking at post-drift days | Up to -8 from dimension 2 |
| Multiple testing across features ignored without discussion | Up to -5 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
