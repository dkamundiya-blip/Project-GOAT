"""
Project GOAT v0.8 — Market Data Reporting Models

Immutable reporting structures supporting Markdown exports and canonical JSON formatting:
- MarketTickReport
- MarketCandleReport
- MarketStreamReport
- MarketGapReport
- ReplaySnapshotReport
- MarketDataExecutiveReport
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.marketdata.core.canonical import compute_report_id
from goat.marketdata.core.models import (
    MarketCandle,
    MarketGap,
    MarketStreamState,
    MarketTick,
    ReplaySnapshot,
)
from goat.integration.core.canonical import serialize_canonical_json


class MarketTickReport(BaseModel):
    """Immutable report summarizing tick processing metrics."""

    report_id: str = Field(..., description="Report ID formatted as MRP_<HEX16>")
    symbol: str = Field(..., description="Target market symbol")
    total_ticks_processed: int = Field(default=0, ge=0, description="Total valid ticks processed")
    average_bid: float = Field(default=0.0, ge=0.0, description="Average bid price across window")
    average_ask: float = Field(default=0.0, ge=0.0, description="Average ask price across window")
    average_spread: float = Field(default=0.0, ge=0.0, description="Average spread across window")
    latest_tick: MarketTick | None = Field(default=None, description="Most recent tick model")
    timestamp: str = Field(..., description="ISO 8601 UTC report generation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        lines = [
            f"# Market Tick Report — {self.symbol}",
            f"**Report ID**: `{self.report_id}`  ",
            f"**Timestamp**: {self.timestamp}  ",
            f"**Total Ticks Processed**: {self.total_ticks_processed}  ",
            f"**Average Bid**: `{self.average_bid:.5f}`  ",
            f"**Average Ask**: `{self.average_ask:.5f}`  ",
            f"**Average Spread**: `{self.average_spread:.5f}`  ",
        ]
        if self.latest_tick:
            lines.append(f"**Latest Tick ID**: `{self.latest_tick.tick_id}` (Bid: `{self.latest_tick.bid}`, Ask: `{self.latest_tick.ask}`)")
        return "\n".join(lines)

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class MarketCandleReport(BaseModel):
    """Immutable report summarizing candle processing metrics."""

    report_id: str = Field(..., description="Report ID formatted as MRP_<HEX16>")
    symbol: str = Field(..., description="Target market symbol")
    total_candles_count: int = Field(default=0, ge=0, description="Total candles in report")
    timeframe: str = Field(default="1M", description="Candle timeframe")
    period_open: float = Field(default=0.0, ge=0.0, description="First candle open price")
    period_high: float = Field(default=0.0, ge=0.0, description="Highest high across period")
    period_low: float = Field(default=0.0, ge=0.0, description="Lowest low across period")
    period_close: float = Field(default=0.0, ge=0.0, description="Latest candle close price")
    latest_candle: MarketCandle | None = Field(default=None, description="Most recent candle model")
    timestamp: str = Field(..., description="ISO 8601 UTC report generation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        return (
            f"# Market Candle Report — {self.symbol} ({self.timeframe})\n"
            f"**Report ID**: `{self.report_id}`  \n"
            f"**Timestamp**: {self.timestamp}  \n"
            f"**Total Candles**: {self.total_candles_count}  \n"
            f"**OHLC Range**: Open `{self.period_open:.5f}` | High `{self.period_high:.5f}` | Low `{self.period_low:.5f}` | Close `{self.period_close:.5f}`\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class MarketStreamReport(BaseModel):
    """Immutable report summarizing stream health telemetry."""

    report_id: str = Field(..., description="Report ID formatted as MRP_<HEX16>")
    symbol: str = Field(..., description="Target market symbol")
    stream_state: MarketStreamState = Field(..., description="Current MarketStreamState entity")
    is_healthy: bool = Field(..., description="True if stream health check passes")
    timestamp: str = Field(..., description="ISO 8601 UTC report generation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        s = self.stream_state
        return (
            f"# Market Stream Telemetry Report — {self.symbol}\n"
            f"**Report ID**: `{self.report_id}`  \n"
            f"**Connection Status**: `{s.connection_status.value}` (Healthy: `{self.is_healthy}`)  \n"
            f"**Latency**: `{s.latency_ms:.2f} ms`  \n"
            f"**Packets Received**: `{s.packets_received}` | **Packets Dropped**: `{s.packets_dropped}` | **Reconnects**: `{s.reconnect_count}`\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class MarketGapReport(BaseModel):
    """Immutable report summarizing detected market stream gaps."""

    report_id: str = Field(..., description="Report ID formatted as MRP_<HEX16>")
    symbol: str = Field(..., description="Target market symbol")
    detected_gaps_count: int = Field(default=0, ge=0, description="Total gaps recorded")
    gaps: list[MarketGap] = Field(default_factory=list, description="List of MarketGap models")
    timestamp: str = Field(..., description="ISO 8601 UTC report generation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        lines = [
            f"# Market Data Gap Report — {self.symbol}",
            f"**Report ID**: `{self.report_id}`  ",
            f"**Total Gaps Detected**: `{self.detected_gaps_count}`  ",
        ]
        for g in self.gaps:
            lines.append(f"- Gap `{g.gap_id}`: `{g.reason.value}` from `{g.start_timestamp}` to `{g.end_timestamp}` ({g.missing_packets} missing packets)")
        return "\n".join(lines)

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class ReplaySnapshotReport(BaseModel):
    """Immutable report summarizing replay snapshot integrity."""

    report_id: str = Field(..., description="Report ID formatted as MRP_<HEX16>")
    symbol: str = Field(..., description="Target market symbol")
    snapshot: ReplaySnapshot = Field(..., description="Target ReplaySnapshot model")
    replay_passed: bool = Field(..., description="True if replay checksum verification succeeded")
    timestamp: str = Field(..., description="ISO 8601 UTC report generation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        s = self.snapshot
        return (
            f"# Market Replay Snapshot Report — {self.symbol}\n"
            f"**Report ID**: `{self.report_id}`  \n"
            f"**Snapshot ID**: `{s.replay_id}`  \n"
            f"**Replay Verification**: `{'PASSED' if self.replay_passed else 'FAILED'}`  \n"
            f"**Checksum Digest**: `{s.replay_checksum}`\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class MarketDataExecutiveReport(BaseModel):
    """Executive consolidated report for Step 7.0 Live Market Data Infrastructure."""

    report_id: str = Field(..., description="Executive report ID formatted as MRP_<HEX16>")
    overall_safety_status: str = Field(..., description="Production Safety Gate Status (HEALTHY, DEGRADED, UNAVAILABLE)")
    active_symbols_count: int = Field(default=0, ge=0, description="Total active symbols tracked")
    total_ticks_ingested: int = Field(default=0, ge=0, description="Total valid ticks ingested")
    total_candles_built: int = Field(default=0, ge=0, description="Total candles constructed")
    total_gaps_detected: int = Field(default=0, ge=0, description="Total gaps recorded")
    tick_reports: list[MarketTickReport] = Field(default_factory=list, description="Sub-reports for ticks")
    stream_reports: list[MarketStreamReport] = Field(default_factory=list, description="Sub-reports for stream telemetry")
    timestamp: str = Field(..., description="ISO 8601 UTC report generation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        lines = [
            "# Step 7.0 — Live Market Data Infrastructure Executive Report",
            f"**Report ID**: `{self.report_id}`  ",
            f"**Timestamp**: {self.timestamp}  ",
            f"**Production Safety Gate Status**: `{self.overall_safety_status}`  ",
            f"**Active Symbols**: `{self.active_symbols_count}` | **Total Ticks**: `{self.total_ticks_ingested}` | **Total Candles**: `{self.total_candles_built}` | **Gaps**: `{self.total_gaps_detected}`",
            "",
            "## Subsystem Telemetry Summaries",
        ]
        for sr in self.stream_reports:
            lines.append(f"- **{sr.symbol}**: Status `{sr.stream_state.connection_status.value}` (Latency: `{sr.stream_state.latency_ms}ms`, Packets: `{sr.stream_state.packets_received}`)")
        return "\n".join(lines)

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"
