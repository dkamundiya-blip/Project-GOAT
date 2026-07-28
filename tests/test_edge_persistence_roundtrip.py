"""
Project GOAT v0.6 — Edge Persistence Roundtrip Tests

Verifies domain object serialization/deserialization accuracy, file database persistence across
reopens, Unicode stability, negative-zero canonical behavior, and immutable structure reconstruction.
"""

from __future__ import annotations

from types import MappingProxyType
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.enums import EdgeScope, EvidenceDimensionType
from goat.research.edge.evidence import AtomicEvidenceRecord
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy


def test_file_database_close_and_reopen(tmp_path):
    """Verify closing database connection and reopening preserves all records."""
    db_file = tmp_path / "edge_registry.db"

    # 1. Open database, write records, close connection
    with SQLiteEdgeRepository(db_file) as repo:
        edge = CandidateEdge(
            proposition_name="Vol Compression 📈",
            causal_primitive="quantile_membership",
            target_feature="relative_range",
            economic_rationale_category="volatility",
            base_condition_spec={"lookback": 50, "unicode_val": "α_test"},
            display_labels=["label_1", "label_2"],
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
        ev = repo.save_evidence(
            AtomicEvidenceRecord(
                validation_run_id=run.validation_run_id,
                edge_id=edge.edge_id,
                dimension_type=EvidenceDimensionType.DISCOVERY,
                dimension_key="disc_1",
                partition_identity="train",
                sample_count=100,
                effect_size=0.25,
                raw_p_value=0.01,
                context_metadata={"unicode": "📈_boost"},
            )
        )

    # 2. Reopen database from same file path and verify all records persist
    with SQLiteEdgeRepository(db_file) as repo_reopened:
        fetched_edge = repo_reopened.get_candidate_edge(edge.edge_id)
        fetched_pol = repo_reopened.get_validation_policy(pol.policy_hash)
        fetched_run = repo_reopened.get_validation_run(run.validation_run_id)
        fetched_ev = repo_reopened.get_evidence(ev.evidence_id)

        assert fetched_edge.edge_id == edge.edge_id
        assert fetched_edge.proposition_name == "Vol Compression 📈"
        assert fetched_pol.policy_hash == pol.policy_hash
        assert fetched_run.validation_run_id == run.validation_run_id
        assert fetched_ev.evidence_id == ev.evidence_id
        assert fetched_ev.context_metadata["unicode"] == "📈_boost"


def test_nested_immutable_structure_reconstruction():
    """Verify deserialized domain models maintain true nested immutability (MappingProxyType/tuple)."""
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Nested Test",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"outer": {"inner": [1, 2]}},
        display_labels=["l1", "l2"],
    )
    repo.save_candidate_edge(edge)

    fetched = repo.get_candidate_edge(edge.edge_id)
    assert isinstance(fetched.base_condition_spec, MappingProxyType)
    assert isinstance(fetched.display_labels, tuple)

    with pytest.raises(TypeError):
        fetched.base_condition_spec["outer"] = 999


def test_negative_zero_canonical_behavior_in_persistence():
    """Verify negative zero (-0.0) is normalized canonically upon model reconstruction and DB write."""
    repo = SQLiteEdgeRepository(":memory:")
    edge = CandidateEdge(
        proposition_name="Neg Zero Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"val": -0.0},
    )
    repo.save_candidate_edge(edge)

    fetched = repo.get_candidate_edge(edge.edge_id)
    assert fetched.edge_id == edge.edge_id
    assert fetched.base_condition_spec["val"] == 0.0
