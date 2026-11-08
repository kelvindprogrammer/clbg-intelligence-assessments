# ML-T3-007 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Frames labels as noisy measurements; understands class-conditional and annotator-conditional noise. |
| 2 | Technical correctness | 15 | Public and hidden tests pass; estimates and selection precision meet the stated bars. |
| 3 | Implementation quality | 5 | Clean, seeded, no hidden dependence on the expert labels. |
| 4 | Methodology and experimentation | 25 | Simulation study, noise-model comparison and expert-label roles are rigorous and leak-free. |
| 5 | Testing and evaluation | 10 | Own tests check methods against simulated truth. |
| 6 | Documentation and reproducibility | 5 | `experiments.py` regenerates all tables. |
| 7 | Critical thinking and limitations | 20 | Defends trade-offs between cleaning, discarding and modelling; states what the evidence cannot show; considers harm and annotator accountability. |
| 8 | Presentation and communication | 10 | Answers the officer's four questions clearly and with calibrated confidence. |
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
| Expert labels used to both tune and score a method | Up to -15 from dimension 4 |
| Accuracy reported only against the noisy labels | Up to -10 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
