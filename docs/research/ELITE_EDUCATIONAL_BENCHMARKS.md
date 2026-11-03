# Elite Educational Benchmarks for the CLBG Intelligence Track

**Document:** `docs/research/ELITE_EDUCATIONAL_BENCHMARKS.md`
**Scope:** Intelligence Track: Data Science (DS), ML Engineering (MLE), AI Engineering (AIE); Tiers T1 Foundation, T2 Applied, T3 Advanced/Research
**Sources accessed:** November 2026 (2026-11-03)
**Status:** Research input to the assessment architecture. Benchmarks only; see Section 6.

---

## Contents

1. [Purpose and method](#1-purpose-and-method)
2. [Course-by-course benchmarks](#2-course-by-course-benchmarks)
   - 2.1 [Harvard CS50x](#21-harvard-cs50x-introduction-to-computer-science)
   - 2.2 [Harvard CS50 AI](#22-harvard-cs50s-introduction-to-artificial-intelligence-with-python)
   - 2.3 [MIT 6.3900 (and 6.036 archive)](#23-mit-63900-introduction-to-machine-learning-and-the-6036-ocw-archive)
   - 2.4 [MIT 6.100L](#24-mit-6100l-introduction-to-cs-and-programming-using-python-ocw)
   - 2.5 [MIT 18.S191 Computational Thinking](#25-mit-18s191-introduction-to-computational-thinking)
   - 2.6 [Stanford CS229](#26-stanford-cs229-machine-learning)
   - 2.7 [Stanford CS231N](#27-stanford-cs231n-deep-learning-for-computer-vision)
   - 2.8 [Stanford CS224N](#28-stanford-cs224n-natural-language-processing-with-deep-learning)
   - 2.9 [CMU 10-301/10-601](#29-cmu-10-30110-601-introduction-to-machine-learning)
   - 2.10 [CMU 17-445/645 Machine Learning in Production](#210-cmu-17-445645745-machine-learning-in-production)
   - 2.11 [Berkeley CS188](#211-uc-berkeley-cs188-introduction-to-artificial-intelligence)
   - 2.12 [Berkeley CS189/289A](#212-uc-berkeley-cs189289a-introduction-to-machine-learning)
   - 2.13 [Berkeley Data 100](#213-uc-berkeley-data-100-principles-and-techniques-of-data-science)
   - 2.14 [Full Stack Deep Learning](#214-full-stack-deep-learning-2022)
   - 2.15 [Made With ML](#215-made-with-ml)
   - 2.16 [fast.ai](#216-fastai-practical-deep-learning-for-coders)
3. [Cross-cutting synthesis: CLBG design principles](#3-cross-cutting-synthesis-clbg-design-principles)
4. [Adopt / Adapt / Avoid](#4-adopt--adapt--avoid)
5. [Mapping to CLBG tiers and assessment formats](#5-mapping-to-clbg-tiers-and-assessment-formats)
6. [Disclaimer](#6-disclaimer)
7. [References](#7-references)

---

## 1. Purpose and method

### 1.1 Purpose

CLBG is designing an assessment ecosystem for its Intelligence Track: placement and progression assessments across three subtracks and three tiers. This document benchmarks how well-regarded university and open courses in computer science, machine learning, data science and ML systems structure their assessments. The aim is to pull out design patterns CLBG can **adopt**, **adapt** to its context (a student-run community at a Nigerian university, with volunteer reviewers, uneven compute and connectivity, and no course credit), or **avoid**.

### 1.2 Method

- **Collection.** Official course websites, syllabi, policy pages, project pages and public course repositories were located through web search and direct navigation, then fetched and read. Search-engine snippets were used only to find pages, never as evidence.
- **Evidence rule.** A claim appears in this document only if it was verified on a page that was actually retrieved. Each claim cites a direct URL. Where a page could not be retrieved, or did not contain the information, that is stated explicitly as "not verified".
- **Retrieval note.** Several `web.stanford.edu` pages failed an automated TLS certificate check in the standard fetch tool. The CS224N home page and the CS229 Fall 2021 logistics archive were therefore retrieved with a standard HTTP client (`curl`) and read as plain text. The content is the same public page; only the retrieval route differs.
- **Paraphrase only.** No assignment text is reproduced. Assignments are described by structure (what is implemented, how it is checked, how it is weighted). Short policy phrases are quoted only where the exact wording matters.
- **Date.** All pages were accessed in November 2026. Course offerings change every term. Each section names the term the cited page describes.

### 1.3 Limits

- **Login walls.** MIT 6.3900's grading and collaboration policy pages, Stanford CS229's current logistics document (a Google Doc) and most Canvas, Ed and Gradescope material sit behind institutional login and were not examined.
- **Term drift.** Some evidence comes from archived terms (CS229 Fall 2021, CMU 10-601 Fall 2020, CS231N 2025 assignment page). It is labelled as archival and used to show patterns, not current policy.
- **No grader internals.** Public pages describe what autograders do (for example "public tests are sanity checks, hidden tests check correctness"). They do not publish test suites. No claim is made about how a grader works internally.
- **Pages not retrieved:** the MIT 6.3900 Fall 2024 introductory slides (timed out); the MIT OCW 6.100L assignments page (redirect loop); the CS229 `syllabus.html` page and the CMU 10-601 `syllabus.html` page (both HTTP 404); the CMU MLiP S2025 assignments page (HTTP 404). Nothing from these pages is claimed here.

---

## 2. Course-by-course benchmarks

Each entry uses the same nine items: (1) institution and course; (2) philosophy; (3) assessment structure; (4) engagement; (5) independent problem-solving; (6) competence evaluation; (7) lessons for CLBG; (8) influence on our architecture; (9) sources.

---

### 2.1 Harvard CS50x: Introduction to Computer Science

**1. Institution and course.** Harvard University, CS50x (2026 OpenCourseWare and edX edition).

**2. Philosophy.** CS50x is open to students with or without prior experience. It teaches problem-solving both with and without code, stresses correctness, design and style, and aims to teach students to program in general and to learn new languages on their own. The language sequence runs C → Python → SQL → HTML/CSS/JavaScript. [S1]

**3. Assessment structure.**
- Ten problem sets and a final project. [S2]
- Each problem is scored on correctness, checked by `check50`, and on style, checked by `style50`, usually combined as 3 × correctness + 1 × style. [S2]
- For a verified certificate, students need at least 70% on each submitted problem and on the final project. [S2]
- Within a problem set, students choose between a "less comfortable" and a "more comfortable" version of some problems (for example Mario, and Cash or Credit). If both are submitted, only the higher score counts. [S3]
- Self-paced, with one global deadline. [S2][S3]
- The final project is open-topic and must solve a real problem or matter to the student or their community. It needs more effort than a typical problem set, and groups of up to three must scale scope to team size. Deliverables are a demo video of up to three minutes with a fixed title card, a `README.md` (several hundred words minimum, about 750 suggested) explaining what each file does and the design decisions, and the code. [S4]

**4. Engagement.** Real-world framing and personal relevance in the final project. Tiered problem variants let stronger students choose harder work without leaving weaker students behind. [S3][S4]

**5. Independent problem-solving.** The honesty policy allows debugging help after the student has written the code, and pseudocode whiteboarding, but forbids viewing solutions before submitting and searching online for outright solutions. Only CS50's own AI tools are allowed for problem sets. Non-course AI tools that suggest or complete answers or code are not allowed. The final project, by contrast, allows AI tools if cited and the core work remains the student's. [S5][S4]

**6. Competence evaluation.** Automated correctness and style checks with fast feedback; a fixed minimum threshold per problem; a written README explaining design decisions plus a video demo for the capstone; academic honesty audits of submissions. [S2][S4] A "regret clause" lets students self-report a violation within 72 hours, after which the course generally imposes local sanctions rather than a disciplinary referral. [S5]

**7. Lessons for CLBG.**
- *Adopt:* separate correctness and style scores with an explicit published weighting; per-item minimum thresholds rather than one aggregate; README-plus-demo capstone.
- *Adapt:* "less/more comfortable" variants as tier-aware branches within one placement assessment.
- *Adapt:* AI-tool rules that differ by assessment type (strict for core skills, permitted with citation for capstones).
- *Adopt:* a regret or self-report clause to encourage honesty in a peer community.

**8. Influence on our architecture.** Basis for the T1 Implementation format (spec, then autograde, then style check), the dual-variant problem design, and the capstone deliverable bundle (code + README with design rationale + short video).

**9. Sources.** [S1] https://cs50.harvard.edu/x/ · [S2] https://cs50.harvard.edu/x/syllabus/ · [S3] https://cs50.harvard.edu/x/psets/1/ · [S4] https://cs50.harvard.edu/x/project/ · [S5] https://cs50.harvard.edu/x/honesty/

---

### 2.2 Harvard CS50's Introduction to Artificial Intelligence with Python

**1. Institution and course.** Harvard University, CS50 AI (OpenCourseWare and edX).

**2. Philosophy.** Hands-on projects teach the theory behind AI techniques (graph search, knowledge, uncertainty, optimization, learning, neural networks, language). Students get both library experience and the principles needed to design intelligent systems. Prerequisite: CS50x or at least one year of Python. [S6]

**3. Assessment structure.** Seven projects, numbered 0 to 6, alongside seven topic weeks. [S7] A representative project (Degrees) gives students distribution code with small and large datasets, a skeleton file and utilities. Students implement one specified function (plus helpers) and leave the rest unchanged. The specification fixes the return format, accepts any valid shortest path, and requires a defined value when no path exists. [S8]

**4. Engagement.** Concrete, recognizable problem domains, with an "Understanding" section that walks students through the data structures before they code. [S8]

**5. Independent problem-solving.** The scaffold limits scope to the algorithmic core. Hints point to lecture code and supplied utilities rather than giving solutions. A restriction on unauthorized imports stops students from outsourcing the core algorithm to a library. [S8]

**6. Competence evaluation.** Optional local correctness (`check50`) and style (`style50`) checks; submission through `submit50` or a specified Git branch; grading usually within minutes, with progress shown on a gradebook. [S8] Grading weights for CS50 AI were not found on the fetched pages.

**7. Lessons for CLBG.**
- *Adopt:* "implement only the core function inside a provided harness". This isolates the competence being measured and makes autograding reliable.
- *Adopt:* a small dataset for local testing and a large dataset for scale.
- *Adopt:* an explicit list of allowed and forbidden imports, which enforces first-principles implementation.

**8. Influence on our architecture.** Template for T1/T2 Implementation tasks (harness + one or two target functions + import allow-list + small/large data).

**9. Sources.** [S6] https://cs50.harvard.edu/ai/ · [S7] https://cs50.harvard.edu/ai/projects/ · [S8] https://cs50.harvard.edu/ai/projects/0/degrees/

---

### 2.3 MIT 6.3900: Introduction to Machine Learning (and the 6.036 OCW archive)

**1. Institution and course.** Massachusetts Institute of Technology, 6.390 (Fall 2026 site); predecessor 6.036 archived on MIT OpenCourseWare (Fall 2020).

**2. Philosophy.** Machine learning taught from an optimization perspective, covering linear and non-linear models for supervised, unsupervised and reinforcement learning, with a focus on gradient-based methods and neural architectures. [S9] The 6.036 archive emphasizes problem formulation, representation, over-fitting and generalization. [S10]

**3. Assessment structure (Fall 2026).** [S9]
- **Exercises:** short online items due before recitation and lab, to prepare students.
- **Labs:** synchronous 1.5-hour sessions in teams of two or three, each with several **checkoffs** (brief discussions with a staff member). If the first checkoff is done in session, the rest can be completed later in office hours.
- **Recitations:** pen-and-paper problem-solving in small sections.
- **Homework:** weekly, submitted on the course site (built on the open-source CAT-SOOP platform).
- **Exams:** two midterms and a final, all in person and written.
- Grading weights sit on a login-protected page and were **not verified**.

**4. Engagement.** A tight weekly rhythm (exercise → lab → recitation → homework). Small-team labs with live staff interaction.

**5. Independent problem-solving.** The exercises force first contact with the concepts before the collaborative lab; recitations rehearse pen-and-paper reasoning; individual homework and in-person exams check what each student can do alone. [S9]

**6. Competence evaluation.** Oral checkoffs (a student explains their work to staff), online-checked exercises and homework, and in-person written exams. [S9]

**7. Lessons for CLBG.**
- *Adopt:* short oral checkoffs as a competence signal that cannot be outsourced.
- *Adopt:* the "first checkoff in session, rest later" pattern, which keeps live sessions low-stakes but anchored.
- *Adapt:* pre-session exercises as gating micro-checks before collaborative work.

**8. Influence on our architecture.** Oral "explain-your-work" checkpoints in T2/T3 and on any high-stakes placement result. Pre-assessment readiness exercises.

**9. Sources.** [S9] https://introml.mit.edu/fall26/info · [S10] https://ocw.mit.edu/courses/6-036-introduction-to-machine-learning-fall-2020/

---

### 2.4 MIT 6.100L: Introduction to CS and Programming Using Python (OCW)

**1. Institution and course.** MIT, 6.100L, Fall 2022 (OpenCourseWare).

**2. Philosophy.** A slower-paced, full-semester version of 6.100A, explicitly to give students who have never programmed time to practise. It aims to show how computation helps solve problems and to build confidence in writing small, useful programs, whatever the student's major. [S11]

**3. Assessment structure.** Problem sets 45%; completion of mandatory **finger exercises** 10%; **microquizzes**, best 7 of 10, 45%. [S11] The assignments page could not be retrieved (redirect loop), so pset-level details are **not verified**.

**4. Engagement.** Frequent small wins through finger exercises; low-stakes repeated microquizzes with drops.

**5. Independent problem-solving.** Microquizzes carry nearly half the grade, which weights individually demonstrated skill heavily against take-home work. [S11]

**6. Competence evaluation.** Completion credit for practice; frequent short quizzes with a best-of-N rule. [S11]

**7. Lessons for CLBG.**
- *Adopt:* completion-graded practice that is separate from mastery-graded checks.
- *Adopt:* best-of-N micro-assessments, which reduce the impact of a single bad day.

**8. Influence on our architecture.** T1 micro-checks (short, repeatable, best-of-N) and a completion-credited practice bank separate from the placement score.

**9. Sources.** [S11] https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/pages/syllabus/

---

### 2.5 MIT 18.S191: Introduction to Computational Thinking

**1. Institution and course.** MIT, Computational Thinking (Fall 2024 site).

**2. Philosophy.** "Three fields, one course": computer science, mathematics and applications, built around real-world problems such as climate change. Interactive notebooks replace a textbook, so learners manipulate sliders and code directly. The course uses Julia with an emphasis on clear abstractions. [S12]

**3. Assessment structure.** Ten homework sets across three modules (images and transformations; social and data science; climate science), with tasks such as building image filters and convolutions, text generation and epidemic/climate models. The page mentions "automatic checks" only for one homework. Grading policy and any final project are **not described** on the fetched page. [S12]

**4. Engagement.** Live, manipulable notebooks; socially meaningful problem domains. [S12]

**5. Independent problem-solving.** Students build models (for example epidemic simulations) rather than call black-box functions. [S12]

**6. Competence evaluation.** Not verifiable from public pages beyond the reference to automatic checks.

**7. Lessons for CLBG.**
- *Adapt:* notebook assessments with embedded automatic checks and interactive exploration, framed around local problems (for example Nigerian public-health, agriculture or energy data).

**8. Influence on our architecture.** DS Investigation tasks delivered as notebooks with inline sanity checks and a locally relevant problem framing.

**9. Sources.** [S12] https://computationalthinking.mit.edu/Fall24/

---

### 2.6 Stanford CS229: Machine Learning

**1. Institution and course.** Stanford University, CS229 (current public home page: Summer 2026; detailed policies from the Fall 2021 logistics archive).

**2. Philosophy.** Broad and mathematical. Covers supervised learning (generative, parametric and non-parametric, neural networks), unsupervised learning, learning theory and reinforcement learning. Prerequisites are Python/NumPy programming, probability, multivariable calculus and linear algebra. An ungraded "Pset0" is offered as a starting point. [S13]

**3. Assessment structure (Fall 2021 archive).** Four assignments mixing written questions and Python programming (45% combined, weighted by point value), a midterm (15%) and a final project (40%). [S14] The current home page lists problem sets plus final project proposal, milestone, report and poster session in its schedule. [S13] The current logistics document is a Google Doc and was not examined.

**4. Engagement.** An open-choice term project; pair submissions allowed for homework in the archived term. [S14]

**5. Independent problem-solving.**
- Study groups are encouraged, but each student (or pair) must write the solution independently, without referring to notes from the joint session, and must understand it well enough to reconstruct it alone. [S14]
- Pairs are warned not to divide up the work, because the midterm tests each individual. [S14]
- Office-hour staff are discouraged from debugging large blocks of student code. Students are expected to do their own groundwork first. [S14]

**6. Competence evaluation.** Gradescope submission; plagiarism detection against current and past submissions; an in-person proctored exam (the current page notes participation in an in-person proctoring pilot). [S13][S14]

**Late policy (archived term).** Three free late days for homework, proposal and milestone, none for the final report or poster; 20% penalty per late day afterwards; nothing accepted more than three days late. [S14]

**7. Lessons for CLBG.**
- *Adopt:* the "reconstruct it yourself" collaboration standard.
- *Adopt:* project stage gates (proposal → milestone → report → poster/demo).
- *Adopt:* late allowances valid for intermediate milestones but never for the final deliverable.

**8. Influence on our architecture.** T3 capstone milestone structure; collaboration policy language; a "no grace on final deliverable" rule.

**9. Sources.** [S13] https://cs229.stanford.edu/ · [S14] https://cs229.stanford.edu/logistics_faq.html-backup-fall21

---

### 2.7 Stanford CS231N: Deep Learning for Computer Vision

**1. Institution and course.** Stanford University, CS231N (Spring 2026 site; 2025 assignment page).

**2. Philosophy.** Build vision models up from the components. Assignments are in Python/NumPy and move from kNN and softmax classifiers to CNNs, RNN/transformer captioning, self-supervised learning and diffusion. [S15][S16]

**3. Assessment structure.** Assignments 45% (12% / 18% / 15%), midterm 20%, final project 35%, plus up to 3% participation extra credit. [S15][S16]
- **Assignments** contain programming parts and written questions. [S16] Assignment 1 (2025) spans five notebooks (kNN, softmax, two-layer net, image features versus raw pixels, fully connected nets), stresses efficient vectorized NumPy, and uses train/validation/test splits for tuning. Students submit a code zip plus a PDF of the executed notebooks with visible outputs. [S17]
- **Final project:** a 200–400-word proposal (1%); three 10-minute staff check-ins, each with a 2–5 slide deck (problem and related work with at least three papers; technical approach; preliminary results); a 6–8-page conference-style report (20%) with suggested section weights (methods 30%, experiments 30%, introduction, related work and data 10% each, conclusion 5%, writing 5%); and a poster session (5%). [S18]
- **Late days:** four free (at most two per assignment), 25% per day after that, none on the final report. [S15]

**4. Engagement.** Two project tracks: applications (a real domain problem) and models (building or adapting a model). Past reports are offered as exemplars. A public poster session. [S18]

**5. Independent problem-solving.** Study groups are allowed, but solutions must be written independently of group notes and independently of any AI output. The nature of AI collaboration must be declared, and using AI to substantially complete sections violates the Honor Code. TAs do not review code. [S16] For projects, AI-generated code must be documented (plans, prompts, transcripts, labels), and writing report content with generative AI is prohibited; editing and formatting help is allowed. [S18]

**6. Competence evaluation.** Gradescope submission of code plus rendered notebook; check-ins graded on **progress, clarity and robustness**, where robustness covers sound reasoning, validated approaches, acknowledged limitations and justified design choices; a weighted report rubric. [S16][S17][S18]

**7. Lessons for CLBG.**
- *Adopt:* the check-in rubric (progress / clarity / robustness) almost verbatim as a CLBG milestone rubric.
- *Adopt:* published report section weights that put most of the credit on methods and experiments.
- *Adopt:* "submit executed notebook with outputs visible" for reproducibility evidence.
- *Adapt:* AI-use disclosure requirements (prompt and transcript logs) for T3.

**8. Influence on our architecture.** T3 Replication and Capstone report templates; milestone rubric; AI-disclosure appendix.

**9. Sources.** [S15] https://cs231n.stanford.edu/ · [S16] https://cs231n.stanford.edu/assignments.html · [S17] https://cs231n.github.io/assignments2025/assignment1/ · [S18] https://cs231n.stanford.edu/project.html

---

### 2.8 Stanford CS224N: Natural Language Processing with Deep Learning

**1. Institution and course.** Stanford University, CS224N (Winter 2026 site).

**2. Philosophy.** Weekly assignments aim to improve both theoretical understanding and practical skills. The final project applies these skills to an in-depth application. [S19]

**3. Assessment structure.** [S19]
- **Assignments (48%):** four, each with written questions and programming parts.
- **Final project (49%):** either the **Default Final Project** (implement parts of a minimalist GPT-2 in PyTorch and apply it to three downstream tasks) or a **Custom Final Project**. Credit splits into proposal 8%, milestone 6%, poster 3%, report 32%.
- **Participation (3%):** guest-lecture attendance or reaction paragraphs, surveys and "karma" for helping others.
- **Late days:** six, at most three per assignment, then 1% off the course grade per extra day. Late days for the proposal and milestone are individual; teams may pool them for the final report.
- **Regrades:** via Gradescope within three days.

**4. Engagement.** Students choose between a scaffolded default and a self-directed custom project. Custom teams get a mentor; default teams do not. [S19]

**5. Independent problem-solving.** Students must not look at solutions or implementations online. TAs may not look at final-project code. Teams must state which parts of a project are their own work and may never use another group's code. Generative AI may be used as a "collaborator", but soliciting answers directly, copying solutions, or using AI to substantially complete work violates the Honor Code. [S19]

**6. Competence evaluation.** Written + programming assignments on Gradescope; automated similarity detection; staged project deliverables with the report carrying most of the weight. [S19]

**7. Lessons for CLBG.**
- *Adopt:* the default-or-custom capstone choice.
- *Adopt:* contribution statements that separate a student's own work from borrowed code.
- *Adopt:* a weighting that puts most capstone credit on the final report while still rewarding early stages.

**8. Influence on our architecture.** AIE/MLE T3 capstone: a "default" path (for example implement a small transformer component and fine-tune it on a fixed task) alongside a custom path with a mentor.

**9. Sources.** [S19] https://web.stanford.edu/class/cs224n/ (retrieved via `curl`; see Section 1.2)

---

### 2.9 CMU 10-301/10-601: Introduction to Machine Learning

**1. Institution and course.** Carnegie Mellon University, 10-301/10-601 (Spring 2026 site; Fall 2020 site for comparison).

**2. Philosophy.** Written work covers derivations, "on-paper" implementations and theory. Programming work implements ML algorithms from scratch in Python, with emphasis on applications, end-to-end systems and experimental design. [S20]

**3. Assessment structure (Spring 2026).** [S20][S21]
- Homework 35%; coding labs 5% (lowest dropped); three in-class **programming quizzes** 10%; three exams at 15% each; participation 5%.
- Nine homework assignments (decision trees through reinforcement learning), most combining written and programming parts; three are written only. Each programming quiz covers two programming assignments. [S21]
- **Slot A / Slot B:** each homework has a human-only Slot A submission, then feedback, then an AI-assisted Slot B submission graded only on the questions missed in Slot A. The final score formula rewards Slot A performance, including a bonus if Slot A scores above 50%. [S20]
- Written answers are typeset in LaTeX against a template, with small penalties for misaligned uploads. [S20]

**4. Engagement.** Pair coding labs encourage human collaboration. Immediate autograder feedback. [S20]

**5. Independent problem-solving.** Slot A forbids all generative AI, including AI-enabled IDEs and code agents. Coding labs never allow AI assistants. Slot B allows AI and full collaboration to fix earlier mistakes. Submitting AI-assisted work to Slot A is an integrity violation: a 100% penalty the first time, failing the course the second time. [S20]

**6. Competence evaluation.** Programming is autograded on a VM with immediate feedback. Submissions scoring under 75% are hand-graded for partial credit, capped at 75% of the autograder points. Programming quizzes in class check individual coding ability. [S20]

**Late policy.** Six grace days (not for HW1), at most three per assignment; Slot B late credit drops 75% → 50% → 25% over three days; no late Slot A. [S20] For comparison, the Fall 2020 offering used homework 50%, three exams 45% and participation 5%, with six slip days. [S22]

**7. Lessons for CLBG.**
- *Adopt:* the Slot A / Slot B model. It is the clearest published design for measuring unaided competence while still letting students learn with AI.
- *Adopt:* autograder plus capped human partial credit, so a near-miss is not scored zero but cannot outscore a correct solution.
- *Adopt:* short supervised programming quizzes that verify the same skills as take-home work.

**8. Influence on our architecture.** Core placement design: an unaided attempt (scored) followed by an assisted revision (scored only on missed items). Capped partial credit when autograder results are low.

**9. Sources.** [S20] https://www.cs.cmu.edu/~mgormley/courses/10601/ · [S21] https://www.cs.cmu.edu/~mgormley/courses/10601/coursework.html · [S22] https://www.cs.cmu.edu/~10601/

---

### 2.10 CMU 17-445/645/745: Machine Learning in Production

**1. Institution and course.** Carnegie Mellon University, Machine Learning in Production (MLiP) (Spring 2025 and Fall 2026 materials).

**2. Philosophy.** How to turn ML models into reliable, responsible software products and operate them in production: deployment, testing, MLOps, scaling, and qualities beyond accuracy (safety, fairness, explainability, security), plus teamwork between software engineers and data scientists. Aimed at students with some ML and Python experience. [S23]

**3. Assessment structure.**
- **Fall 2026:** individual assignments 35%, group project 30%, midterms and participation 25%, labs 10%. [S24]
- **Spring 2025:** individual assignments 35%, group project 30%, midterms 15%, labs 10%, reading quizzes 5%, participation 5%. [S23]
- **Group project:** teams build a movie-recommendation service through milestones covering modeling and first deployment; infrastructure quality; monitoring and continuous delivery; and fairness, security and feedback loops. A final report and video follow. [S23] The Fall 2026 README describes the service as serving about a million users and running live for several weeks, with a 30-minute TA-mentor meeting after each milestone. [S24]
- **Specification grading:** every requirement is pass/fail with no partial credit. Point breakdowns are published so students can choose which parts to skip. Some rubric items require a verbal explanation to staff. [S23][S24]
- **Labs:** pass/fail, shown to a TA in session. Collaboration is allowed, but each student must explain their own solution. [S24]

**4. Engagement.** A realistic, live, long-running system that changes under the team; explicit choice over which parts to attempt. [S23][S24]

**5. Independent problem-solving.** AI tools are allowed and recommended, but students are solely responsible for correctness. Plausible but wrong output earns no credit. AI is prohibited in exams, offline quizzes and live conversations with staff. Sharing code or text with other students is not allowed. [S24]

**6. Competence evaluation.** Spec-based pass/fail rubrics; verbal explanation items; TA mentor debriefs; peer ratings of "team citizenship" that can adjust individual grades; high grade cutoffs (A+ at 99% or above). [S23][S24]

**Late/resubmission tokens.** Eight individual tokens: one day late costs 1; a resubmission with reflection costs 3 and returns 90% of the improvement (Fall 2026). Eight separate team tokens. 15% penalty per started day once tokens run out. [S23][S24]

**7. Lessons for CLBG.**
- *Adopt:* specification grading with pass/fail criteria. Volunteer reviewers can apply it consistently and quickly.
- *Adopt:* the token economy for late work and resubmission with reflection.
- *Adopt:* peer citizenship ratings for team projects.
- *Adapt:* a live, evolving system as the MLE/AIE T3 project, scaled down to CLBG infrastructure.

**8. Influence on our architecture.** MLE and AIE System Design and Capstone formats; the resubmission policy; the peer-assessment instrument; "explain it to a reviewer" rubric items.

**9. Sources.** [S23] https://mlip-cmu.github.io/s2025/ · [S24] https://github.com/mlip-cmu/f2026 · [S25] https://mlip-cmu.github.io/

---

### 2.11 UC Berkeley CS188: Introduction to Artificial Intelligence

**1. Institution and course.** UC Berkeley, CS188 (Fall 2025).

**2. Philosophy.** Not stated as a philosophy on the fetched pages. The structure (game-based projects with bundled autograders) indicates learning by implementing classic AI algorithms in a rich, visual environment. [S26][S27]

**3. Assessment structure.** Projects 25%, homework 20%, midterm 20%, final 35%. [S27]
- Five projects (plus an optional Project 0), autograded for correctness on Gradescope, with unlimited resubmission before the deadline. Pairs are allowed after Project 0. No slip days. [S27]
- Ten homeworks (one dropped), each with **Part A** (electronic, autograded, resubmittable) and **Part B** (written, graded for completion and effort on a 0/5/8/10 scale, plus a **self-assessment** against the staff solution due a week later). [S27]
- In Project 1 (Search), students edit two files (search algorithms and search agents) and leave the engine, utilities and test cases untouched. A bundled local autograder runs all questions, one question or one test. Points are allocated per question (25 total). Heuristic questions are scored in tiers by nodes expanded, and an inconsistent heuristic earns no credit. There is an optional extra-credit tier. [S28]

**4. Engagement.** Visual game environment; performance-tier scoring (fewer nodes means more points) and extra-credit tiers reward optimization beyond correctness. [S28]

**5. Independent problem-solving.** Automatic code generators (for example ChatGPT, Copilot) are "absolutely forbidden." Code may not be shared. [S27] Submissions are compared against others' code for logical redundancy. [S28]

**6. Competence evaluation.** The autograder gives the score, but "correctness of your implementation" is the final judge, and staff may review submissions individually. [S28] Written work uses self-assessment against model solutions. [S27]

**7. Lessons for CLBG.**
- *Adopt:* a local autograder shipped with the task, with per-question runs.
- *Adopt:* performance-tiered scoring for Optimization tasks.
- *Adopt:* self-assessment against a model solution for written work. It builds metacognition and reduces reviewer load.
- *Adopt:* an explicit statement that the autograder is not the final arbiter.

**8. Influence on our architecture.** Optimization format (tiered thresholds); local test harness design; self-assessment step after written components.

**9. Sources.** [S26] https://inst.eecs.berkeley.edu/~cs188/fa25/ · [S27] https://inst.eecs.berkeley.edu/~cs188/fa25/policies/ · [S28] https://inst.eecs.berkeley.edu/~cs188/fa25/projects/proj1/

---

### 2.12 UC Berkeley CS189/289A: Introduction to Machine Learning

**1. Institution and course.** UC Berkeley, CS189/289A (Fall 2026).

**2. Philosophy.** A rigorous foundation in ML theory, preparation for advanced AI coursework, and practical implementation of algorithms. [S29] The syllabus combines mathematical rigor with practical application. [S31]

**3. Assessment structure.** CS189: homework 35%, midterm 25%, final 30%, participation 10%. At least 50% weighted on the exams is required to pass. CS289 adds a 10% graduate team project. [S30] Five homeworks, each three weeks long, with a **Warmup** (shorter, introduces concepts) and a **Main** part (deeper application), mixing derivations and code, submitted to separate written and coding portals. [S30][S31] Ten slip days, at most four per homework. [S30]

**4. Engagement.** The Warmup-then-Main ramp lowers the barrier to starting. [S31]

**5. Independent problem-solving.** Generative AI is a "consulting tool, not an author". It is allowed with citation for error messages, concepts and planning, and for tab completion only if the student could reproduce the result. It is not allowed for pasting assignment text, "vibe coding" or agents implementing assignments, or summarizing one's own analysis. An acknowledgement (tool, purpose, use) is required. [S31]

**6. Competence evaluation.** **Public tests are basic sanity checks; hidden tests check correctness.** Some parts are graded manually. Staff may **randomly require a Zoom interview or walkthrough**, and a student who cannot explain their work may receive zero. [S31] An exam floor gates passing. [S30]

**7. Lessons for CLBG.**
- *Adopt:* the public-sanity / hidden-correctness test split.
- *Adopt:* random oral walkthroughs as an integrity and competence check.
- *Adopt:* the Warmup → Main ramp within each assessment.
- *Adopt:* an individually verified floor (for example a minimum on the supervised component) before a tier is awarded.

**8. Influence on our architecture.** Test-suite design for all autograded formats; random viva sampling; tier-award gating rules.

**9. Sources.** [S29] https://eecs189.org/ · [S30] https://eecs189.org/fa26/faq/ · [S31] https://eecs189.org/fa26/syllabus/

---

### 2.13 UC Berkeley Data 100: Principles and Techniques of Data Science

**1. Institution and course.** UC Berkeley, Data 100 / Data 200 (Fall 2026).

**2. Philosophy.** The full data science lifecycle: question formulation, data cleaning, exploratory analysis and visualization, statistical inference and prediction, and decision-making. Prepares students for upper-division work and data science careers. [S32]

**3. Assessment structure (Fall 2026).** [S33]
- Assignments (homeworks and projects; long-form, combining theory and practice, with projects synthesizing several topics) 10%; discussion 5% (optional track); lecture participation 5%; prerequisite quiz 5%; three computer-based "Quizterms" at 15% each; final 30%.
- Passing requires at least 50% weighted on the quizterms and final.
- 12 slip days (at most four per assignment), applied automatically; no homework drops.

**4. Engagement.** Projects that synthesize the lifecycle across topics. [S33]

**5. Independent problem-solving.** Using LLMs to generate written or code solutions is prohibited unless an assignment allows it. Pasting assignment text into an LLM counts as cheating. Asking about error messages, library behaviour or concepts is allowed. Collaborators must be listed in notebooks. Plagiarism detection runs on all assignments. [S33]

**6. Competence evaluation.** **Autograded work has public tests (mainly sanity checks) and hidden tests (correctness).** Written portions go to a separate portal for manual grading. A failing autograder test is a logistical error, not grounds for an accommodation. Proctored computer-based quizterms carry most of the grade. [S33]

**7. Lessons for CLBG.**
- *Adopt:* public/hidden test split; a separate written-reasoning portal.
- *Adopt:* heavy weight on supervised assessments when take-home integrity is uncertain.
- *Adapt:* computer-based timed "quizterms" as CLBG placement checkpoints run in a lab.

**8. Influence on our architecture.** DS T1/T2 Investigation format (notebook + hidden tests + written interpretation); supervised placement sessions.

**9. Sources.** [S32] https://ds100.org/ · [S33] https://ds100.org/fa26/syllabus/

---

### 2.14 Full Stack Deep Learning (2022)

**1. Institution and course.** Full Stack Deep Learning (FSDL), 2022 course (independent, free online).

**2. Philosophy.** Building an entire ML application "from soup to nuts". It covers when to use ML, development infrastructure, troubleshooting and testing, data management, deployment, continual learning, foundation models, team and project management, and ethics. [S34]

**3. Assessment structure.** Weekly lecture + lab. The labs build one text-recognition application across the course (experiment tracking, testing and profiling, annotation, web deployment, monitoring). A team project runs alongside: group formation, proposals, about four weeks of build time, then presentations. [S34] No grading criteria are published. [S34][S35]

**4. Engagement.** Labs accumulate into one working product. The project showcase lists about 27 team projects with live demos, repositories, slides or posters. [S35]

**5. Independent problem-solving.** Self-chosen products, scoped and built by teams. [S35]

**6. Competence evaluation.** Public demos and presentations. No published rubric. [S34][S35]

**7. Lessons for CLBG.**
- *Adopt:* the "one application grows across labs" design for MLE T2.
- *Adopt:* a public showcase of demos and repositories as a motivation and portfolio channel.
- *Avoid:* project assessment with no published rubric.

**8. Influence on our architecture.** MLE progression path; capstone showcase event; deployment evidence (live demo link) as a deliverable.

**9. Sources.** [S34] https://fullstackdeeplearning.com/course/2022/ · [S35] https://fullstackdeeplearning.com/course/2022/project-showcase/

---

### 2.15 Made With ML

**1. Institution and course.** Made With ML (independent, open MLOps and foundations curriculum).

**2. Philosophy.** ML as software engineering. Build a first-principles understanding of each concept before coding, apply software-engineering best practices, connect MLOps components into an end-to-end system, and move from development to production without changing code. [S36]

**3. Assessment structure.** No formal assessment is described. The curriculum runs through design, data, model, develop, utilities, testing (code, data and models), reproducibility (versioning) and production (jobs and services, CI/CD, monitoring). A Foundations track covers Python through transformers. [S36]

**4–6. Engagement / problem-solving / evaluation.** Not described as assessment. The page names testing of **code, data and models** as a dedicated stage. [S36]

**7. Lessons for CLBG.**
- *Adopt:* "test code, data and models" as three evidence categories in MLE rubrics.
- *Adopt:* "first principles before code" as a T1/T2 sequencing rule.

**8. Influence on our architecture.** MLE rubric dimensions (tests, reproducibility, CI); the curriculum ordering behind tier boundaries.

**9. Sources.** [S36] https://madewithml.com/

---

### 2.16 fast.ai: Practical Deep Learning for Coders

**1. Institution and course.** fast.ai, Practical Deep Learning (independent, free).

**2. Philosophy.** Top-down and code-first. Start with a complete, state-of-the-art model on a real problem, then explain the deeper layers later; context before abstract math. Advanced math, big data and expensive hardware are not needed for strong results. [S37]

**3. Assessment structure.** No formal assessment is described. [S37] Lesson 1 asks learners to run the notebooks (including one that builds a model from their own data), read the book chapter, and check answers to the chapter questions against published solutions. [S38] By the end of lesson 2, learners build and deploy a model on data they collected. [S37]

**4. Engagement.** Something working from day one; deploying on one's own data. [S37][S38]

**5. Independent problem-solving.** Learners collect their own datasets and share projects on the forums. [S37]

**6. Competence evaluation.** Self-check against published solutions; community feedback. [S38]

**7. Lessons for CLBG.**
- *Adapt:* a top-down "working baseline first" opening for AIE T1 tasks, where learners get a working pipeline and must extend or explain it.
- *Avoid:* relying on self-assessment alone for placement decisions.

**8. Influence on our architecture.** Reverse-engineering format (start from a working system); "bring your own data" extensions.

**9. Sources.** [S37] https://course.fast.ai/ · [S38] https://course.fast.ai/Lessons/lesson1.html

---

## 3. Cross-cutting synthesis: CLBG design principles

These are the principles CLBG will adopt. Each cites the benchmark evidence it rests on.

**P1. Specification + autograded core + open-ended extension.** Every technical assessment starts with a precise specification and an autograded core, then offers an open-ended or performance-tiered extension. *Evidence:* CS50 specs and `check50` [S2][S8]; CS188 per-question points with extra-credit tiers [S28]; CS50 tiered variants [S3].

**P2. Public sanity tests, hidden correctness tests.** Learners get local tests that confirm format and basic behaviour. Scoring uses hidden tests. *Evidence:* Data 100 [S33]; CS189 [S31]; CS188 bundled local autograder [S28].

**P3. The autograder is evidence, not the verdict.** Reviewers may override autograder results. Low autograder scores can earn capped manual partial credit. *Evidence:* CS188 "correctness of your implementation is the final judge" [S28]; CMU 10-601 hand-grading below 75%, capped at 75% [S20].

**P4. Separate correctness from style and design, with published weights.** *Evidence:* CS50 3 × correctness + 1 × style [S2]; CS231N report section weights [S18].

**P5. First-principles implementation before library use.** At T1/T2, the core algorithm is implemented in NumPy or plain Python under an import allow-list. Libraries come at the next tier. *Evidence:* CMU 10-601 from-scratch programming [S20]; CS231N vectorized NumPy [S17]; CS50 AI unauthorized-import restriction [S8]; Made With ML first principles before code [S36].

**P6. Every submission explains its reasoning in writing.** Code comes with a written component: derivation, interpretation, design rationale or a limitations statement. *Evidence:* written + programming in CS229 [S14], CS224N [S19], CS231N [S16], 10-601 [S20], CS189 [S31]; CS50 README with design decisions [S4].

**P7. An unaided attempt first, then an assisted revision.** Placement scores rest mainly on an AI-free, individual first attempt. A second, AI-permitted revision is scored only on the items missed. *Evidence:* CMU 10-601 Slot A / Slot B [S20].

**P8. AI-use rules differ by format and are always disclosed.** Strict for core-skill checks and supervised sessions; permitted with citation and logs for capstones and system work; never allowed in oral checks. *Evidence:* CS50 [S4][S5]; CS231N [S16][S18]; CS224N [S19]; CS189 [S31]; MLiP [S24]; Data 100 [S33].

**P9. Oral checkoffs and random walkthroughs.** Short "explain your work" conversations verify competence at T2/T3 and on any high placement result. A random sample of other submissions gets the same. *Evidence:* MIT 6.390 checkoffs [S9]; MLiP verbal rubric items and lab explanations [S24]; CS189 random interviews [S31].

**P10. Milestone checkpoints for projects.** Proposal → check-ins → final report → demo or poster, each with its own weight. *Evidence:* CS231N [S18]; CS224N [S19]; CS229 [S13][S14]; MLiP milestones [S23]; FSDL [S34].

**P11. Milestone rubric: progress, clarity, robustness.** *Evidence:* CS231N check-in criteria [S18].

**P12. Specification (pass/fail) grading for system-building work.** Binary criteria that a volunteer reviewer can apply consistently, with point values published so learners can choose what to attempt. *Evidence:* MLiP [S23][S24].

**P13. Late and resubmission policy as a token budget.** A fixed budget of tokens buys short extensions or a resubmission with a reflection, at reduced credit (for example 90% of the improvement). Tokens never apply to the final capstone deliverable. *Evidence:* MLiP tokens [S23][S24]; CS229 and CS231N no late days on the final report [S14][S15]; CS224N individual vs pooled late days [S19].

**P14. Individually verified floor before a tier is awarded.** A minimum score on the supervised or individual component is required regardless of take-home performance. *Evidence:* CS189 50% exam floor [S30]; Data 100 50% floor [S33]; CS50 70% per problem [S2].

**P15. Choice of a default or a custom capstone.** A scaffolded default task with a fixed evaluation, or a mentored custom project of equal rigor. *Evidence:* CS224N [S19]; CS231N applications vs models tracks [S18].

**P16. Contribution statements and citation of external code.** Teams declare who did what and what was borrowed. *Evidence:* CS224N [S19]; CS231N [S18]; MLiP peer citizenship ratings [S23][S24].

**P17. Reproducibility evidence is a deliverable.** Executed notebooks with visible outputs, pinned environments, and tests of code, data and models. *Evidence:* CS231N executed-notebook PDF [S17]; Made With ML testing and versioning stages [S36].

**P18. Tiered or performance-scaled scoring for optimization tasks.** *Evidence:* CS188 node-expansion tiers [S28].

**P19. Self-assessment against model solutions for written work.** *Evidence:* CS188 Part B self-assessment [S27]; fast.ai chapter questions with solutions [S38].

**P20. Real, local and meaningful problem framing, with public showcase.** *Evidence:* CS50 final project relevance to the student's community [S4]; 18.S191 real-world problems [S12]; FSDL showcase [S35]; fast.ai own-data deployment [S37].

---

## 4. Adopt / Adapt / Avoid

| Practice | Decision | Rationale for CLBG | Sources |
|---|---|---|---|
| Spec + autograded core (check50-style) | **Adopt** | Scales with few reviewers; gives fast feedback | [S2][S8] |
| Public sanity tests + hidden correctness tests | **Adopt** | Stops tuning to visible tests | [S31][S33] |
| Autograder not final; capped manual partial credit | **Adopt** | Fair on near-misses; keeps a ceiling | [S20][S28] |
| Correctness and style scored separately | **Adopt** | Signals that engineering quality counts | [S2] |
| Import allow-lists for first-principles tasks | **Adopt** | Measures understanding, not library recall | [S8] |
| Slot A (unaided) / Slot B (assisted revision) | **Adopt** | Best-published balance of integrity and learning with AI | [S20] |
| Oral checkoffs / random walkthroughs | **Adopt** | Cannot be outsourced; cheap at small scale | [S9][S24][S31] |
| Milestone rubric (progress, clarity, robustness) | **Adopt** | Clear, reusable, reviewer-friendly | [S18] |
| Specification (pass/fail) grading for systems work | **Adopt** | Consistent across volunteer reviewers | [S23][S24] |
| Token-based late and resubmission policy | **Adopt** | Flexibility under unreliable power and internet, without endless extensions | [S23][S24] |
| Default vs custom capstone | **Adopt** | Supports both scaffolded and ambitious learners | [S19] |
| Contribution statements; peer citizenship ratings | **Adopt** | Team fairness | [S19][S24] |
| Self-report ("regret") clause | **Adopt** | Encourages honesty in a peer community | [S5] |
| Less/more comfortable variants | **Adapt** | Use as placement branches that route to T1 vs T2 | [S3] |
| CS231N/CS224N report weighting | **Adapt** | Scale down to 3–5 pages for student capacity | [S18][S19] |
| Live long-running production project (MLiP) | **Adapt** | Scale to CLBG hosting; shorter live window | [S23][S24] |
| Proctored computer-based quizterms | **Adapt** | Run as supervised lab sessions, with offline fallback | [S33] |
| AI disclosure with prompt and transcript logs | **Adapt** | Require at T3; lighter disclosure at T1/T2 | [S18][S31] |
| Interactive notebooks with embedded checks | **Adapt** | Use Python/Jupyter rather than Julia/Pluto | [S12] |
| Top-down "working baseline first" | **Adapt** | Use for Reverse-engineering and AIE onboarding, not for T1 core skills | [S37] |
| Blanket AI ban on all work | **Avoid** | Hard to enforce in an open community and misaligned with AIE practice; prefer format-specific rules (P8) | [S27] vs [S20][S24] |
| Unrestricted AI with no unaided component | **Avoid** (for placement) | Fine for MLiP's production focus, but cannot show unaided competence for tier placement | [S24] |
| Project assessment with no published rubric | **Avoid** | Inconsistent and opaque | [S34][S35] |
| Self-assessment as the only evidence | **Avoid** | Not valid for placement | [S38] |
| Heavy dependence on large-GPU compute | **Avoid** | Equity; members' compute access varies. Benchmarks depend on donated compute | [S19] (sponsor compute credits) [S35] (donated GPUs) |
| Language-agnostic programming choice in assessments | **Avoid** at T1 | Reviewer load; fix Python for comparability | [S22] |

---

## 5. Mapping to CLBG tiers and assessment formats

### 5.1 Tier mapping

| Tier | Benchmark analogues | Principles applied | Evidence of competence |
|---|---|---|---|
| **T1 Foundation** | CS50x, CS50 AI, 6.100L, CS188 projects, Data 100 homework | P1, P2, P4, P5, P6 (short), P7, P14, P19 | Autograded core with hidden tests; style score; short written explanation; supervised micro-checks (best-of-N) |
| **T2 Applied** | 10-601, CS189, CS229 problem sets, Data 100 projects, FSDL labs | P1–P9, P12, P13, P17, P18 | Derivation + implementation + experiment write-up; oral checkoff sample; reproducibility evidence |
| **T3 Advanced / Research** | CS231N, CS224N projects, CS229 project, MLiP project, 17-745 research project | P6, P8–P13, P15–P17, P20 | Milestones (proposal → check-ins → report → demo); conference-style report; mandatory viva; contribution statement; AI-use log |

### 5.2 Subtrack emphasis

| Subtrack | Strongest benchmark influences | Distinctive evidence |
|---|---|---|
| **Data Science** | Data 100, 18.S191, CS229 | Lifecycle notebooks; hidden tests on data transforms; written interpretation and limitations |
| **ML Engineering** | MLiP, FSDL, Made With ML, CS231N | Tests of code, data and models; deployment and monitoring evidence; spec-graded milestones |
| **AI Engineering** | CS224N, CS50 AI, fast.ai, MLiP | Transformer or agent components built from parts; evaluation harnesses; AI-use disclosure; default/custom capstone |

### 5.3 Assessment formats

| Format | Design pattern (from benchmarks) | Tiers | Principles | Key sources |
|---|---|---|---|---|
| **Implementation** | Harness + target functions + import allow-list; public/hidden tests; style score | T1, T2 | P1, P2, P3, P4, P5, P7 | [S2][S8][S17][S20][S28] |
| **Investigation** | Notebook on a real dataset; hidden tests on intermediate results; written findings | T1, T2 | P2, P6, P17, P20 | [S12][S33] |
| **Reverse-engineering** | Start from a working system; explain, modify, or extend it; oral check | T1, T2 | P6, P9 | [S37][S38][S9] |
| **Replication** | Reproduce a published result; report with methods/experiments weighting; executed notebooks | T2, T3 | P6, P10, P11, P17 | [S18][S19] |
| **Comparative** | Compare methods under fair, validated protocols; justify the choice | T2, T3 | P6, P11 | [S17][S18] |
| **Optimization** | Correct baseline first, then performance tiers (speed, nodes, accuracy) | T1–T3 | P1, P18 | [S28] |
| **System Design** | Spec-graded pass/fail requirements; design doc; verbal explanation items | T2, T3 | P9, P12, P16 | [S23][S24] |
| **Debugging / Forensics** | Seeded faults in code, data or model; hidden tests confirm the fix; written root-cause analysis | T2, T3 | P2, P6, P17 | [S36] (testing code, data, models); [S14] (do your own groundwork) |
| **Open-ended** | Spec core + open extension; rubric published in advance | T2, T3 | P1, P4, P11 | [S3][S18] |
| **Capstone** | Default or custom; proposal → check-ins → report → demo/showcase; tokens not valid on the final deliverable; viva; contribution and AI logs | T3 | P8–P11, P13, P15, P16, P20 | [S4][S18][S19][S23][S35] |

Note on Debugging/Forensics: none of the benchmark pages describes a dedicated debugging assessment. This format is CLBG's own design, drawing on the Made With ML testing emphasis and the general self-reliance standards cited above.

---

## 6. Disclaimer

This document uses publicly available information about the courses named here only as **educational benchmarks**. CLBG (Collective Lab Builders Group) has **no affiliation** with, and no endorsement, sponsorship or partnership from, Harvard University, the Massachusetts Institute of Technology, Stanford University, Carnegie Mellon University, the University of California, Berkeley, Full Stack Deep Learning, Made With ML, fast.ai, or any of their instructors. Course names are used only to identify sources. No assignment text, test suite or solution has been reproduced. Policies described reflect the cited pages in November 2026 and may since have changed; readers should consult the official pages. CLBG assessments are original works and must not be presented as equivalent to, or a substitute for, any of these courses or their credentials.

---

## 7. References

All accessed November 2026.

| ID | Course / page | URL |
|---|---|---|
| S1 | Harvard CS50x home | https://cs50.harvard.edu/x/ |
| S2 | Harvard CS50x syllabus | https://cs50.harvard.edu/x/syllabus/ |
| S3 | Harvard CS50x Problem Set 1 | https://cs50.harvard.edu/x/psets/1/ |
| S4 | Harvard CS50x final project | https://cs50.harvard.edu/x/project/ |
| S5 | Harvard CS50x academic honesty | https://cs50.harvard.edu/x/honesty/ |
| S6 | Harvard CS50 AI home | https://cs50.harvard.edu/ai/ |
| S7 | Harvard CS50 AI projects index | https://cs50.harvard.edu/ai/projects/ |
| S8 | Harvard CS50 AI Project 0 (Degrees) | https://cs50.harvard.edu/ai/projects/0/degrees/ |
| S9 | MIT 6.390 Fall 2026 basic information | https://introml.mit.edu/fall26/info |
| S10 | MIT OCW 6.036 Fall 2020 | https://ocw.mit.edu/courses/6-036-introduction-to-machine-learning-fall-2020/ |
| S11 | MIT OCW 6.100L Fall 2022 syllabus | https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/pages/syllabus/ |
| S12 | MIT 18.S191 Computational Thinking Fall 2024 | https://computationalthinking.mit.edu/Fall24/ |
| S13 | Stanford CS229 home | https://cs229.stanford.edu/ |
| S14 | Stanford CS229 logistics/FAQ (Fall 2021 archive) | https://cs229.stanford.edu/logistics_faq.html-backup-fall21 |
| S15 | Stanford CS231N home (Spring 2026) | https://cs231n.stanford.edu/ |
| S16 | Stanford CS231N assignments | https://cs231n.stanford.edu/assignments.html |
| S17 | Stanford CS231N Assignment 1 (2025) | https://cs231n.github.io/assignments2025/assignment1/ |
| S18 | Stanford CS231N final project | https://cs231n.stanford.edu/project.html |
| S19 | Stanford CS224N home (Winter 2026) | https://web.stanford.edu/class/cs224n/ |
| S20 | CMU 10-301/10-601 Spring 2026 home and syllabus | https://www.cs.cmu.edu/~mgormley/courses/10601/ |
| S21 | CMU 10-301/10-601 coursework | https://www.cs.cmu.edu/~mgormley/courses/10601/coursework.html |
| S22 | CMU 10-301/10-601 Fall 2020 | https://www.cs.cmu.edu/~10601/ |
| S23 | CMU Machine Learning in Production, Spring 2025 | https://mlip-cmu.github.io/s2025/ |
| S24 | CMU Machine Learning in Production, Fall 2026 repository | https://github.com/mlip-cmu/f2026 |
| S25 | CMU Machine Learning in Production, course hub | https://mlip-cmu.github.io/ |
| S26 | UC Berkeley CS188 Fall 2025 home | https://inst.eecs.berkeley.edu/~cs188/fa25/ |
| S27 | UC Berkeley CS188 Fall 2025 policies | https://inst.eecs.berkeley.edu/~cs188/fa25/policies/ |
| S28 | UC Berkeley CS188 Fall 2025 Project 1 | https://inst.eecs.berkeley.edu/~cs188/fa25/projects/proj1/ |
| S29 | UC Berkeley CS189/289A home | https://eecs189.org/ |
| S30 | UC Berkeley CS189/289A Fall 2026 FAQ | https://eecs189.org/fa26/faq/ |
| S31 | UC Berkeley CS189/289A Fall 2026 syllabus | https://eecs189.org/fa26/syllabus/ |
| S32 | UC Berkeley Data 100 home | https://ds100.org/ |
| S33 | UC Berkeley Data 100 Fall 2026 syllabus | https://ds100.org/fa26/syllabus/ |
| S34 | Full Stack Deep Learning 2022 | https://fullstackdeeplearning.com/course/2022/ |
| S35 | Full Stack Deep Learning 2022 project showcase | https://fullstackdeeplearning.com/course/2022/project-showcase/ |
| S36 | Made With ML | https://madewithml.com/ |
| S37 | fast.ai Practical Deep Learning | https://course.fast.ai/ |
| S38 | fast.ai Lesson 1 | https://course.fast.ai/Lessons/lesson1.html |

**Pages attempted but not retrieved or not informative** (no claims made from them): https://cs229.stanford.edu/syllabus.html (404); https://www.cs.cmu.edu/~mgormley/courses/10601/syllabus.html (404); https://mlip-cmu.github.io/s2025/assignments/ (404); https://introml.mit.edu/_static/fall24/LectureNotes/intro_slides.pdf (timeout); https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/pages/assignments/ (redirect loop); https://introml.mit.edu/ (logged-out view; grading and collaboration pages require login); https://inst.eecs.berkeley.edu/~cs188/ (landing page only).
