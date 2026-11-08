# ML-T1-001 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Report explains each failure mechanically (what overflows, what cancels), not just 'use the trick'. |
| 2 | Technical correctness | 20 | All public and hidden tests pass, including extreme inputs, float32 inputs and re-seeded data. |
| 3 | Implementation quality | 15 | Vectorised, no Python loops over samples, shared helpers rather than copy-paste, dtype handled deliberately. |
| 4 | Methodology and evidence | 15 | Naive versus stable behaviour is demonstrated with measured numbers; gradient checks use a justified step size and tolerance. |
| 5 | Testing and evaluation | 15 | At least 8 meaningful own tests, including at least 3 numerical edge cases that the naive code gets wrong. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run works first time; report numbers regenerate from a script. |
| 7 | Critical thinking and limitations | 10 | Honest discussion of what float64 still cannot do, and where stability costs accuracy or speed. |
| 8 | Presentation and communication | 5 | Concise report that a colleague could follow without running the code. |
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
| Hard-coded special cases to satisfy a visible test value | Up to −10 from dimension 2 |
| Python loop over samples in a loss or gradient | Up to −5 from dimension 3 |
| Report numbers that the submitted script does not regenerate | Up to −5 from dimension 6 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
