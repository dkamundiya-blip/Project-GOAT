"""
Project GOAT v0.9 — Deriv Market Microstructure Liquidity Profiling Engine
"""

import math
from typing import Any

from goat.microstructure.core.canonical import (
    compute_liquidity_profile_id,
    compute_observation_id,
)
from goat.microstructure.core.enums import (
    MicrostructureMetricType,
    ObservationCategory,
    SyntheticIndexType,
)
from goat.microstructure.core.models import (
    LiquidityProfile,
    MicrostructureObservation,
)


class LiquidityProfilingEngine:
    """Quantitative Research Engine for Liquidity Profiling.

    Measures:
    • Spread stability (1 / (1 + stdev(spread)))
    • Quote continuity (fraction of time window with active quotes)
    • Tick density (ticks per second)
    • Market activity (composite volume / tick velocity metric)
    """

    def analyze_quotes(
        self,
        symbol: str,
        index_type: SyntheticIndexType | str,
        spreads: list[float],
        timestamps: list[float] | None = None,
        timestamp_str: str = "2026-01-01T00:00:00Z",
        window_seconds: int = 300,
        expected_tick_rate: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[LiquidityProfile, list[MicrostructureObservation]]:
        """Analyze bid-ask spreads and quote timestamps to quantify liquidity."""
        if isinstance(index_type, str):
            index_type = SyntheticIndexType(index_type)

        meta = dict(metadata or {})

        if not spreads:
            return self._build_fallback(symbol, index_type, timestamp_str, window_seconds, meta)

        num_ticks = len(spreads)
        avg_spread = sum(spreads) / num_ticks

        if num_ticks > 1:
            var_spread = sum((s - avg_spread) ** 2 for s in spreads) / num_ticks
            spread_stdev = math.sqrt(var_spread)
        else:
            spread_stdev = 0.0

        # Spread Stability (normalized 0..1 measure)
        spread_stability = 1.0 / (1.0 + spread_stdev)

        # Tick Density (ticks per second)
        duration = float(window_seconds)
        if timestamps and len(timestamps) > 1:
            duration = max(0.1, timestamps[-1] - timestamps[0])

        ticks_per_second = num_ticks / duration
        tick_density = num_ticks / (window_seconds / 60.0)  # Ticks per minute

        # Quote Continuity Score (observed tick rate vs expected tick rate, capped at 1.0)
        actual_rate = num_ticks / max(1.0, window_seconds)
        quote_continuity = min(1.0, max(0.0, actual_rate / max(0.001, expected_tick_rate)))

        # Composite Activity Score
        activity_score = round(ticks_per_second * 100.0 * spread_stability, 4)

        observations = []

        # Spread Stability Observation
        obs_id_ss, hash_ss = compute_observation_id(
            symbol, MicrostructureMetricType.SPREAD_STABILITY.value, timestamp_str, spread_stability, window_seconds
        )
        obs_ss = MicrostructureObservation(
            observation_id=obs_id_ss,
            metric_type=MicrostructureMetricType.SPREAD_STABILITY,
            category=ObservationCategory.LIQUIDITY,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=spread_stability,
            unit="stability_index",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_ss,
        )
        observations.append(obs_ss)

        # Quote Continuity Observation
        obs_id_qc, hash_qc = compute_observation_id(
            symbol, MicrostructureMetricType.QUOTE_CONTINUITY.value, timestamp_str, quote_continuity, window_seconds
        )
        obs_qc = MicrostructureObservation(
            observation_id=obs_id_qc,
            metric_type=MicrostructureMetricType.QUOTE_CONTINUITY,
            category=ObservationCategory.LIQUIDITY,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=quote_continuity,
            unit="continuity_ratio",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_qc,
        )
        observations.append(obs_qc)

        # Tick Density Observation
        obs_id_td, hash_td = compute_observation_id(
            symbol, MicrostructureMetricType.TICK_DENSITY.value, timestamp_str, tick_density, window_seconds
        )
        obs_td = MicrostructureObservation(
            observation_id=obs_id_td,
            metric_type=MicrostructureMetricType.TICK_DENSITY,
            category=ObservationCategory.LIQUIDITY,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=tick_density,
            unit="ticks_per_minute",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_td,
        )
        observations.append(obs_td)

        # Market Activity Observation
        obs_id_ma, hash_ma = compute_observation_id(
            symbol, MicrostructureMetricType.MARKET_ACTIVITY.value, timestamp_str, activity_score, window_seconds
        )
        obs_ma = MicrostructureObservation(
            observation_id=obs_id_ma,
            metric_type=MicrostructureMetricType.MARKET_ACTIVITY,
            category=ObservationCategory.LIQUIDITY,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=activity_score,
            unit="activity_index",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_ma,
        )
        observations.append(obs_ma)

        obs_ids = [o.observation_id for o in observations]

        prof_id, p_hash = compute_liquidity_profile_id(
            symbol=symbol,
            timestamp=timestamp_str,
            window_seconds=window_seconds,
            average_spread=avg_spread,
            tick_density=tick_density,
            observation_ids=obs_ids,
        )

        profile = LiquidityProfile(
            profile_id=prof_id,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            window_seconds=window_seconds,
            average_spread=avg_spread,
            spread_stdev=spread_stdev,
            spread_stability=spread_stability,
            quote_continuity_score=quote_continuity,
            ticks_per_second=ticks_per_second,
            tick_density=tick_density,
            activity_score=activity_score,
            observation_ids=obs_ids,
            metadata=meta,
            canonical_hash=p_hash,
        )

        return profile, observations

    def _build_fallback(
        self,
        symbol: str,
        index_type: SyntheticIndexType,
        timestamp_str: str,
        window_seconds: int,
        metadata: dict[str, Any],
    ) -> tuple[LiquidityProfile, list[MicrostructureObservation]]:
        obs_id, o_hash = compute_observation_id(
            symbol, MicrostructureMetricType.SPREAD_STABILITY.value, timestamp_str, 0.0, window_seconds
        )
        obs = MicrostructureObservation(
            observation_id=obs_id,
            metric_type=MicrostructureMetricType.SPREAD_STABILITY,
            category=ObservationCategory.LIQUIDITY,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=0.0,
            unit="stability_index",
            window_seconds=window_seconds,
            metadata=metadata,
            canonical_hash=o_hash,
        )
        p_id, p_hash = compute_liquidity_profile_id(symbol, timestamp_str, window_seconds, 0.0, 0.0, [obs_id])
        prof = LiquidityProfile(
            profile_id=p_id,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            window_seconds=window_seconds,
            average_spread=0.0,
            spread_stdev=0.0,
            spread_stability=0.0,
            quote_continuity_score=0.0,
            ticks_per_second=0.0,
            tick_density=0.0,
            activity_score=0.0,
            observation_ids=[obs_id],
            metadata=metadata,
            canonical_hash=p_hash,
        )
        return prof, [obs]
