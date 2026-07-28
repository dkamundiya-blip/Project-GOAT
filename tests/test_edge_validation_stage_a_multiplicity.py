"""
Project GOAT v0.6 — Stage A Multiplicity Safety Unit Tests
"""

import numpy as np
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.models import ReasonCode, StageDecision
from goat.research.edge.validation.multiplicity import MultiplicityFamilyCoordinator
from goat.research.edge.validation.stages.stage_a import StageAValidator


def test_stage_a_raw_p_significant_but_q_not_significant_fails():
    """MANDATORY TEST: Raw p <= alpha, but FDR adjusted q > alpha MUST produce FAIL decision."""
    validator = StageAValidator()

    edge1 = CandidateEdge(
        proposition_name="Edge 1",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    edge2 = CandidateEdge(
        proposition_name="Edge 2",
        causal_primitive="less_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 2},
    )
    edge3 = CandidateEdge(
        proposition_name="Edge 3",
        causal_primitive="crosses_above",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 3},
    )

    policy = ValidationPolicy(
        policy_id="P1", stage_a_min_sample=100, stage_a_effect_min=0.10, stage_a_alpha=0.05
    )

    coord = MultiplicityFamilyCoordinator("FAM_TEST", alpha=policy.stage_a_alpha)

    # Register raw p-values:
    # edge1 raw p = 0.04 (<= 0.05). But across M=3 tests with p2=0.40, p3=0.80:
    # FDR adjusted q for edge1: q1 = (3/1) * 0.04 = 0.12 (> 0.05)!
    coord.register_candidate(edge1.edge_id, 0.04)
    coord.register_candidate(edge2.edge_id, 0.40)
    coord.register_candidate(edge3.edge_id, 0.80)
    coord.freeze_family()

    run1 = ValidationRunInfo(
        edge_id=edge1.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    rng = np.random.default_rng(42)
    cond1 = rng.normal(loc=0.3, scale=1.0, size=150)
    base1 = rng.normal(loc=0.0, scale=1.0, size=150)

    res1 = validator.evaluate(
        candidate_edge=edge1,
        hypothesis_version="123",
        policy=policy,
        validation_run=run1,
        dataset_partitions={},
        multiplicity_coordinator=coord,
        cond_arr=cond1,
        base_arr=base1,
    )

    # Even though raw p was 0.04 <= 0.05, the FDR adjusted q (0.12) exceeds alpha (0.05)!
    assert res1.decision == StageDecision.FAIL
    assert res1.reason_code == ReasonCode.SIGNIFICANCE_FAILED
