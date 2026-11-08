# AI-T3-002: Thirty Students, One Lab PC: A Quantisation and Batching Study for Local Inference

> *A university computer lab wants a private, local model for thirty students. Quantise it, batch it, and defend the trade-off between quality, latency and capacity, without a GPU or a single model download.*

![Format: Investigation (secondary: System-design)](https://img.shields.io/badge/format-investigation-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T3-002` |
| **Title** | Thirty Students, One Lab PC: A Quantisation and Batching Study for Local Inference |
| **Subtrack** | AI Engineering |
| **Tier** | 3: Advanced Engineering, Research and System Design |
| **Unit** | [AI-03: Model APIs and Local Inference](../README.md) |
| **Format** | Investigation (secondary: System-design) |
| **Difficulty** | Technical 4 · Mathematical 3 · Research 4 · Engineering 3 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 26–36 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. Full test run under 2 minutes |
| **Recommended prerequisites** | Numpy linear algebra, perplexity, queueing intuition (arrival rate against service rate). Recommended: AI-T2-004 |
| **Skills developed** | Writing quantisers from scratch; diagnosing outlier-driven quality loss; event simulation of static and continuous batching; capacity under a latency SLO; threats to validity of a simulated study; local-versus-hosted decision under data-residency constraints |
| **Technologies** | Python 3.10+, numpy, pytest |

---

## B. Problem Statement

The Computer Science department at a Nigerian federal university (fictional: *Unity Federal University*) has a 16-seat lab and a spare workstation with 8 GB of free memory and no GPU. Staff want to run an open-weight assistant locally for about **30 students** at a time. Reasons: lecture notes and student submissions should not leave campus (the data-protection officer cites the Nigeria Data Protection Act 2023, ss. 41 to 43, on cross-border transfers), hosted API costs are paid in dollars, and the campus link is unreliable. The vendor of the model shows a table of "accuracy lost" for 4-bit versions on a leaderboard and says batching "just works".

You will test those claims in a **simulated** but carefully built environment, because the grading must be reproducible on any laptop with no downloads:

- A **toy language model** (`resources/toylm.py`) whose weights are `A` (V x d) and `B` (d x V). It was built from a synthetic Markov chain, then a few feature channels were rescaled (column `j` of `A` times `s`, row `j` of `B` divided by `s`). In floating point the model is *unchanged*; in low-bit arithmetic the planted outliers are hostile, as they are in real transformers. Quality is **perplexity** on text sampled from the chain.
- An **analytic cost model** (`CostModel`): a decode step reads all weights (so it is memory-bandwidth bound) plus a per-sequence cost; prefill is per prompt token; memory is weights plus a key-value cache per live sequence. A 3-billion-parameter model is assumed: 6 GB in fp16, 3 GB in int8, 1.5 GB in int4.
- A **workload generator**: Poisson student requests, optionally with lecture-end bursts.

You must implement the quantisers and the simulator, then run a study that ends in a recommendation with an SLO of your own justification (the tests use a p95 of 10 seconds). The brief deliberately does not tell you which scheme to use, which batching policy wins, or how much quality loss is acceptable. **Deciding and defending those is the assessment.** The mock is an abstraction: your report must say exactly what it can and cannot support.

> **Why this matters beyond this task.** Local inference decisions are routinely made from leaderboard numbers and vendor claims. Being able to build the measurement apparatus, see where it can lie, and reason about capacity is what separates a deployment from a demo.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** symmetric quantisation with per-tensor, per-channel and grouped scales, exactly and efficiently.
2. **Diagnose** why a function-preserving rescaling of channels ruins per-tensor int4 but not per-channel int4, and measure it as perplexity.
3. **Simulate** static and continuous batching on a CPU cost model, with prefill stalls, memory limits and tail latency.
4. **Define** capacity under a latency SLO and search a configuration space for the best feasible point.
5. **Stress-test** the recommendation: vary workload, hardware assumptions, quality tolerance and SLO, and show what changes.
6. **Argue** the limits of a simulated study and when a local model beats a hosted API for this lab.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `servelab` package in [`starter/servelab/core.py`](starter/servelab/core.py). Use only numpy and the standard library. Signatures are fixed.

| ID | Requirement |
|---|---|
| **R1** | `quantize(w, bits, axis=None, group=None) -> QTensor`, `dequantize(qt)`, `qbytes(qt)`. Symmetric, round to nearest even (`numpy.rint`), `qmax = 2**(bits-1) - 1`, codes clipped to `[-qmax, qmax]`. A **block** shares one scale `max(abs(block)) / qmax` (a zero block uses scale 1). `axis=None`: one block, the whole tensor. `axis=k`: one block per index along every *other* axis, reducing over axis `k` (so `axis=0` on a V x d matrix gives one scale per column). `group=g`: split axis `k` into consecutive groups of `g` (it must divide the axis length, else `ValueError`; `group` without `axis` is a `ValueError`). Works for any number of dimensions. `qbytes = ceil(codes * bits / 8) + 2 * (number of scales)`. |
| **R2** | `quantize_model(model, bits, scheme) -> (A_hat, B_hat, bytes)` and `ppl_ratio(model, bits, scheme, tokens)`. `bits=16` returns the arrays unchanged at 2 bytes per weight. Schemes: `"tensor"`; `"channel"` (A: `axis=0`, B: `axis=1`, so each feature channel `j` has its own scale in both matrices); `"group<g>"` (A: `axis=1`, B: `axis=0`, groups of `g` contiguous channels). `ppl_ratio` is the perplexity of the dequantised model divided by that of the fp model, using `toylm.perplexity`. |
| **R3** | `simulate(requests, policy, max_batch, max_wait_s, bits, cm) -> SimResult`. `requests` are `(arrival_s, prompt_tokens, output_tokens)`, possibly unsorted; latencies are returned in input order. Raise `ValueError` if `cm.memory_gb(max_batch, bits) > cm.mem_cap_gb` or the policy is unknown. **Static**: when the engine is free and requests wait, the batch starts at `tf = max(engine_free, min(arrival of the max_batch-th request from the head, head_arrival + max_wait_s))`, takes the waiting requests with `arrival <= tf` (up to `max_batch`), pays the sum of their prefill times, then runs `max(output)` steps at `step_s(b)` with `b` the batch size (finished sequences keep their slot); all its requests complete together. **Continuous**: at every step boundary, requests with `arrival <= now` are admitted in order up to `max_batch` live sequences, each admission stalling the engine for its prefill time; then one decode step runs at `step_s(live)`; a sequence completes at the end of the step in which its last token is produced and frees its slot. `max_wait_s` is ignored. |
| **R4** | `max_load_multiplier(requests, config, cm, slo_p95_s, multipliers)`: the largest multiplier `m` (arrival times divided by `m`) whose p95 meets the SLO, stopping at the first failure; 0 if `m=1` fails. This is the **capacity** of a configuration. |
| **R5** | `recommend(model, requests, cm, slo_p95_s, max_ppl_ratio, tokens) -> dict` returns the configuration (keys `bits, scheme, policy, max_batch, max_wait_s`) plus `p95_s, ppl_ratio, memory_gb, capacity` that meets the SLO, the quality cap and the memory cap, and has the highest capacity among those you searched. Your search space must at least cover bits 16/8/4, schemes tensor/channel/group8, both policies, batches 1 to 16 and waits up to 0.2 s. |

**The study (hand-assessed, and the larger share of the marks).** Using your code, the report must contain: (a) a scheme-by-bits quality table across at least 5 model seeds and outlier scales, with the mechanism explained from the weights, not only the numbers; (b) the batching comparison on at least two workload shapes (smooth and bursty); (c) a recommendation for the lab with its SLO and quality tolerance justified; (d) at least three sensitivity analyses of your choice (for example bandwidth, SLO, KV size, outlier strength, burstiness) saying which assumption the recommendation is most fragile to; (e) a local-versus-hosted comparison using stated assumptions about electricity, hardware amortisation and hosted prices of your choice quoted in kobo per 1,000 tokens with their source, including the data-residency argument; (f) a threats-to-validity section.

### D.2 Engineering requirements (mandatory)

- Deterministic: all randomness is seeded. No network, no model download, no GPU.
- The simulator must be efficient enough that `recommend` finishes in under 30 seconds on a laptop for 300 requests.
- At least **12 tests of your own** in `tests/test_member_*.py`, including a hand-computed continuous-batching trace and a property test that a rescaling of a channel (A column times s, B row divided by s) leaves fp perplexity unchanged.
- `experiments.py` regenerates every table and figure in `REPORT.md`.

### D.3 Responsibility

Explain, in the report, what data would be sent to a model in this lab (student code, essays, possibly personal details), why that matters under the Nigeria Data Protection Act 2023, and what a local deployment still leaves unsolved (logging of prompts on the lab PC, who can read them, retention, consent for any evaluation using student text). Say whether quality tolerance should be the same for a code helper and a feedback-on-essays tool. The data in this assessment is synthetic.

### D.4 Optional enhancements

- Replace per-tensor outlier damage with a SmoothQuant-style rebalancing and show it recovers per-tensor int8/int4.
- Add speculative decoding or prefix caching to the simulator and measure when it helps.
- Measure real latency of an open-weight model served locally (for example via Ollama) on your machine and fit the cost model's constants. Optional; never required, and the tests do not use it.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Toy model, cost model, workload** | [`resources/toylm.py`](resources/toylm.py): `make_model(seed, vocab, rank, outlier_channels, outlier_scale)`, `sample_tokens`, `perplexity`, `CostModel`, `make_workload(seed, n, rate_per_s, burst)` |
| **Provenance** | **Synthetic and deterministic.** The "model" is a rank-24 factorisation of a random Markov chain; the cost model is analytic with documented constants. Nothing real is measured |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Default cost model** | 3e9 parameters, 50 GB/s memory bandwidth, 0.25 GB of KV cache per live sequence, 8 GB cap; fp16 / int8 / int4 weights of 6 / 3 / 1.5 GB; int4 pays 20 % more per-sequence time for unpacking |
| **Size** | Nothing is committed beyond code; a full model and 4,000 tokens are generated in well under a second |
| **Compute** | numpy on CPU; the public tests run in a few seconds |

Hidden tests use other model seeds and outlier strengths, a different cost model (larger model, slower memory, bigger cache), bursty workloads, and differential tests of your quantiser and simulator against an independent implementation, so exactness matters.

**Setup**

```bash
cd assessments/ai-engineering/tier-3/units/AI-03-model-apis-and-local-inference/AI-T3-002-thirty-students-one-lab-pc
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `servelab/` package | Quantisers, model quantisation, simulator, capacity, recommendation |
| 2 | `tests/test_member_*.py` (at least 12 tests) | Includes a hand-computed trace and the rescaling invariance property |
| 3 | `experiments.py` | Regenerates every table and figure |
| 4 | `REPORT.md`, at most 3,000 words plus tables and figures, from the [template](submission-template/REPORT.md) | The study (a) to (f) in §D.1 and the AI-use declaration |
| 5 | A 10-minute technical defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `quantize`, `dequantize` and `qbytes` agree with an independent implementation on random tensors of 2 and 3 dimensions, with every axis and group, at 3, 4 and 8 bits (hidden test).
3. ⚙ `simulate` agrees with the specification to 1e-9 on unsorted, tied, bursty workloads for both policies on a cost model that differs from the public one (hidden test).
4. ⚙ On the public world the recommendation meets the SLO, the quality cap and the memory cap, and its capacity is at least that of every configuration in the coarse grid of the public test. On the hidden world (different hardware, burstier workload, stronger outliers) its capacity is at least that of the assessor's reference search.
5. ✍ **Mechanism.** The report explains from the weights (scale statistics, per-channel ranges, how many levels remain for ordinary channels) why per-tensor int4 fails and per-channel succeeds, and why grouping is in between, with a figure.
6. ✍ **Sensitivity and fragility.** At least three sensitivity analyses with a clear statement of which assumption would change the recommendation.
7. ✍ **Validity.** A threats-to-validity section that separates what the toy model can show (qualitative mechanisms, ordering of schemes) from what it cannot (absolute accuracy of real models, real latency).
8. ✍ **Decision.** A local-versus-hosted recommendation with explicit assumptions and numbers, a data-residency argument, and a statement of what evidence would reverse it.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 12 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Methodology and evidence | 20 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 8 |
| Critical thinking and limitations | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-AI-T3-002-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `servelab/` (your package), `tests/` (provided tests plus your own), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Rebalancing.** Implement a SmoothQuant-style migration of outlier scale between `A` and `B` and compare to per-channel scales.
2. **Mixed precision.** Keep the most sensitive channels in higher precision and measure bytes against quality.
3. **Real measurement.** Fit the cost model to timings of a small open-weight model run locally. Optional and outside grading.
4. **Admission control.** Add a queue-length limit and measure the p95 versus rejection-rate trade-off under bursts.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask you to explain, from a printout of the scales, why one outlier channel destroys per-tensor int4 but is harmless per-channel, and what the same effect looks like in a real transformer; (2) ask which single assumption in your cost model you trust least and how you would measure it on this lab PC; (3) give an unseen modification, for example "the PC has 6 GB free and the SLO is 5 seconds" or "half the requests have 1,000-token prompts", and ask you to predict which configuration changes and why, before running anything.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Numpy linear algebra, perplexity, queueing intuition. No deep-learning framework. |
| **New skill developed** | Building and critically using a measurement apparatus for an inference deployment, including knowing what it cannot show. |
| **Decisions the member must make** | Quality tolerance and SLO; which schemes and policies to search; which sensitivities matter; local or hosted. |
| **What must be investigated independently** | Why outliers break coarse scales; where continuous batching stops helping; which assumption dominates. |
| **Why it is interesting** | The bug is in the weights, not the bit width: the same 4 bits are catastrophic or free depending on the scale granularity. |
| **Evidence of competence** | Differential tests against an independent implementation, a recommendation that survives a changed world, and a study that names its own fragility. |
| **Misconceptions exposed** | '4-bit always loses a fixed few percent.' 'Bigger batches are always better.' 'Local is free.' 'A leaderboard number transfers to my model.' |
| **Preparation for later work** | Leads into AI-13 production operations, ML-12 serving and optimisation, and AI-10 evaluation. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
