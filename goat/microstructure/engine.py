"""
Project GOAT v0.9 — Deriv Market Microstructure Research Engine
"""

from typing import Any

from goat.microstructure.core.canonical import compute_research_summary_id
from goat.microstructure.core.enums import SyntheticIndexType
from goat.microstructure.core.models import (
    ExecutionProfile,
    JumpProfile,
    LiquidityProfile,
    MarketProfile,
    MicrostructureObservation,
    ResearchSummary,
    VolatilityProfile,
)
from goat.microstructure.execution.engine import ExecutionProfilingEngine
from goat.microstructure.jumps.engine import JumpProfilingEngine
from goat.microstructure.liquidity.engine import LiquidityProfilingEngine
from goat.microstructure.persistence.sqlite import MicrostructureDatabase
from goat.microstructure.profiling.engine import MarketProfilingEngine
from goat.microstructure.reporting.reports import MicrostructureReportGenerator
from goat.microstructure.volatility.engine import VolatilityProfilingEngine


class MicrostructureResearchEngine:
    """Master Research Engine for Deriv Market Microstructure & Synthetic Index Analysis.

    Scientifically measures, classifies, and archives observable market microstructure
    characteristics across Deriv Synthetic Indices.

    Strict Non-Trading Protocol:
    • NO trading signals
    • NO order execution
    • NO hypothesis evaluation
    • ONLY scientific measurement and archiving
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db = MicrostructureDatabase(db_path)
        self.volatility_engine = VolatilityProfilingEngine()
        self.jump_engine = JumpProfilingEngine()
        self.liquidity_engine = LiquidityProfilingEngine()
        self.execution_engine = ExecutionProfilingEngine()
        self.market_profiling_engine = MarketProfilingEngine()
        self.reporter = MicrostructureReportGenerator()

    def profile_synthetic_index(
        self,
        symbol: str,
        index_type: SyntheticIndexType | str,
        prices: list[float],
        spreads: list[float] | None = None,
        latencies_ms: list[float] | None = None,
        fill_times_ms: list[float] | None = None,
        timestamps: list[float] | None = None,
        timestamp_str: str = "2026-01-01T00:00:00Z",
        window_seconds: int = 300,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[MarketProfile, list[MicrostructureObservation]]:
        """Run complete quantitative microstructure analysis on a synthetic index."""
        if isinstance(index_type, str):
            index_type = SyntheticIndexType(index_type)

        meta = dict(metadata or {})
        spreads = spreads or [0.001] * max(1, len(prices))
        latencies_ms = latencies_ms or [45.0] * max(1, len(prices))

        # 1. Volatility Profiling
        vol_profile, vol_obs = self.volatility_engine.analyze_series(
            symbol=symbol,
            index_type=index_type,
            prices=prices,
            timestamp=timestamp_str,
            window_seconds=window_seconds,
            metadata=meta,
        )

        # 2. Jump Profiling
        jump_profile, jump_obs = self.jump_engine.analyze_series(
            symbol=symbol,
            index_type=index_type,
            prices=prices,
            timestamps=timestamps,
            timestamp_str=timestamp_str,
            window_seconds=window_seconds,
            metadata=meta,
        )

        # 3. Liquidity Profiling
        liq_profile, liq_obs = self.liquidity_engine.analyze_quotes(
            symbol=symbol,
            index_type=index_type,
            spreads=spreads,
            timestamps=timestamps,
            timestamp_str=timestamp_str,
            window_seconds=window_seconds,
            metadata=meta,
        )

        # 4. Execution Profiling
        exec_profile, exec_obs = self.execution_engine.analyze_latencies(
            symbol=symbol,
            index_type=index_type,
            latencies_ms=latencies_ms,
            fill_times_ms=fill_times_ms,
            timestamp_str=timestamp_str,
            window_seconds=window_seconds,
            metadata=meta,
        )

        # Aggregate Observations
        all_obs = vol_obs + jump_obs + liq_obs + exec_obs

        # Save profiles first (due to foreign key constraints in MarketProfile table)
        self.db.volatility.save(vol_profile)
        self.db.jumps.save(jump_profile)
        self.db.liquidity.save(liq_profile)
        self.db.execution.save(exec_profile)

        for obs in all_obs:
            self.db.observations.save(obs)

        # 5. Market Profile Aggregation
        market_profile = self.market_profiling_engine.aggregate_market_profile(
            symbol=symbol,
            index_type=index_type,
            volatility_profile=vol_profile,
            jump_profile=jump_profile,
            liquidity_profile=liq_profile,
            execution_profile=exec_profile,
            timestamp_str=timestamp_str,
            metadata=meta,
        )
        self.db.market_profiles.save(market_profile)

        return market_profile, all_obs

    def generate_research_summary(
        self, timestamp_str: str = "2026-01-01T00:00:00Z", metadata: dict[str, Any] | None = None
    ) -> ResearchSummary:
        """Compute and persist an immutable ResearchSummary across archived observations."""
        meta = dict(metadata or {})

        all_obs = self.db.observations.list_all()
        vol_profs = self.db.volatility.list_all()
        jump_profs = self.db.jumps.list_all()
        liq_profs = self.db.liquidity.list_all()
        exec_profs = self.db.execution.list_all()
        mkt_profs = self.db.market_profiles.list_all()

        symbols_set = {p.symbol for p in mkt_profs} | {o.symbol for o in all_obs}
        symbols_list = sorted(list(symbols_set))

        category_counts: dict[str, int] = {}
        for o in all_obs:
            c_val = o.category.value
            category_counts[c_val] = category_counts.get(c_val, 0) + 1

        summary_id, s_hash = compute_research_summary_id(
            timestamp=timestamp_str,
            total_observations=len(all_obs),
            symbols_profiled=symbols_list,
        )

        summary = ResearchSummary(
            summary_id=summary_id,
            timestamp=timestamp_str,
            symbols_profiled=symbols_list,
            total_observations=len(all_obs),
            total_volatility_profiles=len(vol_profs),
            total_jump_profiles=len(jump_profs),
            total_liquidity_profiles=len(liq_profs),
            total_execution_profiles=len(exec_profs),
            total_market_profiles=len(mkt_profs),
            category_breakdown=category_counts,
            metadata=meta,
            canonical_hash=s_hash,
        )

        self.db.summaries.save(summary)
        return summary

    def close(self) -> None:
        """Close SQLite persistence connection."""
        self.db.close()
