# AI-T1-006 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Explanations link each rule (jitter, no retry on 400, bill malformed) to a real failure mode. |
| 2 | Technical correctness | 25 | Public and hidden tests pass: exact sleeps, error classification, parsing, ledger arithmetic, stream handling. |
| 3 | Implementation quality | 15 | Small functions, clear control flow, no duplicated retry logic, deterministic. |
| 4 | Methodology and evidence | 10 | The storm experiment is run correctly and reported with numbers. |
| 5 | Testing and evaluation | 15 | At least 8 own tests including the two required; edge cases chosen deliberately. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces the report's table. |
| 7 | Critical thinking and limitations | 10 | Honest account of what the mock cannot show (real latency, provider-specific semantics). |
| 8 | Presentation and communication | 5 | A teammate could act on the report. |
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
| Real sleeping (`time.sleep`) or any network call | Up to -8 from dimension 2 |
| Retrying `BadRequestError` | -5 from dimension 2 |
| Unseeded randomness | Up to -4 from dimension 3 |
| Hard-coding the mock's script or token counting | Up to -6 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
