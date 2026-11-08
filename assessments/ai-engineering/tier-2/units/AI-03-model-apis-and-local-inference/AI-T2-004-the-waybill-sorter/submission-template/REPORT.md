# REPORT: AI-T2-004

**Member:** `<name>`   **Commit SHA:** `<sha>`

## 1. Recommendation (for the head of dispatch)
Batch size, provider order, cooldown, expected cost, makespan and accuracy for a night of 600 waybills.

## 2. Evidence
Tables over at least 3 seeds: batch-size sweep; cache on/off; failover on/off; naive baseline. Mean and spread.

## 3. How the batch size was chosen
Your rule for `choose_batch_size`, the noise in a small dev set, and what you did about it.

## 4. Failure behaviour
What happens in the outage, with all providers down, and with truncated replies. Cost of bad replies.

## 5. Privacy and limits
The D.3 paragraph, and what the mock cannot tell you about real providers.

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
