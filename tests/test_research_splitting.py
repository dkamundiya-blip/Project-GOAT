"""
Project GOAT v0.3 — Unit Tests for Chronological Splitter

Tests Amendment Requirement I:
- Holdout partition remains sealed by default unless explicitly allowed.
- Chronological time-series splitting with zero random shuffling.
"""

import pandas as pd
import pytest

from goat.research.splitting import ChronologicalSplitter


def test_chronological_splitter_sealed_holdout_discipline() -> None:
    """Amendment I: Holdout partition is sealed and inaccessible by default."""
    dates = pd.date_range("2024-07-22", periods=100, freq="1min")
    df = pd.DataFrame({"timestamp": dates, "close": range(100)})

    splitter = ChronologicalSplitter(train_ratio=0.6, val_ratio=0.2, holdout_ratio=0.2)

    # 1. Sealed holdout (default)
    parts_sealed = splitter.split(df, allow_holdout=False)
    assert len(parts_sealed["train"]) == 60
    assert len(parts_sealed["validation"]) == 20
    assert len(parts_sealed["holdout"]) == 0  # Sealed!

    # 2. Unsealed holdout (explicitly allowed)
    parts_open = splitter.split(df, allow_holdout=True)
    assert len(parts_open["holdout"]) == 20
    assert parts_open["holdout"]["close"].iloc[0] == 80  # Chronological continuation
