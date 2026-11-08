# DS-T1-023 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and reasoning | 10 | Explains censoring and why the critical ratio is a quantile. |
| 2 | Technical correctness | 25 | R1–R8 pass public and hidden tests; MLE and planning correct on regenerated data. |
| 3 | Implementation quality | 10 | Vectorised, clear, no mutation, validation errors. |
| 4 | Methodology of the simulation study | 15 | Sensible design linking stocking habits to the cost of censoring. |
| 5 | Testing | 15 | At least 6 meaningful tests incl. edge cases (zero stock, no censoring). |
| 6 | Documentation and reproducibility | 10 | Clean run; table regenerates. |
| 7 | Critical thinking and limitations | 10 | Poisson assumption, constant prices, day-type granularity, what the plan ignores. |
| 8 | Presentation and communication | 5 | Plain-language advice a trader could follow. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight, for example quantifies a risk others only mention. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps that do not affect trustworthiness. |
| **Developing** | 50–69% | Partly meets the requirement; some choices unjustified or untested. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. |

## Gates (pass/fail, independent of points)

1. **Integrity:** the AI-use declaration is present and consistent with the defence.
2. **Reproducibility:** the assessor reruns your code from a clean environment and gets your reported numbers.
3. **Defence:** you explain your own code and handle the unseen modification with sound reasoning.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Planning from mean sales and calling it the optimum | Up to −8 from dimension 2 |
| Treating censored days as ordinary Poisson observations in the MLE | Up to −8 from dimension 2 |
| Report quotes numbers `analysis.py` does not regenerate | Up to −4 from dimension 6 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
