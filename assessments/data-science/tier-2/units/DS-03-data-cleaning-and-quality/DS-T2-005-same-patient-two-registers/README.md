# DS-T2-005: Same Patient, Two Registers

> *A primary health centre and a general hospital each keep a register. Neither shares an ID with the other. Link them well enough to follow patients across the referral pathway, without merging twins, mothers and daughters, or two Muhammad Bellos.*

![Format: Comparative](https://img.shields.io/badge/format-comparative-d93f0b) ![Tier 2](https://img.shields.io/badge/tier-2-fbca04) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-005` |
| **Title** | Same Patient, Two Registers: Probabilistic vs Deterministic Record Linkage |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Engineering and Independent Problem-Solving |
| **Unit** | [DS-03: Data Cleaning and Data Quality](../README.md) |
| **Format** | Comparative (secondary: Implementation) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 3 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 20–35 hours over 2–3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Solid pandas (merges, groupby); probability (conditional probability, likelihood ratios, logarithms); string similarity at a conceptual level; evaluation with precision and recall. [DS-T1-006](../../../../tier-1/units/DS-03-data-cleaning-and-quality/DS-T1-006-the-registry-that-lies/README.md) is good preparation. |
| **Skills developed** | Standardisation for linkage; blocking and its recall/cost trade-off; comparison vectors with graded agreement; the Fellegi–Sunter model (m- and u-probabilities, match weights); parameter estimation by EM or from a clerical sample; threshold choice and clerical-review bands; one-to-one assignment; linkage error analysis |
| **Technologies** | Python 3.10+, pandas, NumPy, pytest. Optional: `rapidfuzz`, `jellyfish`, `recordlinkage` or `splink` (declare them, and explain what they do for you) |

---

## B. Problem Statement

A state primary health care board in Kaduna wants to know what happens to patients after a primary health centre (PHC) refers them to the general hospital (GH). Do referred pregnant women actually arrive? How long does it take? Which children are seen in both places? Answering these questions needs the two registers to be **linked**: for each person, which PHC record and which GH record describe them.

There is no shared identifier. NIN coverage in these registers is too patchy to rely on, so the board has asked for linkage on what the registers *do* share: names, sex, date of birth, phone number and location. That is where it gets hard.

- **The registers disagree on format.** The PHC splits names into fields and writes dates as DD/MM/YYYY. The GH stores a single `full_name` (sometimes `SURNAME, Given`, sometimes `Given Other Surname`) and writes ISO dates with international phone numbers.
- **Names vary legitimately.** Muhammad, Mohammed and Muhammadu; Oluwaseun and Seun; Aisha and Aishatu. Typing errors are added on top.
- **Dates of birth are often estimated.** Many adults don't know their exact birth date. One register writes estimated dates as `01/01/YYYY`, and the other uses a different convention you need to discover. Agreeing on an estimated date means much less than agreeing on a real one.
- **Households share identifiers.** Children are registered with the household phone, and siblings share a surname, a settlement and sometimes a birthday (twins). A married woman may appear under her husband's surname in one register and her own family name in the other.

A false link attaches one person's hospital record to another person: a child's immunisation history to her twin, or a mother's antenatal record to her daughter. A missed link makes a referral look as though it never arrived. The board accepts that some pairs will go to a **clerical review** queue, but its records officers can review only a limited number.

Your job is to build a **deterministic baseline**, build a **probabilistic linker** (the Fellegi–Sunter model or a justified alternative), compare them fairly, and recommend an operating point.

**Known facts and resources:**

- A records officer has clerically reviewed **250 randomly chosen PHC records** and recorded each one's true GH match, or that it has none ([`clerical_sample.csv`](resources/data/clerical_sample.csv)). This is the only ground truth you get. Its truth is complete for those 250 records, so precision and recall restricted to them are unbiased estimates for the whole register. The provided `evaluate_links` computes them.
- [`name_variants.csv`](resources/reference/name_variants.csv) is a list of name variants compiled by records staff. It is useful, and it is not perfect: some entries join names that are also distinct names in their own right.
- Both registers describe the same catchment of five LGAs over overlapping periods. Roughly half of PHC patients also appear at the GH, but nobody knows the exact number.

---

## C. Objectives

You should be able to show that you can:

1. **Standardise** two registers with different conventions into one comparable form, including detecting placeholder (estimated) dates.
2. **Design blocking** that keeps nearly all true matches while cutting comparisons by more than 99%, and measure both properties.
3. **Build a deterministic baseline** that a sensible analyst would actually use, not a straw man.
4. **Implement Fellegi–Sunter linkage**: comparison vectors with graded agreement levels, m- and u-probabilities, match weights, a threshold and one-to-one assignment.
5. **Compare** the two approaches fairly on the precision–recall trade-off, with uncertainty, using only the clerical sample.
6. **Analyse errors**: which kinds of pairs each method gets wrong, and why.
7. **Recommend** an operating point (match threshold and review band) with its expected precision, recall and clerical workload.

---

## D. Technical Requirements

### D.1 Mandatory requirements

The interface below is fixed because the tests import it ([`starter/linkage/__init__.py`](starter/linkage/__init__.py)). **Everything behind it is your design.**

| ID | Requirement |
|---|---|
| **R1** | **Standardisation.** Bring both registers to a common schema (names split and normalised, dates parsed, estimated-date placeholders detected, phones canonicalised, locations comparable). Document every rule and the profiling evidence behind it. |
| **R2** | **Blocking.** `candidate_pairs(a, b) -> DataFrame[a_id, b_id]`. Report its **pair completeness** (the share of clerical-sample matches retained) and **reduction ratio** (1 − candidates / (\|A\| × \|B\|)), and justify each blocking key. |
| **R3** | **Deterministic baseline.** `deterministic_link(a, b) -> DataFrame[a_id, b_id]`, one-to-one. It must be a rule a competent analyst would deploy (for example exact standardised name and DOB, or phone plus first name), with its precision at least 0.9. |
| **R4** | **Probabilistic linker.** `link(a, b, clerical) -> DataFrame[a_id, b_id, score, decision]` with `decision ∈ {match, review}` and one-to-one `match` pairs. Use the Fellegi–Sunter framework or a justified alternative. At least three fields must have **more than two** agreement levels (for example exact / close / far / missing). |
| **R5** | **Parameter estimation.** Estimate the model's parameters in at least **two** ways and compare them. For example: unsupervised EM, versus m-probabilities from the clerical sample with u-probabilities from random pairs. Report what each gives and which you trust. `link` must take its parameters from the registers it is given (the `clerical` argument is the sample *for those registers*), not from constants tuned on the public files. |
| **R6** | **Comparison and operating point.** Plot precision against recall for both methods, estimated on the clerical sample, with confidence intervals (bootstrap the 250 records). Recommend a match threshold and a review band, and state the expected precision, recall and number of pairs sent to review. |
| **R7** | **Error analysis.** Classify the false matches and missed matches of your recommended configuration (twins and siblings, household phone, maiden name, estimated DOB, name variants, typos, other), and connect each class to a specific modelling choice. |

### D.2 Engineering requirements

- `link` runs end to end on the public registers in under **5 minutes** on a laptop.
- Modular code: standardisation, blocking, comparison, estimation and decision are separately testable.
- **At least 12 tests of your own**: each standardiser, each comparison level, the one-to-one step, and at least one known-hard pair type.
- Every number in the report is regenerated by a script or notebook (`analysis.py` or `analysis.ipynb`).
- Bounded dependencies in `requirements.txt`. If you use a linkage library, you must still be able to explain its m/u estimation and implement one comparison function yourself at defence.

### D.3 Privacy, ethics and safeguards

The registers are **synthetic**, and every name is a random combination of common names. Health registers are still special-category personal data under the Nigeria Data Protection Act 2023, and real linkage projects need a lawful basis, a data-sharing agreement and minimisation. In your report (one short section):

- Explain why linkage should happen in a controlled environment, and why the linked output should carry only what the analysis needs (for example a link key and referral dates, not full names).
- Say who should see the **review queue**, and what a reviewer needs to see to decide a pair while seeing as little as possible.
- Describe the harm of a false match in this setting, and how your operating point reflects it.

Never paste register rows into public AI tools or forums.

### D.4 Optional enhancements

- **Term-frequency adjustment:** agreement on a rare surname is stronger evidence than agreement on "Bello". Implement it and measure the gain.
- A household-aware constraint or feature that reduces twin and sibling confusions.
- A second probabilistic method (for example logistic regression on comparison vectors, trained on the clerical sample with cross-validation) compared against Fellegi–Sunter.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | [`phc_register.csv`](resources/data/phc_register.csv) (4,025 rows) · [`gh_register.csv`](resources/data/gh_register.csv) (3,422 rows) · [`clerical_sample.csv`](resources/data/clerical_sample.csv) (250 rows). About 0.6 MB in total. |
| **Provenance** | **Synthetic**, generated by CLBG from a fictional population of households in five Kaduna State LGAs, with a fixed seed. Names are random combinations from lists of common names, and phones are random numbers with Nigerian prefixes. No real person is described. The generator and full truth are kept in the assessor kit. |
| **Licence** | CC BY 4.0 (same as this repository's content) |
| **Integrity** | SHA-256 in `tests/test_contract.py`; don't modify the files. |
| **Reference list** | [`name_variants.csv`](resources/reference/name_variants.csv) (canonical, variant) |

**Schemas** (all text):

| PHC column | Notes | GH column | Notes |
|---|---|---|---|
| `phc_id` | unique | `gh_id` | unique |
| `surname`, `first_name`, `other_name` | split; case varies | `full_name` | two layouts |
| `sex` | `F`/`Female`/`M`/`Male` | `sex` | `F`/`M` |
| `dob` | DD/MM/YYYY or empty | `date_of_birth` | ISO or empty |
| `age_years` | sometimes filled | | |
| `phone` | local format or empty | `phone` | several formats or empty |
| `lga`, `settlement` | | `lga`, `address` | spelling varies; settlement is inside the address |

**Known limitations.** 250 labelled records give confidence intervals of a few percentage points, so report them. The simulated error rates are plausible but not measured from a real register. There is no NIN, and that is deliberate.

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-03-data-cleaning-and-quality/DS-T2-005-same-patient-two-registers
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract
pytest
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `linkage/` package | The standardisation, blocking, baseline and probabilistic linker |
| 2 | `tests/test_member_*.py` (≥ 12) | Evidence that each component behaves as designed |
| 3 | `analysis.py` or `analysis.ipynb` | Regenerates every table and figure: blocking metrics, PR curves with CIs, parameter comparison, error analysis |
| 4 | `outputs/links.csv` | Your recommended `link` output on the public registers |
| 5 | `LINKAGE_REPORT.md` (≤ 2,500 words plus figures), from the [template](submission-template/LINKAGE_REPORT.md) | The comparison, the recommendation and the safeguards, for the board's data manager |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 7 | 15-minute defence | Justify and debug (see §K) |

---

## G. Acceptance Criteria

⚙ = automated (public tests and hidden suite on **two newly generated populations** scored against complete truth); ✍ = assessor judgement.

1. ⚙ Provided and member tests pass in a clean environment.
2. ⚙ **Blocking:** pair completeness **≥ 0.95** and reduction ratio **≥ 0.99**. *Justification:* matches lost at blocking can never be recovered, so blocking must keep almost all of them. The reference keeps 98% with a 99.87% reduction. 0.99 is the level at which comparison cost on registers this size stays in the tens of thousands of pairs.
3. ⚙ **Baseline is real:** the deterministic rule has precision **≥ 0.90** and recall **≥ 0.40** on hidden truth. *Justification:* a comparison against a straw man proves nothing. Exact name-and-DOB rules typically reach precision above 0.98 and recall around 0.70 on these registers.
4. ⚙ **Linker quality:** `match` pairs have precision **≥ 0.93** and recall **≥ 0.85** on hidden truth. *Justification:* the board's tolerance for false links is low because they corrupt clinical histories. 0.93 means fewer than 1 in 14 links is wrong, before clerical review. The reference achieves 0.96–0.98 precision with 0.96–0.98 recall, so both bars leave room for different defensible designs.
5. ⚙ **Beats the baseline:** linker F1 is at least **0.05** above the member's own baseline F1 on hidden truth. *Justification:* graded agreement and weights should recover the many matches that exact rules miss (name variants, estimated DOBs, changed phones). The reference gains about 0.14.
6. ⚙ `link` is one-to-one on matches and finishes in under 5 minutes.
7. ✍ R5: two estimation approaches are compared and the choice is justified with evidence. A member who finds that unsupervised EM behaves badly on these registers, and explains why, meets this fully.
8. ✍ R6: PR curves with bootstrap intervals, and an operating point with expected review workload.
9. ✍ R7: an error analysis that connects error classes to modelling choices.
10. ✍ The privacy and safeguards section is specific to this linkage, not generic.

---

## H. Evaluation Rubric

Full rubric: **[rubric.md](rubric.md)**.

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Methodology and experimentation (blocking, estimation, comparison) | 20 |
| Testing and evaluation design | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking, error analysis and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

---

## I. Submission Instructions

1. A private repository named `clbg-DS-T2-005-<your-github-username>`, built from this assessment's `starter/`, `tests/`, `resources/` and `submission-template/`.
2. Expected structure:
   ```text
   clbg-DS-T2-005-<username>/
   ├── README.md              # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── linkage/
   ├── tests/
   ├── resources/             # unchanged
   ├── analysis.py | analysis.ipynb
   ├── outputs/links.csv
   ├── LINKAGE_REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. Commit as you work. Exploratory dead ends belong in the history, and in the report if they taught you something.
4. Submit through the **Assessment submission** issue template with the repository URL and commit SHA, and add the assessor account as a read-only collaborator.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Term-frequency weights.** Make agreement on a rare surname count for more than agreement on a common one, and measure the effect on precision.
2. **Twin safety.** Design a rule or feature that prevents twin confusions without losing recall, and quantify both.
3. **Supervised alternative.** Train a classifier on comparison vectors from the clerical sample with cross-validation, and compare it with Fellegi–Sunter at the same precision.
4. **Linkage bias.** Is linkage recall lower for some groups (married women, people with estimated DOBs, particular LGAs)? Why does that matter for the referral analysis the board wants to run?

---

## K. Assessment Integrity

**AI tools are permitted** for learning, debugging and explanation, for example of the Fellegi–Sunter model, Jaro–Winkler similarity or EM. **They are not permitted to design and write the linker for you.** Disclose every use in `AI_USE_AND_SOURCES.md`.

- **Cite** the sources you used for the method (textbooks, papers, library documentation).
- **Collaboration:** you may discuss general techniques. You may not share code, thresholds, parameters, results or report text.
- **How understanding is verified (15 minutes):**
  1. The assessor picks one `match` and one `review` pair from your output, and you compute the match weight by hand from your m and u tables.
  2. You explain what an m-probability and a u-probability are, and why agreement on an estimated DOB carries less weight than agreement on a real one.
  3. **Unseen modification:** add a new agreement level or field live (for example a "first name agrees with the other register's other name" level, or settlement in the blocking keys), and predict its effect on precision and recall before running it.
  4. Defend your operating point: "The board can review only 50 pairs a month. What do you change?"

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | pandas, conditional probability and likelihood ratios, precision and recall, basic string similarity. |
| **New skill developed** | Probabilistic record linkage as a *measurement* problem: estimating how much each piece of evidence is worth, choosing where to draw lines, and knowing what the result can be trusted for. |
| **Decisions the member must make** | Standardisation rules; blocking keys; comparison levels; how to estimate m and u; threshold and review band; how to evaluate with only 250 labelled records. |
| **What must be investigated independently** | The two registers' conventions (including the estimated-date placeholder); which identifiers households share; why unsupervised EM can lock onto households instead of people; the classes of error. |
| **Why it's interesting** | The exact-match baseline looks excellent on precision and quietly misses almost 30% of people. The probabilistic linker recovers them, but only if the member understands why a shared phone or a shared 01/01 birthday is weak evidence. The tension between false links (clinical harm) and missed links (lost referrals) is real and has to be priced. |
| **Evidence of competence** | Hidden-truth precision, recall and blocking completeness on unseen populations; a fair comparison with confidence intervals; a hand-computed match weight at defence. |
| **Misconceptions exposed** | "Same name and phone means same person." "EM always finds the matches." "Precision on the pairs I looked at is the precision." "A higher threshold is always safer." "The baseline is there to lose." |
| **Preparation for later work** | It leads into DS-T3 work on how cleaning and linkage choices change downstream conclusions, into entity resolution at scale (Splink, distributed blocking), and into any health-information-system integration project. |

**Suggested approach** (optional): profile both registers for a day before writing linkage code. Build standardisation with tests, then measure blocking on the clerical sample, then the baseline. Build Fellegi–Sunter with simple levels first, check its weights for sense (agreement positive, disagreement negative, rarer agreement stronger), and only then refine.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
