# DS-T1-014: Collision Course

> *"Thirty-one to the sixth is 887 million. Two passengers can't get the same booking reference." They can, they did, and the log says the generator is even worse than the arithmetic.*

![Format: Investigation](https://img.shields.io/badge/format-investigation-d73a49) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-014` |
| **Title** | Collision Course: How Long Must a Booking Reference Be? |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-05: Probability and Statistics](../README.md) |
| **Format** | Investigation (secondary: Implementation) |
| **Difficulty** | Technical 2 · Mathematical 3 · Research 1 · Engineering 2 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 8–14 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | Basic combinatorics (counting, products of probabilities); the Poisson distribution; logarithms; Python and NumPy; running `pytest` |
| **Skills developed** | Birthday-problem reasoning and its generalisations; numerically stable probability computation; Poisson approximation; Monte Carlo verification; estimating a hidden population size from collisions; hypothesis tests for "more coincidences than chance"; turning probability into a design requirement |
| **Technologies** | Python 3.10+, NumPy, SciPy (`scipy.stats` distributions), pandas, matplotlib, pytest |

---

## B. Problem Statement

A state bus rapid transit (BRT) operator (fictional, but modelled on real Nigerian BRT schemes) sells seats through a USSD and SMS booking service. Every booking receives a **six-character reference** from a 31-symbol alphabet (digits and capitals without `0`, `1`, `I`, `L` and `O`, which are easily confused). The conductor checks the reference at boarding. References are valid for 24 hours. Across the network, about **120,000** bookings are made each day; the busiest depot handles about **25,000**.

Last month a conductor at that depot found two passengers holding the same reference for different seats. The operations lead's response was:

> "31⁶ is 887,503,681. With 25,000 bookings a day, the chance of a repeat is about 25,000 / 887 million, roughly 0.003%. That was a one-off glitch."

The head of digital products is not convinced and asks you to investigate. You have two days of references issued at the busiest depot (50,000 references, exported from the booking database), and three questions:

1. **Was the operations lead's arithmetic right?** If the generator worked exactly as designed, how often would a day at this depot, or across the whole network, contain at least one duplicate?
2. **Is the generator working as designed?** Do the two days of data show more duplicates than the design predicts? If so, how large is the code space the generator *actually* uses?
3. **What should the next design be?** How long must the reference be so that a whole network day has at most a 1% chance of any duplicate, **and** someone typing random references (10,000 attempts a day, a realistic scripted attack on the USSD menu) has at most a 0.1% chance of hitting a live booking?

What makes it hard:

- **Intuition fails.** The operations lead computed the chance that *one particular* booking repeats. The question is whether *any pair* among 25,000 does, and there are over 312 million pairs.
- **Floating point fails.** `1 − ∏(1 − i/N)` for N in the trillions and n in the hundreds of thousands loses most of its significant digits if computed naively.
- **The defect is hidden.** The symbols in the log look perfectly uniform. A frequency check passes. Only the coincidences give the generator away.
- **The design has two failure modes pulling in different directions.** Short codes are easy to read over the phone; long codes are safe from collisions and from guessing. A uniqueness check at issue removes collisions entirely, but it does nothing about guessing.

**Known facts:**

- The designed space is 31⁶ references, each meant to be equally likely and independent of all previous references.
- The export contains every reference issued at the depot on 12 and 13 October 2026, in issue order within each day.
- The booking system did **not** check for duplicates before issuing a reference.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Derive** the exact collision probability for n uniform draws from N values, its Poisson approximation and the expected number of colliding pairs, and say when the approximation is good.
2. **Compute** these quantities stably for very large N and n, and **verify** them by Monte Carlo simulation with a stated tolerance.
3. **Generalise** to non-uniform draws, and explain why Σpᵢ² (the "collision entropy") is the quantity that matters.
4. **Investigate** an operational log: test whether its coincidences exceed the design's prediction, estimate the effective space with an interval, and recognise that uniform symbol frequencies do not imply a uniform joint distribution.
5. **Turn probability into a requirement**, recommending a reference length and a design (random against checked against sequential) with both collision and guessing risks quantified.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `ref_collisions` package in [`starter/ref_collisions/`](starter/ref_collisions/). The signatures are fixed because the tests import them; the CLI is provided.

| ID | Requirement |
|---|---|
| **R1** | `p_collision_exact(n, N)`: exact, accurate to a relative error of about 1e-9 even when the answer is 1e-10 or smaller, for N up to 31¹⁰ and n up to 10⁶. Your report must explain the numerical problem and your fix (for example `log1p` and `expm1`). |
| **R2** | `expected_colliding_pairs(n, N)` and `p_collision_approx(n, N)`. The report must **derive** E[pairs] = C(n, 2)/N using indicator variables and linearity of expectation (no independence needed), and justify the Poisson approximation. Show a table of exact against approximate values for at least five (n, N) pairs, including one where the approximation is poor. |
| **R3** | `p_collision_nonuniform(n, probs)`: the Poisson approximation for non-uniform probabilities. The report derives the per-pair collision probability Σpᵢ² and explains why 1/Σpᵢ² acts as an "effective space size". |
| **R4** | `max_n_for_risk(N, risk)`, `guess_success_prob(active, N, guesses)` and `min_code_length(alphabet_size, n_per_window, collision_risk, guesses, guess_risk)`, as specified in the docstrings. |
| **R5** | `simulate_collision_prob(n, N, reps, rng)`: a Monte Carlo estimate with a Wilson interval. In the report, verify R1 and R3 against simulation for at least four settings, and state your tolerance and why you chose it. |
| **R6** | `count_colliding_pairs(codes)` and `estimate_space_size(codes)`: the moment estimator N̂ = C(n, 2)/pairs, with an interval from an **exact** Poisson interval for the pair count. Zero pairs must give N̂ = ∞, not an error. |
| **R7** | `excess_collision_pvalue(codes, designed_space)` and `char_uniformity_pvalue(codes)`, as specified in the docstrings. |
| **R8** | `python -m ref_collisions resources/data/booking_refs.csv --out outputs/` writes `evidence.json` (provided CLI). |
| **R9** | **Investigation report** answering the three questions in §B with numbers, intervals and figures: (a) the design's own collision risk per depot day and per network day; (b) the evidence about the actual generator, including per-day and pooled analyses, the space estimate with its interval, and the frequency check, explaining why the latter cannot see the defect; (c) a recommendation of length and design. The recommendation must compare at least **three** designs: random with no check, random with a uniqueness check at issue, and sequential numbers with a check digit. Quantify their collision and guessing risks, and say what each costs operationally. |

### D.2 Engineering requirements (mandatory)

- **Reproducibility.** Every number in the report is regenerated by code with stated seeds.
- **Tests.** Keep the provided tests passing and add **at least 10 tests of your own** in `tests/test_member_*.py`, including a hand-computed small case (for example n = 3, N = 4, where you can enumerate all 64 outcomes) and a test that would fail if the exact probability were computed naively.
- **Dependencies.** Only [`starter/requirements.txt`](starter/requirements.txt).

### D.3 Security and privacy

Booking references are bearer tokens: whoever holds one can board. The export therefore contains live credentials in a real system; here they are synthetic and expired. In your report:

- explain why the references in the export should be treated as sensitive even without names or phone numbers attached;
- state the trust boundary: who can request references and how quickly, and which control (rate limiting, binding a reference to a phone number, length) addresses which threat;
- do not publish any reference from the log in your report beyond at most three redacted examples (for example `K7••QX`).

### D.4 Optional enhancements (not required for full marks)

- An estimator of the space size that uses the *timing* of the first repeat (the "birthday attack" view) and its sampling distribution.
- A Bayesian estimate of N with a prior over plausible internal state sizes (2¹⁶, 2²⁰, 2²⁴, 2³², …).
- A check-digit scheme (for example Luhn mod N or Damm) and the share of single-character typos it catches.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/booking_refs.csv`](resources/data/booking_refs.csv): 50,000 rows, 2 columns, about 0.9 MB |
| **Provenance** | **Synthetic**, produced by CLBG with a fixed seed from a simulated booking system. The generator is held in the assessor kit because it reveals the defect. No passenger data of any kind is included. |
| **Licence** | CC BY 4.0 (same as this repository's content) |
| **Integrity** | SHA-256 `51b8638d6dbaa057294878c548feac91b809c1c3bde42582e9d63437d875aed7`. The contract test checks it. |

| Column | Meaning |
|---|---|
| `date` | Issue date (`2026-10-12` or `2026-10-13`), 25,000 references each |
| `ref` | Six-character booking reference over the alphabet `23456789ABCDEFGHJKMNPQRSTUVWXYZ` |

**Known limitations (by design).** One depot and two days only. You can't see the generator's code, only its output. Two days of data are enough to establish *that* the space is too small and to bound *how* small, but not to identify the mechanism with certainty, and your report should say so.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-05-probability-and-statistics/DS-T1-014-collision-course
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract     # passes immediately
pytest                 # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `ref_collisions/` package | The probability and evidence tools |
| 2 | `tests/test_member_*.py` (≥ 10 tests) | Shows you can verify probability code by enumeration and simulation |
| 3 | `investigation.ipynb` **or** `investigation.py` | Reproduces every number and figure in the report |
| 4 | `outputs/evidence.json` | The machine-readable evidence (R8) |
| 5 | `REPORT.md` (at most 1,800 words plus derivations, tables and figures) | Derivations (R2, R3), verification (R5), the investigation and recommendation (R9), security notes (D.3) |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 7 | A 5–10 minute live defence | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

Criteria marked ⚙ are checked automatically with the public and hidden test suites; criteria marked ✍ are checked by the assessor.

1. ⚙ `pytest` passes all public tests and your own tests from a clean environment.
2. ⚙ `p_collision_exact` matches an independent product loop to a relative error of 1e-9, reproduces the classic birthday values (0.5073 at n = 23, N = 365), and agrees with C(n, 2)/N to 1e-6 relative error at n = 1,000, N = 31¹⁰. *Justification:* these are exact computations; the 1e-6 band is the approximation's own relative error (about n/N plus the square of the probability), so only a naive computation fails it.
3. ⚙ `min_code_length` and `max_n_for_risk` return the exact boundary values (for example, length 9 for the network requirement in §B).
4. ⚙ On logs re-generated from generators with different, unknown effective spaces, your space estimate's interval contains the true size and N̂ is within a factor of 2 of it. *Justification:* with 18–300 observed pairs, the Poisson relative error is between 6% and 25%; a factor of 2 is reached only by a wrong estimator (for example C(n, 2)/pairs computed with ordered pairs, or with n replaced by the number of distinct codes).
5. ⚙ The excess-collision test flags the defective generator (p < 0.001 pooled) and does **not** flag a healthy one (p > 0.01 on one day). *Justification:* 0.001 separates a 4.7-fold to 240-fold excess of pairs from chance at the tested sizes, and 0.01 keeps the false-alarm rate for a healthy generator at 1% by construction.
6. ⚙ `char_uniformity_pvalue` detects a 60% over-representation of 10 symbols in 3,000 codes (p < 1e-6) and stays above 0.01 on the official log.
7. ✍ The report's derivations (R2, R3) are correct and use indicator variables, not an unjustified independence assumption.
8. ✍ The report states the design's own risk correctly, about **0.30 per depot day** and **essentially 1 per network day** (about 8 expected duplicate pairs a day), and explains the operations lead's error in one sentence.
9. ✍ The space estimate is reported with its interval, per-day and pooled, together with an argument for why the frequency check passes even though the generator is broken.
10. ✍ The recommendation compares the three designs of R9, with numbers for both risks, and makes a clear choice with its operational cost (length a passenger must read or type, a database lookup, the guessing risk of sequential codes).

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Methodology: investigation and evidence | 20 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create a private repository** named `clbg-DS-T1-014-<your-github-username>` with this assessment's `starter/` contents at the top level, plus `tests/`, `resources/` and `submission-template/`.
2. **Expected structure:**
   ```text
   clbg-DS-T1-014-<username>/
   ├── README.md                 # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── ref_collisions/
   ├── tests/                    # provided tests + test_member_*.py
   ├── resources/                # unchanged
   ├── investigation.ipynb | investigation.py
   ├── outputs/evidence.json
   ├── figures/
   ├── REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** The history is part of the evidence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue with the repository URL and commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **First-repeat estimator.** The number of references issued before the first duplicate is about √(πN/2). Use the first repeat within each day as a second estimate of N, and compare its spread with the pair-count estimator's by simulation.
2. **Which bit width?** Generators usually fail at powers of two. Compute the likelihood of the data for N = 2ᵏ, k = 16…32, and say how sharply the data identify k.
3. **Matriculation numbers.** Apply the same analysis to a university that wants random 8-digit student IDs for 40,000 new students a year that must stay unique for 10 years. Should it use random IDs at all?
4. **Typos.** Add a check character and measure, by simulation, the share of single substitutions and adjacent transpositions it detects.

---

## K. Assessment Integrity

**AI tools are permitted** for learning, for example explaining the birthday problem, reviewing your code or suggesting plots. **They must not do the assessment for you.** You must be able to derive and explain everything you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`. Disclosed, reasonable use is not penalised.
- **Cite** any derivation or code you adapted.
- **Collaboration:** you may discuss general ideas with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In the defence the assessor will:
  1. ask you to derive E[pairs] = C(n, 2)/N on paper and say why no independence assumption is needed;
  2. ask you to explain, without code, why the frequency check passes on a broken generator;
  3. give you an **unseen modification**, such as a different alphabet, a 12-hour validity window, or "the system now rejects duplicates at issue: what is the new risk?", and ask you to compute the answer live with your package;
  4. ask where `log1p` or `expm1` matters in your code and what would go wrong without it.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Counting, independence, the Poisson distribution, logarithms, NumPy. |
| **New skill developed** | Treating coincidences as evidence: using the pair count both to predict risk and to infer an unseen parameter (the effective space), with an honest interval. |
| **Decisions the member must make** | Per-day against pooled analysis; which interval to use for a small count; what tolerance validates a formula by simulation; which design to recommend when collision and security requirements conflict. |
| **What must be investigated independently** | Whether the generator is defective, how large its real space is, and why the frequency check cannot detect it. |
| **Why it's interesting** | Two layers of surprise: the design itself was never safe at this volume, and the implementation is about 50 times worse. The final recommendation hinges on a requirement (guessing) that the incident never mentioned. |
| **Evidence of competence** | Exact boundary values; agreement with simulation; correct recovery of hidden spaces on re-generated logs; correct derivations reproduced live. |
| **Misconceptions exposed** | "P(collision) ≈ n/N." "Uniform symbols mean uniform codes." "A rare event observed once is a glitch." "Uniqueness checks make short codes safe." "1 − ∏(1 − i/N) is fine in floating point." |
| **Preparation for later work** | Capture–recapture and population-size estimation, hashing and sketching in data engineering (HyperLogLog, Bloom filters), record linkage, and security engineering for tokens and API keys. |

**Suggested approach** (optional):

1. Do n = 3, N = 4 by enumeration on paper, then implement R1–R2 and test against it.
2. Write the simulation (R5) early. It is your safety net for every formula.
3. Only then open the log: count pairs per day, compare with the design's expectation, then estimate N.
4. Write the recommendation last, after you have computed both risks for every candidate design.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
