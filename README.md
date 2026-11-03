<div align="center">

# CLBG Intelligence Assessment Hub

**Collective Lab Builders Group · Intelligence Track**

*Research → Build → Demonstrate → Evaluate → Grow*

| [Data Science](assessments/data-science/README.md) | [ML Engineering](assessments/ml-engineering/README.md) | [AI Engineering](assessments/ai-engineering/README.md) |
|:---:|:---:|:---:|
| [Tier 1](assessments/data-science/tier-1/README.md) · [Tier 2](assessments/data-science/tier-2/README.md) · [Tier 3](assessments/data-science/tier-3/README.md) | [Tier 1](assessments/ml-engineering/tier-1/README.md) · [Tier 2](assessments/ml-engineering/tier-2/README.md) · [Tier 3](assessments/ml-engineering/tier-3/README.md) | [Tier 1](assessments/ai-engineering/tier-1/README.md) · [Tier 2](assessments/ai-engineering/tier-2/README.md) · [Tier 3](assessments/ai-engineering/tier-3/README.md) |

[**Assessment catalogue**](CATALOGUE.md) · [Member handbook](docs/member-handbook.md) · [Assessor handbook](docs/assessor-handbook.md) · [Signature Challenges](signature-challenges/README.md)

</div>

---

## What this is

This repository is the **project-based competency assessment system** of the CLBG Intelligence Track. It contains a library of complete, rigorously specified, independently assessable projects. They are built to **develop** genuine capability, **evidence** it fairly, and help CLBG **form strong technical teams**.

Every assessment is a real project. Each one has:
- a problem worth solving;
- measurable objectives;
- precise requirements;
- documented data;
- objective acceptance criteria;
- a published 100-point rubric;
- submission instructions;
- extension challenges;
- integrity rules;
- a technical defence.

Most come with starter code, data generators and automated tests.

**About CLBG.** The Collective Lab Builders Group is a community for collaborative technical learning, experimentation, innovation and building practical solutions. The **Intelligence Track** is CLBG's home for data-driven and intelligent systems.

## The three subtracks

| Subtrack | The question it answers | Example units |
|---|---|---|
| [**Data Science**](assessments/data-science/README.md) | *Is this real, how big is it, how sure are we, and what should we do?* | Cleaning & data quality · Statistics · Causal inference · Forecasting · Visualisation · Pipelines |
| [**ML Engineering**](assessments/ml-engineering/README.md) | *Will this model keep working on real data, at real cost, after deployment?* | Foundations · Supervised & deep learning · CV · NLP · Evaluation · Efficient ML · MLOps · Responsible ML |
| [**AI Engineering**](assessments/ai-engineering/README.md) | *Can we build a dependable, secure product on top of foundation models, and prove it?* | Prompting & structured output · RAG · Agents · Context & memory · Evaluation · Security · Production architecture |

They overlap but are not interchangeable. The [competency framework](docs/competency-framework.md) sets out the shared foundations and the specialist competencies of each.

## The three tiers

Tiers ask **different kinds of question**. They are not just bigger projects.

| Tier | Name | The question |
|---|---|---|
| **1** | Foundation and Technical Fluency | Can you understand the fundamentals and produce a correct, explained, reproducible solution to a well-specified problem? |
| **2** | Applied Engineering and Independent Problem-Solving | Can you solve a realistic, partially specified problem, choosing and justifying your methods, testing your work and reasoning about its limits? |
| **3** | Advanced Engineering, Research and System Design | Can you take on an ambiguous, substantial problem, make research-informed decisions, experiment rigorously and defend the trade-offs? |

Placement is **per subtrack**. You can be Tier 1 in Data Science and Tier 3 in AI Engineering at the same time. See [tier definitions](docs/tier-definitions.md) and the [placement framework](docs/placement-framework.md).

## How to take an assessment

```text
 1. Choose          2. Register          3. Build              4. Submit          5. Defend & grow
 subtrack → tier →  open an "Assessment  in your own private   commit SHA via the  technical defence,
 unit → assessment  attempt" issue       repo; commit often    submission issue    feedback, placement
```

1. **Choose.** Browse a subtrack, then a tier, then a unit, and pick any assessment. Or search the [catalogue](CATALOGUE.md). **Nothing is sequential.** Prerequisites are advice, not gates.
2. **Register** your attempt with the issue template, and you'll be assigned a deadline and an assessor.
3. **Build** in a private repository named `clbg-<ID>-<username>`. Run the contract tests first.
4. **Submit** following the [submission guidelines](docs/submission-guidelines.md).
5. **Defend** your work in a short [technical defence](assessment-operations/oral-defense/technical-defence-guide.md), then receive feedback and an outcome.

The [member handbook](docs/member-handbook.md) walks you through all of it, including a self-check for choosing where to start.

## How assessments are structured

```text
assessments/<subtrack>/tier-<n>/units/<UNIT>-<name>/<ID>-<slug>/
├── README.md            # full specification: sections A–K + pedagogical design
├── rubric.md            # the 100-point rubric, public in full
├── metadata.yaml        # time, 6-dimensional difficulty, compute, technologies, status
├── starter/             # scaffolding (no solutions)          ┐
├── resources/           # data, schemas, generators           │ only where
├── tests/               # contract + requirement tests        │ useful
└── submission-template/ # report and AI-use declaration       ┘
```

**Difficulty has six dimensions**: Technical, Mathematical, Research, Engineering, Ambiguity and Resources. A project can be analytically subtle but technically light, or the other way round. Pick what stretches you.

**Assessment formats vary on purpose**: implementation, investigation, reverse engineering, research replication, comparative, optimisation, system design, debugging and forensics, open-ended, and integrated capstones.

## How evaluation works

| Evidence | Purpose |
|---|---|
| Public + **hidden** automated tests | Correctness, including on held-out or re-seeded data |
| Assessor reproduction | Results reappear from a clean environment |
| Rubric scoring (100 points, published) | Reasoning, methodology, quality, testing, limitations, communication |
| Technical defence | You understand, own and can extend your work |

Outcomes are *Meets requirements*, *Meets with minor deficiencies*, *Requires revision* or *Does not yet demonstrate competence*. **No placement rests on a single score**: gates for integrity, reproducibility and defence apply too. Revision and reassessment are always available. See the [evaluation framework](docs/evaluation-framework.md).

**AI tools are allowed, with disclosure**, within each assessment's rules. Understanding is verified through repository history, reproduction, walkthroughs, live modification and defence, never through AI detectors. See [assessment integrity](docs/assessment-integrity.md).

## Accessibility

- **Laptop first.** Every assessment runs on a CPU laptop with 4–8 GB RAM, or on a free notebook tier.
- **No paid APIs required.** AI Engineering assessments run on local open-weight models or provided mocks, and hosted APIs are optional.
- **Free and open tooling** throughout.

## Repository map

| Path | Contents |
|---|---|
| [`assessments/`](assessments/) | The three subtrack assessment banks (units × tiers + capstones) |
| [`cross-disciplinary/`](cross-disciplinary/README.md) | Shared foundations, integrated team challenges, advanced challenges |
| [`signature-challenges/`](signature-challenges/README.md) | CLBG flagship challenges for events and showcases |
| [`docs/`](docs/) | Policy, frameworks, handbooks, research ([standards report](docs/research/RESEARCH_AND_STANDARDS_REPORT.md), [benchmarks](docs/research/ELITE_EDUCATIONAL_BENCHMARKS.md), [legacy audit](docs/research/LEGACY_REPOSITORY_AUDIT.md)) |
| [`shared/`](shared/) | Unit registry, schemas, templates, [dataset registry](shared/datasets/DATASET_REGISTRY.md), [foundations](shared/foundations/README.md) |
| [`assessment-operations/`](assessment-operations/) | Defence guide, scoring templates, moderation, checklists |
| [`tools/`](tools/) | Validator, catalogue generator, link checker, test runner, dataset validator, rubric tools |

Confidential assessor material (reference solutions, hidden tests, marking guides) is kept in a separate **private assessor kit** repository.

## Contributing

Report problems with an **Assessment feedback** issue, propose new assessments, or improve tooling. See [CONTRIBUTING.md](CONTRIBUTING.md), the [authoring guide](docs/contributing/AUTHORING_GUIDE.md) and the [Code of Conduct](CODE_OF_CONDUCT.md). Maintainers should read the [maintenance guide](docs/contributing/maintenance.md).

## Licence

Code: MIT. Content and CLBG synthetic datasets: CC BY 4.0. Third-party datasets keep their own terms. See [LICENSE](LICENSE).

<sub>Educational approaches at institutions such as Harvard (CS50), MIT, Stanford, Carnegie Mellon and UC Berkeley informed the design of this system as benchmarks ([report](docs/research/ELITE_EDUCATIONAL_BENCHMARKS.md)). No affiliation with or endorsement by those institutions is claimed or implied.</sub>
