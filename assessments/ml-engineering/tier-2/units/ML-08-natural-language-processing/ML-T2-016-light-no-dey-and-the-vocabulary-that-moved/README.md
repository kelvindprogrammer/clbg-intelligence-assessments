# ML-T2-016: Light No Dey: Complaint Triage When the Vocabulary Moves

> *An electricity distribution company routes WhatsApp complaints in English and Pidgin. Validation says 100 percent; after a tariff reform the words change. Build a router that survives, with a review desk for the rest.*

![Format: Comparative (secondary: System Design)](https://img.shields.io/badge/format-comparative-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-016` |
| **Title** | Light No Dey: Complaint Triage When the Vocabulary Moves |
| **Subtrack** | ML Engineering |
| **Tier** | 2: Applied Engineering and Independent Problem-Solving |
| **Unit** | [ML-08: Natural Language Processing](../README.md) |
| **Format** | Comparative (secondary: System Design) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14–20 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | TF-IDF and logistic regression in scikit-learn; macro-F1; the idea of dataset drift. Recommended: ML-T1-017 |
| **Skills developed** | Evaluating text models under vocabulary drift; building a stress validation; character versus word features; typo augmentation; confidence-based deferral to a human desk with a review budget; per-class error analysis on imbalanced classes |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Harmattan Power Distribution (a fictional company) receives complaints by WhatsApp and SMS in English and Nigerian Pidgin: `light don go for Hilltop since yesterday`, `my prepaid meter no dey accept token`, `why una increase tariff of light`. A router must send each to one of five desks: **billing**, **outage**, **meter**, **transformer** or **tariff**. Traffic is imbalanced (outage is about 38 percent, tariff about 7 percent). A small human desk can read at most **15 percent** of messages, so the router must also decide which messages to send there.

You have 1,500 labelled messages from before a tariff reform and a validation set of 300 more from the same period. The company will deploy the router *after* the reform, when new vocabulary appears (`band A`, `smart meter`, `ussd`, `vendor`, `blackout`), customers type faster and mistype more (the generator raises the typo rate from 3 to 12 percent), and only a fifth of messages still use the old phrasings. You get no labelled data from the new period.

The previous contractor trained a word-level TF-IDF logistic regression. It scores 1.00 on the validation set and about 0.73 macro-F1 after the reform. Three problems are built in:

1. **A saturated validation set.** Every sensible candidate scores near 1.00 on it, so it cannot choose between them. You must build a validation that exposes the shift without access to future labels.
2. **Vocabulary and spelling drift.** Some new words cannot be learned from old data; others are old roots with new spellings or inflections.
3. **A review budget.** Deferring the least confident 15 percent only helps if confidence is informative; you must check that, not assume it.

The task is partially specified: the tests fix interfaces and bars; representation, classifier, augmentation, the stress validation and the way you pick a model are yours to choose and defend. The templates are synthetic teaching material; a Pidgin speaker should review them before any real use.

> **Why this matters beyond this task.** Production text systems are deployed into a future that training data do not contain. Noticing that a perfect validation score is a warning rather than a result, and building evidence anyway, is the central applied-NLP skill.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Recognise** a saturated validation set and build a stress validation that exposes drift without future labels.
2. **Compare** word, character and augmented representations under vocabulary and spelling drift against a baseline.
3. **Simulate** misspellings with a controlled corruption function and measure its effect.
4. **Route** messages with a review budget and verify that confidence identifies errors.
5. **Report** per-class behaviour and what drift you could not defend against.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `discotriage` in [`starter/discotriage/`](starter/discotriage/). Interfaces are fixed; modelling choices are yours. Use only numpy and scikit-learn.

| ID | Requirement |
|---|---|
| **R1** | `typo_corrupt(texts, rng, p)` returns a new list of strings. Each letter independently suffers, with total probability `p`, a drop, a swap with the next character or a doubling; non-letters are never changed or moved; no characters are invented; the input list is not mutated; the result is deterministic given the generator; `p=0` returns the texts unchanged. |
| **R2** | `macro_f1(y_true, y_pred, labels)`: the unweighted mean of per-class F1 over `labels`; a class with no support and no predictions scores 0. |
| **R3** | `route_with_budget(proba, classes, budget_frac)` returns, for each row, the most probable class, except that the `ceil(budget_frac * n)` least confident rows (lowest maximum probability; ties go to the earlier row) receive `"REVIEW"`. |
| **R4** | `build_triage(X_train, y_train, X_val, y_val, seed=0)` returns a model with `predict`, `predict_proba`, `classes_` (sorted), `chosen_` and `report_`: at least three candidates, one `"word_tfidf_logreg"`, mapping to macro-F1 on **your own stress validation** (not the plain validation set). |

### D.2 Engineering requirements (mandatory)

- Deterministic: explicit seeds and generators everywhere.
- No fitting, tuning or selection with post-reform data; the test period is for final reporting only.
- At least **10 tests of your own** in `tests/test_member_*.py`, including a non-mutation test for `typo_corrupt` and a per-message independence test for the model.
- `experiments.py` regenerates every number and figure: the saturation evidence (validation versus post-reform scores for each candidate), a comparison over **at least 5 seeds**, per-class F1 before and after the reform, and the review-budget curve for budgets 5, 10, 15, 20 and 30 percent.

### D.3 Responsibility

The data are synthetic. Write one paragraph on what a misrouted complaint costs a customer (a transformer fault reported to the billing desk may wait days), why you would never fully automate the transformer and outage classes, and how you would check that Pidgin-heavy messages are not routed worse than English ones. Also say how you would handle real customer messages under the Nigeria Data Protection Act 2023.

### D.4 Optional enhancements

- A drift monitor that flags the new period from unlabelled messages alone (for example the share of out-of-vocabulary tokens).
- A labelling plan: which 200 post-reform messages would you label first, and why?
- Cost-sensitive routing where a missed transformer fault costs ten times a billing error.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_complaints(n=1500, seed=0, period='early' | 'late')` returns `texts` and `labels` (`billing`, `outage`, `meter`, `transformer`, `tariff`) |
| **Provenance** | **Synthetic** templates in English and Pidgin with typos; the late period adds new vocabulary and heavier noise; no real customer or company |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Public protocol** | Train on 1,500 early messages (seed 1), validate on 300 early (seed 2), test on 1,000 late (seed 3) |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes two TSVs of about 100 KB each |

Hidden tests use other seeds, an 800-message training set and a clean early-period test.

**Setup**

```bash
cd assessments/ml-engineering/tier-2/units/ML-08-natural-language-processing/ML-T2-016-light-no-dey-and-the-vocabulary-that-moved
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `discotriage/` package | Corruption, metric, routing and model selection |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Includes non-mutation and per-message independence |
| 3 | `experiments.py` | Reproduces all tables and figures (5 or more seeds) |
| 4 | `REPORT.md` (at most 1,700 words plus tables), from the [template](submission-template/REPORT.md) | Decision memo for the contact-centre head; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `typo_corrupt` is deterministic, non-mutating, identity at `p=0`, invents no characters, never changes non-letters and changes a majority of messages at `p=0.2`; `macro_f1` and `route_with_budget` match hand-computed values, including ties and the ceiling rule.
3. ⚙ `report_` has at least three candidates including `word_tfidf_logreg`, `chosen_` is a key and `classes_` is sorted.
4. ⚙ **Performance.** On the public post-reform test set (1,000 messages) macro-F1 is at least **0.80** and at least **1.1 times** that of a word-level TF-IDF logistic regression trained on the early data. *Justification:* the reference reaches about 0.85 against 0.73; the bar leaves room for a different but reasonable representation.
5. ⚙ **Review desk.** At a 15 percent budget the automated 85 percent of messages have error at most **0.09**, and the reviewed 15 percent contain at least **40 percent** of all the model's errors. *Justification:* the reference gives about 0.067 and 0.48; the second bar is the evidence that confidence is informative (random review would capture 15 percent).
6. ⚙ **Robustness.** On hidden seeds with an 800-message training set the macro-F1 bar is 0.78 and 1.08 times the baseline, and on a clean early-period test macro-F1 stays at least 0.95.
7. ⚙ Predictions for a message do not depend on the other messages in the batch.
8. ✍ The report shows the saturation of the plain validation set, how your stress validation compares with the actual post-reform scores, and what drift remains undetected.
9. ✍ The report gives per-class behaviour (especially the 7 percent tariff class) and the review-budget curve.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 15 |
| Methodology and evidence | 15 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T2-016-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `discotriage/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `experiments.py`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Out-of-vocabulary monitor.** Flag the reform from unlabelled messages and plot the signal against time.
2. **Calibration.** Calibrate probabilities and test whether calibration improves the review desk.
3. **Active labelling.** Choose 200 post-reform messages to label using uncertainty and measure the gain.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why the baseline scores 1.00 on validation and 0.73 afterwards and what in your report shows you saw it coming; (2) ask how you know that low confidence marks errors; (3) give an unseen change, for example a 30 percent review budget or a new complaint class, and ask what changes in your choices.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | TF-IDF and logistic regression; macro-F1; probability outputs. No sequence-model theory. |
| **New skill developed** | Building evidence about the future when validation is blind to it, and routing under a human review budget. |
| **Decisions the member must make** | Stress validation design; representation; augmentation strength; model; how to verify confidence is informative. |
| **What must be investigated independently** | Which parts of the post-reform drop are spelling (recoverable) and which are vocabulary (not). |
| **Why it is interesting** | Every candidate scores 100 percent on validation, so the member has to create a better test before they can choose. |
| **Evidence of competence** | Post-reform F1 above the bar on re-seeded data, a routing curve showing informative confidence, and a stress validation that tracks the real drop. |
| **Misconceptions exposed** | 'Perfect validation means a good model.' 'Word features are enough.' 'Confidence thresholds always catch errors.' |
| **Preparation for later work** | Leads into ML-08 Tier 3 shortcut auditing, ML-10 drift monitoring and AI-07 human-in-the-loop design. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
