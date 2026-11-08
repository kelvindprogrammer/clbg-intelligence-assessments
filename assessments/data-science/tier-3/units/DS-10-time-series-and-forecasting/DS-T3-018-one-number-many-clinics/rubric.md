# DS-T3-018 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links each reconciler's assumption to where the information lives and to what the transfer event breaks. |
| 2 | Technical correctness | 20 | Algebraic properties hold; shrinkage formula matches; hidden robustness and detection criteria are met. |
| 3 | Implementation quality | 15 | Clear numerical code with a well-structured study, no leakage, deterministic, within the time budget. |
| 4 | Methodology and evidence | 15 | A well-designed evaluation with ablations, uncertainty quantification and a justified detector, tied to the literature. |
| 5 | Testing and evaluation | 15 | At least 12 meaningful member tests covering algebraic properties, edge cases and leakage. |
| 6 | Documentation and reproducibility | 10 | Reproducible analysis script; figures and tables regenerate; sources cited. |
| 7 | Critical thinking and limitations | 10 | A proportionate conclusion on a small effect; limits of one synthetic process stated; false-alarm behaviour of the detector assessed. |
| 8 | Presentation and communication | 5 | A decision-maker could act on the recommendation and see why. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight, for example by quantifying a risk or testing an assumption unprompted. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps that do not affect trustworthiness. |
| **Developing** | 50–69% | Partly meets the requirement: some choices unjustified or untested. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. |

## Gates (pass/fail, independent of points)

1. **Integrity:** the AI-use declaration in `REPORT.md` is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns your tests from a clean environment and gets your reported results.
3. **Defence:** you trace assessor-chosen cases and handle the unseen modification with sound reasoning.
4. **Privacy and safety:** no personal data in the report; any safeguards required in §D.3 are present.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Reconciler uses information from after the origin | Up to −10 from dimension 2 |
| Claims an improvement without any uncertainty measure | Up to −6 from dimension 7 |
| Detector tuned on the public file's known answer without a false-alarm assessment | Up to −6 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
