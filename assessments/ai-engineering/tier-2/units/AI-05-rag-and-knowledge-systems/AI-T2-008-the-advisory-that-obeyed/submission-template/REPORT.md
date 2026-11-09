# REPORT: AI-T2-008 The Advisory That Obeyed

**Member:** `<name>`   **Commit SHA:** `<sha>`

## 1. Recommendation (one paragraph)
The shipped `DEFAULT_CFG`, its accuracy, wrong_rate and abstain_recall, and the main residual risk.

## 2. Retrieval comparison
Recall at 1 and 3 on `direct` and `syn` questions for bm25, dense and hybrid, on at least 3 seeds. Explain what fusion adds.

## 3. Ablation
Each stage off in turn (sanitize, newest_only, verify, sufficiency) across the three mock modes: accuracy, wrong_rate, abstain_recall, injected.

## 4. Threshold and chunk-size choices
Sweep `min_coverage` and `max_words`; justify the choice and say how you avoided tuning on the test seeds.

## 5. Safety and limits
Unseen hijack phrasings, benign decoys, what the pipeline does not protect against, and the D.3 paragraph.

## AI use and sources declaration

### 1. AI tools used
| Tool | What I used it for | Example prompt | How I verified the output |
|---|---|---|---|
| | | | |

If you used none, write "None".

### 2. External sources and adapted code
| Source (link) | What I used | Where in my code |
|---|---|---|
| | | |

### 3. Collaboration
Who did you discuss *general techniques* with, and on what topic? No code, counts or report text may be shared.

### 4. Declaration
I confirm that I can explain and modify every part of this submission, and that this declaration is complete and accurate.
