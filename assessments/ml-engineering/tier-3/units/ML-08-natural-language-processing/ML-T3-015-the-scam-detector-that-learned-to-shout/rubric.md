# ML-T3-015 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The audit identifies the mechanism of failure and why dev metrics miss it. |
| 2 | Technical correctness | 15 | Public and hidden tests pass; operating-point and counterfactual bars met on re-seeded data. |
| 3 | Implementation quality | 10 | Deterministic, batch-independent scoring; clean decomposition. |
| 4 | Methodology and evidence | 25 | Discovery from data, a defensible stress validation, mitigations compared with ablations, intervals, several seeds. |
| 5 | Testing and evaluation | 10 | At least 10 own tests including counterfactual and stress-validation checks. |
| 6 | Documentation and reproducibility | 10 | `experiments.py` regenerates every number; the threshold protocol is explicit. |
| 7 | Critical thinking and limitations | 15 | Validity and harm analysis: who is affected, small-group uncertainty, signal lost by mitigation, synthetic limits. |
| 8 | Presentation and communication | 5 | A product owner could act on the audit. |
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
| Operating threshold or model chosen using the shifted test regime | Up to -12 from dimension 2 |
| Cue hard-coded with no discovery evidence | Up to -6 from dimension 4 |
| Subgroup gaps reported without counts or intervals | Up to -4 from dimension 4 |
| Accuracy or AUC as the headline instead of the operating point | Up to -5 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
