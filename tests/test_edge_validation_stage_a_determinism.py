"""
Project GOAT v0.6 — Stage A Determinism & Input Order Invariance Unit Tests
"""

import numpy as np
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.stages.stage_a import StageAValidator


def test_stage_a_cross_process_determinism():
    validator = StageAValidator()

    edge = CandidateEdge(
        proposition_name="Determinism Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    policy = ValidationPolicy(
        policy_id="P1", stage_a_min_sample=100, stage_a_effect_min=0.15, stage_a_alpha=0.05
    )
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    rng1 = np.random.default_rng(100)
    cond1 = rng1.normal(loc=0.4, scale=1.0, size=120)
    base1 = rng1.normal(loc=0.0, scale=1.0, size=120)

    res1 = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="123",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        cond_arr=cond1,
        base_arr=base1,
    )

    rng2 = np.random.default_rng(100)
    cond2 = rng2.normal(loc=0.4, scale=1.0, size=120)
    base2 = rng2.normal(loc=0.0, scale=1.0, size=120)

    res2 = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="123",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        cond_arr=cond2,
        base_arr=base2,
    )

    assert res1.decision == res2.decision
    assert res1.reason_code == res2.reason_code
    assert res1.evidence_ids == res2.evidence_ids
