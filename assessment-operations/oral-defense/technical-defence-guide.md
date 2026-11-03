# Technical Defence Guide

The technical defence is a structured conversation in which a member shows that they understand, own and can extend their work. It is required for every outcome above "Does not yet demonstrate competence".

This guide is public. Members should read it so that they know what to expect. Each assessment's **specific** defence questions and unseen modifications are confidential and live in the assessor kit.

## 1. Format by tier

| | Tier 1 | Tier 2 | Tier 3 / capstones |
|---|---|---|---|
| Length | 5–10 min | 10–20 min | 20–40 min |
| Assessors | 1 | 1 (2 if double-marked) | 2, at least one independent |
| Live modification | 1 small change | 1–2 changes, or a debugging task | 1 design change plus a deep probe |
| Emphasis | Can you trace and explain? | Can you justify and adapt? | Can you defend design, methodology and validity against alternatives? |

Defences run in person or by video call with screen sharing. The member's own machine and repository are used.

## 2. Structure

1. **Opening.** "In two sentences: what problem did you solve, and what was the hardest part?"
2. **Walkthrough.** The member gives a short tour of the architecture or analysis flow. Slides are not required.
3. **Trace.** The assessor picks inputs (a record, a query, a request) and the member traces exactly what happens to them, in the code.
4. **Unseen modification.** A small new requirement, a format change, an edge case, or a planted bug. The member implements it live while thinking aloud, and runs the tests.
5. **Probing.** Questions on alternatives, failure modes, evaluation validity and limitations.
6. **Reflection.** "What would you do with another week? What did you learn?"

## 3. What every member should be able to explain

- The problem, and why it matters.
- The technical approach, and how the implementation works.
- Why particular tools and methods were chosen, and which alternatives were considered.
- How the work was tested and evaluated, and why that evaluation is valid.
- The limitations and failure modes.
- What they would improve.

**Discipline-specific expectations**

| Data Science | ML Engineering | AI Engineering |
|---|---|---|
| Data provenance and representativeness. Why the analytical method fits the question. How uncertainty was quantified. Alternative explanations. What the data **cannot** support. | Model choice versus baselines. Validation design and leakage avoidance. Metric choice and the costs of errors. Error analysis. Calibration and robustness. Deployment and monitoring trade-offs. | System architecture and the data flow. Retrieval behaviour and its evaluation. Model failure modes (hallucination, refusal, brittleness). The evaluation methodology. The trust boundary, prompt injection and tool permissions. Cost and latency. |

## 4. Assessor scoring of the defence

The defence itself is **not** scored on the 100-point rubric. Instead it:
1. **confirms or adjusts** rubric scores where it changes the assessor's understanding of the evidence, for example when a member explains a design choice the report didn't, or can't explain code they submitted;
2. decides the **defence gate**:

| Judgement | Meaning |
|---|---|
| **Satisfactory** | Traces correctly, explains the key decisions, completes the modification with sound reasoning (minor slips are fine). |
| **Satisfactory with follow-up** | Mostly sound, but one area is unclear. A 10-minute follow-up within a week resolves it. |
| **Unsatisfactory** | Can't trace or explain core parts of the work, or can't approach the modification. The gate fails. If integrity concerns arise, follow the [integrity procedure](../../docs/assessment-integrity.md#5-handling-concerns). Never raise them as an accusation during the defence. |

## 5. Good practice for assessors

- Start easy and build up. Give the member thinking time and let them use their notes and their own code.
- Ask "how would you find out?" when they don't know something. Knowing how to investigate counts.
- Separate nervousness from understanding, and rephrase questions when needed.
- Keep a written record: questions asked, answers summarised, the modification outcome.
- For approved adjustments, a written follow-up may replace parts of the oral defence.

## 6. Preparing (for members)

- Re-read all your code the day before, especially the parts an AI tool helped you write.
- Practise explaining your most important decision to a friend in under a minute.
- Have the environment ready, the tests passing, and your report open.
- Know your weakest point, and say so. Honest limitation analysis scores well.
