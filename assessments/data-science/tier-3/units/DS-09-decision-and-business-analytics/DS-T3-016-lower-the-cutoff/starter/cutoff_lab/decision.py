"""Decision layer (R3-R8)."""


def expected_profit(cutoff, df, curve, terms):
    """R3: expected profit per applicant of approving everyone with score >= cutoff."""
    raise NotImplementedError("R3: expected_profit")


def best_cutoff(df, curve, terms, grid=None):
    """R4: (cutoff, profit) maximising R3 over the grid (default range(300, 851, 5)); ties to the lowest cutoff."""
    raise NotImplementedError("R4: best_cutoff")


def bootstrap_cutoff(df, method, degree, terms, n_boot=100, seed=0):
    """R5: applicant-level bootstrap of the whole fit-then-optimise pipeline."""
    raise NotImplementedError("R5: bootstrap_cutoff")


def scenario_profits(df, curve, terms, cutoffs, multipliers):
    """R6: long DataFrame cutoff, multiplier, profit when true default probabilities are scaled."""
    raise NotImplementedError("R6: scenario_profits")


def minimax_regret(table):
    """R7: the cutoff with the smallest worst-case regret across multipliers."""
    raise NotImplementedError("R7: minimax_regret")


def recommend(df, terms, multipliers=(1.0, 1.3, 1.6), n_boot=100, seed=0):
    """R8: dictionary with the recommendation inputs described in the README."""
    raise NotImplementedError("R8: recommend")
