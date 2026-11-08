# ML-T2-003 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links every design choice to the operational constraint: alert budget, drift and cost of a missed fraud. |
| 2 | Technical correctness | 20 | Public and hidden tests pass: leak found, splits correct, budget metric exact, test recall above the bar on re-seeded data. |
| 3 | Implementation quality | 15 | Pipeline is leakage-free, deterministic, modular; candidate models share one evaluation path. |
| 4 | Methodology and evidence | 15 | Candidate comparison uses the right metric, time-ordered validation and more than one seed or split; imbalance handling is compared, not assumed. |
| 5 | Testing and evaluation | 15 | At least 10 own tests, including a leak-injection test and a look-ahead test. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces the comparison table; seeds fixed. |
| 7 | Critical thinking and limitations | 10 | Honest account of what the validation set cannot tell you: drift, small positive counts, selection bias. |
| 8 | Presentation and communication | 5 | A fraud-operations lead could act on the report. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight, for example by quantifying uncertainty or testing a claim the brief did not ask about. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps that do not affect trust in the result. |
| **Developing** | 50–69% | Partly meets the requirement; some choices are unjustified or untested. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. |

## Gates (pass/fail, independent of points)

1. **Integrity:** the AI-use declaration is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns the tests and experiments from a clean environment and gets your reported numbers.
3. **Defence:** you explain your code and handle an unseen modification with sound reasoning.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Test-period data used for fitting, selecting or thresholding | Up to −12 from dimension 2 |
| Random K-fold used across time without discussion | Up to −5 from dimension 4 |
| Accuracy or ROC-AUC used as the headline metric under an alert budget | Up to −5 from dimension 4 |
| Leaky column named in code rather than detected | Up to −8 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
