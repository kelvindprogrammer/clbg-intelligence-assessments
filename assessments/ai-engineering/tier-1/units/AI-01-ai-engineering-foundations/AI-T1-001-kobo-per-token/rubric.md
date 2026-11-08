# AI-T1-001 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Report connects the tokenisation mechanism to the finance team's observation. |
| 2 | Technical correctness | 20 | Hidden tests pass: merge order, ties, early stop, vocabulary ids and integer cost are exact. |
| 3 | Implementation quality | 15 | Counting and merging are clear, deterministic and do not mutate inputs; no hidden global state. |
| 4 | Methodology and evidence | 15 | Fertility is measured per language, for two training mixes, with the same code path. |
| 5 | Testing and evaluation | 15 | At least 8 own tests, including a hand-computed tie-break and a round-trip property. |
| 6 | Documentation and reproducibility | 10 | One command reproduces the table; seeds and merge counts stated. |
| 7 | Critical thinking and limitations | 10 | States what a synthetic corpus cannot show; no claim about real Yoruba usage. |
| 8 | Presentation and communication | 5 | A finance lead could follow the explanation and the proposed mitigation. |
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
| Third-party tokeniser or BPE library used | Up to -20 from dimension 2 |
| Ties broken by dict or insertion order rather than the specified rule | Up to -6 from dimension 2 |
| Conclusion about real Yoruba speakers drawn from the synthetic corpus | Up to -4 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
