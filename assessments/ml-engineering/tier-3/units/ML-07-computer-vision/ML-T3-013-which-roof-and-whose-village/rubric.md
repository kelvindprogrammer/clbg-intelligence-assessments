# ML-T3-013 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The memo answers the director's four questions and links each to spatial structure. |
| 2 | Technical correctness | 15 | Public and hidden tests pass; splits, intervals and features behave as specified; bars met on re-seeded worlds. |
| 3 | Implementation quality | 10 | Deterministic, modular code; no statistic leaks from held-out villages. |
| 4 | Methodology and evidence | 25 | Blocked versus random gap, label-efficiency curves with repeated draws, well-designed ablations, cluster intervals. |
| 5 | Testing and evaluation | 10 | At least 10 own tests including leakage and interval-width checks. |
| 6 | Documentation and reproducibility | 10 | `experiments.py` regenerates every number; seeds and protocols stated. |
| 7 | Critical thinking and limitations | 15 | Validity argument: what synthetic villages cannot show, ground-colour dependence, small number of villages, who is harmed by errors. |
| 8 | Presentation and communication | 5 | A programme director could act on the memo. |
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
| Statistics (dictionary, scaler, normalisation) computed using held-out villages | Up to -12 from dimension 2 |
| Tile-level cross-validation used to select models | Up to -6 from dimension 4 |
| Intervals that treat tiles as independent | Up to -4 from dimension 4 |
| Real-world accuracy claims from synthetic results | Up to -4 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
