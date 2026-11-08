# Data dictionary: households.csv

One row per smallholder household, surveyed 12 months after a mobile-banking training programme was offered. Synthetic data.

| Column | Meaning | Measured |
|---|---|---|
| `household_id` | Identifier | n/a |
| `region` | North, Middle, South-West, South-East | before training |
| `income_ngn` | Household monthly income, naira | before training |
| `education_years` | Years of schooling of the household head | before training |
| `distance_km` | Distance to the nearest mobile-money agent | before training |
| `age` | Age of the household head | before training |
| `hh_size` | Household size | before training |
| `trained` | 1 if a member attended the training, else 0 (not randomised: households chose) | the treatment |
| `loan_taken` | 1 if the household took a loan during the 12 months after training | **after** training |
| `visited_agent` | 1 if the household visited a mobile-money agent in the last month | **after** training |
| `savings_ngn` | Savings held at the survey date, naira | outcome, after training |

The estimand is the **total** effect of attending the training on savings, for the households in the survey.
