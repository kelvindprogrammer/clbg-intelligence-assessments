# ML-T2-022 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links each choice to the flash budget and the cost of wrong decisions at the node. |
| 2 | Technical correctness | 20 | Public and hidden tests pass; the arithmetic of R1 to R3 is exact; budgets and accuracy bars are met on re-seeded models. |
| 3 | Implementation quality | 15 | Shared evaluation path; no input mutation; clean separation of quantiser, pruner, storage model and search. |
| 4 | Methodology and evidence | 15 | Baselines are fair and at equal size; the saving is attributed by ablation rather than asserted; selection uses only calibration data. |
| 5 | Testing and evaluation | 15 | At least 8 own tests including bounds and identities; sensitivity of layers examined. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces the table across at least 5 seeds; seeds fixed. |
| 7 | Critical thinking and limitations | 10 | Honest treatment of calibration noise, synthetic data and rare-class risk; states when sparse storage does not pay. |
| 8 | Presentation and communication | 5 | The firmware team could act on the memo without asking questions. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight, for example by quantifying uncertainty or testing a claim the brief did not ask about. |
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
| Test split used to choose bits, sparsity or thresholds | Up to −12 from dimension 2 |
| Storage reported by parameter count rather than by the R3 model | Up to −6 from dimension 4 |
| Compression claimed from one seed only | Up to −4 from dimension 4 |
| Quantisation applied to biases without the report saying so, while R3 counts them as float32 | Up to −3 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
