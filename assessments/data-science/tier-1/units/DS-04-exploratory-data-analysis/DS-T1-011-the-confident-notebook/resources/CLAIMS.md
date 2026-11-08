# The Ten Claims (from `flawed_notebook/agent_insights.py`)

Each claim below is quoted from the Growth Analytics notebook, with the number it printed on the official data. Under each claim, **"Corrected quantity"** defines exactly what your `notebook_audit` function must compute. That definition is fixed so that everyone's numbers can be compared. It does **not** tell you whether the claim is right or why it might be wrong: deciding that is your job.

Conventions: "2025 agent-months" means rows of `monthly_activity.csv` whose `month` starts with `2025`. "Mean" is the arithmetic mean over the rows described. All ratios are *first group divided by second group*.

---

### C1. "Our 2023 recruits are our best agents."
> Using the CRM snapshot of active agents, 2023-cohort agents average **1.29×** the monthly transactions of 2025-cohort agents in 2025. *Recommendation: repeat the 2023 recruitment strategy.*

**Corrected quantity (`c1_cohort_ratio`):** using **all** agents in `agents.csv`, take every agent-month whose tenure (months since `onboard_month`, so the onboarding month has tenure 0) is 0 to 5. Report mean `txn_count` for agents onboarded in 2023 divided by mean `txn_count` for agents onboarded in 2025.

### C2. "The fraud flag is reliable."
> The flag agrees with confirmed fraud in **97.4%** of 2025 agent-months, so a flagged agent-month is 97.4% likely to be real fraud. *Recommendation: suspend flagged agents automatically.*

**Corrected quantity (`c2_ppv`):** among 2025 agent-months with `fraud_flagged = 1`, the share with `fraud_confirmed = 1`.

### C3. "Lagos versus Kano."
> On the chart (`flawed_notebook/c3_value_by_state.png`), the Lagos bar is about twice the height of the Kano bar, so Lagos agents process **about twice** the value of Kano agents.

**Corrected quantity (`c3_value_ratio`):** median `txn_value_ngn` over Lagos 2025 agent-months divided by the median over Kano 2025 agent-months.

### C4. "Training works."
> Trained agents average **1.41×** the monthly transactions of untrained agents in 2025, so training raises transactions by 41%. *Recommendation: train every agent.*

**Corrected quantity (`c4_stratified_training_ratio`):** within each `lga_type` separately, compute mean `txn_count` of trained 2025 agent-months divided by mean `txn_count` of untrained 2025 agent-months. Combine the two ratios as a weighted average, where each weight is the number of distinct trained agents with at least one 2025 agent-month in that `lga_type`.

### C5. "Rural agents are a fraud risk."
> Across the 12 states, the share of rural agent-months and the confirmed-fraud rate are correlated at **r = 0.83**, so rural agents are more fraud-prone. *Recommendation: tighter KYC for rural agents.*

**Corrected quantity (`c5_mh_rate_ratio`):** the Mantel–Haenszel rate ratio of confirmed fraud, rural versus urban, over 2025 agent-months, stratified by state. For each state s, let a = rural fraud events, n₁ = rural agent-months, b = urban fraud events, n₀ = urban agent-months and N = n₁ + n₀. Report Σₛ(a·n₀/N) ÷ Σₛ(b·n₁/N), skipping any state with no rural or no urban agent-months.

### C6. "Coaching calls turn around weak agents."
> The coached members of the Q1-2025 bottom 120 improved their mean monthly transactions by **16%** from Q1 to Q2 2025. *Recommendation: coach the bottom quartile every quarter.*

**Corrected quantity (`c6_coaching_difference`):** among agents with `q1_bottom_120 = 1`, compute for each `coached_q2` group: (mean `txn_count` over its April–June 2025 agent-months) ÷ (mean `txn_count` over its January–March 2025 agent-months) − 1. Report the coached value minus the uncoached value.

### C7. "Urban agents hold more float."
> The median float balance of urban 2025 agent-months is **1.78×** that of rural ones.

**Corrected quantity (`c7_float_ratio`):** median `float_balance_avg_ngn` over urban 2025 agent-months divided by the median over rural 2025 agent-months.

### C8. "The new fraud rules engine has not changed investigators' workload."
> The flag rate went from **3.7%** of agent-months in H1 2025 to **4.9%** in H2 2025 (after the July rules-engine change), a change of only **1.2%**. *Recommendation: no extra investigators needed.*

**Corrected quantity (`c8_relative_flag_rate_change`):** (share of July–December 2025 agent-months flagged) ÷ (share of January–June 2025 agent-months flagged) − 1.

### C9. "December is our biggest month."
> December 2025 had the highest total transaction value of any month in 2025.

**Corrected quantity (`c9_december_ratio`):** total `txn_value_ngn` in 2025-12 divided by the largest monthly total among the other eleven months of 2025.

### C10. "One area has a churn problem."
> Of every state and area-type group tested, **Kaduna/rural** churn differs significantly from the network (**p = 0.011**). *Recommendation: send a retention team.*

**Corrected quantity (`c10_bonferroni_min_p`):** consider agents with at least one 2025 agent-month; an agent "churned in 2025" if its `churn_month` starts with `2025`. For each `state`/`lga_type` group, run a two-sided exact binomial test (`scipy.stats.binomtest`) of the group's churned count against the overall churned share. Report min(1, smallest p-value × number of groups).
