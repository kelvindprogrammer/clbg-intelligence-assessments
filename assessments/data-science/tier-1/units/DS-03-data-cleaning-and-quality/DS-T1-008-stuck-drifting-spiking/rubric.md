# DS-T1-008 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You explain why each rule exists (sensor resolution and stuck runs, robust scale and spikes, latency vs clock error) and why measurement order matters. |
| 2 | Technical correctness | 25 | Public and hidden tests pass: per-fault recall, no false alarms on clean data or real episodes, late uploads not treated as clock faults, accurate corrected timestamps and drift estimates. |
| 3 | Implementation quality | 15 | Each rule is a small, pure function; the pipeline applies them in the specified order; the spike rule is vectorised or otherwise fast enough; values are never modified. |
| 4 | Methodology: rules → evidence | 10 | Per-device counts for each flag; a plot or table of clock offset against time that shows the drift, the steps and the late uploads. |
| 5 | Testing and evaluation | 20 | At least 12 member tests on hand-built inputs, each isolating one rule or edge case (window edges, NaN in runs, MAD = 0, exact thresholds), plus at least two that reproduce a §B trap. |
| 6 | Documentation and reproducibility | 10 | A clean run reproduces the outputs; the README explains how; requirements are bounded. |
| 7 | Critical thinking and limitations | 5 | What each rule cannot detect (slow calibration drift, a fault that stays within range and keeps varying), and when a rule could hide a real event. |
| 8 | Presentation and communication | 5 | A concise report that a field-team lead could act on. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight. For example: a sensitivity analysis of the spike rule, or a clear demonstration of what arrival-order processing breaks. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps. |
| **Developing** | 50–69% | Partly meets the requirement. Rules mostly right, but an ordering or masking mistake causes false flags or misses. |
| **Beginning** | 0–49% | Missing or incorrect rules; values clipped or interpolated; flags not combinable. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** the assessor reruns the CLI from a clean environment and gets the submitted outputs.
3. **Defence:** the member decodes a flag value and applies the Hampel rule by hand correctly.

## Automatic deductions

| Issue | Deduction |
|---|---|
| The raw feed or `qc_config.json` was modified | Gate fail until corrected |
| Any output `value` differs from the raw value (clipping, interpolation) | Up to −10 from dimension 2 |
| Parameters hard-coded instead of read from the config | Up to −5 from dimension 3 |
| Fault locations hard-coded (device IDs, dates) | Up to −15 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
