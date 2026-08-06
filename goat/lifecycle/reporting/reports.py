"""
Project GOAT v0.8 — Trade Lifecycle Reporting Engine

Generates canonical Markdown and JSON reports for:
- TradeLifecycleReport
- TradeEventReport
- ExecutionReport
- LifecycleAuditReport
- TradeSummaryReport
- LifecycleExecutiveReport

Supports to_markdown() and to_json() formatting.
"""

from __future__ import annotations

import json
from typing import Any

from goat.lifecycle.core.models import (
    BrokerExecution,
    LifecycleAudit,
    LifecycleSummary,
    TradeEvent,
    TradeLifecycle,
    TradeReconciliationItem,
)


class BaseLifecycleReport:
    """Base report class providing to_markdown() and to_json() contract interface."""

    def __init__(self, title: str, markdown_content: str, json_payload: dict[str, Any]):
        self.title = title
        self._markdown = markdown_content
        self._json_payload = json_payload

    def to_markdown(self) -> str:
        return self._markdown

    def to_json(self) -> str:
        return json.dumps(self._json_payload, indent=2, sort_keys=True)

    def get_dict(self) -> dict[str, Any]:
        return dict(self._json_payload)


class TradeLifecycleReport(BaseLifecycleReport):
    """Report detailing single trade lifecycle state and metadata."""
    pass


class TradeEventReport(BaseLifecycleReport):
    """Report detailing append-only event streams for a trade lifecycle."""
    pass


class ExecutionReport(BaseLifecycleReport):
    """Report detailing broker execution fill telemetry."""
    pass


class LifecycleAuditReport(BaseLifecycleReport):
    """Report detailing state transition audit trail log entries."""
    pass


class TradeSummaryReport(BaseLifecycleReport):
    """Report summarizing aggregated trade lifecycle metrics across state categories."""
    pass


class LifecycleExecutiveReport(BaseLifecycleReport):
    """Executive report combining lifecycle metrics, reconciliation status, and event audits."""
    pass


class LifecycleReportEngine:
    """Reporting engine generating structured Markdown and JSON reports."""

    def build_lifecycle_report(self, lifecycle: TradeLifecycle) -> TradeLifecycleReport:
        json_data = lifecycle.model_dump()
        markdown = f"""# GOAT Trade Lifecycle Report

- **Lifecycle ID**: `{lifecycle.lifecycle_id}`
- **Intent ID**: `{lifecycle.intent_id}`
- **Symbol**: {lifecycle.symbol}
- **Side**: {lifecycle.side}
- **Quantity**: `{lifecycle.quantity}`
- **Current State**: `{lifecycle.current_state.value}`
- **Created At**: {lifecycle.created_at}
- **Updated At**: {lifecycle.updated_at}
- **Closed At**: {lifecycle.closed_at or 'N/A'}
- **Position Reference**: `{lifecycle.position_id or 'None'}`
- **Broker Execution Ref**: `{lifecycle.broker_execution_id or 'None'}`

---
*Canonical Hash*: `{lifecycle.canonical_hash}`
"""
        return TradeLifecycleReport("Trade Lifecycle Report", markdown, json_data)

    def build_event_report(self, events: list[TradeEvent], lifecycle_id: str) -> TradeEventReport:
        json_data = {
            "lifecycle_id": lifecycle_id,
            "events_count": len(events),
            "events": [e.model_dump() for e in events],
        }

        rows = []
        for e in events:
            rows.append(f"| `{e.event_id[:12]}` | `{e.event_type.value}` | {e.timestamp} | {e.details} |")
        table = "\n".join(rows) if rows else "| None | - | - | - |"

        markdown = f"""# GOAT Trade Event Stream Report

- **Target Lifecycle ID**: `{lifecycle_id}`
- **Total Events Recorded**: {len(events)}

| Event ID | Type | Timestamp | Details |
|---|---|---|---|
{table}
"""
        return TradeEventReport("Trade Event Stream Report", markdown, json_data)

    def build_execution_report(self, executions: list[BrokerExecution]) -> ExecutionReport:
        json_data = {
            "executions_count": len(executions),
            "executions": [ex.model_dump() for ex in executions],
        }

        rows = []
        for ex in executions:
            rows.append(
                f"| `{ex.execution_id[:12]}` | `{ex.broker_order_id}` | {ex.symbol} | {ex.side} | {ex.quantity} | `${ex.price:,.2f}` | {ex.timestamp} |"
            )
        table = "\n".join(rows) if rows else "| None | - | - | - | - | - | - |"

        markdown = f"""# GOAT Broker Execution Fill Report

- **Total Executions**: {len(executions)}

| Execution ID | Broker Order ID | Symbol | Side | Quantity | Fill Price | Timestamp |
|---|---|---|---|---|---|---|
{table}
"""
        return ExecutionReport("Broker Execution Fill Report", markdown, json_data)

    def build_audit_report(self, audits: list[LifecycleAudit], lifecycle_id: str) -> LifecycleAuditReport:
        json_data = {
            "lifecycle_id": lifecycle_id,
            "audits_count": len(audits),
            "audits": [a.model_dump() for a in audits],
        }

        rows = []
        for a in audits:
            prev = a.previous_state.value if a.previous_state else "None"
            rows.append(f"| `{a.audit_id[:12]}` | `{a.event_type.value}` | `{prev}` -> `{a.new_state.value}` | {a.reason} | {a.timestamp} |")
        table = "\n".join(rows) if rows else "| None | - | - | - | - |"

        markdown = f"""# GOAT Lifecycle Audit Trail Report

- **Target Lifecycle ID**: `{lifecycle_id}`
- **Total Audit Log Entries**: {len(audits)}

| Audit ID | Event Type | State Transition | Reason | Timestamp |
|---|---|---|---|---|
{table}
"""
        return LifecycleAuditReport("Lifecycle Audit Trail Report", markdown, json_data)

    def build_summary_report(self, summary: LifecycleSummary) -> TradeSummaryReport:
        json_data = summary.model_dump()

        markdown = f"""# GOAT Trade Lifecycle Summary Report

- **Summary ID**: `{summary.summary_id}`
- **Timestamp**: {summary.timestamp}

## Aggregated Metrics
- **Total Trade Lifecycles**: {summary.total_trades}
- **Active Open Trades**: {summary.open_trades}
- **Completed Closed Trades**: {summary.closed_trades}
- **Cancelled Trades**: {summary.cancelled_trades}
- **Rejected Trades**: {summary.rejected_trades}
- **Failed Trades**: {summary.failed_trades}
"""
        return TradeSummaryReport("Trade Lifecycle Summary Report", markdown, json_data)

    def build_executive_report(
        self,
        summary: LifecycleSummary,
        recon_items: list[TradeReconciliationItem],
        recent_events: list[TradeEvent],
    ) -> LifecycleExecutiveReport:
        is_reconciled = len(recon_items) == 0
        json_data = {
            "summary": summary.model_dump(),
            "reconciliation_status": "RECONCILED" if is_reconciled else "DISCREPANCIES",
            "discrepancy_count": len(recon_items),
            "discrepancies": [item.model_dump() for item in recon_items],
            "recent_events_count": len(recent_events),
        }

        disc_rows = []
        for item in recon_items:
            disc_rows.append(f"- **[{item.mismatch_type.value}]** ({item.symbol}): {item.description}")
        disc_text = "\n".join(disc_rows) if disc_rows else "- No discrepancies detected. Broker, Portfolio, and Lifecycle states are 100% synchronized."

        markdown = f"""# GOAT Trade Lifecycle Executive Report

- **Timestamp**: {summary.timestamp}
- **Reconciliation Audit**: {"✓ RECONCILED (SYNCHRONIZED)" if is_reconciled else f"⚠️ {len(recon_items)} DISCREPANCIES DETECTED"}

## Lifecycle Overview
- **Total Trades**: {summary.total_trades} | **Open**: {summary.open_trades} | **Closed**: {summary.closed_trades}
- **Cancelled**: {summary.cancelled_trades} | **Rejected**: {summary.rejected_trades} | **Failed**: {summary.failed_trades}

## Reconciliation Findings ({len(recon_items)})
{disc_text}
"""
        return LifecycleExecutiveReport("Trade Lifecycle Executive Report", markdown, json_data)
