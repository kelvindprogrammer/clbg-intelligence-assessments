# ML-T1-013 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You can derive and explain the gradients and initialisation choices, not only code them. |
| 2 | Technical correctness | 20 | Public and hidden tests pass; gradient check below 1e-6; momentum steps exact; held-out accuracy at least 0.90. |
| 3 | Implementation quality | 15 | Vectorised, readable code with clear caching; no frameworks; deterministic. |
| 4 | Methodology and evidence | 15 | Experiments (gradient table, zero-init, learning-rate curves) are designed to answer a question and are reproducible. |
| 5 | Testing and evaluation | 15 | At least 6 tests including one that detects a missing ReLU mask; edge cases such as a short final batch. |
| 6 | Documentation and reproducibility | 10 | `experiments.py` regenerates every number and figure; requirements bounded. |
| 7 | Critical thinking and limitations | 10 | Honest treatment of label noise, small data, hyperparameter selection on train only, and what accuracy means here. |
| 8 | Presentation and communication | 5 | A short report with clear figures and captions. |
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
