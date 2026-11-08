# DS-T2-015 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and reasoning | 10 | Leads with validity; understands why each trap changes the decision. |
| 2 | Technical correctness | 25 | Hidden-scenario verdicts correct; R1–R7 behave; robustness property holds. |
| 3 | Method choice and justification | 15 | Revenue estimator chosen from evidence in `analysis.py`; trade-offs named. |
| 4 | Implementation quality | 10 | Clear modules, no mutation, errors for degenerate input. |
| 5 | Testing | 15 | At least 10 tests, one regression test per trap, a property test for whale robustness. |
| 6 | Documentation and reproducibility | 5 | Analysis regenerates every figure. |
| 7 | Critical thinking and limitations | 15 | Honest about power, excluded users and what the verdict does not say. |
| 8 | Presentation and communication | 5 | A memo a product manager can act on in two minutes. |
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
| Revenue p-value computed with a plain t-test on raw revenue | Up to −8 from dimension 3 |
| Effect estimated before the SRM check, or SRM treated as a warning only | Up to −6 from dimension 2 |
| Hard-coding the supplied export's verdict | Gate fail |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
