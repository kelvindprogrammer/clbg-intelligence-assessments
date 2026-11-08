# DS-T1-007 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You explain why a unit is not a weight (crop-specific factors, paddy vs grain), why yield rather than quantity is the quantity to test, and why the log scale suits skewed yields. |
| 2 | Technical correctness | 20 | Public and hidden tests pass: conversions match the table, unconvertible records stay unconverted, impossible yields and the systemic defect are flagged, genuine large farms and zero harvests survive, and the imputed total is close to the truth. |
| 3 | Implementation quality | 10 | The unit mapping is data-driven and readable (not a chain of `if` statements); parsers, rules and pipeline are separate; output is deterministic; the raw file is untouched. |
| 4 | Investigation methodology and evidence | 20 | A reproducible unit census; MAD vs IQR vs domain counts and overlap; flags cross-tabulated by unit, enumerator, LGA and crop; the source of the implausible values identified with evidence rather than asserted. |
| 5 | Testing and evaluation | 15 | At least 10 meaningful member tests, at least 3 derived from profiling, and tests that would catch a rule applied on the wrong scale or a borrowed factor. |
| 6 | Documentation and reproducibility | 10 | A clean-environment run works first time; the analysis regenerates every number in the report; requirements are bounded. |
| 7 | Critical thinking and limitations | 10 | A recommended total with a range and an honest account of what the range omits (no sampling weights, a fixed-factor model, unmodelled measure variation). Imputation is justified rather than assumed. |
| 8 | Presentation and communication | 5 | A non-specialist ADP manager could act on the report. Enumerator-level findings are framed as a training need, not blame. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight. For example: it decomposes the uncertainty range by factor, or shows the total is robust to the choice of k. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps that don't affect trustworthiness. |
| **Developing** | 50–69% | Partly meets the requirement. Some rules are unjustified or untested, or the investigation describes flags without explaining them. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. For example: flagged records silently dropped, factors borrowed between crops, or outliers detected on raw quantities. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** the assessor reruns the pipeline and analysis from a clean environment and gets the submitted outputs.
3. **Defence:** the member traces two assessor-chosen records and computes a modified z-score by hand.
4. **Responsible reporting:** no enumerator is named in a way that would be inappropriate in a real ADP report (codes are fine; blame is not).

## Automatic deductions

| Issue | Deduction |
|---|---|
| The raw survey or a reference table was modified (checksum mismatch or edited factors) | Gate fail until corrected |
| A conversion factor invented or borrowed from another crop | Up to −10 from dimension 2 |
| Records dropped from `harmonised.csv` | Up to −10 from dimension 2 |
| Report numbers that the analysis does not regenerate | Up to −5 from dimension 6 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
