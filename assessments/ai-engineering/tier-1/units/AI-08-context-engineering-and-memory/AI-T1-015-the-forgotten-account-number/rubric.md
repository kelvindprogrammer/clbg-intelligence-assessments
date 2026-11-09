# AI-T1-015 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links each strategy's retention to a mechanism, not just a number. |
| 2 | Technical correctness | 20 | Hidden tests pass: exact arithmetic, no holes, no overflow, retention ordering. |
| 3 | Implementation quality | 15 | Token rule, fitting, compaction and metrics are separate small functions; no global state. |
| 4 | Methodology and evidence | 15 | Retention is measured on several seeds and budgets, not one conversation. |
| 5 | Testing and evaluation | 15 | At least 8 own tests including the empty list, oversize message and all-pinned cases. |
| 6 | Documentation and reproducibility | 10 | One command reproduces the retention table; seeds and budgets are stated. |
| 7 | Critical thinking and limitations | 10 | Names what the mock summariser and the fact check cannot capture (paraphrases, negations). |
| 8 | Presentation and communication | 5 | A support team lead could act on the pinning recommendation. |
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
| Underscore-prefixed mock internals imported | Up to -10 from dimension 2 |
| Budget exceeded by compaction on any tested input | Up to -6 from dimension 2 |
| Input messages mutated | Up to -4 from dimension 3 |
| Retention reported from a single conversation | Up to -6 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
