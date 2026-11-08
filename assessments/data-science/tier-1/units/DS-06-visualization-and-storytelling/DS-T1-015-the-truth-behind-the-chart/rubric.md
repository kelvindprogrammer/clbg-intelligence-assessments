# DS-T1-015 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | For each defect you can name the visual channel being abused (length, position, area, lightness, orientation) and explain *why* bars need a zero baseline but lines do not, and why a reversed rank axis is honest. |
| 2 | Technical correctness | 25 | Exact audits on the official and both hidden galleries; lie factors to 1e-4 with `ValueError` where undefined; CIELAB within 0.001; correct `colormap_ok` verdicts on unseen maps; every redraw passes all R7 rules. |
| 3 | Implementation quality | 15 | Rules are data-driven, with no branching on ids, titles or field names. Redraw logic is organised per mark rather than per chart. Inputs are not mutated, and the colour code is vectorised. |
| 4 | Methodology: evidence for every verdict | 10 | Each verdict in the report cites the spec property or the data computation that triggers it (e.g. "domain starts at 480,000; data effect +5.1%, graphic effect +250%"). |
| 5 | Testing and evaluation | 15 | At least 10 member tests, including at least 3 false-positive guards (honest charts that look guilty) and edge cases such as an exactly 50% window or a whitespace source. The tests would fail if a rule regressed. |
| 6 | Documentation and reproducibility | 5 | The README run instructions work first time; the committed PNGs regenerate from `python -m chart_forensics redraw`. |
| 7 | Critical thinking and limitations | 10 | A concrete blind spot of the desk policy, with an example chart it would pass; a reasoned view on when emphasis (zoomed lines, log scales) is legitimate and how to disclose it. |
| 8 | Presentation and communication | 10 | Honest replacement headlines that the data supports; redraws readable at social-media size; neutral, evidence-based language about publishers. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight. For example, the report quantifies how a reader's estimate would be off, or a redraw choice is justified against an alternative (stacked panels vs an indexed scale). |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps that don't affect trustworthiness. |
| **Developing** | 50–69% | Partly meets the requirement. Some verdicts are unexplained, there are false positives on honest charts, or a redraw keeps a distortion. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. For example: every non-zero axis flagged, chart-id lookups, or redraws that keep the misleading headline. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns the tests and the redraw command from a clean environment and gets the submitted outputs.
3. **Defence:** the member correctly predicts the auditor's verdict on an unseen chart and explains an honest-chart case.
4. **Generality:** no logic keyed on chart ids, titles or field names.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Gallery files modified (checksum mismatch) | Gate fail until corrected |
| Branching on `spec["id"]` or a title | Gate fail (generality) |
| A redraw keeps a headline the data contradicts | Up to −4 from dimension 8 |
| Report verdicts that differ from what the code outputs | Up to −5 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
