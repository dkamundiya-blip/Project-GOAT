"""
Project GOAT v0.3 — Unit Tests for Trailing Regime Classifier

Tests Amendment Requirement B:
- Fit/apply semantics: Parameters fitted on TRAIN are frozen and applied to VALIDATION/HOLDOUT.
- Validation/holdout observations cannot alter parameters fitted on TRAIN.
"""

import pandas as pd
import pytest

from goat.research.regimes import RegimeClassifier


def test_regime_classifier_fit_on_train_and_apply_frozen() -> None:
    """Amendment B: Validation/holdout data cannot alter parameters fitted on TRAIN."""
    train_prices = [100.0 + (i * 0.1) for i in range(50)]
    train_df = pd.DataFrame({"close": train_prices})

    val_prices = [200.0 + (i * 10.0 if i % 2 == 0 else -i * 5.0) for i in range(50)]  # High vol
    val_df = pd.DataFrame({"close": val_prices})

    clf = RegimeClassifier(lookback_window=10)
    clf.fit(train_df, price_col="close")

    train_low_thresh = clf.low_threshold
    train_high_thresh = clf.high_threshold

    # Apply to validation partition
    val_result = clf.apply(val_df, price_col="close")

    # Fitted threshold parameters remain strictly unchanged after applying to validation
    assert clf.low_threshold == train_low_thresh
    assert clf.high_threshold == train_high_thresh
    assert "volatility_regime" in val_result.columns


def test_regime_classifier_apply_before_fit_raises() -> None:
    """Calling apply() before fit() raises RuntimeError."""
    df = pd.DataFrame({"close": [100.0, 101.0, 102.0]})
    clf = RegimeClassifier()
    with pytest.raises(RuntimeError, match="must be fitted on TRAIN partition before calling apply"):
        clf.apply(df)
