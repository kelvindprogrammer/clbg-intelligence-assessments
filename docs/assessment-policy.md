# Assessment Policy

This policy governs how CLBG Intelligence Track assessments are offered, attempted, submitted, evaluated and recorded. It applies to every subtrack and tier.

## 1. Scope and authority

The policy is maintained by the **Intelligence Track Assessment Committee**: the track lead, the subtrack leads and at least two experienced assessors. Changes are proposed by pull request and need approval from two committee members. Material changes take effect at the start of the next cohort, never in the middle of one.

## 2. Purpose of assessment

Assessments exist to:
1. **develop** competence through meaningful projects;
2. **evidence** competence fairly and consistently;
3. **inform** placement, team formation and mentoring.

They are not competitions, and they don't rank members against each other. The one exception is Signature Challenges, which follow their own protocol.

## 3. Eligibility and choice

- Any registered CLBG member may attempt any assessment in any subtrack and tier.
- Members choose freely: **subtrack → tier → unit → assessment**. There is no required order.
- **Concurrent attempts:** at most **two** assessments in progress at once, across all subtracks. This protects quality and assessor capacity.
- **Prerequisites** are listed in each assessment. They are advisory. Members who lack them are encouraged to start with the [foundations](../shared/foundations/README.md).

## 4. The standard assessment specification

Every assessment follows the standard format (sections A–K plus Pedagogical Design) described in the [authoring guide](contributing/AUTHORING_GUIDE.md). An assessment can only be attempted when its status is `reviewed` or `approved`. `draft` assessments may be piloted only with committee permission.

## 5. Registering an attempt

1. Open an **Assessment attempt** issue in this repository using its template. Record the assessment ID and its version.
2. The cohort coordinator confirms the deadline and assigns an assessor, normally within 5 working days.
3. The assessment **version** at registration is the one assessed. Later changes don't apply unless the member chooses to adopt them.

## 6. Collaboration

Each assessment's `collaboration` field (individual, pair or team) defines what is permitted:

| Mode | Allowed | Not allowed |
|---|---|---|
| **Individual** | Discussing general techniques, concepts and documentation; asking mentors conceptual questions. | Sharing code, notebooks, results, report text or rules specific to the assessment. |
| **Pair / team** | Full collaboration within the declared group. | Undeclared contributors. Each member must be able to defend **every** part of the work, and contribution statements are required. |

## 7. Deadlines, extensions and late work

- **Default windows:** Tier 1 has 3 weeks, Tier 2 has 5 weeks and Tier 3 has 8 weeks from registration. Capstones and Signature Challenges state their own windows. Coordinators may set cohort-wide dates.
- **Extensions:** requested **before** the deadline through the attempt issue, for reasons such as illness, examinations, bereavement or caring duties. Normally up to 7 days, and longer at committee discretion. Supporting detail stays private between the member and the coordinator.
- **Late work without an extension:** it is accepted up to 7 days late and assessed normally, but the best outcome available is **M−**. After 7 days the attempt lapses, and the member may register again after the cooling-off period.
- **Token flexibility:** each member has **three grace days per academic session** that they can apply to any non-capstone deadline without asking.

## 8. Evaluation

Evaluation follows the [evaluation framework](evaluation-framework.md) and the [placement framework](placement-framework.md):
- rubric scoring by a trained assessor using the public rubric and the confidential marking guide;
- gates (integrity, reproducibility, defence, plus any assessment-specific gate);
- a technical defence for every outcome above N;
- moderation and double marking where the framework requires them.

Target turnaround is feedback within **10 working days** of submission, or of the defence for Tier 3.

## 9. Disputes and appeals

1. **Informal review.** Within 7 days of receiving feedback, the member may ask the assessor to reconsider specific points, with reasons. The assessor responds within 5 working days.
2. **Formal appeal.** If the matter isn't resolved, the member submits an appeal to the committee within 14 days of the informal review. A **different** assessor re-marks the contested dimensions blind to the original marks. If the two marks differ by 10 points or more, a third assessor adjudicates.
3. **Grounds.** Procedural error, factual error in assessing the work, or inconsistency with the published rubric. Disagreeing with academic judgement alone is not grounds for appeal.
4. **Outcome.** The appeal decision is final for that attempt. Every appeal is logged anonymously in the moderation record and used to improve rubrics.

## 10. Records and privacy

- Placement records contain: name, GitHub username, assessment IDs and versions, outcomes, factor judgements, assessor names and dates. **No other personal data is kept.**
- Records are visible only to the member, the assessors involved and the committee. They are stored privately, never in the public repository.
- Members can request a copy or correction of their record at any time. Records are kept for the member's period of membership plus one year, unless the member asks for earlier deletion. This follows the Nigeria Data Protection Act 2023 principles of purpose limitation, minimisation and storage limitation.
- Public showcases of member work happen **only with explicit opt-in consent**.

## 11. Integrity

See [assessment integrity](assessment-integrity.md). Suspected breaches are handled under that policy, never informally.

## 12. Accessibility and reasonable adjustments

Members with disabilities or other circumstances that affect assessment may ask for adjustments, such as extended time, written instead of oral defence components, or alternative presentation formats. Adjustments change *how* competence is shown, never *what* competence is required.

## 13. Assessment lifecycle

Each assessment carries a version, an author, a review date and a status (`draft → reviewed → approved → retired`). See the [maintenance guide](contributing/maintenance.md). Retired assessments stay in the history but can't be newly attempted, and their IDs are never reused.
