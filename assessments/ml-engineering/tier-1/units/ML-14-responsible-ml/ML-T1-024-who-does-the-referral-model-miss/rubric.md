# ML-T1-024 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report links each audit step to the programme question and to the harm of a missed referral. |
| 2 | Technical correctness | 20 | Public and hidden tests pass: rates, guards, bootstrap procedure, calibration and card content are exact. |
| 3 | Implementation quality | 15 | Pure, vectorised where natural, with explicit handling of undefined cases; no duplicated logic across functions. |
| 4 | Methodology and evidence | 15 | The report uses the interval, not the point gap, for its claims, and explains the small-group decision. |
| 5 | Testing and evaluation | 15 | At least 8 own tests including no-positives and zero-in-interval cases. |
| 6 | Documentation and reproducibility | 10 | A clean-environment run of `audit.py` reproduces the report's tables. |
| 7 | Critical thinking and limitations | 10 | Honest statement of what the audit cannot show: causes, other groupings, real-world harm, unobserved outcomes. |
| 8 | Presentation and communication | 5 | A programme director could act on the summary and the card. |
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
| Undefined rates silently reported as 0 or NaN | Up to -6 from dimension 2 |
| Bootstrap resamples all rows rather than within groups | Up to -6 from dimension 2 |
| Ranks or reports a gap for a group below the size guard | Up to -5 from dimension 4 |
| Claims causation (for example that a zone is 'biased') from a gap | Up to -4 from dimension 7 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
