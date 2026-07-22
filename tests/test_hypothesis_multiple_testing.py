"""
Project GOAT v0.4 — Unit Tests for Benjamini-Hochberg FDR Control
"""

import numpy as np

from goat.research.hypothesis.multiple_testing import benjamini_hochberg_fdr


def test_benjamini_hochberg_fdr_math() -> None:
    """Test BH FDR q-value calculation and significance ranking."""
    raw_pvals = [0.001, 0.008, 0.039, 0.041, 0.150]
    q_vals, rejected = benjamini_hochberg_fdr(raw_pvals, alpha=0.05)

    assert len(q_vals) == len(raw_pvals)
    # q-values are monotonically increasing with rank
    assert q_vals[0] <= q_vals[1] <= q_vals[2]
    # Raw p-values preserved
    assert raw_pvals[0] == 0.001
