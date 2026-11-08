# ML-T3-017 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links regime change, detection delay and calibration to real decisions by traders and the food office. |
| 2 | Technical correctness | 15 | Public and hidden tests pass; interfaces and scaling behave; bars met on unseen seeds. |
| 3 | Implementation quality | 10 | Harness is shared across strategies; no leakage of the break week; clean and deterministic. |
| 4 | Methodology and evidence | 20 | Ablations isolate each decision, with control series, six or more seeds and spreads; early-origin analysis included. |
| 5 | Testing and evaluation | 10 | At least 10 own tests, including history-only, unit-scaling and false-alarm tests. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces every table and figure; seeds fixed. |
| 7 | Critical thinking and limitations | 20 | Honest treatment of the single-step-shock assumption, the weeks with almost no new data, and what the generator cannot represent. |
| 8 | Presentation and communication | 5 | A food-security office could apply the recommended policy from the summary. |
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
| Break week read from the generator or hard-coded | Up to -10 from dimension 2 |
| Fitting or choosing a window with data after the forecast origin | Up to -10 from dimension 2 |
| Point error only; intervals never scored | Up to -5 from dimension 4 |
| No control series or false-alarm check | Up to -3 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
