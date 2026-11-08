# DS-T2-007 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You explain why raw correlations mislead here (national shocks, trends, seasonality, search) and what your register's statuses mean for a food-security decision. |
| 2 | Technical correctness | 20 | Hidden-panel recall, FDR, lag accuracy and baseline margins meet the thresholds; q-values are genuine multiplicity adjustments; p-values account for the lag/feature search. |
| 3 | Implementation quality | 10 | Modular preparation, feature, inference and reporting code; vectorised where it matters; deterministic; runs well inside 5 minutes. |
| 4 | Methodology and experimentation | 20 | Exploration that visibly drives the method; a simulation study on several panels with known truth; a fair baseline comparison; a sensitivity analysis naming robust claims. |
| 5 | Testing and evaluation | 15 | At least 10 member tests, including anomaly construction on a hand-made series and a null-calibration test (roughly uniform p-values with no links). |
| 6 | Documentation and reproducibility | 10 | The register and every figure regenerate from code; commit history shows exploration before the final method. |
| 7 | Critical thinking and limitations | 10 | Informative missingness detected and discussed; association versus causation; what the FDR guarantees and what it does not; honest reporting of what failed in the simulation. |
| 8 | Presentation and communication | 5 | The register is usable by a non-statistician: clear statuses, effects in interpretable units, concrete follow-ups. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Goes beyond the requirement, e.g. partial pooling across states, or the real-data replication with an honest result. |
| **Proficient** | 70–89% | Fully meets the requirement; the method is sound and validated, with minor gaps in sensitivity or discussion. |
| **Developing** | 50–69% | A reasonable method, but weak validation (no simulation, or no null calibration) or unadjusted search. |
| **Beginning** | 0–49% | Raw correlations, best-lag p-values without adjustment, or no baseline comparison. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** the assessor regenerates `outputs/hypothesis_register.csv` from a clean environment.
3. **Defence:** the member traces one supported and one unsupported pair from raw data to q-value and predicts the effect of a live perturbation.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Data modified (checksum mismatch) | Gate fail until corrected |
| States, commodities or lags hard-coded into `build_register` | Up to −15 from dimension 2 |
| A simulator that copies or reverse-engineers the assessor's data rather than testing the method | Up to −5 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
