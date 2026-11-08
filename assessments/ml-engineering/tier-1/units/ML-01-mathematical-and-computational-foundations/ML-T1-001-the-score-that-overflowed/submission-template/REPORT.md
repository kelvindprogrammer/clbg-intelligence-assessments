# REPORT: ML-T1-001 The Score That Overflowed

**Member:** `<name>`   **Commit SHA:** `<sha>`

## 1. What broke (one paragraph per naive function)
For each function in `naive.py`: the input that breaks it, the intermediate quantity that overflows, underflows or cancels, and the measured result.

## 2. How each fix works
Algebra for the shift in `logsumexp`, the `log1p` form of BCE, and the gradient of softmax cross-entropy. Include the tolerance you chose for the gradient check and why.

## 3. Evidence
A table of naive versus stable results at logits 10, 100, 1000 and 10000 in float32 and float64. State the command that regenerates it.

## 4. Model results
Final loss and agreement with scikit-learn; what would have happened without internal standardisation.

## 5. Limits and risks
What your code still cannot do; the NDPA/operational paragraph from D.3.

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

Signed: `<name>`  Date: `<date>`
