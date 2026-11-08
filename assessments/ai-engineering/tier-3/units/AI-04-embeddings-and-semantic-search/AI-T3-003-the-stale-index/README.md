# AI-T3-003: The Stale Index: Approximate Nearest-Neighbour Search for a Marketplace Whose Catalogue Keeps Moving

> *A marketplace search index was built in January and nobody rebuilt it. Build the index yourself, find out who it fails, decide when to rebuild, and defend a recall-versus-cost policy that includes the customers your average hides.*

![Format: Investigation (secondary: System-design)](https://img.shields.io/badge/format-investigation-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T3-003` |
| **Title** | The Stale Index: Approximate Nearest-Neighbour Search for a Marketplace Whose Catalogue Keeps Moving |
| **Subtrack** | AI Engineering |
| **Tier** | 3: Advanced Engineering, Research and System Design |
| **Unit** | [AI-04: Embeddings and Semantic Search](../README.md) |
| **Format** | Investigation (secondary: System-design) |
| **Difficulty** | Technical 4 · Mathematical 3 · Research 4 · Engineering 3 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 26–36 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. Full test run under 2 minutes |
| **Recommended prerequisites** | k-means, nearest-neighbour search, recall@k. Recommended: AI-T2-006 |
| **Skills developed** | Building an IVF approximate nearest-neighbour index from scratch; counting search cost with a hardware-independent proxy; segment-wise recall analysis; detecting distribution drift in an embedding index; calibrating a rebuild policy against a defined harm; stating threats to validity of a synthetic study |
| **Technologies** | Python 3.10+, numpy, pytest |

---

## B. Problem Statement

*Soko Market* (fictional) is a Nigerian online marketplace with 5,000 listed products in the study world, embedded as unit vectors. Search returns the 10 products nearest to the query by dot product. An exact scan over everything was fine at launch and is now too slow at peak, so an engineer built an approximate **inverted-file (IVF) index** in January: k-means partitions the catalogue into lists and a query scans only the few lists nearest to it. Average recall looked excellent in the load test. Since then:

- **New products arrive daily** and are appended to the lists of the nearest existing centroid; the index has never been retrained. In March a wave of products in categories that did not exist in January (new phone accessories, solar kits) arrived.
- **Customers complain unevenly.** Shoppers looking for niche or noisily described items, the **tail**, report that search "does not find anything", while head-category queries are fine. The load test used head-heavy traffic.
- The data-protection and cost teams want a clear **rebuild policy**: rebuilding is expensive and disruptive, but a stale index silently loses sales.

You will implement the index from scratch with numpy, using a hardware-independent cost proxy (the number of vector-distance computations per query), and conduct a study that answers: how much recall must we pay for under a cost budget; who is failed by the average; how fast the index decays with drift; which unlabelled signal tells us when to rebuild; and how much of this would carry over to a real catalogue.

The synthetic generator (`resources/catalogue.py`) plants cluster structure with skewed cluster sizes, a quarter of clusters designated tail with noisier queries, and drift parameterised by a strength: with that probability a new item comes from a new category, and the old categories also move. The brief does not give the answers: you must design the evaluation set (including how head and tail queries are weighted), decide how to define harm, calibrate your policy on worlds you generate, and argue where the generator flatters or misleads.

> **Why this matters beyond this task.** Approximate indexes are everywhere in retrieval and RAG, and they decay silently as data changes. Teams that cannot say who the index fails, or when to rebuild, discover the problem from customers.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** deterministic k-means and an inverted-file index whose search reports an exact distance-computation count.
2. **Measure** the recall-versus-cost frontier and choose the number of lists and probes under a stated budget.
3. **Decompose** recall by query segment and explain why the average hides who is failed.
4. **Show** how appending new items without retraining degrades recall, and which unlabelled signals reveal it.
5. **Design** a rebuild policy, calibrate it on worlds you generate against a stated definition of harm, and test it on worlds you did not.
6. **State** the validity limits of the synthetic study and how real data would change the conclusions.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `annlab` package in [`starter/annlab/core.py`](starter/annlab/core.py). Use only numpy and the standard library; no faiss or scikit-learn. Vectors are unit length and the score is the dot product.

| ID | Requirement |
|---|---|
| **R1** | `kmeans(X, k, seed, iters)`: deterministic Lloyd's algorithm. Same seed gives the same centroids; emptied clusters are re-seeded; `k` larger than the number of distinct points does not crash or produce NaN. |
| **R2** | `exact_search(X, q, k)` (ties to the lower id) and `recall_at_k(found, truth)` (mean of `|found ∩ truth| / |truth|`). |
| **R3** | `IVFIndex(n_lists, seed)` with `build(X)`, `add(X_new)` (no retraining; ids continue; returns the new ids), `list_sizes()`, `search(q, k, nprobe) -> (ids, ndist)` and the attribute `build_qerr` (mean Euclidean distance from build vectors to their centroid). Probing order and ranking ties are by lower id. `ndist` is `n_lists` plus the number of vectors scanned. With `nprobe = n_lists` the result equals exact search. |
| **R4** | `evaluate_index(index, Q, k, nprobe, truth=None) -> (mean recall, mean ndist)` against exact search over `index.X`; `segment_recall(index, Q, segments, k, nprobe)` returns recall per segment label. |
| **R5** | `choose_config(X, Q, k, budget_ndist, n_lists_grid, nprobe_grid, seed)` returns the `(n_lists, nprobe)` with the highest mean recall whose mean `ndist` is within the budget, or `None`. |
| **R6** | `drift_report(index, X_new)` (must include `qerr_ratio` and `imbalance`) and `should_rebuild(report)`. **Harm is defined by the assessors**: rebuild is needed when recall@10 at `nprobe = 4` of the stale index (new vectors appended without retraining) is at least **0.05 below** that of an index rebuilt on all vectors. Your policy may use any unlabelled signals; justify thresholds with a calibration experiment on your own worlds. |

**The study (hand-assessed, and the larger share of the marks).** The report must contain: (a) the evaluation-set design (query counts, head/tail mix, `k`, and why); (b) the recall-versus-`ndist` frontier for at least four `n_lists` values and a justified choice at a budget of your own, with uncertainty; (c) head versus tail recall and an explanation of the gap from the geometry, not only the numbers; (d) the decay curve of recall against drift strength for a stale index, with the rebuilt index as reference; (e) your rebuild policy, its calibration on worlds not used for the hidden tests, its precision and recall as a classifier of the harm definition, and its cost (an unneeded rebuild versus a missed one); (f) at least three sensitivity analyses (for example catalogue size, noise level `sigma`, `k`, dimension, `nprobe` for the harm definition); (g) a threats-to-validity section on what the generator makes too easy or too hard, why `ndist` is only a proxy for latency, and what you would measure on a real index.

### D.2 Engineering requirements (mandatory)

- Deterministic: every random choice is seeded. No network, no downloads.
- The public tests run in about half a minute; your own experiments may take longer but `experiments.py` must finish within 15 minutes on a laptop.
- At least **12 tests of your own** in `tests/test_member_*.py`, including a partition invariant (every id in exactly one list after `build` and after `add`) and a cost-accounting test.
- `experiments.py` regenerates every table and figure in `REPORT.md`.

### D.3 Responsibility

Product search can steer customers and sellers: a tail-blind index is a fairness problem for sellers of niche goods and for shoppers whose phrasing differs from the majority's. In the report, discuss who bears the cost of a low tail recall, how you would monitor it in production without labels, and what the Nigeria Data Protection Act 2023 implies if query logs are used to build the evaluation set (retention, minimisation, consent). The data here is synthetic.

### D.4 Optional enhancements

- Add product quantisation to the lists and trade memory against recall.
- Add a second signal to the drift monitor (for example list-size shift) and test whether it improves the policy.
- Compare IVF with a locality-sensitive-hashing index at equal `ndist`.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Generator** | [`resources/catalogue.py`](resources/catalogue.py): `make_catalogue(seed, n=5000, d=32, n_clusters=40, sigma=0.30)`, `make_queries(world, n, seed)` returning vectors and `head`/`tail` labels, `queries_from_rows(X, n, seed)`, `make_drift(world, strength, m, seed)` |
| **Provenance** | **Synthetic and deterministic**; vectors only, no text, no real product or customer data. Nothing is committed beyond code |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Planted structure** | Zipf-skewed cluster sizes; the smallest quarter of clusters are the tail; tail queries carry double the noise; drift adds items from 8 new clusters with probability `strength` and moves old centres by `0.35 * strength` |
| **Cost proxy** | `ndist` = number of vector-distance computations per query. It ignores memory access and parallelism |

Hidden tests use other worlds (different sizes, cluster counts, noise), other drift strengths and seeds, and a differential oracle. Policies are judged against the stated harm definition; borderline cases within 0.02 of the 0.05 boundary are not scored.

**Setup**

```bash
cd assessments/ai-engineering/tier-3/units/AI-04-embeddings-and-semantic-search/AI-T3-003-the-stale-index
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `annlab/` package | k-means, IVF index, evaluation, configuration choice and drift policy |
| 2 | `tests/test_member_*.py` (at least 12 tests) | Includes the partition invariant and a cost-accounting test |
| 3 | `experiments.py` | Regenerates every table and figure |
| 4 | `REPORT.md`, at most 3,000 words plus tables and figures, from the [template](submission-template/REPORT.md) | The study (a) to (g) and the AI-use declaration |
| 5 | A 10-minute technical defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ Lists partition the collection after `build` and after `add`; `nprobe = n_lists` reproduces exact search; `ndist` equals `n_lists` plus the sizes of the probed lists (public and hidden tests).
3. ⚙ On the public world the index with 64 lists reaches recall@10 of at least 0.6 at 2 probes, 0.93 at 8 and 0.98 at 16; the head-tail gap at 2 probes exceeds 0.05. *Justification:* the reference reaches about 0.75, 0.97 and 0.995, with a head-tail gap of about 0.13.
4. ⚙ `choose_config` stays within the budget and within 0.03 (public) or 0.04 (hidden) recall of the best configuration in the grid.
5. ⚙ `should_rebuild` agrees with the harm definition on public worlds with no drift and strength 0.6 and 1.0, and on hidden worlds of other sizes and strengths 0, 0.05, 0.9 and 1.0.
6. ✍ The report meets items (a) to (g) in §D.1 with evidence, including the head-tail decomposition, the decay curve and the policy's classification quality on unseen worlds.
7. ✍ The report separates conclusions that should transfer to real catalogues (mechanisms, ordering of effects) from those that should not (absolute recall, thresholds), and proposes the real-world measurement that would settle each open question.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 12 |
| Technical correctness | 18 |
| Implementation quality | 10 |
| Methodology and evidence | 22 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 8 |
| Critical thinking and limitations | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-AI-T3-003-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `annlab/` (your package), `tests/` (provided tests plus your own), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Product quantisation.** Compress the vectors in the lists and measure recall against memory.
2. **Incremental retraining.** Re-train only the lists that drifted and compare cost to a full rebuild.
3. **Real embeddings.** Run the pipeline on embeddings from a small open-weight model of a public text collection and compare conclusions. Optional; the graded path is offline.
4. **Tail-aware probing.** Spend more probes on queries whose nearest centroids are far, and show the effect on the tail gap.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask you to explain, from the geometry of your clusters, why tail queries lose recall at the same number of probes; (2) ask which of your two error types (unneeded rebuild or missed rebuild) your policy prefers and why that is a business decision; (3) give an unseen modification, for example "the catalogue is ten times bigger" or "harm is defined at 0.02", and ask which parts of your recommendation change and which of your measurements you would redo first.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | K-means, nearest-neighbour search, recall. No index-library knowledge. |
| **New skill developed** | Treating an approximate index as a system that decays and fails some users more than others, and measuring that rigorously. |
| **Decisions the member must make** | Evaluation-set design; cost budget; definition of acceptable tail recall; which signals to monitor; calibration protocol. |
| **What must be investigated independently** | The tail gap and the drift decay, which the brief only reports as complaints. |
| **Why it is interesting** | The index can look healthy on average and on the load test while failing a whole population of shoppers, and the signal that exposes it is available without labels. |
| **Evidence of competence** | Exact accounting, near-optimal configuration choice, a policy that classifies harm correctly on unseen worlds, and a study that names its own limits. |
| **Misconceptions exposed** | 'Average recall is the quality of the index.' 'Approximate means slightly worse everywhere.' 'Rebuild on a schedule.' 'Synthetic results transfer unchanged.' |
| **Preparation for later work** | Leads into AI-05 RAG and knowledge-base maintenance, AI-13 production operations, ML-10 drift monitoring and AI-10 evaluation. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
