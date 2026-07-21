"""
Project GOAT v0.3 — Unit Tests for Impulse & Pullback Event Characterization
"""

import pandas as pd

from goat.research.events import ImpulseCharacterization, PullbackCharacterization


def test_impulse_and_pullback_characterization() -> None:
    """Test detecting impulse events and retrospective pullback measurements."""
    # Flat series with sharp spike at index 25
    prices = [100.0] * 25 + [120.0] + [115.0, 110.0, 112.0, 114.0, 115.0]
    dates = pd.date_range("2024-07-22", periods=len(prices), freq="1min")
    df = pd.DataFrame({"timestamp": dates, "close": prices})

    imp_detector = ImpulseCharacterization(std_threshold=1.5, lookback_window=20)
    impulses = imp_detector.detect_impulses(df, price_col="close")

    assert len(impulses) >= 1
    assert "is_impulse" in impulses.columns

    pb_analyzer = PullbackCharacterization(forward_horizon=4)
    pullbacks = pb_analyzer.analyze_pullbacks(df, impulses, price_col="close")

    assert not pullbacks.empty
    assert "retracement_fraction" in pullbacks.columns
