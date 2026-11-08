# DS-T3-001 Evaluation Rubric (public)

This rubric is public so you know how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Explains propagation, laundering and non-cascading findings with reference to the graph, not to the code. |
| 2 | Technical correctness | 25 | Public and hidden tests pass: effective licences, findings, attribution, `can_use`, CLI; no false positives on compliant data. |
| 3 | Implementation quality | 10 | Memoised, iterative or cycle-safe traversal; clean separation of graph, licence rules and integrity checks. |
| 4 | Methodology and research | 20 | `LICENCE_MODEL.md` cites section-level primary sources and gives at least four substantive, correct divergences with sensible tool responses. |
| 5 | Testing and evaluation | 10 | Constructed catalogues (diamond, self-loop, NC chain) and a scale test; tests assert findings exactly. |
| 6 | Documentation and reproducibility | 10 | Clean run from scratch; report numbers regenerate from the CLI output. |
| 7 | Critical thinking and limitations | 10 | Distinguishes decision support from legal advice; identifies what must go to a human; handles the personal-data extension thoughtfully. |
| 8 | Presentation and communication | 5 | Reuse decisions and citations are clear to a non-specialist lab director. |
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
| Licence or dataset names hard-coded in the rules | Up to -10 from dimension 2 |
| Primary sources not cited (secondary summaries only) | Up to -8 from dimension 4 |
| Catalogue or data files modified | Gate fail until corrected |

Outcome bands: [placement framework](../../../../../../docs/placement-framework.md).
