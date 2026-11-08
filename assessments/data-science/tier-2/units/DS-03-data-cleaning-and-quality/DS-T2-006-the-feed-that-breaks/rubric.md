# DS-T2-006 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You explain why each fault class matters downstream (payouts, fraud rules, regulator report), and why schema checks miss unit changes, truncation and re-sends. |
| 2 | Technical correctness | 20 | Hidden sequences: every status matches the policy; row quarantine is exact; holidays are accepted; nothing is accepted twice. |
| 3 | Architecture and implementation quality | 20 | Truly contract-driven; reading, row rules, delivery rules, baselines, routing and alerting are separable; deterministic and rerunnable; it fails safe (an exception quarantines, it doesn't accept). |
| 4 | Methodology: contract and thresholds | 10 | Every rule has an owner, a severity and a justification; thresholds come from evidence in the public sequence and from reasoning about the faults, not from fitting 20 days. |
| 5 | Testing and evaluation | 15 | At least 15 member tests; at least six fault fixtures including an unseen fault class and a good-but-unusual day; an honest per-delivery account of the public ledger. |
| 6 | Documentation and operations | 10 | `DESIGN.md` covers architecture, alert routing, least privilege, retention, trust boundary and release procedure. |
| 7 | Critical thinking and limitations | 10 | What the framework still can't catch (a one-hour clock shift with a correct offset, gradual drift, movable holidays), and the cost of false alarms. |
| 8 | Presentation and communication | 5 | A partner could read the contract, and an on-call engineer could act on the alerts. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight. For example: incremental idempotent processing, a release workflow, or a statistic for the hidden clock shift. |
| **Proficient** | 70–89% | Meets every requirement with minor gaps. |
| **Developing** | 50–69% | Catches schema faults but misses a statistical one, or baselines learn from bad deliveries; the contract is incomplete. |
| **Beginning** | 0–49% | Hard-coded checks, no baseline, holidays quarantined, or bad rows reaching the accepted area. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** rerunning on the public inbox reproduces `outputs/`.
3. **Defence:** the member predicts the verdict on an unseen delivery and explains the code path.
4. **Fail-safe:** a malformed delivery never results in rows being accepted.

## Automatic deductions

| Issue | Deduction |
|---|---|
| Faulty days hard-coded by date | Gate fail |
| Public inbox modified | Gate fail until corrected |
| Thresholds in code that are not in the contract | Up to −5 from dimension 3 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
