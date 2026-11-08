# ML-T3-023 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The design ties every stage and guardrail to a named failure mode, the label lag and the cost of both kinds of error; the trade-off between harm and delay is explicit. |
| 2 | Technical correctness | 20 | Statistics are exact; the controller clears the safety and speed bars on the public bench and the hidden worlds; non-inferiority is used correctly. |
| 3 | Implementation quality | 15 | Controller is small, readable and stateless where possible; decisions are explained; no access to anything outside `obs` and `info`. |
| 4 | Methodology and evidence | 15 | Design document written first; ablations isolate components with intervals over 5 or more seeds; peeking is treated explicitly; robustness is tested in worlds not tuned on. |
| 5 | Testing and evaluation | 15 | At least 10 own tests, including terminal rollback and no-evidence-no-advance; edge cases around empty samples and zero variance. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces every number and figure; design changes after results are logged; runbook is usable. |
| 7 | Critical thinking and limitations | 10 | Specific limits: the simulator's independence assumptions, a single failure kind per candidate, proxy validity, and what a real rollout would still need. |
| 8 | Presentation and communication | 5 | The risk committee could sign off from the first page; the operating-curve figure supports the choice. |
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
| Design document written or edited after seeing bench results without being logged | Up to −8 from dimension 4 |
| Reading simulator internals (candidate descriptions) from inside the controller | Up to −15 from dimension 2 |
| Advancing a stage on no outcome evidence at stages 2 to 4 | Up to −6 from dimension 2 |
| Thresholds tuned only on the public bench seed and reported as general | Up to −6 from dimension 4 |
| Pooled-only checks with no rule protecting the new-to-credit segment | Up to −5 from dimension 1 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
