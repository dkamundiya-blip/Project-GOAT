"""
Project GOAT v0.6 — Edge Persistence Repository Tests

Verifies CRUD and query operations for all Edge Registry domain entities.
"""

from __future__ import annotations

import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.enums import EdgeScope, EvidenceDimensionType
from goat.research.edge.evidence import AtomicEvidenceRecord
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import (
    RecordNotFoundError,
    SQLiteEdgeRepository,
)
from goat.research.edge.policy import ValidationPolicy


def test_candidate_edge_crud():
    """Verify CandidateEdge can be saved, retrieved, and metadata updated cleanly."""
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Vol Breakout",
        causal_primitive="quantile_membership",
        target_feature="relative_range",
        economic_rationale_category="volatility",
        base_condition_spec={"lookback": 50},
        description="Initial description",
    )

    saved = repo.save_candidate_edge(edge)
    assert saved.edge_id == edge.edge_id

    fetched = repo.get_candidate_edge(edge.edge_id)
    assert fetched.edge_id == edge.edge_id
    assert fetched.proposition_name == "Vol Breakout"
    assert fetched.base_condition_spec["lookback"] == 50

    # Metadata update on existing edge_id
    edge_updated = CandidateEdge(
        proposition_name="Vol Breakout Updated",
        causal_primitive="quantile_membership",
        target_feature="relative_range",
        economic_rationale_category="volatility",
        base_condition_spec={"lookback": 50},
        description="Updated description",
    )
    repo.save_candidate_edge(edge_updated)
    fetched_updated = repo.get_candidate_edge(edge.edge_id)
    assert fetched_updated.proposition_name == "Vol Breakout Updated"
    assert fetched_updated.description == "Updated description"


def test_hypothesis_version_crud():
    """Verify hypothesis version persistence and retrieval."""
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Edge 1",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 14},
    )
    repo.save_candidate_edge(edge)

    version_hash = repo.save_hypothesis_version(
        edge_id=edge.edge_id,
        condition_parameters={"period": 14},
        forward_outcome_metric="fwd_return_5",
        forward_horizon=5,
    )
    assert len(version_hash) == 12

    fetched = repo.get_hypothesis_version(version_hash)
    assert fetched["edge_id"] == edge.edge_id
    assert fetched["forward_horizon"] == 5
    assert fetched["condition_parameters"]["period"] == 14


def test_validation_policy_crud():
    """Verify ValidationPolicy persistence and retrieval by policy_hash."""
    repo = SQLiteEdgeRepository(":memory:")
    policy = ValidationPolicy(
        policy_id="POL_PROV",
        version="1.0.0",
        description="Default Policy",
        stage_a_alpha=0.05,
    )

    saved = repo.save_validation_policy(policy)
    assert saved.policy_hash == policy.policy_hash

    fetched = repo.get_validation_policy(policy.policy_hash)
    assert fetched.policy_hash == policy.policy_hash
    assert fetched.stage_a_alpha == 0.05


def test_validation_run_crud_and_multiple_runs_for_same_edge():
    """Verify multiple validation runs for the same edge can be saved independently."""
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Edge 1",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 14},
    )
    repo.save_candidate_edge(edge)

    pol1 = ValidationPolicy(policy_id="P1", stage_a_alpha=0.05)
    pol2 = ValidationPolicy(policy_id="P2", stage_a_alpha=0.01)
    repo.save_validation_policy(pol1)
    repo.save_validation_policy(pol2)

    run1 = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=pol1.policy_hash,
        dataset_fingerprint="fp_train_1",
        candidate_target_scope=EdgeScope.UNIVERSAL,
    )
    run2 = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=pol2.policy_hash,
        dataset_fingerprint="fp_train_2",
        candidate_target_scope=EdgeScope.REGIME_SPECIFIC,
    )

    repo.save_validation_run(run1)
    repo.save_validation_run(run2)

    f1 = repo.get_validation_run(run1.validation_run_id)
    f2 = repo.get_validation_run(run2.validation_run_id)

    assert f1.validation_run_id != f2.validation_run_id
    assert f1.edge_id == edge.edge_id
    assert f2.edge_id == edge.edge_id


def test_atomic_evidence_crud_and_listing():
    """Verify atomic evidence creation, retrieval, and run listing."""
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Edge 1",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 14},
    )
    repo.save_candidate_edge(edge)
    pol = repo.save_validation_policy(ValidationPolicy(policy_id="P1"))
    run = repo.save_validation_run(
        ValidationRunInfo(
            edge_id=edge.edge_id,
            policy_hash=pol.policy_hash,
            dataset_fingerprint="fp_1",
            candidate_target_scope=EdgeScope.UNIVERSAL,
        )
    )

    ev1 = AtomicEvidenceRecord(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        dimension_type=EvidenceDimensionType.DISCOVERY,
        dimension_key="disc_1",
        partition_identity="train",
        sample_count=100,
        effect_size=0.25,
        raw_p_value=0.01,
    )

    ev2 = AtomicEvidenceRecord(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        dimension_type=EvidenceDimensionType.WALK_FORWARD_FOLD,
        dimension_key="fold_1",
        partition_identity="validation",
        sample_count=80,
        effect_size=0.30,
        raw_p_value=0.005,
    )

    repo.save_evidence(ev1)
    repo.save_evidence(ev2)

    evidence_list = repo.list_evidence_for_run(run.validation_run_id)
    assert len(evidence_list) == 2
    assert sorted([e.evidence_id for e in evidence_list]) == sorted([ev1.evidence_id, ev2.evidence_id])


def test_confirmatory_audit_crud():
    """Verify ConfirmatoryAudit metadata persistence and lookup."""
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Edge 1",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 14},
    )
    repo.save_candidate_edge(edge)
    pol = repo.save_validation_policy(ValidationPolicy(policy_id="P1"))
    run = repo.save_validation_run(
        ValidationRunInfo(
            edge_id=edge.edge_id,
            policy_hash=pol.policy_hash,
            dataset_fingerprint="fp_1",
            candidate_target_scope=EdgeScope.UNIVERSAL,
        )
    )

    audit_id = repo.save_confirmatory_audit(
        validation_run_id=run.validation_run_id,
        frozen_hypothesis_version="1234567890ab",
        dataset_fingerprint="fp_holdout",
        policy_hash=pol.policy_hash,
    )

    fetched = repo.get_confirmatory_audit(audit_id)
    assert fetched["audit_id"] == audit_id
    assert fetched["validation_run_id"] == run.validation_run_id
    assert fetched["holdout_partition_identity"] == "holdout_sealed_v1"


def test_record_not_found_raises():
    """Verify accessing nonexistent records raises RecordNotFoundError."""
    repo = SQLiteEdgeRepository(":memory:")

    with pytest.raises(RecordNotFoundError):
        repo.get_candidate_edge("EDGE_NONEXISTENT")

    with pytest.raises(RecordNotFoundError):
        repo.get_hypothesis_version("nonexistent")

    with pytest.raises(RecordNotFoundError):
        repo.get_validation_policy("PLC_NONEXISTENT")

    with pytest.raises(RecordNotFoundError):
        repo.get_validation_run("VAL_NONEXISTENT")

    with pytest.raises(RecordNotFoundError):
        repo.get_evidence("EVD_NONEXISTENT")

    with pytest.raises(RecordNotFoundError):
        repo.get_confirmatory_audit("AUD_NONEXISTENT")
