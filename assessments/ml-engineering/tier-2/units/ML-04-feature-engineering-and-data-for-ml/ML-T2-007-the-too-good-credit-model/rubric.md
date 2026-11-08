# ML-T2-007 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Explains how each leak arises and why timing, not correlation alone, is the test. |
| 2 | Technical correctness | 20 | Public and hidden tests pass; exact leak set; honest AUC in range; PSI exact. |
| 3 | Implementation quality | 10 | Clean, seeded, no label use outside evaluation. |
| 4 | Methodology and experimentation | 25 | Per-leak and per-split ablations are fair and informative; evidence threshold is justified. |
| 5 | Testing and evaluation | 10 | Own tests guard against reintroduced leaks and bad splits. |
| 6 | Documentation and reproducibility | 5 | `analysis.py` regenerates all tables. |
| 7 | Critical thinking and limitations | 15 | Questions the dictionary, quantifies uncertainty, names harms and reviewers. |
| 8 | Presentation and communication | 5 | Committee-ready finding up front. |
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
| A leaked feature retained in the honest model | Up to -15 from dimension 2 |
| Dictionary trusted without any statistical check | Up to -5 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
