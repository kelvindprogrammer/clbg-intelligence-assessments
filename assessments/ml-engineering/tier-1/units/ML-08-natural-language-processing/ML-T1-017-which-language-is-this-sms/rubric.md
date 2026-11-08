# ML-T1-017 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links each design choice (log space, smoothing, n-grams, abstention) to the short noisy code-switched messages. |
| 2 | Technical correctness | 25 | Hand-computed examples, the scikit-learn comparison and the accuracy bars pass on re-seeded data. |
| 3 | Implementation quality | 15 | Clean, deterministic, readable code with no banned libraries. |
| 4 | Methodology and evidence | 15 | Word-versus-character comparison at several noise levels, same classifier and data, more than one seed. |
| 5 | Testing and evaluation | 15 | At least 6 own tests including the reference comparison and underflow. |
| 6 | Documentation and reproducibility | 10 | `analysis.py` reproduces every number in the report. |
| 7 | Critical thinking and limitations | 5 | Honest account of template data, language coverage and who is disadvantaged. |
| 8 | Presentation and communication | 5 | Clear explanations a colleague could follow. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight, for example by quantifying uncertainty or testing a claim the brief did not ask about. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps that do not affect trust in the result. |
| **Developing** | 50–69% | Partly meets the requirement; some choices are unjustified or untested. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. |

## Gates (pass/fail, independent of points)

1. **Integrity:** the AI-use declaration is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns the tests from a clean environment and gets your reported numbers.
3. **Defence:** you explain your code and handle an unseen modification with sound reasoning.

## Automatic deductions

| Issue | Deduction |
|---|---|
| NLP or ML library used inside the package | Up to -10 from dimension 3 |
| Probabilities multiplied without logs | Up to -6 from dimension 2 |
| Accuracy claimed for real Pidgin or Yoruba from synthetic results | Up to -4 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
