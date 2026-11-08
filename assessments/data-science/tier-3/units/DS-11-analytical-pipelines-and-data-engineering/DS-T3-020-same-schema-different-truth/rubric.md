# DS-T3-020 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report ties each fault family to a business cost and a justified action, including the failure that costs the most. |
| 2 | Technical correctness | 20 | Public and hidden handling, false-alarm limits and attribution criteria are met; the gate never crashes. |
| 3 | Implementation quality | 15 | A clean architecture separating schema, rules, drift and policy; typed, deterministic and fast. |
| 4 | Methodology and evidence | 15 | Thresholds derived from clean-history variation with evidence; no tuning on the test stream; baseline policy justified. |
| 5 | Testing and evaluation | 15 | At least 12 meaningful member tests including planted faults, hostile input and threshold sensitivity. |
| 6 | Documentation and reproducibility | 10 | Reproducible analysis script; thresholds, operating characteristics and gate log regenerate. |
| 7 | Critical thinking and limitations | 10 | Honest operating characteristics; a named missed-fault scenario; limits of 15 batches and synthetic data. |
| 8 | Presentation and communication | 5 | A data steward could read the gate log and the threshold table and act. |
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
| Thresholds tuned on batches 15–29 of the public stream | Up to −8 from dimension 4 |
| Hard-coded column names for the drift test with no generalisation | Up to −5 from dimension 3 |
| Claims detection rates without a fault-injection or other measurement | Up to −6 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
