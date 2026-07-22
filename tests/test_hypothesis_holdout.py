"""
Project GOAT v0.4 — Unit Tests for Sealed Holdout Discipline & Audit Log
"""

import json

import pandas as pd

from goat.config import GoatSettings
from goat.research.dataset import DatasetManifest
from goat.research.hypothesis.definition import HypothesisDefinition
from goat.research.hypothesis.experiment import ExperimentRunner
from goat.research.outcomes import ForwardOutcomeTable


def test_holdout_sealed_by_default_and_audited_on_access(tmp_path) -> None:
    """Test holdout is sealed by default and produces audit log when unsealed."""
    audit_file = tmp_path / "holdout_audit.json"
    settings = GoatSettings(holdout_audit_log_path=audit_file)

    dates = pd.date_range("2024-07-22", periods=100, freq="1min")
    prices = [100.0 + (i * 0.1) for i in range(100)]
    df = pd.DataFrame({"timestamp": dates, "close": prices})

    fwd_gen = ForwardOutcomeTable(horizons=[1])
    outcomes_df = fwd_gen.compute_outcomes(df)

    manifest = DatasetManifest(
        dataset_id="fp_test",
        symbol="R_10",
        timeframe="M1",
        actual_start_timestamp=dates[0].to_pydatetime(),
        actual_end_timestamp=dates[-1].to_pydatetime(),
        actual_observation_count=100,
        canonical_checksum="checksum",
    )

    hyp = HypothesisDefinition(
        hypothesis_id="HYP-HOLDOUT",
        version="1.0.0",
        name="Holdout test",
        description="Desc",
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
        forward_outcome_metric="fwd_return_1",
        forward_horizon=1,
    )

    runner = ExperimentRunner(settings=settings)

    # 1. Sealed holdout (default) -> holdout partition is sealed
    exp_sealed = runner.run_experiment_family(
        family_name="sealed_family",
        hypotheses=[hyp],
        df=df,
        outcomes_df=outcomes_df,
        manifest=manifest,
        allow_holdout=False,
    )
    assert "holdout" not in exp_sealed.partitions_accessed
    assert not audit_file.exists()

    # 2. Unsealed holdout (explicitly allowed) -> logs audit record
    exp_unsealed = runner.run_experiment_family(
        family_name="unsealed_family",
        hypotheses=[hyp],
        df=df,
        outcomes_df=outcomes_df,
        manifest=manifest,
        allow_holdout=True,
    )
    assert "holdout" in exp_unsealed.partitions_accessed
    assert audit_file.exists()

    audit_records = json.loads(audit_file.read_text(encoding="utf-8"))
    assert len(audit_records) == 1
    assert audit_records[0]["dataset_fingerprint"] == "fp_test"
