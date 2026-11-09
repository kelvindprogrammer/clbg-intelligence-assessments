# Placement Framework

Placement records **demonstrated competence in the one subtrack and tier you chose for this window**. It is built from evidence, and it never depends on a single number.

## 1. Principles

1. **One subtrack, one tier, one task.** You choose all three before you start, and your result is your placement for this window.
2. **Evidence over scores.** The rubric score is one input. Gates and the technical defence are others, and they carry equal weight.
3. **Consistent.** Assessors use the same rubrics and gates (see [evaluation framework](evaluation-framework.md)).

## 2. Assessment outcomes

Each assessed submission receives exactly one of four outcomes:

| Outcome | Requirements |
|---|---|
| **Meets requirements** (M) | Score ≥ 80, **all gates passed**, every mandatory acceptance criterion met, and a defence that shows independent understanding. |
| **Meets requirements with minor deficiencies** (M−) | Score 65–79, all gates passed, and every mandatory acceptance criterion met or missed only in ways that don't undermine the result's trustworthiness. Deficiencies are listed in the feedback. |
| **Requires revision** (R) | Score 50–64, **or** one or two mandatory criteria failed in a fixable way, **or** a defence that was incomplete but not concerning. |
| **Does not yet demonstrate competence** (N) | Score < 50, **or** a failed reproducibility or defence gate, **or** fundamental errors. |

**Gates.** Integrity declaration, reproducibility, defence, and any assessment-specific gate such as privacy or safety. They are pass/fail. **A failed gate overrides the score.** An excellent score with a failed reproducibility gate is not "Meets requirements".

The rubric tool prints a *provisional* band from the score (`tools/rubric-tools/scoresheet.py --score`). Assessors confirm the outcome only after applying the gates and the defence.

## 3. Tier placement

A member is **placed at the tier they were assessed at** when the single chosen assessment reaches outcome **M** or **M−**, with a defence showing independent understanding (10–20 minutes at Tier 2, 20–40 minutes at Tier 3, with a second assessor for Tier 3).

An outcome of **R or N** means that tier is not yet demonstrated. The assessor may still note whether the work shows competence at a lower tier's descriptors.

## 4. Factors beyond the score

Assessors record a short judgement on each factor below (Strong / Adequate / Concern) in the placement record. A single *Concern* on independence or understanding prevents placement until it is resolved, usually through a follow-up defence.

| Factor | Evidence |
|---|---|
| Technical correctness | Hidden tests, reproduced results, technical review |
| Demonstrated independence | Commit history, AI-use declaration, defence answers, the unseen-modification task |
| Understanding during defence | Tracing, explanation of alternatives, live modification |
| Quality of reasoning | Justification of methods, handling of uncertainty and limitations |
| Reproducibility | Clean-environment rerun by the assessor |

## 5. Feedback

Every R or N outcome lists specific deficiencies in the feedback the member receives. A placement is reviewed if later evidence contradicts it, for example a serious integrity finding; it is never quietly downgraded, and the member is informed and heard.

## 6. Verifying competence

Competence is verified through the combination of mechanisms set out in [assessment integrity](assessment-integrity.md):
- hidden tests on held-out or re-seeded data;
- the assessor rerunning the work from a clean environment;
- a review of repository history;
- the technical defence, including tracing, live unseen modification and small debugging exercises;
- for Tier 3, a second independent assessor.

## 7. Recommended starting points

Members unsure where to begin should use the self-check in the [member handbook](member-handbook.md#3-choosing-where-to-start). It is not graded and not recorded. Its only purpose is to suggest a sensible first tier.
