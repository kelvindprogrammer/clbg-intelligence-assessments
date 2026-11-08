# REPORT: AI-T2-006

**Member:** `<name>`   **Commit SHA:** `<sha>`

## 1. Recommendation (for the head of compliance)
The retriever, its chunk size and fusion, expected quality per query type, and the main risk.

## 2. Evidence
Table over at least 3 seeds, separately for id and topic queries: whole-document BM25, whole-document dense, chunked BM25, chunked dense, hybrid.

## 3. What each decision contributed
Chunk size sweep, fusion comparison, and the case where naive fusion hurt (if you found one) with the reason.

## 4. Method discipline and uncertainty
How the development queries were used; noise in a 120-query evaluation.

## 5. Privacy and limits
The D.3 paragraph, and what the toy embedder cannot tell you about real text.

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
