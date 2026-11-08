# %% [markdown]
# # KoboLink Agent Network: 2025 Insights
# *Growth Analytics team, internal circulation. Prepared for the Q1 2026 strategy offsite.*
#
# This notebook explores agent performance, fraud and churn across our 12 states, and makes
# ten recommendations. It is written in "percent" format: it runs as a plain script
# (`python agent_insights.py`) and opens as a notebook in Jupyter or VS Code.
#
# **DS-T1-011 note to members:** this is the artefact you are auditing. Do not "fix" this file.
# Your corrected analyses go in your own `notebook_audit` package. Several of its conclusions are
# wrong for different reasons, and some are right.

# %%
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parent
agents = pd.read_csv(DATA / "agents.csv", dtype=str, keep_default_na=False)
act = pd.read_csv(DATA / "monthly_activity.csv", dtype={"agent_id": str, "month": str})
agents["trained"] = agents["trained"].astype(int)
agents["coached_q2"] = agents["coached_q2"].astype(int)
agents["q1_bottom_120"] = agents["q1_bottom_120"].astype(int)
y25 = act[act.month.str.startswith("2025")].merge(agents, on="agent_id")
print(f"{len(agents)} agents, {len(act)} agent-months")

# %% [markdown]
# ## C1. Our 2023 recruits are our best agents
# We compare 2025 productivity across onboarding cohorts, using our current active agent
# base (the CRM snapshot only lists active agents).

# %%
active = agents[agents.status == "active"]
cur = act[act.month.str.startswith("2025")].merge(active, on="agent_id")
cur["cohort"] = cur.onboard_month.str[:4]
c1 = cur.groupby("cohort").txn_count.mean()
print("C1 ratio 2023/2025 cohort:", round(c1["2023"] / c1["2025"], 2))
# CLAIM C1: 2023-cohort agents are about this much more productive; repeat the 2023 recruitment strategy.

# %% [markdown]
# ## C2. The fraud flag is reliable

# %%
acc = (y25.fraud_flagged == y25.fraud_confirmed).mean()
print("C2 flag accuracy:", round(acc, 3))
# CLAIM C2: the flag is this accurate, so a flagged agent-month is this likely to be real fraud.
# Recommendation: suspend flagged agents automatically.

# %% [markdown]
# ## C3. Lagos versus Kano

# %%
med = y25.groupby("state").txn_value_ngn.median().sort_values()
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(med.index, med.values, color="#4a7")
ax.set_yscale("log")
ax.set_ylabel("Median monthly value per agent (NGN)")
ax.set_title("Agent value by state")
plt.xticks(rotation=45)
plt.tight_layout()
fig.savefig(OUT / "c3_value_by_state.png", dpi=110)
# CLAIM C3: looking at the chart, the Lagos bar is about twice the height of the Kano bar,
# so Lagos agents process about twice the value of Kano agents.

# %% [markdown]
# ## C4. Training works

# %%
t = y25.groupby("trained").txn_count.mean()
print("C4 trained/untrained:", round(t[1] / t[0], 2))
# CLAIM C4: training raises monthly transactions by this factor. Train every agent.

# %% [markdown]
# ## C5. Rural agents are a fraud risk

# %%
st = y25.groupby("state").agg(rural=("lga_type", lambda s: (s == "rural").mean()), fraud=("fraud_confirmed", "mean"))
r = st.rural.corr(st.fraud)
print("C5 state-level correlation rural share vs fraud rate:", round(r, 2))
# CLAIM C5: states with more rural agents have much more fraud, so rural agents are more
# fraud-prone. Recommendation: tighter KYC for rural agents.

# %% [markdown]
# ## C6. Coaching calls turn around weak agents

# %%
b = act.merge(agents, on="agent_id")
b = b[(b.q1_bottom_120 == 1) & (b.coached_q2 == 1)]
q1 = b[b.month.isin(["2025-01", "2025-02", "2025-03"])].txn_count.mean()
q2 = b[b.month.isin(["2025-04", "2025-05", "2025-06"])].txn_count.mean()
print("C6 coached agents' improvement Q1->Q2:", round(q2 / q1 - 1, 2))
# CLAIM C6: coached agents improved by this much, so coaching works. Coach the bottom quartile every quarter.

# %% [markdown]
# ## C7. Urban agents hold more float

# %%
fm = y25.groupby("lga_type").float_balance_avg_ngn.median()
print("C7 median float urban/rural:", round(fm["urban"] / fm["rural"], 2))
# CLAIM C7: urban agents hold higher float balances than rural agents.

# %% [markdown]
# ## C8. The new fraud rules engine (July 2025) has not changed investigators' workload

# %%
h1 = y25[y25.month <= "2025-06"].fraud_flagged.mean()
h2 = y25[y25.month >= "2025-07"].fraud_flagged.mean()
print(f"C8 flag rate H1 {h1:.1%}, H2 {h2:.1%}, change {100 * (h2 - h1):.1f}%")
# CLAIM C8: the flag rate rose by only about this percentage, so investigator workload is essentially unchanged.

# %% [markdown]
# ## C9. December is our biggest month

# %%
tot = y25.groupby("month").txn_value_ngn.sum()
print("C9 top month:", tot.idxmax())
# CLAIM C9: December 2025 had the highest total transaction value of any month in 2025.

# %% [markdown]
# ## C10. One area has a churn problem
# We tested every state and area type (urban/rural) for unusual churn.

# %%
ids = set(y25.agent_id)
a = agents[agents.agent_id.isin(ids)].copy()
a["ch"] = a.churn_month.str.startswith("2025")
p0 = a.ch.mean()
a["group"] = a.state + "/" + a.lga_type
p = a.groupby("group").ch.agg(lambda s: stats.binomtest(int(s.sum()), len(s), p0).pvalue)
print("C10 lowest p-value:", p.idxmin(), round(p.min(), 4))
# CLAIM C10: this group's churn is significantly different from the network (p < 0.05). Send a retention team.
