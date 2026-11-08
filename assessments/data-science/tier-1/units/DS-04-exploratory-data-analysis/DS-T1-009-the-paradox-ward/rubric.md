# DS-T1-009 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 15 | You explain *why* the crude ranking misleads (case mix, not care), in words the Commissioner could repeat. You identify which comparison is fair and why. |
| 2 | Technical correctness | 20 | R1–R7 match the oracle on re-generated data; `build_findings` finds the referral centre and confounder without hard-coding; the decomposition adds up. |
| 3 | Implementation quality | 10 | Small, readable functions; no mutation of inputs; no copy-pasted blocks per hospital; the CLI is deterministic. |
| 4 | Exploratory methodology | 15 | You examined several stratifiers and pairs, not just the one that "works"; case-mix and stratified figures with intervals; the order of exploration is visible and reproducible. |
| 5 | Testing and evaluation | 10 | At least 8 member tests with hand-computed answers, covering edge cases: a missing stratum, `min_n` exclusion, ties, a two-group table. |
| 6 | Documentation and reproducibility | 10 | The exploration code regenerates every number in `FINDINGS.md`; the README run instructions work first time. |
| 7 | Critical thinking and limitations | 15 | Small cells are flagged and not over-read; `referral_source` is explained as a proxy; at least two concrete reasons the data cannot prove one hospital's care is better. |
| 8 | Presentation and communication | 5 | A Commissioner can act on the report. Every claim is quantified, figures are labelled with interval bars, and no row-level data appears. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Goes beyond the requirement with insight. For example, the member shows how large residual within-stratum confounding would have to be to overturn the conclusion. |
| **Proficient** | 70–89% | Fully meets the requirement, with minor gaps that do not affect the recommendation. |
| **Developing** | 50–69% | Partly meets it. For example, the paradox is found but not explained, or small cells are read as findings. |
| **Beginning** | 0–49% | Missing or incorrect. For example, the report endorses the crude ranking, or the confounder is hard-coded. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** the assessor reruns the CLI and the exploration code from a clean environment and gets the submitted outputs.
3. **Defence:** the member recomputes one interval by hand and explains the reversal without notes.
4. **Privacy:** no row-level data appears in the report or the rendered notebook.

## Automatic deductions

| Issue | Deduction |
|---|---|
| The data file was modified (checksum mismatch) | Gate fail until corrected |
| A hospital name or the confounder is hard-coded in `build_findings` | Up to −10 from dimension 2 |
| Stratified figures without interval bars | Up to −3 from dimension 8 |
| Report numbers that the exploration code does not regenerate | Up to −5 from dimension 6 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
