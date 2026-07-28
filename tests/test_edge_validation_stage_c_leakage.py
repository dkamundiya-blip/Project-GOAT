"""
Project GOAT v0.6 — Stage C Temporal Leakage & Embargo Unit Tests
"""

import pytest

from goat.research.edge.validation.exceptions import TemporalLeakageError
from goat.research.edge.validation.leakage import TemporalLeakageGuard


def test_stage_c_embargo_boundary_enforcement():
    # Valid gap (gap = 10 - 5 = 5 >= 5)
    TemporalLeakageGuard.verify_fold_embargo(
        fold_train_end_idx=5, fold_test_start_idx=10, horizon_bars=5
    )

    # Violation gap (gap = 7 - 5 = 2 < 5)
    with pytest.raises(TemporalLeakageError):
        TemporalLeakageGuard.verify_fold_embargo(
            fold_train_end_idx=5, fold_test_start_idx=7, horizon_bars=5
        )
