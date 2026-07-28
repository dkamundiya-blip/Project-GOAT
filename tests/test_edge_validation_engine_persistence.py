"""
Project GOAT v0.6 — Engine Persistence & Recovery Unit Tests

Verifies SQLite repository integration, durable entity persistence, and process recovery.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.engine import MultiStageValidationEngine


def test_engine_persists_entities_to_repository():
    repo = SQLiteEdgeRepository(":memory:")
    engine = MultiStageValidationEngine(repository=repo)

    edge = CandidateEdge(
        proposition_name="Persisted Engine Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1_PERSIST")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp_persist",
        candidate_target_scope="UNIVERSAL",
    )

    np.random.seed(42)
    cond = np.random.normal(0.35, 0.5, 150)
    base = np.random.normal(0.0, 0.5, 150)
    partitions = {
        "train": pd.DataFrame({"conditional_outcome": cond, "baseline_outcome": base}),
    }

    engine.execute_preconfirmatory(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions=partitions,
        baseline_effect=0.30,
    )

    # Verify repository saved edge, policy, and run
    fetched_edge = repo.get_candidate_edge(edge.edge_id)
    assert fetched_edge.edge_id == edge.edge_id

    fetched_policy = repo.get_validation_policy(policy.policy_hash)
    assert fetched_policy.policy_hash == policy.policy_hash

    fetched_run = repo.get_validation_run(run.validation_run_id)
    assert fetched_run.validation_run_id == run.validation_run_id
