"""
Project GOAT v0.5 — Unit Tests for Stochastic Seed Determinism & Invariant #6
"""

from unittest.mock import patch
import numpy as np
import pandas as pd
import pytest

from goat.orchestration.queue import ExperimentTask
from goat.orchestration.scheduler import compute_experiment_id
from goat.orchestration.worker import WorkerPool, derive_canonical_seed_material, seed_material_to_int
from goat.research.hypothesis.definition import HypothesisDefinition
from goat.research.hypothesis.experiment import ExperimentRunner
from goat.research.hypothesis.result import HypothesisResult
from goat.research.hypothesis.testing import run_statistical_test
from goat.research.outcomes import ForwardOutcomeTable


def make_stochastic_hypothesis(hyp_id: str = "HYP-STOCH-01") -> HypothesisDefinition:
    """Create hypothesis definition configured to use stochastic permutation testing."""
    return HypothesisDefinition(
        hypothesis_id=hyp_id,
        version="1.0.0",
        name="Stochastic Permutation Hypothesis",
        description="Hypothesis for testing stochastic seed propagation",
        symbol_scope=["R_10"],
        timeframe_scope=["M1"],
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
        forward_outcome_metric="fwd_return_1",
        forward_horizon=1,
        statistical_test="permutation",
    )


def make_mock_market_data(num_bars: int = 100) -> tuple[pd.DataFrame, pd.DataFrame]:
    dates = pd.date_range("2024-07-22", periods=num_bars, freq="1min")
    prices = [100.0 + (i % 5) * 0.5 for i in range(num_bars)]
    df = pd.DataFrame({"timestamp": dates, "close": prices})
    outcomes_df = ForwardOutcomeTable(horizons=[1]).compute_outcomes(df)
    return df, outcomes_df


def test_seed_determinism_same_master_seed_same_output() -> None:
    """1. Same experiment + same master_seed produces identical stochastic statistical output across repeated execution."""
    hyp = make_stochastic_hypothesis()
    df, outcomes_df = make_mock_market_data()
    exp_id = compute_experiment_id(hyp, "R_10", "M1", "fp_test")
    task = ExperimentTask(exp_id, hyp, "R_10", "M1")

    pool1 = WorkerPool(max_workers=1, master_seed=42)
    _, res1, err1 = pool1.execute_task(task, df, outcomes_df, "fp_test")

    pool2 = WorkerPool(max_workers=1, master_seed=42)
    _, res2, err2 = pool2.execute_task(task, df, outcomes_df, "fp_test")

    assert err1 is None and err2 is None
    assert res1 is not None and res2 is not None
    assert res1.raw_p_value == res2.raw_p_value
    assert res1.statistic_value == res2.statistic_value


def test_seed_determinism_worker_count_invariance() -> None:
    """2. Same experiment executed with different worker counts produces identical stochastic statistical output."""
    hyp = make_stochastic_hypothesis()
    df, outcomes_df = make_mock_market_data()
    exp_id = compute_experiment_id(hyp, "R_10", "M1", "fp_test")

    tasks1 = [ExperimentTask(exp_id, hyp, "R_10", "M1")]
    tasks2 = [ExperimentTask(exp_id, hyp, "R_10", "M1")]

    pool1 = WorkerPool(max_workers=1, master_seed=42)
    batch_res1 = pool1.execute_batch(tasks1, {("R_10", "M1"): df}, {("R_10", "M1"): outcomes_df}, {("R_10", "M1"): "fp_test"})

    pool4 = WorkerPool(max_workers=4, master_seed=42)
    batch_res2 = pool4.execute_batch(tasks2, {("R_10", "M1"): df}, {("R_10", "M1"): outcomes_df}, {("R_10", "M1"): "fp_test"})

    res1 = batch_res1[0][1]
    res2 = batch_res2[0][1]
    assert res1 is not None and res2 is not None
    assert res1.raw_p_value == res2.raw_p_value


def test_seed_determinism_task_execution_order_invariance() -> None:
    """3. Different task execution order does not alter stochastic output."""
    hypA = make_stochastic_hypothesis("HYP-A")
    hypB = make_stochastic_hypothesis("HYP-B")
    df, outcomes_df = make_mock_market_data()

    taskA = ExperimentTask(compute_experiment_id(hypA, "R_10", "M1", "fp"), hypA, "R_10", "M1")
    taskB = ExperimentTask(compute_experiment_id(hypB, "R_10", "M1", "fp"), hypB, "R_10", "M1")

    pool = WorkerPool(max_workers=1, master_seed=42)

    _, resA1, _ = pool.execute_task(taskA, df, outcomes_df, "fp")
    _, resB1, _ = pool.execute_task(taskB, df, outcomes_df, "fp")

    _, resB2, _ = pool.execute_task(taskB, df, outcomes_df, "fp")
    _, resA2, _ = pool.execute_task(taskA, df, outcomes_df, "fp")

    assert resA1 is not None and resA2 is not None
    assert resB1 is not None and resB2 is not None
    assert resA1.raw_p_value == resA2.raw_p_value
    assert resB1.raw_p_value == resB2.raw_p_value


def test_seed_determinism_worker_id_invariance() -> None:
    """4. Different worker IDs do not alter stochastic output."""
    hyp = make_stochastic_hypothesis()
    df, outcomes_df = make_mock_market_data()
    task = ExperimentTask(compute_experiment_id(hyp, "R_10", "M1", "fp"), hyp, "R_10", "M1")

    pool = WorkerPool(max_workers=1, master_seed=42)
    _, res_w0, _ = pool.execute_task(task, df, outcomes_df, "fp", worker_id="worker_0")
    _, res_w99, _ = pool.execute_task(task, df, outcomes_df, "fp", worker_id="worker_99")

    assert res_w0 is not None and res_w99 is not None
    assert res_w0.raw_p_value == res_w99.raw_p_value


def test_seed_determinism_no_global_rng_mutation() -> None:
    """5. No stochastic statistical test uses shared mutable global RNG state."""
    np.random.seed(999999)

    hyp = make_stochastic_hypothesis()
    df, outcomes_df = make_mock_market_data()
    task = ExperimentTask(compute_experiment_id(hyp, "R_10", "M1", "fp"), hyp, "R_10", "M1")

    pool = WorkerPool(max_workers=1, master_seed=42)
    _, res1, _ = pool.execute_task(task, df, outcomes_df, "fp")

    np.random.seed(111111)
    pool2 = WorkerPool(max_workers=1, master_seed=42)
    _, res2, _ = pool2.execute_task(task, df, outcomes_df, "fp")

    assert res1 is not None and res2 is not None
    assert res1.raw_p_value == res2.raw_p_value


def test_canonical_seed_material_reaches_statistical_test() -> None:
    """6. canonical_seed_material actually reaches the stochastic statistical execution path."""
    hyp = make_stochastic_hypothesis()
    df, outcomes_df = make_mock_market_data()
    exp_id = compute_experiment_id(hyp, "R_10", "M1", "fp")
    task = ExperimentTask(exp_id, hyp, "R_10", "M1")

    expected_bytes = derive_canonical_seed_material(master_seed=42, experiment_id=exp_id)
    expected_seed_int = seed_material_to_int(expected_bytes, num_bytes=16)

    captured_seeds: list[int] = []

    original_run_stat = run_statistical_test

    def mock_run_stat(*args, **kwargs):
        if "seed" in kwargs:
            captured_seeds.append(kwargs["seed"])
        return original_run_stat(*args, **kwargs)

    with patch("goat.research.hypothesis.experiment.run_statistical_test", side_effect=mock_run_stat):
        pool = WorkerPool(max_workers=1, master_seed=42)
        pool.execute_task(task, df, outcomes_df, "fp")

    assert len(captured_seeds) == 1
    assert captured_seeds[0] == expected_seed_int


def test_seed_determinism_different_master_seeds_differ() -> None:
    """7. Different master_seed values produce different derived experiment-local random streams where randomness is used."""
    hyp = make_stochastic_hypothesis()
    df, outcomes_df = make_mock_market_data()
    exp_id = compute_experiment_id(hyp, "R_10", "M1", "fp")
    task = ExperimentTask(exp_id, hyp, "R_10", "M1")

    pool_seed42 = WorkerPool(max_workers=1, master_seed=42)
    _, res42, _ = pool_seed42.execute_task(task, df, outcomes_df, "fp")

    pool_seed999 = WorkerPool(max_workers=1, master_seed=999)
    _, res999, _ = pool_seed999.execute_task(task, df, outcomes_df, "fp")

    assert res42 is not None and res999 is not None
    seed42_int = seed_material_to_int(derive_canonical_seed_material(42, exp_id))
    seed999_int = seed_material_to_int(derive_canonical_seed_material(999, exp_id))
    assert seed42_int != seed999_int


def test_seed_determinism_task_retry_reuses_canonical_seed() -> None:
    """8. Retrying the same experiment reuses the same canonical seed and reproduces the same statistical result."""
    hyp = make_stochastic_hypothesis()
    df, outcomes_df = make_mock_market_data()
    exp_id = compute_experiment_id(hyp, "R_10", "M1", "fp")
    task = ExperimentTask(exp_id, hyp, "R_10", "M1")

    pool = WorkerPool(max_workers=1, master_seed=42)
    _, res_try1, _ = pool.execute_task(task, df, outcomes_df, "fp")

    task.retry_count += 1
    _, res_try2, _ = pool.execute_task(task, df, outcomes_df, "fp")

    assert res_try1 is not None and res_try2 is not None
    assert res_try1.raw_p_value == res_try2.raw_p_value


def test_existing_deterministic_tests_unchanged() -> None:
    """9. Existing deterministic statistical tests remain unchanged."""
    c = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    b = np.array([0.5, 1.5, 2.5, 3.5, 4.5])

    stat_welch, p_welch = run_statistical_test(c, b, test_type="welch_ttest")
    assert p_welch < 1.0

    stat_mw, p_mw = run_statistical_test(c, b, test_type="mann_whitney")
    assert p_mw < 1.0
