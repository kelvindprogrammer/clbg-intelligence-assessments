# DS-T2-023 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links watermark, lateness and pruning to finance consequences and states what is traded off. |
| 2 | Technical correctness | 20 | Oracle equality, memory bound and restart equivalence hold on hidden streams. |
| 3 | Implementation quality | 15 | A clean state design; pruning is safe; no re-reading of old batches; deterministic. |
| 4 | Methodology and evidence | 15 | An independent oracle, a lateness sweep as evidence and a justified recommendation. |
| 5 | Testing and evaluation | 15 | At least 10 meaningful member tests including re-splitting, restart at every cut and edge cases (lateness 0, empty batch, version ties). |
| 6 | Documentation and reproducibility | 10 | Clean-environment run works; sweep outputs and chart regenerate. |
| 7 | Critical thinking and limitations | 10 | Honest account of the limits: events whose time is corrected, clocks, concurrency, batch-level redelivery. |
| 8 | Presentation and communication | 5 | A finance lead can read the recommendation and the chart. |
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
| Oracle shares the aggregator's logic so the equality test is vacuous | Up to −8 from dimension 5 |
| State grows with the stream (no pruning) | Up to −8 from dimension 2 |
| Uses wall-clock time anywhere in the logic | Up to −5 from dimension 3 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
