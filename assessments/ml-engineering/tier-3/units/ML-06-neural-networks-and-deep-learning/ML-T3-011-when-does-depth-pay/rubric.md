# ML-T3-011 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The research question, hypotheses and design table are precise, and each factor is motivated by the farming context and the literature. |
| 2 | Technical correctness | 20 | Hidden tests pass: structural behaviours of the study, correct pairing and crossover logic, determinism, a competent MLP. |
| 3 | Implementation quality | 15 | Fair-budget tuning code, deterministic seeds, clean separation of study utilities from analysis, no test-set leakage. |
| 4 | Methodology and evidence | 15 | Controls and ablations isolate mechanisms; paired intervals support every comparison; contradicted hypotheses are reported. |
| 5 | Testing and evaluation | 15 | At least 8 own tests covering pairing, determinism and crossover edge cases; they fail when the logic regresses. |
| 6 | Documentation and reproducibility | 10 | `run_all.py` regenerates all results within the time limit; versions, seeds and budgets recorded. |
| 7 | Critical thinking and limitations | 10 | Claims are scoped (supported, plausible, unsupported); limits of synthetic tasks and of the metric are stated; harm analysis of the subsidy decision. |
| 8 | Presentation and communication | 5 | The report and the recommendation to the director are clear and usable by a non-specialist. |
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
