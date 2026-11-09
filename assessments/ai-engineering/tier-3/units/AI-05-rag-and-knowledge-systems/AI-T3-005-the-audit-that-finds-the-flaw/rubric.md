# AI-T3-005 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Frames the evaluation question precisely and ties each metric to a failure it can and cannot detect. |
| 2 | Technical correctness | 20 | Hidden tests pass: exact metrics, unseen seeds and pairs, weak-flaw power, zero false alarms. |
| 3 | Implementation quality | 15 | Population definitions and tolerances are explicit, separable and testable. |
| 4 | Methodology and evidence | 15 | Validity study (a) to (e) is complete, uses many seeds, and reports uncertainty not single runs. |
| 5 | Testing and evaluation | 15 | At least 12 own tests including exact tiny cases, interacting flaws and a false-alarm test. |
| 6 | Documentation and reproducibility | 10 | One command reproduces every table and figure; seeds and settings stated. |
| 7 | Critical thinking and limitations | 10 | Names at least three ways the zoo differs from real systems and what each would invalidate; honest about power limits. |
| 8 | Presentation and communication | 5 | A charity trustee could understand what the audit does and does not license. |
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
| Flaw inferred from zoo internals, attributes or the `make_system` source | Up to -15 from dimension 2 |
| Tolerances tuned on hidden-style seeds (200 and above) | Up to -6 from dimension 4 |
| Accuracy used as the only evidence of system quality | Up to -5 from dimension 1 |
| Validity study reports single-seed results as detection rates | Up to -5 from dimension 4 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
