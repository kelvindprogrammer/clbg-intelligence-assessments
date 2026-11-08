# AI-T3-001 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Protocol and report link each design choice to the harm model and release cost. |
| 2 | Technical correctness | 20 | Hidden tests pass: exact R1 to R4, calibration and power on a different mock, thin-data honesty. |
| 3 | Implementation quality | 15 | Gate, bootstrap and simulation are separate, vectorised and deterministic; a 150-trial calibration runs in under a minute. |
| 4 | Methodology and evidence | 15 | At least three gate variants compared across at least four scenarios and two sizes, with Monte Carlo error. |
| 5 | Testing and evaluation | 15 | At least 12 own tests including calibration and power tests with justified tolerances. |
| 6 | Documentation and reproducibility | 10 | One command reproduces tables and figure; trial counts and seeds stated. |
| 7 | Critical thinking and limitations | 10 | Validity argument separates mock findings from real-model claims; discusses contamination and slice choice. |
| 8 | Presentation and communication | 5 | A release board could adopt or reject the protocol from the report. |
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
| Cell-level resampling presented as item-level inference | Up to -8 from dimension 4 |
| Real-model claims drawn from mock effect sizes | Up to -6 from dimension 7 |
| Operating characteristics reported without trial counts or Monte Carlo error | Up to -4 from dimension 4 |
| Underscore-prefixed mock internals imported | Up to -15 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
