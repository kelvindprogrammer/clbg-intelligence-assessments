# AI-T1-004 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Report ties each component to a concrete failure it prevents and one it cannot. |
| 2 | Technical correctness | 20 | Hidden tests pass: R1 to R8 exact, fuzzed extraction and fence, injection fails. |
| 3 | Implementation quality | 15 | Small pure functions, no hidden global state, clear errors. |
| 4 | Methodology and evidence | 15 | Mock failure modes are each exercised and the flaky success rate is measured, not assumed. |
| 5 | Testing and evaluation | 15 | At least 8 own tests including injection and every mock mode. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces numbers in the report. |
| 7 | Critical thinking and limitations | 10 | States the limits of fencing and of schema validation (valid is not true). |
| 8 | Presentation and communication | 5 | A cooperative engineer could follow the explanation. |
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
| Prompt-templating or JSON-repair library used | Up to -15 from dimension 2 |
| `extract_json` implemented with a greedy regex that fails on braces in strings | Up to -6 from dimension 2 |
| Claim that fencing eliminates prompt injection | Up to -4 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
