# ML-T3-027 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report frames the clinical risk of an unfaithful explanation and states which questions the evidence can and cannot answer. |
| 2 | Technical correctness | 20 | Exactness, faithfulness, stability and audit tests pass, including hidden positions, strengths and model classes. |
| 3 | Implementation quality | 15 | Methods are cleanly separated, deterministic and efficient enough to run the full study. |
| 4 | Methodology and evidence | 15 | The study varies model class, position, strength, baseline and seed, and reports uncertainty and a clean-model control. |
| 5 | Testing and evaluation | 15 | At least 12 own tests including exactness and false-alarm tests. |
| 6 | Documentation and reproducibility | 10 | A clean-environment run reproduces every table and figure. |
| 7 | Critical thinking and limitations | 10 | A validity section that names threats and the evidence needed beyond explanations; no claim of causation from attribution. |
| 8 | Presentation and communication | 5 | A medical lead could challenge or act on the findings. |
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
| Audit uses the training set as the reference sample without discussion | Up to -6 from dimension 4 |
| Device column name or position hard-coded | Up to -8 from dimension 2 |
| Attribution described as causal effect | Up to -5 from dimension 7 |
| Single baseline, single model class or single seed in the study | Up to -6 from dimension 4 |
| Efficiency property violated by a shortcut in the Shapley code | Up to -8 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
