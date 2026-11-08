# DS-T1-003 Performance Notes

**Member:** `<name>`  **Commit:** `<sha>`

At most 1,200 words plus tables. Quote numbers from `outputs/profile_legacy.txt` and `outputs/benchmark.csv`.

## 1. Environment

CPU, RAM, OS, and the Python, NumPy and pandas versions. What else was running?

## 2. Where the legacy time goes

For each legacy function: the top two or three entries of the profile, and what they tell you. Explain, with evidence, why `standardised_anomalies` scales worse than linearly.

## 3. How each fast function works

For each function, three to six sentences: the representation (for example, a complete calendar), the key array operations, and how NaN, absent days and boundaries are handled. One small worked example for the onset rule.

## 4. Results

| Function | Legacy sample (s) | Fast sample (s) | Legacy medium (s) | Fast medium (s) | Speed-up medium | Fast full (s) | Peak MB full |
|---|---|---|---|---|---|---|---|
| monthly_totals | | | | | | | |
| longest_dry_spell | | | | | | | |
| onset_dates | | | | | | | |
| standardised_anomalies | | | | | | | |

Report medians with the IQR. Then give your **estimate** of legacy time on `full`, and how you estimated it.

## 5. Equivalence evidence

Which tests, which generators, and how many random seeds. List the equivalence bugs you found along the way, and the test that now catches each one.

## 6. Limitations and doubts

Timing noise, hardware, anything about the onset rule you would question (without changing it), and what evidence you would want before replacing the legacy pipeline in production.
