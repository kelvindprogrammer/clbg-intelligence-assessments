# ML-T2-029 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report ties each criterion to who is harmed and to the committee's decision. |
| 2 | Technical correctness | 20 | Public and hidden tests pass: metrics, reweighing, exhaustive search and out-of-sample bars. |
| 3 | Implementation quality | 15 | Clean separation of metrics, search and pipeline; no test-set leakage. |
| 4 | Methodology and evidence | 15 | Multi-criterion comparison over 5 or more seeds with a trade-off curve and an ablation. |
| 5 | Testing and evaluation | 15 | At least 10 own tests including independence and brute-force checks. |
| 6 | Documentation and reproducibility | 10 | A clean-environment run reproduces every table and figure. |
| 7 | Critical thinking and limitations | 10 | Honest treatment of validation noise, proxy features, group-dependent rules and the impossibility result. |
| 8 | Presentation and communication | 5 | A risk committee could act on the recommendation. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90-100% | Exceeds the requirement with insight, for example by testing a claim the brief did not ask about. |
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
| Test data used for fitting, selection or thresholds | Up to -12 from dimension 2 |
| Claims fairness is achieved because the protected attribute was removed | Up to -5 from dimension 7 |
| Reports only the constrained gap and not the other gaps or profit | Up to -5 from dimension 4 |
| Validation-only evidence for the out-of-sample claim | Up to -4 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
