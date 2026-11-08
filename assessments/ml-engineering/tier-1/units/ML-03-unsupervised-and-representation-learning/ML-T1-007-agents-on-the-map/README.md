# ML-T1-007: Agents on the Map

> *Build k-means and the silhouette score with nothing but numpy, then use them to decide how many agent hubs a state needs.*

![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T1-007` |
| **Title** | Agents on the Map: K-Means and Silhouette from Scratch for Mobile-Money Agent Siting |
| **Subtrack** | Machine Learning Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [ML-03: Unsupervised and Representation Learning](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 8-14 hours over 1-2 weeks |
| **Collaboration** | Individual |
| **Compute** | CPU only, 4 GB RAM, no GPU, no paid services, no internet after setup. The whole suite runs in about a minute |
| **Recommended prerequisites** | numpy array indexing and broadcasting; what a mean and a Euclidean distance are; running `pytest`. No prior clustering knowledge is assumed beyond the idea of grouping similar points. |
| **Skills developed** | Vectorised numerical programming; k-means++; Lloyd's algorithm; empty-cluster handling; silhouette analysis; validating against a reference implementation |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

A mobile-money operator in a Nigerian state wants to place a small number of **agent hubs**, each stocked with float and cash so that nearby field agents can rebalance without travelling to the state capital. Operations has plotted 600 locations where customer demand is concentrated (market clusters, motor parks, campuses) on a 120 km by 120 km grid. Nobody knows how many natural groupings of demand exist, and the operator will only pay for hubs it can justify.

Your job has two parts. First, build the clustering machinery yourself, because a team that cannot reproduce k-means cannot debug it when it misbehaves in production: k-means++ seeding, Lloyd's iterations with a defined repair for clusters that lose all their points, restarts that keep the best run, and the silhouette score. Second, use it on `demand_points.csv` to recommend a number of hubs and explain, in a short report, what your evidence does and does not show. This is a Tier 1 assessment: the specification is exact, your implementation is checked against scikit-learn and against hand-computed cases, and your reasoning is checked in the report and the defence.

---

## C. Objectives

When you finish, you should be able to show that you can:

- Implement k-means++ seeding and Lloyd's algorithm in vectorised numpy and explain why seeding changes the result.
- Handle degenerate cases deliberately: empty clusters, duplicate points, k equal to 1 and k equal to n.
- Implement the silhouette score from its definition and verify it against a reference library.
- Use restarts and an internal validity index to choose k, and state honestly what that choice assumes.
- Explain when k-means is the wrong tool (non-spherical groups, very unequal densities, no structure at all).

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the functions in `agentmap/core.py`. Each stub raises `NotImplementedError("R<n>: ...")`. Only numpy may be imported inside the package; scikit-learn is used by the tests as the reference.

| # | Requirement |
|---|---|
| R1 | `kmeans_pp_init(X, k, rng)`: the first centre is uniform over rows; each further centre is sampled with probability proportional to squared distance to the nearest centre already chosen. Return copies of rows of `X`. |
| R2 | `assign(X, centers)`: index of the nearest centre per row, ties to the lowest index, fully vectorised. |
| R3 | `update_centers(X, labels, centers)`: cluster means. A cluster with no points is re-seeded at the point farthest from its currently assigned old centre; several empty clusters take distinct points, farthest first. Inputs must not be modified. |
| R4 | `inertia(X, centers, labels)`: the sum of squared distances to assigned centres. |
| R5 | `kmeans(X, k, *, seed, n_init, max_iter, tol)`: n_init restarts of k-means++ then Lloyd; stop when the largest centre movement is below `tol` or at `max_iter`; keep the lowest-inertia run; deterministic for a given seed; `X` untouched. |
| R6 | `silhouette_scores(X, labels)`: per-sample silhouette from its definition; singleton clusters score 0. |
| R7 | `choose_k(X, k_range, seed)`: returns `(best_k, table)` with one `{k, inertia, silhouette}` row per k, best by mean silhouette. |

Then run your code on `demand_points.csv` for k from 2 to 9 and write the report described in section F.

### D.2 Engineering requirements (mandatory)

- `pytest` passes from a clean environment built from `requirements.txt`; the package imports no scikit-learn.
- No Python loop over data points inside `assign`, `inertia` or the centre update (loops over k or over restarts are fine). The silhouette may use a full pairwise distance matrix at this data size.
- Results depend only on the `seed` argument: no global random state, no reliance on dictionary or set ordering.
- At least 5 of your own tests in `tests/test_member_*.py`, including one degenerate case that you found yourself.

### D.3 Privacy and responsibility

The coordinates are synthetic and describe no real person or business. In a real deployment, demand locations derived from transaction records are personal data under the NDPA 2023 when they can be tied to a customer; aggregate to grid cells or agent-level counts before clustering and keep raw coordinates out of reports. State in your report which aggregation you would require before using this method on real data.

### D.4 Optional enhancements (not required for full marks)

- Compare your inertia curve with the silhouette curve and explain where they disagree.
- Add a `predict` method that assigns a new location to a hub and returns its distance in km.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/demand_points.csv`](resources/data/demand_points.csv): 600 rows with `point_id`, `x_km`, `y_km` (about 12 KB) |
| **Provenance** | **Synthetic**, generated with a fixed seed by a generator held in the assessor kit because it reveals the true number of groups. No real locations or people. |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Reference** | scikit-learn's `KMeans`, `pairwise_distances_argmin` and `silhouette_samples` are used by the tests only |
| **Setup** | `pip install -r starter/requirements.txt` (numpy, scikit-learn, pytest) |

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `agentmap/` package (completed starter) | Core technical evidence for R1-R7 |
| 2 | `tests/test_member_*.py` (at least 5 tests) | Shows you can pin behaviour and find edge cases |
| 3 | `analysis.py` that prints your k table and saves one plot | Reproducible evidence for the recommendation |
| 4 | `REPORT.md` (at most 700 words plus the table) from the [template](submission-template/REPORT.md) | Recommendation, evidence, limits and AI-use declaration |
| 5 | A 5-minute live defence | Verifies understanding (section K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion holds. Criteria marked (auto) are checked by the public and hidden test suites; the rest are checked by hand.

1. (auto) All public tests pass from a clean environment, and your own tests pass.
2. (auto) `kmeans` reaches inertia within 1% of scikit-learn's `KMeans(n_init=10)` on the public data. *Justification:* both are local-optimum heuristics; 1% allows legitimate restart variation but rejects a broken update step.
3. (auto) On hidden re-seeded data with a different number of groups, your clustering recovers the true grouping (adjusted Rand index above 0.95) and `choose_k` returns the true k. *Justification:* hidden groups are separated by at least 38 km against 2.5-5.5 km spread, so a correct implementation separates them essentially perfectly.
4. (auto) Silhouette values match scikit-learn to 1e-9, including singleton clusters; runs are deterministic for a fixed seed.
5. (auto) Degenerate inputs (duplicate points, k=n, k=1, several empty clusters) do not crash and behave as specified.
6. Your report recommends a k with the full table, says what silhouette assumes, and names at least two conditions under which your recommendation would be wrong.
7. `analysis.py` regenerates every number in the report.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 15 |
| Methodology and validation | 10 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, reproducible results and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T1-007-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders into it.
2. **Expected structure:**
   ```text
   clbg-ML-T1-007-<username>/
   ├── requirements.txt
   ├── agentmap/            # your package
   ├── tests/               # provided tests + your test_member_*.py
   ├── resources/           # unchanged
   ├── analysis.py
   └── REPORT.md
   ```
3. **Commit as you work.** A single "final" commit containing everything will be questioned at defence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** set by the cohort coordinator. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback but never stand in for the core requirements.

1. **Seeding experiment.** Run random seeding versus k-means++ with n_init=1 over 200 seeds and report the distribution of final inertia.
2. **Sensible hubs.** Replace Euclidean distance with a road-distance proxy (for example inflate east-west distance by 1.4) and show whether your k changes.
3. **When silhouette lies.** Build a two-moons dataset where k-means with the best silhouette gives a wrong grouping, and explain why in terms of the algorithm.
4. **Mini-batch.** Implement mini-batch k-means and measure the loss in inertia against the speed-up on 100,000 generated points.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration inside `REPORT.md`. Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** adapted code with a link. **Collaboration** is limited to general techniques; never share code, numbers or report text.
- **How understanding is verified.** In a short defence the assessor will:

1. Trace one Lloyd iteration on a 6-point example you choose, including a cluster that empties.
2. Explain why k-means++ seeding usually beats random seeding, and what it costs.
3. Handle an unseen modification live, such as weighting points by transaction volume or adding a minimum cluster size.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | numpy broadcasting, means and distances, pytest mechanics. No statistics beyond averages. |
| **New skill developed** | Turning an algorithm described in words into correct vectorised code, and verifying it against a trusted reference. |
| **Decisions the member must make** | How to vectorise assignment, how to repair empty clusters within the stated rule, how to structure restarts so they are deterministic, and how much to trust a silhouette peak. |
| **What must be investigated independently** | The shape of the k table on the data, and what the data can and cannot say about the number of hubs. |
| **Why it is interesting** | The setting is a real siting decision, and the empty-cluster and duplicate-point cases are exactly where textbook pseudocode breaks. |
| **Evidence of competence** | Numerical agreement with scikit-learn, correct behaviour on hidden re-seeded data and degenerate cases, and a defence that traces the algorithm by hand. |
| **Misconceptions exposed** | "k-means finds the global optimum." "The highest silhouette is the true k." "Seeding does not matter." "Clusters always exist." |
| **Preparation for later work** | Leads to density-based and mixture models, stability analysis of clusterings, and the research-grade segmentation problem at Tier 3 in this unit. |

**Suggested approach**, for members who want guidance (you may ignore it):

1. Do R2, R4 and R3 first; they are short and let you test the loop.
2. Add R1 and R5, then compare inertia with scikit-learn on a few seeds.
3. Write the silhouette against the definition on a 6-point example before vectorising it.
4. Only then run the k table and write the report.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
