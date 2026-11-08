# ML-T2-001 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report separates the three causes (numerical error, non-identifiability, distribution shift) and links each to evidence. |
| 2 | Technical correctness | 20 | Public and hidden tests pass; the chosen model beats the raw normal-equation baseline by the stated margin on re-seeded data with different collinear structure. |
| 3 | Implementation quality | 15 | Solvers share a clear interface, preprocessing is fitted on training data only, no leakage, deterministic. |
| 4 | Methodology and evidence | 15 | Solver comparison is a controlled experiment (same data, stated metrics, repeated over seeds), not a single run. |
| 5 | Testing and evaluation | 15 | At least 10 own tests covering solver agreement on easy data, failure on hard data, and leakage. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces the comparison table exactly. |
| 7 | Critical thinking and limitations | 10 | Honest account of what the model cannot know: sensor recalibration, extrapolation to hotter weather, collinear coefficient meaning. |
| 8 | Presentation and communication | 5 | A feeder engineer could act on the report; the table and figure are legible. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight, for example by quantifying uncertainty or testing a claim the brief did not ask about. |
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
| Preprocessing (means, scales, CV folds) fitted using test-period data | Up to −10 from dimension 2 |
| Shuffled K-fold used on time-ordered data without comment | Up to −5 from dimension 4 |
| Hard-coding column indices of the collinear sensors | Up to −10 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
