# AI-T2-002 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Memo ties each policy choice to measured cost, latency and risk. |
| 2 | Technical correctness | 20 | Hidden tests pass: exact schedules, grounding, zero wrong accepts, bad-key behaviour, policy generalisation. |
| 3 | Implementation quality | 15 | Retry, validation, pipeline and policy search are separate and testable; the virtual clock is injected. |
| 4 | Methodology and evidence | 15 | Policies are compared on several seeds and mocks with cost and latency, not a single run. |
| 5 | Testing and evaluation | 15 | At least 12 own tests with scripted failures for each kind. |
| 6 | Documentation and reproducibility | 10 | One command reproduces the table; seeds and rates stated. |
| 7 | Critical thinking and limitations | 10 | States what grounding and screening cannot catch, and the data-handling consequences. |
| 8 | Presentation and communication | 5 | An operations lead could adopt the recommendation. |
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
| Underscore-prefixed mock internals imported or the labelled truth recomputed from the mock | Up to -15 from dimension 2 |
| Auth or unknown errors retried | Up to -5 from dimension 2 |
| Record accepted on schema validity alone | Up to -6 from dimension 2 |
| Real sleeping or wall-clock time in the harness | Up to -4 from dimension 3 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
