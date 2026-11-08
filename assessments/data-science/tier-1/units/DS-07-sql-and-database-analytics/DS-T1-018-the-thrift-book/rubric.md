# DS-T1-018 Evaluation Rubric (public)

This rubric is public so you know how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report explains what each question needs (which rows must survive a join) and why the naive version fails, using numbers from the data. |
| 2 | Technical correctness | 25 | Public and hidden tests pass; q04 is immune to fan-out; ties and NULL handled as specified. |
| 3 | Implementation quality | 15 | Readable one-clause-per-line SQL, aliases, CTEs where they help, no repeated subqueries copy-pasted without reason. |
| 4 | Methodology and verification | 15 | Each answer is reconciled (e.g. q01 total equals the sum of contributions; q09 copies explain the gap) before it is trusted. |
| 5 | Testing and evaluation | 10 | Evidence of checking beyond the provided tests: spot checks, row-count reconciliations, a deliberately broken variant. |
| 6 | Documentation and reproducibility | 10 | Queries run from a clean checkout; comments explain non-obvious choices. |
| 7 | Critical thinking and limitations | 10 | Treats double postings and overpayments as findings to escalate, not as noise to delete; states the limits of one year of data. |
| 8 | Presentation and communication | 5 | The report is short and readable by a treasurer. |
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
| A query pastes literal results or IDs | Up to -10 from dimension 2 |
| A query modifies the database or its schema | Gate fail until corrected |
| Report numbers cannot be reproduced from the queries | Up to -5 from dimension 6 |

Outcome bands: [placement framework](../../../../../../docs/placement-framework.md).
