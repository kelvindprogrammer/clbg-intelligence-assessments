# DS-T1-002 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 15 | Each defect's root cause is explained in terms of the pandas behaviour behind it (fan-out, inner-join loss, dedup key, copy semantics, UTC vs WAT, interval closure), not just "it was wrong". |
| 2 | Technical correctness | 20 | Hidden tests pass on regenerated ledgers: exact agent-day settlement, every day reconciled, and every docstring sentence honoured, including no mutation and one row per input. |
| 3 | Implementation quality | 10 | Small, targeted fixes in the legacy functions; no rewrite; no warnings; no hard-coded IDs or dates; cardinality checks where a join could fan out. |
| 4 | Methodology: isolate, prove, fix, measure | 20 | A minimal failing example for each defect, committed before its fix; impact measured by re-introducing one defect at a time; reconciliation used as evidence after each fix. |
| 5 | Testing and evaluation | 15 | One regression test per defect, each failing on the legacy code; at least four further meaningful tests; boundary cases (₦5,000, 23:00 UTC, `valid_to` dates) covered. |
| 6 | Documentation and reproducibility | 5 | `impact.py` and the CLI reproduce the submitted outputs exactly from a clean environment. |
| 7 | Critical thinking and limitations | 10 | Explains why isolated impacts do not sum; identifies which defects the control totals cannot detect; proposes safeguards tied to specific defects. |
| 8 | Presentation and communication | 5 | `FORENSICS.md` is clear to a finance reader, quantifies consequences, and contains no agent-level payout table. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Every defect found, including those the control totals cannot see; each with a minimal red-then-green test; an impact table with a clear account of masking between defects. |
| **Proficient** | 70–89% | Every defect fixed and the settlement exact, with minor gaps in tests, history or explanation. |
| **Developing** | 50–69% | The control totals reconcile, but at least one defect invisible to them (fees, commission or mutation) remains, or fixes are untested. |
| **Beginning** | 0–49% | Totals still differ from the switch, fixes are guesses, or the code was rewritten without explanation. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence. Asking an AI tool to find the defects is a breach (README §K).
2. **Reproducibility:** the assessor reruns the CLI and `impact.py` from a clean environment and gets the submitted outputs.
3. **Defence:** the member reproduces a defect live and diagnoses the injected defect with sound reasoning.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Data files modified (checksum mismatch) | Gate fail until corrected |
| Agent IDs, dates or totals hard-coded | Up to −10 from dimension 2 |
| Settlement rewritten from scratch with no explained diff | Up to −8 from dimension 3 |
| `impact.csv` not reproducible by `impact.py` | Up to −5 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
