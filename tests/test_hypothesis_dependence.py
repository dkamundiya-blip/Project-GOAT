"""
Project GOAT v0.4 — Unit Tests for Embargo Spacing & Dependence Handling
"""

import pandas as pd

from goat.research.hypothesis.dependence import apply_embargo_spacing, evaluate_dependence_risk


def test_apply_embargo_spacing() -> None:
    """Test non-overlapping embargo event selection."""
    # Consecutive events at indices 0, 1, 2, 5, 6
    mask = pd.Series([True, True, True, False, False, True, True])

    # Embargo horizon k=3
    filtered = apply_embargo_spacing(mask, horizon_k=3)

    # Index 0 triggered -> suppresses 1 and 2
    # Index 5 triggered -> suppresses 6
    assert filtered.iloc[0] is True or filtered.iloc[0] == 1
    assert filtered.iloc[1] is False or filtered.iloc[1] == 0
    assert filtered.iloc[2] is False or filtered.iloc[2] == 0
    assert filtered.iloc[5] is True or filtered.iloc[5] == 1
    assert filtered.iloc[6] is False or filtered.iloc[6] == 0


def test_evaluate_dependence_risk() -> None:
    """Test dependence risk detection for overlapping events."""
    mask = pd.Series([True, True, True, True, True])
    risk, warning = evaluate_dependence_risk(mask, horizon_k=5)

    assert risk is True
    assert "Overlapping forward outcomes" in warning
