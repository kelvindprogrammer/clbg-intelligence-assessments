# DS-T3-008 Evaluation Rubric (public)

This rubric is public so you know how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Connects clustering, design effect and heavy tails to coverage; explains why a coverage study needs a known truth. |
| 2 | Technical correctness | 20 | Public and hidden tests pass; estimators and intervals behave as specified in unseen regimes. |
| 3 | Implementation quality | 10 | Vectorised bootstrap; no Python loops over bootstrap draws; deterministic seeding with independent streams. |
| 4 | Methodology and experimentation | 25 | Grid, replication count, common random numbers and ablation are justified; Monte Carlo error is reported for every coverage figure. |
| 5 | Testing and evaluation | 10 | Hand-checkable cases and the zero-SE edge case; sanity checks of the estimator against the generator's known ICC. |
| 6 | Documentation and reproducibility | 5 | One command reproduces the table and figure; environment pinned. |
| 7 | Critical thinking and limitations | 15 | Mechanism of failure explained from the member's own runs; scope limits and DGP mismatch discussed; no overclaiming from simulation. |
| 8 | Presentation and communication | 5 | Figure and table readable, titled by finding, with error bars; recommendation understandable to an actuary. |
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
| Coverage reported without Monte Carlo error | Up to -6 from dimension 4 |
| Bootstrap implemented with a Python loop over draws making the grid impractical | Up to -4 from dimension 3 |
| Modified `dgp.py` | Gate fail until corrected |
| Different methods compared on different random datasets without comment | Up to -4 from dimension 4 |

Outcome bands: [placement framework](../../../../../../docs/placement-framework.md).
