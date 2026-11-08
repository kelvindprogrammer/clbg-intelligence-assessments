# ML-T2-024 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links the policy to the SLO, the burst and the cost of shedding, not just to average latency. |
| 2 | Technical correctness | 20 | Simulator, metrics and calibrator pass public and hidden tests; semantics are exact; held-out traffic meets the SLO. |
| 3 | Implementation quality | 15 | Clean simulator separated from tuning; invariants (one worker, conservation) hold; efficient enough for grid search. |
| 4 | Methodology and evidence | 15 | Policy search is justified; robustness to heavier traffic is built in rather than hoped for; more than one seed is used. |
| 5 | Testing and evaluation | 15 | At least 8 own tests with conservation and one-worker invariants; hand traces beyond those given. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces the trade-off table; seeds fixed; figures labelled. |
| 7 | Critical thinking and limitations | 10 | Honest account of what a simulator omits (network, variable service time, multiple models) and of how shedding affects users. |
| 8 | Presentation and communication | 5 | A platform lead could set the three parameters from the report alone. |
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
| Policy tuned and judged on the same trace only | Up to −6 from dimension 4 |
| p99 computed over shed requests as zero latency, or shed requests silently dropped from the rate | Up to −6 from dimension 2 |
| Average latency used as the headline metric | Up to −4 from dimension 4 |
| Using the true cost from `make_timings` instead of the calibrated one inside `tune_policy` | Up to −5 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
