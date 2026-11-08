# ML-T2-009 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The memo shows why time, maturity and leakage each change the answer, tied to the lender's costs. |
| 2 | Technical correctness | 20 | Hidden tests pass: realised cost beats the trivial policy, threshold near oracle, honest cv estimate; splits obey maturity rules. |
| 3 | Implementation quality | 15 | Pipelines fitted inside folds, clear module structure, no leakage in preprocessing, deterministic. |
| 4 | Methodology and evidence | 15 | Each correction is isolated and quantified (leak, maturity, forward-vs-random); candidate comparison includes intervals. |
| 5 | Testing and evaluation | 15 | At least 8 own tests including edge cases; tests would catch a regression in the embargo or the missing-label handling. |
| 6 | Documentation and reproducibility | 10 | `analysis.py` regenerates every table; requirements bounded; runtime within limits. |
| 7 | Critical thinking and limitations | 10 | Honest limits: synthetic drift, repeat customers, proxy risk of region, what monitoring would catch. |
| 8 | Presentation and communication | 5 | A decision memo a credit committee can act on, within the word limit. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight; quantifies uncertainty and anticipates objections. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps that do not affect trustworthiness. |
| **Developing** | 50–69% | Partly meets the requirement; some choices unjustified or untested. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. |

## Gates (pass/fail, independent of points)

1. **Integrity:** the AI-use declaration is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns your code from a clean environment and gets your reported numbers.
3. **Defence:** you explain your choices and handle an unseen modification with sound reasoning.
4. **Honesty of evidence:** no test-set information is used for any choice; no result is reported that was not produced by the submitted code.

## Automatic deductions

- Importing a library the assessment forbids, or hard-coding values from the visible data: dimension 2 is capped at Developing.
- Numbers in the report that the code does not regenerate: up to −10 on dimension 6.
