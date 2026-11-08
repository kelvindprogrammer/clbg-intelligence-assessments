# ML-T1-004: The Field Officer's Decision Tree: A CART Classifier from Scratch for Cassava Disease Triage

> *Extension officers in Oyo State cannot run a neural network on a feature phone. Build a decision tree from first principles, match scikit-learn, and turn it into rules they can follow.*

![Format: Implementation (secondary: Replication)](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T1-004` |
| **Title** | The Field Officer's Decision Tree: A CART Classifier from Scratch for Cassava Disease Triage |
| **Subtrack** | ML Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [ML-02: Supervised Learning and Ensembles](../README.md) |
| **Format** | Implementation (secondary: Replication) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 10–14 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Python classes and recursion; numpy sorting, cumulative sums and boolean masks; the idea of a classification label. Helpful but optional: ML-T1-001 |
| **Skills developed** | Gini impurity and information gain; exhaustive split search in O(n log n) per feature; recursive tree construction; stopping rules; impurity-based feature importance; rule extraction; diagnosing overfitting with a depth sweep |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Extension officers of the (fictional) Oyo Agricultural Development Programme visit cassava farms to triage two diseases: cassava mosaic disease (CMD) and cassava bacterial blight (CBB). They carry a basic phone and a paper card. A new tool should classify a plot as *healthy*, *CMD* or *CBB* from five quick measurements: a leaf-mosaic score (0 to 10), whitefly count per plant, rainfall in the past two weeks, soil pH and plant age in weeks. Because officers must explain a diagnosis to a farmer, and because the phone cannot run a large model, the programme wants a **decision tree** whose rules can be printed on the card.

You will build that tree from first principles. The package `treeforge` has the same skeleton as any CART implementation: an impurity measure, an efficient exhaustive search for the best binary split, a recursive builder with stopping rules, and prediction. You will verify it against scikit-learn's `DecisionTreeClassifier` (which you may use *only in tests and in your report*, never inside your package), then turn the fitted tree into plain-language rules and check that those rules route plots exactly as the model does.

You will also investigate two behaviours that every practitioner meets. First, a deep tree memorises the training plots, so you will run a depth sweep and find where validation accuracy peaks. Second, greedy splitting looks at one feature at a time, so it struggles when disease depends on an *interaction* (the XOR problem). You will demonstrate that and explain it.

> **Why this matters beyond this task.** Random forests and gradient boosting, which dominate tabular ML, are built from exactly this component. If you understand how a single tree decides, the ensembles stop being a black box.

**Facts you can rely on.**

- Features are continuous. Labels are integers: 0 healthy, 1 CMD, 2 CBB.
- Impurity is Gini: `1 − Σ pₖ²` over class proportions.
- A split sends `x[feature] <= threshold` to the left child. Candidate thresholds are midpoints between consecutive *distinct* sorted values of a feature.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Compute** Gini impurity and the gain of a split exactly, including weighted child impurity.
2. **Search** all splits of all features efficiently by sorting once per feature and updating class counts with cumulative sums.
3. **Build** a tree recursively with `max_depth` and `min_samples_leaf` stopping rules, and predict class labels and probabilities.
4. **Verify** a from-scratch model against a reference library on tie-free data, and explain any differences.
5. **Extract** human-readable rules and confirm they reproduce the model's predictions.
6. **Diagnose** overfitting with a depth sweep and explain why greedy splitting needs extra depth to solve XOR.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `treeforge` in [`starter/treeforge/`](starter/treeforge/). Signatures are fixed; internals are yours. You may not import `sklearn.tree` inside the package.

| ID | Requirement |
|---|---|
| **R1** | `gini(y) -> float`: Gini impurity of an integer label array (0.0 for an empty or pure array). |
| **R2** | `best_split(X, y, min_samples_leaf=1) -> (feature, threshold, gain) \| None`. Considers midpoints between consecutive distinct sorted values; both children must have at least `min_samples_leaf` samples; `gain = gini(parent) − weighted child Gini`. Returns `None` if no valid split exists (for example all features constant). Ties in gain (within `1e-12`) go to the lower feature index, then the lower threshold. Must handle `n = 20,000` and `d = 5` in under 2 seconds. A split with gain 0 is still returned if it is valid. |
| **R3** | `DecisionTree(max_depth=None, min_samples_leaf=1)` with `fit(X, y)`, `predict(X)`, `predict_proba(X)` (columns follow the sorted class labels), and attributes `depth_`, `n_leaves_`, `classes_`. A node is a leaf if it is pure, has fewer than 2 samples, is at `max_depth`, or has no valid split. Leaf prediction is the majority class, with the lowest label winning ties. |
| **R4** | `feature_importances_`: for each feature, the sum over its internal nodes of `n_node · gini_node − n_left · gini_left − n_right · gini_right`, divided by the total over all features (so the vector sums to 1; all zeros if the tree is a single leaf). |
| **R5** | `export_rules(tree, feature_names) -> list[str]`: one string per leaf, left-to-right, in the exact form `IF temp <= 3.2 AND ph > 5.5 THEN class=1`. Numbers use 4 significant digits (`"%.4g"`). A single-leaf tree gives `["IF TRUE THEN class=<c>"]`. |
| **R6** | `depth_sweep(X_train, y_train, X_val, y_val, depths) -> list[tuple[int, float, float]]` of `(depth, train_accuracy, val_accuracy)`. |

### D.2 Engineering requirements (mandatory)

- No Python loop over *samples* inside `best_split` (loops over features and recursion are fine).
- The builder must not mutate the caller's arrays.
- Provide at least **8 tests of your own** in `tests/test_member_*.py`, including degenerate cases (single class, single sample, constant feature, duplicated feature values).
- Provide `report_numbers.py` that regenerates every number in `REPORT.md`, including the depth sweep and the XOR experiment.

### D.3 Responsibility

The data is synthetic; no real farm is described. In the report, write one paragraph on what happens when a rule misdiagnoses CBB as CMD (the treatments differ) and why an officer should see the rule and its confidence, not only a label.

### D.4 Optional enhancements

- Entropy as an alternative criterion, with a measured difference.
- Cost-complexity pruning, with the pruned tree's validation accuracy.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_cassava(n, seed)` (five features, three classes) and `make_xor(n, seed)` (two features, two classes with an interaction) |
| **Provenance** | **Synthetic**, deterministic given the seed; features follow plausible agronomic ranges but no real farm is described |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes a 600-row CSV of about 40 KB |
| **Feature names** | `mosaic_score, whitefly_count, rain_mm, soil_ph, age_weeks` |

The official seed is 2026; hidden tests use other seeds, so hard-coded thresholds will fail.

**Setup**

```bash
cd assessments/ml-engineering/tier-1/units/ML-02-supervised-learning-and-ensembles/ML-T1-004-the-field-officers-decision-tree
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `treeforge/` package | The technical evidence |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Pins down behaviour on degenerate cases |
| 3 | `report_numbers.py` | Reproduces the depth sweep, XOR experiment and agreement figures |
| 4 | `REPORT.md` (at most 1,200 words), from the [template](submission-template/REPORT.md) | Explains the algorithm, the experiments and their limits; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `gini` and `best_split` are exact: on a hand-checkable five-row example the gain equals the value derived in the test; ties break as specified; constant features give `None`.
3. ⚙ **Agreement with scikit-learn.** With `criterion='gini'`, matching `max_depth` and `min_samples_leaf`, on continuous data with `max_depth` up to 5 (and `min_samples_leaf` 1 to 10) your tree has the same number of leaves and depth, and predicts identically on at least **99%** of 2,000 fresh samples; `feature_importances_` agree to `1e-9`. *Justification:* both are deterministic greedy CART with midpoint thresholds. Deeper trees contain many exact gain ties in tiny nodes, which scikit-learn breaks with a random feature order, so exact agreement is demanded only for shallow trees; your report should explain the difference you observe for an unrestricted tree.
4. ⚙ `best_split` handles `n = 20,000, d = 5` in under 2 seconds. *Justification:* a sort-and-cumulate search is O(n log n) per feature and takes about 0.1 s in numpy; an O(n²) search takes minutes.
5. ⚙ **XOR.** A depth-1 tree scores at most 0.60 on `make_xor`, and a depth-8 tree scores at least 0.95 on fresh data. *Justification:* with no first-order signal the early splits are driven by noise, so greedy trees need several levels (the reference needs depth 5), not the 2 that an ideal tree would use.
6. ⚙ **Rules.** The exported rules, parsed by the test, route every sample to the same class the tree predicts.
7. ⚙ **Depth sweep.** Train accuracy is non-decreasing in depth, and the deepest tree beats the shallowest on training data by at least 0.15 on the cassava data.
8. ✍ The report explains the observed optimal depth, why validation accuracy falls beyond it, and why greedy trees need far more than two levels on XOR.
9. ✍ `report_numbers.py` regenerates every number in the report.

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

1. **Create your own private repository** named `clbg-ML-T1-004-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `treeforge/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Entropy.** Add entropy as a criterion and compare trees on the same seeds.
2. **Instability.** Refit on 20 bootstrap samples, measure how often the root split changes, and relate it to bagging.
3. **Cost-complexity pruning.** Implement it and pick alpha by validation.
4. **Unequal costs.** Weight the CBB class more heavily and show how splits and rules change.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask you to compute the Gini gain of one split by hand on a five-row example; (2) ask why a threshold equal to a data value could misroute a sample; (3) give an unseen modification, for example entropy instead of Gini or a `min_impurity_decrease` stopping rule, and ask you to adapt your code live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python classes and recursion, numpy sorting and cumulative sums, class proportions. No optimisation theory. |
| **New skill developed** | Turning an algorithm described in words into an efficient, verified implementation, using a reference library as an oracle without copying it. |
| **Decisions the member must make** | How to organise the split search, how to represent nodes, how to stop, how to break ties, and how to turn the structure into rules. |
| **What must be investigated independently** | Where a depth-1 tree fails on XOR and how many levels greedy search really needs; where the validation optimum lies. |
| **Why it is interesting** | A model small enough to print on a card, built by hand, and checked against a library that millions use. |
| **Evidence of competence** | 99% agreement with scikit-learn on re-seeded data, exact importances, a timing bound, and rules that reproduce predictions. |
| **Misconceptions exposed** | 'Trees try every value as a threshold.' 'Deeper is better.' 'Greedy means optimal.' 'Importances are causal.' |
| **Preparation for later work** | Leads into bagging and boosting (ML-02 tiers 2 and 3) and ML-06 evaluation work. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
