# ML-T2-014 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report characterises the camera shift from data and links each design choice to it. |
| 2 | Technical correctness | 20 | Public and hidden tests pass: augmentation contract, metrics exact, bars met on re-seeded field and lab data. |
| 3 | Implementation quality | 15 | Deterministic, modular code; augmentation and features share one clean path for every candidate. |
| 4 | Methodology and evidence | 15 | Per-camera, per-class results over several seeds; component ablation; honest selection on the small validation set. |
| 5 | Testing and evaluation | 15 | At least 8 own tests including non-mutation and row independence. |
| 6 | Documentation and reproducibility | 10 | `experiments.py` reproduces every table and figure. |
| 7 | Critical thinking and limitations | 10 | Honest treatment of validation noise, synthetic data and what the model cannot see. |
| 8 | Presentation and communication | 5 | A programme lead could act on the memo. |
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
| Test images used for fitting, augmenting-to-match or selecting | Up to -12 from dimension 2 |
| Model selected on lab accuracy only | Up to -5 from dimension 4 |
| Batch statistics used at prediction time | Up to -5 from dimension 2 |
| Accuracy as the only headline metric | Up to -3 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
