"""
Project GOAT v0.9 — Deriv Market Microstructure Volatility Profiling Engine
"""

import math
from typing import Any

from goat.microstructure.core.canonical import (
    compute_observation_id,
    compute_volatility_profile_id,
)
from goat.microstructure.core.enums import (
    MicrostructureMetricType,
    ObservationCategory,
    SyntheticIndexType,
    VolatilityRegime,
)
from goat.microstructure.core.models import (
    MicrostructureObservation,
    VolatilityProfile,
)


class VolatilityProfilingEngine:
    """Quantitative Research Engine for Volatility Profiling.

    Measures:
    • Realized volatility
    • Volatility clustering (autocorrelation of return magnitudes)
    • Volatility persistence (decay / autoregressive coefficient)
    • Volatility expansion (peak rolling volatility ratio)
    • Volatility contraction (trough rolling volatility ratio)
    """

    def analyze_series(
        self,
        symbol: str,
        index_type: SyntheticIndexType | str,
        prices: list[float],
        timestamp: str = "2026-01-01T00:00:00Z",
        window_seconds: int = 300,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[VolatilityProfile, list[MicrostructureObservation]]:
        """Analyze a series of price data to measure volatility characteristics."""
        if isinstance(index_type, str):
            index_type = SyntheticIndexType(index_type)

        meta = dict(metadata or {})
        if len(prices) < 2:
            return self._build_fallback(symbol, index_type, timestamp, window_seconds, meta)

        # Log returns
        returns = []
        for i in range(1, len(prices)):
            p0, p1 = prices[i - 1], prices[i]
            if p0 > 0 and p1 > 0:
                returns.append(math.log(p1 / p0))
            else:
                returns.append(0.0)

        if not returns:
            return self._build_fallback(symbol, index_type, timestamp, window_seconds, meta)

        # 1. Realized Volatility (standard deviation of log returns)
        mean_ret = sum(returns) / len(returns)
        var_ret = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
        realized_vol = math.sqrt(var_ret)

        # 2. Volatility Clustering (lag-1 autocorrelation of absolute returns)
        abs_returns = [abs(r) for r in returns]
        vol_clustering = self._compute_autocorr(abs_returns, lag=1)

        # 3. Volatility Persistence (lag-2 autocorrelation of squared returns)
        sq_returns = [r ** 2 for r in returns]
        vol_persistence = self._compute_autocorr(sq_returns, lag=1)

        # 4 & 5. Volatility Expansion and Contraction Ratios
        sub_window = max(2, len(returns) // 5)
        rolling_vols = []
        for i in range(0, len(returns) - sub_window + 1, max(1, sub_window // 2)):
            sub = returns[i : i + sub_window]
            sub_mean = sum(sub) / len(sub)
            sub_var = sum((r - sub_mean) ** 2 for r in sub) / len(sub)
            rolling_vols.append(math.sqrt(sub_var))

        if rolling_vols and realized_vol > 1e-12:
            max_vol = max(rolling_vols)
            min_vol = min(rolling_vols)
            expansion_ratio = max_vol / realized_vol
            contraction_ratio = min_vol / realized_vol
        else:
            expansion_ratio = 1.0
            contraction_ratio = 1.0

        # Classified Regime
        regime = self._classify_regime(realized_vol, expansion_ratio, contraction_ratio)

        # Create Observations
        observations = []

        # Realized Vol Observation
        obs_id_rv, hash_rv = compute_observation_id(
            symbol, MicrostructureMetricType.REALIZED_VOLATILITY.value, timestamp, realized_vol, window_seconds
        )
        obs_rv = MicrostructureObservation(
            observation_id=obs_id_rv,
            metric_type=MicrostructureMetricType.REALIZED_VOLATILITY,
            category=ObservationCategory.VOLATILITY,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp,
            value=realized_vol,
            unit="std_log_returns",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_rv,
        )
        observations.append(obs_rv)

        # Volatility Clustering Observation
        obs_id_vc, hash_vc = compute_observation_id(
            symbol, MicrostructureMetricType.VOLATILITY_CLUSTERING.value, timestamp, vol_clustering, window_seconds
        )
        obs_vc = MicrostructureObservation(
            observation_id=obs_id_vc,
            metric_type=MicrostructureMetricType.VOLATILITY_CLUSTERING,
            category=ObservationCategory.VOLATILITY,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp,
            value=vol_clustering,
            unit="autocorr_coeff",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_vc,
        )
        observations.append(obs_vc)

        # Volatility Persistence Observation
        obs_id_vp, hash_vp = compute_observation_id(
            symbol, MicrostructureMetricType.VOLATILITY_PERSISTENCE.value, timestamp, vol_persistence, window_seconds
        )
        obs_vp = MicrostructureObservation(
            observation_id=obs_id_vp,
            metric_type=MicrostructureMetricType.VOLATILITY_PERSISTENCE,
            category=ObservationCategory.VOLATILITY,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp,
            value=vol_persistence,
            unit="decay_coeff",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_vp,
        )
        observations.append(obs_vp)

        # Volatility Expansion Observation
        obs_id_ve, hash_ve = compute_observation_id(
            symbol, MicrostructureMetricType.VOLATILITY_EXPANSION.value, timestamp, expansion_ratio, window_seconds
        )
        obs_ve = MicrostructureObservation(
            observation_id=obs_id_ve,
            metric_type=MicrostructureMetricType.VOLATILITY_EXPANSION,
            category=ObservationCategory.VOLATILITY,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp,
            value=expansion_ratio,
            unit="expansion_ratio",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_ve,
        )
        observations.append(obs_ve)

        # Volatility Contraction Observation
        obs_id_vct, hash_vct = compute_observation_id(
            symbol, MicrostructureMetricType.VOLATILITY_CONTRACTION.value, timestamp, contraction_ratio, window_seconds
        )
        obs_vct = MicrostructureObservation(
            observation_id=obs_id_vct,
            metric_type=MicrostructureMetricType.VOLATILITY_CONTRACTION,
            category=ObservationCategory.VOLATILITY,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp,
            value=contraction_ratio,
            unit="contraction_ratio",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_vct,
        )
        observations.append(obs_vct)

        obs_ids = [o.observation_id for o in observations]

        profile_id, p_hash = compute_volatility_profile_id(
            symbol=symbol,
            timestamp=timestamp,
            window_seconds=window_seconds,
            realized_volatility=realized_vol,
            observation_ids=obs_ids,
        )

        profile = VolatilityProfile(
            profile_id=profile_id,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp,
            window_seconds=window_seconds,
            realized_volatility=realized_vol,
            volatility_clustering_coeff=vol_clustering,
            volatility_persistence=vol_persistence,
            expansion_ratio=expansion_ratio,
            contraction_ratio=contraction_ratio,
            regime=regime,
            observation_ids=obs_ids,
            metadata=meta,
            canonical_hash=p_hash,
        )

        return profile, observations

    def _compute_autocorr(self, series: list[float], lag: int = 1) -> float:
        if len(series) <= lag:
            return 0.0
        n = len(series)
        mean_val = sum(series) / n
        var_val = sum((x - mean_val) ** 2 for x in series)
        if var_val < 1e-12:
            return 0.0
        cov_val = sum((series[i] - mean_val) * (series[i - lag] - mean_val) for i in range(lag, n))
        return cov_val / var_val

    def _classify_regime(
        self, realized_vol: float, expansion_ratio: float, contraction_ratio: float
    ) -> VolatilityRegime:
        if expansion_ratio > 1.8:
            return VolatilityRegime.EXPANDING
        elif contraction_ratio < 0.5:
            return VolatilityRegime.CONTRACTING
        elif realized_vol > 0.05:
            return VolatilityRegime.EXTREME_VOLATILITY
        elif realized_vol > 0.02:
            return VolatilityRegime.HIGH_VOLATILITY
        elif realized_vol < 0.005:
            return VolatilityRegime.LOW_VOLATILITY
        return VolatilityRegime.NORMAL_VOLATILITY

    def _build_fallback(
        self,
        symbol: str,
        index_type: SyntheticIndexType,
        timestamp: str,
        window_seconds: int,
        metadata: dict[str, Any],
    ) -> tuple[VolatilityProfile, list[MicrostructureObservation]]:
        obs_id, o_hash = compute_observation_id(
            symbol, MicrostructureMetricType.REALIZED_VOLATILITY.value, timestamp, 0.0, window_seconds
        )
        obs = MicrostructureObservation(
            observation_id=obs_id,
            metric_type=MicrostructureMetricType.REALIZED_VOLATILITY,
            category=ObservationCategory.VOLATILITY,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp,
            value=0.0,
            unit="std_log_returns",
            window_seconds=window_seconds,
            metadata=metadata,
            canonical_hash=o_hash,
        )
        p_id, p_hash = compute_volatility_profile_id(symbol, timestamp, window_seconds, 0.0, [obs_id])
        prof = VolatilityProfile(
            profile_id=p_id,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp,
            window_seconds=window_seconds,
            realized_volatility=0.0,
            volatility_clustering_coeff=0.0,
            volatility_persistence=0.0,
            expansion_ratio=1.0,
            contraction_ratio=1.0,
            regime=VolatilityRegime.NORMAL_VOLATILITY,
            observation_ids=[obs_id],
            metadata=metadata,
            canonical_hash=p_hash,
        )
        return prof, [obs]
