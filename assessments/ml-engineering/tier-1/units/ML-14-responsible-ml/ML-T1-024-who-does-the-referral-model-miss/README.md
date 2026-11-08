# ML-T1-024: Who Does the Referral Model Miss? A Group-Wise Error Audit and Model Card for a Child-Health Screening Tool

> *A community health referral model has good average accuracy. For whom is it worse, by how much, and is that difference real or noise?*

![Format: Implementation (secondary: Investigation)](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T1-024` |
| **Title** | Who Does the Referral Model Miss? A Group-Wise Error Audit and Model Card for a Child-Health Screening Tool |
| **Subtrack** | ML Engineering |
| **Tier** | 1: Foundations |
| **Unit** | [ML-14: Responsible ML (Fairness, Interpretability and Robustness)](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 8-12 hours over 1 week |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Precision, recall and the confusion matrix; numpy; the idea of a bootstrap. No fairness theory is needed. |
| **Skills developed** | Group-wise error audit; small-sample guards; bootstrap intervals; reliability bins; model-card writing |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

A state primary-health programme in Nigeria (fictional) equips community health workers with a simple tool that flags a sick child for **referral to a health facility**. A missed referral (a child who needed referral but was not flagged) can mean a delayed diagnosis. The programme's data team has a file with the tool's outputs for 2,000 children from the six geopolitical zones: the true need for referral, the flag, and the model's score. All data are synthetic; no real child, clinic or programme is represented.

Overall the tool looks good. The programme director asks a narrower question: **does it miss children more often in some zones than in others, and how sure are we?** Zones differ greatly in size, and one has fewer than 30 children in the file, so a naive table of rates would mislead. You will build the small toolkit an auditor needs, and then use it to write a model card.

You will implement, with numpy only:

1. **group metrics**: for each group, the number of children, the number who needed referral, and the selection rate, true-positive rate (the share of children who needed referral who were flagged), false-positive rate and positive predictive value, with `None` where a rate is undefined;
2. a **disparity table** against a reference group with a **minimum group size** guard;
3. a **group-stratified percentile bootstrap** for the gap in a rate between two groups;
4. **calibration within groups**: reliability bins and an expected calibration error;
5. a **model card generator** that turns the numbers into a markdown document with the warnings an honest card needs.

The tests fix every number. The thinking is in using them: which zone is worse, whether the gap is distinguishable from noise, why the smallest zone must not be ranked, and why equal calibration across zones would not mean equal missed referrals.

> **Why this matters beyond this task.** The first step of any fairness work is an audit that reports group differences with their uncertainty and refuses to over-read small groups. Most harm in deployed health models is found this way, long before any mitigation is considered.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Compute** per-group error rates exactly, with undefined rates handled explicitly instead of as zeros or NaNs.
2. **Report** group differences only where the group is large enough, and state the guard that decides.
3. **Estimate** the uncertainty of a gap by a stratified bootstrap and read the interval correctly.
4. **Check** whether scores mean the same thing in every group (calibration) and explain how that differs from equal error rates.
5. **Write** a model card whose claims never exceed what the intervals support.
6. **Explain** the audit's findings, and its blind spots, in plain language for a programme director.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement [`auditkit`](starter/auditkit/). Use only numpy and the standard library in the package.

| ID | Requirement |
|---|---|
| **R1** | `group_metrics(y_true, y_pred, group) -> dict`: keys are `str(group value)` in sorted order; each value is a dict with `n`, `positives`, `selection_rate` (mean of `y_pred`), `tpr`, `fpr`, `ppv`. A rate whose denominator is zero is `None`. Works for string or integer group labels. |
| **R2** | `disparity(metrics, key, ref=None, min_n=30) -> dict`: for each group a dict `{diff, ratio, reportable}` against the reference group (default: the group with the largest `n`, ties to the alphabetically first). `reportable` is true only if the group has `n >= min_n` and both values are not `None`; otherwise `diff` and `ratio` are `None`. `ratio` is `None` when the reference value is 0. |
| **R3** | `bootstrap_gap_ci(y_true, y_pred, group, g1, g2, metric="tpr", n_boot=1000, seed=0, alpha=0.05) -> (gap, lo, hi)`. `gap` is the observed metric of `g1` minus that of `g2`. Use `rng = np.random.default_rng(seed)`; in each replicate resample group `g1` (indices in original order, `rng.integers(0, n, n)`) and then group `g2`; skip replicates where either rate is undefined; `lo, hi` are the `alpha/2` and `1 - alpha/2` percentiles of the replicate gaps. |
| **R4** | `calibration_by_group(y_true, score, group, bins=5) -> dict`: for each group `{n, ece, bins}` where each non-empty bin is `{lo, hi, n, mean_score, observed}`; bin index is `min(int(score * bins), bins - 1)`; `ece` is the sum over bins of `n_bin / n * abs(mean_score - observed)`. |
| **R5** | `model_card(title, y_true, y_pred, score, group, intended_use, limitations, min_n=30, seed=0) -> str`: markdown with, in this order, `# Model card: <title>`, `## Intended use`, `## Evaluation data`, `## Overall performance` (lines `- accuracy: x.xxx`, `- tpr: ...`, `- fpr: ...`), `## Group performance` (a table row per group: `| group | n | selection rate | tpr | fpr | ppv |` with three decimals, `n/a` for `None`), `## Disparities`, `## Limitations`. In Disparities, compare each group's TPR with the reference group's (largest `n`) using R3 with `n_boot=500` and the given seed: a line `- <group>: <gap> [<lo>, <hi>], not distinguishable from zero` (or `distinguishable from zero`) with signed three-decimal numbers; for each group below `min_n` a line starting `WARNING: ` that names the group and says it is too small. The function must not modify its inputs and must be deterministic. |

### D.2 Engineering requirements (mandatory)

- Deterministic and pure: no global state, inputs unchanged.
- No pandas and no scikit-learn in the package.
- At least **8 tests of your own** in `tests/test_member_*.py`, including a case where a group has no positives and a case where a gap's interval contains zero.
- `audit.py` runs your toolkit on the official data and prints the model card and the calibration table; the output is quoted in `REPORT.md`.

### D.3 Responsibility

All data are synthetic. In the report, write one paragraph on what a missed referral means for a child and a family, on why a zone (a geographic grouping) can be a proxy for other characteristics, and on the **Nigeria Data Protection Act 2023**: health information is treated as sensitive personal data, so a real audit of this kind needs a lawful basis, data minimisation, and appropriate safeguards; automated decision-making that significantly affects people is also regulated. Cite only what you are sure of and say when you are not.

### D.4 Optional enhancements

- Add a Wilson interval for a single rate and compare it with the bootstrap.
- Add an intersectional audit (zone by urban or rural) and show how quickly cells become too small.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/referralgen.py`](resources/referralgen.py): `make_audit_data(n=2000, seed=5)` returns `y_true, y_pred, score, group` |
| **Provenance** | **Synthetic**, deterministic given the seed; fictional children, zones as labels only |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Groups** | Zones `NC, NE, NW, SE, SS, SW` with very different sizes (the smallest has under 30 children) |
| **Size** | Nothing is committed; `python resources/referralgen.py --out DIR --seed 5` writes a CSV of about 50 KB |

Hidden tests use other seeds, integer group labels, a planted gap, a null gap and different bootstrap settings.

**Setup**

```bash
cd assessments/ml-engineering/tier-1/units/ML-14-responsible-ml/ML-T1-024-who-does-the-referral-model-miss
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `auditkit/` package | Metrics, disparity, bootstrap, calibration and model card |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Includes the no-positives and zero-in-interval cases |
| 3 | `audit.py` | Produces the model card and tables quoted in the report |
| 4 | `REPORT.md` (at most 900 words plus tables), from the [template](submission-template/REPORT.md) | Findings for the programme director; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `group_metrics` matches independent numpy computations on the official and hidden data, with `None` for undefined rates and sorted string keys.
3. ⚙ `disparity` uses the correct reference, ties, the minimum-size guard and `None` handling.
4. ⚙ `bootstrap_gap_ci` reproduces the specified procedure exactly (to 1e-12) for TPR and FPR, any seed and alpha; on the official data the interval for the weakest large zone excludes zero, and on a null simulation it contains zero. *Justification:* the planted TPR gap is about 0.3 to 0.4 on groups of several hundred children, far beyond the interval half-width of about 0.1.
5. ⚙ `calibration_by_group` matches hand-computed bins, edge scores of 1.0 and ECE.
6. ⚙ `model_card` has the specified structure and numbers, warns about every group below `min_n`, and is deterministic and pure.
7. ✍ The report names the zone with the worst missed-referral rate, quotes its interval, explains why the smallest zone is not ranked, and states one difference between 'equal calibration' and 'equal TPR'.

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

1. **Create your own private repository** named `clbg-ML-T1-024-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `auditkit/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Threshold sensitivity.** Show how the TPR gap and PPV gap move as the flag threshold changes, and explain what that implies for choosing a single threshold.
2. **Multiple comparisons.** Adjust the intervals for the five comparisons and discuss what changes.
3. **Adding uncertainty to the card.** Extend the card with Wilson intervals for every cell of the group table.
4. **Audit the audit.** Write a test that shows your bootstrap interval has about 95% coverage on simulated data.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why a zone with 24 children is not given a TPR gap in the card even if its TPR is 1.0; (2) show an interval of [-0.02, 0.21] and ask what you may and may not conclude; (3) give an unseen modification, for example a minimum group size of 100 or a different reference group, and ask which lines of the card change.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Confusion-matrix rates, numpy indexing, the bootstrap idea. No fairness definitions or theory. |
| **New skill developed** | Auditing a model by group with uncertainty and refusing to over-interpret small groups. |
| **Decisions the member must make** | How to represent undefined rates; how to organise per-group computation; how to phrase a card so that it does not overclaim. |
| **What must be investigated independently** | Why a percentile bootstrap should resample within groups, and what happens to a replicate with no positives. |
| **Why it is interesting** | The headline accuracy is high; the audit shows one zone's children are missed far more often, and another zone cannot be assessed at all. |
| **Evidence of competence** | Exact agreement with independent computations on re-seeded data, a correct bootstrap, and a card that flags what it cannot support. |
| **Misconceptions exposed** | 'High average accuracy means a safe model.' 'A rate of 1.0 on 20 cases is good news.' 'A gap without an interval is a finding.' |
| **Preparation for later work** | Leads into ML-14 Tier 2 (fairness metric trade-offs and mitigation) and Tier 3 (interpretability faithfulness), and into model governance. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
