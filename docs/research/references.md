# References

Categorised bibliography for the CLBG Intelligence Track assessment ecosystem. All sources accessed 2026-11-03. Detailed notes and the claims drawn from each source are kept in the working research notes.

Format: **Title**, Author or publisher, Year. URL. *Use:* what it supports.

---

## 1. Curriculum standards

- **Computer Science Curricula 2023 (CS2023)**, ACM / IEEE Computer Society / AAAI, 2023/2024.
  - Report DOI: https://dl.acm.org/doi/book/10.1145/3664191
  - Knowledge-area hours (ACM CSED page, marked "mockup"): https://csed.acm.org/mockup-cs2023/
  - AI knowledge area: https://csed.acm.org/mockup-artificial-intelligence/
  - *Use:* knowledge-area hours and the AI-ML core topics for T1 floors, including ethics inside the ML core.
- **CS2023 Machine Learning CS Core (teaching materials)**, T. Neller, Gettysburg College / Model AI, 2026. https://modelai.gettysburg.edu/2026/cs2023ml/
  - *Use:* the verbatim AI-ML CS Core topic list (CS2023 p. 71).
- **Computing Competencies for Undergraduate Data Science Curricula**, ACM Data Science Task Force (A. Danyluk, P. Leidig, co-chairs), January 2021.
  - Report: https://dstf.acm.org/DSTF_Final_Report.pdf
  - Task force: https://dstf.acm.org/
  - *Use:* the 11 DS knowledge areas, the knowledge/skills/dispositions model and the T1/T2/E tiering.
- **O\*NET OnLine: Data Scientists (15-2051.00)**, U.S. Department of Labor / O\*NET, current. https://www.onetonline.org/link/summary/15-2051.00
  - *Use:* industry task definition of the data-scientist role.

## 2. Vendor learning resources

- **Machine Learning Crash Course**, Google for Developers, current. https://developers.google.com/machine-learning/crash-course
  - *Use:* foundation-level ML scope, including LLM intro, production ML and fairness.
- **Rules of Machine Learning: Best Practices for ML Engineering**, M. Zinkevich / Google, current. https://developers.google.com/machine-learning/guides/rules-of-ml
  - *Use:* scorable MLE practices: metrics first, simple baseline, training-serving skew, silent failures.

## 3. Certification exam guides

- **Professional Machine Learning Engineer: exam page and Exam Guide v3.1**, Google Cloud, 2024–2026.
  - Exam page: https://cloud.google.com/learn/certification/machine-learning-engineer
  - Exam guide: https://services.google.com/fh/files/misc/professional_machine_learning_engineer_exam_guide_english_3.1_final.pdf
  - *Use:* MLE section weightings (13 / ~14 / ~18 / ~20 / ~22 / ~13%) and the GenAI scope.
- **AWS Certified Machine Learning Engineer – Associate (MLA-C01) Exam Guide v1.0**, Amazon Web Services, 2024. https://d1.awsstatic.com/training-and-certification/docs-machine-learning-engineer-associate/AWS-Certified-Machine-Learning-Engineer-Associate_Exam-Guide.pdf
  - *Use:* MLE domains (28 / 26 / 22 / 24%) and the out-of-scope tasks used as T3 markers.
- **AWS Certified AI Practitioner (AIF-C01) Exam Guide**, Amazon Web Services, current. https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01.html
  - *Use:* the AI-literacy baseline (20 / 24 / 28 / 14 / 14%), placed below CLBG T1.
- **Study guide for Exam AI-102 (retired 30 June 2026)**, Microsoft Learn, 2025–2026. https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-102
  - *Use:* historical AI-engineer skill outline and retirement status.
- **Study guide for Exam DP-100 (retired 1 June 2026)**, Microsoft Learn, 2025–2026. https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/dp-100
  - *Use:* historical data-scientist skill outline and retirement status.
- **Study guide for Exam AI-300: Operationalizing Machine Learning and Generative AI Solutions**, Microsoft Learn, 2026. https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-300
  - *Use:* the merged MLOps/GenAIOps role definition and its weightings.
- **Study guide for Exam AI-103: Developing AI Apps and Agents on Azure**, Microsoft Learn, 2026. https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103
  - *Use:* the AI-engineer (apps and agents) role definition and its weightings.
- **The AI job boom is here. Are you ready to showcase your skills?**, Microsoft Tech Community (Skills Hub Blog), 2026. https://techcommunity.microsoft.com/blog/skills-hub-blog/the-ai-job-boom-is-here-are-you-ready-to-showcase-your-skills/4494128
  - *Use:* the retirement-to-replacement mapping (DP-100 → AI-300; AI-102 → AI-103).

## 4. Practitioner courses

- **Made With ML (MLOps course)**, G. Mohandas / Anyscale, current. https://madewithml.com/
  - *Use:* MLOps lesson structure, including testing of code, data and models.
- **Full Stack Deep Learning 2022**, Full Stack Deep Learning, 2022. https://fullstackdeeplearning.com/course/2022/
  - *Use:* the production DL lecture sequence (deployment, continual learning, teams, ethics).
- **LLM Course**, Hugging Face, current. https://huggingface.co/learn/llm-course/chapter1/1
  - *Use:* the progression from Transformers basics to fine-tuning and reasoning models.
- **AI Agents Course**, Hugging Face, current. https://huggingface.co/learn/agents-course/unit0/introduction
  - *Use:* agent fundamentals, frameworks, and benchmark-based final assessment.

## 5. MLOps maturity

- **MLOps: Continuous delivery and automation pipelines in machine learning**, Google Cloud Architecture Center, current. https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
  - *Use:* MLOps levels 0–2, continuous training (CT), and data and model validation.
- **MLOps Maturity Model**, Microsoft Azure Architecture Center, 2026. https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/mlops-maturity-model
  - *Use:* levels 0–4 across People / Model creation / Model release / Application integration, used as rubric rows.

## 6. AI engineering practice

- **AI Engineering: Building Applications with Foundation Models**, C. Huyen / O'Reilly Media, 2025.
  - Book page: https://huyenchip.com/books/
  - Table of contents: https://github.com/chiphuyen/aie-book/blob/main/ToC.md
  - *Use:* the AI Eng vs ML Eng boundary and evaluation methodology (ch. 3–4).
- **Evaluation best practices**, OpenAI, current. https://developers.openai.com/api/docs/guides/evaluation-best-practices
  - *Use:* eval-driven development, grader types, LLM-judge bias controls and agent eval metrics.
- **Structured Outputs**, OpenAI, current. https://developers.openai.com/api/docs/guides/structured-outputs
  - *Use:* schema-enforced outputs, the strict setting and refusal handling.
- **Structured outputs (Gemini API)**, Google AI Studio documentation, current. https://aistudio.google.com/docs/structured-output
  - *Use:* constraints that are not enforced, and the requirement for semantic validation.
- **Tool use with Claude**, Anthropic, current. https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
  - *Use:* the tool-call loop, client vs server tools, and strict tool schemas.
- **Create strong empirical evaluations**, Anthropic, current. https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
  - *Use:* grading-method trade-offs and LLM-grader rubric tips.
- **Building effective agents**, Anthropic, 2024. https://www.anthropic.com/engineering/building-effective-agents
  - *Use:* workflow vs agent distinction, agent patterns and tool-interface design.
- **Model Context Protocol Specification (2026-07-28, latest)**, Model Context Protocol project, 2026. https://modelcontextprotocol.io/specification/latest
  - *Use:* MCP architecture, extensions, and the consent and tool-safety principles.
- **Model Context Protocol Specification (2025-06-18)**, Model Context Protocol project, 2025. https://modelcontextprotocol.io/specification/2025-06-18
  - *Use:* the previous version, kept for change tracking (sampling, roots).

## 7. Security, risk and responsible AI

- **OWASP Top 10 for LLM Applications 2025**, OWASP GenAI Security Project, 2024/2025. https://genai.owasp.org/llm-top-10/
  - *Use:* the LLM01–LLM10 risk taxonomy for AI-11 and the agent units.
- **OWASP Machine Learning Security Top 10 (draft)**, OWASP Foundation, 2023 (draft).
  - Project page: https://owasp.org/www-project-machine-learning-security-top-10/
  - List: https://raw.githubusercontent.com/OWASP/www-project-machine-learning-security-top-10/master/index.md
  - *Use:* the ML01–ML10 classical ML attack taxonomy for ML-14.
- **AI Risk Management Framework (AI RMF 1.0)**, NIST, 2023.
  - Overview: https://www.nist.gov/itl/ai-risk-management-framework
  - Core: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
  - *Use:* the Govern / Map / Measure / Manage structure for T3 risk analysis.
- **NIST AI 600-1: Artificial Intelligence Risk Management Framework: Generative AI Profile**, NIST, 2024. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
  - *Use:* the 12 GAI risk categories and suggested actions.

## 8. Nigerian legal and policy context

- **Nigeria Data Protection Act, 2023 (Act No. 37), Official Gazette Vol. 110 No. 119**, Federal Republic of Nigeria (copy hosted by the Nigerian Communications Commission), 2023. https://ncc.gov.ng/media/801/view
  - *Use:* principles (s.24), lawful bases (s.25), consent (s.26), DPIA (s.28), sensitive data (s.30, s.65), children (s.31), rights (ss.34–38), security and breach (ss.39–40), cross-border transfer (ss.41–43), sanctions (s.48).
- **NDP Act General Application and Implementation Directive (GAID) 2025, NDPC/NDP ACT-GAID/01/2025**, Nigeria Data Protection Commission, 2025. https://ndpc.gov.ng/wp-content/uploads/2025/07/NDP-ACT-GAID-2025-MARCH-20TH.pdf
  - *Use:* mandatory consent cases (Art. 18), mandatory DPIA including student records (Art. 28), breach (Art. 33), emerging technologies and AI (Art. 43–44).
- **NDPC GAID takes effect on 19 September: Is your organisation prepared?**, Aluko & Oyebode, 2025. https://aluko-oyebode.com/insights/ndpc-gaid-takes-effect-on-19-september-is-your-organisation-prepared/
  - *Use:* GAID effective date and the repeal of NDPR 2019.
- **Nigeria: NDPC Issues GAID – Key Compliance Insights**, DLA Piper Privacy Matters, 2025. https://privacymatters.dlapiper.com/2025/06/nigeria-ndpc-issues-gaid-key-compliance-insights/
  - *Use:* issue date, transition period, LIA template and transfer-approval commentary.
- **Highlights of the NDPA General Application and Implementation Directive**, Afriwise, 2025. https://www.afriwise.com/blog/highlights-of-the-nigeria-data-protection-act-general-application-and-implementation-directive
  - *Use:* GAID issue date and territorial scope.
- **Are you GAID 2025 ready?**, Banwo & Ighodalo, 2025. https://www.banwo-ighodalo.com/grey-matter/are-you-gaid-2025-ready-navigating-nigerias-gaid-2025-what-your-organisation-needs-to-know-how-bi-can-support-your-compliance-journey/
  - *Use:* corroboration of the GAID effective date.
- **National Artificial Intelligence Strategy (NAIS), Nigeria (OECD.AI policy entry)**, OECD.AI / Federal Ministry of Communications, Innovation and Digital Economy, 2025. https://oecd.ai/en/dashboards/policy-initiatives/national-artificial-intelligence-strategy-nais
  - *Use:* NAIS publication (September 2025), goals and five pillars, including talent and responsible AI.
- **FMCIDE released National Artificial Intelligence Strategy**, Digital Policy Alert, 2025. https://digitalpolicyalert.org/event/40784-federal-ministry-of-communication-innovation-and-digital-economy-released-national-artificial-intelligence-strategy
  - *Use:* corroboration of the NAIS release date (19 September 2025) and publisher.

## 9. Competitions, leaderboards and leakage

- **Competing in a data science contest without reading the data**, M. Hardt, 2015. https://blog.mrtz.org/2015/03/09/competition.html
  - *Use:* the mechanism of public-leaderboard overfitting ("wacky boosting").
- **The Ladder: A Reliable Leaderboard for Machine Learning Competitions**, A. Blum and M. Hardt, ICML / PMLR 37, 2015. https://proceedings.mlr.press/v37/blum15.html
  - *Use:* a formal treatment of adaptive leaderboard overfitting and a mitigation.
- **A Meta-Analysis of Overfitting in Machine Learning**, R. Roelofs et al., NeurIPS, 2019. https://proceedings.neurips.cc/paper/2019/hash/ee39e503b6bedf0c98c388b7e8589aca-Abstract.html
  - *Use:* counter-evidence that, across 100+ Kaggle competitions, overfitting was limited.
- **Leakage and the Reproducibility Crisis in ML-based Science**, S. Kapoor and A. Narayanan, Princeton, 2022–2024. https://reproducible.cs.princeton.edu/
  - *Use:* the leakage taxonomy, the scale of affected papers and model info sheets.

## 10. Documentation and reproducibility standards

- **Datasheets for Datasets**, T. Gebru et al., arXiv v8 / Communications of the ACM, 2018/2021. https://arxiv.org/abs/1803.09010
  - *Use:* the dataset documentation standard for DS and ML submissions.
- **Model Cards for Model Reporting**, M. Mitchell et al., FAT\* 2019. https://arxiv.org/abs/1810.03993
  - *Use:* the model documentation standard with disaggregated evaluation.
- **REFORMS: Consensus-based Recommendations for Machine-learning-based Science**, S. Kapoor et al., Science Advances, 2024. https://reforms.cs.princeton.edu/
  - *Use:* a 32-item, 8-section checklist for T3 research-style assessments.
- **NeurIPS Paper Checklist Guidelines**, NeurIPS, 2026. https://neurips.cc/public/guides/PaperChecklist
  - *Use:* the 16-item Yes/No/NA + justification format, adapted for T3 reports.
- **Improving Reproducibility in Machine Learning Research (A Report from the NeurIPS 2019 Reproducibility Program)**, J. Pineau et al., JMLR 22(164), 2021. https://jmlr.org/papers/v22/20-303.html
  - *Use:* the origin and rationale of the ML Reproducibility Checklist.

## 11. Assessment design and rubrics

- **A Model of Learning Objectives based on A Taxonomy for Learning, Teaching, and Assessing (Anderson & Krathwohl, 2001)**, document hosted by Boston University, c. 2012. https://www.bu.edu/provost/files/2013/10/Anderson-Krathwohl-Revision-to-Blooms-Taxonomy-of-Educational-Objectives.pdf
  - *Use:* the cognitive-process and knowledge dimensions for writing tiered outcomes.
- **SOLO Taxonomy (Biggs & Collis, 1982)**, University of KwaZulu-Natal, School of Clinical Medicine, Educational Theory pages, n.d. https://medicine.ukzn.ac.za/educationaltheory/solotaxonomy/
  - *Use:* response-structure levels for rubric performance descriptors.
- **Creating and Using Rubrics**, University of Hawaiʻi at Mānoa Assessment and Curriculum Support Center, current. https://manoa.hawaii.edu/assessment/resources/creating-and-using-rubrics/
  - *Use:* analytic vs holistic rubrics, development steps, norming and anchors.
- **Grading and Performance Rubrics**, Carnegie Mellon University Eberly Center, current. https://www.cmu.edu/teaching/assessment/assesslearning/rubrics.html
  - *Use:* rubric components and benefits for consistency and feedback.
