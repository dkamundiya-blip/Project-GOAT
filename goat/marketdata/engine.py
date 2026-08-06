"""
Project GOAT v0.8 — Live Market Data Engine Coordinator

Central engine integrating:
- Ingestion Engine (MarketIngestionEngine)
- Stream Engine (MarketStreamEngine)
- Validation Engine (MarketValidationEngine)
- Gap Detection Engine (MarketGapDetectionEngine)
- Replay Engine (MarketReplayEngine)
- Production Safety Gate (MarketStreamSafetyGate)
- In-memory Buffer (MarketDataBuffer)
- SQLite Repositories
"""

from __future__ import annotations

import datetime
import sqlite3
from typing import Any
from pydantic import BaseModel, Field

from goat.marketdata.core.canonical import compute_report_id
from goat.marketdata.core.enums import SafetyGateStatus
from goat.marketdata.core.models import (
    MarketCandle,
    MarketGap,
    MarketStreamState,
    MarketTick,
    ReplaySnapshot,
)
from goat.marketdata.gap.engine import MarketGapDetectionEngine
from goat.marketdata.ingestion.engine import IngestionResult, MarketIngestionEngine
from goat.marketdata.persistence.repository import (
    MarketCandleRepository,
    MarketGapRepository,
    MarketReportRepository,
    MarketStreamRepository,
    MarketTickRepository,
    ReplaySnapshotRepository,
)
from goat.marketdata.replay.engine import MarketReplayEngine, ReplayResult
from goat.marketdata.reporting.reports import (
    MarketDataExecutiveReport,
    MarketStreamReport,
    MarketTickReport,
)
from goat.marketdata.safety import MarketStreamSafetyGate, SafetyGateResult
from goat.marketdata.storage.buffer import MarketDataBuffer
from goat.marketdata.stream.engine import MarketStreamEngine
from goat.marketdata.validation.engine import MarketValidationEngine, ValidationResult
from goat.research.edge.canonical import compute_canonical_sha256


class ProcessTickOutput(BaseModel):
    """Immutable result from LiveMarketDataEngine processing a raw tick."""

    ingestion_success: bool = Field(..., description="True if raw tick was ingested and parsed")
    validation_success: bool = Field(..., description="True if tick passed validation checks")
    tick: MarketTick | None = Field(default=None, description="Normalized MarketTick if valid")
    gap_detected: MarketGap | None = Field(default=None, description="MarketGap record if gap was detected")
    safety_status: SafetyGateStatus = Field(..., description="Current safety status of stream")
    rejection_reason: str | None = Field(default=None, description="Reason if tick was rejected")

    class Config:
        frozen = True
        extra = "forbid"


class LiveMarketDataEngine:
    """Coordinator engine managing the entire live market data lifecycle."""

    def __init__(
        self,
        db_conn: sqlite3.Connection | None = None,
        default_broker: str = "DERIV",
    ):
        self.broker = default_broker.strip().upper()
        self.db_conn = db_conn

        # Instantiate Sub-engines
        self.ingestion_engine = MarketIngestionEngine(default_broker=self.broker)
        self.stream_engine = MarketStreamEngine(broker=self.broker)
        self.validation_engine = MarketValidationEngine()
        self.gap_engine = MarketGapDetectionEngine()
        self.replay_engine = MarketReplayEngine()
        self.safety_gate = MarketStreamSafetyGate()
        self.buffer = MarketDataBuffer()

        # Repositories
        if db_conn:
            self.tick_repo = MarketTickRepository(db_conn)
            self.candle_repo = MarketCandleRepository(db_conn)
            self.stream_repo = MarketStreamRepository(db_conn)
            self.gap_repo = MarketGapRepository(db_conn)
            self.replay_repo = ReplaySnapshotRepository(db_conn)
            self.report_repo = MarketReportRepository(db_conn)
        else:
            self.tick_repo = None
            self.candle_repo = None
            self.stream_repo = None
            self.gap_repo = None
            self.replay_repo = None
            self.report_repo = None

        self._sequence_counters: dict[str, int] = {}
        self._total_ticks_ingested = 0
        self._total_candles_built = 0
        self._total_gaps_detected = 0

    def process_raw_tick(
        self,
        raw_payload: dict[str, Any],
        source_latency: float = 0.0,
    ) -> ProcessTickOutput:
        """Process a raw tick payload through the entire pipeline: Ingestion -> Stream -> Validation -> Gap -> Safety -> Storage."""

        sym = str(
            raw_payload.get("symbol", raw_payload.get("tick", {}).get("symbol", "UNKNOWN"))
            if isinstance(raw_payload.get("tick"), dict)
            else raw_payload.get("symbol", "UNKNOWN")
        ).strip().upper()

        seq = self._sequence_counters.get(sym, 0) + 1

        # 1. Ingestion
        ingest_res: IngestionResult = self.ingestion_engine.process_raw_tick(
            raw_data=raw_payload,
            sequence_number=seq,
            source_latency=source_latency,
        )

        if not ingest_res.success or ingest_res.tick is None:
            self.stream_engine.record_packet_dropped(sym, reason="INGESTION_FAILED")
            stream_state = self.stream_engine.get_or_create_stream_state(sym)
            safety_res = self.safety_gate.evaluate_stream(stream_state)
            return ProcessTickOutput(
                ingestion_success=False,
                validation_success=False,
                tick=None,
                gap_detected=None,
                safety_status=safety_res.status,
                rejection_reason=ingest_res.rejection_reason,
            )

        tick = ingest_res.tick

        # 2. Validation
        val_res: ValidationResult = self.validation_engine.validate_tick(tick)
        if not val_res.is_valid:
            self.stream_engine.record_packet_dropped(sym, reason=val_res.rule_breached or "VALIDATION_FAILED")
            stream_state = self.stream_engine.get_or_create_stream_state(sym)
            safety_res = self.safety_gate.evaluate_stream(stream_state)
            return ProcessTickOutput(
                ingestion_success=True,
                validation_success=False,
                tick=tick,
                gap_detected=None,
                safety_status=safety_res.status,
                rejection_reason=val_res.rejection_reason,
            )

        # Update sequence counter
        self._sequence_counters[sym] = seq
        self._total_ticks_ingested += 1

        # 3. Stream Telemetry
        stream_state = self.stream_engine.record_packet_received(
            symbol=sym,
            latency_ms=source_latency,
            timestamp=tick.timestamp,
        )

        # 4. Gap Detection
        gap = self.gap_engine.check_tick(tick)
        if gap:
            self._total_gaps_detected += 1
            if self.gap_repo:
                self.gap_repo.save(gap)

        # 5. Buffer & Storage
        self.buffer.append_tick(tick)
        if self.tick_repo:
            self.tick_repo.save(tick)
        if self.stream_repo:
            self.stream_repo.save(stream_state)

        # 6. Safety Gate
        safety_res = self.safety_gate.evaluate_stream(stream_state)

        return ProcessTickOutput(
            ingestion_success=True,
            validation_success=True,
            tick=tick,
            gap_detected=gap,
            safety_status=safety_res.status,
            rejection_reason=None,
        )

    def process_raw_candle(self, raw_payload: dict[str, Any]) -> IngestionResult:
        """Process a raw candle payload."""
        ingest_res = self.ingestion_engine.process_raw_candle(raw_payload)
        if ingest_res.success and ingest_res.candle:
            candle = ingest_res.candle
            val_res = self.validation_engine.validate_candle(candle)
            if val_res.is_valid:
                self.buffer.append_candle(candle)
                self._total_candles_built += 1
                if self.candle_repo:
                    self.candle_repo.save(candle)
        return ingest_res

    def evaluate_safety_gate(self, symbol: str) -> SafetyGateResult:
        """Evaluate Production Safety Gate for symbol stream."""
        stream_state = self.stream_engine.get_or_create_stream_state(symbol)
        return self.safety_gate.evaluate_stream(stream_state)

    def generate_executive_report(self) -> MarketDataExecutiveReport:
        """Generate executive report summarizing live market data infrastructure state."""
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        active_symbols = sorted(list(self._sequence_counters.keys()))

        tick_reports: list[MarketTickReport] = []
        stream_reports: list[MarketStreamReport] = []
        overall_status = SafetyGateStatus.HEALTHY

        for sym in active_symbols:
            ticks = self.buffer.get_recent_ticks(sym, limit=100)
            avg_bid = sum(t.bid for t in ticks) / len(ticks) if ticks else 0.0
            avg_ask = sum(t.ask for t in ticks) / len(ticks) if ticks else 0.0
            avg_spread = sum(t.spread for t in ticks) / len(ticks) if ticks else 0.0

            rep_id, canonical_hash = compute_report_id("TICK", now_iso)
            tick_rep = MarketTickReport(
                report_id=rep_id,
                symbol=sym,
                total_ticks_processed=len(ticks),
                average_bid=round(avg_bid, 5),
                average_ask=round(avg_ask, 5),
                average_spread=round(avg_spread, 5),
                latest_tick=ticks[-1] if ticks else None,
                timestamp=now_iso,
                canonical_hash=canonical_hash,
            )
            tick_reports.append(tick_rep)

            s_state = self.stream_engine.get_or_create_stream_state(sym)
            s_safety = self.safety_gate.evaluate_stream(s_state)

            if s_safety.status == SafetyGateStatus.UNAVAILABLE:
                overall_status = SafetyGateStatus.UNAVAILABLE
            elif s_safety.status == SafetyGateStatus.DEGRADED and overall_status != SafetyGateStatus.UNAVAILABLE:
                overall_status = SafetyGateStatus.DEGRADED

            s_rep_id, s_canonical_hash = compute_report_id("STREAM", now_iso)
            stream_rep = MarketStreamReport(
                report_id=s_rep_id,
                symbol=sym,
                stream_state=s_state,
                is_healthy=(s_safety.status == SafetyGateStatus.HEALTHY),
                timestamp=now_iso,
                canonical_hash=s_canonical_hash,
            )
            stream_reports.append(stream_rep)

        exec_id, exec_canonical_hash = compute_report_id("EXECUTIVE", now_iso)
        exec_report = MarketDataExecutiveReport(
            report_id=exec_id,
            overall_safety_status=overall_status.value,
            active_symbols_count=len(active_symbols),
            total_ticks_ingested=self._total_ticks_ingested,
            total_candles_built=self._total_candles_built,
            total_gaps_detected=self._total_gaps_detected,
            tick_reports=tick_reports,
            stream_reports=stream_reports,
            timestamp=now_iso,
            canonical_hash=exec_canonical_hash,
        )

        if self.report_repo:
            self.report_repo.save_report(
                report_id=exec_id,
                report_type="EXECUTIVE",
                symbol="ALL",
                timestamp=now_iso,
                markdown_content=exec_report.to_markdown(),
                json_content=exec_report.to_json(),
                canonical_hash=exec_canonical_hash,
            )

        return exec_report
