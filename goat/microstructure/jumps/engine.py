"""
Project GOAT v0.9 — Deriv Market Microstructure Jump Profiling Engine
"""

import math
from typing import Any

from goat.microstructure.core.canonical import (
    compute_jump_profile_id,
    compute_observation_id,
)
from goat.microstructure.core.enums import (
    JumpDirection,
    MicrostructureMetricType,
    ObservationCategory,
    SyntheticIndexType,
)
from goat.microstructure.core.models import (
    JumpProfile,
    MicrostructureObservation,
)


class JumpProfilingEngine:
    """Quantitative Research Engine for Jump Profiling.

    Measures:
    • Jump frequency
    • Jump magnitude
    • Jump spacing
    • Jump persistence
    • Jump clustering (Fano factor / variance-to-mean ratio of jump counts)
    """

    def analyze_series(
        self,
        symbol: str,
        index_type: SyntheticIndexType | str,
        prices: list[float],
        timestamps: list[float] | None = None,
        timestamp_str: str = "2026-01-01T00:00:00Z",
        window_seconds: int = 300,
        jump_threshold_std: float = 3.0,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[JumpProfile, list[MicrostructureObservation]]:
        """Analyze a series of price data for jump dynamics."""
        if isinstance(index_type, str):
            index_type = SyntheticIndexType(index_type)

        meta = dict(metadata or {})

        if len(prices) < 2:
            return self._build_fallback(symbol, index_type, timestamp_str, window_seconds, meta)

        if timestamps is None or len(timestamps) != len(prices):
            timestamps = [float(i) for i in range(len(prices))]

        # Step changes / returns
        diffs = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        time_diffs = [max(0.1, timestamps[i] - timestamps[i - 1]) for i in range(1, len(prices))]

        if not diffs:
            return self._build_fallback(symbol, index_type, timestamp_str, window_seconds, meta)

        mean_diff = sum(diffs) / len(diffs)
        std_diff = math.sqrt(sum((d - mean_diff) ** 2 for d in diffs) / len(diffs))

        # Detect jumps exceeding threshold
        threshold = max(1e-6, std_diff * jump_threshold_std)
        jumps = []
        up_count, down_count = 0, 0

        for i, d in enumerate(diffs):
            if abs(d) >= threshold:
                jumps.append({
                    "index": i,
                    "magnitude": abs(d),
                    "raw_diff": d,
                    "time": timestamps[i + 1],
                    "dt": time_diffs[i],
                })
                if d > 0:
                    up_count += 1
                else:
                    down_count += 1

        jump_count = len(jumps)
        total_time_min = max(0.1, (timestamps[-1] - timestamps[0])) / 60.0
        jump_frequency = jump_count / total_time_min

        if jump_count > 0:
            magnitudes = [j["magnitude"] for j in jumps]
            mean_jump_mag = sum(magnitudes) / jump_count
            max_jump_mag = max(magnitudes)

            # Dominant Direction
            if up_count > down_count * 1.5:
                dominant_dir = JumpDirection.UPWARD
            elif down_count > up_count * 1.5:
                dominant_dir = JumpDirection.DOWNWARD
            else:
                dominant_dir = JumpDirection.NEUTRAL

            # Jump spacing (seconds between consecutive jumps)
            spacings = []
            for k in range(1, jump_count):
                spacings.append(jumps[k]["time"] - jumps[k - 1]["time"])
            mean_spacing = sum(spacings) / len(spacings) if spacings else (window_seconds / max(1, jump_count))

            # Jump persistence (autocorrelation of jump sizes)
            if len(magnitudes) > 1:
                m_mean = sum(magnitudes) / len(magnitudes)
                m_var = sum((m - m_mean) ** 2 for m in magnitudes)
                if m_var > 1e-12:
                    cov = sum((magnitudes[k] - m_mean) * (magnitudes[k - 1] - m_mean) for k in range(1, len(magnitudes)))
                    jump_persistence = cov / m_var
                else:
                    jump_persistence = 0.0
            else:
                jump_persistence = 0.0

            # Jump clustering (Fano factor across sub-windows)
            num_bins = min(10, max(2, len(prices) // 20))
            bin_counts = [0] * num_bins
            t_min, t_max = timestamps[0], timestamps[-1]
            bin_size = max(0.001, (t_max - t_min) / num_bins)
            for j in jumps:
                bin_idx = min(num_bins - 1, int((j["time"] - t_min) / bin_size))
                bin_counts[bin_idx] += 1

            b_mean = sum(bin_counts) / len(bin_counts)
            b_var = sum((c - b_mean) ** 2 for c in bin_counts) / len(bin_counts)
            clustering_index = (b_var / b_mean) if b_mean > 0 else 1.0

        else:
            mean_jump_mag = 0.0
            max_jump_mag = 0.0
            mean_spacing = float(window_seconds)
            jump_persistence = 0.0
            clustering_index = 0.0
            dominant_dir = JumpDirection.NEUTRAL

        observations = []

        # Jump Frequency Observation
        obs_id_jf, hash_jf = compute_observation_id(
            symbol, MicrostructureMetricType.JUMP_FREQUENCY.value, timestamp_str, jump_frequency, window_seconds
        )
        obs_jf = MicrostructureObservation(
            observation_id=obs_id_jf,
            metric_type=MicrostructureMetricType.JUMP_FREQUENCY,
            category=ObservationCategory.JUMP,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=jump_frequency,
            unit="jumps_per_minute",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_jf,
        )
        observations.append(obs_jf)

        # Jump Magnitude Observation
        obs_id_jm, hash_jm = compute_observation_id(
            symbol, MicrostructureMetricType.JUMP_MAGNITUDE.value, timestamp_str, mean_jump_mag, window_seconds
        )
        obs_jm = MicrostructureObservation(
            observation_id=obs_id_jm,
            metric_type=MicrostructureMetricType.JUMP_MAGNITUDE,
            category=ObservationCategory.JUMP,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=mean_jump_mag,
            unit="price_delta",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_jm,
        )
        observations.append(obs_jm)

        # Jump Spacing Observation
        obs_id_js, hash_js = compute_observation_id(
            symbol, MicrostructureMetricType.JUMP_SPACING.value, timestamp_str, mean_spacing, window_seconds
        )
        obs_js = MicrostructureObservation(
            observation_id=obs_id_js,
            metric_type=MicrostructureMetricType.JUMP_SPACING,
            category=ObservationCategory.JUMP,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=mean_spacing,
            unit="seconds",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_js,
        )
        observations.append(obs_js)

        # Jump Persistence Observation
        obs_id_jp, hash_jp = compute_observation_id(
            symbol, MicrostructureMetricType.JUMP_PERSISTENCE.value, timestamp_str, jump_persistence, window_seconds
        )
        obs_jp = MicrostructureObservation(
            observation_id=obs_id_jp,
            metric_type=MicrostructureMetricType.JUMP_PERSISTENCE,
            category=ObservationCategory.JUMP,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=jump_persistence,
            unit="decay_factor",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_jp,
        )
        observations.append(obs_jp)

        # Jump Clustering Observation
        obs_id_jc, hash_jc = compute_observation_id(
            symbol, MicrostructureMetricType.JUMP_CLUSTERING.value, timestamp_str, clustering_index, window_seconds
        )
        obs_jc = MicrostructureObservation(
            observation_id=obs_id_jc,
            metric_type=MicrostructureMetricType.JUMP_CLUSTERING,
            category=ObservationCategory.JUMP,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=clustering_index,
            unit="fano_factor",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_jc,
        )
        observations.append(obs_jc)

        obs_ids = [o.observation_id for o in observations]

        prof_id, p_hash = compute_jump_profile_id(
            symbol=symbol,
            timestamp=timestamp_str,
            window_seconds=window_seconds,
            jump_count=jump_count,
            mean_jump_magnitude=mean_jump_mag,
            observation_ids=obs_ids,
        )

        profile = JumpProfile(
            profile_id=prof_id,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            window_seconds=window_seconds,
            jump_count=jump_count,
            jump_frequency=jump_frequency,
            mean_jump_magnitude=mean_jump_mag,
            max_jump_magnitude=max_jump_mag,
            mean_jump_spacing_sec=mean_spacing,
            jump_persistence=jump_persistence,
            jump_clustering_index=clustering_index,
            dominant_direction=dominant_dir,
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
    ) -> tuple[JumpProfile, list[MicrostructureObservation]]:
        obs_id, o_hash = compute_observation_id(
            symbol, MicrostructureMetricType.JUMP_FREQUENCY.value, timestamp_str, 0.0, window_seconds
        )
        obs = MicrostructureObservation(
            observation_id=obs_id,
            metric_type=MicrostructureMetricType.JUMP_FREQUENCY,
            category=ObservationCategory.JUMP,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=0.0,
            unit="jumps_per_minute",
            window_seconds=window_seconds,
            metadata=metadata,
            canonical_hash=o_hash,
        )
        p_id, p_hash = compute_jump_profile_id(symbol, timestamp_str, window_seconds, 0, 0.0, [obs_id])
        prof = JumpProfile(
            profile_id=p_id,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            window_seconds=window_seconds,
            jump_count=0,
            jump_frequency=0.0,
            mean_jump_magnitude=0.0,
            max_jump_magnitude=0.0,
            mean_jump_spacing_sec=float(window_seconds),
            jump_persistence=0.0,
            jump_clustering_index=0.0,
            dominant_direction=JumpDirection.NEUTRAL,
            observation_ids=[obs_id],
            metadata=metadata,
            canonical_hash=p_hash,
        )
        return prof, [obs]
