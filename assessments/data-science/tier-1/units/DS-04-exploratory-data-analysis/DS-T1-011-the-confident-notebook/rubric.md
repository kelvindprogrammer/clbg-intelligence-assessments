# DS-T1-011 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 15 | Each flaw is explained by its mechanism in this data (who was filtered out, what differs between groups, what the axis encodes), not just named. |
| 2 | Technical correctness | 20 | Corrected values match the oracle on re-generated data; verdicts and flaw labels meet the thresholds; `audit.json` validates. |
| 3 | Implementation quality | 10 | One small, readable function per claim; no mutation; shared helpers instead of copy-paste. |
| 4 | Forensic methodology | 15 | Every claim reproduced first, then challenged; at least two mechanism figures; a corrected C3 chart. |
| 5 | Testing and evaluation | 10 | At least 8 hand-worked member tests, including one where the notebook's method and the corrected method disagree. |
| 6 | Documentation and reproducibility | 10 | `run_audit.py` regenerates every number and figure; run instructions work first time. |
| 7 | Critical thinking and limitations | 15 | The two correct claims are defended; corrected values that are themselves uncertain are flagged; "we don't know yet" is used where appropriate. |
| 8 | Presentation and communication | 5 | A COO can act on it: verdict, flaw, number and replacement recommendation per claim, in a constructive tone. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Goes beyond the requirement, e.g. intervals for the corrections, or a missed true pattern found and supported. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps. |
| **Developing** | 50–69% | Flaws named but mechanisms not shown, or correct claims rejected. |
| **Beginning** | 0–49% | Uniform verdicts, labels without reasoning, or corrected values not computed. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** the assessor reruns `run_audit.py` from a clean environment and gets `outputs/audit.json`.
3. **Defence:** the member explains two mechanisms without notes and judges one unseen claim soundly.
4. **Privacy:** no agent is named as a fraudster or poor performer in the report.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Data or flawed notebook modified (checksum mismatch) | Gate fail until corrected |
| Corrected values typed into `audit.json` by hand rather than generated | Up to −5 from dimension 6 |
| Hard-coded values inside the corrected functions | Up to −10 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
