import pandas as pd


def load_scores(path):
    return pd.read_csv(path, dtype={"patient_id": str, "household_id": str})


def run_report(df, recall_target=0.9, k=5, seed=0):
    """R8: return a dict with keys n, prevalence, accuracy_always_negative, auc, average_precision, ece,
    threshold, precision_at_threshold, recall_at_threshold, fold_positives (list of k ints).
    Metrics use the y_true and risk_score columns; folds group by household_id."""
    raise NotImplementedError("R8: run_report")


def main(argv=None):
    """R8: `python -m evalkit data.csv --out DIR [--recall-target 0.9]` writes DIR/metrics.json (sorted keys)."""
    raise NotImplementedError("R8: command line")
