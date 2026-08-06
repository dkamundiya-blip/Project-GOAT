"""
Project GOAT v0.8 — Market Quality Engine

Evaluates replay integrity, stream health telemetry, feed latency, missing packet gaps,
and validation checksum consistency to produce a deterministic MarketQualityAssessment (MQA_<HEX16>).
"""

from __future__ import annotations

from typing import Sequence

from goat.marketdata.core.enums import SafetyGateStatus, StreamConnectionStatus
from goat.marketdata.core.models import MarketGap, MarketStreamState
from goat.marketstate.core.canonical import compute_quality_id
from goat.marketstate.core.enums import QualityState
from goat.marketstate.core.models import MarketQualityAssessment
from goat.research.edge.canonical import compute_canonical_sha256


class MarketQualityEngine:
    """Engine responsible for consolidating feed, stream, and validation quality assessments."""

    def __init__(self):
        pass

    def evaluate_quality(
        self,
        symbol: str,
        stream_state: MarketStreamState | None = None,
        recent_gaps: Sequence[MarketGap] = (),
        safety_status: SafetyGateStatus = SafetyGateStatus.HEALTHY,
        replay_integrity_passed: bool = True,
    ) -> MarketQualityAssessment:
        """Evaluate overall market data quality for a symbol."""
        sym = symbol.strip().upper()
        reasons: list[str] = []

        # 1. Stream Health Quality
        if not stream_state or stream_state.connection_status in (StreamConnectionStatus.DISCONNECTED, StreamConnectionStatus.TERMINATED):
            stream_qual = QualityState.INVALID
            reasons.append("Stream is disconnected or unavailable")
        elif stream_state.connection_status == StreamConnectionStatus.RECONNECTING:
            stream_qual = QualityState.POOR
            reasons.append("Stream is currently reconnecting")
        elif stream_state.connection_status == StreamConnectionStatus.DEGRADED:
            stream_qual = QualityState.ACCEPTABLE
            reasons.append("Stream is operating in degraded state")
        else:
            stream_qual = QualityState.EXCELLENT

        # 2. Latency Quality
        latency = stream_state.latency_ms if stream_state else 0.0
        if latency <= 50.0:
            lat_qual = QualityState.EXCELLENT
        elif latency <= 200.0:
            lat_qual = QualityState.GOOD
        elif latency <= 1000.0:
            lat_qual = QualityState.ACCEPTABLE
            reasons.append(f"Elevated latency ({latency:.1f}ms)")
        else:
            lat_qual = QualityState.POOR
            reasons.append(f"Excessive latency ({latency:.1f}ms)")

        # 3. Data Validation Quality (Gaps & Drops)
        dropped = stream_state.packets_dropped if stream_state else 0
        gap_count = len(recent_gaps)
        if gap_count == 0 and dropped == 0:
            data_qual = QualityState.EXCELLENT
        elif gap_count <= 2 and dropped <= 5:
            data_qual = QualityState.GOOD
        elif gap_count <= 5 and dropped <= 20:
            data_qual = QualityState.ACCEPTABLE
            reasons.append(f"Minor data gaps detected ({gap_count} gaps, {dropped} dropped packets)")
        else:
            data_qual = QualityState.POOR
            reasons.append(f"Significant data gaps detected ({gap_count} gaps, {dropped} dropped packets)")

        # 4. Replay Quality
        replay_qual = QualityState.EXCELLENT if replay_integrity_passed else QualityState.INVALID
        if not replay_integrity_passed:
            reasons.append("Offline replay checksum integrity check failed")

        # 5. Overall Consolidated Quality
        if stream_qual == QualityState.INVALID or replay_qual == QualityState.INVALID or safety_status == SafetyGateStatus.UNAVAILABLE:
            overall = QualityState.INVALID
        elif stream_qual == QualityState.POOR or data_qual == QualityState.POOR or lat_qual == QualityState.POOR:
            overall = QualityState.POOR
        elif stream_qual == QualityState.ACCEPTABLE or data_qual == QualityState.ACCEPTABLE or lat_qual == QualityState.ACCEPTABLE or safety_status == SafetyGateStatus.DEGRADED:
            overall = QualityState.ACCEPTABLE
        elif data_qual == QualityState.GOOD or lat_qual == QualityState.GOOD:
            overall = QualityState.GOOD
        else:
            overall = QualityState.EXCELLENT

        if not reasons:
            reasons.append("All stream health, latency, gap detection, and replay checks passed nominal standards")

        explanation = f"Overall Quality: {overall.value}. Factors: " + "; ".join(reasons)

        mqa_id, canonical_hash = compute_quality_id(sym, data_qual.value, stream_qual.value, overall.value)

        return MarketQualityAssessment(
            assessment_id=mqa_id,
            symbol=sym,
            data_quality=data_qual,
            stream_health=stream_qual,
            latency_quality=lat_qual,
            replay_quality=replay_qual,
            overall_quality=overall,
            explanation=explanation,
            metadata={"latency_ms": latency, "dropped_packets": dropped, "gaps_count": gap_count},
            canonical_hash=canonical_hash,
        )
