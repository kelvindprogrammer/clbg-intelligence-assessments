# AI-T1-014 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links each design choice (copies, limits, retry scope) to a failure it prevents. |
| 2 | Technical correctness | 20 | Hidden tests pass: exact statuses, traces, errors, limits, checkpoints, validation. |
| 3 | Implementation quality | 15 | Engine, graph builder and validation are separate; no global state; steps are pure with respect to inputs. |
| 4 | Methodology and evidence | 15 | Claims in the report are backed by traces or test output. |
| 5 | Testing and evaluation | 15 | At least 8 own tests including cycle, double pause and non-transient error. |
| 6 | Documentation and reproducibility | 10 | One command reproduces the report traces; the document explains the data model. |
| 7 | Critical thinking and limitations | 10 | Names what the validator cannot catch (labels a step never emits) and what a human queue costs. |
| 8 | Presentation and communication | 5 | A mentor could follow the argument for workflow over agent. |
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
| Exceptions escape `run_workflow` | Up to -5 from dimension 2 |
| Steps receive and mutate the live state object | Up to -5 from dimension 3 |
| Hard-coded replies or totals for the visible messages | Up to -10 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
