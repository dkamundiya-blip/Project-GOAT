"""
Project GOAT Phase 6 — Unit Tests for Statistical Significance Engine
"""

from goat.edge_discovery.significance import StatisticalSignificanceEngine


def test_statistical_significance_engine():
    engine = StatisticalSignificanceEngine(bootstrap_resamples=200)

    # Positive return series with strong statistical signal
    positive_returns = [0.005, 0.004, 0.006, 0.003, 0.005, 0.007, 0.002, 0.004, 0.005, 0.006] * 5

    res = engine.evaluate_significance(positive_returns)

    assert "p_value" in res
    assert "confidence_interval_low" in res
    assert "confidence_interval_high" in res
    assert "effect_size" in res
    assert "standard_error" in res
    assert "statistical_power" in res
    assert "monte_carlo_score" in res

    assert res["p_value"] < 0.05
    assert res["confidence_interval_low"] > 0.0
    assert res["effect_size"] > 0.0
    assert res["statistical_power"] > 0.5
