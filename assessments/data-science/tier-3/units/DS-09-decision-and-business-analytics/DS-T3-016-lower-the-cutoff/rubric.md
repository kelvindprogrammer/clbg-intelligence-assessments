# DS-T3-016 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and reasoning | 15 | Identifies selection bias as the core issue; frames the decision correctly. |
| 2 | Technical correctness | 20 | Hidden-book recovery, closed-form checks, draw order, bootstrap coverage. |
| 3 | Implementation quality | 10 | Clear, deterministic, well-tested pipeline. |
| 4 | Methodology: baselines, ablations, robustness | 20 | Naive versus IPW, degrees compared, scenario analysis, exploration simulation. |
| 5 | Testing | 5 | At least 10 meaningful tests. |
| 6 | Documentation and reproducibility | 5 | `analysis.py` reproduces every figure. |
| 7 | Critical thinking, ethics and limitations | 20 | Honest about the thin exploration sample, model dependence, fairness and regulation. |
| 8 | Presentation and communication | 5 | A director could decide from the memo. |
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
| Recommending the lower cut-off on the approved-only extrapolation | Up to −10 from dimension 1 |
| Reporting a single cut-off with no uncertainty | Up to −6 from dimension 4 |
| No discussion of the ethics or regulation of the lending pilot | Up to −6 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
