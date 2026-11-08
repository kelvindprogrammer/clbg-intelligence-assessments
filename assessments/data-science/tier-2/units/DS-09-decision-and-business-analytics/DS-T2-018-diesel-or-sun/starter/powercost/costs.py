"""Costs, comparison, break-even and sensitivity (R4-R7)."""


def pv_cost(option, paths, annual_rate):
    """R4: present value of total cost per path, shape (n_paths,)."""
    raise NotImplementedError("R4: pv_cost")


def compare(options, paths, annual_rate):
    """R5: DataFrame with columns option, mean, p05, p95, cvar95, prob_cheapest (input order)."""
    raise NotImplementedError("R5: compare")


def breakeven_price(opt_a, opt_b, months, annual_rate):
    """R6: constant diesel price at which the two options have equal present-value cost."""
    raise NotImplementedError("R6: breakeven_price")


def tornado(opt_a, opt_b, base, ranges, months=120):
    """R7: one-at-a-time sensitivity of PV(a) - PV(b); columns param, low_diff, high_diff, swing."""
    raise NotImplementedError("R7: tornado")
