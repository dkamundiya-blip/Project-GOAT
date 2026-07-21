"""
Project GOAT v0.3 — Unit Tests for Forward Outcome Table Generator

Tests Amendment Requirement C:
- ForwardOutcomeTable metadata is classified as FORWARD_NON_CAUSAL.
- Causal feature-generation functions explicitly reject DataFrames containing FORWARD_NON_CAUSAL metadata or forward outcome columns.
"""

import pandas as pd
import pytest

from goat.research.outcomes import ForwardOutcomeTable
from goat.research.returns import calculate_returns
from goat.research.stats import calculate_range_stats


def test_forward_outcome_table_generation_and_metadata() -> None:
    """Test forward outcomes calculation and metadata classification."""
    df = pd.DataFrame([
        {"timestamp": "2024-07-22T00:00:00Z", "close": 100.0, "high": 101.0, "low": 99.0},
        {"timestamp": "2024-07-22T00:01:00Z", "close": 102.0, "high": 103.0, "low": 100.5},
        {"timestamp": "2024-07-22T00:02:00Z", "close": 104.0, "high": 105.0, "low": 101.0},
        {"timestamp": "2024-07-22T00:03:00Z", "close": 98.0, "high": 104.0, "low": 97.0},
    ])

    fwd = ForwardOutcomeTable(horizons=[1, 2])
    outcomes = fwd.compute_outcomes(df, price_col="close")

    assert outcomes.attrs.get("classification") == "FORWARD_NON_CAUSAL"
    assert outcomes.attrs.get("is_causal") is False
    assert "fwd_return_1" in outcomes.columns
    assert "fwd_mfe_1" in outcomes.columns
    assert "fwd_mae_1" in outcomes.columns


def test_causal_api_rejects_forward_outcome_dataframe() -> None:
    """Amendment C: Causal feature-generation functions reject forward outcome DataFrames."""
    df = pd.DataFrame([
        {"timestamp": "2024-07-22T00:00:00Z", "close": 100.0, "fwd_return_1": 0.02},
        {"timestamp": "2024-07-22T00:01:00Z", "close": 102.0, "fwd_return_1": 0.01},
    ])

    # 1. Reject due to forward outcome column
    with pytest.raises(ValueError, match="rejected input DataFrame containing forward outcome column"):
        calculate_returns(df, price_col="close")

    # 2. Reject due to FORWARD_NON_CAUSAL metadata attribute
    clean_df = pd.DataFrame([
        {"timestamp": "2024-07-22T00:00:00Z", "close": 100.0},
        {"timestamp": "2024-07-22T00:01:00Z", "close": 102.0},
    ])
    clean_df.attrs["classification"] = "FORWARD_NON_CAUSAL"

    with pytest.raises(ValueError, match="cannot consume DataFrames classified as FORWARD_NON_CAUSAL"):
        calculate_range_stats(clean_df)
