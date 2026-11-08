# ML-T3-025 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report frames retraining as a cost, delay and regime problem and justifies the cost ratio and regimes it studies. |
| 2 | Technical correctness | 20 | Simulator and decision rules pass independent-computation tests; bars on re-seeded streams are met. |
| 3 | Implementation quality | 15 | Clean separation of simulator, policies and analysis; the label gate cannot be bypassed; policies are deterministic. |
| 4 | Methodology and evidence | 15 | Policy set, regret analysis, sweep and ablation form a coherent study with paired uncertainty across 5 or more seeds. |
| 5 | Testing and evaluation | 15 | At least 12 own tests including leakage, accounting and brute-force recommendation tests. |
| 6 | Documentation and reproducibility | 10 | A clean-environment run reproduces every table and figure. |
| 7 | Critical thinking and limitations | 10 | A validity section that names threats and ties each to a result; a clear statement of when the recommendation stops holding. |
| 8 | Presentation and communication | 5 | A head of credit risk could act on the one-page summary and challenge the details. |
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
| Simulator lets a policy read an unlabelled week | Up to -15 from dimension 2 |
| Onset or period hard-coded in a policy | Up to -8 from dimension 4 |
| Recommendation based on one seed or on mean cost only without discussion | Up to -5 from dimension 4 |
| No sensitivity to retraining cost and label delay | Up to -8 from dimension 4 |
| Claims real-world validity from synthetic regimes | Up to -4 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
