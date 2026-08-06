"""
Project GOAT v0.8 — Broker Reporting Models

Immutable reporting structures supporting Markdown exports and canonical JSON formatting:
- BrokerProfileReport
- ConnectionReport
- AccountReport
- OrderIntentReport
- BrokerCapabilityReport
- BrokerExecutiveReport
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.integration.core.canonical import serialize_canonical_json
from goat.brokers.core.canonical import compute_report_id
from goat.brokers.core.models import (
    BrokerAccount,
    BrokerConnection,
    BrokerOrderIntent,
    BrokerProfile,
)


class BrokerProfileReport(BaseModel):
    """Immutable report summarizing a BrokerProfile configuration."""

    report_id: str = Field(..., description="Report ID formatted as BRR_<HEX16>")
    profile: BrokerProfile = Field(..., description="BrokerProfile entity")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        p = self.profile
        return (
            f"# Broker Profile Report — {p.broker_name}\n"
            f"**Report ID**: `{self.report_id}` | **Broker ID**: `{p.broker_id}`  \n"
            f"**Type**: `{p.broker_type.value}` | **API Version**: `{p.api_version}`  \n"
            f"**Supported Assets**: `{', '.join(p.supported_assets)}`  \n"
            f"**Capabilities**: Streaming `{p.supports_streaming}` | Positions `{p.supports_positions}` | History `{p.supports_history}`\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class ConnectionReport(BaseModel):
    """Immutable report summarizing session connection telemetry."""

    report_id: str = Field(..., description="Report ID formatted as BRR_<HEX16>")
    connection: BrokerConnection = Field(..., description="BrokerConnection entity")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        c = self.connection
        return (
            f"# Broker Connection Telemetry Report — {c.broker_id}\n"
            f"**Report ID**: `{self.report_id}` | **Connection ID**: `{c.connection_id}`  \n"
            f"**Status**: `{c.status.value}` | **Latency**: `{c.latency_ms:.1f}ms`  \n"
            f"**Connected At**: `{c.connected_at}` | **Heartbeat**: `{c.heartbeat_timestamp}`  \n"
            f"**Reconnect Attempts**: `{c.reconnect_attempts}`\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class AccountReport(BaseModel):
    """Immutable report summarizing broker account balance, equity, and margin."""

    report_id: str = Field(..., description="Report ID formatted as BRR_<HEX16>")
    account: BrokerAccount = Field(..., description="BrokerAccount entity")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        a = self.account
        return (
            f"# Broker Account State Report — {a.broker_id}\n"
            f"**Report ID**: `{self.report_id}` | **Account ID**: `{a.account_id}`  \n"
            f"**Type**: `{a.account_type}` | **Currency**: `{a.account_currency}`  \n"
            f"**Balance**: `{a.balance:.2f} {a.account_currency}` | **Equity**: `{a.equity:.2f} {a.account_currency}`  \n"
            f"**Margin**: `{a.margin:.2f}` | **Free Margin**: `{a.free_margin:.2f}` | **Leverage**: `1:{a.leverage:.0f}`\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class OrderIntentReport(BaseModel):
    """Immutable report summarizing an order intent structure."""

    report_id: str = Field(..., description="Report ID formatted as BRR_<HEX16>")
    intent: BrokerOrderIntent = Field(..., description="BrokerOrderIntent entity")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        i = self.intent
        return (
            f"# Broker Order Intent Report — {i.intent_id}\n"
            f"**Report ID**: `{self.report_id}` | **Broker ID**: `{i.broker_id}`  \n"
            f"**Symbol**: `{i.symbol}` | **Side**: `{i.side.value}` | **Quantity**: `{i.quantity}`  \n"
            f"**Order Type**: `{i.order_type.value}` | **TIF**: `{i.time_in_force.value}`  \n"
            f"**SL**: `{i.stop_loss}` | **TP**: `{i.take_profit}`\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class BrokerCapabilityReport(BaseModel):
    """Immutable report summarizing capability registry matrix."""

    report_id: str = Field(..., description="Report ID formatted as BRR_<HEX16>")
    profiles: list[BrokerProfile] = Field(default_factory=list, description="List of registered profiles")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        lines = [
            "# Broker Capability Registry Report",
            f"**Report ID**: `{self.report_id}`  ",
            f"**Total Registered Profiles**: `{len(self.profiles)}`",
            "",
            "## Registered Adapters",
        ]
        for p in self.profiles:
            lines.append(f"- **{p.broker_name}** (`{p.broker_id}`): Type `{p.broker_type.value}`, Assets: `{len(p.supported_assets)}`")
        return "\n".join(lines)

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class BrokerExecutiveReport(BaseModel):
    """Consolidated executive report summarizing all registered broker connections and account states."""

    report_id: str = Field(..., description="Report ID formatted as BRR_<HEX16>")
    active_brokers_count: int = Field(default=0, ge=0, description="Active registered broker adapter count")
    profiles: list[BrokerProfile] = Field(default_factory=list, description="Registered profiles")
    connections: list[BrokerConnection] = Field(default_factory=list, description="Connection states")
    accounts: list[BrokerAccount] = Field(default_factory=list, description="Account states")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        lines = [
            "# Step 7.2 — Broker Abstraction Framework Executive Report",
            f"**Report ID**: `{self.report_id}`  ",
            f"**Timestamp**: {self.timestamp}  ",
            f"**Active Brokers Count**: `{self.active_brokers_count}`",
            "",
            "## Broker Connections Summary",
        ]
        for c in self.connections:
            lines.append(f"- **{c.broker_id}**: Status `{c.status.value}`, Latency `{c.latency_ms:.1f}ms`")
        return "\n".join(lines)

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"
