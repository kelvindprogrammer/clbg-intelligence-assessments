# ML-T3-025: When to Retrain the Harvest-Loan Model: Cost, Label Delay and Drift Regimes in a Retraining-Policy Study

> *Retraining is not free and labels arrive late. Decide when a lender should retrain, show when your answer stops being true, and say what the simulation cannot know.*

![Format: Open-Ended (secondary: Comparative)](https://img.shields.io/badge/format-open-ended-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-025` |
| **Title** | When to Retrain the Harvest-Loan Model: Cost, Label Delay and Drift Regimes in a Retraining-Policy Study |
| **Subtrack** | ML Engineering |
| **Tier** | 3: Advanced Practice |
| **Unit** | [ML-13: ML Pipelines, MLOps and Monitoring](../README.md) |
| **Format** | Open-Ended (secondary: Comparative) |
| **Difficulty** | Technical 4 · Mathematical 3 · Research 4 · Engineering 4 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 24-32 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 3 minutes |
| **Recommended prerequisites** | Strong grounding in supervised learning and evaluation; experience writing simulations. Recommended: ML-T2-026 and ML-T1-023. |
| **Skills developed** | Policy simulation; delayed-label monitoring; seasonal training-window design; minimax-regret recommendation; sensitivity analysis; validity argument |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

Kijibe Credit (fictional) lends seed and fertiliser loans to smallholder farmers in northern Nigeria. A logistic-regression model scores each loan application; **whether the borrower defaults is known only 12 weeks after the loan is scored**. Each retraining needs a data pull, a model-risk review and sign-off, which the lender prices at about the cost of **150 wrongly decided loans**. The head of credit risk asks one question:

> *When should we retrain the model, on what data, and how do we know?*

Three kinds of change have hurt lenders like this one, and you do not know which will happen next:

- a **shock**: an abrupt change in how farm and household features relate to repayment (a currency shock, a policy change), with the borrower population looking the same;
- **creep**: a slow rotation in the relationship, with the population itself drifting (inflation);
- a **seasonal cycle**: repayment behaviour that alternates with the farming calendar.

This is a research-style task and it is deliberately under-specified. You must build the instrument, design the candidate policies, run a fair study, and write a recommendation that survives the question 'what if your assumptions are wrong?'. You will:

1. implement a **simulator** that replays a stream week by week, hides labels that would not yet exist, lets a policy decide to retrain and choose its training weeks, and charges errors plus retraining costs;
2. design **at least five policies** (two baselines, 'never' and 'weekly', plus your own, for example periodic, covariate-drift-triggered, performance-triggered under delayed labels, season-aware, or a hybrid);
3. run a **study** over the three regimes and several seeds, compare policies on cost, regret and the trade-off between cost and number of retrains, and recommend one under uncertainty about the regime;
4. show how the recommendation **changes** with the retraining cost and the label delay, and where it stops being valid.

Nothing in the brief tells you which policy wins. A covariate-drift trigger cannot see a pure concept shock; a performance trigger sees it only after the delay; a naive retrain uses a window that mixes old and new behaviour; a recent-window rule is blind to the calendar. Finding and quantifying these is the assessment.

> **Why this matters beyond this task.** Retraining schedules are usually chosen by habit. A cost-aware, delay-aware study is how a team replaces habit with evidence, and how a reviewer decides whether to trust it.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Build** a simulator that provably cannot show a policy a label that would not yet exist, and that accounts for cost exactly.
2. **Design** retraining policies that differ in trigger (time, covariates, delayed performance, calendar) and in training-window rule.
3. **Explain** from first principles why each policy fails in at least one regime, then show it with data.
4. **Select** a policy under uncertainty about the regime with an explicit decision rule (minimax regret), and compare with alternatives such as average cost.
5. **Quantify** how the recommendation depends on retraining cost and label delay, and identify the break-even region.
6. **Argue** the validity of a synthetic study: what it can establish, what it cannot, and what real-world evidence would change the recommendation.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement [`retrainlab`](starter/retrainlab/). `base.py` provides `LabelNotYetAvailable`, `fit_model`, the `Policy` base class and the `Result` record. Use only numpy, scikit-learn and the standard library.

| ID | Requirement |
|---|---|
| **R1** | `simulate(policy, stream, cfg) -> Result`. `cfg` has `retrain_cost` (default 150.0) and `t0` (default 36). A stream is the dict from `regimes.make_regime`. Fit the initial model with `fit_model` on all weeks whose labels are known at week `t0` (weeks `0` to `t0 - delay`); it is not charged. For each week `t` from `t0` to the last week: build a **view** and call `policy.decide(t, view)`; if true, call `policy.train_weeks(t, view)`, fit a new model on exactly those weeks (raise `LabelNotYetAvailable` if any week is not yet labelled, `ValueError` or `LabelNotYetAvailable` if empty) and charge `retrain_cost`; then score week `t` with the current model (class 1 if probability at least 0.5) and count misclassified loans. The view exposes `t`, `delay`, `visible_weeks` (`0` to `t - delay`), `model`, `retrain_weeks`, `X(w)` for `w <= t` (else `ValueError`), `y(w)` for `w <= t - delay` (else `LabelNotYetAvailable`) and `error(w)`, the current model's misclassification rate on a visible week. `Result.total_cost = error_cost + retrain_cost_total`; `errors_by_week` has one entry per simulated week. |
| **R2** | `candidate_policies(cfg) -> dict[str, zero-argument factory]` with at least five entries including `"never"` and `"weekly"`; each factory returns a fresh `Policy`. At least one policy must use delayed labels and at least one must override `train_weeks`. |
| **R3** | `evaluate_policies(factories, streams, cfg) -> {name: {kind: mean total cost}}`, where `streams` is `{kind: [stream, ...]}`. |
| **R4** | `pareto_front(points)` returns the sorted indices of points not dominated by any other (a point is dominated if another is no worse in both coordinates and strictly better in one; both of two identical points are kept). Both coordinates are minimised. |
| **R5** | `recommend(table)` returns the name with the smallest **maximum regret** over regimes, where regret in a regime is the policy's cost minus the lowest cost among all policies in that regime. Ties go to the lower mean cost, then to the alphabetically first name. |
| **R6** | `sweep(factories, streams, cfg, param, values) -> {value: recommended name}` re-runs the study with `cfg[param] = value` and applies R5. |

### D.2 Engineering requirements (mandatory)

- Deterministic: fixed seeds, no wall-clock dependence. A policy may keep its own state but must not read `stream` directly or any global.
- Do not hard-code regime onsets or the 52-week period; a season-aware policy must infer or defend its calendar assumption from labelled data and say how.
- At least **12 tests of your own** in `tests/test_member_*.py`, including a leakage test (a policy that asks for an unlabelled week must fail), a cost-accounting test against an independent computation, and a test of `recommend` against brute force.
- `experiments.py` regenerates every number and figure in `REPORT.md`, using at least **5 seeds per regime**.
- The study must include at least: a regret table, a cost-versus-retrain-count Pareto plot, a sweep over `retrain_cost` (at least five values spanning 20 to 1,000) and over the label delay (at least 4, 12, 26 weeks), and an ablation of one design element of your best policy.

### D.3 Responsibility

The data are synthetic and fictional. In the report discuss, in at most 400 words: who bears the cost when a stale credit model misjudges loans (farmers wrongly refused or over-lent to), why the cost ratio in this study is itself an ethical choice and not a given, how an automated decision about credit relates to the **Nigeria Data Protection Act 2023** (cite only the provisions you are sure of, such as the Act's treatment of automated decision-making and the principle of accuracy, and flag any you are unsure of), and how retraining records (see ML-T1-023) support accountability. State what a human reviewer must sign off before a retrained model goes live.

### D.4 Optional enhancements

- Add a second model family (a depth-limited tree ensemble) and test whether the policy ranking depends on the family.
- Make the cost asymmetric (a missed default costs more than a wrongly refused loan) and show how the thresholded decision and the policy ranking move.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/regimes.py`](resources/regimes.py): `make_regime(kind, seed, weeks=130, n=200, delay=12)` with `kind` in `shock`, `creep`, `seasonal` returns a dict with `X (weeks, n, 8)`, `y (weeks, n)`, `delay` and `kind` |
| **Provenance** | **Synthetic**, deterministic given kind and seed; onset and weights depend on the seed; no real borrower or lender |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing is committed; `python resources/regimes.py --out DIR --seed 1` writes three CSVs of about 2 MB each |
| **Run time** | One simulation of 94 weeks takes about 0.1 to 3 seconds depending on the policy; the public acceptance test takes about 1 minute |

Hidden tests use other seeds (so other onsets and weights), other label delays (4 and 20 weeks), a different `t0` and different costs.

**What the generator does not tell you.** It does not say which features carry the change, when the shock occurs, or that the seasonal cycle has a 52-week period. The stream is the only evidence, as it would be for a real lender.

**Setup**

```bash
cd assessments/ml-engineering/tier-3/units/ML-13-ml-pipelines-mlops-and-monitoring/ML-T3-025-when-to-retrain-the-harvest-loan-model
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `retrainlab/` package | Simulator, policies, analysis functions |
| 2 | `tests/test_member_*.py` (at least 12 tests) | Leakage, accounting and recommendation tests |
| 3 | `experiments.py` | Reproduces every table and figure (5 or more seeds per regime) |
| 4 | `REPORT.md` (at most 3,000 words plus tables and figures), from the [template](submission-template/REPORT.md) | Policy study and recommendation for the head of credit risk; carries the AI-use declaration |
| 5 | A 10-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ **Simulator correctness.** `simulate` matches independent cost computations for `never`, scripted periodic and scripted fixed-week policies at other `t0` and label delays, gates every label by the delay, and rejects unlabelled or empty training weeks.
3. ⚙ **Decision rules.** `pareto_front`, `recommend` (minimax regret with the stated tie-breaks) and `sweep` match brute-force implementations on random tables.
4. ⚙ **Finding the structure.** On seed 1 (public) your best non-baseline policy costs at most **0.90** of `never` in the shock regime and at most **0.92** of `never` in the seasonal regime; on hidden seeds the means over two seeds are at most **0.92** and **0.94**. *Justification:* the reference reaches about 0.75 (a short-window performance trigger) and 0.83 (a season-aware rule), so the bars require finding the structure, not tuning noise; `weekly` is far worse than `never` at this cost, which is the point of charging for retraining.
5. ⚙ The recommended policy beats `weekly` in every regime.
6. ✍ The report states the decision rule and compares minimax regret with mean cost and with a rule you choose; shows the sweep over cost and delay and identifies where the recommendation changes; includes an ablation; reports uncertainty across seeds (paired differences, not just means).
7. ✍ The validity section lists at least four threats (single model family, synthetic regimes that match the policies, known-cost assumption, no covariate-label coupling beyond the generator, no feedback from decisions to data) and says which result would be most affected by each.
8. ✍ The report states what real evidence the lender should collect before acting on the recommendation.

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

1. **Create your own private repository** named `clbg-ML-T3-025-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `retrainlab/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Value of faster labels.** Reduce the delay with a proxy label (for example early repayment status) that is noisy but available after 4 weeks, and quantify when it pays.
2. **Learned trigger.** Train a small model that predicts, from monitoring signals, whether retraining will reduce next-8-week error, and compare with hand-written triggers.
3. **Feedback.** Let the model's decisions change which loans are written, so training data become selected, and re-run the study.
4. **Shadow deployment.** Design (but do not build) a shadow-run protocol that would let the lender learn the real cost ratio.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 10-minute defence the assessor will (1) ask you to show, in your simulator, the line that makes it impossible for a policy to see a label early; (2) pick a cell of your regret table and ask why that policy lost there, then ask what the table would look like with a label delay of 26 weeks; (3) give an unseen modification, for example a regime in which two shocks occur 20 weeks apart or retraining that costs 20 rather than 150, and ask which recommendation changes and why.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Supervised learning, drift concepts and cost-sensitive evaluation. No reinforcement learning or control theory is assumed. |
| **New skill developed** | Turning 'how often should we retrain?' into a measured, assumption-aware decision with a defensible rule. |
| **Decisions the member must make** | Simulator semantics; policy set; training-window rules; the decision rule across regimes; sweep ranges; how to present uncertainty and limits. |
| **What must be investigated independently** | Why covariate monitoring misses a concept shock, what delay does to performance monitoring, and how to find a seasonal period from labelled data. |
| **Why it is interesting** | The popular answers (schedule, drift alert) each lose somewhere, and the winner changes with cost and delay; the recommendation has a region of validity. |
| **Evidence of competence** | A leak-proof simulator, structure-finding policies that beat baselines on re-seeded streams, a sweep with a break-even analysis, and an honest validity section. |
| **Misconceptions exposed** | 'Retrain on a schedule.' 'Drift detection tells you when to retrain.' 'Use all the data you have.' 'The best policy is the same at every cost.' |
| **Preparation for later work** | Leads into research-grade work on continual learning, model governance and the economics of monitoring, and into ML-12 deployment practice. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
