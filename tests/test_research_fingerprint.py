"""
Project GOAT v0.3 — Unit Tests for Market Fingerprint Generator & Comparator
"""

import pandas as pd

from goat.research.fingerprint import compare_market_fingerprints, generate_market_fingerprint


def test_market_fingerprint_generation_and_comparison() -> None:
    """Test generating MarketFingerprint objects and comparative summary."""
    dates = pd.date_range("2024-07-22", periods=1200, freq="1min")
    prices = [100.0 + (i * 0.05) for i in range(1200)]
    df1 = pd.DataFrame({"timestamp": dates, "close": prices, "open": prices, "high": [p + 0.1 for p in prices], "low": [p - 0.1 for p in prices]})

    fp1 = generate_market_fingerprint(df1, symbol="R_10", timeframe="M1")
    assert fp1.symbol == "R_10"
    assert fp1.sufficiency.is_sufficient is True
    assert "mean" in fp1.distribution
    assert "autocorr_lag_1" in fp1.serial_dependence

    fp_json = fp1.to_json()
    assert "R_10" in fp_json

    # Cross-market comparison
    fp2 = generate_market_fingerprint(df1, symbol="R_50", timeframe="M1")
    comp_df = compare_market_fingerprints([fp1, fp2])

    assert len(comp_df) == 2
    assert "symbol" in comp_df.columns
    assert "std_return" in comp_df.columns
