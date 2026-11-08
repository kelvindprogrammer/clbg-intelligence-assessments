# DS-T3-013 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and causal reasoning | 15 | Clear estimand, assumptions and a correct account of why TWFE fails. |
| 2 | Technical correctness | 20 | Hidden-panel recovery, TWFE exactness, bootstrap replica, pre-trend separation. |
| 3 | Implementation quality | 10 | Readable, tested, deterministic estimators. |
| 4 | Methodology: ablations and baselines | 20 | Meaningful ablation set, standard errors, honest reading of what changes. |
| 5 | Testing | 10 | At least 10 tests including a noiseless bias construction. |
| 6 | Documentation and reproducibility | 5 | `ablation.py` regenerates every quoted number. |
| 7 | Critical thinking and validity argument | 15 | Threats identified, tied to data that would test them, recommendation proportionate to evidence. |
| 8 | Presentation and communication | 5 | Memo usable by a non-technical decision maker. |
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
| Recommending the TWFE number without a stated reason it is valid | Up to −8 from dimension 1 |
| Standard errors clustered at the observation level, or ignoring clustering | Up to −6 from dimension 2 |
| Reporting flat pre-trends as proof of parallel trends | Up to −4 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
