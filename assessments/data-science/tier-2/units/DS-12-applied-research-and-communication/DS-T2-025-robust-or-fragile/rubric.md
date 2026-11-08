# DS-T2-025 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report explains why the answers differ, why two variables are bad controls, and what the estimand is. |
| 2 | Technical correctness | 20 | Estimators and the curve match independent computations; the expected bias structure appears; E-value is right. |
| 3 | Implementation quality | 15 | Clean estimator code from the equations; reusable curve machinery; seeded and deterministic. |
| 4 | Methodology and evidence | 15 | The list of bad controls is argued from causal structure before inspecting the curve; the sensitivity analysis is interpreted. |
| 5 | Testing and evaluation | 15 | At least 10 meaningful member tests including cross-checks against a library and edge cases (perfect separation guard, empty control set). |
| 6 | Documentation and reproducibility | 10 | Clean-environment run works; the curve, figure and E-values regenerate. |
| 7 | Critical thinking and limitations | 10 | A conclusion proportionate to robustness; limits named (constant effect, measured confounders, one outcome, synthetic data). |
| 8 | Presentation and communication | 5 | A programme officer can read the summary and know what to believe. |
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
| Bad controls chosen by looking at which makes the result significant | Up to −8 from dimension 4 |
| A regression or propensity routine taken from a library for the estimators | Up to −8 from dimension 3 |
| Report claims a causal effect size without the curve or sensitivity analysis | Up to −6 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
