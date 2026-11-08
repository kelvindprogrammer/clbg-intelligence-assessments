"""Newsvendor arithmetic (R1-R3, R6, R7)."""


def critical_ratio(price, cost, salvage):
    """R1: (price - cost) / (price - salvage). ValueError unless salvage < cost < price."""
    raise NotImplementedError("R1: critical_ratio")


def expected_profit(q, demand, price, cost, salvage):
    """R2: mean profit of stocking q units over an array of demand outcomes."""
    raise NotImplementedError("R2: expected_profit")


def best_quantity(demand, price, cost, salvage):
    """R3: (q, expected_profit) maximising the empirical expected profit over q = 0..max(demand); ties go to the smaller q."""
    raise NotImplementedError("R3: best_quantity")


def poisson_quantity(lam, price, cost, salvage):
    """R6: profit-maximising integer q when demand ~ Poisson(lam) (smallest q with cdf(q) >= critical ratio)."""
    raise NotImplementedError("R6: poisson_quantity")


def expected_profit_poisson(q, lam, price, cost, salvage):
    """R7: exact expected profit of stocking q when demand ~ Poisson(lam)."""
    raise NotImplementedError("R7: expected_profit_poisson")
