# DS-T1-002 Forensic Findings

**Member:** `<name>`  **Commit:** `<sha>`

At most 1,500 words plus tables. Write for the finance team: explain the cause in plain language first, then the technical detail.

## 1. Summary for finance (5 sentences or fewer)

How many defects, what they did to agents' pay overall, and whether the corrected settlement now matches the switch.

## 2. Defects

Repeat this block for each defect, numbered D1, D2, ...

### D<n>: <short name>

| Field | Finding |
|---|---|
| Function | |
| Specification sentence violated | (quote the docstring) |
| Symptom in the data | (what you saw first) |
| Root cause | (one or two sentences) |
| Minimal example | (name of the regression test) |
| Fix | (one or two sentences, and the commit SHA) |
| Isolated impact | (from `outputs/impact.csv`: count, value, fees, commission, agent-days) |

## 3. Why the isolated impacts do not add up

Compare the sum of the isolated rows with the full-legacy row. Explain which defects mask or amplify each other, with one concrete example.

## 4. Who was underpaid, and who was overpaid?

Describe which kinds of agents gained or lost commission under the legacy code (for example: agents whose tier changed, agents with messy IDs, agents not in the tier file), with counts. Do not list individual agents' amounts in this report.

## 5. Defects the control totals cannot see

Which of your defects did not change the reconciliation with `switch_control_totals.csv`, and how did you find them?

## 6. Handling a real investigation (one paragraph)

Access control, communication of corrected payments to agents, and retention and deletion of the forensic copy (NDPA 2023).

## 7. What I would add to stop this happening again

Two or three concrete safeguards (assertions, tests or monitoring), each linked to the defect it would have caught.
