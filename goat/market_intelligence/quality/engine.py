"""
Project GOAT Phase 4 — Data Quality Engine (`goat.market_intelligence.quality`)

Performs automated 8-point validation on incoming market ticks and candles, rejecting invalid data
and producing detailed DataQualityReports.
"""

from __future__ import annotations

import datetime
from typing import Any, Sequence

from goat.market_intelligence.models.quality import (
    DataQualityCheckResult,
    DataQualityReport,
    QualityIssue,
    QualityIssueReason,
    compute_data_quality_report_id,
)
from goat.market_intelligence.models.tick import RecordedTick
from goat.market_intelligence.persistence.interfaces import IDataQualityRepository
from goat.research.edge.canonical import compute_canonical_sha256


class DataQualityEngine:
    """Institutional Data Quality Engine performing continuous multi-point tick & candle validation."""

    def __init__(
        self,
        repository: IDataQualityRepository | None = None,
        max_allowed_latency_ms: float = 5000.0,
        max_silence_seconds: float = 60.0,
        max_price_jump_ratio: float = 0.5,  # 50% single-tick price jump
    ):
        self.repository = repository
        self.max_allowed_latency_ms = max_allowed_latency_ms
        self.max_silence_seconds = max_silence_seconds
        self.max_price_jump_ratio = max_price_jump_ratio

        # Internal state tracking per symbol: symbol -> last_tick dict
        self._last_ticks: dict[str, dict[str, Any]] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def evaluate_tick(self, raw_payload_or_tick: Any) -> DataQualityCheckResult:
        """Perform 8-point quality check on an incoming tick object or raw dict payload."""
        issues: list[QualityIssue] = []

        # 1. Corrupted Payload Check
        if raw_payload_or_tick is None:
            issues.append(
                QualityIssue(
                    reason=QualityIssueReason.CORRUPTED_PAYLOAD,
                    description="Payload is None",
                    details={"input": "None"},
                )
            )
            return DataQualityCheckResult(passed=False, symbol="UNKNOWN", timestamp=self._now_iso(), issues=issues)

        # Handle RecordedTick or raw payload dict
        if isinstance(raw_payload_or_tick, RecordedTick):
            tick_data = {
                "symbol": raw_payload_or_tick.symbol,
                "timestamp": raw_payload_or_tick.timestamp,
                "bid": raw_payload_or_tick.bid,
                "ask": raw_payload_or_tick.ask,
                "mid_price": raw_payload_or_tick.mid_price,
                "spread": raw_payload_or_tick.spread,
                "latency_ms": raw_payload_or_tick.latency_ms,
                "sequence_number": raw_payload_or_tick.sequence_number,
            }
        elif isinstance(raw_payload_or_tick, dict):
            symbol = str(raw_payload_or_tick.get("symbol", raw_payload_or_tick.get("tick", {}).get("symbol", ""))).strip().upper()
            if not symbol:
                issues.append(
                    QualityIssue(
                        reason=QualityIssueReason.CORRUPTED_PAYLOAD,
                        description="Missing required field 'symbol'",
                        details=raw_payload_or_tick,
                    )
                )
                return DataQualityCheckResult(passed=False, symbol="UNKNOWN", timestamp=self._now_iso(), issues=issues)

            bid = raw_payload_or_tick.get("bid", raw_payload_or_tick.get("tick", {}).get("bid"))
            ask = raw_payload_or_tick.get("ask", raw_payload_or_tick.get("tick", {}).get("ask"))
            price = raw_payload_or_tick.get("mid_price", raw_payload_or_tick.get("price", raw_payload_or_tick.get("quote", raw_payload_or_tick.get("tick", {}).get("quote"))))
            ts = raw_payload_or_tick.get("timestamp", raw_payload_or_tick.get("time", self._now_iso()))
            seq = raw_payload_or_tick.get("sequence_number", raw_payload_or_tick.get("seq", 0))
            lat = raw_payload_or_tick.get("latency_ms", 0.0)

            tick_data = {
                "symbol": symbol,
                "timestamp": str(ts),
                "bid": float(bid) if bid is not None else (float(price) - 0.01 if price is not None else None),
                "ask": float(ask) if ask is not None else (float(price) + 0.01 if price is not None else None),
                "mid_price": float(price) if price is not None else (float(bid) + float(ask)) / 2.0 if bid and ask else None,
                "spread": (float(ask) - float(bid)) if ask and bid else 0.0,
                "latency_ms": float(lat) if lat is not None else 0.0,
                "sequence_number": int(seq) if seq is not None else 0,
            }
        else:
            issues.append(
                QualityIssue(
                    reason=QualityIssueReason.CORRUPTED_PAYLOAD,
                    description=f"Invalid payload type '{type(raw_payload_or_tick).__name__}'",
                    details={"type": type(raw_payload_or_tick).__name__},
                )
            )
            return DataQualityCheckResult(passed=False, symbol="UNKNOWN", timestamp=self._now_iso(), issues=issues)

        symbol = tick_data["symbol"]
        ts_str = tick_data["timestamp"]
        bid = tick_data["bid"]
        ask = tick_data["ask"]
        mid = tick_data["mid_price"]
        seq = tick_data["sequence_number"]
        lat = tick_data["latency_ms"]

        # 2. Impossible Prices Check
        if mid is None or mid <= 0.0 or bid is None or bid <= 0.0 or ask is None or ask <= 0.0:
            issues.append(
                QualityIssue(
                    reason=QualityIssueReason.IMPOSSIBLE_PRICE,
                    description=f"Non-positive or missing prices (mid={mid}, bid={bid}, ask={ask})",
                    details={"mid": mid, "bid": bid, "ask": ask},
                )
            )

        # 3. Negative Spread Check
        if ask is not None and bid is not None and ask < bid:
            issues.append(
                QualityIssue(
                    reason=QualityIssueReason.NEGATIVE_SPREAD,
                    description=f"Negative spread detected (ask={ask} < bid={bid})",
                    details={"ask": ask, "bid": bid, "spread": ask - bid},
                )
            )

        # 4. Latency Anomaly Check
        if lat > self.max_allowed_latency_ms:
            issues.append(
                QualityIssue(
                    reason=QualityIssueReason.LATENCY_ANOMALY,
                    description=f"Latency {lat:.1f}ms exceeds maximum allowed threshold of {self.max_allowed_latency_ms}ms",
                    details={"latency_ms": lat, "threshold": self.max_allowed_latency_ms},
                )
            )

        # Compare with last recorded tick for symbol
        last = self._last_ticks.get(symbol)
        if last:
            # 5. Duplicate Timestamp Check
            if last["timestamp"] == ts_str and last["sequence_number"] == seq:
                issues.append(
                    QualityIssue(
                        reason=QualityIssueReason.DUPLICATE_TIMESTAMP,
                        description=f"Duplicate timestamp and sequence detected for {symbol}: {ts_str}",
                        details={"timestamp": ts_str, "sequence_number": seq},
                    )
                )

            # 6. Out-of-Order Tick Check
            if seq > 0 and last["sequence_number"] > 0 and seq < last["sequence_number"]:
                issues.append(
                    QualityIssue(
                        reason=QualityIssueReason.OUT_OF_ORDER_TICK,
                        description=f"Out-of-order sequence index: current {seq} < previous {last['sequence_number']}",
                        details={"current_seq": seq, "last_seq": last["sequence_number"]},
                    )
                )
            elif ts_str < last["timestamp"]:
                issues.append(
                    QualityIssue(
                        reason=QualityIssueReason.OUT_OF_ORDER_TICK,
                        description=f"Out-of-order timestamp: current {ts_str} < previous {last['timestamp']}",
                        details={"current_timestamp": ts_str, "last_timestamp": last["timestamp"]},
                    )
                )

            # 7. Time Gap / Provider Silence Check
            try:
                t1 = datetime.datetime.fromisoformat(last["timestamp"].replace("Z", "+00:00"))
                t2 = datetime.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                delta_sec = (t2 - t1).total_seconds()
                if delta_sec > self.max_silence_seconds:
                    issues.append(
                        QualityIssue(
                            reason=QualityIssueReason.TIME_GAP,
                            description=f"Time gap / silence of {delta_sec:.1f}s exceeds threshold of {self.max_silence_seconds}s",
                            details={"delta_sec": delta_sec, "threshold": self.max_silence_seconds},
                        )
                    )
            except Exception:
                pass

            # Extreme Price Jump Check (Impossible Price variant)
            if mid is not None and last["mid_price"] is not None and last["mid_price"] > 0:
                jump_ratio = abs(mid - last["mid_price"]) / last["mid_price"]
                if jump_ratio > self.max_price_jump_ratio:
                    issues.append(
                        QualityIssue(
                            reason=QualityIssueReason.IMPOSSIBLE_PRICE,
                            description=f"Extreme price jump of {jump_ratio*100:.1f}% exceeds max ratio of {self.max_price_jump_ratio*100:.1f}%",
                            details={"price": mid, "last_price": last["mid_price"], "jump_ratio": jump_ratio},
                        )
                    )

        # Update symbol stats and state
        passed = (len(issues) == 0)
        self._record_stat(symbol, passed, issues)

        if passed:
            self._last_ticks[symbol] = {
                "timestamp": ts_str,
                "sequence_number": seq,
                "mid_price": mid,
            }

        return DataQualityCheckResult(
            passed=passed,
            symbol=symbol,
            timestamp=ts_str,
            issues=issues,
        )

    def generate_report(self, symbol: str) -> DataQualityReport:
        """Generate aggregate DataQualityReport for a symbol."""
        sym_str = symbol.upper()
        stats = self._stats.get(sym_str, {"total": 0, "valid": 0, "rejected": 0})
        total = stats["total"]
        valid = stats["valid"]
        rejected = stats["rejected"]
        pass_rate = (valid / total) if total > 0 else 1.0

        breakdown: dict[str, int] = {}
        for key, val in stats.items():
            if key.startswith("issue_"):
                reason_name = key[6:]
                breakdown[reason_name] = val

        ts_now = self._now_iso()
        report_id, canon_hash = compute_data_quality_report_id(
            symbol=sym_str,
            timestamp=ts_now,
            total_ticks_checked=total,
            rejected_ticks_count=rejected,
            pass_rate=pass_rate,
        )

        checksum = compute_canonical_sha256(
            {
                "pass_rate": pass_rate,
                "rejected_ticks_count": rejected,
                "symbol": sym_str,
                "total_ticks_checked": total,
            }
        )

        report = DataQualityReport(
            report_id=report_id,
            symbol=sym_str,
            timestamp=ts_now,
            total_ticks_checked=total,
            valid_ticks_count=valid,
            rejected_ticks_count=rejected,
            pass_rate=pass_rate,
            issues_breakdown=breakdown,
            checksum=checksum,
            metadata={"generator": "DataQualityEngine"},
            canonical_hash=canon_hash,
        )

        if self.repository:
            self.repository.save_report(report)

        return report

    def _record_stat(self, symbol: str, passed: bool, issues: Sequence[QualityIssue]) -> None:
        sym_str = symbol.upper()
        if sym_str not in self._stats:
            self._stats[sym_str] = {"total": 0, "valid": 0, "rejected": 0}

        st = self._stats[sym_str]
        st["total"] += 1
        if passed:
            st["valid"] += 1
        else:
            st["rejected"] += 1
            for issue in issues:
                key = f"issue_{issue.reason.value}"
                st[key] = st.get(key, 0) + 1

    @staticmethod
    def _now_iso() -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()
