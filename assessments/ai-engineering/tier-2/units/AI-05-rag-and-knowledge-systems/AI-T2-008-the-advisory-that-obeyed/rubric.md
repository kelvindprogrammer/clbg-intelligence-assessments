# AI-T2-008 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Memo ties each stage to a measured failure and to the farmer-harm it prevents. |
| 2 | Technical correctness | 20 | Hidden tests pass: unseen phrasings, unseen places, confabulator, newest-bulletin wins. |
| 3 | Implementation quality | 15 | Stages are separate, pure and individually testable; config switches work. |
| 4 | Methodology and evidence | 15 | Ablation on at least 3 seeds and 3 mock modes, with retrieval-mode comparison, not one run. |
| 5 | Testing and evaluation | 15 | At least 12 own tests including an invented hijack phrasing and a benign decoy. |
| 6 | Documentation and reproducibility | 10 | One command reproduces the tables; seeds and thresholds stated. |
| 7 | Critical thinking and limitations | 10 | States what sanitising, sufficiency and verification do not catch, with an example, and the data-handling consequences. |
| 8 | Presentation and communication | 5 | An operations lead could adopt the recommended configuration. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90-100% | Exceeds the requirement with insight, for example by testing a claim the brief did not ask about. |
| **Proficient** | 70-89% | Fully meets the requirement with minor gaps that do not affect trust in the result. |
| **Developing** | 50-69% | Partly meets the requirement; some choices are unjustified or untested. |
| **Beginning** | 0-49% | Missing, incorrect or unexplained. |

## Gates (pass/fail, independent of points)

1. **Integrity:** the AI-use declaration is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns the tests and experiments from a clean environment and gets your reported numbers.
3. **Defence:** you explain your code and handle an unseen modification with sound reasoning.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Citation or number check recomputed from the mock's internals | Up to -15 from dimension 2 |
| Hijack handling hard-coded to the public phrase or to `ACCT-` only | Up to -8 from dimension 2 |
| Answer accepted without verification when `verify` is on | Up to -5 from dimension 2 |
| Tuning on a hidden-style seed instead of the development corpus | Up to -5 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
