# Scoring Templates

| Template | Use |
|---|---|
| [score-sheet.md](score-sheet.md) | Score one submission. Generate an assessment-specific version with `python tools/rubric-tools/scoresheet.py <ID>`. |
| [placement-record.md](placement-record.md) | A member's cumulative placement evidence per subtrack. Keep it **privately**, never in this repository. |
| [feedback-template.md](feedback-template.md) | Structured feedback returned to the member. |
| [progress-tracker.md](progress-tracker.md) | A member-facing personal tracker of attempts and placements. |

CSV workflow:
```bash
python tools/rubric-tools/scoresheet.py DS-T1-006 --csv > DS-T1-006_<member>.csv
# fill in the 'awarded' and 'evidence_and_comments' columns, then:
python tools/rubric-tools/scoresheet.py --score DS-T1-006_<member>.csv
```
