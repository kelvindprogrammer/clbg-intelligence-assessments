# AI-T3-003 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 12 | Frames recall, cost, segments and drift as one decision problem with a stated harm. |
| 2 | Technical correctness | 18 | Public and hidden tests pass for the index, accounting, configuration choice and policy. |
| 3 | Implementation quality | 10 | Vectorised, readable, deterministic; accounting separated from search logic. |
| 4 | Methodology and evidence | 22 | Evaluation-set design, frontier with uncertainty, decay curve, calibration separate from validation, three sensitivities. |
| 5 | Testing and evaluation | 10 | At least 12 own tests including invariants. |
| 6 | Documentation and reproducibility | 8 | Clean-environment run reproduces every number. |
| 7 | Critical thinking and limitations | 15 | Specific validity threats, fairness discussion, honest account of the proxy and the generator. |
| 8 | Presentation and communication | 5 | An engineering manager could adopt the policy from the report. |
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
| Calibrating the rebuild thresholds on the hidden-test worlds or on the public test queries without a separate validation world | Up to -8 from dimension 4 |
| Reporting only average recall with no segment breakdown | Up to -6 from dimension 4 |
| Treating `ndist` as wall-clock latency without qualification | Up to -4 from dimension 7 |
| Using faiss, scikit-learn or another index library | Up to -10 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
