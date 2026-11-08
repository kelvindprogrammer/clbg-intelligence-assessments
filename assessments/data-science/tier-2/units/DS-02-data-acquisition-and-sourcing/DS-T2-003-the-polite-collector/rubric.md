# DS-T2-003 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You can explain why each portal behaviour (session parameters, archive trap, silent amendments, 410s, template drift) threatens either politeness or correctness, and how your design answers it. |
| 2 | Technical correctness | 20 | Public and hidden tests pass: RFC 9309 edge cases, zero server-side violations, exact new, updated and withdrawn sets on an unseen scenario, drift alarms without data loss, and no stored personal data. |
| 3 | Architecture and implementation quality | 20 | Clear separation of fetching, robots, discovery, parsing and validation, storage and strategy. Politeness enforced in one place, so it can't be bypassed. Atomic state. Strategies are pluggable rather than copy-pasted. `DESIGN.md` justifies the choices and the alternatives you rejected. |
| 4 | Methodology: strategy comparison | 15 | At least two strategies plus the baseline over at least 5 days, with every R9 metric measured from the portal's log. The comparison is reproducible from `experiments/compare.py`, and the default strategy is chosen *from* the numbers. |
| 5 | Testing and evaluation | 10 | At least 15 member tests that would catch regressions: robots precedence, delay arithmetic, a crash mid-run, drift on each field type, and a budget overrun. |
| 6 | Ethics, terms and privacy | 10 | Every terms clause is mapped to a decision and a test. The minimisation is justified under NDPA 2023. You state what you would refuse to do even where it is technically possible. |
| 7 | Critical thinking and limitations | 10 | An honest account of what each strategy misses, how quickly drift is detected, what happens to amendments while pages are quarantined, and where the mock differs from real portals. |
| 8 | Presentation and communication | 5 | Concise documents with tables and one clear architecture diagram, readable by the civic group's non-specialist lead. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | A measured hybrid strategy or freshness–politeness frontier; drift repair with human approval; a thoughtful real-world terms review. The numbers drive every decision. |
| **Proficient** | 70–89% | All requirements met, with a sound design and a fair comparison. Minor gaps in tests or documentation. |
| **Developing** | 50–69% | The collector works but is fragile: politeness can be bypassed, drift is detected only for values, or the comparison is anecdotal. |
| **Beginning** | 0–49% | Violations in the server log, nulls written on drift, contact data stored, or no comparison. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Politeness:** the hidden scenario's server log shows zero disallowed and zero too-fast requests.
3. **Privacy:** no contact-officer data in `state_dir`.
4. **Defence:** you justify the design with your own numbers and complete the live modification.

## Automatic deductions

| Issue | Deduction |
|---|---|
| A provided test or `mocksite.py` modified to make tests pass | Gate fail until corrected |
| Real `time.sleep` in the collector, so tests take real time | Up to −5 from dimension 3 |
| A real site crawled without a written terms review | Up to −10 from dimension 6 |
| Mass withdrawal after a listing change | Up to −5 from dimension 2 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
