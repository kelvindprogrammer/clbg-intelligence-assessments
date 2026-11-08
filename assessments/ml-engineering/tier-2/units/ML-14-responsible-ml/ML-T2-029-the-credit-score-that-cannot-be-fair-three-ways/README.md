# ML-T2-029: The Credit Score That Cannot Be Fair Three Ways: Fairness Metric Trade-offs and Mitigation in Micro-Lending

> *You can equalise missed good borrowers, approval rates or repayment precision between urban and rural traders. You cannot equalise all three. Choose, price it and defend it.*

![Format: Comparative (secondary: Investigation)](https://img.shields.io/badge/format-comparative-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T2-029` |
| **Title** | The Credit Score That Cannot Be Fair Three Ways: Fairness Metric Trade-offs and Mitigation in Micro-Lending |
| **Subtrack** | ML Engineering |
| **Tier** | 2: Applied Competence |
| **Unit** | [ML-14: Responsible ML (Fairness, Interpretability and Robustness)](../README.md) |
| **Format** | Comparative (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14-20 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Classifier evaluation and thresholds; numpy and scikit-learn. Recommended: ML-T1-024. |
| **Skills developed** | Fairness metrics; pre-processing and post-processing mitigation; constrained optimisation by search; trade-off analysis; ethical and legal justification |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Sabi Agents (fictional) offers micro-loans through agent-banking points. A trader is approved or declined by a score from a logistic regression. Repayment is the positive outcome (`y = 1`): approving a trader who repays earns 1 unit of interest, approving one who defaults loses 4. Traders are **urban (group 0)** or **rural (group 1)**. Rural traders repay a little less often on average, have less formal documentation (so the income-proof feature is noisier for them), fewer prior loans and live further from an agent.

A first model, group-blind and with a single profit-maximising threshold, approves creditworthy rural traders much less often than creditworthy urban traders: its true-positive rate is about 10 to 25 points lower for rural traders. The risk committee asks for a fairer system but has not said what 'fair' means. Several criteria are on the table:

- **equal opportunity**: creditworthy (repaying) traders should be approved at the same rate in both groups;
- **demographic parity**: approval rates should be equal;
- **equalized odds**: both approval rates among repayers and among defaulters should be equal;
- **predictive parity**: an approved trader should be equally likely to repay in either group.

You will implement the measures and two mitigations (pre-processing by **reweighing**, post-processing by **per-group thresholds** found by exhaustive search under a gap tolerance), then build a pipeline that chooses a scorer and thresholds on validation data. The brief is partly specified: the tests fix metrics, the search procedure and the acceptance bars; the model candidates, the criterion and tolerance you recommend, and the argument for them are yours.

Be prepared for the central result: when base rates differ and the scorer is imperfect, equalising error rates generally breaks predictive parity and calibration, and vice versa. The assessment asks you to show that on this data, to price each criterion, and to say which you would recommend and under what governance.

> **Why this matters beyond this task.** Fairness is a choice among incompatible criteria with costs, not a number to maximise. The professional skill is to make the trade-off explicit and to be honest about who bears it.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Compute** group fairness gaps correctly, including undefined cases.
2. **Implement** reweighing and prove it removes the group-label dependence in the training data.
3. **Search** per-group thresholds exhaustively under a gap constraint and reproduce the search independently.
4. **Quantify** the profit cost and the side effects (on other gaps) of each criterion across a range of tolerances.
5. **Explain** why the criteria conflict here, using the data's base rates and error rates.
6. **Defend** a recommendation, including whether the decision rule may depend on group and what must be reviewed by humans.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement [`fairlend`](starter/fairlend/). Use numpy and scikit-learn only. Group is `0` (urban) or `1` (rural); `y = 1` means repaid; approval means `score >= threshold`.

| ID | Requirement |
|---|---|
| **R1** | `fairness_report(y, pred, group) -> dict` with `rates` (`{0: {n, selection_rate, tpr, fpr, ppv}, 1: ...}`, `None` for undefined), and the gaps (group 1 minus group 0): `demographic_parity_diff` (selection rate), `equal_opportunity_diff` (TPR), `fpr_diff`, `predictive_parity_diff` (PPV), and `equalized_odds_gap = max(abs(tpr diff), abs(fpr diff))`. |
| **R2** | `reweighing_weights(y, group)`: weight of a row in cell `(g, y)` is `P(g) P(y) / P(g, y)`. |
| **R3** | `group_thresholds(score, y, group, criterion, tol, gain=1.0, loss=4.0, grid=51) -> (t0, t1, info)`. Candidate thresholds for group `k` are `np.unique(np.quantile(score[group == k], np.linspace(0, 1, grid)))`. Search all pairs; feasible pairs satisfy the criterion gap `<= tol` (`equal_opportunity`: abs TPR gap; `demographic_parity`: abs selection-rate gap; `equalized_odds`: the larger of abs TPR and FPR gaps); maximise `gain * TP - loss * FP` summed over both groups; ties go to the lower `t0`, then the lower `t1`. `info` has `profit` and `gap`. Raise `ValueError` if no pair is feasible. |
| **R4** | `tradeoff_curve(score, y, group, criterion, tols, ...) -> list[dict]` with `tol`, `t0`, `t1`, `profit`, `gap` for each feasible tolerance, in the order given. |
| **R5** | `select_and_mitigate(X_tr, y_tr, g_tr, X_va, y_va, g_va, criterion="equal_opportunity", tol=0.03, gain=1.0, loss=4.0) -> predictor`. The predictor has `predict(X, g)` returning 0/1 approvals, `chosen_` (name of the chosen scorer/mitigation), `thresholds_` (`(t0, t1)`) and `report_`, a dict with `baseline` and `mitigated` entries, each a `fairness_report` plus `profit`, both computed on the validation data. The baseline is a group-blind logistic regression with one profit-maximising threshold. You choose the candidate scorers and select among them on validation profit under the constraint. |

### D.2 Engineering requirements (mandatory)

- Deterministic, and no use of test data for fitting, selection or thresholds.
- The test set is used once, at the end, to report each criterion's gaps and profit.
- At least **10 tests of your own** in `tests/test_member_*.py`, including a reweighing independence test and a brute-force check of `group_thresholds` on a tiny case.
- `experiments.py` regenerates every number and figure in `REPORT.md` on at least **5 seeds**: baseline versus each criterion (equal opportunity, demographic parity, equalized odds), the trade-off curve over tolerances, the PPV gap each mitigation creates, and an ablation of reweighing versus thresholds alone.

### D.3 Responsibility

All data are synthetic. In the report, discuss: who is harmed by each criterion (creditworthy rural traders refused; urban traders cross-subsidising); whether an explicit group-dependent threshold is acceptable (it treats applicants differently by group; consider the law, the lender's duties and regulators, and what you would need to check; cite the **Nigeria Data Protection Act 2023** only for provisions you are sure of, such as its treatment of automated decisions and fairness of processing, and say when you are unsure) versus a group-blind mitigation such as reweighing; why `distance_to_agent_km` may be a proxy for rural status; and what a human credit committee must review before any mitigation is deployed.

### D.4 Optional enhancements

- Add a calibration-within-groups analysis and show formally that calibration and equal FPR/TPR cannot both hold here.
- Try a group-blind mitigation that does not use group at decision time (for example removing the proxy feature) and measure what it recovers.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/lendgen.py`](resources/lendgen.py): `make_lending(n=6000, seed=1)` returns `X, y, g, names` |
| **Provenance** | **Synthetic**, deterministic given the seed; fictional traders |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Features** | `income_proof, wallet_txn_volume, months_in_business, prior_loans, distance_to_agent_km, phone_age_months`; group is separate |
| **Recommended split** | rows 0 to 2999 train, 3000 to 4499 validation, 4500 to 5999 test (the public tests use this) |
| **Size** | Nothing is committed; `python resources/lendgen.py --out DIR --seed 1` writes a CSV of about 300 KB |

Hidden tests use other seeds, other criteria and tolerances, and a different gain-to-loss ratio.

**Setup**

```bash
cd assessments/ml-engineering/tier-2/units/ML-14-responsible-ml/ML-T2-029-the-credit-score-that-cannot-be-fair-three-ways
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `fairlend/` package | Metrics, reweighing, threshold search, trade-off curve and pipeline |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Includes independence and brute-force checks |
| 3 | `experiments.py` | Reproduces the multi-criterion comparison on 5 or more seeds |
| 4 | `REPORT.md` (at most 1,800 words plus tables), from the [template](submission-template/REPORT.md) | Recommendation to the risk committee; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `fairness_report`, `reweighing_weights`, `group_thresholds` and `tradeoff_curve` match hand and exhaustive computations, including other criteria and cost ratios in hidden tests.
3. ⚙ **Mitigation works out of sample.** On the public test split the baseline has an absolute TPR gap of at least **0.12**, your mitigated predictor at most **0.10**, and its profit is at least **85%** of the baseline's. On hidden seeds the mitigated gap is smaller than the baseline's and at most **0.14**, with profit at least 85%. *Justification:* the validation tolerance is 0.03, but with about 250 rural repayers in validation the gap's standard error is about 0.04, so the out-of-sample gap is bounded by sampling noise rather than by the tolerance; the reference reaches 0.05 and 0.02 to 0.11 with profit ratios of 0.92 to 1.02.
4. ⚙ The predictor's validation report shows the constraint satisfied (`abs(equal_opportunity_diff) <= tol`).
5. ✍ The report shows, for each criterion, the profit cost and the effect on the other gaps (especially PPV), explains why they conflict using the group base rates, and gives a recommendation with its conditions.
6. ✍ The report includes an ablation and uncertainty over seeds, and addresses D.3 including the group-at-decision-time question.

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

1. **Create your own private repository** named `clbg-ML-T2-029-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `fairlend/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Cost ratio sensitivity.** Vary the loss-to-gain ratio and show whether the preferred criterion changes.
2. **Intersectional groups.** Add a gender attribute to the generator in your own copy and show how the search degrades with small cells.
3. **Error-rate balance with noise.** Replace exact threshold search with a smoothed optimiser and compare.
4. **Monitoring.** Specify the fairness metrics you would monitor in production and their alarm rules.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask you to show on your data why equal opportunity and predictive parity cannot both be met; (2) ask what happens to your out-of-sample gap if validation had 100 rural repayers; (3) give an unseen modification, for example a loss-to-gain ratio of 10 or a regulator who forbids group-dependent thresholds, and ask what you change.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Classifier evaluation and thresholds. No prior fairness theory. |
| **New skill developed** | Turning an ethical requirement into a measurable constraint, pricing it, and being honest about incompatibility. |
| **Decisions the member must make** | Scorer candidates; criterion and tolerance; how to select on validation; whether to use group at decision time. |
| **What must be investigated independently** | Why out-of-sample gaps exceed the validation tolerance, and how PPV and calibration move when TPR is equalised. |
| **Why it is interesting** | The mitigation that fixes one gap visibly worsens another, and the cost can be nil or large depending on the criterion. |
| **Evidence of competence** | Exact agreement with exhaustive search, out-of-sample gap reduction on re-seeded data, a trade-off analysis and a defended recommendation. |
| **Misconceptions exposed** | 'Remove the protected attribute and the model is fair.' 'Fairness is one number.' 'A constraint met on validation is met in production.' |
| **Preparation for later work** | Leads into ML-14 Tier 3 (interpretability faithfulness and shortcut audits) and into model governance. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
