# AI-T1-012 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Explains how each mock mode reaches a different branch of the loop and why. |
| 2 | Technical correctness | 20 | Hidden tests pass: exact validation, parsing edge cases, contained exceptions, bounded runaway, redaction. |
| 3 | Implementation quality | 15 | Small single-purpose functions; no shared mutable state; clear names. |
| 4 | Methodology and evidence | 15 | Report trace table covers every mock mode and matches the code. |
| 5 | Testing and evaluation | 15 | At least 8 own tests including a raising tool and a brace-in-string case. |
| 6 | Documentation and reproducibility | 10 | One command reproduces the trace table; settings stated. |
| 7 | Critical thinking and limitations | 10 | States what validation cannot catch (a valid call with a harmful intent) and what to log. |
| 8 | Presentation and communication | 5 | Short and clear enough for a new teammate to follow. |
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
| Tool exceptions allowed to escape `call` or `run_agent` | Up to -8 from dimension 2 |
| Parsing by regular expression that fails on braces inside strings | Up to -5 from dimension 2 |
| `eval`, `exec` or `ast.literal_eval` used on model text | Up to -10 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
