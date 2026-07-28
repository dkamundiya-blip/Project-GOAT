"""
Project GOAT v0.6 — Engine Integration Unit Tests

Verifies complete pre-confirmatory (A-F) and synthetic confirmatory (A-G) pipeline orchestration.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationContextUniverse, ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.engine import MultiStageValidationEngine
from goat.research.edge.validation.holdout import HoldoutAccessGate
from goat.research.edge.validation.models import StageDecision, ValidationStage


@pytest.fixture
def sample_edge():
    return CandidateEdge(
        proposition_name="Engine Test Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )


@pytest.fixture
def sample_policy():
    return ValidationPolicy(policy_id="P1_ENGINE", stage_a_alpha=0.05, stage_a_effect_min=0.15)


@pytest.fixture
def sample_run(sample_edge, sample_policy):
    return ValidationRunInfo(
        edge_id=sample_edge.edge_id,
        policy_hash=sample_policy.policy_hash,
        dataset_fingerprint="ds_engine_fingerprint_123",
        candidate_target_scope="UNIVERSAL",
    )


@pytest.fixture
def synthetic_partitions():
    np.random.seed(42)
    cond_arr = np.random.normal(loc=0.35, scale=0.5, size=200)
    base_arr = np.random.normal(loc=0.0, scale=0.5, size=200)

    # Train / Discovery partition
    df_train = pd.DataFrame({"conditional_outcome": cond_arr, "baseline_outcome": base_arr})

    # Validation partition
    df_val = pd.DataFrame({"conditional_outcome": cond_arr, "baseline_outcome": base_arr})

    # Folds
    folds = [pd.DataFrame({"effect": np.random.normal(0.25, 0.1, 50)}) for _ in range(6)]

    # Perturbed grid
    grid = {f"p_{i}": 0.25 for i in range(10)}

    # Contradictory partition
    df_contra = pd.DataFrame({"effect": np.random.normal(-0.10, 0.2, 100)})

    # Synthetic Holdout partition
    df_holdout = pd.DataFrame({"effect": np.random.normal(0.30, 0.4, 150)})

    return {
        "train": df_train,
        "validation": df_val,
        "walk_forward_folds": folds,
        "perturbed_grid": grid,
        "contradictory": df_contra,
        "holdout": df_holdout,
    }


def test_full_a_to_f_preconfirmatory_pass(sample_edge, sample_policy, sample_run, synthetic_partitions):
    engine = MultiStageValidationEngine()
    universe = ValidationContextUniverse(contexts=("AAPL", "MSFT", "GOOGL"))
    contexts = [
        ("AAPL", 0.30, 0.001, 200),
        ("GOOGL", 0.32, 0.002, 200),
        ("MSFT", 0.28, 0.001, 200),
    ]

    results = engine.execute_preconfirmatory(
        candidate_edge=sample_edge,
        hypothesis_version="1234567890ab",
        policy=sample_policy,
        validation_run=sample_run,
        dataset_partitions=synthetic_partitions,
        context_evaluations=contexts,
        context_universe=universe,
        baseline_effect=0.30,
    )

    assert len(results) == 6
    for stage, res in results.items():
        assert res.decision == StageDecision.PASS


def test_full_synthetic_a_to_g_pass(sample_edge, sample_policy, sample_run, synthetic_partitions):
    engine = MultiStageValidationEngine()
    universe = ValidationContextUniverse(contexts=("AAPL", "MSFT", "GOOGL"))
    contexts = [
        ("AAPL", 0.30, 0.001, 200),
        ("GOOGL", 0.32, 0.002, 200),
        ("MSFT", 0.28, 0.001, 200),
    ]

    results_af = engine.execute_preconfirmatory(
        candidate_edge=sample_edge,
        hypothesis_version="1234567890ab",
        policy=sample_policy,
        validation_run=sample_run,
        dataset_partitions=synthetic_partitions,
        context_evaluations=contexts,
        context_universe=universe,
        baseline_effect=0.30,
    )

    stage_f_res = results_af[ValidationStage.STAGE_F_REPLICATION]
    gate = HoldoutAccessGate()

    res_g = engine.execute_confirmatory(
        candidate_edge=sample_edge,
        hypothesis_version="1234567890ab",
        policy=sample_policy,
        validation_run=sample_run,
        dataset_partitions=synthetic_partitions,
        stage_f_result=stage_f_res,
        holdout_gate=gate,
        baseline_effect=0.30,
        context_universe=universe,
    )

    assert res_g.decision == StageDecision.PASS
    assert gate.bytes_read > 0
