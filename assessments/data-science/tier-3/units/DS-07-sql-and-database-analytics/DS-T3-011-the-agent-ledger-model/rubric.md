# DS-T3-011 Evaluation Rubric (public)

This rubric is public so you know how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The design records show an understanding of event-sourcing, temporal validity and why each noise pattern matters to Finance. |
| 2 | Technical correctness | 25 | Public and hidden tests pass; semantics (version resolution, boundaries, as-of rates, exceptions precedence) are exact. |
| 3 | Implementation quality | 10 | Layered build (staging, dimension, fact, marts), readable SQL, idempotent, no duplicated logic. |
| 4 | Methodology and experimentation | 15 | Type 1 impact is measured from the build; alternatives in the decision records are weighed against this data. |
| 5 | Testing and evaluation | 15 | Constructed edge cases (boundary date, amend after reverse, duplicate delivery) and invariants (reconciliation, no gaps) are tested. |
| 6 | Documentation and reproducibility | 10 | DESIGN.md and REPORT.md numbers regenerate from the repository; clean run from scratch. |
| 7 | Critical thinking and limitations | 10 | Staleness, incremental-load risks and back-dated corrections are discussed honestly with the cost of each choice. |
| 8 | Presentation and communication | 5 | Decision records are concise, and the report is readable by a finance lead. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90-100% | Exceeds the requirement with insight, for example by quantifying uncertainty or testing an assumption nobody asked about. |
| **Proficient** | 70-89% | Fully meets the requirement with minor gaps that do not affect trustworthiness. |
| **Developing** | 50-69% | Partly meets the requirement; some claims are unjustified or untested. |
| **Beginning** | 0-49% | Missing, incorrect or unexplained. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns your work from a clean environment and obtains the submitted results.
3. **Defence:** you trace assessor-chosen results and handle an unseen modification with sound reasoning.
4. **Privacy and ethics:** no real personal data is introduced; any limits stated in §D are respected.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Exceptions or reversed transactions silently dropped (reconciliation does not close) | Up to -10 from dimension 2 |
| Agent, date or currency hard-coded | Up to -10 from dimension 2 |
| Raw tables modified by the build | Gate fail until corrected |
| Report figures not regenerable | Up to -5 from dimension 6 |

Outcome bands: [placement framework](../../../../../../docs/placement-framework.md).
