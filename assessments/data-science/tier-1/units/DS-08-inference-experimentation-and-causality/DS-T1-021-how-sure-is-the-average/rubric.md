# DS-T1-021 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and reasoning | 10 | The note shows why intervals, not means, answer PaySabi's question, and why small regions differ. |
| 2 | Technical correctness | 20 | R1–R6 pass public and hidden tests; draw order is exact; coverage bands met. |
| 3 | Implementation quality | 10 | Vectorised draws, clear functions, no input mutation, validation errors. |
| 4 | Methodology of the simulation study | 20 | Sensible design (distributions, n, reps), reproducible `analysis.py`, Monte Carlo error acknowledged. |
| 5 | Testing | 10 | At least 8 meaningful tests, two sensitive to draw order. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run works; every quoted figure regenerates. |
| 7 | Critical thinking and limitations | 15 | Correct interpretation of 95%; honest treatment of tiny regions; limits of bootstrap. |
| 8 | Presentation and communication | 5 | Plain-language, concise note with no false precision. |
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
| Using `scipy.stats.bootstrap` or another library routine in place of R2 | Up to −8 from dimension 2 |
| Quoting coverage figures that `analysis.py` does not regenerate | Up to −5 from dimension 6 |
| Describing a computed interval as having a 95% probability of containing the truth | Up to −3 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
