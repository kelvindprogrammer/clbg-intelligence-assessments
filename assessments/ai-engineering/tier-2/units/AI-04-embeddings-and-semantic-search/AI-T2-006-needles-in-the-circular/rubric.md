# AI-T2-006 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Links design choices to the two query types and the dilution problem. |
| 2 | Technical correctness | 20 | Public and hidden tests pass: exact components and the performance bars on re-seeded worlds. |
| 3 | Implementation quality | 15 | Clear separation of chunking, lexical, dense and fusion; no leakage of test data; deterministic. |
| 4 | Methodology and evidence | 15 | Per-type results on several seeds; dev/test discipline; ablations; uncertainty acknowledged. |
| 5 | Testing and evaluation | 15 | At least 10 own tests including boundaries; failure cases examined. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run reproduces the tables. |
| 7 | Critical thinking and limitations | 10 | Honest about the toy embedder, small corpus and what would change with real text. |
| 8 | Presentation and communication | 5 | A compliance lead could choose from the report. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight, for example by testing a claim the brief did not ask about. |
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
| Any use of test queries for tuning or selection | Up to -12 from dimension 2 |
| Reporting only an overall MRR with no per-type breakdown | Up to -5 from dimension 4 |
| Using scikit-learn, faiss or other retrieval libraries | Up to -8 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
