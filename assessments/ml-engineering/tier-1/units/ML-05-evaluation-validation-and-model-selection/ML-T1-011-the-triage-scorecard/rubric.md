# ML-T1-011 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You understand why accuracy, AUC, threshold and calibration answer different questions, and the report ties each to a programme decision. |
| 2 | Technical correctness | 20 | Public and hidden tests pass; AUC and AP match the oracle to 1e-12 including ties; folds never split a household; the threshold is the largest valid one. |
| 3 | Implementation quality | 15 | Small clear functions, vectorised where natural, no input mutation, no sklearn inside the package, deterministic output. |
| 4 | Methodology and evidence | 15 | Numbers in the report come from the submitted code; the leakage claim is backed by a count from your own splitter versus a naive split. |
| 5 | Testing and evaluation | 15 | At least 6 own tests, at least 2 real edge cases (all ties, single-positive fold), tests that would fail if the tie handling regressed. |
| 6 | Documentation and reproducibility | 10 | A clean-environment run reproduces `outputs/metrics.json` exactly; requirements are bounded. |
| 7 | Critical thinking and limitations | 10 | Honest reading of ECE and AP at 11% prevalence; limits of a 733-row sample; what changes with real clinic data. |
| 8 | Presentation and communication | 5 | Report is readable by a non-technical programme manager and under 900 words plus tables. |
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
