# Assessor Handbook

This handbook is for everyone who evaluates CLBG Intelligence Track submissions. Confidential materials (reference solutions, hidden tests, marking guides and defence question banks) live in the **private assessor kit** repository. Access is granted by the Assessment Committee.

## 1. Your role

You decide, on evidence, whether a submission demonstrates the competence its assessment targets. You also help the member grow. Be **rigorous**, **consistent**, **fair** and **kind**.

Before marking for the first time, complete calibration (§10).

## 2. The review workflow

| Step | What you do | Time guide (T1 / T2 / T3) |
|---|---|---|
| 1. Intake | Confirm the commit SHA, assessment ID and version. Check for any declared deviations. Declare any conflict of interest. | 5 min |
| 2. Reproduce | Fresh clone at the SHA, then build the environment from the member's manifest and run their README steps. Record whether the key results reproduce. | 15 / 30 / 60 min |
| 3. Automated evidence | Run public tests, member tests and **hidden tests** (`CLBG_SUBMISSION_DIR=<repo> pytest <kit>/solutions/<ID>/hidden_tests`). Save the output. | 5–15 min |
| 4. Read | Read the report or notebook, then the code. Use the marking guide's "common mistakes" table. | 30 / 60 / 120 min |
| 5. Provisional score | Score each rubric dimension with **one line of evidence**. Use `tools/rubric-tools/scoresheet.py <ID>`. | 15 min |
| 6. Defence | Run the defence using the kit's defence script for the assessment (§6). Adjust provisional scores **only** where the defence changes your understanding of the evidence. | 5–10 / 10–20 / 20–40 min |
| 7. Outcome | Apply the gates, then decide the outcome band ([placement framework](placement-framework.md)). Flag the work for double marking where required. | 5 min |
| 8. Feedback | Write feedback to the [standard](evaluation-framework.md#6-feedback-standards) and update the placement record. | 15–30 min |

## 3. Interpreting rubrics

- **Score the evidence, not the effort.** Hours spent are not a dimension.
- **Use the performance levels** (Exemplary 90–100%, Proficient 70–89%, Developing 50–69%, Beginning 0–49%) to find the band, then place the score within it.
- **Avoid halo effects.** Score dimensions independently. A beautiful report doesn't fix a wrong method, and a brilliant algorithm doesn't excuse unreadable code.
- **Don't double-penalise.** If one root cause, such as data leakage, affects several dimensions, penalise it where it belongs most (usually Methodology or Correctness) and note the knock-on effects.
- **Acceptance criteria are not the rubric.** They decide whether the work *works*. The rubric decides *how well* it demonstrates competence. A failed mandatory acceptance criterion usually caps the outcome at R (see the placement framework).

## 4. Evaluating code quality

Look for:
- **Correct structure:** responsibilities separated (I/O, logic, presentation); no 400-line functions.
- **Readability:** meaningful names; comments that explain *why*, not *what*.
- **Robustness:** input validation; explicit error handling; no silent `except: pass`.
- **Testing:** tests that would fail if the logic were wrong, with edge cases taken from the problem.
- **Reproducibility:** pinned or bounded dependencies, fixed seeds, scripted data steps.
- **Security hygiene:** no committed secrets; safe handling of untrusted input, which is especially important for AI Engineering.

Don't penalise stylistic preferences (tabs or spaces, a particular framework) unless the assessment requires them.

## 5. Assessing technical reasoning

Ask: *does each important decision follow from the problem?*
- **Data Science:** provenance and representativeness acknowledged; methods matched to the question; uncertainty quantified; alternative explanations considered.
- **ML Engineering:** the validation design matches the data structure (grouped, temporal, imbalanced); baselines are meaningful; metrics match costs; error analysis drives the next steps.
- **AI Engineering:** the architecture matches the requirements; retrieval and generation are evaluated separately; failure modes and the trust boundary are explicit; cost and latency are measured, not assumed.

## 6. The technical defence

Every assessment's kit entry contains a defence script. The general structure is:

1. **Opening (1–3 min):** "In two sentences, what problem did you solve and what was hardest?"
2. **Trace (2–10 min):** pick specific inputs and have the member walk you through exactly what their system does to them.
3. **Unseen modification (2–15 min):** a small new requirement or edge case, implemented live. You're watching the reasoning, not the typing speed.
4. **Probing (2–10 min):** "Why this method? What else did you consider? What would break it? How do you know it works?"
5. **Close:** "What would you do with another week?"

Discipline-specific emphasis:
- **DS:** data provenance, analytical method, interpretation, and what the data *can't* tell you.
- **ML:** model and validation choices, metrics, leakage, error analysis, deployment trade-offs.
- **AI:** architecture, retrieval behaviour, model failure modes, evaluation design, prompt injection and other security concerns.

**Conduct.** Be welcoming and allow thinking time. Rephrase a question if it's misunderstood. Nervousness isn't a lack of understanding, so look for whether the member can *get there* with prompting. Record your observations as you go. Members with approved adjustments may give written answers for parts of the defence.

Full guide: [technical defence guide](../assessment-operations/oral-defense/technical-defence-guide.md).

## 7. Identifying copied or fabricated results

Signals worth investigating. Each one is evidence to follow up, **not proof**:
- results that don't reproduce, or that reproduce only with steps the member didn't document;
- numbers in the report that differ from what the code outputs;
- code style or idioms inconsistent with the rest of the submission, or with the member's explanations;
- an inability to explain or modify core code;
- a history consisting of one large commit, combined with weak explanations;
- outputs that are suspiciously clean on hidden data (possible hard-coding), so check the code paths;
- references to libraries, files or functions that don't exist in the repository.

If you have a concern, follow the [integrity procedure](assessment-integrity.md#5-handling-concerns). **Never** use AI-text detectors, and never accuse a member during the defence.

## 8. Assessing AI-assisted work

- Check that `AI_USE_AND_SOURCES.md` exists and is plausible.
- Disclosed, allowed use is **neutral**: it neither earns nor loses marks.
- The defence is the test. A member who used AI heavily but can trace, justify and modify everything has demonstrated competence. A member who can't has not, whatever tools they used.
- Note in the feedback when a submission shows **good** AI-assisted practice, such as verifying outputs, testing generated code or critiquing suggestions. That's a professional skill.

## 9. Recording feedback and disputes

- Use the score sheet and the placement record ([templates](../assessment-operations/scoring-templates/README.md)).
- Write one line of evidence per rubric dimension, and give feedback to the [standard](evaluation-framework.md#6-feedback-standards).
- **Disputes:** respond to informal review requests within 5 working days. If you can't resolve one, tell the member about the formal appeal route ([assessment policy §9](assessment-policy.md#9-disputes-and-appeals)). Don't discuss disputes publicly.

## 10. Calibration and moderation

- **New assessors:** independently score two calibration exemplars from the kit for a subtrack, then compare with the reference scores in a calibration session. You may mark live submissions once your total is within ±6 of the reference on both.
- **Each cohort:** join the moderation meeting ([moderation](../assessment-operations/moderation/README.md)).
- **Confidentiality:** the kit's contents must never be shared with members, posted publicly or pasted into third-party tools. Report any leak immediately (see [SECURITY.md](../SECURITY.md)). Assessments whose materials leak are rotated.
