# ML-T3-021 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report relates every choice to the device limits, the shift in real traffic and the cost of misrouting; hypotheses come from reasoning, not from the results. |
| 2 | Technical correctness | 20 | Instruments are exact; candidates are honest; the chosen model meets the limits and the shifted-accuracy bar on re-seeded tasks. |
| 3 | Implementation quality | 15 | Instruments modular and tested; no reliance on self-reported numbers; deterministic and efficient enough for five-seed ablations. |
| 4 | Methodology and evidence | 15 | Protocol written first; controls and ablations isolate each factor; uncertainty carried through; no ranking within the noise; null results reported. |
| 5 | Testing and evaluation | 15 | At least 10 own tests including brute-force and audit tests; negative tests for dishonest specs. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces every number; figures labelled; protocol deviations logged. |
| 7 | Critical thinking and limitations | 10 | Validity argument is specific (synthetic text, shift type coverage, selection with 150 labels) and states what would change the recommendation. |
| 8 | Presentation and communication | 5 | A product lead could decide from the first page; the figures show shifted accuracy beside clean accuracy. |
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
| Test sets used to choose a candidate, hyperparameter or threshold | Up to −12 from dimension 2 |
| Clean accuracy used as the headline of any comparison | Up to −6 from dimension 4 |
| `PROTOCOL.md` written or edited after seeing the results | Up to −8 from dimension 4 |
| Candidate specs that understate size (for example bits or nnz not matching the weights) | Up to −8 from dimension 2 |
| Ranking candidates whose difference is under one standard error | Up to −4 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
