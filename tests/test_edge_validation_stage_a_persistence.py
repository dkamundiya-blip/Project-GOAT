"""
Project GOAT v0.6 — Stage A Persistence Integration Unit Tests
"""

import numpy as np
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.evidence import AtomicEvidenceRecord
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import EvidenceConflictError, SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.stages.stage_a import StageAValidator


def test_stage_a_evidence_persistence_and_replay():
    repo = SQLiteEdgeRepository(":memory:")
    validator = StageAValidator()

    edge = CandidateEdge(
        proposition_name="Persistence Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    repo.save_candidate_edge(edge)

    policy = ValidationPolicy(
        policy_id="P1", stage_a_min_sample=100, stage_a_effect_min=0.15, stage_a_alpha=0.05
    )
    repo.save_validation_policy(policy)

    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )
    repo.save_validation_run(run)

    rng = np.random.default_rng(42)
    cond = rng.normal(loc=0.5, scale=1.0, size=150)
    base = rng.normal(loc=0.0, scale=1.0, size=150)

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        cond_arr=cond,
        base_arr=base,
    )

    ev_id = res.evidence_ids[0]

    # Re-evaluating identically produce identical evidence ID and EVP hash
    res_replay = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        cond_arr=cond,
        base_arr=base,
    )
    assert res_replay.evidence_ids[0] == ev_id
