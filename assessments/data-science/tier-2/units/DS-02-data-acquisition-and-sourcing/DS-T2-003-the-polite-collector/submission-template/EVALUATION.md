# Evaluation: DS-T2-003

**Member:** `<name>`  **Commit:** `<sha>`  **Command that regenerates every table:** `python experiments/compare.py ...`

> Limit: 1,500 words plus tables. Every number comes from the portal's log (`portal.log`, `portal.violations()`) or `portal.truth()`, not from your collector's own counters alone.

## 1. Set-up
- Scenario(s) and number of days (at least 5; extend `PUBLIC_SCENARIO` with further days and say what each day does):
- Strategies compared (at least two of your own, plus the baseline). For the baseline, use `MockPortal(..., enforce=False)` and say why:

## 2. Results per strategy (totals over all days)
| Strategy | Requests | Bytes | Disallowed | Too fast | Changes missed | Mean detection latency (days) | Drift detected on day |
|---|---|---|---|---|---|---|---|
| baseline | | | | | | | |
| | | | | | | | |

## 3. Day-by-day for your default strategy
| Day | Events (from truth) | Requests | Bytes | new / updated / withdrawn | Alarms | Quarantined |
|---|---|---|---|---|---|---|

## 4. Choice of default and its trade-off
Which strategy is the default, and why, from the numbers above? What does it give up?

## 5. Drift handling
What happened on the drift day? What happened to amendments published while pages were quarantined, and how would an operator recover?

## 6. Threats to validity
How might the mock differ from real portals (caching proxies, ETag behaviour, anti-bot measures, legal context)?
