"""
Project GOAT v0.7 — Scientific Signal Reports

Provides immutable, deterministic report models and renderers:
- TradingSignalReport
- SignalPayloadReport
- SignalLifecycleReport
- ExecutionReadinessReport
- SignalAuditReport
- SignalExecutiveReport
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.integration.core.canonical import serialize_canonical_json
from goat.signals.core.models import (
    ExecutionReadiness,
    SignalAuditRecord,
    SignalLifecycleEvent,
    SignalPayload,
    TradingSignal,
)


class TradingSignalReport(BaseModel):
    """Report detailing TradingSignal outcomes and required public parameters."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    signals: list[TradingSignal] = Field(default_factory=list, description="List of trading signals")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Trading Signal Summary Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Signals**: {len(self.signals)}",
            "",
            "| Signal ID | Instrument | Direction | Entry Price | Stop Loss | Take Profit | Lots | Monetary Risk | Monetary Reward | Confidence | Status |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for s in sorted(self.signals, key=lambda x: x.signal_id):
            st = s.lifecycle_state.value if hasattr(s.lifecycle_state, "value") else str(s.lifecycle_state)
            lines.append(
                f"| `{s.signal_id}` | `{s.instrument}` | `{s.direction.value}` | `{s.entry_price:.5f}` | `{s.stop_loss:.5f}` | `{s.take_profit:.5f}` | `{s.recommended_lot_size:.2f}` | `${s.monetary_risk:,.2f}` | `${s.monetary_reward:,.2f}` | `{s.scientific_confidence:.2f}` | `{st}` |"
            )
        return "\n".join(lines)


class SignalPayloadReport(BaseModel):
    """Report detailing generated SignalPayload formats."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    payloads: list[SignalPayload] = Field(default_factory=list, description="List of signal payloads")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Signal Payload Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Payloads**: {len(self.payloads)}",
            "",
            "| Payload ID | Signal ID | Format | Checksum |",
            "| :--- | :--- | :--- | :--- |",
        ]
        for p in sorted(self.payloads, key=lambda x: x.payload_id):
            fmt = p.payload_format.value if hasattr(p.payload_format, "value") else str(p.payload_format)
            lines.append(
                f"| `{p.payload_id}` | `{p.signal_id}` | `{fmt}` | `{p.checksum[:16]}...` |"
            )
        return "\n".join(lines)


class SignalLifecycleReport(BaseModel):
    """Report detailing SignalLifecycleEvent transitions."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    events: list[SignalLifecycleEvent] = Field(default_factory=list, description="List of lifecycle events")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Signal Lifecycle Event Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Events**: {len(self.events)}",
            "",
            "| Event ID | Signal ID | Previous State | Current State | Timestamp | Reason |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for e in sorted(self.events, key=lambda x: x.lifecycle_event_id):
            prev = e.previous_state.value if hasattr(e.previous_state, "value") else str(e.previous_state)
            curr = e.current_state.value if hasattr(e.current_state, "value") else str(e.current_state)
            lines.append(
                f"| `{e.lifecycle_event_id}` | `{e.signal_id}` | `{prev}` | `{curr}` | `{e.event_timestamp}` | {e.triggering_reason} |"
            )
        return "\n".join(lines)


class ExecutionReadinessReport(BaseModel):
    """Report detailing ExecutionReadiness decisions."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    readiness_evaluations: list[ExecutionReadiness] = Field(default_factory=list, description="List of execution readiness evaluations")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Execution Readiness Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Evaluations**: {len(self.readiness_evaluations)}",
            "",
            "| Readiness ID | Signal ID | Status | Readiness Score | Summary |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for r in sorted(self.readiness_evaluations, key=lambda x: x.readiness_id):
            st = r.execution_status.value if hasattr(r.execution_status, "value") else str(r.execution_status)
            lines.append(
                f"| `{r.readiness_id}` | `{r.signal_id}` | `{st}` | `{r.readiness_score:.2f}` | {r.validation_summary} |"
            )
        return "\n".join(lines)


class SignalAuditReport(BaseModel):
    """Report detailing SignalAuditRecord scientific provenance lineage."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    audit_records: list[SignalAuditRecord] = Field(default_factory=list, description="List of audit records")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Signal Audit Provenance Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Audit Records**: {len(self.audit_records)}",
            "",
            "| Audit ID | Signal ID | Qualification Ref | Simulation Ref | Risk Ref | Replay Ref |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for a in sorted(self.audit_records, key=lambda x: x.audit_id):
            lines.append(
                f"| `{a.audit_id}` | `{a.signal_id}` | `{a.qualification_reference}` | `{a.simulation_reference}` | `{a.risk_reference}` | `{a.replay_reference}` |"
            )
        return "\n".join(lines)


class SignalExecutiveReport(BaseModel):
    """Executive root report for Scientific Signal Generation Subsystem & Version 0.7 Milestone."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    total_signals_generated: int = Field(..., ge=0)
    total_signals_ready: int = Field(..., ge=0)
    top_instrument: str = Field(default="")
    top_direction: str = Field(default="")
    top_lot_size: float = Field(default=0.0, ge=0.0)
    top_monetary_risk: float = Field(default=0.0, ge=0.0)
    top_monetary_reward: float = Field(default=0.0, ge=0.0)
    summary_notes: str = Field(default="")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Scientific Signal Executive Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Signals Generated**: {self.total_signals_generated}",
            f"- **Total Execution Ready Signals**: {self.total_signals_ready}",
            f"- **Top Instrument**: `{self.top_instrument}` ({self.top_direction})",
            f"- **Top Recommended Lots**: `{self.top_lot_size:.2f}`",
            f"- **Top Monetary Risk**: `${self.top_monetary_risk:,.2f}`",
            f"- **Top Monetary Reward**: `${self.top_monetary_reward:,.2f}`",
            "",
            "## Version 0.7 Milestone Summary",
            self.summary_notes or "Scientific signal generation, payload formatting, lifecycle transitions, and execution readiness completed deterministically.",
        ]
        return "\n".join(lines)
