# DS-T2-012 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration exemplars, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You can explain why a higher-band tariff can give a lower effective price, which assumptions drive that result, and when it breaks (undelivered hours). |
| 2 | Technical correctness (model, data, parity) | 15 | Hidden property checks pass. Every tariff is sourced and dated. `PARITY.md` shows the page and the Python model agree on 10 scenarios. |
| 3 | Implementation quality (the explorable) | 15 | Works from disk on a phone; keyboard accessible with labelled controls and an `aria-live` output; no tracking; clean, readable code; assumptions on screen. |
| 4 | Methodology: usability protocol and baseline comparison | 20 | The protocol was committed before the sessions, with consent, tasks, pre/post comprehension, SUS and a counterbalanced comparison with the static baseline. It was run with 3–5 non-member adults. |
| 5 | Testing and evaluation | 10 | At least 8 member tests including parity. The analysis is reproducible from the CSVs. The results are interpreted without overclaiming from a small sample. |
| 6 | Documentation and reproducibility (sources) | 10 | `SOURCES.md` names the distribution company and tariff order with URLs and dates. Every other parameter is sourced or labelled as an adjustable assumption. |
| 7 | Critical thinking and limitations | 10 | Honest findings (including where the baseline won), the limits of the model and the study, and neutrality reviewed by a peer. |
| 8 | Presentation and communication | 10 | Plain-language copy a household can follow; each view answers its stated question; the revision is shown before and after. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight. For example, delivered-hours uncertainty that participants demonstrably understood, or a second test round after revision. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps. |
| **Developing** | 50–69% | Partly meets the requirement. For example, a protocol written after the sessions, no baseline, or unsourced numbers. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. For example: placeholder tariffs, no participants, or campaigning copy. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence. No fabricated usability data.
2. **Ethics:** consent was obtained (records kept offline, available to the assessor on request), adults only, and no personal data in the repository.
3. **Reproducibility:** tests pass, and the page opens from disk.
4. **Defence:** a live phone demo and a correct prediction after a tariff change.

## Automatic deductions

| Issue | Deduction |
|---|---|
| A number on the page with no source or assumption label | Up to −5 from dimension 6 |
| Protocol committed after the first session | Up to −8 from dimension 4 |
| Analytics or data-sending code in the page | Gate 2 fail until removed |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
