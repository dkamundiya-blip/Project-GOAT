"""
Project GOAT v0.5 — Unit Tests for Worker-Count Invariant Determinism

Verifies that executing a campaign with 1 worker, 2 workers, or 4 workers
produces 100% byte-for-byte identical scientific outputs, reports, and manifests.
"""

import json
from pathlib import Path
import pandas as pd
import pytest

from goat.config import GoatSettings
from goat.data.schemas import Timeframe
from goat.data.storage.parquet import ParquetStorage
from goat.orchestration.campaign import CampaignDefinition
from goat.orchestration.scheduler import ExperimentScheduler, compute_configuration_hash
from goat.research.hypothesis.definition import HypothesisDefinition


def test_worker_count_invariant_determinism(tmp_path) -> None:
    """Test campaign execution with 1, 2, and 4 workers yields identical output files."""
    settings = GoatSettings(
        data_dir=tmp_path / "data",
        raw_data_dir=tmp_path / "data" / "raw",
        processed_data_dir=tmp_path / "data" / "processed",
        research_data_dir=tmp_path / "data" / "research",
        campaign_data_dir=tmp_path / "data" / "campaigns",
    )
    storage = ParquetStorage(settings.get_raw_data_dir(), settings.get_processed_data_dir())
    # 1. Create mock market data
    dates = pd.date_range("2024-07-22", periods=100, freq="1min", tz="UTC")
    prices = [100.0 + (i * 0.1) for i in range(100)]
    df = pd.DataFrame({
        "timestamp": dates,
        "open": prices,
        "high": [p + 0.05 for p in prices],
        "low": [p - 0.05 for p in prices],
        "close": prices,
        "volume": [10.0] * 100,
    })

    from decimal import Decimal
    from goat.data.schemas import Candle, DataSource, Timeframe

    candles = [
        Candle(
            symbol="R_10",
            timeframe=Timeframe.M1,
            timestamp=row.timestamp.to_pydatetime(),
            open=Decimal(str(row.open)),
            high=Decimal(str(row.high)),
            low=Decimal(str(row.low)),
            close=Decimal(str(row.close)),
            source=DataSource.HISTORICAL_IMPORT,
        )
        for row in df.itertuples()
    ]
    storage.write_candles("R_10", Timeframe.M1, candles)

    # 2. Define hypothesis grid
    hyp1 = HypothesisDefinition(
        hypothesis_id="HYP-INVARIANT-1",
        version="1.0.0",
        name="Hypothesis 1",
        description="Desc 1",
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 102.0},
        forward_outcome_metric="fwd_return_1",
        forward_horizon=1,
    )
    hyp2 = HypothesisDefinition(
        hypothesis_id="HYP-INVARIANT-2",
        version="1.0.0",
        name="Hypothesis 2",
        description="Desc 2",
        causal_condition={"primitive": "less_than", "feature": "close"},
        condition_parameters={"threshold": 105.0},
        forward_outcome_metric="fwd_return_1",
        forward_horizon=1,
    )
    grid = [hyp1, hyp2]

    symbols = ["R_10"]
    timeframes = ["M1"]

    cfg_hash = compute_configuration_hash(
        hypothesis_grid=grid,
        symbols=symbols,
        timeframes=timeframes,
        master_seed=42,
        fdr_alpha=0.05,
    )

    outputs_by_worker_count: dict[int, dict[str, str]] = {}

    for worker_count in (1, 2, 4):
        scheduler = ExperimentScheduler(settings=settings, storage=storage)

        camp_def = CampaignDefinition(
            campaign_id=f"CMP-INVARIANT-W{worker_count}",
            configuration_hash=cfg_hash,
            name="Invariant Test Campaign",
            symbol_scope=symbols,
            timeframe_scope=timeframes,
            master_seed=42,
            max_workers=worker_count,
        )

        out_dir = scheduler.run_campaign(
            campaign_def=camp_def,
            hypothesis_grid=grid,
            symbols=symbols,
            timeframes=timeframes,
        )

        # Read output files and parse JSON to strip execution timestamps
        results_json = json.loads((out_dir / "experiment_results.json").read_text(encoding="utf-8"))
        for item in results_json:
            item.pop("created_at", None)

        stats_json = json.loads((out_dir / "campaign_statistics.json").read_text(encoding="utf-8"))
        stats_json.pop("campaign_id", None)

        outputs_by_worker_count[worker_count] = {
            "results": json.dumps(results_json, sort_keys=True),
            "stats": json.dumps(stats_json, sort_keys=True),
        }

    # 3. Assert 100% identical scientific outputs across 1 worker, 2 workers, and 4 workers
    w1_out = outputs_by_worker_count[1]
    w2_out = outputs_by_worker_count[2]
    w4_out = outputs_by_worker_count[4]

    assert w1_out["results"] == w2_out["results"] == w4_out["results"]
    assert w1_out["stats"] == w2_out["stats"] == w4_out["stats"]
