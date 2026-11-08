# Feed Validation Framework: Design

**Member:** `<name / GitHub username>`  **Submission commit:** `<sha>`  **Date:** `<date>`

> Limit: 2,500 words plus diagrams. Audiences: the data-team lead (sections 1–6) and the partner's integration team (section 3).

## 1. Summary (≤ 150 words)

## 2. Architecture
A diagram of inbox → validation stages → accepted / quarantine / alerts, and where state lives.

## 3. The contract
How it is structured, and why. For each rule family: owner, severity and justification of thresholds.

| Rule | Owner | Severity | Threshold | Justification |
|---|---|---|---|---|
| | | | | |

## 4. Baselines
Volume and distribution: what is compared with what; calendar handling; behaviour with short history; why only accepted deliveries are used (with an example from the public sequence).

## 5. Alerting and routing
Severity levels, recipients, channels and the "holiday" case.

## 6. Security, privacy and operations
Least privilege, retention, trust boundary (malformed or malicious files), and the release procedure with its audit trail.

## 7. Evaluation
### 7.1 Public sequence
| Date | Status | Findings | My explanation |
|---|---|---|---|
| | | | |
### 7.2 Fault-injection fixtures
| Fixture | Fault | Expected | Got |
|---|---|---|---|
| | | | |

## 8. Limitations
What this framework still cannot catch, and what it would cost to catch it.

## 9. Reproduction
```bash
```
