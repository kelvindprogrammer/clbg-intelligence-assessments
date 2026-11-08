# ML-T3-005 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Frames existence of structure as a testable claim; understands what each null and statistic assumes. |
| 2 | Technical correctness | 15 | Public and hidden tests pass; no-structure populations reported as one segment; exact k on hidden segmented populations. |
| 3 | Implementation quality | 5 | Clean, deterministic, unit-invariant code. |
| 4 | Methodology and experimentation | 25 | Ablations, null comparison and calibration are well designed, seeded and fair; thresholds chosen without peeking at the target file. |
| 5 | Testing and evaluation | 10 | Own tests capture failure modes; evaluation covers false discovery and missed discovery. |
| 6 | Documentation and reproducibility | 5 | `experiments.py` regenerates all tables. |
| 7 | Critical thinking and limitations | 20 | Defends trade-offs, states what the evidence cannot show, and discusses fairness of acting on segments. |
| 8 | Presentation and communication | 10 | The verdict is clear to a non-technical board; figures and tables carry the argument. |
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
| Decision thresholds tuned on the cooperative file itself | Up to -15 from dimension 4 |
| Verdict reports a cluster count with no uncertainty or null comparison | Up to -10 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
