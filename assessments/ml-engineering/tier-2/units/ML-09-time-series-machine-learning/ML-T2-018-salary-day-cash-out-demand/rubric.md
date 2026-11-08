# ML-T2-018 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report ties every feature to the cash-out mechanism (payday, eve, market day) and the cost of a stock-out. |
| 2 | Technical correctness | 20 | Public and hidden tests pass: causal features, exact metrics, holdout bar met on re-seeded data. |
| 3 | Implementation quality | 15 | Pipeline is causal, deterministic and modular; candidates share one code path. |
| 4 | Methodology and evidence | 15 | Comparison uses rolling origins, several seeds and a baseline; uncertainty of the selection is quantified. |
| 5 | Testing and evaluation | 15 | At least 10 own tests including future-poisoning and closed-day tests. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces the comparison table; seeds fixed. |
| 7 | Critical thinking and limitations | 10 | Honest about the four-origin validation window, payday sample size and drift risk. |
| 8 | Presentation and communication | 5 | Operations lead could size float from the memo. |
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
| Final-28-day data used for fitting, scaling or selection | Up to -12 from dimension 2 |
| Features that include the target day or later | Up to -8 from dimension 2 |
| Random K-fold across origins | Up to -5 from dimension 4 |
| MAPE as the headline metric with zero-volume days | Up to -4 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
