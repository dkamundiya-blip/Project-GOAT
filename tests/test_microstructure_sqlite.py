"""
Project GOAT v0.9 — Dedicated Tests for Microstructure SQLite Persistence & Repositories
"""

import sqlite3
import pytest

from goat.microstructure.core.enums import SyntheticIndexType
from goat.microstructure.core.models import (
    ExecutionProfile,
    JumpProfile,
    LiquidityProfile,
    VolatilityProfile,
)
from goat.microstructure.execution.engine import ExecutionProfilingEngine
from goat.microstructure.jumps.engine import JumpProfilingEngine
from goat.microstructure.liquidity.engine import LiquidityProfilingEngine
from goat.microstructure.persistence.sqlite import MicrostructureDatabase
from goat.microstructure.profiling.engine import MarketProfilingEngine
from goat.microstructure.volatility.engine import VolatilityProfilingEngine

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_sqlite_repository_roundtrips(index_type: SyntheticIndexType) -> None:
    db = MicrostructureDatabase(":memory:")

    # Pragma checks
    cursor = db.conn.execute("PRAGMA foreign_keys;")
    assert cursor.fetchone()[0] == 1

    vol_p, vol_obs = VolatilityProfilingEngine().analyze_series("SYM", index_type, [100.0, 101.0, 100.5])
    jmp_p, jmp_obs = JumpProfilingEngine().analyze_series("SYM", index_type, [100.0, 101.0, 100.5])
    liq_p, liq_obs = LiquidityProfilingEngine().analyze_quotes("SYM", index_type, [0.001, 0.001])
    exc_p, exc_obs = ExecutionProfilingEngine().analyze_latencies("SYM", index_type, [50.0, 60.0])

    # Save components
    db.volatility.save(vol_p)
    db.jumps.save(jmp_p)
    db.liquidity.save(liq_p)
    db.execution.save(exc_p)

    for o in vol_obs + jmp_obs + liq_obs + exc_obs:
        db.observations.save(o)

    mkt_p = MarketProfilingEngine().aggregate_market_profile("SYM", index_type, vol_p, jmp_p, liq_p, exc_p)
    db.market_profiles.save(mkt_p)

    # Retrieval assertions
    fetched_mkt = db.market_profiles.get_by_id(mkt_p.profile_id)
    assert fetched_mkt is not None
    assert fetched_mkt.profile_id == mkt_p.profile_id
    assert fetched_mkt.canonical_hash == mkt_p.canonical_hash
    assert fetched_mkt.index_type == index_type

    fetched_vol = db.volatility.get_by_id(vol_p.profile_id)
    assert fetched_vol is not None
    assert fetched_vol.realized_volatility == vol_p.realized_volatility

    fetched_jmp = db.jumps.get_by_id(jmp_p.profile_id)
    assert fetched_jmp is not None
    assert fetched_jmp.jump_count == jmp_p.jump_count

    fetched_liq = db.liquidity.get_by_id(liq_p.profile_id)
    assert fetched_liq is not None
    assert fetched_liq.average_spread == liq_p.average_spread

    fetched_exc = db.execution.get_by_id(exc_p.profile_id)
    assert fetched_exc is not None
    assert fetched_exc.mean_latency_ms == exc_p.mean_latency_ms

    db.close()


def test_sqlite_foreign_key_enforcement() -> None:
    db = MicrostructureDatabase(":memory:")
    # Try inserting MarketProfile with bogus foreign keys -> must raise IntegrityError
    mkt_p = MarketProfilingEngine().aggregate_market_profile(
        "SYM",
        SyntheticIndexType.VOLATILITY_10,
        VolatilityProfile(
            profile_id="VLP_BOGUS",
            symbol="SYM",
            index_type=SyntheticIndexType.VOLATILITY_10,
            timestamp="2026-01-01T00:00:00Z",
            window_seconds=300,
            realized_volatility=0.0,
            volatility_clustering_coeff=0.0,
            volatility_persistence=0.0,
            expansion_ratio=1.0,
            contraction_ratio=1.0,
            regime="NORMAL_VOLATILITY",
            observation_ids=[],
            metadata={},
            canonical_hash="HASH",
        ),
        JumpProfile(
            profile_id="JMP_BOGUS",
            symbol="SYM",
            index_type=SyntheticIndexType.VOLATILITY_10,
            timestamp="2026-01-01T00:00:00Z",
            window_seconds=300,
            jump_count=0,
            jump_frequency=0.0,
            mean_jump_magnitude=0.0,
            max_jump_magnitude=0.0,
            mean_jump_spacing_sec=300.0,
            jump_persistence=0.0,
            jump_clustering_index=0.0,
            dominant_direction="NEUTRAL",
            observation_ids=[],
            metadata={},
            canonical_hash="HASH",
        ),
        LiquidityProfile(
            profile_id="LIQ_BOGUS",
            symbol="SYM",
            index_type=SyntheticIndexType.VOLATILITY_10,
            timestamp="2026-01-01T00:00:00Z",
            window_seconds=300,
            average_spread=0.0,
            spread_stdev=0.0,
            spread_stability=0.0,
            quote_continuity_score=0.0,
            ticks_per_second=0.0,
            tick_density=0.0,
            activity_score=0.0,
            observation_ids=[],
            metadata={},
            canonical_hash="HASH",
        ),
        ExecutionProfile(
            profile_id="EXP_BOGUS",
            symbol="SYM",
            index_type=SyntheticIndexType.VOLATILITY_10,
            timestamp="2026-01-01T00:00:00Z",
            window_seconds=300,
            sample_count=0,
            mean_latency_ms=0.0,
            median_latency_ms=0.0,
            p95_latency_ms=0.0,
            fill_time_ms=0.0,
            consistency_score=1.0,
            rating="NORMAL",
            observation_ids=[],
            metadata={},
            canonical_hash="HASH",
        ),
    )

    with pytest.raises(sqlite3.IntegrityError):
        db.market_profiles.save(mkt_p)

    db.close()
