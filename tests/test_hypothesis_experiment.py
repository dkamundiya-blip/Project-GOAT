"""
Project GOAT v0.4 — Unit Tests for Experiment Runner & Workflow
"""

import pandas as pd
import pytest

from goat.research.dataset import DatasetManifest
from goat.research.hypothesis.definition import HypothesisDefinition
from goat.research.hypothesis.experiment import ExperimentRunner
from goat.research.outcomes import ForwardOutcomeTable


def test_experiment_runner_train_and_fdr_flow() -> None:
    """Test running experiment family with FDR control on TRAIN partition."""
    dates = pd.date_range("2024-07-22", periods=500, freq="1min")
    prices = [100.0 + (i * 0.1) for i in range(500)]
    df = pd.DataFrame({"timestamp": dates, "close": prices, "open": prices, "high": [p + 0.2 for p in prices], "low": [p - 0.2 for p in prices]})

    fwd_gen = ForwardOutcomeTable(horizons=[1, 5])
    outcomes_df = fwd_gen.compute_outcomes(df)

    manifest = DatasetManifest(
        dataset_id="test_ds_123",
        symbol="R_10",
        timeframe="M1",
        actual_start_timestamp=dates[0].to_pydatetime(),
        actual_end_timestamp=dates[-1].to_pydatetime(),
        actual_observation_count=500,
        canonical_checksum="dummy_checksum",
    )

    hyp1 = HypothesisDefinition(
        hypothesis_id="HYP-1",
        version="1.0.0",
        name="Hyp 1",
        description="Desc",
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 120.0},
        forward_outcome_metric="fwd_return_1",
        forward_horizon=1,
    )
    hyp2 = HypothesisDefinition(
        hypothesis_id="HYP-2",
        version="1.0.0",
        name="Hyp 2",
        description="Desc",
        causal_condition={"primitive": "less_than", "feature": "close"},
        condition_parameters={"threshold": 120.0},
        forward_outcome_metric="fwd_return_5",
        forward_horizon=5,
    )

    runner = ExperimentRunner()
    exp = runner.run_experiment_family(
        family_name="test_family",
        hypotheses=[hyp1, hyp2],
        df=df,
        outcomes_df=outcomes_df,
        manifest=manifest,
        allow_holdout=False,
    )

    assert exp.family_name == "test_family"
    assert len(exp.results) == 2
    assert exp.results[0].adjusted_q_value is not None
