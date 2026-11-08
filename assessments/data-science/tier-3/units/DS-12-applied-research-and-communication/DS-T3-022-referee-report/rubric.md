# DS-T3-022 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report grasps why each claimed number could mislead and what the paper's design can and cannot identify. |
| 2 | Technical correctness | 20 | Tools match independent calculations; hidden-world accuracy, null-world behaviour and permutation procedure are correct. |
| 3 | Implementation quality | 15 | Clean, tested, deterministic tools; the review script regenerates everything. |
| 4 | Methodology and evidence | 15 | Concerns are ranked, each supported by a number and a check; the re-analysis is justified and its assumptions stated. |
| 5 | Testing and evaluation | 15 | At least 10 meaningful member tests including planted-flaw examples and a null world. |
| 6 | Documentation and reproducibility | 10 | A clean-environment run regenerates all report numbers; outputs are tidy and labelled. |
| 7 | Critical thinking and limitations | 10 | Proportionate conclusions: what survives, what does not, what the design cannot tell; no overclaiming in either direction. |
| 8 | Presentation and communication | 5 | A regulator could act on the recommendation and the one-paragraph summary. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight, for example by quantifying a risk or testing an assumption unprompted. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps that do not affect trustworthiness. |
| **Developing** | 50–69% | Partly meets the requirement: some choices unjustified or untested. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. |

## Gates (pass/fail, independent of points)

1. **Integrity:** the AI-use declaration in `REPORT.md` is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns your tests from a clean environment and gets your reported results.
3. **Defence:** you trace assessor-chosen cases and handle the unseen modification with sound reasoning.
4. **Privacy and safety:** no personal data in the report; any safeguards required in §D.3 are present.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Report asserts a flaw with no number or check from the script | Up to −6 from dimension 4 |
| Declares the model ineffective (rather than the evidence insufficient) without support | Up to −6 from dimension 7 |
| Quotes the whitepaper's numbers as reproduced without reproducing them | Up to −5 from dimension 6 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
