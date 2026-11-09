# AI-T1-004: The Maize SMS Prompt Kit: Templates, Few-Shot Selection, Fencing and Strict Parsing

> *A farmers' cooperative wants SMS messages turned into clean JSON by a language model. Before any model is trusted, build the plain code around it: the template, the examples, the fence around untrusted text, the parser and the validator.*

![Format: Implementation](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T1-004` |
| **Title** | The Maize SMS Prompt Kit: Templates, Few-Shot Selection, Fencing and Strict Parsing |
| **Subtrack** | AI Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [AI-02: Prompt Engineering and Structured Generation](../README.md) |
| **Format** | Implementation |
| **Difficulty** | Technical 2 · Mathematical 1 · Research 1 · Engineering 2 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8-12 hours over 1 week |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. The graded path uses a deterministic mock; the full test run takes under a minute |
| **Recommended prerequisites** | Python strings, regular expressions at a basic level, dictionaries and JSON; pytest. No machine-learning background needed |
| **Skills developed** | Strict prompt templating; deterministic few-shot selection; delimiting untrusted input; extracting JSON from messy replies; schema validation; never trusting a model's output format |
| **Technologies** | Python 3.10+, pytest (standard library only in your code) |

---

## B. Problem Statement

Kaduna Maize Growers Cooperative (fictional) receives hundreds of SMS messages a week from farmers: armyworm in the leaves, no rain for a week, traders offering a poor price. Extension officers want each message turned into a small JSON record, `{"crop": ..., "issue": ..., "urgency": 1-3}`, so that the urgent ones reach a human first. A language model will read the messages, but the cooperative's engineer has seen what models do in practice: they wrap the JSON in chatty text, put it in code fences, cut it off mid-object, return `"high"` where a number belongs, and, if a farmer's message says "ignore previous instructions", sometimes obey it.

None of that is solved by a cleverer prompt. It is solved by ordinary, careful code around the model. You will write that code. The assessment ships a **deterministic mock model** (`resources/mock_llm.py`) with controllable failure modes (`good`, `fenced`, `chatty`, `truncated`, `badtype`, and a `flaky` mode that mixes them) and a documented prompt-injection weakness, so every behaviour you test is reproducible and no API, key or network is involved.

This is a Tier 1 assessment: the rules are precise and fully specified, and your job is to implement them exactly, test them, and explain in a one-page report what each piece protects against.

> **Why this matters beyond this task.** Every production LLM feature is a pipeline of prompt construction, a call, parsing and validation. Most failures happen in the parts that are not the model.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Render** prompts from templates that fail loudly on missing or unused variables and never expand values twice.
2. **Fence** untrusted text so it cannot imitate the prompt's own delimiters.
3. **Select** few-shot examples deterministically and fit the prompt to a word budget.
4. **Extract and validate** a JSON object from a messy reply against a small schema, producing precise errors.
5. **Compose** the pieces into a function that returns a structured outcome for every model behaviour, including failure.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `promptkit` in [`starter/promptkit/`](starter/promptkit/). Interfaces are fixed; where the brief is silent the choices are yours to make and defend. Stubs raise `NotImplementedError("R<n>: ...")`.

| ID | Requirement |
|---|---|
| **R1** | `render(template, **variables)`: placeholders are `{{name}}` (optional inner spaces). Raise `PromptError` whose message starts with `missing:` if the template needs a variable not supplied, or `unused:` if a variable is supplied but not in the template (names sorted, comma-separated). Substitution is **single pass**: a value that itself contains `{{x}}` is inserted literally. |
| **R2** | `fence(text, tag="FARMER")`: first remove every occurrence of `"<<<"` and `">>>"` from `text`, **repeating until none remain** (so `"<<<<<<"` and `"<<>>>>"` cannot reassemble a marker); then return `"<<<TAG\n" + clean + "\nTAG>>>"`. |
| **R3** | `select_shots(examples, query, k)`: score each example (`{"text", "label"}`) by Jaccard similarity of lower-cased word sets (words are matches of `[a-z0-9']+`) with the query; take the `k` highest (ties to the lower original index; `k <= 0` gives none; `k` larger than the list gives all) and return them ordered so the **most similar example is last**. |
| **R4** | `build_prompt(instruction, shots, query)`: lines joined with `"\n"`: the instruction, an empty line, `Examples:`, then for each shot `Message:` / the fenced shot text / `Answer: ` plus `json.dumps(label, sort_keys=True)` / an empty line, and finally `Message:`, the fenced query, and `Answer:`. The prompt ends with `Answer:`. |
| **R5** | `build_prompt_within(instruction, shots, query, max_words)`: the R4 prompt if its whitespace-split word count is at most `max_words`; otherwise drop shots from the front (least similar first) one at a time until it fits. Raise `PromptError` if it does not fit with no shots. |
| **R6** | `extract_json(text) -> dict`: return the first span that is a balanced `{...}` (aware of quotes and escapes, so braces inside strings do not count) **and** parses as a JSON object. Skip spans that fail. Raise `ParseError` if there is none. Do not repair trailing commas or truncation. |
| **R7** | `validate(obj, schema) -> list[str]`: for each schema field `{"type": string/integer/number/boolean, "enum": [...], "min", "max", "required": True}`: `missing: f`, `type: f expected T` (a bool is not an integer or number), `enum: f`, `range: f`; plus `unexpected: f` for each field not in the schema. Return the sorted list, empty when valid. Do not mutate `obj`. |
| **R8** | `triage(llm, message, examples, schema, instruction, k=3) -> dict` builds a prompt with k selected shots, calls `llm.complete(prompt)`, extracts and validates. Returns `{"ok": bool, "data": dict or None, "errors": list[str]}`. Errors are `["call: <ExceptionName>"]` if the call raises, `["parse: no JSON object"]` if extraction fails, otherwise the validation errors. It never raises on model misbehaviour. |

### D.2 Engineering requirements (mandatory)

- Deterministic: no wall-clock time, no global random state, no network. Everything randomised takes an explicit seed.
- At least **8 tests of your own** in `tests/test_member_*.py`; include one injection test and one test for each failure mode of the mock.
- Standard library only in your package; no prompt-templating or JSON-repair library.
- `REPORT.md` (from the [template](submission-template/REPORT.md)) carries every number you cite, reproducible with one command you document.

### D.3 Responsibility

All messages are synthetic. In the report, write one paragraph on what could go wrong if a real cooperative's extension service routed farmers' messages through a model: who is harmed when an urgent message is mislabelled as routine, why the fence is a mitigation and not a guarantee against injection, and what a human reviewer should always see. Messages from real farmers are personal data under the Nigeria Data Protection Act 2023: say what you would minimise or remove before sending them to any hosted service.

### D.4 Optional enhancements

- Add a `repair` step that retries once with the validator's error list appended to the prompt, and measure how many `flaky` failures it recovers.
- Report the fertility of your prompt in words against the shot count.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Mock model** | [`resources/mock_llm.py`](resources/mock_llm.py): `MockLLM(mode, seed).complete(prompt) -> str`; the module docstring documents every mode and the injection weakness |
| **Data** | `make_examples(seed=2026, n=40)` returns `{"text", "label"}` dictionaries of synthetic farmer messages; `rule_label` is the labelling rule the mock uses; `SCHEMA` and `INSTRUCTION` are provided |
| **Provenance** | **Synthetic**: templated sentences with random crops, problems and urgency phrases; no real farmer, message or cooperative |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing committed beyond a 4 KB module |
| **Model access** | None. No network, key, GPU or download |

Hidden tests fuzz the parser and the fence with random inputs and use other example sets.

**Setup**

```bash
cd assessments/ai-engineering/tier-1/units/AI-02-prompt-engineering-and-structured-generation/AI-T1-004-maize-sms-prompt-kit
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
| 1 | `promptkit/` package | R1 to R8 |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Includes an injection test and one test per mock failure mode |
| 3 | `REPORT.md` (at most 700 words plus a table), from the [template](submission-template/REPORT.md) | What each component protects against; carries the AI-use declaration |
| 4 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked (T) are checked by the public and hidden test suites; the rest are checked by hand.

1. (T) `pytest` passes the provided tests and your own from a clean environment.
2. (T) `render`, `fence`, `select_shots`, `build_prompt` and `build_prompt_within` follow R1 to R5 exactly, including the repeated-removal rule and tie-breaking.
3. (T) `extract_json` recovers objects from bare, fenced and chatty replies, ignores braces inside strings, and returns the right object for 60 random nested objects embedded in noise (hidden fuzz test).
4. (T) `validate` produces the exact sorted error strings of R7 and treats `True` as not an integer.
5. (T) `triage` returns `ok` with the labelled record for `good`, `fenced` and `chatty` modes; returns `ok: False` with a non-empty error list for `truncated` and `badtype`; never raises on the `flaky` mode or on a model that throws.
6. (T) A message that tries to forge fence markers and a `Message:` block does not make the mock return its injected record. With the plain 60%-valid `flaky` mode, the measured success rate is between 0.4 and 0.8 (three of five modes are valid, so about 0.6; the bounds absorb prompt-format differences).
7. The report explains, for each component, one failure it prevents and one it does not.

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

1. **Create your own private repository** named `clbg-AI-T1-004-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `promptkit/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Repair loop.** Retry once with validator errors in the prompt and measure the recovery rate on `flaky`.
2. **Better similarity.** Replace Jaccard with a TF-IDF score and show where selection changes.
3. **Real model check.** Try the pipeline against a local open-weight model if you have one (optional; never graded).

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why `fence` removes markers repeatedly rather than once, with an example; (2) ask what the fence does not protect against even when it works; (3) give an unseen change, such as a new schema field or a model that returns two JSON objects, and ask which function changes and what test you would add first.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python strings, regular expressions and JSON. No model internals. |
| **New skill developed** | Treating the prompt and the reply as untrusted interfaces with explicit contracts and tests. |
| **Decisions the member must make** | How to scan for balanced braces; how to structure the single-pass substitution; which errors to expose. |
| **What must be investigated independently** | Why a single-pass strip of markers is not enough, and what the mock does with each broken format. |
| **Why it is interesting** | A short pipeline turns an unreliable model into a component with a predictable interface. |
| **Evidence of competence** | Exact behaviour on edge cases, fuzz-tested extraction, and an injection that fails. |
| **Misconceptions exposed** | 'Asking nicely for JSON gives JSON.' 'Delimiters make injection impossible.' 'If it parses it is valid.' |
| **Preparation for later work** | Leads into AI-02 Tier 2 reliability harnesses, AI-04 tool use, and AI-09 safety. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
