"""
Project GOAT v0.6 — TemporalLeakageGuard Unit Tests
"""

import pandas as pd
import pytest

from goat.research.edge.validation.exceptions import TemporalLeakageError
from goat.research.edge.validation.leakage import TemporalLeakageGuard


def test_chronological_ordering_verification():
    valid_ts = ["2024-01-01", "2024-01-02", "2024-01-03"]
    TemporalLeakageGuard.verify_chronological_ordering(valid_ts)

    invalid_ts = ["2024-01-01", "2024-01-03", "2024-01-02"]
    with pytest.raises(TemporalLeakageError):
        TemporalLeakageGuard.verify_chronological_ordering(invalid_ts)


def test_partition_boundary_verification():
    train_df = pd.DataFrame({"timestamp": ["2024-01-01", "2024-01-02"]})
    val_df = pd.DataFrame({"timestamp": ["2024-01-03", "2024-01-04"]})

    TemporalLeakageGuard.verify_partition_boundaries(train_df, val_df)

    # Overlapping boundary must be rejected
    overlap_val_df = pd.DataFrame({"timestamp": ["2024-01-02", "2024-01-03"]})
    with pytest.raises(TemporalLeakageError):
        TemporalLeakageGuard.verify_partition_boundaries(train_df, overlap_val_df)


def test_fold_embargo_boundary_verification():
    # Gap = 10 - 5 = 5 bars. Required horizon = 5 bars -> Valid
    TemporalLeakageGuard.verify_fold_embargo(
        fold_train_end_idx=5, fold_test_start_idx=10, horizon_bars=5
    )

    # Gap = 8 - 5 = 3 bars. Required horizon = 5 bars -> Violation
    with pytest.raises(TemporalLeakageError):
        TemporalLeakageGuard.verify_fold_embargo(
            fold_train_end_idx=5, fold_test_start_idx=8, horizon_bars=5
        )
