"""
Project GOAT v0.4 — Unit Tests for Hypothesis Definition & Versioning
"""

from goat.research.hypothesis.definition import HypothesisDefinition


def test_hypothesis_definition_hash_versioning() -> None:
    """Test deterministic hash versioning when parameters change."""
    hyp1 = HypothesisDefinition(
        hypothesis_id="HYP-VOL-COMPRESS",
        version="1.0.0",
        name="Volatility Compression",
        description="Test compression",
        causal_condition={"primitive": "less_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
    )

    hyp1_same = HypothesisDefinition(
        hypothesis_id="HYP-VOL-COMPRESS",
        version="1.0.0",
        name="Volatility Compression",
        description="Test compression",
        causal_condition={"primitive": "less_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
    )

    hyp2_diff = HypothesisDefinition(
        hypothesis_id="HYP-VOL-COMPRESS",
        version="1.0.0",
        name="Volatility Compression",
        description="Test compression",
        causal_condition={"primitive": "less_than", "feature": "close"},
        condition_parameters={"threshold": 105.0},  # Threshold changed!
    )

    # Same parameters -> same hash
    assert hyp1.compute_version_hash() == hyp1_same.compute_version_hash()

    # Different parameters -> different hash
    assert hyp1.compute_version_hash() != hyp2_diff.compute_version_hash()


def test_hypothesis_definition_freeze() -> None:
    """Test freezing hypothesis parameters."""
    hyp = HypothesisDefinition(
        hypothesis_id="HYP-RANGE",
        version="1.0.0",
        name="Range test",
        description="Desc",
        causal_condition={"primitive": "greater_than", "feature": "close"},
    )
    assert hyp.is_frozen is False

    frozen = hyp.freeze()
    assert frozen.is_frozen is True
