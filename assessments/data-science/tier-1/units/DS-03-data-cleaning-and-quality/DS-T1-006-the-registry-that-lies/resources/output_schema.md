# DS-T1-006 Output Schema

## `clean_registry.csv`

There is one row per **inferred student**. Rows are sorted by `student_id`. The file is UTF-8 with a header row, `\n` line endings, and an empty string for null values.

| Column | Type | Rule |
|---|---|---|
| `student_id` | string | `STU00001`, `STU00002`, …, assigned in ascending order of the smallest `record_id` in the group. This makes the IDs deterministic. |
| `source_record_ids` | string | `;`-separated `record_id`s merged into this student, ascending. |
| `matric_no` | string | Canonical `YY/DEP/NNNN`. |
| `first_name` | string | Title case. |
| `last_name` | string | Title case. |
| `date_of_birth` | ISO date or empty | Empty only if `dob_status` is `missing` or `invalid`. |
| `dob_status` | enum | `ok`, `ambiguous`, `missing`, `invalid`. |
| `state_of_origin` | enum or empty | One of `resources/reference/nigerian_states.txt`. |
| `phone_e164` | string or empty | `^\+234[789][01]\d{8}$`. |
| `email` | string or empty | Lower case. |
| `jamb_score` | int or empty | 0–400. |
| `admission_date` | ISO date or empty | |
| `department` | enum | One of `resources/reference/departments.txt`. |
| `level` | int | 100–500 in steps of 100. |
| `cgpa_5pt` | float (2 dp) or empty | Always on the 5.0 scale after any rescaling. |
| `cgpa_rescaled` | bool (`True`/`False`) | `True` if the value was converted from another scale. |

**Conflict resolution when merging duplicates.** When records in a group disagree on a field, choose the most frequent valid value, breaking ties by the smallest `record_id`. Log each disagreement in `issues.csv` with `issue_type = merge_conflict`. You may use a different rule if you justify it in your report.

## `issues.csv`

There is one row per detected defect. The file is sorted by `record_id`, then `column`, then `issue_type`.

| Column | Type | Rule |
|---|---|---|
| `record_id` | string | The input row the issue was found in. Use the smallest `record_id` in the group for group-level issues. |
| `column` | string | The input column, or `*` for row-level issues such as duplicates. |
| `issue_type` | string | Your own controlled vocabulary, documented in your report. These are required at minimum: `missing`, `invalid`, `ambiguous`, `normalized`, `duplicate`, `rescaled`, `merge_conflict`. |
| `original_value` | string | The raw value, verbatim. Leave it empty for row-level issues. **The assessor-facing file may contain personal data, so don't publish it.** |
| `action` | string | A short description, e.g. `mapped 'Lag.' -> 'Lagos'`, `set null: truncated (10 digits)`, `merged into STU00042`. |
