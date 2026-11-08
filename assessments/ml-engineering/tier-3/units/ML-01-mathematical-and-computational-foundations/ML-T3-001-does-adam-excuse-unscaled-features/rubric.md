# ML-T3-001 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The plan turns the vague claim into precise hypotheses, metrics and a cost model, and says in advance what would falsify each. |
| 2 | Technical correctness | 20 | Optimisers are correct, the reproduction of known rates is within the stated windows, and the study harness passes public and hidden tests on re-seeded problems. |
| 3 | Implementation quality | 15 | Optimisers and harness separate concerns, deterministic seeding, no hidden global state, cost accounting is explicit. |
| 4 | Methodology and evidence | 15 | Controlled design: one factor varied at a time, repeated seeds, censoring handled, exponents with intervals, ablations (scale vs correlation, preconditioner, step rule). |
| 5 | Testing and evaluation | 15 | At least 12 own tests including a known-answer test for each optimiser and for the exponent estimator. |
| 6 | Documentation and reproducibility | 10 | Every figure and number regenerates from `experiments.py` with fixed seeds in under 10 minutes. |
| 7 | Critical thinking and limitations | 10 | Explicit validity argument: what a synthetic logistic study can and cannot say about Adam on deep networks; negative and inconvenient results reported. |
| 8 | Presentation and communication | 5 | Report reads as a short technical note: claim, method, evidence, verdict, limits. |
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
2. **Reproducibility:** the assessor reruns the tests and experiments from a clean environment and gets your reported numbers.
3. **Defence:** you explain your code and handle an unseen modification with sound reasoning.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Censored runs (not converged) averaged as if they had converged | Up to −8 from dimension 4 |
| Verdict stated with no interval or repeated seeds | Up to −6 from dimension 4 |
| Plan written after seeing results without disclosure (plan history in commits) | Up to −6 from dimension 1 |
| Headline claim generalised to deep networks without argument | Up to −5 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
