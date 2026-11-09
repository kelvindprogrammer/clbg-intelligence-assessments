# ML-T3-009: The Leaderboard That Flatters

> *41 teams, 1,156 submissions, one small public test set. How much of the top score is luck?*

![Format: Investigation](https://img.shields.io/badge/format-investigation-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-009` |
| **Title** | The Leaderboard That Flatters: Winner's Curse and Valid Selection in a Fraud Hackathon |
| **Subtrack** | ML Engineering |
| **Tier** | 3: Advanced Practice and Research Readiness |
| **Unit** | [ML-05: Evaluation, Validation and Model Selection](../README.md) |
| **Format** | Investigation |
| **Difficulty** | Technical 4 · Mathematical 4 · Research 4 · Engineering 3 · Ambiguity 4 · Resources 2 (each out of 5) |
| **Estimated time** | 24–36 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | AUC and its sampling variability, cross-validation with hyperparameter search, bootstrap, power calculations; ML-T2-009 is helpful. |
| **Skills developed** | Selection-bias analysis; nested validation; paired model comparison; sample-size planning; empirical-Bayes shrinkage; argued evaluation design |
| **Technologies** | Python 3.10+, numpy, scipy, scikit-learn, pandas, pytest |

---

## B. Problem Statement

**SabiFraud** is a (fictional) national hackathon run by a Nigerian payments-industry body to find the best model for flagging fraudulent POS-agent transactions. **41 teams** made **1,156 submissions** against a *public* leaderboard computed on only **1,200 held-out transactions with 96 frauds**. The organisers hold a larger *private* set of 3,600 transactions with 288 frauds. The prize, and a place on a bank's fraud-model shortlist, goes to whoever ranks first on the private set; but a sponsor has already circulated a press release naming the public leaderboard's top team and quoting its AUC of 0.921.

The organisers' evaluation lead sends you three questions and a deadline, and she does not say how to answer them.

1. **How much of the public leaderboard's top score is real?** What should the sponsor have quoted instead, and what range of private scores is plausible for the top ten teams?
2. **How should the private phase be run so that the winner is trustworthy?** A single private score per team is the default, but ties and near-ties are expected. Decide the protocol: how many private evaluations per team, how to declare a winner or a tie, and how large the private set must be to separate teams a point or two of AUC apart.
3. **How should a bank's data scientist, with 2,000 labelled transactions and a grid of 24 model configurations, report an honest AUC?** Show what goes wrong with the usual approach on an extreme case (pure noise labels) and on the provided data.

You will implement a small statistical toolkit and use it to write a defended methodology memo. There is no single correct protocol: the marking guide judges your *reasoning, experiments and stated trade-offs*, and the code is checked against fixed statistical behaviour. The real private scores of the hackathon are withheld; assessors compare your leaderboard shrinkage to them on freshly generated hackathons.

## C. Objectives

When you finish, you should be able to show that you can:

- Explain the winner's curse and measure its size by Monte Carlo for a given number of candidates and evaluation-set size.
- Implement nested cross-validation correctly and demonstrate on noise labels how a non-nested procedure produces a flattering AUC.
- Compare two scoring models with a paired bootstrap, and plan an evaluation-set size for a target effect with stated power.
- Shrink noisy leaderboard scores with an empirical-Bayes argument and state its assumptions.
- Design an evaluation protocol for the private phase, and defend it against at least three objections (cost, gaming, fairness to late entrants).
- Run ablations and report which conclusions are robust and which depend on assumptions about the generating process.

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `leaderboard_audit` package in [`starter/leaderboard_audit/`](starter/leaderboard_audit/). Signatures are fixed; `numpy`, `scipy`, `pandas` and `scikit-learn` are allowed. The six functions are the *toolkit*; the experiments and memo are the *assessment*.

| ID | Requirement |
|---|---|
| **R1** | `auc_se_hanley(auc, n_pos, n_neg)`: the Hanley-McNeil standard error of an AUC. |
| **R2** | `winner_inflation(n_candidates, n_pos, n_neg, true_auc, n_sims=1000, seed=0)`: Monte Carlo mean of (best observed AUC among `n_candidates` equally skilled, independent candidates on shared evaluation labels) minus `true_auc`. |
| **R3** | `nested_cv_auc(X, y, configs, make_model, outer_k=5, inner_k=3, seed=0)`: returns `outer_auc`, `chosen`, `nested_mean`, `naive_best_cv_auc`, `naive_best_idx`. Configuration choice in an outer fold may use only that fold's training rows. |
| **R4** | `paired_bootstrap_auc_diff(y, s_a, s_b, n_boot=1000, seed=0)`: `(AUC(a) - AUC(b), lo, hi)`, 95% percentile interval, rows resampled jointly. |
| **R5** | `required_n(delta_auc, auc_ref, pos_rate, corr=0.0, alpha=0.05, power=0.8)`: smallest total evaluation-set size at which the difference is detectable, using Hanley SEs and the correlation between the two AUC estimates. |
| **R6** | `shrink_public_scores(public, n_pos, n_neg, n_submissions=None)`: shrinks team-level public AUCs towards the field using their sampling noise. |
| **R7** | `experiments/` (scripts) and `REPORT.md` that answer the three questions in §B with: (a) the winner's-curse size for the actual leaderboard and a sensitivity analysis to correlated submissions; (b) nested-versus-naive on noise labels and on `dev.csv`; (c) your private-phase protocol with sample-size justification; (d) at least **three ablations** you design (for example: effect of number of configs on the nested-versus-naive gap; independent versus correlated candidates; shrinkage with and without per-team submission counts) and a statement of what each shows. |

### D.2 Engineering requirements (mandatory)

- Deterministic with fixed seeds. Every figure and number in `REPORT.md` is regenerated by `experiments/run_all.py` in under 20 minutes on a laptop CPU.
- Keep the provided tests passing and add **at least 8 tests of your own** (statistical properties are acceptable, for example monotonicity or coverage on simulated data).
- No peeking: nothing you choose may depend on the withheld private scores, and none of your shrinkage code may use them.
- Seeds, library versions and assumptions are recorded in `REPORT.md`.

### D.3 Privacy and responsibility

The data is **synthetic**; no real transaction or agent is described. Fraud labels about named agents or customers can cause real harm: your protocol memo must say how a false flag would be handled (human review, appeal route) under the Nigeria Data Protection Act 2023 principles of accuracy and fairness, and that a leaderboard score is not evidence about any individual.

---

## E. Dataset and Resources

All data is **synthetic**, from a deterministic generator held in the assessor kit.

| File | Content |
|---|---|
| [`resources/data/dev.csv`](resources/data/dev.csv) | 2,000 labelled POS-agent transactions (about 7.5% fraud): amount, hour, agent age, 7-day reversal rate, 24h counts, two pure-noise columns, `is_fraud`. 76 KB. |
| [`resources/data/leaderboard.csv`](resources/data/leaderboard.csv) | 1,156 submissions: `team_id, submission_no, public_auc`, scored on a public set with 96 frauds and 1,104 non-frauds. 16 KB. |

The private-set sizes are 288 frauds and 3,312 non-frauds. Licence: CC BY 4.0. Submissions inside a team are variants of one idea, so their public scores share luck; teams are not interchangeable draws.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `leaderboard_audit/` (completed starter) | The statistical toolkit |
| 2 | `experiments/` with `run_all.py` | Reproducible evidence for every claim |
| 3 | `tests/test_member_*.py` (at least 8 tests) | Statistical sanity tests of your own |
| 4 | `REPORT.md` (at most 2,500 words plus tables and figures), from the [template](submission-template/REPORT.md) | Methodology memo to the organisers; includes the AI-use declaration |
| 5 | A 10-minute live defence | Probes the design choices and the ablations (§K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Criteria marked ⚙ are checked automatically by the public and hidden test suites; the rest are checked by hand.

1. ⚙ Public and your own tests pass from a clean environment.
2. ⚙ Hidden test, five freshly generated hackathons (41 teams each): the mean absolute error of your shrunken scores against the **private** AUCs of the ten teams ranked highest on the public board is **below 85% of the raw public error**. *Justification:* the reference reaches 40-70% on comparable seeds; 85% requires genuine shrinkage but tolerates a simpler estimator.
3. ⚙ On pure-noise labels, your nested mean AUC is within 0.09 of 0.5 and the naive best-of-24 score exceeds it by more than 0.03. *Justification:* with 24 configs and about 36 positives, selection adds roughly 0.05-0.10 to the naive score in the reference.
4. ⚙ `winner_inflation` for 40 candidates on (96, 1104) lies between 1.3 and 2.1 standard errors; `required_n` is consistent with Hanley SEs and the power target.
5. ✍ The report estimates the leaderboard winner's expected private AUC with an interval, and says whether the press-release figure is defensible.
6. ✍ The private-phase protocol is explicit on set size, tie rules and what happens if the top two teams are statistically indistinguishable, with the trade-off (cost, speed, fairness) argued, not asserted.
7. ✍ At least three designed ablations, each with a stated hypothesis and a conclusion, and at least one result that did not go the way you expected, honestly reported.
8. ✍ Every number regenerates from `experiments/run_all.py`.

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

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T3-009-<your-github-username>` from this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `leaderboard_audit/` (your package), `tests/` (provided tests plus your own `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `experiments/` (scripts that produce every figure and table), `REPORT.md` (from the template, including the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core requirements.

1. Replace independent-candidate simulation with a model in which submissions within a team are correlated, estimate the correlation from `leaderboard.csv`, and show how the inflation changes.
2. Implement a "reusable holdout" mechanism (for example a thresholded or noisy answer to leaderboard queries) and measure how it limits adaptive overfitting.
3. Derive when a ranking by shrunken score differs from a ranking by raw score, and quantify how often that changes the prize winner.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn (explain a concept, review your code). **They may not do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: tool, purpose, example prompt, how you verified the output. Undisclosed use that emerges at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code or method adapted from documentation or papers, with a link.
- **Collaboration:** discuss *general techniques* only. Do not share code, numbers or report text.
- **Verification of understanding.** In the short defence the assessor will give you a new setting (for example 10 teams, 20 submissions each, a public set of 5,000 rows) and ask you to estimate the inflation and the required private-set size within the interview, justify one ablation you chose, and explain a result in your report you would not rely on.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | AUC, cross-validation, hyperparameter search, bootstrap and the basic idea of power. |
| **New skill developed** | Reasoning about how selection from many candidates biases the winner's score, and building evaluation procedures that stay honest under that selection. |
| **Decisions the member must make** | Which simulation model is realistic, how to handle correlated submissions, the private-phase protocol and its size, what shrinkage assumes, and which ablations are informative. |
| **What must be investigated independently** | How large the leaderboard bias really is, whether the data supports a within-team correlation, and when the public score tells you anything at all. |
| **Why it's interesting** | A press release has already been issued on a number that this assessment shows is probably inflated by about two standard errors. |
| **Evidence of competence** | Shrinkage beating raw scores against withheld private truth on fresh hackathons, a leak-free nested procedure on noise, and a memo whose claims all regenerate. |
| **Misconceptions exposed** | "The top of the leaderboard is the best model." "CV score of the best config is an unbiased estimate." "More submissions cannot hurt." "A bigger private set always fixes ties." |
| **Preparation for later work** | Leads into research-grade evaluation work in ML-T3 units, MLOps experiment tracking (ML-11) and responsible-AI evaluation design. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
