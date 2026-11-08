# ML-T1-021 Evaluation Rubric (public)

This rubric is public so you know exactly how you will be judged. Assessors also use a confidential marking guide with calibration notes, but it never adds criteria that are not listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | The report ties each rule (codes, ranges, checksum, version) to a failure it prevents in the meter-vending service. |
| 2 | Technical correctness | 20 | Public and hidden tests pass; error pairs are exactly as specified; scoring is exact and stable. |
| 3 | Implementation quality | 15 | Small, readable functions; no mutation of inputs; no unsafe deserialisation; one code path for validation. |
| 4 | Methodology and evidence | 15 | Hostile inputs were enumerated deliberately rather than only tried until tests passed; the limits of a checksum are stated correctly. |
| 5 | Testing and evaluation | 15 | At least 8 own tests including fuzz and tamper tests; edge cases beyond those given. |
| 6 | Documentation and reproducibility | 10 | Clean-environment run passes; `REPORT.md` is complete and the bundle format is documented. |
| 7 | Critical thinking and limitations | 10 | Honest account of what validation cannot catch (drift, wrong-but-valid values) and of the checksum's threat model. |
| 8 | Presentation and communication | 5 | An on-call engineer could read the report and understand each error code. |
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
| Model loaded with pickle, `eval`, `exec` or `joblib` | Up to −10 from dimension 2 |
| Only the first validation error reported instead of all | Up to −4 from dimension 2 |
| Batch prediction that raises on one bad record | Up to −5 from dimension 3 |
| Hard-coded field names instead of using the schema argument | Up to −6 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
