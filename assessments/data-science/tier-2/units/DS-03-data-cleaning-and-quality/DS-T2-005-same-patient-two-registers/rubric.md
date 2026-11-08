# DS-T2-005 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You explain the harms of false and missed links in this setting, why household-shared identifiers are weak evidence, and why estimated DOBs need their own treatment. |
| 2 | Technical correctness | 20 | Hidden-truth blocking completeness, linker precision and recall, and the margin over a real baseline; one-to-one matches; weights that make sense (agreement positive, disagreement negative). |
| 3 | Implementation quality | 10 | Standardisation, blocking, comparison, estimation and decision are separate and testable; there are no constants tuned to the public files; it runs within the time limit. |
| 4 | Methodology and experimentation | 20 | Blocking keys justified by measured completeness and cost; two estimation approaches compared with evidence; PR curves for both methods with bootstrap intervals; an operating point derived, not asserted. |
| 5 | Testing and evaluation design | 15 | At least 12 meaningful member tests, including hard pair types; correct use of the clerical sample (no peeking that biases estimates, and stated uncertainty). |
| 6 | Documentation and reproducibility | 10 | The analysis regenerates every figure and number; the run instructions work. |
| 7 | Critical thinking, error analysis and limitations | 10 | Error classes linked to modelling choices; honest limits (sample size, simulated error rates, linkage bias across groups). |
| 8 | Presentation and communication | 5 | A data manager could choose an operating point from your report. The safeguards section is specific. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight. For example: term-frequency weights with a measured gain, a twin-safe constraint, or a linkage-bias analysis. |
| **Proficient** | 70–89% | Meets every requirement with minor gaps. |
| **Developing** | 50–69% | A working linker, but a weak comparison: no intervals, a straw-man baseline, or an operating point without evidence. |
| **Beginning** | 0–49% | No probabilistic method, evaluation on training labels only, or links that are not one-to-one. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** `link` reproduces `outputs/links.csv` from a clean environment.
3. **Defence:** the member computes a match weight by hand from their own parameters.
4. **Privacy:** no register rows appear in the report beyond redacted examples.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Parameters or thresholds hard-coded from the public files so that `link` ignores the registers it is given | Up to −10 from dimension 2 |
| Clerical-sample truth used inside blocking or matching as a lookup | Gate fail (it is evaluation data, not an identifier) |
| A report figure the analysis does not regenerate | Up to −5 from dimension 6 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
