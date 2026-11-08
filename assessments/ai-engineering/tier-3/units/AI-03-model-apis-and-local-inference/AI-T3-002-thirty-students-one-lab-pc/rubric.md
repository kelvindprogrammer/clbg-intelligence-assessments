# AI-T3-002 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 12 | Frames the lab's real constraints (SLO, quality tolerance, residency) and links each to a modelling choice. |
| 2 | Technical correctness | 20 | Public and hidden differential tests pass for the quantiser, simulator, capacity and recommendation. |
| 3 | Implementation quality | 10 | Vectorised, readable, efficient enough; no duplicated policy logic. |
| 4 | Methodology and evidence | 20 | Multi-seed quality tables, two workload shapes, three sensitivity analyses, ablations that isolate each factor. |
| 5 | Testing and evaluation | 10 | At least 12 own tests including a hand trace and the invariance property. |
| 6 | Documentation and reproducibility | 8 | Clean-environment run reproduces every number. |
| 7 | Critical thinking and limitations | 15 | Honest, specific threats to validity; fragility of the recommendation identified; residency argument sound. |
| 8 | Presentation and communication | 5 | A department head could act on the report. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight, for example by testing a claim the brief did not ask about. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps that do not affect trust in the result. |
| **Developing** | 50–69% | Partly meets the requirement; some choices are unjustified or untested. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. |

## Gates (pass/fail, independent of points)

1. **Integrity:** the AI-use declaration is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns the tests and experiments from a clean environment and gets your reported numbers.
3. **Defence:** you explain your code and handle an unseen modification with sound reasoning.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Using test or hidden-world data to tune the recommendation | Up to -10 from dimension 2 |
| Presenting toy-model perplexity or simulated latency as evidence about real models without qualification | Up to -6 from dimension 7 |
| A single seed or single workload behind a headline claim | Up to -6 from dimension 4 |
| Real timing (`time.time`) used to measure simulated latency | Up to -4 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
