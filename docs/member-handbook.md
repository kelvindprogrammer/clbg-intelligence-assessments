# Member Handbook

Welcome to the CLBG Intelligence Track. This handbook tells you how to use this repository to **build real competence and prove it**. Read it once end to end. It takes about 15 minutes.

## 1. How the track works

```text
  Choose a subtrack ─▶ Choose a tier ─▶ Choose a unit ─▶ Choose an assessment
        │                                                       │
        │          Research → Build → Demonstrate → Evaluate → Grow
        ▼                                                       ▼
  Data Science · ML Engineering · AI Engineering        Submit → Defend → Feedback → Placement
```

- **Three subtracks:** [Data Science](../assessments/data-science/README.md), [ML Engineering](../assessments/ml-engineering/README.md) and [AI Engineering](../assessments/ai-engineering/README.md). Each one is a different discipline. See the [competency framework](competency-framework.md) for how they differ.
- **Three tiers per subtrack:** Foundation, Applied, Advanced. See [tier definitions](tier-definitions.md). Tiers are about the *kind* of thinking required, not about how big the project is.
- **Units** split each subtrack into coherent technical areas, for example *DS-03 Data Cleaning and Data Quality*.
- **Assessments** are complete, independent projects. Pick **one** from any unit you like.

**You do not have to go in order.** You can begin at any tier in any subtrack. Prerequisites tell you what you'll need to know. They're advice, not gates.

## 2. What an assessment looks like

Every assessment folder has:

| File | What it's for |
|---|---|
| `README.md` | The full brief: problem, requirements, data, deliverables, acceptance criteria, rubric summary, submission steps, extensions and integrity rules. **Read every section before you start.** |
| `rubric.md` | Exactly how you'll be scored. Nothing hidden is added on top. |
| `metadata.yaml` | Time estimate, difficulty dimensions, compute needs, technologies. |
| `starter/` | Scaffolding, where it's provided. It helps you start without doing the thinking for you. |
| `tests/` | Contract tests (pass from day one) and requirement tests (pass once you've implemented the work). Assessors also run hidden tests. |
| `submission-template/` | Report and declaration templates. |

**Reading the difficulty profile.** Six numbers from 1 to 5 tell you *where* the challenge lies: Technical, Mathematical, Research, Engineering, Ambiguity and Resources. A project rated "Math 4, Engineering 1" is a different kind of hard from one rated "Math 1, Engineering 4". Pick what stretches you.

## 3. Choosing where to start

Answer honestly. This is for you, and nobody records it.

**Data Science**
- Can you load a CSV with pandas, filter it, group it and plot it without looking everything up? *If not, start with the [foundations](../shared/foundations/README.md) and then Tier 1.*
- Can you explain a confidence interval and a p-value correctly, and say when each misleads? *If yes, and you've done real analysis projects, consider Tier 2.*
- Have you designed an analysis where the question itself was unclear, and defended your methodology to critics? *Consider Tier 3.*

**ML Engineering**
- Can you train and evaluate a scikit-learn model with a proper train/validation/test split, and explain overfitting? *Tier 1 territory.*
- Can you design a cross-validation scheme that avoids leakage for grouped or temporal data, and compare models statistically? *Tier 2.*
- Have you implemented models from papers, run ablations and deployed a monitored model? *Tier 3.*

**AI Engineering**
- Can you call an LLM API (or a local model), get structured output and handle errors? *Tier 1.*
- Have you built a RAG or tool-using system **and measured** how well it works? *Tier 2.*
- Can you design an evaluated, observable, secure AI system under cost and latency budgets, and defend the architecture? *Tier 3.*

If you're between two tiers, **choose the higher one**. An attempt that falls short can still establish the lower tier ([placement framework §3](placement-framework.md#3-tier-placement)).

## 4. Doing the work well

1. **Register** your attempt (an issue, using the template) so you get a deadline and an assessor.
2. **Read the whole brief**, especially sections D (requirements) and G (acceptance criteria).
3. **Run the contract tests first** (`pytest -m contract`). They should pass before you write a line of code.
4. **Commit as you go.** Your history is evidence of your process.
5. **Keep a decision log** (a simple `NOTES.md`): what you tried, what failed, and why you chose what you chose. It will make your report and your defence much easier.
6. **Ask conceptual questions** in the CLBG channels. Don't share assessment-specific code or answers.
7. **Use AI tools wisely,** within the rules in section K of the brief, and declare what you used. The defence will expose anything you don't understand.

## 5. Submitting and the defence

Follow the [submission guidelines](submission-guidelines.md). The defence is a conversation, not an exam you can fail by being nervous. Assessors want to see that **you** understand **your** work. Prepare by:
- re-reading your own code a day before;
- being ready to trace any input through your system;
- knowing your biggest limitation, and what you'd do next.

See the [technical defence guide](../assessment-operations/oral-defense/technical-defence-guide.md).

## 6. Feedback and growth

Every outcome comes with specific feedback.
- **Requires revision** means you're close: fix the listed points and resubmit.
- **Does not yet demonstrate competence** means you should build the missing foundations and try a *different* assessment in the same unit later.

Nobody is labelled permanently. Your placement updates as your evidence grows.

## 7. Turning assessments into portfolio evidence

Completed assessments make strong portfolio pieces if you:
- write a short public README (problem, approach, results, limitations) **without** revealing assessment-specific answers;
- make the repository public **only after** you've been assessed, and only if the assessment's section K allows it. Some assessments ask you to keep solutions private to protect future cohorts;
- link to it from your CV or GitHub profile, and be ready to discuss it in interviews. Your defence was practice.

A polished README isn't competence. The work and your understanding of it are what count.

## 8. Contributing back

Found an ambiguity, a broken link, or a better idea for an assessment? Open an **Assessment feedback** issue, or propose a new assessment. See [CONTRIBUTING.md](../CONTRIBUTING.md). Members who have reached Tier 2 or above in a subtrack can join the review panel for that subtrack.
