# AI-T1-008 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 15 | Connects the symptom (the same long answers everywhere) to vector norms and ranks. |
| 2 | Technical correctness | 30 | Public and hidden tests pass: scoring, ties, metrics, evaluation. |
| 3 | Implementation quality | 10 | Vectorised, readable, numerically safe. |
| 4 | Methodology and evidence | 10 | The comparison table is correct and the statistic is measured, not asserted. |
| 5 | Testing and evaluation | 10 | At least 8 own tests including ties and zero vectors. |
| 6 | Documentation and reproducibility | 8 | `experiments.py` reproduces the table. |
| 7 | Critical thinking and limitations | 10 | States what a toy embedder and a synthetic world cannot show. |
| 8 | Presentation and communication | 7 | A help-desk lead could follow the explanation. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight, for example by testing a claim the brief did not ask about. |
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
| Using scikit-learn, faiss or any search library | Up to -10 from dimension 2 |
| A Python loop over documents in `scores` | -3 from dimension 3 |
| Reporting numbers that the submitted code does not reproduce | Up to -6 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
