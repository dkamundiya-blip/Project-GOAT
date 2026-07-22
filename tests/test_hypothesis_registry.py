"""
Project GOAT v0.4 — Unit Tests for EdgeRegistry Persistence & History Preservation
"""

from goat.research.hypothesis.definition import HypothesisDefinition
from goat.research.hypothesis.registry import EdgeRegistry
from goat.research.hypothesis.result import HypothesisResult


def test_edge_registry_history_preservation(tmp_path) -> None:
    """Test registering hypothesis, recording results, and append-only history."""
    reg_file = tmp_path / "edge_registry.json"
    registry = EdgeRegistry(reg_file)

    hyp = HypothesisDefinition(
        hypothesis_id="HYP-REG-TEST",
        version="1.0.0",
        name="Registry Test",
        description="Desc",
        causal_condition={"primitive": "greater_than", "feature": "close"},
    )

    registry.register_hypothesis(hyp, status="EXPLORATORY")

    res1 = HypothesisResult(
        hypothesis_id="HYP-REG-TEST",
        version="1.0.0",
        dataset_fingerprint="fp1",
        partition="train",
        symbol="R_10",
        timeframe="M1",
        conditional_sample_count=100,
        baseline_sample_count=100,
    )
    registry.record_evaluation_result(res1, new_status="TRAIN_SUPPORTED")

    res2 = HypothesisResult(
        hypothesis_id="HYP-REG-TEST",
        version="1.0.0",
        dataset_fingerprint="fp1",
        partition="validation",
        symbol="R_10",
        timeframe="M1",
        conditional_sample_count=100,
        baseline_sample_count=100,
    )
    registry.record_evaluation_result(res2, new_status="VALIDATION_SUPPORTED")

    # Reload from disk
    registry_reloaded = EdgeRegistry(reg_file)
    entry = registry_reloaded.get_entry("HYP-REG-TEST", "1.0.0")

    assert entry is not None
    assert entry.status == "VALIDATION_SUPPORTED"
    # History preserved append-only
    assert len(entry.evaluation_history) == 2
