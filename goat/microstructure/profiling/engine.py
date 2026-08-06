"""
Project GOAT v0.9 — Deriv Market Microstructure Aggregation Engine
"""

from typing import Any

from goat.microstructure.core.canonical import compute_market_profile_id
from goat.microstructure.core.enums import SyntheticIndexType
from goat.microstructure.core.models import (
    ExecutionProfile,
    JumpProfile,
    LiquidityProfile,
    MarketProfile,
    VolatilityProfile,
)


class MarketProfilingEngine:
    """Quantitative Research Engine for Market Profile Aggregation.

    Aggregates all domain profiles (volatility, jump, liquidity, execution) into
    an immutable unified MarketProfile.
    """

    def aggregate_market_profile(
        self,
        symbol: str,
        index_type: SyntheticIndexType | str,
        volatility_profile: VolatilityProfile,
        jump_profile: JumpProfile,
        liquidity_profile: LiquidityProfile,
        execution_profile: ExecutionProfile,
        timestamp_str: str = "2026-01-01T00:00:00Z",
        metadata: dict[str, Any] | None = None,
    ) -> MarketProfile:
        """Aggregate sub-profiles into an immutable MarketProfile."""
        if isinstance(index_type, str):
            index_type = SyntheticIndexType(index_type)

        meta = dict(metadata or {})

        total_obs = (
            len(volatility_profile.observation_ids)
            + len(jump_profile.observation_ids)
            + len(liquidity_profile.observation_ids)
            + len(execution_profile.observation_ids)
        )

        # Compute overall market health score (0..100)
        # Components: liquidity score (35%), execution score (35%), stability score (30%)
        liq_contrib = liquidity_profile.quote_continuity_score * 35.0
        exec_contrib = execution_profile.consistency_score * 35.0
        stab_contrib = liquidity_profile.spread_stability * 30.0
        overall_health = round(min(100.0, max(0.0, liq_contrib + exec_contrib + stab_contrib)), 2)

        prof_id, p_hash = compute_market_profile_id(
            symbol=symbol,
            timestamp=timestamp_str,
            volatility_profile_id=volatility_profile.profile_id,
            jump_profile_id=jump_profile.profile_id,
            liquidity_profile_id=liquidity_profile.profile_id,
            execution_profile_id=execution_profile.profile_id,
        )

        return MarketProfile(
            profile_id=prof_id,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            volatility_profile_id=volatility_profile.profile_id,
            jump_profile_id=jump_profile.profile_id,
            liquidity_profile_id=liquidity_profile.profile_id,
            execution_profile_id=execution_profile.profile_id,
            observation_count=total_obs,
            overall_health_score=overall_health,
            metadata=meta,
            canonical_hash=p_hash,
        )
