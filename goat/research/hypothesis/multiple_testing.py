"""
Project GOAT v0.4 — Multiple Hypothesis Testing & FDR Correction

Implements the Benjamini-Hochberg False Discovery Rate (FDR) control procedure.
Calculates q-values across the complete registered experiment family.
"""

from __future__ import annotations

import numpy as np

from goat.logging import get_logger

_log = get_logger("hypothesis.multiple_testing")


def benjamini_hochberg_fdr(
    p_values: list[float] | np.ndarray,
    alpha: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
    """Perform Benjamini-Hochberg False Discovery Rate (FDR) correction.

    Args:
        p_values: List or array of raw p-values across an experiment family of size M.
        alpha: Target FDR significance threshold (default 0.05).

    Returns:
        Tuple of (adjusted_q_values: np.ndarray, is_rejected_mask: np.ndarray).
    """
    pvals = np.asarray(p_values, dtype=np.float64)
    m = len(pvals)

    if m == 0:
        return np.array([]), np.array([], dtype=bool)

    sorted_indices = np.argsort(pvals)
    sorted_pvals = pvals[sorted_indices]

    # q_i = min_{k >= i} (M/k * p_(k))
    q_sorted = np.zeros(m, dtype=np.float64)
    q_sorted[-1] = sorted_pvals[-1]

    for i in range(m - 2, -1, -1):
        k = i + 1
        q_val = (m / k) * sorted_pvals[i]
        q_sorted[i] = min(q_val, q_sorted[i + 1])

    # Cap q-values at 1.0
    q_sorted = np.minimum(q_sorted, 1.0)

    # Re-order to match original p_values order
    q_values = np.zeros(m, dtype=np.float64)
    q_values[sorted_indices] = q_sorted

    is_rejected = q_values <= alpha

    _log.info(
        "fdr_correction_applied",
        total_tests=m,
        alpha=alpha,
        significant_count=int(np.sum(is_rejected)),
    )

    return q_values, is_rejected
