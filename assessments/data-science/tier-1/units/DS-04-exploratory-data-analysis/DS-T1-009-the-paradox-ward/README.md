# DS-T1-009: The Paradox Ward

> *The hospital with the worst death rate in the network may be the safest place to have emergency surgery. Prove it, quantify it, and explain it to a Commissioner.*

![Format: Investigation](https://img.shields.io/badge/format-investigation-0e8a16) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-009` |
| **Title** | The Paradox Ward: Stratified Exploration of Hospital Outcome Rankings |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-04: Exploratory Data Analysis](../README.md) |
| **Format** | Investigation (secondary: Implementation) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 8–14 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | pandas `groupby`, `crosstab` and `merge`; proportions and percentages; what a confidence interval is; running `pytest` |
| **Skills developed** | Stratified rate tables; case-mix analysis; detecting and explaining Simpson's paradox; direct standardisation; rate-gap decomposition; binomial uncertainty; writing evidence-based findings for a non-technical decision-maker |
| **Technologies** | Python 3.10+, pandas, numpy, matplotlib, pytest |

---

## B. Problem Statement

A fictional State Ministry of Health runs four public hospitals that perform emergency general surgery: **Ase Cottage**, **Idu Teaching**, **Kuramo General** and **Rimi Specialist**. The Ministry is about to publish its first hospital "league table". The draft ranks the hospitals by **crude 30-day mortality after emergency surgery** for 2024–2025. The hospital at the bottom will be placed under a "special measures" review, which means a management change, a public statement and a freeze on new consultants.

On the draft, Idu Teaching comes last, with roughly double Ase Cottage's death rate. Idu's Chief Medical Director has written to the Commissioner. She says the table is "statistically illiterate", because Idu is the network's referral centre and receives the patients the other hospitals cannot manage. The Commissioner's office has asked you, as an analyst, to settle the question **with evidence** before the table is published:

> *Is the ranking a fair comparison of surgical care? If not, what comparison would be fair, and what does it show?*

You have `admissions.csv`, with one row per emergency surgical admission (9,600 admissions). Each row records the hospital, the month, the patient's age band and sex, the **triage category** at arrival (1 = most severe, 4 = least), whether the patient was referred from another facility, the procedure group, length of stay, and whether the patient died within 30 days.

**What makes it hard.** The arithmetic is easy. The reasoning is not:

- An aggregate comparison can point in the **opposite direction** from every subgroup comparison. That is Simpson's paradox, and it is a statement about *composition*, not a statistical trick.
- Not every variable you stratify on is a confounder. Some change nothing, and one is a *proxy* for the real driver that only partly corrects the picture. You must check several candidates and show why one of them matters.
- Within strata, some cells are small. A stratum rate based on 70 patients has a wide interval, and "Hospital X is worst in triage 1" may not be a supportable claim at all.
- Even a correct stratified analysis cannot prove that care at one hospital is better. Triage category is coarse, and residual severity differences within a category are invisible in this data. Saying exactly what the data **cannot** show is part of the task.

**Known facts from the Ministry** (treat these as your only documentation):

- The triage scale is applied by the receiving hospital's emergency team using a common state protocol.
- `died_30d` is complete: the Ministry linked every admission to the death register, so there is no loss to follow-up.
- Idu Teaching is the designated referral centre for the network. The Ministry does not know how strongly this shapes its case mix.
- The data is **synthetic**. No real hospital, patient or outcome is described.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Build stratified rate tables** with correctly computed binomial (Wilson) intervals, and read them critically, including when a cell is too small to support a claim.
2. **Diagnose case-mix differences** between groups with a composition table, and explain how composition alone can produce an aggregate difference.
3. **Detect a Simpson's reversal** systematically, using a precise rule, across every pair of groups and several candidate stratifiers.
4. **Standardise** rates to a common population and **decompose** a crude gap into a composition effect and a rate effect that sum exactly to the gap.
5. **Distinguish a confounder from a non-confounder and from a proxy** using evidence, not intuition.
6. **Write findings for a decision-maker** that quantify every claim, state uncertainty, and are explicit about what the data cannot establish.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `paradox_ward` package in [`starter/paradox_ward/`](starter/paradox_ward/). The signatures are fixed because the tests import them. `load_admissions` and the CLI skeleton are provided. Rates are proportions in `[0, 1]`, not percentages.

| ID | Requirement |
|---|---|
| **R1** | `wilson_interval(events, n, z=1.96) -> (low, high)` returns the Wilson score interval, clipped to `[0, 1]`. It raises `ValueError` if `n <= 0` or `events` is outside `[0, n]`. |
| **R2** | `rate_table(df, by, outcome="died_30d", z=1.96)` returns one row per combination of the `by` columns, sorted by them, with columns `*by, n, events, rate, ci_low, ci_high`. |
| **R3** | `mix_table(df, group_col, stratum_col)` returns the case-mix table: index = groups, columns = strata (both sorted), cell = share of the group's rows in that stratum. Rows sum to 1. |
| **R4** | `find_reversals(df, group_col, stratum_col, outcome="died_30d", min_n=20)` returns one row per unordered pair of groups (`group_a < group_b` alphabetically) with columns `group_a, group_b, crude_diff, n_strata_compared, n_strata_opposite, reversal`. `crude_diff` = crude rate of a − crude rate of b. A stratum is **compared** only if both groups have at least `min_n` rows in it. A compared stratum is **opposite** if its rate difference (a − b) is non-zero and has the opposite sign to `crude_diff`. `reversal` is `True` exactly when `crude_diff != 0`, at least **two** strata are compared, and **every** compared stratum is opposite. |
| **R5** | `direct_standardise(df, group_col, stratum_col, outcome="died_30d")` returns columns `<group_col>, crude_rate, standardised_rate`, one row per group sorted by group. The standard population is the **pooled** distribution of `stratum_col` across all rows. A group with no rows in some stratum gets `NaN`. |
| **R6** | `decompose_gap(df, a, b, group_col, stratum_col, outcome="died_30d")` returns `{"crude_gap", "composition_effect", "rate_effect"}` using the **Kitagawa (1955)** two-factor decomposition: composition = Σₛ (pₐₛ − p_bₛ)(rₐₛ + r_bₛ)/2 and rate = Σₛ (rₐₛ − r_bₛ)(pₐₛ + p_bₛ)/2, where p is the case-mix share and r the stratum rate. The two effects must sum to `crude_gap`. Raise `ValueError` if a stratum is missing from either group. |
| **R7** | `screen_stratifiers(df, group_col, candidates, outcome="died_30d", min_n=20)` returns one row per candidate with columns `candidate, max_shift, n_reversal_pairs`, where `max_shift` = the largest absolute difference between crude and standardised rate over all groups (using R5 with that candidate) and `n_reversal_pairs` = number of `reversal == True` rows from R4. Sort by `max_shift` descending, ties by `candidate` ascending. |
| **R8** | `build_findings(df, group_col="hospital", outcome="died_30d") -> dict` returns a JSON-serialisable dictionary with exactly these keys: `group_col`, `outcome`, `crude_rates` (group → rate), `standardised_rates` (group → rate, standardised on the primary confounder), `highest_crude`, `lowest_crude`, `highest_standardised`, `lowest_standardised`, `primary_confounder` (the first row of R7 run on `CANDIDATE_STRATIFIERS`), `stratifier_screen` (R7 as a list of records), `reversal_pairs` (sorted list of sorted `[a, b]` pairs with a reversal on the primary confounder), and `gap_decomposition` (`{"pair": [highest_crude, lowest_crude], ...R6 output}`). Nothing may be hard-coded. |
| **R9** | `python -m paradox_ward <admissions.csv> --out <dir>` writes `findings.json` (R8) and `stratified_rates.csv` (R2 by hospital and primary confounder). |
| **R10** | An exploration notebook or script (`exploration.ipynb` or `exploration.py`) that produces every number and figure used in your findings report, including at least: a crude rate table with intervals; a case-mix figure; a stratified rate figure **with interval bars**; the stratifier screen; and the decomposition for the pair the Ministry is worried about. |
| **R11** | `FINDINGS.md` (at most 1,200 words plus tables and figures), using the [template](submission-template/FINDINGS.md), written for the Commissioner. It must answer the question in §B and contain the **required quantified claims** listed in §G.7. |

### D.2 Engineering requirements (mandatory)

- **Determinism.** Running the CLI twice gives identical `findings.json`.
- **No mutation.** Functions must not modify the `DataFrame` they receive.
- **Tests.** Keep the provided tests passing and add **at least 8 tests of your own** in `tests/test_member_*.py`. At least three must use small hand-built tables where you can work out the right answer on paper, for example a stratum present in only one group, a tie in a stratum, or `min_n` excluding a stratum.
- **Dependencies.** Only those in [`starter/requirements.txt`](starter/requirements.txt).

### D.3 Privacy and responsibility

The data is entirely synthetic, but hospital outcome data is among the most sensitive health information there is, and league tables affect people's careers and patients' trust. Under the Nigeria Data Protection Act 2023, health data is **sensitive personal data**.

- Report only aggregates. Don't publish row-level extracts, even of synthetic data. Suppress or flag any cell with fewer than 10 events or 20 admissions in the report, and say that you did.
- In one paragraph of `FINDINGS.md`, explain how the analysis would change if the data were real: who may access row-level data, small-cell suppression, and why a hospital should see its figures before publication.

### D.4 Optional enhancements (not required for full marks)

- Indirect standardisation (standardised mortality ratios with intervals) and a comparison with your direct standardisation.
- A funnel plot of hospital rates against volume.
- A logistic regression with hospital and triage terms, compared with your standardised rates.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/admissions.csv`](resources/data/admissions.csv) (9,600 rows × 10 columns, about 630 KB, UTF-8) |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed. The hospitals are fictional and no patient is described. The generator is kept in the assessor kit because it would reveal the planted structure. |
| **Licence** | CC BY 4.0 (the same as this repository's content) |
| **Integrity** | SHA-256 `31021d475b5ee5e2198db17bbfe1c18682e4d9c1fbf4817c5a025c45ab7c0d50`. The contract test checks it, so don't edit the file. |

**Schema**

| Column | Type | Meaning |
|---|---|---|
| `admission_id` | text | Unique row identifier |
| `hospital` | text | One of four hospitals |
| `admission_month` | text `YYYY-MM` | Month of admission, 2024-01 to 2025-12 |
| `age_band` | text | `18-39`, `40-59`, `60+` |
| `sex` | text | `F` / `M` |
| `triage_category` | int | 1 (most severe) to 4 (least severe), at arrival |
| `referral_source` | text | `referred` from another facility, or `walk-in` |
| `procedure_group` | text | Five broad procedure groups |
| `los_days` | int | Length of stay in days |
| `died_30d` | int | 1 if the patient died within 30 days of admission |

**Known limitations (by design).** Triage category is a coarse, four-level summary of severity. There are no comorbidity scores, no vital signs and no surgeon identifiers. Your conclusions must respect that.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-04-exploratory-data-analysis/DS-T1-009-the-paradox-ward
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract      # passes immediately: checks data and scaffold
pytest                  # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `paradox_ward/` package (the completed starter) | The reusable, tested analysis logic |
| 2 | `tests/test_member_*.py` (≥ 8 tests) | Shows you can pin down definitions with cases you worked out by hand |
| 3 | `exploration.ipynb` **or** `exploration.py` | Reproduces every number and figure in the report |
| 4 | `outputs/findings.json`, `outputs/stratified_rates.csv` | Machine-readable findings, checked against the hidden truth |
| 5 | `FINDINGS.md` (≤ 1,200 words plus tables/figures) | The answer to the Commissioner, with quantified claims and limits |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 7 | A 5–10 minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. ⚙ = checked automatically by the public and hidden suites; ✍ = checked by the assessor.

1. ⚙ `pytest` passes all provided tests and all of your own tests in a clean environment built from `requirements.txt`.
2. ⚙ R1–R7 match an independent implementation **exactly** (to 1e-9) on the official data **and** on two re-generated datasets in which a different hospital is the referral centre. *Justification:* these are deterministic definitions with one correct answer, so there is no tolerance beyond floating-point error.
3. ⚙ On every hidden dataset, `build_findings` identifies the correct primary confounder, the hospital with the highest crude rate, the hospital with the lowest standardised rate, and exactly the set of reversal pairs defined by R4. *Justification:* hard-coding "Idu Teaching" or "triage_category" will fail on the re-generated data, which is the point.
4. ⚙ `decompose_gap` effects sum to the crude gap within 1e-12, and `findings.json` is regenerated by the CLI.
5. ✍ The exploration code regenerates every number in `FINDINGS.md`.
6. ✍ Every stratified figure shows interval bars, and every cell with fewer than 20 admissions or 10 events is flagged in the report.
7. ✍ `FINDINGS.md` contains these **required quantified claims**, each with its number and interval where applicable:
   1. the crude 30-day mortality of each hospital with a 95% Wilson interval;
   2. the case-mix share of triage 1–2 patients at each hospital;
   3. the standardised mortality of each hospital, and the resulting ranking;
   4. the decomposition of the gap between the highest and lowest crude hospital into composition and rate effects, in percentage points;
   5. at least one stratum comparison that the data **cannot** resolve, with the interval that shows why;
   6. evidence that at least two candidate stratifiers are *not* the explanation, and an explanation of why `referral_source` only partly corrects the picture.
8. ✍ The report gives the Commissioner a clear recommendation about the league table, and **at least two specific limitations** that stop the analysis proving one hospital's care is better (for example residual confounding within triage category, or triage applied by the receiving hospital).
9. ✍ No row-level data appears in the report.

---

## H. Evaluation Rubric

The full rubric, with performance levels, is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 15 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Exploratory methodology | 15 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible submission and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create a private GitHub repository** named `clbg-DS-T1-009-<your-github-username>`, and copy in this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` contents.
2. **Expected structure:**
   ```text
   clbg-DS-T1-009-<username>/
   ├── README.md                    # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── paradox_ward/                # your package (from starter/)
   ├── tests/                       # provided tests + your test_member_*.py
   ├── resources/                   # unchanged
   ├── exploration.ipynb | exploration.py
   ├── outputs/findings.json
   ├── outputs/stratified_rates.csv
   ├── figures/                     # PNGs referenced by FINDINGS.md
   ├── FINDINGS.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue in the CLBG assessments repository with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core.

1. **Build your own paradox.** Construct the smallest table (fewest rows) in which a reversal holds in all three strata of a three-level stratifier. Explain what constraints on the case mix make it possible.
2. **Indirect versus direct.** Compute standardised mortality ratios with Poisson or exact intervals. When do the two standardisations disagree on the ranking, and which should the Ministry publish?
3. **Funnel plot.** Plot each hospital's standardised rate against volume with 95% and 99.8% control limits, as used in UK and US hospital profiling, and explain why a funnel plot is safer than a ranked list.
4. **Sensitivity to residual confounding.** Suppose triage-1 patients at the referral centre are, on average, 20% more likely to die than triage-1 patients elsewhere, for reasons not in the data. Does the conclusion survive?

---

## K. Assessment Integrity

**AI tools are permitted** for learning: explaining the Wilson interval, suggesting pandas idioms, or reviewing your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`: the tool, what you used it for, and an example prompt. Disclosed, reasonable use is not penalised. Undisclosed use that becomes apparent at defence is an integrity breach.
- **Cite** any adapted code or formula source, with a link.
- **Collaboration:** you may discuss general ideas (for example "what is Simpson's paradox?") with other members. You may not share code, numbers, figures or report text.
- **How your understanding is verified.** In the defence (5–10 minutes), the assessor will:
  1. point at one cell of your stratified table and ask you to recompute its interval by hand from n and events;
  2. ask you to explain, without notes, how a hospital can be worse overall and better in every stratum;
  3. give you an **unseen modification** to make live, for example: change `find_reversals` so that ties count as non-opposite and add a test; or re-run the screen with `procedure_group` as a candidate and interpret the result;
  4. ask what single extra variable you would ask the Ministry to collect, and why.

  Your commit history and exploration code are reviewed for consistency with your report. See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Proportions, `groupby`/`crosstab`, the idea of a confidence interval, basic plotting. |
| **New skill developed** | Treating an aggregate comparison as a hypothesis to be stress-tested by stratification, standardisation and decomposition, rather than as a finding. |
| **Decisions the member must make** | Which stratifiers to examine, which cells are too small to interpret, which pair of hospitals to decompose, how to present an ambiguous stratum, and what to recommend about the league table. |
| **What must be investigated independently** | Whether the paradox exists at all, on which variable, for which pairs, and why the referral variable only partly explains it. Nobody tells the member which column matters. |
| **Why it's interesting** | The headline story ("Idu kills twice as many") is the opposite of the story the data supports. There is a real decision with real consequences attached. |
| **Evidence of competence** | Exact agreement with an independent oracle on re-generated data, a decomposition that adds up, interval-aware reading of small cells, and a defence in which the member explains the paradox without notes. |
| **Misconceptions exposed** | "Bigger crude rate means worse care." "Stratifying on anything is controlling for confounding." "A difference in a stratum of 70 patients is a finding." "Standardisation proves causation." |
| **Preparation for later work** | It leads into DS-08 (causal thinking, adjustment sets), DS-06 (honest uncertainty visualisation) and the DS-04 Tier 3 work on confirmatory versus exploratory findings. |

**Suggested approach** (optional):

1. Before writing code, compute the crude table and look at the case mix by hand. Form a hypothesis.
2. Implement R1–R3 with tests on the kidney-stone example in the public tests, then R4–R7.
3. Only then write the report, starting from the Commissioner's question rather than from your tables.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
