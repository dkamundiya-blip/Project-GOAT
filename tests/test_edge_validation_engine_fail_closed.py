"""
Project GOAT v0.6 — Engine Fail-Closed Unit Tests

Verifies that any failure or insufficient evidence decision at Stage A-F halts execution immediately.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.engine import MultiStageValidationEngine
from goat.research.edge.validation.models import StageDecision, ValidationStage


@pytest.fixture
def sample_edge():
    return CandidateEdge(
        proposition_name="Fail Closed Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )


@pytest.fixture
def sample_policy():
    return ValidationPolicy(policy_id="P1_FAIL", stage_a_alpha=0.05, stage_a_effect_min=0.15)


@pytest.fixture
def sample_run(sample_edge, sample_policy):
    return ValidationRunInfo(
        edge_id=sample_edge.edge_id,
        policy_hash=sample_policy.policy_hash,
        dataset_fingerprint="ds_fp_123",
        candidate_target_scope="UNIVERSAL",
    )


def test_stage_a_fail_blocks_all_downstream_stages(sample_edge, sample_policy, sample_run):
    engine = MultiStageValidationEngine()
    # Weak/empty partitions causing Stage A to fail sample requirement
    partitions = {"train": pd.DataFrame({"close": [10.0] * 10})}

    results = engine.execute_preconfirmatory(
        candidate_edge=sample_edge,
        hypothesis_version="1234567890ab",
        policy=sample_policy,
        validation_run=sample_run,
        dataset_partitions=partitions,
    )

    assert len(results) == 1
    assert ValidationStage.STAGE_A_DISCOVERY in results
    assert results[ValidationStage.STAGE_A_DISCOVERY].decision != StageDecision.PASS
    assert ValidationStage.STAGE_B_RETENTION not in results
    assert ValidationStage.STAGE_F_REPLICATION not in results
