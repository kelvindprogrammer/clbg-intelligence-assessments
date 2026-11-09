# AI-T1-010 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Explains where each stage can fail and ties the experiment to those failures. |
| 2 | Technical correctness | 20 | Hidden tests pass: exact BM25, chunk invariants, withheld forged answers, recall on an unseen seed. |
| 3 | Implementation quality | 15 | Small, single-purpose functions; no recomputation of state; clear names. |
| 4 | Methodology and evidence | 15 | Chunking experiment uses at least four size/overlap settings and counts intact fact sentences. |
| 5 | Testing and evaluation | 15 | At least 8 own tests including a hand-computed score and each verdict. |
| 6 | Documentation and reproducibility | 10 | One command reproduces every number; seeds stated. |
| 7 | Critical thinking and limitations | 10 | States what citation checking cannot catch (a real chunk cited for a false claim) and logging risks. |
| 8 | Presentation and communication | 5 | Table and explanations a cooperative secretary could follow. |
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
| Citation check compares against the whole corpus instead of the retrieved set | Up to -8 from dimension 2 |
| Underscore-prefixed internals imported from `resources/` | Up to -5 from dimension 2 |
| BM25 or tokenizer taken from a library instead of implemented | Up to -10 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
