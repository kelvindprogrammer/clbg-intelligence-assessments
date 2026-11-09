# ML-T2-007: The Too-Good Credit Model

> *A default model scores an AUC of 1.00 in the notebook and collapses in production. Find out why, quantify the honest number, and say what would break next.*

![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-007` |
| **Title** | The Too-Good Credit Model: Leakage Forensics on a Microfinance Default Model |
| **Subtrack** | Machine Learning Engineering |
| **Tier** | 2: Applied Competence |
| **Unit** | [ML-04: Feature Engineering and Data for ML](../README.md) |
| **Format** | Debugging & Forensics (secondary: Comparative) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14-22 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | CPU only, 4 GB RAM, no GPU, no paid services, no internet after setup. The whole suite runs in about a minute |
| **Recommended prerequisites** | Familiarity with scikit-learn pipelines, logistic regression and AUC. [ML-T1-009](../../../../tier-1/units/ML-04-feature-engineering-and-data-for-ml/ML-T1-009-maize-yield-without-peeking/README.md) is helpful but optional. |
| **Skills developed** | Leakage forensics; evaluation design; temporal and group splits; drift monitoring; model risk communication |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

A microfinance bank lends small working-capital loans to market traders across several branches. Its data team has built a model to predict whether a loan will default, and the notebook reports an AUC of 1.00 on a held-out set. The credit committee is delighted, until the loan officers point out that the model flags almost nothing useful on new applications and that the first month of production scores look random. The head of risk asks you to find out what happened before anyone else relies on the model.

You are given 1,399 historical loans over 24 months: application-time information (amount, tenor, income, prior loans, a credit score, phone changes), several fields that the bank's systems record later (days past due at month end, collections calls, a restructuring flag, a refreshed bureau score), the month of disbursement, a customer identifier (many customers borrow repeatedly) and the default outcome. A data dictionary states when each field is recorded, but it was written by the team that built the model, and it is not necessarily correct.

Your job is forensic and constructive. Decide which features cannot be available when a lending decision is made, using both the dictionary and evidence in the data. Rebuild an evaluation that matches how the model would actually be used (train on the past, score the future, never score a customer the model has already learned from). Report the honest performance next to the naive one, quantify what drove the gap, and check whether the honest features are stable over time. The specification is partial: you choose the evidence standard for a leak and justify it, and you decide what else a credit committee needs to hear.

---

## C. Objectives

When you finish, you should be able to show that you can:

- Identify leaked features by combining documentation about timing with statistical evidence, and justify an evidence threshold.
- Design an evaluation split that respects time and customer identity and explain what each rule prevents.
- Quantify the inflation caused by leakage and by random splitting, using the same model on equal footing.
- Detect covariate drift between training and deployment periods with the population stability index.
- Write a risk finding that tells a credit committee what is wrong, what the honest number is and what to monitor.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the functions in `loan_audit/core.py`; stubs raise `NotImplementedError("R<n>: ...")` and the docstrings are the specification. Loading helpers are provided.

| # | Requirement |
|---|---|
| R1 | `audit_features(data, dictionary, auc_threshold)`: a verdict (`leak` or `ok`), single-feature AUC and reasons per candidate feature, combining the documented recording time with statistical evidence. |
| R2 | `honest_split(data, cutoff)`: temporal split with customers disjoint between train and test. |
| R3 | `leaky_vs_honest(data, dictionary, cutoff, seed)`: the naive random-split AUC with all features versus the honest AUC with leaks removed, plus the dropped features, using the same pipeline for both. |
| R4 | `psi` and `drift_check`: population stability index from its definition and a drift report between the early and late periods. |

You must also run these extra analyses and report them (not tested): (a) which single leak accounts for most of the inflation, by dropping features one at a time from the naive model; (b) the effect of each split rule separately (temporal only, customer-disjoint only, both); (c) what the PSI report implies for monitoring the honest model.

### D.2 Engineering requirements (mandatory)

- `pytest` passes from a clean environment built from `requirements.txt`; numpy and scikit-learn only.
- No label information may be used to build features inside the honest pipeline; scaling is fitted on training rows only.
- All randomness is seeded; `analysis.py` regenerates every table in the report in under 5 minutes.
- At least 6 tests of your own in `tests/test_member_*.py`, including a test that would fail if a post-outcome field were reintroduced.

### D.3 Privacy and responsibility

The loan records are synthetic and fictional. Real credit data are financial personal data under the NDPA 2023 and, in Nigeria, subject to credit-bureau rules; a default model also affects who obtains credit. Your finding must say how a wrongly trusted model could harm applicants (wrongful rejection or over-lending) and who should review the corrected model before use.

### D.4 Optional enhancements (not required for full marks)

- Train a gradient-boosted model on the honest features and compare it with logistic regression; explain what the gap does and does not show.
- Show how the leak audit would change if the bank also knew the loan officer's override notes.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/loans.csv`](resources/data/loans.csv): 1,399 loans x 14 columns (about 85 KB), and [`resources/data/data_dictionary.csv`](resources/data/data_dictionary.csv) |
| **Provenance** | **Synthetic**, generated with a fixed seed by a generator in the assessor kit (it holds the leak truth). Repeat borrowers, a rising default rate and income inflation are simulated. No real customers |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Hidden evaluation** | Re-seeded portfolios with the same structure |
| **Setup** | `pip install -r starter/requirements.txt` (numpy, scikit-learn, pytest) |

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `loan_audit/` package (completed starter) | R1-R4 |
| 2 | `tests/test_member_*.py` (at least 6 tests) | Guards against reintroducing leaks |
| 3 | `analysis.py` and its output tables | Per-feature ablation, split-rule ablation and PSI evidence |
| 4 | `REPORT.md` (at most 1,200 words plus tables) from the [template](submission-template/REPORT.md) | Risk finding for the credit committee and AI-use declaration |
| 5 | A 7-minute live defence | Verifies understanding (section K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Criteria marked (auto) are checked by the public and hidden test suites; the rest are checked by hand.

1. (auto) All public tests pass from a clean environment, and your own tests pass.
2. (auto) The audit flags exactly the four leaked features on the public data and on re-seeded portfolios, and flags the mislabelled field even when the dictionary says everything is recorded at application. *Justification:* the leaks have single-feature AUC of 0.74 to 1.00 and the strongest legitimate feature 0.58 to 0.67, so a threshold of 0.85 separates them; the weakest leak (restructuring flag) is caught only by documentation, which is why both signals are required.
3. (auto) The honest split is strictly temporal and customer-disjoint at any cutoff.
4. (auto) The naive AUC exceeds 0.97 and the honest AUC is between 0.58 and 0.80. *Justification:* the reference gives 1.00 and 0.64 to 0.68 on four seeds; an honest AUC outside this range signals a leak left in or a broken split.
5. (auto) PSI matches its definition and the drift report ranks income first (about 0.2) with tenor near zero.
6. The report separates the inflation due to each leak from that due to the random split, and names the monitoring metric and threshold you would set.
7. The report states plainly that the committee's 1.00 should be disregarded and what number replaces it, with its uncertainty.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Methodology and experimentation | 25 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 5 |
| Critical thinking and limitations | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, reproducible results and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T2-007-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders into it.
2. **Expected structure:**
   ```text
   clbg-ML-T2-007-<username>/
   ├── requirements.txt
   ├── loan_audit/          # your package
   ├── tests/               # provided tests + your test_member_*.py
   ├── resources/           # unchanged
   ├── analysis.py
   └── REPORT.md
   ```
3. **Commit as you work.** A single "final" commit containing everything will be questioned at defence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** set by the cohort coordinator. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback but never stand in for the core requirements.

1. **Bootstrap the honest AUC.** Give a confidence interval that respects customer clustering.
2. **Rolling origin.** Replace the single cutoff with a rolling-origin evaluation and show the AUC over time.
3. **Feature timing registry.** Design a machine-checkable schema that makes the next dictionary error detectable at build time.
4. **Policy impact.** Convert the honest model into an approval rule and estimate the loss from the naive model's false confidence.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration inside `REPORT.md`. Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** adapted code with a link. **Collaboration** is limited to general techniques; never share code, numbers or report text.
- **How understanding is verified.** In a short defence the assessor will:

1. Walk through how each leaked feature came to exist and why its timing makes it unusable for a lending decision.
2. Explain what the customer-disjoint rule changes in your numbers and why it matters even though customers differ by month.
3. Handle an unseen modification live, such as a new field that is recorded at application but computed from later data, or a different cutoff.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Logistic regression, AUC, pipelines, train/test logic, simple profiling. |
| **New skill developed** | Auditing a modelling dataset for leakage using both what documentation says and what the data show, and building an evaluation that mirrors deployment. |
| **Decisions the member must make** | The evidence standard for a leak, how to treat features of unknown timing, how to split, which ablations to run, and what to tell the committee. |
| **What must be investigated independently** | Which features are leaks, which split rules matter and how much each contributes, and what drifts. |
| **Why it is interesting** | An impossibly good model is the most common real-world failure in applied ML, and this one has a field the documentation gets wrong. |
| **Evidence of competence** | Exact leak identification on re-seeded portfolios, honest AUC in the expected range, correct PSI and a report that explains the gap. |
| **Misconceptions exposed** | "A high AUC means a great model." "The dictionary is the truth." "A random split is fine for loans." "Leakage only comes from the label column." |
| **Preparation for later work** | Leads to label-quality and data-centric work at Tier 3, monitoring in deployment units and model-risk reporting. |

**Suggested approach**, for members who want guidance (you may ignore it):

1. Plot univariate AUC for every field before reading the dictionary.
2. Build the honest split and check it with assertions.
3. Compare naive and honest on the same pipeline, then ablate.
4. Write the finding first for the committee, then the technical appendix.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
