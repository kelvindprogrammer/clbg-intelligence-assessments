# DS-T2-018 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and reasoning | 10 | Explains why a flat-price spreadsheet fails and what question the board really asks. |
| 2 | Technical correctness | 20 | R1–R7 pass public and hidden tests; reversal reproduced. |
| 3 | Implementation quality | 10 | Vectorised, clear, no mutation, deterministic. |
| 4 | Method choices and sensitivity analysis | 20 | Discount rate, drift trust and risk measure varied; tornado used and interpreted. |
| 5 | Testing | 10 | At least 10 tests including an independent loop implementation. |
| 6 | Documentation and reproducibility | 5 | `analysis.py` regenerates all numbers and figures. |
| 7 | Critical thinking and limitations | 20 | Names model risk, what is excluded, and decision triggers. |
| 8 | Presentation and communication | 5 | A board member could act on the memo. |
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
| Ignoring parameter uncertainty in the headline result | Up to −8 from dimension 4 |
| Recommending an option on expected cost alone with no risk statement | Up to −5 from dimension 7 |
| Memo gives a single number with no range | Up to −5 from dimension 8 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
