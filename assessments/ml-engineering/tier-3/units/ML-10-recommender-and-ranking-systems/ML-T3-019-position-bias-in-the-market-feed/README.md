# ML-T3-019: Position Bias in the Market Feed: Learning to Rank from Clicks Without Learning Where We Put Things

> *Listings at the top get clicked because they are at the top. A ranker trained on those clicks learns the old ranking's mistakes, and the vendors it buried stay buried.*

![Format: Open-ended (secondary: Investigation)](https://img.shields.io/badge/format-open-ended-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T3-019` |
| **Title** | Position Bias in the Market Feed: Learning to Rank from Clicks Without Learning Where We Put Things |
| **Subtrack** | ML Engineering |
| **Tier** | 3: Advanced Synthesis |
| **Unit** | [ML-10: Recommender and Ranking Systems](../README.md) |
| **Format** | Open-ended (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 4 · Research 4 · Engineering 3 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 24-34 hours over 3-4 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 2 minutes |
| **Recommended prerequisites** | Logistic regression, ranking metrics, importance weighting at an intuitive level. Recommended: ML-T1-020 and ML-T2-020 |
| **Skills developed** | Position-based click models; propensity estimation from randomised exploration; inverse-propensity estimation and training; bias-variance of clipping; exposure analysis and its trade-offs |
| **Technologies** | Python 3.10+, numpy and scikit-learn, pytest |

---

## B. Problem Statement

Gidan Kasuwa (fictional) is a Nigerian online marketplace where shoppers search for staples and household goods and see eight vendor listings in a ranked list. The current ranker, trained years ago, scores listings on four signals (quality, rating, distance, delivery speed) but also carries a legacy penalty on **small vendors**, whose listings are regularly placed at positions five to eight. A shopper examines lower positions less often, so the click-through rate there is low, and the team has just trained a new click model on the log. It ranks small vendors even lower. Several small vendors have complained; the team suspects the model has learned its own history.

You have a log of 8,000 queries with eight displayed listings each, the clicks, and a **randomised slice**: 10% of queries were shown in uniformly random order as an exploration experiment. In the generator's click model, a shopper clicks a listing with probability *examination(position) × relevance*, and relevance depends on the four signals and, unfavourably to the legacy ranker, positively on being a small vendor. You do not know any of this; the tests do.

Your task is to build a ranker that learns relevance and not position. You will estimate the examination curve from the randomised slice, build an inverse-propensity estimator that scores a ranking policy that was never run, train a debiased ranker, and analyse the exposure consequences for small vendors. This is research-grade and open-ended: the tests fix function interfaces and bars on estimation error, ranker quality and exposure, and the report must justify estimator choices (clipping, self-normalisation, which rows to train on), show ablations, test the assumptions the whole approach rests on, and say what raising small-vendor exposure costs and whom it affects.

> **Why this matters beyond this task.** Any system that learns from the clicks it generated feeds on its own placement choices. Counterfactual estimation from small randomised experiments is how marketplaces, feeds and search engines break that loop, and the trade-offs it exposes (variance, fairness, who pays) are those of real deployments.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Estimate** a position-bias (examination) curve from randomised exposure data.
2. **Compute** an inverse-propensity estimate of the value of a ranking policy that was never deployed, and judge its accuracy.
3. **Train** a ranker that is robust to position bias and compare it with a naive click model and with the logging policy.
4. **Analyse** the bias-variance trade-off of weight clipping and other estimator choices with ablations.
5. **Measure** exposure for a vendor group and state the cost and the beneficiaries of changing it.
6. **Test** the assumptions behind the approach, and design a monitoring plan for the feedback loop.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `feedrank` in [`starter/feedrank/`](starter/feedrank/). Interfaces are fixed; the estimator variants, model class, clipping and training rows are yours. Use only numpy and scikit-learn.

| ID | Requirement |
|---|---|
| **R1** | `estimate_exam(pos, click, randomized, K) -> (K,) array`: examination relative to position 0, from the randomised rows only, so that `exam[0] == 1`. On the official data the maximum error against the generator's curve must be at most 0.10. |
| **R2** | `rank_within_queries(qid, score) -> int array`: the 0-based rank of each row inside its query, by descending score, ties to the lower row index. |
| **R3** | `ips_value(qid, pos, click, exam, new_rank, clip=10.0) -> float`: estimated mean clicks per query if each listing were shown at `new_rank`, summing `click * min(exam[new_rank] / exam[pos], clip)` over rows and dividing by the number of queries. |
| **R4** | `fit_ranker(X, pos, click, exam, clip=10.0) -> ranker` with `score(X)` (higher is better); how position bias enters training is your decision. Position itself is not available at scoring time. |
| **R5** | `exposure_share(qid, rank, group, exam) -> float`: the mean over queries of the share of total examination mass (`exam[rank]`) that goes to rows with `group == 1`. |

### D.2 Engineering requirements (mandatory)

- Deterministic: explicit seeds and no hidden randomness.
- Nothing in estimation, training, selection or tuning may use `true_relevance` or `TRUE_EXAM` from the generator; they exist only to score. Using them is an integrity breach.
- All variants run through one harness on the same held-out log.
- Report results over at least 5 seeds with spread.
- At least **10 tests of your own** in `tests/test_member_*.py`, including a test of `ips_value` on a hand-built log, a test that scoring is independent of the logged position, and a test of the estimator on a log with no position bias.
- `experiments.py` regenerates every number and figure in `REPORT.md`, including exploration-slice sizes of 2%, 5%, 10% and 20%, clipping levels, a self-normalised variant, and a fairness/relevance trade-off curve.

### D.3 Responsibility

The data is synthetic. In the report, discuss who is helped and who is harmed when exposure moves toward small vendors (shoppers with a slightly lower expected quality or longer delivery on average; large vendors who lose revenue), who should decide the target share, and how you would monitor the marketplace for a feedback loop that re-buries the vendors you uplifted. State what you would disclose to vendors.

### D.4 Optional enhancements

- A pairwise (RankNet-style) debiased ranker using scikit-learn components.
- A doubly robust estimator that combines a click model with IPS.
- A policy that guarantees each group a minimum exposure share and the click cost of that guarantee.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_logs(n_queries=8000, seed=2026, random_frac=0.10)` returns a dict with `qid, pos, X, click, randomized` (8 rows per query); `true_relevance` and `TRUE_EXAM` give the generator's truth, for scoring only |
| **Provenance** | **Synthetic**, deterministic given the seed; no real person, transaction, market or institution |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Contents** | X holds four listing signals and a small-vendor flag; the legacy ranker penalises small vendors; clicks follow examination times relevance with a power-law examination curve |
| **Split used by the tests** | Train on a 8,000-query log; the tests score on an independent 3,000-query log from another seed using the generator's true relevance |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes a CSV of about 4 MB (64,000 rows); nothing is committed |

Hidden tests use other seeds, a thinner exploration slice (4%) and four seeds pooled.

**Setup**

```bash
cd assessments/ml-engineering/tier-3/units/ML-10-recommender-and-ranking-systems/ML-T3-019-position-bias-in-the-market-feed
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `feedrank/` package | Propensity estimation, off-policy value, debiased ranking and exposure |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Hand-built IPS, position-independence and no-bias tests |
| 3 | `experiments.py` | Reproduces every table and figure in the report |
| 4 | `REPORT.md` (at most 2500 words plus tables), from the [template](submission-template/REPORT.md) | Research report with ablations, assumption tests and a recommendation on exposure; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `estimate_exam` matches the hand case and is within 0.10 of the truth on the official data; `rank_within_queries`, `ips_value` and `exposure_share` match hand-computed values, including clipping.
3. ⚙ **Off-policy accuracy.** The IPS estimate of the value of the best-possible ordering (a policy never run) is within 8% of the truth, and the truth is at least 1.3 times the logged click rate. *Justification:* the reference is within 1% on seed 2026 and within 6% on the others; at 8% the bar tolerates a noisy examination estimate but not a missing correction.
4. ⚙ **Ranker quality.** On the independent log the debiased ranker's expected clicks per query exceed the logging policy's by at least 0.15 and a naive click-trained logistic model's by at least 0.008. *Justification:* the reference gives about 0.83 against 0.61 for the logging policy and 0.81 for the naive model, with an optimum of about 0.87; the gap to the naive model is small by construction because that model is simple and well specified, and is consistent over seeds (0.01 to 0.02).
5. ⚙ **Exposure.** The ranker's small-vendor exposure share is at least 1.4 times the logging policy's (reference about 1.8).
6. ⚙ **Robustness** (hidden): four unseen seeds pooled, mean examination error at most 0.15, mean IPS error at most 8% with none above 12%, and a 4% exploration slice still yields a usable curve.
7. ✍ The report includes the ablations, the assumption tests, the exploration-slice analysis, the exposure/relevance trade-off with a stated cost, and a monitoring plan.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 15 |
| Implementation quality | 10 |
| Methodology and evidence | 20 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 20 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T3-019-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `feedrank/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `experiments.py`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Trust bias.** Add a trust-bias term to your own simulator and see how far the estimator drifts.
2. **Variance control.** Build a bootstrap interval for the IPS estimate and check its coverage.
3. **Online learning.** Simulate three rounds of retraining on the new ranker's clicks and track the small-vendor share.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why a randomised slice of only 10% can fix the bias in the other 90%; (2) ask what breaks if shoppers click top positions more than their relevance warrants; (3) give an unseen change, for example a logging policy that is deterministic and never explores, and ask which of your components can no longer be estimated.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Logistic regression, ranking metrics, the idea of reweighting. No off-policy theory; the report derives what it needs. |
| **New skill developed** | Separating what was shown from what was wanted: counterfactual reasoning about ranking policies from logged, biased data. |
| **Decisions the member must make** | Which rows estimate the examination curve, how to clip and normalise, which model class, how to define and trade off exposure, how to test assumptions. |
| **What must be investigated independently** | How the logging policy created the bias, why the naive model's gap is small yet its exposure outcome is not, and when IPS fails. |
| **Why it is interesting** | Clicks mostly record where listings were put; a small randomised slice recovers the truth, and the fairness outcome follows from the same correction. |
| **Evidence of competence** | Estimation error, off-policy accuracy, ranker and exposure bars on unseen seeds; ablations and assumption tests in the report. |
| **Misconceptions exposed** | 'More clicks means more relevant.' 'A random slice is wasted traffic.' 'Debiasing and fairness are the same thing.' |
| **Preparation for later work** | Leads into experimentation, bandits and responsible-ranking work. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
