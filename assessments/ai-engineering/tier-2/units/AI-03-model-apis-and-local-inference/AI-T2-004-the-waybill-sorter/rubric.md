# AI-T2-004 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Choices tied to the economics: overhead per call, quality decay, outage behaviour, billing of bad replies. |
| 2 | Technical correctness | 20 | Public and hidden tests pass: limiter semantics, zero rejections, ordering, budget, reconciliation, performance bars. |
| 3 | Implementation quality | 15 | One request path for all providers; clear separation of limiter, cache, router; small functions. |
| 4 | Methodology and evidence | 15 | Sweeps and ablations on several seeds; the baseline is the specified naive loop; noise acknowledged. |
| 5 | Testing and evaluation | 15 | At least 10 own tests including the two required; failure injection used deliberately. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces the report tables. |
| 7 | Critical thinking and limitations | 10 | What the mock cannot show: real 429 semantics, concurrency, provider drift, per-token billing differences. |
| 8 | Presentation and communication | 5 | An operations lead could decide from the report. |
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
| Real sleeping or any network call | Up to -8 from dimension 2 |
| Learning limits by triggering rejections (reactive limiter) instead of mirroring them | Up to -8 from dimension 2 |
| Hard-coding the reference provider names, limits or prices | Up to -8 from dimension 2 |
| Reporting the batch size without measured evidence | Up to -5 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
