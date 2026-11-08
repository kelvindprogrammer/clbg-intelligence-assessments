# DS-T1-012 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You explain why demand is not the number served, why the tail of the wait (not the mean) drives the decision, and why ρ ≥ 1 has no steady state. |
| 2 | Technical correctness | 25 | Erlang C is exact and stable for large `c`; the FCFS simulator matches independent recursions; validation intervals cover theory; the decision is right on the official and re-generated logs. The derivations in the report are correct. |
| 3 | Implementation quality | 10 | Pure, seedable functions; the simulator separated from the randomness; no global random state; input validation as specified; readable code without copy-pasted blocks per `c`. |
| 4 | Methodology: validation and input modelling | 15 | Validation at three or more settings including ρ > 0.9, with warm-up and run length justified; a quantified check of exponential service; balking handled; a resampling study of input uncertainty (R10). |
| 5 | Testing and evaluation | 15 | At least 10 member tests, three of them against independent calculations; tests that would catch an off-by-one in server assignment or a wrong tail formula. |
| 6 | Documentation and reproducibility | 10 | One command regenerates every number and figure from stated seeds; the README run instructions work from a clean environment. |
| 7 | Critical thinking and limitations | 10 | Names what the model ignores (balking, non-stationary arrivals, attendants' breaks, pump-specific fuel types) and says which way each would push the decision. |
| 8 | Presentation and communication | 5 | A plain-language paragraph a station manager could act on, with uncertainty stated honestly and without jargon. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Correct and validated tools, with insight: for example, showing how the required run length grows as ρ → 1, or using common random numbers to compare pump counts. |
| **Proficient** | 70–89% | All requirements met. Minor gaps in validation coverage or explanation that do not affect the decision's trustworthiness. |
| **Developing** | 50–69% | A working simulator, but validation uses i.i.d. intervals, demand counts served customers only, or the M/M/c answer is accepted without checking service variability. |
| **Beginning** | 0–49% | Simulator incorrect or unverified, unstable `c` reported with a finite wait, or a decision without any statement of uncertainty. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns the CLI and the analysis from a clean environment and gets the submitted outputs.
3. **Defence:** the member derives P(wait) for M/M/2 and handles the unseen modification with sound reasoning.

## Automatic deductions

| Issue | Deduction |
|---|---|
| The station log was modified (checksum mismatch) | Gate fail until corrected |
| A queueing or simulation library used inside the core package | Up to −10 from dimension 2 |
| Unstable pump counts simulated and reported with a finite mean wait | Up to −5 from dimension 2 |
| Report numbers that the analysis code does not regenerate | Up to −5 from dimension 6 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
