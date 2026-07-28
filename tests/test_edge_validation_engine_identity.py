"""
Project GOAT v0.6 — Engine Identity Locking Unit Tests

Verifies strict identity chain locking across all pipeline stages.
"""

from __future__ import annotations

import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.engine import MultiStageValidationEngine
from goat.research.edge.validation.exceptions import StageValidationError


def test_engine_rejects_edge_id_mismatch():
    engine = MultiStageValidationEngine()
    edge = CandidateEdge(
        proposition_name="Edge A",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1")
    run = ValidationRunInfo(
        edge_id="EDGE_MISMATCHED9999",
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    with pytest.raises(StageValidationError) as excinfo:
        engine.execute_preconfirmatory(
            candidate_edge=edge,
            hypothesis_version="1234567890ab",
            policy=policy,
            validation_run=run,
            dataset_partitions={},
        )
    assert "edge_id" in str(excinfo.value)


def test_engine_rejects_policy_hash_mismatch():
    engine = MultiStageValidationEngine()
    edge = CandidateEdge(
        proposition_name="Edge A",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash="PLC_MISMATCHED999",
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    with pytest.raises(StageValidationError) as excinfo:
        engine.execute_preconfirmatory(
            candidate_edge=edge,
            hypothesis_version="1234567890ab",
            policy=policy,
            validation_run=run,
            dataset_partitions={},
        )
    assert "policy_hash" in str(excinfo.value)
