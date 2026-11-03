# Assessment Integrity

CLBG assessments establish **genuine understanding**. This policy is designed to verify understanding, not to punish people for legitimately using modern development tools.

## 1. Principles

1. **You own what you submit.** You must be able to explain, justify and change every part of it.
2. **Disclosure, not prohibition.** Using AI coding assistants, documentation, forums and libraries is normal professional practice. Hiding that use is the problem.
3. **Verification through understanding.** CLBG does **not** rely on plagiarism detectors or AI-text detectors, because they are unreliable and unfair. It relies on the mechanisms in §4.
4. **Proportionality.** Responses to concerns are proportionate, documented and fair, and members are always heard.

## 2. Use of AI tools

Unless an assessment states otherwise in section K, these rules apply:

| Use | Status |
|---|---|
| Asking an AI tool to explain a concept, an error message, an API or a library | ✅ Permitted, and you don't need to disclose individual queries, though general use should be declared |
| Getting suggestions for small code fragments that you then understand, adapt and test | ✅ Permitted with disclosure |
| Asking an AI tool to review your code or writing | ✅ Permitted with disclosure |
| Generating whole functions, modules, analyses or report sections that you submit with little change | ⚠️ Permitted only where the assessment explicitly allows it, with disclosure. You must still defend the work in full. |
| Pasting the assessment brief into a tool and submitting what comes back | ❌ Not permitted |
| Pasting dataset rows that represent personal data, even synthetic data treated as real, into third-party tools | ❌ Not permitted (privacy practice) |
| Using AI to fabricate results, citations, logs or experiment outputs | ❌ Serious breach |

Some assessments set stricter rules. For example, a first-principles implementation may ban autocompletion of the core algorithm, and a Tier 1 attempt may require an unaided first pass followed by an assisted revision. Section K of the assessment always takes precedence.

**Disclosure.** Every submission includes `AI_USE_AND_SOURCES.md`, built from the template in each assessment. It lists the tools used, what they were used for, example prompts, and how outputs were verified. Reasonable disclosed use is never penalised. Undisclosed substantial use that comes to light is treated as an integrity concern.

## 3. Citation, attribution and originality

- Cite any code, method, figure or text you adapted from someone else, with a link.
- Respect licences: credit open-source code according to its licence, and use datasets only under their stated terms.
- Results must come from **your** runs of **your** code. Copying numbers from papers, leaderboards or other members' work as if they were your own is fabrication.

## 4. How understanding is verified

These mechanisms are used in proportion to the tier and the stakes:

| Mechanism | What it shows |
|---|---|
| **Repository history** | Work developed over time, with meaningful commits. A single "final" commit invites closer questioning. It is not proof of misconduct, but you should expect deeper questions. |
| **Reproduction** | The assessor reruns your work from a clean environment, and the claimed results must reappear. |
| **Hidden tests** | Your code is tested on held-out or re-seeded data, so hard-coded answers fail. |
| **Code walkthrough** | You explain chosen parts of your code, line by line where needed. |
| **Tracing** | You trace specific inputs through your system, for example "what happened to record R00417?". |
| **Unseen modification** | You make a small, previously unseen change live, such as a new requirement, format or edge case. |
| **Live debugging** | You diagnose and fix a small planted bug in your own code. |
| **Design questioning** | You explain why you chose this approach, what the alternatives were, and what would break it. |

## 5. Handling concerns

1. **A concern is raised.** An assessor notes specific, observable evidence, for example an inability to explain core code, results that don't reproduce, or text identical to a known source.
2. **Follow-up conversation.** The member is invited to a further defence of 15–30 minutes with a second assessor. This is **not** a hearing, and many concerns are resolved here.
3. **Determination.** If concerns remain, the committee reviews the evidence and the member's written response. Possible findings:
   - **No breach:** the attempt proceeds normally.
   - **Poor practice**, such as incomplete disclosure or weak citation: corrected through revision, with no penalty beyond the revision.
   - **Breach**, such as substantial undisclosed generation, copying or fabrication: the attempt is recorded as N, and a further attempt in that unit is deferred for one cohort.
   - **Serious breach**, such as fabricated results or impersonation: as for a breach, plus referral to CLBG leadership.
4. **Records.** Findings are recorded privately and kept only as long as necessary. A first finding of poor practice is not kept beyond the cohort.

Members may be accompanied by a peer or mentor at any integrity conversation, and may respond in writing.

## 6. Assessor obligations

- Base every concern on evidence, never on writing style alone or on how a member speaks.
- Never use AI-text detectors as evidence.
- Keep confidential assessor materials confidential (see [SECURITY.md](../SECURITY.md) for reporting leaks).
- Declare conflicts of interest, such as close friends, team-mates or mentees, and step aside where necessary.
