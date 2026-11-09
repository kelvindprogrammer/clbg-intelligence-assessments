# ML-T2-005: Quiet Meters

> *Rank 360 meters by how suspicious they look when you have almost no labels, big honest customers, and an inspection budget.*

![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-005` |
| **Title** | Quiet Meters: Unsupervised Detection of Electricity Theft on a Distribution Feeder |
| **Subtrack** | Machine Learning Engineering |
| **Tier** | 2: Applied Competence |
| **Unit** | [ML-03: Unsupervised and Representation Learning](../README.md) |
| **Format** | Comparative (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14-22 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | CPU only, 4 GB RAM, no GPU, no paid services, no internet after setup. The whole suite runs in about a minute |
| **Recommended prerequisites** | Familiarity with scikit-learn estimators; the definitions of precision at k and average precision; numpy. [ML-T1-007](../../../../tier-1/units/ML-03-unsupervised-and-representation-learning/ML-T1-007-agents-on-the-map/README.md) is helpful but optional. |
| **Skills developed** | Anomaly-detection feature design; detector comparison; evaluation with scarce labels; bootstrap uncertainty; operational recommendations |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

A Nigerian distribution company loses a large share of the energy it supplies to non-technical losses: bypassed meters, tampered meters and meters that are simply not read. Field inspections are expensive, because a crew must be dispatched with a vehicle and a security escort, so the commercial team can inspect only a few dozen meters per month. Today they inspect the biggest consumers, because big numbers look suspicious.

You have four weeks of readings for 360 meters on one feeder, as kWh in four time bands per day (night, morning, afternoon, evening), plus the tariff class (residential, small business, industrial). A past audit physically inspected 100 of the meters and recorded whether tampering was found, but only a handful were positive. There are no other labels. Three kinds of tampering exist in the wild: a persistent partial bypass that cuts consumption after some date, a bypass of the evening lighting circuit, and an isolated meter that reads almost nothing on random days. Some meters look just as odd for honest reasons: a house locked for a week while the family travels, and a shop that doubled its trade.

Your job is to build and compare detectors, decide which one to trust given how little audit evidence exists, and hand the commercial team a ranked inspection list of a given size with an honest statement of how much to believe it. The specification below is partial. You choose the features, the preprocessing and the hyper-parameters, and the report must justify them against a baseline.

---

## C. Objectives

When you finish, you should be able to show that you can:

- Design behavioural features that expose tampering while being blind to customer size, weekday pattern and fleet-wide weather effects.
- Compare isolation forest, LOF and PCA reconstruction error against a simple magnitude baseline on equal footing.
- Quantify how uncertain a method ranking is when the audit sample contains few positives, using a bootstrap.
- Reason about decoy anomalies (vacancy, growth) and decide what the model should and should not flag.
- Turn a score into an operational recommendation with a stated inspection budget and caveats.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the functions in `meter_audit/core.py`. Stubs raise `NotImplementedError("R<n>: ...")`; `load_meters` and the dataclasses are provided.

| # | Requirement |
|---|---|
| R1 | `build_features(readings, tariff)`: at least 4 finite, deterministic features per meter, built without labels and invariant to multiplying all readings by one constant. A big honest customer must not look anomalous for being big. |
| R2 | `score_meters(..., "baseline")`: per tariff class, the robust z-score `abs(x - median) / (1.4826 * MAD)` of each meter's mean daily kWh. This is exactly the behaviour of "inspect the biggest consumers". |
| R3 | `score_meters` for `iforest`, `lof` and `pca`: detectors on your features. Preprocessing and hyper-parameters are yours; unknown methods raise `ValueError`; results are deterministic for a given seed. |
| R4 | `precision_at_k` and `average_precision` implemented from their definitions. |
| R5 | `evaluate_methods(data, seed, n_boot)`: audit-sample average precision for every method with a 95% percentile bootstrap interval over audited meters. |
| R6 | `recommend(data, budget_k, seed)`: choose a non-baseline method using the audit evidence **and** its uncertainty, and return `budget_k` meters plus a rationale. |

You are also expected to run your own experiments (an ablation of at least three feature groups, and a sensitivity check of one hyper-parameter) and report them. Those experiments are marked from the report and `experiments.py`, not by tests.

### D.2 Engineering requirements (mandatory)

- `pytest` passes from a clean environment built from `requirements.txt`; only numpy and scikit-learn are used.
- No label information (`audit_y`) flows into features or detector scores; labels are used only for evaluation and method choice, and your report says where.
- All randomness is seeded; `experiments.py` regenerates every table in the report in under 5 minutes on a laptop.
- At least 6 tests of your own in `tests/test_member_*.py`, including one that would catch a feature accidentally encoding customer size.

### D.3 Privacy and responsibility

The data are synthetic and describe no real customer. In practice, meter data reveal when people are at home and are personal data under the NDPA 2023. An inspection list is also a consequential action against named customers: the report must say what human review should happen before a crew is sent, and why a model score alone is not evidence of theft.

### D.4 Optional enhancements (not required for full marks)

- Evaluate a fifth detector of your choice (for example a one-class SVM or a Gaussian mixture) and explain why it does or does not help.
- Estimate how many positives the audit sample would need for the method ranking to be statistically stable.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/meters.npz`](resources/data/meters.npz): `readings` (360 meters x 28 days x 4 bands, kWh), `tariff`, `audit_idx`, `audit_y` (about 80 KB) |
| **Provenance** | **Synthetic**, generated with a fixed seed by a generator in the assessor kit (it contains the full theft truth). Daily patterns, weekday effects, a shared weather factor and customer size are simulated. No real meters or people. |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Labels** | Only the 100 audited meters are labelled. The full truth is held back and used by hidden tests on re-seeded fleets |
| **Setup** | `pip install -r starter/requirements.txt` (numpy, scikit-learn, pytest) |

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `meter_audit/` package (completed starter) | Features, detectors, metrics and recommendation (R1-R6) |
| 2 | `tests/test_member_*.py` (at least 6 tests) | Pins behaviour and guards against scale leakage |
| 3 | `experiments.py` and its saved outputs | Ablation, sensitivity and method-comparison evidence |
| 4 | `REPORT.md` (at most 1,200 words plus tables) from the [template](submission-template/REPORT.md) | Method choice, uncertainty, limits and AI-use declaration |
| 5 | A 7-minute live defence | Verifies understanding (section K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Criteria marked (auto) are checked by the public and hidden test suites; the rest are checked by hand.

1. (auto) All public tests pass from a clean environment, and your own tests pass.
2. (auto) Features are scale-free: scaling every reading by 1,000 changes no feature beyond 1e-4.
3. (auto) On the public audit sample, the recommended method's average precision is at least 0.45 and at least 0.25 above the baseline. *Justification:* the reference reaches 0.73 against 0.12 for the baseline; the bar is modest because method choice is in-sample.
4. (auto) On hidden re-seeded fleets of 500 meters with a different audit sample, the top-k list for k equal to the true number of thieves has precision at least 0.45 and at least 0.30 above the baseline. *Justification:* the reference reaches 0.55-0.60 because honest decoys (vacancy and growth, 8% of meters) are genuinely hard; 0.45 leaves room for a different but sound design.
5. (auto) Ordinary meters are a minority of the hidden top-30 list, and the features are not a disguised proxy for consumption level (no feature correlates above 0.6 with log mean consumption).
6. The report contains the ablation and sensitivity experiments, shows the bootstrap intervals, and states whether the evidence separates the methods or not.
7. The report names what the model cannot tell apart (for example vacancy versus theft), what human check is needed before dispatch, and the cost of a false positive.

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

1. **Create your own private repository** named `clbg-ML-T2-005-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders into it.
2. **Expected structure:**
   ```text
   clbg-ML-T2-005-<username>/
   ├── requirements.txt
   ├── meter_audit/         # your package
   ├── tests/               # provided tests + your test_member_*.py
   ├── resources/           # unchanged
   ├── experiments.py
   └── REPORT.md
   ```
3. **Commit as you work.** A single "final" commit containing everything will be questioned at defence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** set by the cohort coordinator. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback but never stand in for the core requirements.

1. **Decoy handling.** Add a feature or rule that separates a one-week vacancy from persistent theft and measure the precision gain on your own simulated fleets.
2. **Weather robustness.** Remove the fleet-wide daily factor from your features in two different ways and compare their ablations.
3. **Active inspection.** Simulate sequential inspection: after each batch of results, update your ranking. How much does precision improve per batch?
4. **Cost-sensitive list.** Suppose a false inspection costs 4 times a missed theft. How would you change the list size and the ranking criterion?

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration inside `REPORT.md`. Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** adapted code with a link. **Collaboration** is limited to general techniques; never share code, numbers or report text.
- **How understanding is verified.** In a short defence the assessor will:

1. Explain which of your features catches each of the three tampering types, and show on one meter why a vacancy is flagged.
2. Defend your method choice given the width of the bootstrap intervals; what would change your mind?
3. Handle an unseen modification live, such as a new tampering pattern that only affects weekends, or a meter whose class label is wrong.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Standard anomaly detectors, precision at k, bootstrap resampling, numpy. |
| **New skill developed** | Comparing unsupervised methods honestly when labels are scarce, and expressing a recommendation together with its uncertainty. |
| **Decisions the member must make** | Which behavioural features to build, how to remove customer size and weather, which detector settings to use, how to pick a method when intervals overlap, and what to say about decoys. |
| **What must be investigated independently** | Which kinds of tampering exist in the data, what each looks like in the four bands, and how the baseline fails. |
| **Why it is interesting** | The intuitive policy (inspect the biggest meters) is measurably wrong, and the evidence for any better policy is thin, which is the usual state of fraud analytics. |
| **Evidence of competence** | Hidden-fleet precision at k, scale-free features, ablations that explain the result, and a recommendation that does not overstate its evidence. |
| **Misconceptions exposed** | "An outlier is a thief." "Higher consumption means higher risk." "The method with the best point estimate is the best method." "Unsupervised means no evaluation." |
| **Preparation for later work** | Leads to the Tier 3 problem of deciding whether structure exists at all, to label-efficient learning in ML-04, and to monitoring of model drift in deployment units. |

**Suggested approach**, for members who want guidance (you may ignore it):

1. Plot a few suspicious and normal meters per tariff class before designing any feature.
2. Get the baseline and the metrics (R2, R4) right first so you have a fixed yardstick.
3. Add one feature group at a time and watch audit AP and hidden-style precision on your own simulated fleets.
4. Write the report around the experiments, not the other way round.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
