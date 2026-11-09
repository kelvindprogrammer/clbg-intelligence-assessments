# ML-T1-017: Which Language Is This SMS? A Tokenizer, Character N-Grams and Naive Bayes from Scratch

> *A bank's gateway must route short messages to English, Pidgin or Yoruba-speaking agents. Build the text pipeline and the classifier by hand, and make it survive typos.*

![Format: Implementation (secondary: Investigation)](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `ML-T1-017` |
| **Title** | Which Language Is This SMS? A Tokenizer, Character N-Grams and Naive Bayes from Scratch |
| **Subtrack** | ML Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [ML-08: Natural Language Processing](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8–12 hours over 1 week |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid services, no internet after setup. Full test run under 2 minutes |
| **Recommended prerequisites** | Python dictionaries and Counters; logarithms and Bayes' rule; what a classifier is. No NLP library knowledge is needed |
| **Skills developed** | Tokenization rules; character n-grams with boundary markers; multinomial naive Bayes with smoothing; log-space arithmetic and log-sum-exp; abstention; error analysis on noisy code-switched text |
| **Technologies** | Python 3.10+, numpy, scikit-learn, pytest |

---

## B. Problem Statement

A fictional bank, Lagos Mutual Bank, runs an SMS gateway where customers text short questions. Agents speak English, Nigerian Pidgin or Yoruba, and routing a message to the wrong desk wastes minutes. The messages are short, informal and full of typos: `abeg send me the airtime`, `JOWO mo fe ra data!!`, `my token no dey werk`. Many switch language for a word or two (a customer writing Yoruba might open with `please`).

You will build a **language identifier** from first principles, without any NLP library in your package:

1. A **tokenizer** with explicit rules (lowercase; runs of letters and apostrophes; digit runs collapsed to a placeholder).
2. **Character n-grams** with boundary markers, so that `na` and `nature` look different at the edges.
3. A **feature extractor** combining word and character features.
4. A **multinomial naive Bayes** classifier with Laplace smoothing whose log-probabilities are properly normalised and never underflow.
5. A **language identifier** that can also abstain when it has no evidence.

The task is fully specified and tested exactly; the tests compare your naive Bayes against scikit-learn's on the same counts. What you owe beyond code is understanding: why log space, why smoothing, why character n-grams help when people mistype, and honestly how little accuracy on template-generated data says about real language use.

The messages are produced by a generator from hand-written templates in English, Nigerian Pidgin and simplified, tone-mark-free Yoruba-style text. The templates are **synthetic teaching material, not a language resource**, and a native speaker should review them before any non-teaching use.

> **Why this matters beyond this task.** Text classifiers are probability models over counts. Understanding smoothing, log-space arithmetic and sub-word features is what lets you debug a classifier that silently fails on short, noisy, multilingual input, the normal case in African messaging.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Tokenize** noisy short text with explicit, testable rules.
2. **Generate** character n-gram features with boundary markers.
3. **Implement** multinomial naive Bayes with smoothing and numerically stable normalised log-probabilities, and verify it against a reference.
4. **Identify** the language of short code-switched messages and abstain when there is no evidence.
5. **Explain** with an experiment when character n-grams beat word features and what the synthetic data cannot tell you.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `smslang` in [`starter/smslang/`](starter/smslang/). Interfaces are fixed. Use only the standard library and numpy inside the package (scikit-learn is used by the tests as a reference, not by your code).

| ID | Requirement |
|---|---|
| **R1** | `tokenize(text)`: lowercase the text and return, in order, the runs of letters and apostrophes (`[a-z']+`) and runs of digits (`\d+`); every digit run becomes the single token `"<num>"`. Everything else (punctuation, emoji, spaces) is a separator and is discarded. |
| **R2** | `char_ngrams(token, n_min=2, n_max=4)`: take `s = "<" + token + ">"` and return all substrings of `s` of length `n_min` to `n_max`, ordered by length and then by start position. Lengths longer than `s` yield nothing. |
| **R3** | `extract_features(text, n_min=2, n_max=4)` returns a `collections.Counter` with a key `"w:" + token` for every token and `"c:" + gram` for every character n-gram of every token. |
| **R4** | `NaiveBayes(alpha=1.0)` with `fit(docs, labels)` (docs are dicts of feature counts; sets `classes_` (sorted), `vocab_`, `log_prior_`, `log_lik_`), `predict_log_proba(docs)` (rows log-sum-exp to zero; features not seen in training are ignored; no underflow for documents with thousands of counts) and `predict(docs)`. |
| **R5** | `LanguageID(alpha=1.0, n_min=2, n_max=4)` with `fit(texts, labels)`, `predict_proba(texts)` (rows sum to 1), `predict(texts)` and `predict_with_abstain(texts, min_prob)`, which returns `"unk"` where the top probability is below `min_prob`. |

### D.2 Engineering requirements (mandatory)

- No NLP or ML library in the package; numpy and the standard library only.
- Deterministic: no randomness anywhere.
- At least **6 tests of your own** in `tests/test_member_*.py`, including a comparison with scikit-learn's `MultinomialNB` on a small corpus and an underflow test with very long documents.
- `REPORT.md` (at most 900 words plus tables) answering the questions in the template, with the numbers produced by a short script you include.

### D.3 Responsibility

The messages are synthetic, but real customer SMS are personal data under the Nigeria Data Protection Act 2023. Write two sentences on what you would log, how long you would keep it and why a language identifier should not store message text. Also write two sentences on who is disadvantaged when a language identifier is accurate for English but poor for Pidgin or Yoruba, and how you would find out.

### D.4 Optional enhancements

- Compare word-only, character-only and combined features at three noise levels and plot the result.
- Add a prior-correction option for imbalanced traffic and show its effect.
- Report calibration: are predicted probabilities of 0.9 right about 90 percent of the time?

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | Generated by [`resources/datagen.py`](resources/datagen.py): `make_messages(n=900, seed=0, noise=0.04)` returns `texts` and `labels` in `en`, `pcm` (Pidgin), `yo` (Yoruba-style) |
| **Provenance** | **Synthetic** templates written for teaching, with dropped and doubled letters, upper-casing, emoji and short code-switched tags; no real message or customer |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Public protocol** | Train on seed 1, test on seed 2 (900 messages each); a second test uses noise 0.10 |
| **Size** | Nothing is committed; `python resources/datagen.py --out DIR --seed 2026` writes a TSV of about 50 KB |

Hidden tests use other seeds, noise up to 0.08, other n-gram ranges and other smoothing values.

**Setup**

```bash
cd assessments/ml-engineering/tier-1/units/ML-08-natural-language-processing/ML-T1-017-which-language-is-this-sms
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `smslang/` package | Tokenizer, n-grams, features, naive Bayes and language identifier |
| 2 | `tests/test_member_*.py` (at least 6 tests) | Includes the scikit-learn comparison and the underflow test |
| 3 | `analysis.py` | Reproduces the word-versus-character comparison and the error analysis |
| 4 | `REPORT.md` (at most 900 words plus tables), from the [template](submission-template/REPORT.md) | Explanations and experiments; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites; the rest are checked by hand.

1. ⚙ `pytest` passes the provided tests and your own from a clean environment.
2. ⚙ `tokenize`, `char_ngrams` and `extract_features` match the hand-computed examples, including digits, apostrophes, emoji, empty input and short tokens.
3. ⚙ `NaiveBayes.predict_log_proba` equals scikit-learn's `MultinomialNB` (alpha 1.0 and 0.1) to 1e-8, rows are normalised, unseen features are ignored and documents with thousands of counts do not underflow.
4. ⚙ **Performance.** `LanguageID` reaches accuracy at least **0.95** on the public test set and at least **0.94** at noise 0.10. *Justification:* the reference reaches about 0.98 on both; a word-only model reaches about 0.96 at the higher noise, so the bars separate a working pipeline from a broken one without forcing the character features.
5. ⚙ **Robustness.** On hidden seeds with noise up to 0.08 the accuracy bar is 0.93.
6. ⚙ `predict_with_abstain` returns `"unk"` for empty and emoji-only input at `min_prob` 0.6 and keeps at least 90 percent of ordinary messages.
7. ✍ The report explains log space, smoothing, the effect of alpha, and shows when character n-grams beat word features, with an error analysis of the confused messages and a candid note that template data overstate real-world accuracy.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 15 |
| Methodology and evidence | 15 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 5 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-ML-T1-017-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `smslang/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Language mix.** Add a fourth label for English-Pidgin code-switched messages and see how identification degrades.
2. **Feature selection.** Keep only the most informative features and measure the accuracy-versus-size curve.
3. **Discriminative comparison.** Replace naive Bayes with logistic regression on your features and compare calibration.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why your classifier works in log space and what goes wrong without log-sum-exp; (2) ask what alpha does at 0.001 and at 5 and what you saw; (3) give an unseen change, for example 1-grams only or a new language label, and ask what in your code and results changes.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python dictionaries, logarithms, Bayes' rule. No NLP theory. |
| **New skill developed** | Treating a text classifier as exact arithmetic over counts and testing it against a reference implementation. |
| **Decisions the member must make** | How to handle apostrophes and digits, how to structure features, how to normalise stably, how to test. |
| **What must be investigated independently** | When character n-grams beat word features and why. |
| **Why it is interesting** | A fifty-line model identifies code-switched, misspelled messages, and its failure modes are visible in the arithmetic. |
| **Evidence of competence** | Exact agreement with scikit-learn, stable log-probabilities, and an accuracy gain that survives re-seeding. |
| **Misconceptions exposed** | 'Probabilities can be multiplied directly.' 'Smoothing is a detail.' 'High accuracy on synthetic data means it works on real messages.' |
| **Preparation for later work** | Leads into ML-08 Tier 2 drift-aware triage, tokenisation work in AI-12 and low-resource language evaluation. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
