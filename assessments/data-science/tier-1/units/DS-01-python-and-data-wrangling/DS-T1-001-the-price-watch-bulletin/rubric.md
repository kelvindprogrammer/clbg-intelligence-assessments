# DS-T1-001 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You can explain why the file cannot be read with default `read_csv`, what makes data "tidy", why missing cells must stay as rows with a status, and why "previous row" is not "previous month". |
| 2 | Technical correctness | 25 | Public and hidden tests pass on bulletins you have never seen: an exact tidy table, exact published averages, exactly the inconsistent averages flagged, calendar-correct `mom_pct`, and parsers that reject malformed input. |
| 3 | Implementation quality | 15 | Small, pure parsing functions; no hard-coded row numbers, table counts or item names; row-count or `validate=` checks around every reshape and join; no mutation of inputs; readable names. |
| 4 | Methodology: read, parse, reshape, verify | 10 | Evidence that you inspected the raw file first, listed its quirks, and verified each stage (shapes, counts, spot checks) before building the next one. The reconciliation is used to test a hypothesis, not just to produce a file. |
| 5 | Testing and evaluation | 15 | At least 10 meaningful member tests; at least 3 traced to real quirks in the file; tests for the `ValueError` paths; tests that would fail if a reshape dropped or shifted a row. |
| 6 | Documentation and reproducibility | 10 | A short README that runs first time from a clean environment; outputs regenerate byte-for-byte; every number in `ANALYSIS.md` is produced by code you name. |
| 7 | Critical thinking and limitations | 10 | A correct account of the mean-of-means effect and its direction; a reasoned, appropriately hedged explanation of the inconsistent averages; caveats about provisional months. |
| 8 | Presentation and communication | 5 | `ANALYSIS.md` is concise, uses small clear tables, and could be read by a journalist or programme officer. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Correct on every hidden bulletin, with tests that read like a specification of the format. The analysis quantifies the mean-of-means bias per item and links every inconsistent average to the revised figure behind it. |
| **Proficient** | 70–89% | Correct on the hidden bulletins, with minor gaps in tests or explanation that do not affect trust in the outputs. |
| **Developing** | 50–69% | Works on the official file but fails on a regenerated layout (for example, continuations or month spellings), or the analysis states the averaging rule without evidence. |
| **Beginning** | 0–49% | Missing rows, shifted months, a hard-coded layout, or parsers that silently return defaults. |

## Gates (pass/fail, independent of points)

A submission can only receive a passing outcome if all gates are met:

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns the CLI from a clean environment and gets the submitted outputs.
3. **Defence:** the member traces an assessor-chosen cell from the raw file to the tidy table, and handles the unseen format change with sound reasoning.

## Automatic deductions

| Issue | Deduction |
|---|---|
| The raw bulletin was modified (checksum mismatch) | Gate fail until corrected |
| Row numbers, table counts or item names hard-coded | Up to −10 from dimension 2 |
| Missing cells dropped from the tidy table | Up to −8 from dimension 2 |
| `ANALYSIS.md` quotes numbers that no code regenerates | Up to −5 from dimension 6 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
