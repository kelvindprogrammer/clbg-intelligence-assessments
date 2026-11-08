# ML-T1-007 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Correctly explains what each step of the algorithm optimises and why seeding and restarts matter. |
| 2 | Technical correctness | 25 | Public and hidden tests pass; inertia within 1% of scikit-learn; silhouette exact; hidden grouping recovered. |
| 3 | Implementation quality | 15 | Vectorised, readable, pure functions, no global state, clear handling of degenerate cases. |
| 4 | Methodology and validation | 10 | Verifies against references and hand examples before trusting the code; uses the k table sensibly. |
| 5 | Testing and evaluation | 15 | At least 5 meaningful own tests including a self-found degenerate case; tests would fail if the update step regressed. |
| 6 | Documentation and reproducibility | 10 | `analysis.py` regenerates the report numbers from a clean environment. |
| 7 | Critical thinking and limitations | 10 | Names real failure conditions of k-means and silhouette, with reasons. |
| 8 | Presentation and communication | 5 | Short, clear, readable by an operations manager. |
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
| scikit-learn used inside the package | Up to -15 from dimension 2 |
| Test weakened or special-cased to the public data | Up to -10 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
