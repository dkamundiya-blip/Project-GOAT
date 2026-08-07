"""
Project GOAT Phase 6 — Unit Tests for Hypothesis Engine
"""

from goat.edge_discovery.hypothesis import HypothesisEngine
from goat.edge_discovery.models import HypothesisCondition, HypothesisOperator, HypothesisPrediction, HypothesisStatus


def test_hypothesis_engine():
    engine = HypothesisEngine(author="QUANT_TEST")
    conds = [
        HypothesisCondition(feature_name="trend_strength", operator=HypothesisOperator.GT, threshold_value=0.6),
        HypothesisCondition(feature_name="z_score", operator=HypothesisOperator.BETWEEN, threshold_value=-2.0, secondary_value=2.0),
    ]
    pred = HypothesisPrediction(target_feature="future_return", horizon_bars=5, min_return=0.002)

    hyp = engine.create_hypothesis("Test hyp", conds, pred)

    assert hyp.hypothesis_id.startswith("HYP_")
    assert hyp.author == "QUANT_TEST"
    assert hyp.status == HypothesisStatus.DRAFT
    assert len(hyp.conditions) == 2

    # Test condition evaluation
    assert conds[0].evaluate(0.7) is True
    assert conds[0].evaluate(0.5) is False
    assert conds[1].evaluate(0.0) is True
    assert conds[1].evaluate(3.0) is False
