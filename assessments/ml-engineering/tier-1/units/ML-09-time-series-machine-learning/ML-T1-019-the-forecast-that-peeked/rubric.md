# ML-T1-019 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links each design choice to look-ahead and baselines, and explains the three original mistakes. |
| 2 | Technical correctness | 25 | Public and hidden tests pass: exact conventions, recovered coefficients, honest backtest bar. |
| 3 | Implementation quality | 15 | Short, vectorised, deterministic functions with clear error handling. |
| 4 | Methodology and evidence | 10 | The comparison is run on multiple seeds with spread; the baseline is reported alongside every model. |
| 5 | Testing and evaluation | 15 | At least 6 own tests including a look-ahead test and a perfect-pattern test. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces the report's numbers; seeds fixed. |
| 7 | Critical thinking and limitations | 10 | Honest account of what a 420-day series cannot tell you (single season, no outages, no holidays). |
| 8 | Presentation and communication | 5 | A planner could read the summary and know which forecast to trust. |
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
| Test data used to scale, fit or select | Up to -12 from dimension 2 |
| Random shuffling in the backtest | Up to -6 from dimension 4 |
| MASE scaled with test-period data | Up to -5 from dimension 2 |
| Forecast loop reads values beyond the training slice | Up to -8 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
