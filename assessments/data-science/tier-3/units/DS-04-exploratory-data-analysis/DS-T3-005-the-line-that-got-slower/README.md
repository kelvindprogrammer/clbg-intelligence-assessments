# DS-T3-005: The Line That Got Slower: Decomposing a Headline and Finding the Instrument Break

> *Average delay on the BRT corridor rose 4.5% after the new timetable. Every single route got faster. Both statements are true; find out why, and what else is hiding in the data.*

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T3-005` |
| **Title** | The Line That Got Slower: Decomposing a Headline and Finding the Instrument Break |
| **Subtrack** | Data Science |
| **Tier** | 3: Advanced and Research-Informed |
| **Unit** | [DS-04: Exploratory Data Analysis](../README.md) |
| **Format** | Open-ended investigation (secondary: implementation) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 4 · Engineering 2 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 14-22 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM; no GPU; no network after setup |
| **Recommended prerequisites** | pandas (`groupby`, `pivot_table`), weighted means, and a first look at Simpson's paradox (for example DS-T1-009). No time-series background is required; changepoint detection is yours to research. |
| **Skills developed** | Aggregate decomposition, paradox diagnosis, instrument-break detection, correction with uncertainty, exploration discipline |
| **Technologies** | Python 3.10+, pandas, numpy, pytest; matplotlib optional |

---

## B. Problem Statement

A bus rapid transit (BRT) corridor in a Nigerian megacity runs eight routes of different lengths, operated by three companies. On 30 April a **new timetable** took effect: it moved service from short feeder routes to the long trunk routes. The Transport Authority's monthly dashboard now says:

> *Average delay per trip rose from 9.7 to 10.1 minutes (+4.5%) since the new timetable.*

The commissioner wants to know whether to revert the timetable. Operations staff insist this is wrong: they say every route is running **faster**. Both statements can be true. The question for you is not "who is right" but **what the data can and cannot support**, and whether either side has the right number.

You have `route_day.csv`: for each day, route and operator, the number of trips and the mean recorded delay in minutes (120 days, 2,880 rows). Nobody has told you what is in it. A competent exploration should end with answers to these questions, each supported by a computation you can rerun:

1. **Reproduce the headline.** What exactly changed, and by how much?
2. **Decompose it.** How much of the change comes from delays changing *within* routes, and how much from the *mix* of trips shifting between routes of different lengths?
3. **Find the reversal.** Which routes move in the opposite direction to the headline?
4. **Audit the measurement.** Delays are recorded by each operator's own tracker. Is there evidence that one tracker's level changed during the period? If so: which operator, from which date, by how much, and what does the headline become once you correct for it?
5. **State what remains uncertain.** What would you want before recommending anything to the commissioner?

Item 4 is deliberately not announced anywhere in the data. The only place it exists is in comparisons between operators on the same routes and days. The tests do not tell you the answer. They check whether your *method* finds it in data generated from different seeds, with a different operator and break date.

**This is an open-ended assessment.** The tests check the functions below, and the report and ledger carry the rest: how you explored, what you tried and discarded, and how you communicated limits. A confident analysis that confirms every idea it had has probably not looked hard enough.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Run a hypothesis-driven exploration and record every hypothesis, test and verdict, including refuted ones.
2. Decompose a change in an aggregate exactly into within-segment and mix components, and interpret both.
3. Detect and explain a Simpson-style reversal without being told where to look.
4. Detect a measurement-instrument level shift by comparing peers on the same routes and days, and locate it in time.
5. Estimate the shift from data, correct the headline, and show how much of the original story depended on the artefact.
6. Communicate a nuanced finding, with its uncertainty and the follow-up data needed, to a non-technical decision-maker.

---

## D. Technical Requirements

### D.1 Mandatory requirements

Implement the toolkit in `eda_lab` (signatures are fixed in [`starter/eda_lab/__init__.py`](starter/eda_lab/__init__.py)). `df` columns: `date`, `route`, `operator`, `trips`, `mean_delay_min`. "Before" means dates **before** `split_date`; "after" means on or after it. All means are **trip-weighted**.

| ID | Function | Requirement |
|---|---|---|
| **R0** | `load_route_day(path)` | Read the CSV with `date` as datetime. Raise `ValueError` if a required column is missing. |
| **R1** | `headline_change(df, split_date)` | Relative change `(M_after - M_before) / M_before` of the trip-weighted mean delay. |
| **R2** | `kitagawa(df, split_date, by="route")` | Return `{"total", "within", "mix"}` in minutes with `within + mix == total` exactly (to 1e-9). Define period shares `w` (trip share of each segment) and rates `r` (trip-weighted mean delay of each segment). Use the symmetric (Kitagawa / Das Gupta) form: `within = sum((w0+w1)/2 * (r1-r0))`, `mix = sum((r0+r1)/2 * (w1-w0))`. |
| **R3** | `reversal_segments(df, split_date, by="route")` | Sorted labels of segments whose own change in rate has the opposite sign to the headline `total`. |
| **R4** | `locate_instrument_break(df)` | Return `(operator, "YYYY-MM-DD")`: the operator whose recorded delay changed level relative to the others, and the first affected date. **Do not hard-code operator names or dates.** |
| **R5** | `adjusted_headline_change(df, split_date, operator, break_date)` | Estimate the operator's level shift from data (from `break_date` on, relative to the other operators on the same route and day), remove it from that operator's delays, and return the recomputed headline relative change. |
| **R6** | `validate_ledger(path)` | Return a list of problems (empty when valid) for a hypothesis ledger CSV. The rules are in §D.2. |

### D.2 The hypothesis ledger and exploration discipline

`hypotheses.csv` must have exactly the columns `id, hypothesis, test, evidence, verdict, confidence`, with unique ids, at least **eight** rows, every `test` and `evidence` non-empty, `verdict` one of `supported`, `refuted`, `inconclusive`, and at least **two** `refuted` rows. `confidence` is free text (`low`/`medium`/`high` suggested). `evidence` should name a figure, table or notebook cell. Your own tests must include at least one constructed example for `kitagawa` (a tiny table where the answer is known by hand) and one for `locate_instrument_break`.

Other requirements:
- A notebook or script that regenerates every figure and number in `REPORT.md`.
- At least three figures, each titled with its **finding** rather than its variable names, with units and an uncertainty or sample-size annotation where relevant.
- `REPORT.md` must include a plain-language paragraph for the commissioner that answers "should we revert the timetable?" and says what you would need to know before saying yes or no.

### D.3 Privacy and responsibility

No personal data: the data is aggregated by route, operator and day, and is synthetic. If the same method were used on trip-level fare-card data, it would involve travel patterns of identifiable people. In `REPORT.md` write two sentences on what aggregation threshold you would apply before sharing route-level results (small-cell suppression) and why.

### D.4 Optional enhancements

Bootstrap an interval for the corrected headline (resample days within blocks); show the decomposition by operator and by weekday type; test whether the weekday pattern changed.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/route_day.csv`](resources/data/route_day.csv): 2,880 rows (120 days x 8 routes x 3 operators), about 135 KB |
| **Columns** | `date` (ISO), `route`, `operator`, `trips` (count), `mean_delay_min` (mean recorded delay, minutes) |
| **Provenance** | **Synthetic**, from a deterministic CLBG generator (seed 2026). Route names echo real corridors; operator names and every number are invented. The generator is not published, because it would reveal the planted structure. |
| **Licence** | CC BY 4.0 |
| **Integrity** | SHA-256 checked by the contract test. Do not edit the file. |

**Known limitations.** The delay is a daily mean per route-operator, not per trip, so within-day variation is invisible. There is no weather, incident or passenger data. Delays are recorded by each operator's own system.

**Setup**
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract
pytest
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `eda_lab/` package | The executable analysis tools |
| 2 | `tests/test_member_*.py` (including hand-checkable cases) | Evidence you verified the tools independently of the provided tests |
| 3 | `notebook.ipynb` or `analysis.py` and ≥ 3 figures | The reproducible exploration behind the report |
| 4 | `hypotheses.csv` | A record of exploration discipline, including refuted ideas |
| 5 | `REPORT.md` from the [template](submission-template/REPORT.md) (≤ 1,500 words plus tables) | The decision-maker memo and limits |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 7 | A 10-minute live defence | Verifies understanding of the analysis and ability to extend it |

---

## G. Acceptance Criteria

Criteria marked ⚙ are checked by the public and hidden test suites. Criteria marked ✍ are checked by an assessor.

1. ⚙ Public tests: headline, exact decomposition, reversal list, instrument operator and date (within 2 days), adjusted headline and ledger validation.
2. ⚙ Hidden tests on four re-seeded datasets: the operator and break date are found within 2 days, the adjusted headline is within 0.004 of the true no-artefact headline, the decomposition matches an independent computation to 1e-9, and the reversal list is all routes with the artefact and empty without it. *Justification of 0.004:* the reference error is at most 0.0008, and ignoring the artefact leaves an error of about 0.05, so 0.004 separates the two by more than a factor of 10 without demanding unrealistic precision.
3. ⚙ A dataset with no artefact does not produce a large spurious adjustment (the adjusted headline stays within 0.01 of the raw one).
4. ✍ `hypotheses.csv` validates with your own `validate_ledger`, contains at least two genuinely refuted hypotheses, and each cited evidence item exists in the notebook.
5. ✍ `REPORT.md` reports the decomposition in minutes, the estimated shift with an uncertainty statement, and the corrected headline, and makes clear which conclusions survive the correction.
6. ✍ Every figure has a finding-style title, labelled units and an indication of uncertainty or sample size.
7. ✍ The commissioner paragraph is decision-ready: a recommendation conditional on named evidence, not a hedge.

---

## H. Evaluation Rubric

The full rubric with performance levels is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 15 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Methodology and exploration discipline | 20 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 5 |
| Critical thinking and limitations | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates (passing defence, reproducible run, integrity declaration). See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. Create a **private** GitHub repository named `clbg-DS-T3-005-<your-github-username>` from this assessment's `starter/`, `tests/` and `resources/` folders and the `submission-template/` files.
2. Expected structure:
   ```text
   clbg-DS-T3-005-<username>/
   ├── eda_lab/                # your package (from starter/)
   ├── tests/                  # provided tests + your own test_member_*.py
   ├── resources/              # unchanged
   ├── notebook.ipynb | analysis.py   # the exploration that produced your ledger and figures
   ├── hypotheses.csv          # the hypothesis ledger (rules in section D.2)
   ├── REPORT.md               # findings memo, AI-use declaration
   └── AI_USE_AND_SOURCES.md
   ```
3. Commit as you work. Your commit history is evidence of authorship (see §K); a single "final" commit will be questioned at defence.
4. Add the CLBG assessor account as a read-only collaborator and file a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core requirements.

1. Bootstrap the corrected headline with day blocks and report an interval.
2. Show that the reversal disappears when you correct for the artefact, and explain precisely why (headline sign versus route signs).
3. Test whether a different split date (a placebo) produces comparable decompositions, and what that tells you about the timetable effect.
4. Write a short data-quality letter to the three operators asking how their trackers differ.

---

## K. Assessment Integrity

**AI tools are permitted** to explain concepts, suggest idioms or review your code. They may not do the assessment for you, and you must be able to explain and modify every line you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md` (template in `submission-template/`): tool, purpose and an example prompt. Undisclosed use discovered at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** adapted code and any papers or documentation you relied on, with links.
- **Collaboration:** discuss *general techniques* only. Do not share code, results or report text.
- **How understanding is verified.** At a 10-minute defence the assessor will (1) ask you to explain in two minutes why every route can improve while the average worsens, using a number from your decomposition; (2) ask what evidence would convince you that the break is a tracker change rather than a real operational change; (3) set an unseen modification, such as decomposing by operator instead of route or moving the split date, to be run live with an interpretation.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Weighted means, groupby and pivot; the idea of confounding by mix. |
| **New skill developed** | Taking an aggregate headline apart (rate versus mix), auditing measurement, and separating an artefact from an effect. |
| **Decisions the member must make** | How to compare peers to detect a break; how to estimate a shift; how to weight; what to put in the ledger; how to answer a decision-maker under uncertainty. |
| **What must be investigated independently** | Whether any operator's level moved, when, and how much the headline depends on it. Nothing in the data says so. |
| **Why it is interesting** | A real-looking dashboard sentence is true, misleading and contaminated at once. The member must find all three layers. |
| **Evidence of competence** | Exact decomposition, a method that finds the break on unseen seeds, quantified correction, and a ledger that proves the exploration was honest. |
| **Misconceptions exposed** | "The average got worse, so performance got worse"; "if every group improves the total improves"; "outliers are the only data problems"; "if my hypothesis was confirmed I was right". |
| **Preparation for later work** | Leads to DS-08 causal and experimental thinking, DS-T3 data-quality work, and any analytics role where dashboards drive decisions. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
