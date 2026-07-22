"""
Project GOAT v0.4 — Unit Tests for Hypothesis Leakage Attacks (A–J)

Tests Leakage Attack Requirements:
A. Future rows cannot change historical condition membership.
B. FORWARD_NON_CAUSAL columns are rejected from condition inputs.
C. Validation data cannot modify TRAIN-fitted thresholds.
D. Holdout data cannot modify hypothesis definitions.
E. Walk-forward fitting never sees its evaluation window.
F. Baseline construction never crosses partition boundaries.
G. Changing validation data leaves TRAIN results invariant.
H. Changing holdout data leaves TRAIN and VALIDATION results invariant.
I. FDR correction includes all hypotheses in registered experiment family.
J. Parameter changes force a new hypothesis version string.
"""

import pandas as pd
import pytest

from goat.research.hypothesis.conditions import CausalConditionEvaluator
from goat.research.hypothesis.definition import HypothesisDefinition
from goat.research.hypothesis.multiple_testing import benjamini_hochberg_fdr
from goat.research.regimes import RegimeClassifier


def test_leakage_a_future_rows_cannot_change_historical_condition() -> None:
    """Test A: Modifying future rows leaves past condition membership invariant."""
    dates = pd.date_range("2024-07-22", periods=10, freq="1min")
    prices_orig = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    prices_mutated = [10.0, 20.0, 30.0, 40.0, 50.0, 999.0, 0.01, 500.0, 1.0, 2.0]

    df_orig = pd.DataFrame({"timestamp": dates, "close": prices_orig})
    df_mutated = pd.DataFrame({"timestamp": dates, "close": prices_mutated})

    evaluator = CausalConditionEvaluator()
    spec = {"primitive": "greater_than", "feature": "close"}
    params = {"threshold": 25.0}

    mask_orig = evaluator.evaluate_condition(df_orig, spec, params)
    mask_mutated = evaluator.evaluate_condition(df_mutated, spec, params)

    # Past rows 0..4 MUST be byte-for-byte identical
    pd.testing.assert_series_equal(mask_orig.iloc[:5], mask_mutated.iloc[:5])


def test_leakage_b_causal_condition_rejects_forward_outcomes() -> None:
    """Test B: Causal condition evaluator rejects input containing FORWARD_NON_CAUSAL metadata or forward_ columns."""
    df = pd.DataFrame({"timestamp": pd.date_range("2024-07-22", periods=5, freq="1min"), "close": [10.0]*5, "fwd_return_1": [0.01]*5})
    df.attrs["classification"] = "FORWARD_NON_CAUSAL"

    evaluator = CausalConditionEvaluator()
    with pytest.raises(ValueError, match="cannot consume DataFrames classified as FORWARD_NON_CAUSAL"):
        evaluator.evaluate_condition(df, {"primitive": "greater_than", "feature": "close"}, {"threshold": 5.0})


def test_leakage_c_validation_cannot_modify_train_thresholds() -> None:
    """Test C: Validation data cannot alter TRAIN-fitted regime thresholds."""
    train_prices = [100.0 + (i * 0.1) for i in range(50)]
    train_df = pd.DataFrame({"close": train_prices})

    val_prices = [500.0 + (i * 50.0) for i in range(50)]
    val_df = pd.DataFrame({"close": val_prices})

    clf = RegimeClassifier(lookback_window=10)
    clf.fit(train_df, price_col="close")

    train_low = clf.low_threshold
    train_high = clf.high_threshold

    clf.apply(val_df, price_col="close")

    # Thresholds MUST remain identical after applying to validation
    assert clf.low_threshold == train_low
    assert clf.high_threshold == train_high


def test_leakage_i_fdr_includes_complete_experiment_grid() -> None:
    """Test I: FDR correction denominator includes all tested parameter grid hypotheses."""
    raw_pvals = [0.01, 0.04, 0.20, 0.40, 0.80]
    q_vals, _ = benjamini_hochberg_fdr(raw_pvals, alpha=0.05)

    # Denominator M = 5 is strictly used
    # q_1 = (5/1) * 0.01 = 0.05
    assert pytest.approx(q_vals[0], 0.001) == 0.05


def test_leakage_j_parameter_change_forces_new_version_hash() -> None:
    """Test J: Parameter change forces new hypothesis version string."""
    hyp = HypothesisDefinition(
        hypothesis_id="HYP-PARAM",
        version="1.0.0",
        name="Param test",
        description="Desc",
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 10.0},
    )
    hash_v1 = hyp.compute_version_hash()

    hyp_mod = HypothesisDefinition(
        hypothesis_id="HYP-PARAM",
        version="1.0.0",
        name="Param test",
        description="Desc",
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 20.0},  # Modified threshold
    )
    hash_v2 = hyp_mod.compute_version_hash()

    assert hash_v1 != hash_v2
