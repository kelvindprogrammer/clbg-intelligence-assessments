# Legacy Assessment Migration Map

| Field | Value |
|---|---|
| Source | <https://github.com/kelvindprogrammer/assessment-intelligence>, branch `2025`, commit `34c0b5d` |
| Scope | All 63 legacy tasks (3 levels × 7 domains × 3 tasks) |
| Date | 2026-11-03 |
| Prepared by | CLBG Intelligence Track Assessment Committee |
| Companion | [`LEGACY_REPOSITORY_AUDIT.md`](LEGACY_REPOSITORY_AUDIT.md) |

## Classification key

| Class | Meaning |
|---|---|
| **RETAIN** | The core design is sound. Carry the idea forward almost unchanged in substance, rewritten in the new template with a fixed dataset, contract, rubric and tests. |
| **IMPROVE** | Keep the problem, but fix specific defects: arbitrary thresholds, no fixed data, outdated tools, weak evaluation, missing local context. |
| **RESTRUCTURE** | The idea is valuable but its shape is wrong. Split, merge, rescope or re-tier it (e.g. a Pro "build a platform" task becomes a bounded Tier 3 analysis plus a separate engineering task). |
| **REPLACE** | The competency is still needed but the legacy task assesses it with an obsolete approach. A new task covers the same competency. |
| **RETIRE** | Drop it. It is redundant, cannot be verified, or is mis-scoped. Any salvageable idea is noted. |

The legacy "Novice / Intermediate / Pro" labels do **not** map one-to-one onto the new Tiers 1–3. The *suggested tier* below reflects where the rewritten task belongs under `docs/tier-definitions.md`. The **new assessment ID** column is filled once the catalogue is generated.

## Summary

| Classification | Count |
|---|---|
| RETAIN | 11 |
| IMPROVE | 24 |
| RESTRUCTURE | 20 |
| REPLACE | 4 |
| RETIRE | 4 |
| **Total** | **63** |

## Migration table

Paths are relative to the legacy repository root. "T1/T2/T3" in the destination column is the suggested new tier.

### Novice

| # | Legacy path | Legacy task | Classification | Reason | New destination unit | New assessment ID |
|---|---|---|---|---|---|---|
| 1 | `Novice/Computer Vision/tasks.md` | T1 Image Manipulation Basics | IMPROVE | Good first exposure to images as arrays, but it is an unmeasured checklist. Fix input images and expected-output arrays so grayscale, rotate, flip and crop can be unit-tested; add dtype/overflow pitfalls. | ML-07 Computer Vision (T1) | TBD (see catalogue) |
| 2 | `Novice/Computer Vision/tasks.md` | T2 Simple Image Filter | RESTRUCTURE | Overlaps T1 and T3. Merge brightness, contrast and blur into a single "implement 2-D convolution and verify against SciPy" task, with the blur as a kernel. | ML-07 Computer Vision (T1); ML-01 Foundations | TBD (see catalogue) |
| 3 | `Novice/Computer Vision/tasks.md` | T3 Basic Edge Detection | IMPROVE | Sound from-scratch exercise (gradients, thresholding). Add Sobel vs library parity tests, a threshold-selection rationale and a small labelled edge set to score against. | ML-07 Computer Vision (T1) | TBD (see catalogue) |
| 4 | `Novice/Data Analytics/tasks.md` | T1 Sales Data Analysis | IMPROVE | Realistic, but "create or load" allows trivial synthetic data. Fix the data to Online Retail II (DSET-002) and require cancellations/returns handling and a stated decision question. | DS-04 Exploratory Data Analysis (T1); DS-07 SQL | TBD (see catalogue) |
| 5 | `Novice/Data Analytics/tasks.md` | T2 Customer Behavior Analysis (RFM, CLV) | IMPROVE | RFM segmentation is valuable. CLV and "personas" are undefined. Specify the RFM scoring contract, a cohort window and a retention-action recommendation with a cost assumption. | DS-09 Decision and Business Analytics (T1) | TBD (see catalogue) |
| 6 | `Novice/Data Analytics/tasks.md` | T3 Simple Statistical Analysis | IMPROVE | Covers the right concepts (tests, CIs, assumptions), but the candidate chooses both problem and data. Fix the dataset and question, and grade interpretation of p-values and CIs against stated misconceptions. | DS-05 Probability and Statistics (T1) | TBD (see catalogue) |
| 7 | `Novice/Data Science/tasks.md` | T1 Exploratory Data Analysis | RESTRUCTURE | Duplicates Novice DA T1. "At least 5 visualizations" rewards volume. Rebuild as question-driven EDA plus a data-quality audit on a deliberately flawed dataset. | DS-04 EDA (T1); DS-03 Data Cleaning and Quality | TBD (see catalogue) |
| 8 | `Novice/Data Science/tasks.md` | T2 Simple Predictive Model | RESTRUCTURE | Generic "pick any prediction task". Split into a Tier 1 supervised-learning contract (fixed split, baseline, metric choice) in ML-02, with leakage checks moved to ML-04. | ML-02 Supervised Learning and Ensembles (T1) | TBD (see catalogue) |
| 9 | `Novice/Data Science/tasks.md` | T3 Feature Engineering and Analysis | IMPROVE | Good instinct (with/without comparison), but there is no CV and no leakage guard. Require pipeline-contained transforms and CV-based comparison. | ML-04 Feature Engineering and Data for ML (T1) | TBD (see catalogue) |
| 10 | `Novice/Data Visualization/tasks.md` | T1 Basic Chart Types | RESTRUCTURE | A chart-type checklist (it even requires a pie chart). Recast as "choose and justify the right encoding for 5 given questions", graded on perceptual reasoning. | DS-06 Visualization and Storytelling (T1) | TBD (see catalogue) |
| 11 | `Novice/Data Visualization/tasks.md` | T2 Comparative Visualization | RETAIN | Strong core: side-by-side vs overlay vs small multiples, consistent scales, "explain which works best". Fix the dataset (e.g. OWID, DSET-020). | DS-06 Visualization and Storytelling (T1) | TBD (see catalogue) |
| 12 | `Novice/Data Visualization/tasks.md` | T3 Interactive Dashboard Design | IMPROVE | Despite the title it is a static subplot grid. Require a named audience and decision, a layout rationale and an accessibility check (colour-blind-safe palette, alt text). | DS-06 Visualization and Storytelling (T1) | TBD (see catalogue) |
| 13 | `Novice/Deep Learning/tasks.md` | T1 Implement a Simple Neural Network (perceptron) | RESTRUCTURE | A subset of T3. Merge in as a first stage that must also show XOR failing for a single layer, to motivate hidden units. | ML-06 Neural Networks and Deep Learning (T1) | TBD (see catalogue) |
| 14 | `Novice/Deep Learning/tasks.md` | T2 Activation Functions Exploration | RESTRUCTURE | Too thin to stand alone. Fold into the from-scratch MLP task as a vanishing-gradient experiment with numerical gradient checks. | ML-06 Neural Networks (T1); ML-01 Foundations | TBD (see catalogue) |
| 15 | `Novice/Deep Learning/tasks.md` | T3 Training a Network with Backpropagation | RETAIN | Excellent Tier 1 task: from-scratch forward/backward pass, gradient descent, loss curve. Add a finite-difference gradient-check test and a fixed seed. | ML-06 Neural Networks and Deep Learning (T1) | TBD (see catalogue) |
| 16 | `Novice/General Machine Learning/tasks.md` | T1 Linear Regression from Scratch | RETAIN | Classic, auto-testable, builds understanding of loss and gradients. Add a closed-form parity check and feature-scaling effects on convergence. | ML-01 Mathematical and Computational Foundations (T1) | TBD (see catalogue) |
| 17 | `Novice/General Machine Learning/tasks.md` | T2 K-Nearest Neighbors Classifier | RETAIN | Strong from-scratch task (vectorised distances, tie handling, K sweep). Add parity with scikit-learn and a scaling-sensitivity question. | ML-02 Supervised Learning and Ensembles (T1) | TBD (see catalogue) |
| 18 | `Novice/General Machine Learning/tasks.md` | T3 Data Preprocessing and Analysis | RESTRUCTURE | Mixes cleaning with ML preprocessing and omits the key lesson, fitting scalers/imputers on train only. Rebuild as a leakage-detection task. | ML-04 Feature Engineering (T1); DS-03 Data Cleaning | TBD (see catalogue) |
| 19 | `Novice/Natural Language Processing/tasks.md` | T1 Text Preprocessing Pipeline | IMPROVE | Useful, but English-only and stemmer-centric. Add Nigerian-language text (diacritics in Yorùbá, code-switching in Pidgin) where Porter stemming fails, and test tokenizer behaviour. | ML-08 Natural Language Processing (T1) | TBD (see catalogue) |
| 20 | `Novice/Natural Language Processing/tasks.md` | T2 Simple Text Classifier | REPLACE | Keyword scoring "on at least 10 sample texts" teaches invalid evaluation. Replace with a bag-of-words / TF-IDF classifier on a fixed NaijaSenti split (DSET-034) with macro-F1 and a majority baseline. | ML-08 Natural Language Processing (T1) | TBD (see catalogue) |
| 21 | `Novice/Natural Language Processing/tasks.md` | T3 Text Similarity Analysis | RESTRUCTURE | Jaccard/cosine on counts is the right on-ramp to semantic search. Recast as lexical vs embedding similarity on a small labelled retrieval set, measuring recall@k. | AI-04 Embeddings and Semantic Search (T1) | TBD (see catalogue) |

### Intermediate

| # | Legacy path | Legacy task | Classification | Reason | New destination unit | New assessment ID |
|---|---|---|---|---|---|---|
| 22 | `Intermediate/Computer Vision/tasks.md` | T1 Feature Detection and Matching | IMPROVE | Solid classical CV (keypoints, ratio test, RANSAC, homography). Drop SURF (non-free), fix image pairs with ground-truth homographies, and grade reprojection error. | ML-07 Computer Vision (T2) | TBD (see catalogue) |
| 23 | `Intermediate/Computer Vision/tasks.md` | T2 Image Segmentation (Otsu, k-means, watershed) | IMPROVE | Good method comparison, but there is no ground truth. Use Oxford-IIIT Pet trimaps (DSET-050) so IoU/Dice comparisons are real. | ML-07 Computer Vision (T2) | TBD (see catalogue) |
| 24 | `Intermediate/Computer Vision/tasks.md` | T3 Object Detection System (HOG + sliding window) | RESTRUCTURE | HOG pipelines are dated, but NMS, IoU and precision/recall are timeless. Restructure into "implement detection evaluation (IoU, NMS, AP) and audit a pretrained detector's errors". | ML-07 Computer Vision (T2); ML-05 Evaluation | TBD (see catalogue) |
| 25 | `Intermediate/Data Analytics/tasks.md` | T1 A/B Testing and Experimental Analysis | RETAIN | One of the strongest briefs: hypothesis, power, assumptions, practical vs statistical significance, multiple metrics. Provide a fixed experiment log with a planted issue. | DS-08 Statistical Inference, Experimentation and Causal Thinking (T2) | TBD (see catalogue) |
| 26 | `Intermediate/Data Analytics/tasks.md` | T2 Cohort Analysis and Retention | RETAIN | Valuable and realistic (retention heatmaps, normalisation, churn). Fix to Online Retail II (DSET-002) or a synthetic mobile-money cohort log. | DS-09 Decision and Business Analytics (T2) | TBD (see catalogue) |
| 27 | `Intermediate/Data Analytics/tasks.md` | T3 Business Optimization Problem | IMPROVE | LP plus sensitivity analysis is the right skill, but the candidate chooses everything. Specify a Nigerian-context problem (e.g. generator diesel allocation or agro-logistics) with checkable optimal values. | DS-09 Decision and Business Analytics (T2) | TBD (see catalogue) |
| 28 | `Intermediate/Data Science/tasks.md` | T1 End-to-End ML Pipeline | RESTRUCTURE | Covers everything at once. Split into ML-05 (validation design and model comparison) and ML-13 (reproducible pipeline). Replace "save model" via pickle with a versioned artefact plus model card. | ML-05 Evaluation, Validation and Model Selection (T2); ML-13 | TBD (see catalogue) |
| 29 | `Intermediate/Data Science/tasks.md` | T2 Time Series Forecasting | IMPROVE | Right topics (stationarity, ARIMA, intervals). Fix the dataset (e.g. HDX Nigeria food prices, DSET-029), require rolling-origin backtests and a seasonal-naive baseline, and score interval coverage. | DS-10 Time-Series Analysis and Forecasting (T2) | TBD (see catalogue) |
| 30 | `Intermediate/Data Science/tasks.md` | T3 Customer Churn Prediction | IMPROVE | Good emphasis on costs and interpretability. Fix data, require a cost matrix and a decision-threshold choice, and grade the business decision rather than accuracy. | DS-09 Decision and Business Analytics (T2); ML-14 | TBD (see catalogue) |
| 31 | `Intermediate/Data Visualization/tasks.md` | T1 Multi-Dimensional Data Visualization | IMPROVE | Parallel coordinates, clustered heatmaps and PCA/t-SNE are valuable, but 3-D scatter is rarely a good encoding. Require a critique of t-SNE distortions and a justified final encoding. | DS-06 Visualization and Storytelling (T2); ML-03 | TBD (see catalogue) |
| 32 | `Intermediate/Data Visualization/tasks.md` | T2 Interactive Dashboard | IMPROVE | Linked views and filtering are real skills, but there is no question behind them. Require a stakeholder brief, defined KPIs and a usability check with one non-technical reviewer. | DS-06 Visualization and Storytelling (T2) | TBD (see catalogue) |
| 33 | `Intermediate/Data Visualization/tasks.md` | T3 Data Storytelling with Visualizations | RETAIN | Strong narrative brief (progressive disclosure, annotations, recommendations). Fix a Nigeria/Africa-relevant dataset (WDI, DSET-021, or FAOSTAT, DSET-025). | DS-06 Visualization and Storytelling (T2) | TBD (see catalogue) |
| 34 | `Intermediate/Deep Learning/tasks.md` | T1 CNN Implementation | IMPROVE | Fine topic, but ">85% MNIST" is below a linear baseline. Use Fashion-MNIST (DSET-013), require a logistic-regression baseline and set a justified margin above it. | ML-06 Neural Networks and Deep Learning (T2) | TBD (see catalogue) |
| 35 | `Intermediate/Deep Learning/tasks.md` | T2 Optimization and Regularization Study | RETAIN | Well-designed controlled experiment (same architecture, several optimisers and regularisers, logged curves). Add seeds × 3 and require variance bands. | ML-06 Neural Networks and Deep Learning (T2) | TBD (see catalogue) |
| 36 | `Intermediate/Deep Learning/tasks.md` | T3 Transfer Learning Application | IMPROVE | Feature-extraction vs fine-tuning is the right comparison. Fix a CPU-feasible dataset (EuroSAT, DSET-015, or PlantVillage subset, DSET-016) and require a from-scratch baseline. | ML-07 Computer Vision (T2) | TBD (see catalogue) |
| 37 | `Intermediate/General Machine Learning/tasks.md` | T1 Ensemble Learning Implementation | IMPROVE | Bagging/boosting/stacking and the bias-variance discussion are valuable. Remove ">85% accuracy", fix the dataset and require CV-based comparison with intervals. | ML-02 Supervised Learning and Ensembles (T2) | TBD (see catalogue) |
| 38 | `Intermediate/General Machine Learning/tasks.md` | T2 Feature Engineering and Selection | IMPROVE | Filter/wrapper/embedded selection is a good taxonomy. Require selection inside CV folds (selection bias) and a stability comparison. | ML-04 Feature Engineering and Data for ML (T2) | TBD (see catalogue) |
| 39 | `Intermediate/General Machine Learning/tasks.md` | T3 Hyperparameter Optimization | RETAIN | Nested CV and comparing grid, random and Bayesian search on cost and performance is exactly right. Fix the dataset and compute budget. | ML-05 Evaluation, Validation and Model Selection (T2) | TBD (see catalogue) |
| 40 | `Intermediate/Natural Language Processing/tasks.md` | T1 Text Classification with Advanced Features | IMPROVE | Multiple representations is good. Drop ">80% accuracy", add a small pretrained-transformer baseline beside TF-IDF and LSTM, use macro-F1 and analyse errors on AfriSenti or MasakhaNEWS. | ML-08 Natural Language Processing (T2) | TBD (see catalogue) |
| 41 | `Intermediate/Natural Language Processing/tasks.md` | T2 Named Entity Recognition System | IMPROVE | BIO tagging and entity-level F1 are right. Use MasakhaNER 2.0 (DSET-036) for Hausa/Igbo/Yorùbá/Pidgin and grade with `seqeval`-style span F1. | ML-08 Natural Language Processing (T2) | TBD (see catalogue) |
| 42 | `Intermediate/Natural Language Processing/tasks.md` | T3 Text Generation or Summarization | REPLACE | Char-LSTM generation and TextRank are no longer how these problems are solved. Replace with LLM-based structured summarisation under a schema, evaluated against references and a rubric. | AI-02 Prompt Engineering and Structured Generation (T2); AI-10 | TBD (see catalogue) |

### Pro

| # | Legacy path | Legacy task | Classification | Reason | New destination unit | New assessment ID |
|---|---|---|---|---|---|---|
| 43 | `Pro/Computer Vision/tasks.md` | T1 Advanced Object Detection System | RESTRUCTURE | ">70% mAP" is undefined and GPU-heavy. Restructure into a CPU-feasible fine-tune of a small detector on a fixed set with defined mAP@[.5:.95], plus a separate latency/size optimisation component. Note the Ultralytics AGPL licence. | ML-07 Computer Vision (T3); ML-11 Efficient ML | TBD (see catalogue) |
| 44 | `Pro/Computer Vision/tasks.md` | T2 Semantic Segmentation for Complex Scenes | REPLACE | Cityscapes at >75% mIoU plus CRF needs GPU time and non-commercial registration data. Replace with segmentation on Oxford-IIIT Pet or EuroSAT-derived masks, with boundary-error and failure-slice analysis. | ML-07 Computer Vision (T3) | TBD (see catalogue) |
| 45 | `Pro/Computer Vision/tasks.md` | T3 Vision Transformer Implementation | RESTRUCTURE | "Implement" plus ">85% CIFAR" plus "use pretrained weights" contradict each other. Restructure into a small from-scratch ViT data-efficiency study against a CNN at matched parameter count, on CPU-scale data. | ML-06 Neural Networks and Deep Learning (T3); ML-07 | TBD (see catalogue) |
| 46 | `Pro/Data Analytics/tasks.md` | T1 Build an Experimentation Platform | RESTRUCTURE | A product, not an assessment. Extract a bounded Tier 3 analysis (SRM detection, CUPED, sequential testing, A/A validation) for DS-08. Move assignment/bucketing service design to DS-11. | DS-08 Inference, Experimentation and Causal Thinking (T3); DS-11 | TBD (see catalogue) |
| 47 | `Pro/Data Analytics/tasks.md` | T2 Bayesian Analytics and Forecasting | IMPROVE | Hierarchical pooling, MCMC diagnostics and posterior predictive checks are excellent Tier 3 content. Reduce to one problem, replace PyMC3 with PyMC, and grade diagnostic reasoning. | DS-08 Inference, Experimentation and Causal Thinking (T3); DS-10 | TBD (see catalogue) |
| 48 | `Pro/Data Analytics/tasks.md` | T3 Multi-Objective Optimization System | RESTRUCTURE | It asks for four solution families plus RL plus an interactive explorer. Restructure into one Pareto-frontier decision problem with a stakeholder trade-off memo. | DS-09 Decision and Business Analytics (T3) | TBD (see catalogue) |
| 49 | `Pro/Data Science/tasks.md` | T1 Causal Inference for Business Decisions | RETAIN | The strongest Pro brief: several identification strategies, overlap and balance checks, placebo and sensitivity analysis, stated assumptions. Supply a semi-synthetic dataset with a known effect so estimates can be graded. | DS-08 Inference, Experimentation and Causal Thinking (T3) | TBD (see catalogue) |
| 50 | `Pro/Data Science/tasks.md` | T2 Advanced Feature Engineering at Scale | RESTRUCTURE | Mixes feature science with data engineering. Split: leakage-safe temporal/target encoding with ablations (ML-04 T3), and memory-efficient incremental computation (DS-11). | ML-04 Feature Engineering (T3); DS-11 Analytical Pipelines | TBD (see catalogue) |
| 51 | `Pro/Data Science/tasks.md` | T3 Kaggle-Style Competition Solution | RETIRE | "Top 10% leaderboard equivalent" and "5+ model types, 2–3 stacking levels" cannot be verified and reward leaderboard chasing. Salvage adversarial validation and CV-strategy design into ML-05. | ML-05 Evaluation, Validation and Model Selection (idea salvage only) | TBD (see catalogue) |
| 52 | `Pro/Data Visualization/tasks.md` | T1 Real-Time Interactive Dashboard | RESTRUCTURE | Real-time streaming, geospatial, network graphs and deployment in one task. Separate the streaming/aggregation engineering (DS-11) from a decision-focused geospatial dashboard on Nigerian data (DS-06). | DS-06 Visualization (T3); DS-11 Analytical Pipelines | TBD (see catalogue) |
| 53 | `Pro/Data Visualization/tasks.md` | T2 Custom Visualization Library/Component | RETIRE | Front-end library engineering sits outside the Intelligence Track's competencies and cannot be compared across candidates. Salvage accessibility and perceptual-encoding reasoning into DS-06. | DS-06 Visualization (idea salvage only) | TBD (see catalogue) |
| 54 | `Pro/Data Visualization/tasks.md` | T3 Data-Driven Storytelling Project | RESTRUCTURE | Scrollytelling polish overshadows analytical rigour. Restructure as a reproducible research communication piece (code, data provenance, uncertainty, claims audit). | DS-12 Applied Research and Reproducible Communication (T3) | TBD (see catalogue) |
| 55 | `Pro/Deep Learning/tasks.md` | T1 Implement a Transformer from Scratch | IMPROVE | High-value understanding task. Scale to CPU (char-level LM on a small corpus), require attention-mask unit tests, ablate positional encoding, and drop "competitive performance". | ML-06 Neural Networks and Deep Learning (T3); AI-01 | TBD (see catalogue) |
| 56 | `Pro/Deep Learning/tasks.md` | T2 Advanced Model Optimization and Deployment | RETAIN | Excellent: quantisation, pruning and distillation with accuracy retention, size, p50/p95 latency and an API. Make the CPU path (ONNX Runtime / dynamic quantisation) first-class and TensorRT optional. | ML-11 Efficient ML and Optimization (T3); ML-12 | TBD (see catalogue) |
| 57 | `Pro/Deep Learning/tasks.md` | T3 Self-Supervised Learning Implementation | RESTRUCTURE | SimCLR/MAE on ImageNet subsets is GPU-heavy. Restructure into a small-scale contrastive pretraining study with linear-probe evaluation against label fraction. | ML-03 Unsupervised and Representation Learning (T3) | TBD (see catalogue) |
| 58 | `Pro/General Machine Learning/tasks.md` | T1 Build AutoML System | RETIRE | Re-implementing Optuna/auto-sklearn is a multi-month build with no comparable outcome. Salvage multi-fidelity / budget-aware search into ML-05. | ML-05 Evaluation (idea salvage only) | TBD (see catalogue) |
| 59 | `Pro/General Machine Learning/tasks.md` | T2 Advanced Ensemble and Stacking Systems | RETIRE | Repeats Intermediate GML T1 and Pro DS T3 at larger scale ("10+ models"). Adds volume, not reasoning. Diversity-accuracy analysis can enrich the ML-02 Tier 2 ensemble task. | ML-02 Supervised Learning (idea salvage only) | TBD (see catalogue) |
| 60 | `Pro/General Machine Learning/tasks.md` | T3 Production ML Pipeline with MLOps | RESTRUCTURE | The only MLOps content, but it crams tracking, registry, feature store, CI/CD, drift, A/B and serving into one task. Split across ML-12 (serving contract, containerisation) and ML-13 (tracking, CI tests for models, drift monitoring), with a progression across tiers. | ML-13 ML Pipelines, MLOps and Monitoring (T2/T3); ML-12 | TBD (see catalogue) |
| 61 | `Pro/Natural Language Processing/tasks.md` | T1 Fine-tune Large Language Model | RESTRUCTURE | "SOTA" cannot be verified, and full fine-tuning of BERT/T5 is GPU-heavy. Restructure into a PEFT (LoRA) adaptation of a small open model, compared with prompting and few-shot baselines on a fixed evaluation set. | AI-12 Model Adaptation (Fine-tuning, PEFT, Distillation) (T3) | TBD (see catalogue) |
| 62 | `Pro/Natural Language Processing/tasks.md` | T2 Build Multi-lingual NLP System | IMPROVE | Highly relevant to CLBG. Anchor it on MasakhaNER 2.0 / AfriSenti (Hausa, Igbo, Yorùbá, Pidgin), require zero-shot vs fine-tuned transfer and a tokenisation-fertility analysis. | ML-08 Natural Language Processing (T3) | TBD (see catalogue) |
| 63 | `Pro/Natural Language Processing/tasks.md` | T3 Advanced Text Generation System | REPLACE | GPT-2 controllable generation is obsolete. The lasting skills are factuality checks, toxicity filtering, failure-mode documentation and human-evaluation design. Replace with an LLM output evaluation and guardrail task. | AI-10 AI Evaluation and Observability (T3); AI-11 AI Security and Responsible AI | TBD (see catalogue) |

## Coverage by new unit

| New unit | Legacy rows feeding it (primary or secondary) |
|---|---|
| DS-01 Python and Data Wrangling | none (new) |
| DS-02 Data Acquisition and Sourcing | none (new) |
| DS-03 Data Cleaning and Quality | 7, 18 |
| DS-04 Exploratory Data Analysis | 4, 7 |
| DS-05 Probability and Statistics | 6 |
| DS-06 Visualization and Storytelling | 10, 11, 12, 31, 32, 33, 52, 53 |
| DS-07 SQL and Database Analytics | 4 (secondary only) |
| DS-08 Inference, Experimentation and Causal Thinking | 25, 46, 47, 49 |
| DS-09 Decision and Business Analytics | 5, 26, 27, 30, 48 |
| DS-10 Time-Series Analysis and Forecasting | 29, 47 |
| DS-11 Analytical Pipelines and Data Engineering | 46, 50, 52 (secondary) |
| DS-12 Applied Research and Reproducible Communication | 54 |
| ML-01 Mathematical and Computational Foundations | 2, 14, 16 |
| ML-02 Supervised Learning and Ensembles | 8, 17, 37, 59 |
| ML-03 Unsupervised and Representation Learning | 31 (secondary), 57 |
| ML-04 Feature Engineering and Data for ML | 9, 18, 38, 50 |
| ML-05 Evaluation, Validation and Model Selection | 24, 28, 39, 51, 58 |
| ML-06 Neural Networks and Deep Learning | 13, 14, 15, 34, 35, 45, 55 |
| ML-07 Computer Vision | 1, 2, 3, 22, 23, 24, 36, 43, 44, 45 |
| ML-08 Natural Language Processing | 19, 20, 40, 41, 62 |
| ML-09 Time-Series ML | none (new; DS-10 rows inform it) |
| ML-10 Recommender and Ranking Systems | none (new) |
| ML-11 Efficient ML and Optimization | 43, 56 |
| ML-12 Model Deployment and Serving | 56, 60 (secondary) |
| ML-13 ML Pipelines, MLOps and Monitoring | 28, 60 |
| ML-14 Responsible ML | 30 (secondary) |
| AI-01 AI Engineering Foundations and Model Fundamentals | 55 (secondary) |
| AI-02 Prompt Engineering and Structured Generation | 42 |
| AI-03 Model APIs and Local Inference | none (new) |
| AI-04 Embeddings and Semantic Search | 21 |
| AI-05 RAG and Knowledge Systems | none (new) |
| AI-06 Agents and Tool Calling | none (new) |
| AI-07 Agentic Workflows and Orchestration | none (new) |
| AI-08 Context Engineering and Memory | none (new) |
| AI-09 Multimodal AI | none (new) |
| AI-10 AI Evaluation and Observability | 42 (secondary), 63 |
| AI-11 AI Security and Responsible AI | 63 (secondary) |
| AI-12 Model Adaptation | 61 |
| AI-13 Production AI Architecture, Cost and Reliability | none (new) |

Eleven of the 39 units have no legacy source at all. Four more (DS-07, ML-14, AI-01, AI-11) have only secondary, bridging sources. All fifteen must be authored essentially from scratch, and nine of them are in AI Engineering.
