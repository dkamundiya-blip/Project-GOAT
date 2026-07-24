"""
Project GOAT v0.5 — Unit Tests for WorkerPool & Seed Derivation
"""

import pandas as pd
import pytest

from goat.orchestration.queue import ExperimentTask
from goat.orchestration.worker import WorkerPool, derive_canonical_seed_material
from goat.research.hypothesis.definition import HypothesisDefinition


def test_derive_canonical_seed_material() -> None:
    """Test 32-byte canonical seed material derivation is invariant across calls."""
    seed1 = derive_canonical_seed_material(master_seed=42, experiment_id="EXP-123")
    seed2 = derive_canonical_seed_material(master_seed=42, experiment_id="EXP-123")
    seed3 = derive_canonical_seed_material(master_seed=99, experiment_id="EXP-123")

    assert len(seed1) == 32
    assert seed1 == seed2  # Same master seed + experiment_id -> byte-for-byte identical
    assert seed1 != seed3  # Different master seed -> different bytes


def test_worker_pool_task_execution() -> None:
    """Test WorkerPool executes task and returns HypothesisResult."""
    hyp = HypothesisDefinition(
        hypothesis_id="HYP-WORKER-TEST",
        version="1.0.0",
        name="Worker test",
        description="Worker description",
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
        forward_outcome_metric="fwd_return_1",
        forward_horizon=1,
    )
    task = ExperimentTask("exp_worker_1", hyp, "R_10", "M1")

    dates = pd.date_range("2024-07-22", periods=60, freq="1min")
    prices = [100.0 + (i * 0.1) for i in range(60)]
    df = pd.DataFrame({"timestamp": dates, "close": prices})

    from goat.research.outcomes import ForwardOutcomeTable
    outcomes_df = ForwardOutcomeTable(horizons=[1]).compute_outcomes(df)

    pool = WorkerPool(max_workers=2, master_seed=42)
    res_task, res, err = pool.execute_task(
        task=task,
        df=df,
        outcomes_df=outcomes_df,
        dataset_fingerprint="fp_test",
        worker_id="worker_0",
    )

    assert err is None
    assert res is not None
    assert res.hypothesis_id == "HYP-WORKER-TEST"
    assert res.partition == "train"
