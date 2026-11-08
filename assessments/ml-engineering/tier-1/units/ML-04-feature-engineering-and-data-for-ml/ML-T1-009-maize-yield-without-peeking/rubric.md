# ML-T1-009 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Explains exactly what leaks in each leaky variant and why it inflates scores. |
| 2 | Technical correctness | 25 | Public and hidden tests pass; encoder formula and leave-one-out limit exact; perturbation tests pass. |
| 3 | Implementation quality | 15 | Vectorised, pure, readable; fit and transform cleanly separated. |
| 4 | Methodology and validation | 10 | Compares honest, in-sample and leaky pipelines fairly with the same model. |
| 5 | Testing and evaluation | 15 | At least 5 own tests including a self-designed leakage test. |
| 6 | Documentation and reproducibility | 10 | Numbers in the report regenerate from the code. |
| 7 | Critical thinking and limitations | 10 | Edge cases and privacy of encoded tables discussed concretely. |
| 8 | Presentation and communication | 5 | Short, clear, with the three numbers up front. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90-100% | Exceeds the requirement with insight that is evidenced, not asserted. |
| **Proficient** | 70-89% | Fully meets the requirement with minor gaps that do not affect trustworthiness. |
| **Developing** | 50-69% | Partly meets the requirement; some choices are unjustified, untested or unevidenced. |
| **Beginning** | 0-49% | Missing, incorrect or unexplained. |

## Gates (pass/fail, independent of points)

1. **Integrity:** the AI-use declaration inside `REPORT.md` is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns your code from a clean environment and obtains the numbers you report.
3. **Defence:** you explain your own code and handle an unseen modification with sound reasoning.
4. **Honesty:** no number in the report is invented, and no test was weakened or special-cased.

## Automatic deductions

| Issue | Deduction |
|---|---|
| The data file was modified (checksum mismatch) | Gate fail until corrected |
| scikit-learn used inside the package | Up to -15 from dimension 2 |
| A statistic learned from test rows | Up to -15 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
