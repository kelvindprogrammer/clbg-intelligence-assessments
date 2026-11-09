# ML-T3-015: The Scam Detector That Learned to Shout: Auditing and Hardening an SMS Filter Against Style Shortcuts

> *A scam filter looks perfect in testing, then blocks genuine bank alerts in the pilot. Find the shortcut it learned, measure who pays for it, and defend a fix.*

![Format: Debugging & Forensics (secondary: Open-ended)](https://img.shields.io/badge/format-debugging-forensics-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-015` |
| **Title** | The Scam Detector That Learned to Shout: Auditing and Hardening an SMS Filter Against Style Shortcuts |
| **Subtrack** | ML Engineering |
| **Tier** | 3: Advanced and Research-Grade |
| **Unit** | [ML-08: Natural Language Processing](../README.md) |
| **Format** | Debugging & Forensics (secondary: Open-ended) |
| **Difficulty** | Technical 4 · Mathematical 2 · Research 4 · Engineering 3 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 24–32 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 2 minutes |
| **Recommended prerequisites** | TF-IDF and logistic regression; ROC and operating thresholds; bootstrap intervals; subgroup evaluation. Recommended: ML-T2-016 and ML-05 Tier 2 |
| **Skills developed** | Shortcut learning and counterfactual testing; operating-point selection at a fixed false-positive rate; subgroup metrics with intervals; stress validation under distribution shift; mitigation trade-offs (normalisation, augmentation, reweighting); writing a validity argument |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Sahel Pay (a fictional payments company) filters SMS for scams. Its data scientists trained a TF-IDF logistic regression on 300 labelled messages, chose an operating threshold that gives a 2 percent false-positive rate on a dev set and shipped a pilot. In the pilot, **genuine bank alerts were blocked at over ten times the expected rate** and some scams got through. The dev metrics looked perfect.

Messages are English, Nigerian Pidgin or Yoruba-style (about 60, 25 and 15 percent of the training data). Scams ask for an OTP, a BVN, a PIN or a fee; genuine messages are alerts, OTP deliveries, parcel notices and chat. Tricky cases on both sides use the same words (genuine messages warn against sharing your OTP; scams quote a debit alert first). Something else is going on: in the training data, 95 percent of scams are written in capitals with an `URGENT` lead-in and exclamation marks, against 3 percent of genuine messages. In the pilot period, scammers have calmed down (5 percent) and genuine senders have started shouting (60 percent): reminder texts and promotions now use the same style.

This is a forensic and research task, not a recipe. You must:

1. **Reproduce the failure** and show that dev-set numbers cannot see it.
2. **Find the shortcut from data**, with a method that would work without reading the generator (for example top coefficients, ablation and counterfactual flips).
3. **Measure the damage** per language group (recall, false-positive rate, intervals), because small groups carry large uncertainty.
4. **Harden the detector**, compare at least three mitigations with ablations and say what each gives up. Dropping the style channel is a defensible choice here but not a free one: real scammers do sometimes shout.
5. **Defend the operating point and the claims**, including what you could not test.

The tests fix interfaces and minimum bars; the investigation, the mitigations and the argument are yours. The language templates are approximate teaching material, not a language resource.

> **Why this matters beyond this task.** Shortcut learning is the most common reason a model that tests well fails in the field, and the people harmed are usually the ones the test set under-represented. Auditing is a skill separate from building.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Reproduce** a deployment failure and show why standard dev metrics hide it.
2. **Discover** a spurious cue from data using counterfactual perturbation and model inspection.
3. **Measure** subgroup harm with intervals and counts, and choose an operating threshold for a false-positive budget.
4. **Compare** mitigations with ablations on a stress validation you construct, stating the trade-offs.
5. **Argue** validity: what the evidence supports, what it does not, and who bears the residual risk.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `scamguard` in [`starter/scamguard/`](starter/scamguard/). Interfaces are fixed. Use only numpy and scikit-learn. Messages are scored as `P(scam)`; 'flagged' means score at least the threshold.

| ID | Requirement |
|---|---|
| **R1** | `subgroup_report(y_true, y_pred, groups)` returns, for every group present, a dict with `n`, `recall`, `fpr` and `precision` (`nan` where a rate has no denominator; precision is 0.0 when nothing is flagged). |
| **R2** | `bootstrap_ci(outcomes, n_boot=1000, seed=0, alpha=0.05) -> (mean, lo, hi)`: percentile bootstrap interval for the mean of a numeric array, deterministic given `seed`; a constant array gives a degenerate interval. |
| **R3** | `flip_rate(predict, texts, transform)`: the share of texts whose predicted label (from the callable `predict`, which returns an array) differs between `texts` and `transform(texts)`. |
| **R4** | `operating_threshold(scores, y, target_fpr)`: the **smallest** value `t` among the scores such that the false-positive rate of `score >= t` is at most `target_fpr`; `inf` if none exists. |
| **R5** | `fit_detector(texts, y, groups, seed=0)` returns a model with `score(texts) -> P(scam)` array, `chosen_` and `report_`: at least three candidates (one containing `"baseline"` in its name) mapping to your own **stress-validation** worst-group recall at a 2 percent false-positive rate. |

### D.2 Engineering requirements (mandatory)

- Deterministic: explicit seeds everywhere. Model scores depend on a message only, not on its batch.
- No threshold or model choice may use the shifted test regime. The operating threshold is set on training-regime dev data only.
- At least **10 tests of your own** in `tests/test_member_*.py`, including a counterfactual-flip test for your final model and a test that your stress validation separates the baseline from your hardened model.
- `experiments.py` regenerates every number and figure: dev versus shifted-regime metrics for the baseline; the shortcut discovery evidence; subgroup tables with intervals; a comparison of at least three mitigations with ablations over **at least 5 seeds**; and a sensitivity analysis of the operating point.
- `REPORT.md` (at most 2,500 words plus tables) as an audit report with a separate validity and harm section.

### D.3 Responsibility

The data are synthetic and the languages are approximate. Write one paragraph on who bears false positives (a blocked genuine bank alert or OTP can lock someone out of money at a critical moment) and false negatives (a scam victim), why the three language groups may be affected differently, why a fix that deletes capital letters may remove genuine signal elsewhere, and what you would do before deploying a filter that touches real customers' messages (Nigeria Data Protection Act 2023: purpose, minimisation, human review of disputed blocks).

### D.4 Optional enhancements

- Counterfactual data augmentation: add each training message in both styles and compare with normalisation.
- A group-aware training scheme (reweighting or group distributionally robust optimisation) and its effect on worst-group recall.
- A deployment monitor that detects the style-label correlation changing, from unlabelled traffic.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_sms(n=1500, seed=0, regime='train' | 'shift')` returns `texts`, `y` (1 scam) and `groups` (`en`, `pcm`, `yo`); `add_style` and `strip_style` perturb style |
| **Provenance** | **Synthetic** templates, including tricky overlap cases; no real message, bank or customer |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Public protocol** | Train on 300 messages (seed 1, train regime); dev 600 (seed 2, train regime) for the threshold; test 1,500 (seed 3, shift regime) |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes two TSVs of about 100 KB each |

Reading `datagen.py` reveals the cue, which is allowed, but the report must show how it could be found from the data alone. Hidden tests use other seeds, a 200-message training set and a cue-free regime.

**Setup**

```bash
cd assessments/ml-engineering/tier-3/units/ML-08-natural-language-processing/ML-T3-015-the-scam-detector-that-learned-to-shout
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `scamguard/` package | Subgroup metrics, intervals, flip rate, operating threshold and detector |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Includes the counterfactual-flip and stress-validation tests |
| 3 | `experiments.py` | Reproduces the audit tables, ablations and figures (5 or more seeds) |
| 4 | `REPORT.md` (at most 2,500 words plus tables), from the [template](submission-template/REPORT.md) | Audit report with a validity and harm section; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `subgroup_report`, `bootstrap_ci`, `flip_rate` and `operating_threshold` match hand-computed values, including groups with no positives, ties and an infeasible target.
3. ⚙ `report_` has at least three candidates including a baseline, and `score` returns probabilities in [0, 1] that do not depend on the batch.
4. ⚙ **Performance.** With the threshold set on training-regime dev data at a 2 percent false-positive rate, on the shifted test regime the false-positive rate is at most **0.06** and the worst-group recall is at least **0.90**. *Justification:* the reference gives about 0.02 and 0.98, while an unhardened character model on raw text gives a false-positive rate near 0.23; 0.06 allows a threefold degradation, and 0.90 allows for the small groups' variability (about 130 scam messages in the smallest).
5. ⚙ **Counterfactual stability.** At the same threshold, adding the urgent style to genuine messages flags at most **3 percent** of them, and removing it from scams unflags at most **3 percent**.
6. ⚙ **Robustness.** On hidden seeds with a 200-message training set the false-positive bar is 0.07 and the worst-group recall bar 0.88; with the cue removed from every message in the training regime, recall is at least 0.85 and the false-positive rate at most 0.10.
7. ✍ The report reproduces the failure, shows that the dev set cannot see it, and demonstrates discovery of the cue from data without the generator.
8. ✍ At least three mitigations are compared with ablations on a stress validation of your own design; trade-offs, including what is lost by ignoring style, are argued.
9. ✍ Subgroup results include counts and intervals; the validity section states what the synthetic study cannot show.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 15 |
| Implementation quality | 10 |
| Methodology and evidence | 25 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T3-015-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `scamguard/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `experiments.py`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Adaptive adversary.** Let scammers add a calm-style variant of each template and measure how quickly the hardened detector degrades.
2. **Second shortcut.** Add a different spurious cue (for example message length) and test whether your audit method finds it without being told.
3. **Appeals.** Design a human-review path for blocked genuine messages and estimate its workload at your operating point.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why the dev-set false-positive rate is 2 percent for every candidate and what it says about your validation; (2) ask what evidence in your report shows the cue is found from data, not from the generator; (3) give an unseen change, for example scammers writing in capitals again or a fourth language group, and ask which of your numbers change first.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | TF-IDF and logistic regression, ROC thresholds, bootstrap, subgroup metrics. No deep-learning theory. |
| **New skill developed** | Auditing a model for shortcuts with counterfactual tests, and arguing validity and harm. |
| **Decisions the member must make** | How to find the cue, what stress validation to build, which mitigations to compare, how to set and defend the operating point. |
| **What must be investigated independently** | Why dev metrics hide the shortcut and what each mitigation costs. |
| **Why it is interesting** | The most accurate model on the dev set is the worst one in the pilot, and the fix removes information that is real elsewhere. |
| **Evidence of competence** | Operating-point bars met on a shifted regime, near-zero counterfactual flips, intervals on subgroup numbers and a candid validity section. |
| **Misconceptions exposed** | 'Dev accuracy tells you about deployment.' 'Remove the shortcut and you are done.' 'Group averages are enough.' |
| **Preparation for later work** | Leads into ML-05 evaluation, AI-13 responsible AI audits and ML-10 monitoring. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
