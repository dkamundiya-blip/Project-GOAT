"""
Project GOAT v0.4 — Dependence & Embargo Spacing Engine

Handles serial dependence and overlapping forward horizons by filtering
events with non-overlapping embargo spacing.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from goat.logging import get_logger

_log = get_logger("hypothesis.dependence")


def apply_embargo_spacing(
    event_mask: pd.Series,
    horizon_k: int,
) -> pd.Series:
    """Filter triggered boolean event mask using non-overlapping embargo spacing.

    If an event triggers at bar i, subsequent events occurring at bars i+1 .. i+k-1 are suppressed.

    Args:
        event_mask: Boolean Series indicating triggered condition events.
        horizon_k: Embargo horizon in bars.

    Returns:
        Filtered boolean Series with embargo spacing enforced.
    """
    if horizon_k <= 1 or not event_mask.any():
        return event_mask.copy()

    filtered = pd.Series(False, index=event_mask.index)
    last_event_loc = -horizon_k - 1

    event_indices = np.where(event_mask.to_numpy())[0]

    for loc in event_indices:
        if loc >= last_event_loc + horizon_k:
            filtered.iloc[loc] = True
            last_event_loc = loc

    return filtered


def evaluate_dependence_risk(
    event_mask: pd.Series,
    horizon_k: int,
) -> tuple[bool, str]:
    """Check if triggered events suffer from significant overlapping outcome dependence.

    Returns:
        Tuple of (dependence_overlap_risk: bool, warning_message: str).
    """
    if horizon_k <= 1:
        return False, ""

    event_indices = np.where(event_mask.to_numpy())[0]
    if len(event_indices) < 2:
        return False, ""

    gaps = np.diff(event_indices)
    overlapping_count = int(np.sum(gaps < horizon_k))
    pct_overlap = overlapping_count / len(gaps)

    if pct_overlap > 0.10:
        warning = (
            f"Overlapping forward outcomes detected: {overlapping_count}/{len(gaps)} gaps "
            f"({pct_overlap:.1%}) are less than forward horizon k={horizon_k} bars."
        )
        return True, warning

    return False, ""
