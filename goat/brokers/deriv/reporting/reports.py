"""
Project GOAT v0.8 — Deriv Subsystem Reporting

Defines reporting models for Deriv adapter session, auth, market data subscriptions,
order translation, execution responses, and executive reporting.
"""

from __future__ import annotations

import json
from typing import Any
from pydantic import BaseModel, Field

from goat.brokers.deriv.core.models import (
    DerivAuthentication,
    DerivExecutionResponse,
    DerivMarketSubscription,
    DerivOrderPayload,
    DerivSession,
)
from goat.integration.core.canonical import serialize_canonical_json


class DerivSessionReport(BaseModel):
    """Report model for Deriv session state."""

    report_id: str = Field(..., description="Report ID formatted as DRR_<HEX16>")
    session: DerivSession = Field(..., description="Deriv session model")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Canonical SHA-256 digest")

    class Config:
        frozen = True
        extra = "forbid"

    def to_markdown(self) -> str:
        return f"# Deriv Session Report\n\n- **Session ID**: `{self.session.session_id}`\n- **Status**: `{self.session.status.value}`\n- **Server Time**: `{self.session.server_time}`\n- **Ping Latency**: `{self.session.ping_ms} ms`\n"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())


class AuthenticationReport(BaseModel):
    """Report model for Deriv authentication state."""

    report_id: str = Field(..., description="Report ID formatted as DRR_<HEX16>")
    auth: DerivAuthentication = Field(..., description="Deriv authentication model")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Canonical SHA-256 digest")

    class Config:
        frozen = True
        extra = "forbid"

    def to_markdown(self) -> str:
        return f"# Deriv Authentication Report\n\n- **Auth ID**: `{self.auth.auth_id}`\n- **App ID**: `{self.auth.app_id}`\n- **Authenticated**: `{self.auth.is_authenticated}`\n- **User ID**: `{self.auth.user_id}`\n"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())


class SubscriptionReport(BaseModel):
    """Report model for active Deriv subscriptions."""

    report_id: str = Field(..., description="Report ID formatted as DRR_<HEX16>")
    subscriptions: list[DerivMarketSubscription] = Field(..., description="List of subscriptions")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Canonical SHA-256 digest")

    class Config:
        frozen = True
        extra = "forbid"

    def to_markdown(self) -> str:
        lines = [f"# Deriv Market Subscription Report ({len(self.subscriptions)} Active)\n"]
        for s in sorted(self.subscriptions, key=lambda sub: sub.symbol):
            lines.append(f"- **Symbol**: `{s.symbol}` | Stream ID: `{s.stream_id}` | Active: `{s.is_active}`")
        return "\n".join(lines)

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())


class OrderTranslationReport(BaseModel):
    """Report model for translated Deriv order payloads."""

    report_id: str = Field(..., description="Report ID formatted as DRR_<HEX16>")
    payload: DerivOrderPayload = Field(..., description="Deriv order payload model")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Canonical SHA-256 digest")

    class Config:
        frozen = True
        extra = "forbid"

    def to_markdown(self) -> str:
        return f"# Deriv Order Translation Report\n\n- **Payload ID**: `{self.payload.payload_id}`\n- **Intent ID**: `{self.payload.intent_id}`\n- **Symbol**: `{self.payload.symbol}`\n- **Amount**: `{self.payload.amount}`\n- **Contract Type**: `{self.payload.contract_type.value}`\n"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())


class ExecutionTranslationReport(BaseModel):
    """Report model for translated Deriv execution responses."""

    report_id: str = Field(..., description="Report ID formatted as DRR_<HEX16>")
    execution: DerivExecutionResponse = Field(..., description="Deriv execution model")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Canonical SHA-256 digest")

    class Config:
        frozen = True
        extra = "forbid"

    def to_markdown(self) -> str:
        return f"# Deriv Execution Translation Report\n\n- **Execution ID**: `{self.execution.execution_id}`\n- **Contract ID**: `{self.execution.contract_id}`\n- **Buy Price**: `{self.execution.buy_price}`\n- **Status**: `{self.execution.status}`\n"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())


class DerivExecutiveReport(BaseModel):
    """Consolidated executive report for Deriv Production Adapter."""

    report_id: str = Field(..., description="Report ID formatted as DRR_<HEX16>")
    session: DerivSession | None = Field(default=None, description="Current session snapshot")
    auth: DerivAuthentication | None = Field(default=None, description="Current auth snapshot")
    active_subscriptions_count: int = Field(default=0, ge=0, description="Active subscription count")
    total_orders_translated: int = Field(default=0, ge=0, description="Total order translation count")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Canonical SHA-256 digest")

    class Config:
        frozen = True
        extra = "forbid"

    def to_markdown(self) -> str:
        return (
            f"# Project GOAT v0.8 — Step 7.3 Deriv Production Adapter Executive Report\n\n"
            f"- **Report ID**: `{self.report_id}`\n"
            f"- **Session Status**: `{self.session.status.value if self.session else 'NONE'}`\n"
            f"- **Authenticated**: `{self.auth.is_authenticated if self.auth else False}`\n"
            f"- **Active Subscriptions**: `{self.active_subscriptions_count}`\n"
            f"- **Orders Translated**: `{self.total_orders_translated}`\n"
            f"- **Timestamp**: `{self.timestamp}`\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())
