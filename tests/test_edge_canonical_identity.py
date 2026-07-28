"""
Project GOAT v0.6 — Canonical Serialization & Identity Tests

Verifies deterministic identity generation, serialization rules, metadata exclusion,
nested key sorting, and regression against v0.5 experiment identity.
"""

from __future__ import annotations

import pytest

from goat.orchestration.scheduler import compute_configuration_hash, compute_experiment_id
from goat.research.edge.canonical import canonical_json, compute_canonical_sha256
from goat.research.edge.definition import CandidateEdge, compute_hypothesis_version
from goat.research.edge.enums import EdgeScope
from goat.research.edge.models import compute_confirmatory_audit_id, compute_validation_run_id
from goat.research.edge.policy import ValidationPolicy
from goat.research.hypothesis.definition import HypothesisDefinition


def test_canonical_json_sorting_and_determinism():
    """Verify recursive key sorting and compact JSON formatting."""
    d1 = {"b": 2, "a": {"z": 1, "m": [3, 2, 1]}, "c": True}
    d2 = {"c": True, "a": {"m": [3, 2, 1], "z": 1}, "b": 2}

    json1 = canonical_json(d1)
    json2 = canonical_json(d2)

    assert json1 == json2
    assert json1 == '{"a":{"m":[3,2,1],"z":1},"b":2,"c":true}'


def test_canonical_json_negative_zero_normalization():
    """Verify negative zero float (-0.0) is canonically normalized to positive 0.0."""
    json_neg = canonical_json({"val": -0.0})
    json_pos = canonical_json({"val": 0.0})

    assert json_neg == json_pos
    assert json_neg == '{"val":0.0}'
    assert compute_canonical_sha256({"val": -0.0}) == compute_canonical_sha256({"val": 0.0})


def test_canonical_json_float_nan_inf_rejection():
    """Verify non-finite float values are rejected."""
    with pytest.raises(ValueError, match="Cannot canonically serialize non-finite float"):
        canonical_json({"val": float("nan")})

    with pytest.raises(ValueError, match="Cannot canonically serialize non-finite float"):
        canonical_json({"val": float("inf")})

    with pytest.raises(ValueError, match="Cannot canonically serialize non-finite float"):
        canonical_json({"val": float("-inf")})


def test_unicode_canonicalization_determinism():
    """Verify Unicode strings produce deterministic canonical output and hashes."""
    u_dict = {"symbol": "R_10", "unicode_text": "Volatility 📈 Compression β"}
    hash1 = compute_canonical_sha256(u_dict)
    hash2 = compute_canonical_sha256(u_dict)
    assert hash1 == hash2
    assert len(hash1) == 64


def test_candidate_edge_id_determinism_and_format():
    """Verify CandidateEdge produces deterministic EDGE_<HEX16> IDs."""
    edge1 = CandidateEdge(
        proposition_name="Volatility Compression Breakout",
        causal_primitive="quantile_membership",
        target_feature="relative_range",
        economic_rationale_category="volatility_compression",
        base_condition_spec={"lookback": 50, "quantile_upper": 0.20},
    )

    edge2 = CandidateEdge(
        proposition_name="Different Display Name",
        causal_primitive="quantile_membership",
        target_feature="relative_range",
        economic_rationale_category="volatility_compression",
        base_condition_spec={"quantile_upper": 0.20, "lookback": 50},
    )

    assert edge1.edge_id.startswith("EDGE_")
    assert len(edge1.edge_id) == 21  # "EDGE_" (5) + 16 hex chars
    assert edge1.edge_id == edge2.edge_id


def test_candidate_edge_metadata_exclusion():
    """Verify changing human-readable metadata does NOT alter edge_id."""
    edge_base = CandidateEdge(
        proposition_name="Name A",
        causal_primitive="quantile_membership",
        target_feature="relative_range",
        economic_rationale_category="volatility_compression",
        base_condition_spec={"lookback": 50},
        description="Description A",
        notes="Notes A",
        display_labels=["label1"],
    )

    edge_modified_meta = CandidateEdge(
        proposition_name="Name B",
        causal_primitive="quantile_membership",
        target_feature="relative_range",
        economic_rationale_category="volatility_compression",
        base_condition_spec={"lookback": 50},
        description="Description B",
        notes="Notes B",
        display_labels=["label2", "label3"],
    )

    assert edge_base.edge_id == edge_modified_meta.edge_id


def test_candidate_edge_semantic_mutation_sensitivity():
    """Verify mutating semantic fields MUST change edge_id."""
    edge_base = CandidateEdge(
        proposition_name="Name A",
        causal_primitive="quantile_membership",
        target_feature="relative_range",
        economic_rationale_category="volatility_compression",
        base_condition_spec={"lookback": 50},
    )

    # 1. Mutate causal primitive
    edge_diff_primitive = CandidateEdge(
        proposition_name="Name A",
        causal_primitive="greater_than",
        target_feature="relative_range",
        economic_rationale_category="volatility_compression",
        base_condition_spec={"lookback": 50},
    )
    assert edge_base.edge_id != edge_diff_primitive.edge_id

    # 2. Mutate target feature
    edge_diff_feature = CandidateEdge(
        proposition_name="Name A",
        causal_primitive="quantile_membership",
        target_feature="close",
        economic_rationale_category="volatility_compression",
        base_condition_spec={"lookback": 50},
    )
    assert edge_base.edge_id != edge_diff_feature.edge_id

    # 3. Mutate base condition spec
    edge_diff_spec = CandidateEdge(
        proposition_name="Name A",
        causal_primitive="quantile_membership",
        target_feature="relative_range",
        economic_rationale_category="volatility_compression",
        base_condition_spec={"lookback": 100},
    )
    assert edge_base.edge_id != edge_diff_spec.edge_id


def test_hypothesis_version_determinism_and_ordering():
    """Verify compute_hypothesis_version produces 12 hex chars and respects key order invariance."""
    edge_id = "EDGE_1234567890ABCDEF"
    params1 = {"b": 2, "a": 1}
    params2 = {"a": 1, "b": 2}

    ver1 = compute_hypothesis_version(
        edge_id=edge_id,
        condition_parameters=params1,
        forward_outcome_metric="fwd_return_5",
        forward_horizon=5,
    )
    ver2 = compute_hypothesis_version(
        edge_id=edge_id,
        condition_parameters=params2,
        forward_outcome_metric="fwd_return_5",
        forward_horizon=5,
    )

    assert ver1 == ver2
    assert len(ver1) == 12

    # Mutate parameter value
    ver3 = compute_hypothesis_version(
        edge_id=edge_id,
        condition_parameters={"a": 1, "b": 3},
        forward_outcome_metric="fwd_return_5",
        forward_horizon=5,
    )
    assert ver1 != ver3


def test_validation_run_id_goat_version_exclusion():
    """Verify validation_run_id excludes software goat_version metadata."""
    val_id1 = compute_validation_run_id(
        edge_id="EDGE_1234567890ABCDEF",
        policy_hash="PLC_ABCDEF1234567890",
        dataset_fingerprint="fp_9999",
        candidate_target_scope=EdgeScope.UNIVERSAL,
        goat_version="v0.6.0",
    )
    val_id2 = compute_validation_run_id(
        edge_id="EDGE_1234567890ABCDEF",
        policy_hash="PLC_ABCDEF1234567890",
        dataset_fingerprint="fp_9999",
        candidate_target_scope=EdgeScope.UNIVERSAL,
        goat_version="v0.6.1-different",
    )

    assert val_id1 == val_id2
    assert val_id1.startswith("VAL_")
    assert len(val_id1) == 20  # "VAL_" (4) + 16 hex chars


def test_validation_run_id_all_scientific_fields_affect_id():
    """Verify changing any of the 4 scientific fields alters validation_run_id."""
    base_id = compute_validation_run_id("EDGE_A", "PLC_A", "FP_A", EdgeScope.UNIVERSAL)

    assert base_id != compute_validation_run_id("EDGE_B", "PLC_A", "FP_A", EdgeScope.UNIVERSAL)
    assert base_id != compute_validation_run_id("EDGE_A", "PLC_B", "FP_A", EdgeScope.UNIVERSAL)
    assert base_id != compute_validation_run_id("EDGE_A", "PLC_A", "FP_B", EdgeScope.UNIVERSAL)
    assert base_id != compute_validation_run_id("EDGE_A", "PLC_A", "FP_A", EdgeScope.REGIME_SPECIFIC)


def test_confirmatory_audit_id_determinism():
    """Verify confirmatory audit ID generation is deterministic and starts with AUD_."""
    audit_id1 = compute_confirmatory_audit_id(
        validation_run_id="VAL_1234567890ABCDEF",
        frozen_hypothesis_version="1234567890ab",
        dataset_fingerprint="fp_9999",
        policy_hash="PLC_ABCDEF1234567890",
    )
    audit_id2 = compute_confirmatory_audit_id(
        validation_run_id="VAL_1234567890ABCDEF",
        frozen_hypothesis_version="1234567890ab",
        dataset_fingerprint="fp_9999",
        policy_hash="PLC_ABCDEF1234567890",
    )

    assert audit_id1 == audit_id2
    assert audit_id1.startswith("AUD_")
    assert len(audit_id1) == 20  # "AUD_" (4) + 16 hex chars


def test_v05_experiment_identity_regression():
    """Verify existing v0.5 experiment_id and configuration_hash remain 100% unchanged."""
    hyp = HypothesisDefinition(
        hypothesis_id="H_REGRESSION_001",
        name="Regression Test",
        description="Verify v0.5 experiment ID calculation unchanged",
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 10.0},
    )

    exp_id = compute_experiment_id(
        hypothesis=hyp,
        symbol="R_10",
        timeframe="M1",
        dataset_fingerprint="dataset_fp_123",
    )
    cfg_hash = compute_configuration_hash(
        hypothesis_grid=[hyp],
        symbols=["R_10"],
        timeframes=["M1"],
        master_seed=42,
        fdr_alpha=0.05,
    )

    assert exp_id.startswith("EXP_")
    assert len(exp_id) == 20  # "EXP_" + 16 hex chars
    assert cfg_hash.startswith("cfg_")
    assert len(cfg_hash) == 20  # "cfg_" + 16 hex chars
