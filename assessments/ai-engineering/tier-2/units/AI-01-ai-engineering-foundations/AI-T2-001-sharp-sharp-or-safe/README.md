# AI-T2-001: Sharp Sharp or Safe: Choosing Decoding Settings for a USSD Banking Assistant

> *Greedy decoding is safe but robotic; plain sampling is varied but sometimes invents a banking rule. Build the decoding machinery from logits up, then choose settings that meet both a safety bar and a variety bar.*

![Format: Comparative (secondary: Implementation)](https://img.shields.io/badge/format-comparative-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T2-001` |
| **Title** | Sharp Sharp or Safe: Choosing Decoding Settings for a USSD Banking Assistant |
| **Subtrack** | AI Engineering |
| **Tier** | 2: Applied Competence |
| **Unit** | [AI-01: AI Engineering Foundations and Model Fundamentals](../README.md) |
| **Format** | Comparative (secondary: Implementation) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 2 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14-20 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. The graded path uses a deterministic mock; the full test run takes under a minute |
| **Recommended prerequisites** | numpy arrays and probability basics (softmax, cumulative sums); what a language model's next-token distribution is; pytest. Recommended: AI-T1-001 |
| **Skills developed** | Temperature, top-k, top-p and repetition penalty implemented from logits; beam search; measuring generation quality with a validity and a diversity metric; selecting decoding parameters under two competing constraints and checking they generalise |
| **Technologies** | Python 3.10+, numpy, pytest |

---

## B. Problem Statement

Mama Put Bank (fictional) serves customers on a USSD menu and by SMS. A language model writes the short replies: balance, transfer limits, how to block a card. Two prototypes disappointed. With greedy decoding every customer got an identical sentence, so a support lead worried that replies look canned and that repeated probing reveals nothing is "alive" on the other end. With plain sampling, about one reply in five contained a made-up fragment such as "your transfer limit is unlimited naira per day". A regulator-facing reviewer will accept **no more than 3% invalid replies**, and the product team wants **at least 45% of replies in a batch to be distinct** so that messages do not read as copy-paste.

You will not call a real model. The assessment ships `resources/lm.py`, a deterministic stand-in: a 4-gram language model trained on synthetic bank replies, 12% of which were corrupted with a wrong word. It exposes the same thing every real model exposes, a log-probability vector for the next token, plus an `is_valid` oracle that checks a reply against the approved templates.

First you build the decoding machinery from the logits up (temperature, top-k, top-p, repetition penalty, seeded sampling, sequence scoring, beam search). Then comes the part the brief leaves open: you must explore the configuration space, define how to measure it, and write `choose_decoding`, which picks settings that meet both bars on the mock model you are handed and keep meeting them on seeds it never saw. Hidden tests use mock models with more corruption than the public one, so a hard-coded configuration will not survive.

> **Why this matters beyond this task.** Every hosted API exposes some of these knobs. Knowing what each one does to the distribution, and measuring the effect against a product requirement instead of folklore ("0.7 is the good temperature"), is the difference between configuring a model and guessing.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** softmax with temperature, top-k, top-p and repetition penalty with correct tie and boundary behaviour.
2. **Sample** reproducibly from a next-token distribution, with a documented random-number protocol.
3. **Score and search**: compute sequence log-probabilities and implement beam search, and say when it helps.
4. **Measure** generations with validity, uniqueness and repetition metrics that match a product requirement.
5. **Choose** decoding settings under two competing constraints, and show they generalise to held-out seeds and to a noisier model.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `decodelab` in [`starter/decodelab/`](starter/decodelab/). Interfaces are fixed; where the brief is silent the choices are yours to make and defend. Stubs raise `NotImplementedError("R<n>: ...")`.

Pipeline order inside `generate` is fixed: repetition penalty on the logits, then temperature softmax, then top-k, then top-p, then sampling. Config keys: `temperature` (default 1.0), `top_k` (0 = off), `top_p` (1.0 = off), `repetition_penalty` (1.0 = off). Missing keys take defaults.

| ID | Requirement |
|---|---|
| **R1** | `softmax(logits, temperature=1.0)`: numerically stable (no overflow for logits near 1000). `temperature == 0` returns a one-hot on the argmax, ties to the lowest index. |
| **R2** | `filter_top_k(probs, k)`: keep the `k` most probable tokens (ties to the lower index), zero the rest, renormalise. `k <= 0` or `k >= len(probs)` returns a copy unchanged. |
| **R3** | `filter_top_p(probs, p)`: sort by probability descending (stable, ties to the lower index), keep the smallest prefix whose cumulative probability is at least `p` (always at least one token), renormalise. `p >= 1` returns a copy unchanged. Input need not be sorted. |
| **R4** | `apply_repetition_penalty(logits, generated, penalty)`: for each distinct token id in `generated`, divide its logit by `penalty` if the logit is positive, otherwise multiply by `penalty`. Returns a new array. |
| **R5** | `generate(lm, seed, cfg=None, max_len=20) -> list[int]`: start with empty `ids`; at each step compute `lm.logits(ids)` and run the pipeline. Draw **exactly one** `u = rng.random()` per step from `np.random.default_rng(seed)` and pick the smallest index whose cumulative probability exceeds `u`. Stop on `<eos>` (id 1, not included in the result) or at `max_len`. |
| **R6** | `sequence_logprob(lm, ids)`: sum of log-probabilities of `ids` followed by `<eos>`, each under the model's own distribution at temperature 1. |
| **R7** | `beam_search(lm, width, max_len=20)`: standard beam search by cumulative log-probability. Each beam is expanded by its `width` most probable next tokens (never `<bos>`); keep the best `width` candidates, ties broken by smaller id sequence; finished (`<eos>`) hypotheses leave the beam; stop when no beam remains or at `max_len`. Return the best finished hypothesis (or best unfinished if none), without `<eos>`. Width 1 must equal greedy decoding. |
| **R8** | `evaluate_config(lm, cfg, seeds, max_len=20) -> dict` with `valid_rate` (share of generations for which `lm.is_valid` holds), `unique_rate` (distinct id sequences divided by number of generations) and `repeat_rate` (share of generations in which some adjacent token pair occurs twice). One generation per seed. |
| **R9** | `choose_decoding(lm, seeds, min_valid, min_unique) -> dict` returns a config meeting both bars on `seeds` **and expected to meet them on seeds it has not seen**. Which parameters you search, the preference among feasible configs, and any safety margin are yours to choose and defend. It raises `ValueError` if nothing in your search space is feasible. |

### D.2 Engineering requirements (mandatory)

- Deterministic: no wall-clock time, no global random state, no network. Everything randomised takes an explicit seed.
- At least **10 tests of your own** in `tests/test_member_*.py`; include a boundary test for top-p and an exact replay test for the sampling protocol.
- `experiments.py` regenerates the table in the report: validity, uniqueness and repetition for greedy, plain sampling, temperature sweeps, top-k, top-p and your chosen config, over at least 200 seeds.
- `REPORT.md` (from the [template](submission-template/REPORT.md)) carries every number you cite, reproducible with one command you document.

### D.3 Responsibility

The mock is fictional, but the product is not: an invalid reply about a transfer limit can lead a customer to make a payment that fails or to trust a rule that does not exist. In the report, write one paragraph on why validity is a hard constraint and diversity a soft one, who bears the cost of a wrong reply, and why a decoding setting is *not* a substitute for validating output against an approved source before it reaches a customer.

### D.4 Optional enhancements

- Compare beam search outputs with sampled outputs on your two metrics.
- Add a cost-aware metric where invalid replies about money weigh more than other invalid replies.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Model** | [`resources/lm.py`](resources/lm.py): `build_lm(seed=2026, noise=0.12, n=3000)` returns a `TinyLM` with `vocab`, `logits(ids)`, `decode(ids)` and `is_valid(ids)` |
| **Provenance** | **Synthetic** 4-gram table fitted on generated bank replies (five templates with slots); `noise` is the fraction of training replies with one corrupted token. No real customer, message or institution |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing is committed beyond the 3 KB module; the table is built in memory in well under a second |
| **Model access** | None. No network, GPU, weights or API |

Hidden tests use other model seeds and higher noise (up to 0.3), a hand-made model that traps greedy decoding, and an independent replay of the sampling protocol.

**Setup**

```bash
cd assessments/ai-engineering/tier-2/units/AI-01-ai-engineering-foundations/AI-T2-001-sharp-sharp-or-safe
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

Nothing in the graded path calls a hosted model. If you want to try your code against a real local open-weight model (for example through Ollama) or a hosted API afterwards, that is an optional extension; never put keys or outputs from such runs into the repository.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `decodelab/` package | R1 to R9 |
| 2 | `tests/test_member_*.py` (at least 10 tests) | Includes a top-p boundary test and a seeded replay test |
| 3 | `experiments.py` | Reproduces the table and the sweep figure |
| 4 | `REPORT.md` (at most 1,500 words plus tables), from the [template](submission-template/REPORT.md) | Decision memo for the product team; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked (T) are checked by the public and hidden test suites; the rest are checked by hand.

1. (T) `pytest` passes the provided tests and your own from a clean environment.
2. (T) R1 to R4 match hand-computed values, including ties, boundaries (cumulative mass exactly `p`), temperature 0 and large logits.
3. (T) `generate` replays exactly under the stated random-number protocol (hidden tests compare with an independent implementation), and `top_k=1` and `temperature=0` both give the greedy sequence.
4. (T) Beam search of width 1 equals greedy; on a hand-made model where greedy is trapped, a wider beam finds a sequence with higher log-probability.
5. (T) `choose_decoding(lm, 50 seeds, 0.97, 0.45)` returns a config that on 100 unseen seeds reaches valid rate at least 0.95 and unique rate at least 0.40. *Justification:* the reference reaches about 1.0 and 0.49 (unique rate falls as the number of seeds grows because the reply set is finite, so the seed count is fixed); plain sampling gives about 0.8 valid and temperature 0.3 gives about 0.3 unique, so both bars bind.
6. (T) On hidden models with noise 0.2 and 0.3, the chosen config reaches valid rate at least 0.94 and unique rate at least 0.33 on unseen seeds (a fixed config copied from the public model fails here).
7. The report shows the trade-off curve, explains why the chosen setting works for this model, and states what would change with a different model.

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

1. **Create your own private repository** named `clbg-AI-T2-001-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `decodelab/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Margin of safety.** Use a lower confidence bound on validity from the training seeds, not the point estimate, and show the effect on held-out results.
2. **Min-p.** Implement min-p filtering and compare it with top-p on the noisier models.
3. **Real model check.** Run the same experiment against a local open-weight model if you have one (optional; never required or graded).

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why top-p at temperature 1 reaches full validity on this mock yet would not on a model with a fatter plausible tail; (2) ask what top-p 0.9 does when the top token alone has probability 0.95; (3) give an unseen change, such as a validity bar of 0.999 or a model with 40% noise, and ask which part of your choice would break first.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | numpy and basic probability. No neural-network internals. |
| **New skill developed** | Treating decoding settings as measured engineering decisions with acceptance criteria, instead of copied defaults. |
| **Decisions the member must make** | Search space and preference rule in `choose_decoding`; the number of seeds; how much margin to leave; how to report the trade-off. |
| **What must be investigated independently** | Why neither extreme works: greedy has no diversity, plain sampling samples the corrupted tail; and which knob attacks the tail without destroying variety. |
| **Why it is interesting** | The popular intuition that low temperature is the safe fix is shown to be a poor trade here; truncation does better. |
| **Evidence of competence** | Exact protocol replay, boundary correctness, and a configuration that holds on unseen seeds and noisier models. |
| **Misconceptions exposed** | 'Temperature controls truthfulness.' 'Beam search gives the best answer.' 'One good setting works for every model.' |
| **Preparation for later work** | Leads into AI-02 structured generation, AI-03 evaluation, and AI-12 model internals. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
