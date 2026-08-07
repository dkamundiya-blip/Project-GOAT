"""
Project GOAT Phase 6 — Unit Tests for Historical Evaluation Engine
"""

from goat.edge_discovery.evaluator import HistoricalEvaluationEngine
from goat.edge_discovery.hypothesis import HypothesisEngine
from goat.edge_discovery.models import HypothesisCondition, HypothesisOperator, HypothesisPrediction
from goat.feature_engineering.models import FeatureVector, compute_feature_vector_id


def test_historical_evaluation_engine():
    hyp_engine = HypothesisEngine()
    conds = [
        HypothesisCondition(feature_name="trend_strength", operator=HypothesisOperator.GT, threshold_value=0.5),
    ]
    pred = HypothesisPrediction(target_feature="future_return", horizon_bars=5, min_return=0.001, direction=1.0)
    hyp = hyp_engine.create_hypothesis("Test", conds, pred)

    evaluator = HistoricalEvaluationEngine()

    fvs = []
    returns = []
    for i in range(1, 21):
        ts = f"2026-08-07T12:00:{i:02d}Z"
        feat_val = 0.8 if i % 2 == 0 else 0.2  # 10 matched, 10 unmatched
        ret = 0.005 if i % 2 == 0 else -0.003

        v_id, c_hash = compute_feature_vector_id("VOLATILITY_100", "1m", ts, {"trend_strength": feat_val})
        fv = FeatureVector(
            vector_id=v_id,
            symbol="VOLATILITY_100",
            timeframe="1m",
            timestamp=ts,
            version="5.0.0",
            features={"trend_strength": feat_val},
            checksum="CHK",
            metadata={},
            canonical_hash=c_hash,
        )
        fvs.append(fv)
        returns.append(ret)

    metrics = evaluator.evaluate_hypothesis(hyp, fvs, returns)

    assert metrics.sample_size == 10
    assert metrics.win_rate == 1.0
    assert metrics.expected_value == 0.005
    assert metrics.profit_factor > 1.0
    assert metrics.sharpe_ratio > 0.0
