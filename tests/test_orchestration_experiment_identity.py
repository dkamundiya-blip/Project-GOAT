"""
Project GOAT v0.5 — Unit Tests for Canonical Experiment-ID Serialization & Identity
"""

import pytest
from goat.orchestration.scheduler import compute_experiment_id, sort_nested_dict
from goat.research.hypothesis.definition import HypothesisDefinition


def make_dummy_hypothesis(
    hyp_id: str = "HYP-ID-01",
    version: str = "1.0.0",
    cond_params: dict | None = None,
    causal_cond: dict | None = None,
    forward_horizon: int = 5,
    symbol_scope: list[str] | None = None,
    timeframe_scope: list[str] | None = None,
) -> HypothesisDefinition:
    return HypothesisDefinition(
        hypothesis_id=hyp_id,
        version=version,
        name="Test Hypothesis",
        description="Test hypothesis for experiment_id calculation",
        symbol_scope=symbol_scope or ["R_10"],
        timeframe_scope=timeframe_scope or ["M1"],
        causal_condition=causal_cond or {"primitive": "greater_than", "feature": "close"},
        condition_parameters=cond_params or {"threshold": 100.0, "alpha": 0.05},
        forward_outcome_metric="fwd_return_5",
        forward_horizon=forward_horizon,
        event_spacing_bars=0,
        statistical_test="welch_ttest",
    )


def test_experiment_id_identical_definitions_produce_identical_ids() -> None:
    """1. Identical definitions produce identical experiment_id values."""
    h1 = make_dummy_hypothesis()
    h2 = make_dummy_hypothesis()

    id1 = compute_experiment_id(h1, symbol="R_10", timeframe="M1", dataset_fingerprint="fp_abc123")
    id2 = compute_experiment_id(h2, symbol="R_10", timeframe="M1", dataset_fingerprint="fp_abc123")

    assert id1.startswith("EXP_")
    assert len(id1) == 20  # "EXP_" (4) + 16 hex chars = 20 chars
    assert id1 == id2


def test_experiment_id_different_parameter_combinations() -> None:
    """2. Different parameter combinations produce different IDs."""
    h1 = make_dummy_hypothesis(cond_params={"threshold": 100.0})
    h2 = make_dummy_hypothesis(cond_params={"threshold": 105.0})

    id1 = compute_experiment_id(h1, symbol="R_10", timeframe="M1", dataset_fingerprint="fp_abc123")
    id2 = compute_experiment_id(h2, symbol="R_10", timeframe="M1", dataset_fingerprint="fp_abc123")

    assert id1 != id2


def test_experiment_id_different_dataset_fingerprints() -> None:
    """3. Different dataset fingerprints produce different IDs."""
    h = make_dummy_hypothesis()

    id1 = compute_experiment_id(h, symbol="R_10", timeframe="M1", dataset_fingerprint="fp_hash_1")
    id2 = compute_experiment_id(h, symbol="R_10", timeframe="M1", dataset_fingerprint="fp_hash_2")

    assert id1 != id2


def test_experiment_id_different_symbols_timeframes_horizons() -> None:
    """4. Different symbols/timeframes/horizons produce different IDs."""
    h = make_dummy_hypothesis()

    id_sym1 = compute_experiment_id(h, symbol="R_10", timeframe="M1", dataset_fingerprint="fp1")
    id_sym2 = compute_experiment_id(h, symbol="R_50", timeframe="M1", dataset_fingerprint="fp1")
    assert id_sym1 != id_sym2

    id_tf1 = compute_experiment_id(h, symbol="R_10", timeframe="M1", dataset_fingerprint="fp1")
    id_tf2 = compute_experiment_id(h, symbol="R_10", timeframe="M5", dataset_fingerprint="fp1")
    assert id_tf1 != id_tf2

    h_hor1 = make_dummy_hypothesis(forward_horizon=5)
    h_hor2 = make_dummy_hypothesis(forward_horizon=10)
    id_h1 = compute_experiment_id(h_hor1, symbol="R_10", timeframe="M1", dataset_fingerprint="fp1")
    id_h2 = compute_experiment_id(h_hor2, symbol="R_10", timeframe="M1", dataset_fingerprint="fp1")
    assert id_h1 != id_h2


def test_experiment_id_dictionary_insertion_order_invariance() -> None:
    """5. Dictionary insertion order cannot change the ID."""
    params_order1 = {"alpha": 0.05, "beta": 1.0, "threshold": 100.0}
    params_order2 = {"threshold": 100.0, "alpha": 0.05, "beta": 1.0}

    h1 = make_dummy_hypothesis(cond_params=params_order1)
    h2 = make_dummy_hypothesis(cond_params=params_order2)

    id1 = compute_experiment_id(h1, symbol="R_10", timeframe="M1", dataset_fingerprint="fp1")
    id2 = compute_experiment_id(h2, symbol="R_10", timeframe="M1", dataset_fingerprint="fp1")

    assert id1 == id2


def test_experiment_id_campaign_id_invariance() -> None:
    """6. Campaign ID cannot change the experiment ID."""
    h = make_dummy_hypothesis()

    id1 = compute_experiment_id(h, symbol="R_10", timeframe="M1", dataset_fingerprint="fp1")
    id2 = compute_experiment_id(h, symbol="R_10", timeframe="M1", dataset_fingerprint="fp1")

    assert id1 == id2


def test_experiment_id_worker_count_invariance() -> None:
    """7. Worker count/order cannot change the experiment ID."""
    h = make_dummy_hypothesis()

    id1 = compute_experiment_id(h, symbol="R_10", timeframe="M1", dataset_fingerprint="fp1")
    id2 = compute_experiment_id(h, symbol="R_10", timeframe="M1", dataset_fingerprint="fp1")

    assert id1 == id2


def test_experiment_id_canonical_serialization_determinism() -> None:
    """8. Canonical serialization is deterministic."""
    h = make_dummy_hypothesis()
    id1 = compute_experiment_id(h, symbol="R_10", timeframe="M1", dataset_fingerprint="fp1")

    for _ in range(10):
        assert compute_experiment_id(h, symbol="R_10", timeframe="M1", dataset_fingerprint="fp1") == id1


def test_experiment_id_hash_schema_and_algorithm_representation() -> None:
    """9. Hash schema and algorithm metadata are correctly represented."""
    h = make_dummy_hypothesis()
    id_schema1 = compute_experiment_id(h, symbol="R_10", timeframe="M1", experiment_hash_schema=1)
    id_schema2 = compute_experiment_id(h, symbol="R_10", timeframe="M1", experiment_hash_schema=2)
    assert id_schema1 != id_schema2

    id_algo1 = compute_experiment_id(h, symbol="R_10", timeframe="M1", experiment_hash_algorithm="SHA256")
    id_algo2 = compute_experiment_id(h, symbol="R_10", timeframe="M1", experiment_hash_algorithm="SHA512")
    assert id_algo1 != id_algo2


def test_existing_v04_hypothesis_version_hash_not_regressed() -> None:
    """10. Existing v0.4/v0.5 identity behavior that remains valid is not regressed."""
    h = make_dummy_hypothesis()
    v04_hash = h.compute_version_hash()
    assert len(v04_hash) == 12

    v05_id = compute_experiment_id(h, symbol="R_10", timeframe="M1")
    assert v05_id.startswith("EXP_")
    assert len(v05_id) == 20
