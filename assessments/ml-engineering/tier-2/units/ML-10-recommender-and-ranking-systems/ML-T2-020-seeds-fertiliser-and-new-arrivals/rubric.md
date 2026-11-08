# ML-T2-020 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links each choice to the launch-day problem and the cost of recommending to the wrong farmer. |
| 2 | Technical correctness | 20 | Public and hidden tests pass: exact metric and split, bars met on re-seeded data. |
| 3 | Implementation quality | 15 | Single code path for all candidates; deterministic; clean separation of train, validation and test. |
| 4 | Methodology and evidence | 15 | Validation window is built from training data, mimics deployment, and its effect on selection is shown. |
| 5 | Testing and evaluation | 15 | At least 10 own tests including no-future-data and cold-item tests. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces the comparison table; seeds fixed. |
| 7 | Critical thinking and limitations | 10 | Honest about attribute quality, novelty effects and monitoring needs. |
| 8 | Presentation and communication | 5 | A product team could decide what to ship and what to watch. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90-100% | Exceeds the requirement with insight, for example by quantifying uncertainty or testing a claim the brief did not ask about. |
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
| Test-period data used to fit, select or tune | Up to -12 from dimension 2 |
| Item statistics computed from test-period behaviour | Up to -10 from dimension 2 |
| Random split of purchases | Up to -6 from dimension 4 |
| Training items recommended or counted as hits | Up to -4 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
