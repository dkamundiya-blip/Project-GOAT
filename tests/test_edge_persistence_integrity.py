"""
Project GOAT v0.6 — Edge Persistence Integrity & Conflict Tests

Verifies foreign key enforcement, transaction rollbacks, idempotency rules,
and conflict detection for atomic evidence and scientific identities.
"""

from __future__ import annotations

import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.enums import EdgeScope, EvidenceDimensionType
from goat.research.edge.evidence import AtomicEvidenceRecord
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import (
    EvidenceConflictError,
    PersistenceIntegrityError,
    SQLiteEdgeRepository,
)
from goat.research.edge.policy import ValidationPolicy


def test_foreign_key_violation_rejected():
    """Verify writing records with nonexistent foreign keys raises PersistenceIntegrityError."""
    repo = SQLiteEdgeRepository(":memory:")

    # ValidationRun referenced nonexistent edge_id and policy_hash
    run = ValidationRunInfo(
        edge_id="EDGE_NONEXISTENT",
        policy_hash="PLC_NONEXISTENT",
        dataset_fingerprint="fp_1",
        candidate_target_scope=EdgeScope.UNIVERSAL,
    )
    with pytest.raises(PersistenceIntegrityError):
        repo.save_validation_run(run)


def test_identical_evidence_is_idempotent():
    """Verify saving duplicate identical atomic evidence is idempotent."""
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

    ev = AtomicEvidenceRecord(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        dimension_type=EvidenceDimensionType.DISCOVERY,
        dimension_key="disc_1",
        partition_identity="train",
        sample_count=100,
        effect_size=0.25,
        raw_p_value=0.01,
    )

    repo.save_evidence(ev)
    # Save identical evidence a second time
    repo.save_evidence(ev)

    evidence_list = repo.list_evidence_for_run(run.validation_run_id)
    assert len(evidence_list) == 1


def test_conflicting_evidence_rejected():
    """Verify saving evidence with existing evidence_id but conflicting payload_hash raises EvidenceConflictError."""
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

    # Same observation target, DIFFERENT quantitative result (conflicting effect size)
    ev_conflict = AtomicEvidenceRecord(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        dimension_type=EvidenceDimensionType.DISCOVERY,
        dimension_key="disc_1",
        partition_identity="train",
        sample_count=100,
        effect_size=0.99,  # Conflicting payload!
        raw_p_value=0.0001,
    )

    assert ev1.evidence_id == ev_conflict.evidence_id
    assert ev1.evidence_payload_hash != ev_conflict.evidence_payload_hash

    repo.save_evidence(ev1)

    with pytest.raises(EvidenceConflictError, match="Append-only evidence conflict"):
        repo.save_evidence(ev_conflict)


def test_transaction_rollback_on_failure():
    """Verify transaction rollback leaves zero partial records when an operation fails."""
    repo = SQLiteEdgeRepository(":memory:")

    with pytest.raises(PersistenceIntegrityError):
        with repo.transaction() as conn:
            # Valid edge insert
            edge = CandidateEdge(
                proposition_name="Edge 1",
                causal_primitive="greater_than",
                target_feature="close",
                economic_rationale_category="momentum",
                base_condition_spec={"period": 14},
            )
            spec_json = '{"period": 14}'
            conn.execute(
                "INSERT INTO candidate_edges (edge_id, edge_schema_version, causal_primitive, target_feature, economic_rationale_category, base_condition_spec_json, proposition_name, description, notes, display_labels_json, hypothesis_ids_json, lifecycle_state, created_at_utc, updated_at_utc) VALUES (?, 1, 'greater_than', 'close', 'momentum', ?, 'Edge 1', '', '', '[]', '[]', 'CANDIDATE', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z');",
                (edge.edge_id, spec_json),
            )
            # Invalid insert that triggers Foreign Key failure
            conn.execute(
                "INSERT INTO validation_runs (validation_run_id, edge_id, policy_hash, dataset_fingerprint, candidate_target_scope, goat_version, created_at_utc) VALUES ('VAL_X', 'EDGE_NONEXISTENT', 'PLC_NONEXISTENT', 'fp', 'UNIVERSAL', 'v0.6.0', '2026-01-01T00:00:00Z');"
            )

    # Verify edge was rolled back and NOT persisted
    with pytest.raises(Exception):
        repo.get_candidate_edge(edge.edge_id)


def test_different_datasets_never_overwrite_evidence():
    """Verify evaluation under different dataset fingerprints creates distinct validation runs and evidence."""
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

    run_dataset_a = repo.save_validation_run(
        ValidationRunInfo(
            edge_id=edge.edge_id,
            policy_hash=pol.policy_hash,
            dataset_fingerprint="fp_dataset_2020",
            candidate_target_scope=EdgeScope.UNIVERSAL,
        )
    )

    run_dataset_b = repo.save_validation_run(
        ValidationRunInfo(
            edge_id=edge.edge_id,
            policy_hash=pol.policy_hash,
            dataset_fingerprint="fp_dataset_2025",
            candidate_target_scope=EdgeScope.UNIVERSAL,
        )
    )

    ev_a = repo.save_evidence(
        AtomicEvidenceRecord(
            validation_run_id=run_dataset_a.validation_run_id,
            edge_id=edge.edge_id,
            dimension_type=EvidenceDimensionType.DISCOVERY,
            dimension_key="disc_1",
            partition_identity="train",
            sample_count=100,
            effect_size=0.20,
            raw_p_value=0.02,
        )
    )

    ev_b = repo.save_evidence(
        AtomicEvidenceRecord(
            validation_run_id=run_dataset_b.validation_run_id,
            edge_id=edge.edge_id,
            dimension_type=EvidenceDimensionType.DISCOVERY,
            dimension_key="disc_1",
            partition_identity="train",
            sample_count=200,
            effect_size=0.40,
            raw_p_value=0.001,
        )
    )

    assert run_dataset_a.validation_run_id != run_dataset_b.validation_run_id
    assert ev_a.evidence_id != ev_b.evidence_id
    assert len(repo.list_evidence_for_run(run_dataset_a.validation_run_id)) == 1
    assert len(repo.list_evidence_for_run(run_dataset_b.validation_run_id)) == 1
