# ML-T3-009 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The memo explains the mechanism of the winner's curse and why it matters for this leaderboard, not just that it exists. |
| 2 | Technical correctness | 20 | Hidden shrinkage test, noise-label nested test, inflation and sample-size tests pass; functions behave on edge cases. |
| 3 | Implementation quality | 15 | Clean, tested statistical code; no leakage between outer and inner loops; reproducible seeds. |
| 4 | Methodology and evidence | 15 | At least three well-designed ablations with hypotheses; the experiments isolate the effect they claim to. |
| 5 | Testing and evaluation | 15 | Tests of statistical properties (monotonicity, coverage, calibration of intervals) that would catch real regressions. |
| 6 | Documentation and reproducibility | 10 | `run_all.py` regenerates every number within the time limit; versions and seeds recorded. |
| 7 | Critical thinking and limitations | 10 | Assumptions stated and stress-tested; at least one honestly reported surprising or negative result; limits of synthetic data. |
| 8 | Presentation and communication | 5 | A memo the organisers can act on; the protocol and trade-offs are clear and argued. |
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
