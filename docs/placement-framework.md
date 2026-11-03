# Placement Framework

Placement records **demonstrated competence in one subtrack**. It is built from evidence, it is reviewed whenever new evidence arrives, and it never depends on a single number.

## 1. Principles

1. **Per subtrack.** Data Science, ML Engineering and AI Engineering placements are independent.
2. **Evidence over scores.** The rubric score is one input. Gates and the technical defence are others, and they carry equal weight.
3. **Selectable, not sequential.** Members choose any assessment at any tier. Prerequisites tell you what knowledge you need, but they never block you.
4. **Growth-oriented.** Every outcome comes with actionable feedback and a route to reassessment.
5. **Consistent.** Assessors use the same rubrics, gates, calibration and moderation (see [evaluation framework](evaluation-framework.md)).

## 2. Assessment outcomes

Each assessed submission receives exactly one of four outcomes:

| Outcome | Requirements |
|---|---|
| **Meets requirements** (M) | Score ≥ 80, **all gates passed**, every mandatory acceptance criterion met, and a defence that shows independent understanding. |
| **Meets requirements with minor deficiencies** (M−) | Score 65–79, all gates passed, and every mandatory acceptance criterion met or missed only in ways that don't undermine the result's trustworthiness. Deficiencies are listed in the feedback. |
| **Requires revision** (R) | Score 50–64, **or** one or two mandatory criteria failed in a fixable way, **or** a defence that was incomplete but not concerning. The member may resubmit once within the revision window (default 14 days), and the resubmission is assessed on the deficiencies only. |
| **Does not yet demonstrate competence** (N) | Score < 50, **or** a failed reproducibility or defence gate, **or** fundamental errors. The member may attempt a *different* assessment in the same unit and tier after a cooling-off period (default 21 days). |

**Gates.** Integrity declaration, reproducibility, defence, and any assessment-specific gate such as privacy or safety. They are pass/fail. **A failed gate overrides the score.** An excellent score with a failed reproducibility gate is not "Meets requirements".

The rubric tool prints a *provisional* band from the score (`tools/rubric-tools/scoresheet.py --score`). Assessors confirm the outcome only after applying the gates and the defence.

## 3. Tier placement

A member is **placed at Tier N in a subtrack** when the evidence below is recorded in their placement record ([template](../assessment-operations/scoring-templates/placement-record.md)).

| Placement | Minimum evidence |
|---|---|
| **Tier 1** | One **M** or **M−** at Tier 1 in the subtrack, plus a defence showing independent understanding. |
| **Tier 2** | **Two** outcomes of M or M− at Tier 2, from **two different units**, at least one of them **M**. Alternatively, one M at Tier 2 plus one M on a Tier 2 capstone. Each needs a defence of at least 10 minutes. |
| **Tier 3** | **Two** outcomes of M at Tier 3, from different units, **or** one M at Tier 3 plus one M on a Tier 3 capstone or a research-category Signature Challenge. Both need a full defence (20–40 minutes) with **two assessors**, at least one of them independent of the member's mentoring. |

**Attempting above your current tier.** A member with no placement may attempt a Tier 2 or Tier 3 assessment directly.
- If the outcome is M at that tier, the evidence counts toward that tier.
- If the outcome is **R or N at Tier 2/3**, the assessor may also record whether the work **demonstrates Tier 1 (or Tier 2) competence**, using the lower tier's descriptors. That can establish the lower-tier placement without a separate assessment. The member is never penalised for aiming high.

**Lower tiers are implied.** A Tier 3 placement implies Tier 2 and Tier 1 in the same subtrack.

## 4. Factors beyond the score

Assessors record a short judgement on each factor below (Strong / Adequate / Concern) in the placement record. A single *Concern* on independence or understanding prevents placement until it is resolved, usually through a follow-up defence.

| Factor | Evidence |
|---|---|
| Technical correctness | Hidden tests, reproduced results, technical review |
| Demonstrated independence | Commit history, AI-use declaration, defence answers, the unseen-modification task |
| Understanding during defence | Tracing, explanation of alternatives, live modification |
| Quality of reasoning | Justification of methods, handling of uncertainty and limitations |
| Reproducibility | Clean-environment rerun by the assessor |
| Breadth of evidence | Different units, formats and domains across the qualifying submissions |

## 5. Remediation, reassessment and growth

- **Feedback first.** Every R or N outcome lists specific deficiencies and suggests preparatory resources, including the prerequisite refreshers in [shared/foundations](../shared/foundations/README.md).
- **Revision (R):** one resubmission per attempt, within the revision window, assessed by the same assessor where possible.
- **Retry (N):** a *different* assessment in the same unit and tier, after the cooling-off period. Retrying the same assessment is not allowed, because knowledge of the marking would distort the evidence.
- **Moving up.** Members can attempt the next tier at any time. Placement updates as soon as the evidence requirements are met.
- **Placement review.** A placement is reviewed if later evidence contradicts it, for example a serious integrity finding. It is never quietly downgraded: the member is informed and heard.
- **Appeals.** See [assessment policy §9](assessment-policy.md#9-disputes-and-appeals).

## 6. Verifying competence

Competence is verified through the combination of mechanisms set out in [assessment integrity](assessment-integrity.md):
- hidden tests on held-out or re-seeded data;
- the assessor rerunning the work from a clean environment;
- a review of repository history;
- the technical defence, including tracing, live unseen modification and small debugging exercises;
- for Tier 3, a second independent assessor.

## 7. Recommended starting points

Members unsure where to begin should use the self-check in the [member handbook](member-handbook.md#3-choosing-where-to-start). It is not graded and not recorded. Its only purpose is to suggest a sensible first tier.
