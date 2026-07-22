"""
Project GOAT v0.4 — Statistical Testing & Effect-Size Engine

Implements statistical tests (Welch's t-test, Mann-Whitney U, Permutation test, Fisher's exact)
and effect-size calculators with explicit metric selection and seed determinism.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from goat.logging import get_logger

_log = get_logger("hypothesis.testing")


def calculate_effect_size(
    cond_arr: np.ndarray,
    base_arr: np.ndarray,
    method: str = "cohens_d",
) -> float:
    """Calculate specified effect size metric between conditional and baseline samples.

    Args:
        cond_arr: Array of conditional outcomes.
        base_arr: Array of baseline outcomes.
        method: Metric name (``"cohens_d"``, ``"mean_diff"``, ``"median_diff"``, ``"rank_biserial"``, ``"relative_risk"``, ``"prop_diff"``).

    Returns:
        Float effect size value.
    """
    c = cond_arr[np.isfinite(cond_arr)]
    b = base_arr[np.isfinite(base_arr)]

    if len(c) == 0 or len(b) == 0:
        return 0.0

    if method in ("cohens_d", "standardized_mean_diff"):
        m1, m2 = np.mean(c), np.mean(b)
        n1, n2 = len(c), len(b)
        v1, v2 = np.var(c, ddof=1) if n1 > 1 else 0.0, np.var(b, ddof=1) if n2 > 1 else 0.0
        pooled_std = np.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / max(1, n1 + n2 - 2))
        return float((m1 - m2) / pooled_std) if pooled_std > 0 else 0.0

    elif method == "mean_diff":
        return float(np.mean(c) - np.mean(b))

    elif method == "median_diff":
        return float(np.median(c) - np.median(b))

    elif method == "rank_biserial":
        n1, n2 = len(c), len(b)
        if n1 == 0 or n2 == 0:
            return 0.0
        res = stats.mannwhitneyu(c, b, alternative="two-sided")
        u_stat = float(res.statistic)
        return float(2.0 * u_stat / (n1 * n2) - 1.0)

    elif method == "relative_risk":
        # Binary outcome assumes > 0 is event
        c_events = np.sum(c > 0)
        b_events = np.sum(b > 0)
        p1 = c_events / len(c)
        p2 = b_events / len(b)
        if p2 == 0:
            return 1.0
        return float(p1 / p2)

    elif method == "prop_diff":
        p1 = np.mean(c > 0)
        p2 = np.mean(b > 0)
        return float(p1 - p2)

    else:
        raise ValueError(f"Unknown effect size method '{method}'")


def run_statistical_test(
    cond_arr: np.ndarray,
    base_arr: np.ndarray,
    test_type: str = "welch_ttest",
    seed: int = 42,
    num_permutations: int = 1000,
) -> tuple[float, float]:
    """Execute statistical hypothesis test between conditional and baseline samples.

    Args:
        cond_arr: Conditional outcome observations.
        base_arr: Baseline outcome observations.
        test_type: Test identifier (``"welch_ttest"``, ``"mann_whitney"``, ``"permutation"``, ``"fisher_exact"``).
        seed: Random seed for stochastic tests.
        num_permutations: Number of permutations if ``test_type="permutation"``.

    Returns:
        Tuple of (test_statistic, p_value).
    """
    c = cond_arr[np.isfinite(cond_arr)]
    b = base_arr[np.isfinite(base_arr)]

    if len(c) < 2 or len(b) < 2:
        return 0.0, 1.0

    if test_type == "welch_ttest":
        res = stats.ttest_ind(c, b, equal_var=False)
        stat = float(res.statistic) if np.isfinite(res.statistic) else 0.0
        pval = float(res.pvalue) if np.isfinite(res.pvalue) else 1.0
        return stat, pval

    elif test_type == "mann_whitney":
        res = stats.mannwhitneyu(c, b, alternative="two-sided")
        return float(res.statistic), float(res.pvalue)

    elif test_type == "permutation":
        rng = np.random.default_rng(seed)
        observed_diff = np.abs(np.mean(c) - np.mean(b))
        combined = np.concatenate([c, b])
        n_c = len(c)

        perm_diffs = np.zeros(num_permutations)
        for i in range(num_permutations):
            shuffled = rng.permutation(combined)
            perm_diffs[i] = np.abs(np.mean(shuffled[:n_c]) - np.mean(shuffled[n_c:]))

        p_val = float(np.mean(perm_diffs >= observed_diff))
        # Ensure non-zero min p-value for finite permutations
        p_val = max(p_val, 1.0 / num_permutations)
        return float(observed_diff), p_val

    elif test_type == "fisher_exact":
        c_succ = int(np.sum(c > 0))
        c_fail = int(len(c) - c_succ)
        b_succ = int(np.sum(b > 0))
        b_fail = int(len(b) - b_succ)

        table = [[c_succ, c_fail], [b_succ, b_fail]]
        res = stats.fisher_exact(table)
        return float(res.statistic), float(res.pvalue)

    else:
        raise ValueError(f"Unknown statistical test type '{test_type}'")
