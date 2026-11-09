# ML-T3-005: Do the Cooperatives Have Segments?

> *A savings cooperative wants member segments. Your first job is to find out whether segments exist at all, and to defend the answer.*

![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-005` |
| **Title** | Do the Cooperatives Have Segments? Testing for Structure Before Clustering |
| **Subtrack** | Machine Learning Engineering |
| **Tier** | 3: Advanced Practice and Research Thinking |
| **Unit** | [ML-03: Unsupervised and Representation Learning](../README.md) |
| **Format** | Investigation (secondary: Open-ended) |
| **Difficulty** | Technical 4 · Mathematical 3 · Research 4 · Engineering 3 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 24-40 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | CPU only, 4 GB RAM, no GPU, no paid services, no internet after setup. The whole suite runs in about a minute |
| **Recommended prerequisites** | Solid grounding in clustering and in numpy/scikit-learn; ideally [ML-T1-007](../../../../tier-1/units/ML-03-unsupervised-and-representation-learning/ML-T1-007-agents-on-the-map/README.md) and [ML-T2-005](../../../../tier-2/units/ML-03-unsupervised-and-representation-learning/ML-T2-005-quiet-meters/README.md) or equivalent experience. |
| **Skills developed** | Structure testing; null models; gap statistic; stability analysis; preprocessing ablations; simulation-calibrated decision rules; honest reporting of ambiguity |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

A thrift and credit cooperative with 700 members across several local governments wants to "segment its members" so that it can design products: a salary-advance loan for civil servants, a seasonal-input loan for farmers, and so on. A consultant has already produced a slide with five coloured clusters from k-means on the raw spreadsheet. The board is about to fund products on that slide. The cooperative's data officer is unconvinced and asks you the question the consultant never asked: **is there any real structure here, and if so how many segments, and how sure are you?**

The file `coop_members.csv` has eight numeric columns in very different units (monthly contribution, savings balance and loan size in naira with heavy right tails; repayment rate and meeting attendance as proportions; tenure in months; a volatility measure; household size) and a trade label. Some columns are nuisance, and the trade label is not known to carry any signal. The truth is not given. You will not be told whether the file contains three segments, none, or something in between.

This is a research-style problem. You must decide how to prepare the data, what "no structure" should look like (the null model), how to quantify evidence for a given number of segments, how to check that a segmentation survives resampling, and how to turn all of that into a decision rule that returns an honest answer, including **one segment** (no structure) when that is what the evidence supports. Your decision rule is then run by assessors on populations you have never seen, some with two to four segments and some with none. Your report is where you convince the board, in plain language, of what the data do and do not show.

---

## C. Objectives

When you finish, you should be able to show that you can:

- State falsifiable hypotheses about the cooperative data, design experiments to test them, and report results that include negative findings.
- Quantify how preprocessing choices (log transform, scaling, dropping nuisance columns) change the apparent clustering, using ablations.
- Construct and compare null reference distributions, and explain why a uniform reference can manufacture structure in correlated Gaussian data.
- Combine a statistic (gap, information criterion), a stability analysis and a decision threshold into a procedure, and calibrate it on simulated ground truth.
- Defend the trade-off between false discovery of segments and missed segments for a business decision.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the functions in `segment_lab/core.py`; stubs raise `NotImplementedError("R<n>: ...")`. A public simulator `segment_lab.simulate(k, n, seed)` with known truth is provided for your experiments; the hidden evaluation uses a **harder, differently parameterised** family, so tuning only to the simulator will fail.

| # | Requirement |
|---|---|
| R1 | `prepare(X)`: a finite matrix ready for distance-based clustering; not dominated by any column's units or tail; unchanged if a column is rescaled (naira to kobo); deterministic; does not modify its input. |
| R2 | `null_samples(Xp, n_null, seed, kind)`: reference datasets with no cluster structure; `gaussian_cov` (Gaussian with the data's mean and covariance) and `uniform_pca` (uniform on the bounding box in principal-component axes); unknown kinds raise `ValueError`. |
| R3 | `gap_statistic(Xp, k_max, n_null, seed, null_kind)`: `{k: (gap, se)}` for k from 1 to k_max with k-means inertia and the formulas in the docstring. |
| R4 | `stability(Xp, k, n_boot, seed)`: mean pairwise adjusted Rand index of full-data labelings from k-means fitted on 80% subsamples; 1.0 for k below 2. |
| R5 | `estimate_k(X, k_max, seed)`: your decision procedure from raw features to a `StructureReport`; k=1 means no structure; deterministic; under 30 seconds for n=700; insensitive to column units and row order. |

Beyond the code, the report must include: (a) a preprocessing ablation of at least four configurations; (b) a null-model comparison showing the gap statistic under both nulls on the cooperative data and on simulated no-structure data; (c) a calibration of your decision rule over at least 40 simulated populations (k from 1 to 4) with a confusion table; (d) your verdict on the cooperative file with its uncertainty.

### D.2 Engineering requirements (mandatory)

- `pytest` passes from a clean environment built from `requirements.txt`; numpy and scikit-learn only.
- All experiments are seeded and reproducible by `experiments.py` in under 20 minutes on a laptop; results are saved as tables the report quotes.
- Thresholds in your decision rule are chosen on your own simulations, never on the file you are asked to judge, and you say how many simulations stand behind each.
- At least 8 tests of your own in `tests/test_member_*.py`, including a regression test for a failure mode you found.

### D.3 Privacy and responsibility

The data are synthetic; no real member is described. Real cooperative data (savings, loans, repayments) are financial personal data under the NDPA 2023. Segmentation can also entrench discrimination, for example if segments proxy for gender, ethnicity or location and are used to ration credit. State which columns you would refuse to use for product eligibility, and why a statistically real segment is not automatically a fair basis for a decision.

### D.4 Optional enhancements (not required for full marks)

- Compare two additional structure detectors (for example silhouette peak tests and dip tests on a projection) in your calibration.
- Show how your procedure behaves when a real segment is small (5% of members).

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/coop_members.csv`](resources/data/coop_members.csv): 700 members x 8 numeric columns and a trade label (about 60 KB) |
| **Provenance** | **Synthetic**, generated with a fixed seed by a generator in the assessor kit (it holds the truth). Heavy tails and unit differences are simulated. No real people |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Simulator** | `segment_lab.simulate(k, n, seed, sep, tail)`: public, known truth, easier than the hidden family |
| **Setup** | `pip install -r starter/requirements.txt` (numpy, scikit-learn, pytest) |

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `segment_lab/` package (completed starter) | Methods R1-R5 |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Pins behaviour and failure modes |
| 3 | `experiments.py` and saved result tables | Ablation, null comparison and calibration evidence |
| 4 | `REPORT.md` (at most 2,000 words plus tables) from the [template](submission-template/REPORT.md) | Hypotheses, results, verdict, limits and AI-use declaration |
| 5 | A 10-minute live defence | Verifies understanding (section K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Criteria marked (auto) are checked by the public and hidden test suites; the rest are checked by hand.

1. (auto) All public tests pass from a clean environment, and your own tests pass.
2. (auto) `prepare` is invariant to rescaling a column and tames the heavy-tailed money columns (absolute skewness below 0.8 on the simulator).
3. (auto) With a Gaussian null, the gap statistic of correlated Gaussian data stays below 0.3, while the uniform null produces a gap above 0.3, demonstrating the two nulls are implemented as specified.
4. (auto) On hidden populations (n=500, separation 5.5, tail 1.0, seeds you cannot see), `estimate_k` returns 1 for every structureless population and the exact true k for the segmented populations tested (2, 3 and 4). *Justification:* with mean separation of 5.5 latent standard deviations and a Gaussian-mixture reference at 5 of 6 to 6 of 6 exact recoveries on a larger pool, exact recovery is achievable; the no-structure cases must be exact because a false segmentation is the costliest error for the board.
5. (auto) Unit changes and row order do not alter your answer.
6. The report contains the preprocessing ablation, both null comparisons and a calibration table of at least 40 simulations, and its verdict on the cooperative file is stated with a probability-style or interval-style uncertainty.
7. The report states what the consultant's five-cluster slide would have required to be true, and whether your evidence supports it.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 15 |
| Implementation quality | 5 |
| Methodology and experimentation | 25 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 5 |
| Critical thinking and limitations | 20 |
| Presentation and communication | 10 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, reproducible results and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T3-005-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders into it.
2. **Expected structure:**
   ```text
   clbg-ML-T3-005-<username>/
   ├── requirements.txt
   ├── segment_lab/         # your package
   ├── tests/               # provided tests + your test_member_*.py
   ├── resources/           # unchanged
   ├── experiments.py
   ├── results/             # tables quoted in the report
   └── REPORT.md
   ```
3. **Commit as you work.** A single "final" commit containing everything will be questioned at defence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** set by the cohort coordinator. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback but never stand in for the core requirements.

1. **Detection limits.** Plot the probability that your procedure finds a true 2-segment structure as separation shrinks, and locate the point where it can no longer tell the difference from noise.
2. **Misspecification.** Generate segments with non-Gaussian shapes (rings, bananas) and show where Gaussian-mixture reasoning fails and what a density-based method adds.
3. **Representation learning.** Replace the preprocessing with a PCA or autoencoder-style projection and test whether it improves recovery or just changes the metric.
4. **Business value.** Simulate a product decision on top of your segments and compute the expected loss from a false segmentation versus a missed one.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration inside `REPORT.md`. Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** adapted code with a link. **Collaboration** is limited to general techniques; never share code, numbers or report text.
- **How understanding is verified.** In a short defence the assessor will:

1. Explain, with a picture, why the uniform reference invents clusters in correlated Gaussian data.
2. Defend one threshold in your decision rule: what simulations support it and what happens one step either side.
3. Handle an unseen modification live, such as a new column of household income in kobo, or a request to report soft membership probabilities instead of hard labels.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Clustering, mixture models, information criteria, stability metrics, experimental discipline. |
| **New skill developed** | Treating the existence of structure as a testable claim, and engineering a calibrated decision procedure instead of trusting a single cluster-count heuristic. |
| **Decisions the member must make** | Preprocessing, the null model, the statistic, the stability criterion, the thresholds, the cost trade-off between false and missed discoveries, and the wording of a verdict under uncertainty. |
| **What must be investigated independently** | How raw clustering of this file fails, which columns carry signal, and how the rule behaves with no structure. |
| **Why it is interesting** | Most clustering reports are never asked whether clusters exist; here a wrong yes has a business cost and a defensible no is a valid result. |
| **Evidence of competence** | Hidden-population accuracy including all structureless cases, a calibration table that explains it, and a report that quantifies its own uncertainty. |
| **Misconceptions exposed** | "Silhouette peaks mean clusters exist." "k-means always finds k clusters, so it found them." "A uniform reference is neutral." "Preprocessing is a detail." |
| **Preparation for later work** | Leads to density-based and mixture-model work, evaluation without labels in later ML units, and the signature research challenges. |

**Suggested approach**, for members who want guidance (you may ignore it):

1. Reproduce the consultant's slide first, then show how it changes with preprocessing.
2. Build the null models and look at gap curves on simulated no-structure data before touching the real file.
3. Develop the decision rule on simulations only; look at the cooperative file last.
4. Write the verdict with explicit uncertainty.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
