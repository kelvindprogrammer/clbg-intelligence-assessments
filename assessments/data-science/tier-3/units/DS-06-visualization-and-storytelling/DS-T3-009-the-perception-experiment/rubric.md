# DS-T3-009 Evaluation Rubric (public)

This rubric is public so you know how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Explains lie factor, compression and why participants are the unit of analysis, with reference to the original paper. |
| 2 | Technical correctness | 20 | Public and hidden tests pass: honest geometry, balanced design, participant-level bootstrap, recovered ranking in an unseen world. |
| 3 | Implementation quality | 10 | Clean separation of rendering, design and analysis; vectorised bootstrap; closed figures; deterministic seeding. |
| 4 | Methodology and experimentation | 25 | Pre-registration with a decision rule, justified sample size, power curves in two worlds, and a deviation log. |
| 5 | Testing and evaluation | 10 | Randomised honesty property test, balance checks, and a sanity check against the known observer parameters. |
| 6 | Documentation and reproducibility | 5 | One command regenerates all figures and numbers; commit history shows the pre-registration first. |
| 7 | Critical thinking and limitations | 15 | Separates what a simulation can show about a pipeline from what it cannot show about people; handles disagreement with the literature honestly. |
| 8 | Presentation and communication | 5 | Figures are titled by finding with units and uncertainty; the poster guideline is usable. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90-100% | Exceeds the requirement with insight, for example by quantifying uncertainty or testing an assumption nobody asked about. |
| **Proficient** | 70-89% | Fully meets the requirement with minor gaps that do not affect trustworthiness. |
| **Developing** | 50-69% | Partly meets the requirement; some claims are unjustified or untested. |
| **Beginning** | 0-49% | Missing, incorrect or unexplained. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with what the defence shows.
2. **Reproducibility:** the assessor reruns your work from a clean environment and obtains the submitted results.
3. **Defence:** you trace assessor-chosen results and handle an unseen modification with sound reasoning.
4. **Privacy and ethics:** no real personal data is introduced; any limits stated in §D are respected.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Ranking, encoding names or world parameters hard-coded in the analysis | Up to -10 from dimension 2 |
| Pre-registration committed after results | Up to -10 from dimension 4 |
| Bootstrap over trials instead of participants | Up to -6 from dimension 2 |
| Modified `observer.py` | Gate fail until corrected |

Outcome bands: [placement framework](../../../../../../docs/placement-framework.md).
