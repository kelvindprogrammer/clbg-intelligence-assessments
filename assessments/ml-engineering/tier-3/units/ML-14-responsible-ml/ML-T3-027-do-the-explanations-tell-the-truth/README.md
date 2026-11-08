# ML-T3-027: Do the Explanations Tell the Truth? Faithfulness, Stability and Shortcut Audits for a Tuberculosis-Screening Model

> *A screening model looks excellent in the camps where it was trained. Do its explanations reveal that it learned the device, not the disease, and how far can you trust them?*

![Format: Investigation (secondary: Open-Ended)](https://img.shields.io/badge/format-investigation-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-027` |
| **Title** | Do the Explanations Tell the Truth? Faithfulness, Stability and Shortcut Audits for a Tuberculosis-Screening Model |
| **Subtrack** | ML Engineering |
| **Tier** | 3: Advanced Practice |
| **Unit** | [ML-14: Responsible ML (Fairness, Interpretability and Robustness)](../README.md) |
| **Format** | Investigation (secondary: Open-Ended) |
| **Difficulty** | Technical 4 · Mathematical 4 · Research 4 · Engineering 3 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 24-32 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Strong supervised-learning background including evaluation under shift. Recommended: ML-T2-029 and ML-T1-024. |
| **Skills developed** | Attribution methods; faithfulness metrics; explanation stability; shortcut detection; critical evaluation of interpretability claims |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Mobile outreach teams in northern Nigeria (fictional programme) screen people for tuberculosis using a tablet that records nine clinical features and, silently, a **device offset**: a calibration value that differs between the two screening devices in use. In the training camps, sicker people were screened first and on one device, so the device offset is strongly correlated with the label. In routine deployment devices are assigned at random and the correlation vanishes. A model trained on camp data scores an AUC near 0.98 in camps and near 0.63 in deployment. All data are synthetic; no real patient or programme is represented.

Before the model was deployed, a reviewer asked for explanations. A vendor showed attribution plots. The programme medical lead now asks you a harder question than 'what does the model use?':

> *Do these explanations tell the truth about the model, can they reveal a shortcut like the device offset before deployment, and where would they mislead us?*

This is an open investigation. The brief asks you to build the instruments and run the study; it does not prescribe the methods to trust. You will implement a small interpretability toolkit with exactly testable properties, then use it to answer:

1. **Do attribution methods expose the shortcut?** Compare permutation importance and sampled Shapley values (and any method you add) on a logistic regression, a random forest and a small neural network, with the shortcut in different columns and at different strengths.
2. **Are the explanations faithful?** Use deletion curves to test whether removing what the explanation calls important changes the model's output more than removing random or unimportant features. Examine how the answer depends on the **baseline** used to replace features.
3. **Are they stable and do methods agree?** Quantify top-k stability under small input noise and top-k agreement between methods.
4. **Can an audit catch it?** Implement a deployment-shift audit: a feature whose importance on camp-like data is large but vanishes on a deployment-like sample is flagged as a candidate shortcut. Quantify its false alarms on clean models and its power across strengths.
5. **What can't it show?** Correlated features (fever, cough and oxygen saturation are related) split credit; attribution is not causation; the audit needs a deployment-like sample that a real programme may not have.

The tests fix the numerical definitions and a small set of behaviours; your design of the study, the choice of baselines, thresholds and the judgement of what the evidence supports are the assessment.

> **Why this matters beyond this task.** Explanations are used to build trust in clinical models. An explanation that is unfaithful, unstable or silent about a shortcut is worse than none, because it manufactures confidence.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** AUC, permutation importance and sampled Shapley values with properties that can be verified exactly (efficiency, dummy features, linear-model exactness).
2. **Measure** faithfulness with deletion curves and show how the baseline changes conclusions.
3. **Quantify** stability and agreement across methods and model classes, with uncertainty over seeds.
4. **Design** and evaluate a shortcut audit, reporting false alarms on clean models and power across shortcut strengths and positions.
5. **Identify** what correlated features, background choice and sample size do to attributions.
6. **Argue** the limits of interpretability evidence for a clinical decision, including what must still be verified by intervention or deployment data.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement [`xaudit`](starter/xaudit/). Use only numpy and the standard library in the package; scikit-learn may be used in tests and experiments.

| ID | Requirement |
|---|---|
| **R1** | `roc_auc(y, score)`: rank-based (Mann-Whitney) AUC with average ranks for ties; `0.5` for constant scores. |
| **R2** | `permutation_importance(predict, X, y, n_repeats=5, seed=0)`: `predict` maps a matrix to scores. With `rng = np.random.default_rng(seed)`, for each column `j` in order and each repeat in order, replace column `j` by `X[rng.permutation(len(X)), j]`, and record the drop in `roc_auc` from the unpermuted baseline; return the mean drop per column. |
| **R3** | `shapley_sampling(f, x, background, n_perm=200, seed=0) -> (phi, base)`: `f` maps a matrix to a vector. With `rng = np.random.default_rng(seed)`, for each permutation draw `perm = rng.permutation(d)` and then a background row `b = background[rng.integers(len(background))]`; walk from `b` to `x` switching features in `perm` order, evaluating `f` on all `d + 1` intermediate points in one call, and credit each feature with the change in `f` at its step. `phi` is the mean credit; `base` is the mean of `f(b)`. Consequently `phi.sum() == f(x) - base` exactly, unused features get exactly 0, and a linear `f` gives `w * (x - mean of sampled b)`. |
| **R4** | `deletion_curve(f, X, attributions, baseline)`: for each row, order columns by descending absolute attribution (stable ties); for `k = 0..d` replace the top `k` columns of every row by `baseline`; return the mean of `f` over rows (length `d + 1`). `deletion_auc(curve)`: trapezoid area over `k/d` in `[0, 1]`. |
| **R5** | `agreement(a, b, k) -> {topk_jaccard, spearman}` using absolute attributions (stable ties; Spearman as Pearson on average ranks). `stability(method, f, X_rows, noise_sd, seed, k)`: with `rng = np.random.default_rng(seed)`, for each row `x` add `rng.normal(0, noise_sd, d)`, compare the top-`k` sets of `method(f, x)` and `method(f, x_noisy)` by Jaccard, and return the mean. |
| **R6** | `shortcut_audit(predict_proba, X_ref, y_ref, X_dep, y_dep, thresh=0.05, n_repeats=5, seed=0) -> dict` with `flagged` (sorted column indices), `imp_ref` and `imp_dep`. The decision rule and the use of the two samples are yours (the reference rule is on importance difference); justify it in the report. `X_ref` is a **held-out** sample from the training distribution, not the training set. |

### D.2 Engineering requirements (mandatory)

- Deterministic with explicit seeds; no hidden global state.
- Do not hard-code the device column's name or position: hidden tests move it and change its strength.
- At least **12 tests of your own** in `tests/test_member_*.py`, including exactness tests (efficiency, dummy feature, linear model) and a test that the audit stays quiet on a clean model.
- `experiments.py` regenerates every number and figure in `REPORT.md`. The study must cover: three model classes; at least three shortcut positions and three strengths including 0; at least **5 seeds**; two baselines (feature mean and a background sample) in the deletion analysis; and an analysis of the credit given to correlated features.

### D.3 Responsibility

The data are synthetic and no real patient is represented. In the report, discuss in at most 400 words: the risk that a model which learned a device artefact misdirects care and why this is a health-equity issue (devices are not equally distributed across facilities); why an explanation shown to clinicians can create automation bias; and how the **Nigeria Data Protection Act 2023** bears on explanations for automated decisions about health (cite only provisions you are sure of, such as the Act's treatment of sensitive personal data including health data and of automated decision-making, and say when you are unsure). State what clinical and technical sign-off an explanation-based approval would require.

### D.4 Optional enhancements

- Add a local surrogate (LIME-style) method and compare faithfulness and stability with Shapley sampling.
- Add an intervention test that randomises the device column in deployment-like data and compares the predicted effect with the audit's.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/screening.py`](resources/screening.py): `make_screening(n=3000, seed=0, shortcut_col=None, shortcut_strength=0.9, deployment=False)` returns `X, y, names` |
| **Provenance** | **Synthetic**, deterministic given the arguments; fictional patients |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Columns** | `cough_days, weight_loss_kg, night_sweats, fever_days, spo2, resp_rate, age, contact_score, bmi` plus `device_offset` inserted at `shortcut_col` (default last). Some clinical features are correlated with each other |
| **Size** | Nothing is committed; `python resources/screening.py --out DIR --seed 1` writes two CSVs of about 250 KB each |
| **Run time** | Shapley sampling is the slow step: budget `n_perm` and the number of explained rows, and report the Monte Carlo error |

Hidden tests use other seeds, shortcut positions and strengths, a neural network and a clean-model control, and check against ground truth held only by the assessors.

**What the generator does not tell you.** It does not say which features drive the label. The relation between the device offset and the label differs between training and deployment samples; that is all a real programme would know.

**Setup**

```bash
cd assessments/ml-engineering/tier-3/units/ML-14-responsible-ml/ML-T3-027-do-the-explanations-tell-the-truth
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `xaudit/` package | Attribution, faithfulness, stability, agreement and audit functions |
| 2 | `tests/test_member_*.py` (at least 12 tests) | Exactness and clean-model tests |
| 3 | `experiments.py` | Reproduces the full study (3 model classes, 3 positions, 3 strengths, 5 or more seeds) |
| 4 | `REPORT.md` (at most 3,000 words plus tables and figures), from the [template](submission-template/REPORT.md) | Study for the programme medical lead; carries the AI-use declaration |
| 5 | A 10-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ **Exactness.** `roc_auc` matches a brute-force pairwise AUC; `permutation_importance` reproduces the specified RNG procedure to 1e-12; `shapley_sampling` satisfies efficiency to 1e-9, gives exactly 0 to unused features and is exact for linear models.
3. ⚙ **Faithfulness machinery.** `deletion_curve`, `deletion_auc`, `agreement` and `stability` match hand and brute-force values, and stability separates a deterministic method (1.0 at tiny noise) from random attributions (below 0.7).
4. ⚙ **Audit.** `shortcut_audit` flags exactly the device column for logistic regression, forest and neural-network models trained with the shortcut at other positions and strengths (0.7 to 0.9), and flags nothing for models trained without it. *Justification:* at these strengths the device's held-out importance is 0.2 to 0.4 AUC in camps and near 0 in deployment; the reference threshold of 0.05 separates them with a wide margin, and clean models have no column above 0.03 on a held-out reference sample.
5. ⚙ On hidden seeds the Shapley global ranking puts the device column in its top two for shortcut models, and the top four of a clean model include at least three of the four true clinical drivers (known only to the assessors).
6. ✍ The study reports false-alarm and power results for the audit with uncertainty over seeds; shows how baseline choice changes deletion-curve conclusions; shows correlated-feature credit splitting; and compares methods on agreement and stability.
7. ✍ A validity section lists threats (one synthetic generator, shortcut that is easy to see, no real clinicians, deployment sample availability, attribution versus causation) and states what evidence beyond explanations a programme must have before approving a model.

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

1. **Create your own private repository** named `clbg-ML-T3-027-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `xaudit/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Intervention check.** Randomise the device column in the deployment sample and compare the model's change in AUC with each method's attribution.
2. **Adversarial explanations.** Train a model that hides the shortcut from permutation importance (for example by duplicating the device information in two correlated columns) and test whether your audit still flags it.
3. **Mitigation.** Retrain after removing the flagged column, and compare deployment AUC.
4. **Calibration of the threshold.** Set the audit threshold from a null distribution rather than by hand and compare.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 10-minute defence the assessor will (1) ask you to prove from your code why Shapley sampling satisfies efficiency exactly even with few permutations; (2) ask why a deletion curve with a mean baseline and one with a background-sample baseline can rank two methods differently, using a number from your study; (3) give an unseen modification, for example two device columns that are copies of each other, or a deployment sample of only 50 patients, and ask what happens to your audit and why.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Supervised models, AUC and distribution shift. No prior interpretability library knowledge: the methods are built from scratch. |
| **New skill developed** | Evaluating explanations as scientific claims: testing faithfulness, stability and agreement, and auditing for shortcuts with deployment-like data. |
| **Decisions the member must make** | Baselines; number of permutations and rows; audit rule and threshold; what counts as agreement; how to present Monte Carlo and seed uncertainty. |
| **What must be investigated independently** | How correlated features split credit, why training-set importance of a forest is inflated, and what a deletion baseline means. |
| **Why it is interesting** | Explanations can reveal the shortcut, miss it or invent one, depending on model class, baseline and reference sample; the member measures which. |
| **Evidence of competence** | Exact method properties on re-seeded data, an audit that works across positions and models without false alarms, and a study whose claims match its evidence. |
| **Misconceptions exposed** | 'Feature importance tells us what the model understands.' 'An explanation method is correct if it looks sensible.' 'Training-set importance is enough.' |
| **Preparation for later work** | Leads into research on explanation evaluation, robust and causal approaches, and into clinical AI governance. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
