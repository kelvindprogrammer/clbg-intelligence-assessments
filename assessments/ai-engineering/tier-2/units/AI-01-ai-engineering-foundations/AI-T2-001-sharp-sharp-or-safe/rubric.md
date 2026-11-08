# AI-T2-001 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Memo ties each setting to the validity and diversity requirements and the cost of a wrong reply. |
| 2 | Technical correctness | 20 | Hidden tests pass: R1 to R9 exact, held-out seeds and noisier models meet the bars. |
| 3 | Implementation quality | 15 | One shared path for all configs; pure functions; seeds explicit; no global random state. |
| 4 | Methodology and evidence | 15 | Sweeps cover the knobs, use enough seeds, and report spread; the choice is justified by evidence, not by a single run. |
| 5 | Testing and evaluation | 15 | At least 10 own tests, including top-p boundary, tie handling and exact seeded replay. |
| 6 | Documentation and reproducibility | 10 | One command reproduces the table; seeds and parameter grids stated. |
| 7 | Critical thinking and limitations | 10 | States what the mock cannot show about real models, and what would change with a different tail. |
| 8 | Presentation and communication | 5 | A product lead could act on the recommendation. |
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
| Hard-coded configuration returned without searching | Up to -8 from dimension 2 |
| Choice justified from the training seeds only, no held-out check | Up to -5 from dimension 4 |
| Claim that a decoding setting makes output safe without output validation | Up to -4 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
