# DS-T1-017 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You can explain why a fixed 40 °C threshold and a city-relative 90th percentile answer different questions, and why low-coverage years must be NaN. |
| 2 | Technical correctness | 20 | Hidden suite: exact parsing of both layouts with gaps; indicators at unseen thresholds, quantiles and periods; small-multiples rules on an unseen grid with signed values. `results.csv` reproduces on rerun. |
| 3 | Implementation quality | 10 | Indicator functions are reused by `make_story.py` (no copy-pasted logic per city); no hard-coded city lists outside `cities.csv`; clear errors. |
| 4 | Methodology: indicator and design choices | 15 | `chart_specs.json` records reasoned choices (bars vs lines, grid shape, shared axes, ordering). Any unshared axis is justified in the story. The step-change question is examined rather than ignored. |
| 5 | Testing and evaluation | 10 | At least 8 member tests at the boundaries (exactly 90% coverage, leap years, exactly 10 valid years), plus at least one test of the real-file parser on a trimmed header. |
| 6 | Documentation and reproducibility | 10 | The fetch log is committed and the raw data is not. A clean run of `make_story.py` reproduces every figure and number. |
| 7 | Critical thinking and limitations | 10 | The "can't tell you" box covers reanalysis vs stations, coastal cells, step changes and attribution, and the headline is calibrated to the mixed evidence. |
| 8 | Presentation and communication (the story) | 15 | A newsroom-ready story: a headline the evidence supports, figure-led paragraphs, numbers given as days per year with periods named, readable small multiples, and a proper NASA POWER citation. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight. For example, bootstrap intervals show which changes are distinguishable from zero, or the step change is tested. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps. |
| **Developing** | 50–69% | Partly meets the requirement. For example, only one definition of "hot", free y-axes without justification, or numbers in the story that don't match `results.csv`. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. For example: −999 treated as a temperature, or causal claims. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** the assessor's rerun from the logged data reproduces `results.csv`.
3. **Defence:** the member explains the disagreeing city and predicts the effect of a threshold change.
4. **Data handling:** raw POWER files are not committed, and the data is cited.

## Automatic deductions

| Issue | Deduction |
|---|---|
| A causal attribution claim with no source | Up to −4 from dimension 7 |
| Story numbers differ from `results.csv` | Up to −5 from dimension 6 |
| Panels not ordered north to south and no reason given | Up to −2 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
