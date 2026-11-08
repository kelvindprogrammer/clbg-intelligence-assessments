# ML-T2-012 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You connect each design choice to the data (heavy tails, scale, imbalance, interaction) and to the inspection decision. |
| 2 | Technical correctness | 20 | Hidden fresh-population test passes (PR-AUC edge over baseline); preprocessing, early stopping and diagnosis tests pass. |
| 3 | Implementation quality | 15 | Leak-free pipeline; clear separation of preprocessing, training and diagnosis; deterministic; no frameworks. |
| 4 | Methodology and evidence | 15 | Ablations over seeds, with spread; the three deliberately broken runs are diagnosed convincingly. |
| 5 | Testing and evaluation | 15 | At least 6 own tests including boundary cases for diagnose and a leakage check; tests fail when behaviour regresses. |
| 6 | Documentation and reproducibility | 10 | `analysis.py` reproduces all tables; versions and seeds recorded; runtime within limits. |
| 7 | Critical thinking and limitations | 10 | Honest verdict on the network versus a linear model; limits of synthetic data and of the metric; harm of false flags. |
| 8 | Presentation and communication | 5 | Curves and tables are readable; the report is concise and decision-oriented. |
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
