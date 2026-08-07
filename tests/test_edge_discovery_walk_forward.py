"""
Project GOAT Phase 6 — Unit Tests for Walk-Forward Validator
"""

from goat.edge_discovery.hypothesis import HypothesisEngine
from goat.edge_discovery.models import HypothesisCondition, HypothesisOperator, HypothesisPrediction
from goat.edge_discovery.walk_forward import WalkForwardValidator
from goat.feature_engineering.models import FeatureVector, compute_feature_vector_id


def test_walk_forward_validator():
    hyp_engine = HypothesisEngine()
    conds = [HypothesisCondition(feature_name="trend_strength", operator=HypothesisOperator.GT, threshold_value=0.5)]
    pred = HypothesisPrediction()
    hyp = hyp_engine.create_hypothesis("WF Test", conds, pred)

    validator = WalkForwardValidator(train_ratio=0.5, val_ratio=0.25)

    fvs = []
    returns = []
    for i in range(1, 41):
        ts = f"2026-08-07T12:{i:02d}:00Z"
        v_id, c_hash = compute_feature_vector_id("VOLATILITY_100", "1m", ts, {"trend_strength": 0.8})
        fv = FeatureVector(
            vector_id=v_id,
            symbol="VOLATILITY_100",
            timeframe="1m",
            timestamp=ts,
            version="5.0.0",
            features={"trend_strength": 0.8},
            checksum="CHK",
            metadata={},
            canonical_hash=c_hash,
        )
        fvs.append(fv)
        returns.append(0.004)

    wf_res = validator.validate_walk_forward(hyp, fvs, returns)

    assert "train_sharpe" in wf_res
    assert "val_sharpe" in wf_res
    assert "oos_sharpe" in wf_res
    assert "degradation_ratio" in wf_res
    assert "passed_oos" in wf_res

    assert wf_res["passed_oos"] == 1.0
