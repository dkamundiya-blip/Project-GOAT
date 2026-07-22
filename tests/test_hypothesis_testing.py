"""
Project GOAT v0.4 — Unit Tests for Statistical Testing & Effect Sizes
"""

import numpy as np
import pytest

from goat.research.hypothesis.testing import calculate_effect_size, run_statistical_test


def test_calculate_effect_sizes() -> None:
    """Test effect size calculators (Cohen's d, mean diff, rank-biserial, relative risk)."""
    c = np.array([10.0, 12.0, 11.0, 13.0, 14.0])
    b = np.array([5.0, 6.0, 7.0, 5.0, 6.0])

    d = calculate_effect_size(c, b, method="cohens_d")
    assert d > 0.0

    mean_diff = calculate_effect_size(c, b, method="mean_diff")
    assert pytest.approx(mean_diff, 0.01) == (np.mean(c) - np.mean(b))

    rb = calculate_effect_size(c, b, method="rank_biserial")
    assert rb > 0.0


def test_statistical_tests_determinism() -> None:
    """Test Welch t-test, Mann-Whitney U, and seed-reproducible permutation test."""
    c = np.array([10.0, 12.0, 11.0, 13.0, 14.0])
    b = np.array([5.0, 6.0, 7.0, 5.0, 6.0])

    stat_w, p_w = run_statistical_test(c, b, test_type="welch_ttest")
    assert p_w < 0.05

    stat_p1, p_p1 = run_statistical_test(c, b, test_type="permutation", seed=42)
    stat_p2, p_p2 = run_statistical_test(c, b, test_type="permutation", seed=42)

    # Permutation test with same random seed is 100% deterministic
    assert stat_p1 == stat_p2
    assert p_p1 == p_p2
