# DS-T1-006 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report shows you understood *why* each defect matters for the Records Office: namesakes, ambiguous dates, the scale defect. Rules are justified by consequences, not convenience. |
| 2 | Technical correctness | 20 | Public and hidden tests pass. Duplicate precision is ≥ 0.98 and recall ≥ 0.90. Unrecoverable values are flagged, not invented. The systemic defect is detected from data. |
| 3 | Implementation quality | 15 | Clear module boundaries, readable functions, no copy-paste rule blocks, deterministic output, no in-place mutation of the raw data. |
| 4 | Methodology: profiling → rules → evidence | 15 | A reproducible profiling notebook or script; every rule traceable to profiling evidence; a defect inventory with counts. |
| 5 | Testing and evaluation | 15 | At least 12 meaningful member tests, at least 4 profiling-derived edge cases, and tests that would fail if a rule regressed. |
| 6 | Documentation and reproducibility | 10 | A clean-environment run from your README works first time; requirements are pinned or bounded; outputs regenerate exactly. |
| 7 | Critical thinking and limitations | 10 | An honest estimate of residual error, an explanation of what cannot be known (ambiguous DOBs), and the risks of your dedup rule. |
| 8 | Presentation and communication | 5 | The report is concise and readable by a non-technical records officer, with redacted examples and no personal data leakage. |
| | **Total** | **100** | |

## Performance levels

Use these descriptors to place work within each dimension. The proportions are guidance: an assessor may award any integer within the dimension.

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight. For example, the member quantifies the false-merge risk, or reasons about ambiguity probabilistically. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps that don't affect trustworthiness. |
| **Developing** | 50–69% | Partly meets the requirement. Some rules are unjustified or untested, or some defects are missed. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. For example: `dropna()`, clipping, or a hard-coded department. |

## Gates (pass/fail, independent of points)

A submission can only receive a passing outcome if all gates are met:

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns the pipeline from a clean environment and gets the submitted outputs.
3. **Defence:** the member traces two assessor-chosen records and handles the unseen modification with sound reasoning.
4. **Privacy:** no full personal records appear in the report or notebook outputs.

## Automatic deductions

| Issue | Deduction |
|---|---|
| The raw export file was modified (checksum mismatch) | Gate fail until corrected |
| Department name hard-coded for the CGPA rescale | Up to −10 from dimension 2 |
| Rows silently dropped (traceability failure) | Up to −10 from dimension 2 |
| Report quotes counts the profiling code does not regenerate | Up to −5 from dimension 6 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
