# ML-T1-004 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report explains why a split is chosen, why thresholds sit between distinct values, and why greedy gain can fail on XOR. |
| 2 | Technical correctness | 20 | Public and hidden tests pass, including agreement with scikit-learn on re-seeded data and the edge cases. |
| 3 | Implementation quality | 15 | Clear recursive structure, vectorised split search, no copying of data at every node beyond what is needed, deterministic. |
| 4 | Methodology and evidence | 15 | Depth sweep and XOR experiment are reproducible and interpreted, not just plotted. |
| 5 | Testing and evaluation | 15 | At least 8 own tests including degenerate inputs (pure node, constant feature, one sample). |
| 6 | Documentation and reproducibility | 10 | Clean-environment run works first time; report numbers regenerate from a script. |
| 7 | Critical thinking and limitations | 10 | Honest discussion of greedy search, instability of trees and limits of the synthetic data. |
| 8 | Presentation and communication | 5 | Rules a field officer could read; a concise report. |
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
| Calling scikit-learn tree code inside the implementation | Disqualifies the affected requirement |
| Split search that is O(n²) per feature (fails the timing test) | Up to −5 from dimension 3 |
| Hard-coded thresholds or features from the visible data | Up to −10 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
