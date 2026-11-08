# CLBG Signature Challenges

The Signature Challenges are CLBG's flagship problems. They're memorable, multidisciplinary and demanding, and they're designed to run as **recurring events, competitions and public showcases**.

| Category | Code | Spirit |
|---|---|---|
| Intelligence Challenges (`intelligence-challenges/`) | `SIG-INT` | Problems that require reasoning across data, models and AI systems at once |
| Data Challenges (`data-challenges/`) | `SIG-DATA` | Investigations where the truth is hidden in the data |
| Machine Learning Challenges (`machine-learning-challenges/`) | `SIG-ML` | Learning systems under realistic pressure: shift, imbalance, budgets |
| AI Engineering Challenges (`ai-engineering-challenges/`) | `SIG-AIE` | Building AI systems that are reliable, secure and honest |
| Research Challenges (`research-challenges/`) | `SIG-RES` | Replication and inquiry, where negative results count |
| Systems and Optimization Challenges (`systems-and-optimization-challenges/`) | `SIG-SYS` | Making things fast, small, cheap and robust |
| Grand Integrated Challenges (`grand-integrated-challenges/`) | `SIG-GRAND` | Multi-week, multi-team, end-to-end problems |

## The shared evaluation protocol

Signature Challenges let members **compare solutions under a common protocol**, without the distortions of single-metric leaderboards such as overfitting to a public test set, leakage, or tuning by random seed.

1. **Hidden, rotated evaluation data.** Final evaluation uses held-out data that participants never see, and it's refreshed each edition.
2. **Rigour-weighted scoring.** Each challenge publishes its own weights, typically:
   - **35%** performance on the hidden evaluation, banded rather than ranked to the decimal (performance within a confidence interval of the best counts as tied);
   - **25%** validity and rigour: baselines, ablations, uncertainty, absence of leakage;
   - **15%** reproducibility, verified by organisers rerunning the submission;
   - **15%** creativity and insight;
   - **10%** communication, through a short technical report and a demo.
3. **Limited submissions** to the hidden evaluation: at most 3 per team.
4. **Reproducibility gate.** Results that organisers can't reproduce are not ranked.
5. **Showcase.** Finalists present their work. Awards recognise *best rigour*, *best insight* and *best negative result*, as well as best performance.

Signature Challenges can also serve as placement evidence. A research-category challenge assessed at the M level counts toward Tier 3 ([placement framework](../docs/placement-framework.md#3-tier-placement)).

<!-- CATALOGUE:START -->
<!-- CATALOGUE:END -->
