"""
Project GOAT Phase 6 — Unit Tests for Market Regime Validator
"""

from goat.edge_discovery.hypothesis import HypothesisEngine
from goat.edge_discovery.models import HypothesisCondition, HypothesisOperator, HypothesisPrediction
from goat.edge_discovery.regime import MarketRegimeValidator
from goat.feature_engineering.models import FeatureVector, compute_feature_vector_id


def test_market_regime_validator():
    hyp_engine = HypothesisEngine()
    conds = [HypothesisCondition(feature_name="trend_strength", operator=HypothesisOperator.GT, threshold_value=0.5)]
    pred = HypothesisPrediction()
    hyp = hyp_engine.create_hypothesis("Regime Test", conds, pred)

    validator = MarketRegimeValidator()

    fvs = []
    returns = []
    for i in range(1, 11):
        ts = f"2026-08-07T12:00:{i:02d}Z"
        trend_dir = 1.0 if i <= 5 else -1.0
        features = {"trend_strength": 0.8, "trend_direction": trend_dir, "volatility_regime": 0.5}

        v_id, c_hash = compute_feature_vector_id("VOLATILITY_100", "1m", ts, features)
        fv = FeatureVector(
            vector_id=v_id,
            symbol="VOLATILITY_100",
            timeframe="1m",
            timestamp=ts,
            version="5.0.0",
            features=features,
            checksum="CHK",
            metadata={},
            canonical_hash=c_hash,
        )
        fvs.append(fv)
        returns.append(0.005)

    regime_results = validator.evaluate_regimes(hyp, fvs, returns)

    assert "BULL_TREND" in regime_results
    assert "BEAR_TREND" in regime_results
    assert regime_results["BULL_TREND"]["sample_size"] == 5.0
    assert regime_results["BEAR_TREND"]["sample_size"] == 5.0
