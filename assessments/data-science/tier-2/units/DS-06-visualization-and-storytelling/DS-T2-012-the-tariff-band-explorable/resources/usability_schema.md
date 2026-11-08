# Usability data schema (DS-T2-012)

Record your usability sessions in two CSV files under `usability/`. Use **participant codes only** (`P1`, `P2`, …). Never record names, phone numbers, emails, exact ages or addresses. The tests reject any column that is not listed here.

## `usability/sessions.csv`: one row per participant per task

| Column | Type | Meaning |
|---|---|---|
| `participant_code` | `P<number>` | Pseudonymous code |
| `session_date` | `YYYY-MM-DD` | Date of the session |
| `device` | `phone` · `tablet` · `laptop` | What the participant used |
| `task_id` | `T<number>` | Task from your protocol |
| `completed` | `true` / `false` | Task completed without help |
| `time_s` | number ≥ 0 | Seconds to complete (or to give up) |
| `errors` | integer ≥ 0 | Wrong turns you observed |
| `comprehension_pre` | integer 0–5 | Score on your comprehension questions *before* using the explorable |
| `comprehension_post` | integer 0–5 | The same questions *after* |
| `consent_recorded` | `true` | Must be `true`. A row without recorded consent must not exist |

## `usability/sus.csv`: one row per participant

| Column | Type | Meaning |
|---|---|---|
| `participant_code` | `P<number>` | Matches `sessions.csv` |
| `q1` … `q10` | integer 1–5 | System Usability Scale responses (Brooke, 1996), in the standard item order |

Store consent forms **outside** the repository (paper or a private folder). The repository holds only the pseudonymous data above.
