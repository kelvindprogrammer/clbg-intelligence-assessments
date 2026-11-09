# AI-T2-013 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The memo ties each safeguard to a measured failure it prevents and its cost. |
| 2 | Technical correctness | 20 | Hidden tests pass: exact schedules, error lists, clean audits, approval and compensation behaviour. |
| 3 | Implementation quality | 15 | Validation, scheduling, calling, saga and audit are separate and testable; the clock is injected. |
| 4 | Methodology and evidence | 15 | Ablations (no idempotency, no failed-step undo, sequential) are measured on several seeds. |
| 5 | Testing and evaluation | 15 | At least 12 own tests with scripted failures for each kind and an idempotency ablation. |
| 6 | Documentation and reproducibility | 10 | One command reproduces the table; seeds and rates are stated. |
| 7 | Critical thinking and limitations | 10 | Names what the audit cannot see (external effects, SMS already sent) and what remains manual. |
| 8 | Presentation and communication | 5 | An operations lead could adopt the recommended budgets. |
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
| Underscore-prefixed mock internals imported or the audit recomputed from mock internals | Up to -10 from dimension 2 |
| Permanent errors retried | Up to -4 from dimension 2 |
| Money moved before a required approval | Up to -8 from dimension 2 |
| Real sleeping or wall-clock time | Up to -4 from dimension 3 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
