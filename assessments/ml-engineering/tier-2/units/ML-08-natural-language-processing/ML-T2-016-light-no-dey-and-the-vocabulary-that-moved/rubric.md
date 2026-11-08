# ML-T2-016 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links every choice to drift, imbalance and the review budget. |
| 2 | Technical correctness | 20 | Public and hidden tests pass: corruption, metric and routing exact; bars met on re-seeded data. |
| 3 | Implementation quality | 15 | Deterministic, modular code; all candidates share one evaluation path. |
| 4 | Methodology and evidence | 15 | Saturation shown, a defensible stress validation, several seeds, a fair baseline comparison. |
| 5 | Testing and evaluation | 15 | At least 10 own tests including non-mutation and per-message independence. |
| 6 | Documentation and reproducibility | 10 | `experiments.py` regenerates every number. |
| 7 | Critical thinking and limitations | 10 | Honest treatment of what no stress test can show: genuinely new words and meanings. |
| 8 | Presentation and communication | 5 | A contact-centre head could act on the memo. |
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
| Post-reform data used for fitting, tuning or selecting | Up to -12 from dimension 2 |
| Model chosen on the plain early validation set alone | Up to -5 from dimension 4 |
| Accuracy rather than macro-F1 as headline | Up to -3 from dimension 4 |
| Confidence assumed informative without checking | Up to -4 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
