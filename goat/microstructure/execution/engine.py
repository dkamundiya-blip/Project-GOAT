"""
Project GOAT v0.9 — Deriv Market Microstructure Execution Profiling Engine
"""

import math
from typing import Any

from goat.microstructure.core.canonical import (
    compute_execution_profile_id,
    compute_observation_id,
)
from goat.microstructure.core.enums import (
    ExecutionQualityRating,
    MicrostructureMetricType,
    ObservationCategory,
    SyntheticIndexType,
)
from goat.microstructure.core.models import (
    ExecutionProfile,
    MicrostructureObservation,
)


class ExecutionProfilingEngine:
    """Quantitative Research Engine for Execution Profiling.

    Measures:
    • Execution latency (mean, median, p95 millisecond metrics)
    • Fill timing (fill confirmation delay ms)
    • Execution consistency (1 - CV of latency)
    • Broker response metrics (sample statistics across websocket/API calls)
    """

    def analyze_latencies(
        self,
        symbol: str,
        index_type: SyntheticIndexType | str,
        latencies_ms: list[float],
        fill_times_ms: list[float] | None = None,
        timestamp_str: str = "2026-01-01T00:00:00Z",
        window_seconds: int = 300,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[ExecutionProfile, list[MicrostructureObservation]]:
        """Analyze measured broker interaction latencies and fill metrics."""
        if isinstance(index_type, str):
            index_type = SyntheticIndexType(index_type)

        meta = dict(metadata or {})

        if not latencies_ms:
            return self._build_fallback(symbol, index_type, timestamp_str, window_seconds, meta)

        sample_count = len(latencies_ms)
        sorted_lats = sorted(latencies_ms)

        # 1. Mean Latency
        mean_lat = sum(sorted_lats) / sample_count

        # 2. Median Latency
        mid = sample_count // 2
        if sample_count % 2 == 1:
            median_lat = sorted_lats[mid]
        else:
            median_lat = (sorted_lats[mid - 1] + sorted_lats[mid]) / 2.0

        # 3. P95 Latency
        p95_idx = int(math.ceil(0.95 * sample_count)) - 1
        p95_lat = sorted_lats[max(0, min(sample_count - 1, p95_idx))]

        # 4. Fill Time MS
        if fill_times_ms and len(fill_times_ms) > 0:
            mean_fill_time = sum(fill_times_ms) / len(fill_times_ms)
        else:
            mean_fill_time = mean_lat * 1.1

        # 5. Consistency Score (1 - Coefficient of Variation)
        if sample_count > 1 and mean_lat > 1e-6:
            var_lat = sum((l - mean_lat) ** 2 for l in sorted_lats) / sample_count
            stdev_lat = math.sqrt(var_lat)
            cv = stdev_lat / mean_lat
            consistency_score = min(1.0, max(0.0, 1.0 - cv))
        else:
            consistency_score = 1.0

        # Quality Rating
        rating = self._classify_rating(mean_lat, p95_lat, consistency_score)

        observations = []

        # Latency Observation
        obs_id_el, hash_el = compute_observation_id(
            symbol, MicrostructureMetricType.EXECUTION_LATENCY.value, timestamp_str, mean_lat, window_seconds
        )
        obs_el = MicrostructureObservation(
            observation_id=obs_id_el,
            metric_type=MicrostructureMetricType.EXECUTION_LATENCY,
            category=ObservationCategory.EXECUTION,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=mean_lat,
            unit="milliseconds",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_el,
        )
        observations.append(obs_el)

        # Fill Timing Observation
        obs_id_ft, hash_ft = compute_observation_id(
            symbol, MicrostructureMetricType.FILL_TIMING.value, timestamp_str, mean_fill_time, window_seconds
        )
        obs_ft = MicrostructureObservation(
            observation_id=obs_id_ft,
            metric_type=MicrostructureMetricType.FILL_TIMING,
            category=ObservationCategory.EXECUTION,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=mean_fill_time,
            unit="milliseconds",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_ft,
        )
        observations.append(obs_ft)

        # Execution Consistency Observation
        obs_id_ec, hash_ec = compute_observation_id(
            symbol, MicrostructureMetricType.EXECUTION_CONSISTENCY.value, timestamp_str, consistency_score, window_seconds
        )
        obs_ec = MicrostructureObservation(
            observation_id=obs_id_ec,
            metric_type=MicrostructureMetricType.EXECUTION_CONSISTENCY,
            category=ObservationCategory.EXECUTION,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=consistency_score,
            unit="consistency_score",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_ec,
        )
        observations.append(obs_ec)

        # Broker Response Metric Observation
        obs_id_br, hash_br = compute_observation_id(
            symbol, MicrostructureMetricType.BROKER_RESPONSE_METRIC.value, timestamp_str, p95_lat, window_seconds
        )
        obs_br = MicrostructureObservation(
            observation_id=obs_id_br,
            metric_type=MicrostructureMetricType.BROKER_RESPONSE_METRIC,
            category=ObservationCategory.EXECUTION,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=p95_lat,
            unit="p95_milliseconds",
            window_seconds=window_seconds,
            metadata=meta,
            canonical_hash=hash_br,
        )
        observations.append(obs_br)

        obs_ids = [o.observation_id for o in observations]

        prof_id, p_hash = compute_execution_profile_id(
            symbol=symbol,
            timestamp=timestamp_str,
            window_seconds=window_seconds,
            mean_latency_ms=mean_lat,
            sample_count=sample_count,
            observation_ids=obs_ids,
        )

        profile = ExecutionProfile(
            profile_id=prof_id,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            window_seconds=window_seconds,
            sample_count=sample_count,
            mean_latency_ms=mean_lat,
            median_latency_ms=median_lat,
            p95_latency_ms=p95_lat,
            fill_time_ms=mean_fill_time,
            consistency_score=consistency_score,
            rating=rating,
            observation_ids=obs_ids,
            metadata=meta,
            canonical_hash=p_hash,
        )

        return profile, observations

    def _classify_rating(self, mean_lat: float, p95_lat: float, consistency: float) -> ExecutionQualityRating:
        if mean_lat <= 50.0 and p95_lat <= 100.0 and consistency >= 0.8:
            return ExecutionQualityRating.EXCELLENT
        elif mean_lat <= 150.0 and p95_lat <= 300.0 and consistency >= 0.6:
            return ExecutionQualityRating.NORMAL
        elif mean_lat <= 400.0 or p95_lat <= 800.0:
            return ExecutionQualityRating.DEGRADED
        return ExecutionQualityRating.POOR

    def _build_fallback(
        self,
        symbol: str,
        index_type: SyntheticIndexType,
        timestamp_str: str,
        window_seconds: int,
        metadata: dict[str, Any],
    ) -> tuple[ExecutionProfile, list[MicrostructureObservation]]:
        obs_id, o_hash = compute_observation_id(
            symbol, MicrostructureMetricType.EXECUTION_LATENCY.value, timestamp_str, 0.0, window_seconds
        )
        obs = MicrostructureObservation(
            observation_id=obs_id,
            metric_type=MicrostructureMetricType.EXECUTION_LATENCY,
            category=ObservationCategory.EXECUTION,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            value=0.0,
            unit="milliseconds",
            window_seconds=window_seconds,
            metadata=metadata,
            canonical_hash=o_hash,
        )
        p_id, p_hash = compute_execution_profile_id(symbol, timestamp_str, window_seconds, 0.0, 0, [obs_id])
        prof = ExecutionProfile(
            profile_id=p_id,
            symbol=symbol,
            index_type=index_type,
            timestamp=timestamp_str,
            window_seconds=window_seconds,
            sample_count=0,
            mean_latency_ms=0.0,
            median_latency_ms=0.0,
            p95_latency_ms=0.0,
            fill_time_ms=0.0,
            consistency_score=1.0,
            rating=ExecutionQualityRating.NORMAL,
            observation_ids=[obs_id],
            metadata=metadata,
            canonical_hash=p_hash,
        )
        return prof, [obs]
