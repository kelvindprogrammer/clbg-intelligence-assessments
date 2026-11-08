# DS-T1-005 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You can explain why each agency's format needs its own rule (kobo, mudu, per-sheet bag size, appended revisions, implied decimals, zero-as-missing) and why the cross-source median is robust. |
| 2 | Technical correctness | 20 | Public and hidden tests pass. Regenerated files parse exactly to the ground truth. There are no zero prices for missing values. Revisions, trailers and unknown labels are handled. |
| 3 | Implementation quality | 15 | One clear parser per agency sharing the reference lookups. No hard-coded markets, months or sheets. Explicit errors instead of silent skips. Readable code. |
| 4 | Methodology: investigation and evidence | 20 | Each anomaly is classified as a parsing error, a source defect or a real event, with quantitative evidence: the ratio to the other agencies, whether every agency shows it, and the time pattern. The real event is left uncorrected. The profiling script reproduces every number. |
| 5 | Testing and evaluation | 10 | At least 12 meaningful member tests, at least one per parser from your own discovery, and tests that would fail if a rule regressed. |
| 6 | Documentation and reproducibility | 10 | A clean-environment run works first time. The CLI regenerates `outputs/` exactly. The report says which script produced each count. |
| 7 | Critical thinking and limitations | 10 | You state what the files can't tell you (for example, *why* an agency's values are wrong), what you would ask each agency, and how the 15 % tolerance could miss smaller defects. |
| 8 | Presentation and communication | 5 | A brief the desk editor could act on: one table of anomalies, plain language, and no figures presented as real prices. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | All anomalies are correctly classified with compelling evidence. The member also quantifies agency bias or tolerance sensitivity, or finds a format detail not mentioned in the documentation. |
| **Proficient** | 70–89% | Correct parsing and reconciliation. The anomalies are classified sensibly, with minor gaps in evidence. |
| **Developing** | 50–69% | The files parse, but a unit or revision rule is wrong, or anomalies are "fixed" without classification. |
| **Beginning** | 0–49% | Missing or incorrect. For example: hard-coded 100 kg bags, missing values as zero, or the real price shock "corrected". |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** the assessor reruns the CLI and the profiling script and gets the submitted outputs and counts.
3. **Defence:** you trace an assessor-chosen value from the raw file and implement the unseen modification.

## Automatic deductions

| Issue | Deduction |
|---|---|
| A resource file was modified (checksum mismatch) | Gate fail until corrected |
| A market, month or sheet hard-coded to make a defect disappear | Up to −10 from dimension 2 |
| A real market event "corrected" or removed | Up to −8 from dimension 4 |
| Missing values written as `0` | Up to −5 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
