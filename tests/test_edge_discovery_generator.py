"""
Project GOAT Phase 6 — Unit Tests for Feature Combination Generator
"""

from goat.edge_discovery.generator import FeatureCombinationGenerator


def test_feature_combination_generator():
    generator = FeatureCombinationGenerator(max_combinations=20)
    features = ["trend_strength", "z_score", "roc", "volatility_expansion"]
    thresholds = {
        "trend_strength": [0.5, 0.8],
        "z_score": [1.0],
        "roc": [0.01],
        "volatility_expansion": [1.5],
    }

    candidates = generator.generate_candidate_hypotheses(
        available_features=features,
        feature_thresholds=thresholds,
        min_combination_size=1,
        max_combination_size=2,
    )

    assert len(candidates) > 0
    assert len(candidates) <= 20
    for cand in candidates:
        assert cand.hypothesis_id.startswith("HYP_")
        assert len(cand.conditions) in (1, 2)
