# DS-T2-020 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report explains why calibration matters to the planner and why outages and level shifts need explicit treatment. |
| 2 | Technical correctness | 20 | Hidden accuracy, calibration and detection thresholds are met; no peeking. |
| 3 | Implementation quality | 15 | A clean harness, one clear forecaster, no copy-paste, deterministic, within the time budget. |
| 4 | Methodology and evidence | 15 | Method choice is argued from evidence in the data, with at least one alternative tried or reasoned away. |
| 5 | Testing and evaluation | 15 | At least 10 meaningful member tests, including a leak test and an interval-validity test. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run works; reported numbers regenerate. |
| 7 | Critical thinking and limitations | 10 | Honest per-series reporting, including losses, and limits of 11 origins on synthetic data. |
| 8 | Presentation and communication | 5 | A planner could read the report and know how far to trust the intervals. |
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
| Forecaster uses data after the origin | Up to −10 from dimension 2 |
| Intervals tuned on the test windows | Up to −8 from dimension 2 |
| Report averages hide a feeder that loses to the baseline | Up to −4 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
