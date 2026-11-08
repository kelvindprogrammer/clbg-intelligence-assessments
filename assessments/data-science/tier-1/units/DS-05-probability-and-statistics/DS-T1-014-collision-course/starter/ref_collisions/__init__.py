"""ref_collisions: collision analysis of booking references for DS-T1-014.

The public API is fixed because the tests import it. Implement each function in its module.
"""
from .theory import (expected_colliding_pairs, guess_success_prob, max_n_for_risk, min_code_length,
                     p_collision_approx, p_collision_exact, p_collision_nonuniform)
from .empirical import (ALPHABET, Interval, SpaceEstimate, char_uniformity_pvalue, count_colliding_pairs,
                        estimate_space_size, excess_collision_pvalue, simulate_collision_prob)

__all__ = [
    "p_collision_exact", "p_collision_approx", "expected_colliding_pairs", "p_collision_nonuniform",
    "max_n_for_risk", "min_code_length", "guess_success_prob",
    "ALPHABET", "Interval", "SpaceEstimate", "simulate_collision_prob", "count_colliding_pairs",
    "estimate_space_size", "char_uniformity_pvalue", "excess_collision_pvalue",
]
