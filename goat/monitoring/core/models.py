"""
Project GOAT v0.8 — Core Immutable Domain Models for Operational Monitoring & Reliability Engine

Defines immutable Pydantic V2 models using ConfigDict(frozen=True, extra="forbid"):
- SystemHealth (SYH_<HEX16>)
- SubsystemHealth (SBH_<HEX16>)
- HeartbeatRecord (HBT_<HEX16>)
- HealthAlert (HAL_<HEX16>)
- TelemetrySnapshot (TEL_<HEX16>)
- ReliabilityAssessment (RAS_<HEX16>)
- WatchdogStatus (WDG_<HEX16>)
- MonitoringSummary (MSM_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.monitoring.core.enums import AlertLevel, HealthLevel, SubsystemName


class SubsystemHealth(BaseModel):
    """Immutable model representing health status of a single production subsystem."""

    subsystem_health_id: str = Field(
        ...,
        description="Unique subsystem health ID formatted as SBH_<HEX16>",
        pattern=r"^SBH_[A-Fa-f0-9]{16}$",
    )
    subsystem_name: SubsystemName = Field(..., description="Target subsystem enum")
    health_level: HealthLevel = Field(..., description="Assigned health status level enum")
    details: str = Field(default="", description="Detailed health report string or status notes")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class SystemHealth(BaseModel):
    """Immutable model representing overall aggregated system health status."""

    health_id: str = Field(
        ...,
        description="Unique system health ID formatted as SYH_<HEX16>",
        pattern=r"^SYH_[A-Fa-f0-9]{16}$",
    )
    overall_health: HealthLevel = Field(..., description="Aggregated overall system health level")
    subsystem_health_map: dict[str, HealthLevel] = Field(
        default_factory=dict,
        description="Subsystem name string -> HealthLevel mapping",
    )
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class HeartbeatRecord(BaseModel):
    """Immutable model representing a subsystem heartbeat telemetry pulse."""

    heartbeat_id: str = Field(
        ...,
        description="Unique heartbeat record ID formatted as HBT_<HEX16>",
        pattern=r"^HBT_[A-Fa-f0-9]{16}$",
    )
    subsystem_name: SubsystemName = Field(..., description="Source subsystem enum")
    sequence: int = Field(..., ge=0, description="Sequential heartbeat counter")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class HealthAlert(BaseModel):
    """Immutable model representing an operational monitoring health alert."""

    alert_id: str = Field(
        ...,
        description="Unique alert ID formatted as HAL_<HEX16>",
        pattern=r"^HAL_[A-Fa-f0-9]{16}$",
    )
    subsystem_name: SubsystemName = Field(..., description="Originating subsystem enum")
    alert_level: AlertLevel = Field(..., description="Alert severity classification enum")
    message: str = Field(..., description="Human-readable alert message")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class TelemetrySnapshot(BaseModel):
    """Immutable model representing abstract operational performance metrics."""

    snapshot_id: str = Field(
        ...,
        description="Unique telemetry snapshot ID formatted as TEL_<HEX16>",
        pattern=r"^TEL_[A-Fa-f0-9]{16}$",
    )
    cpu_usage: float = Field(..., ge=0.0, le=100.0, description="Abstract CPU usage percentage")
    memory_usage: float = Field(..., ge=0.0, le=100.0, description="Abstract memory usage percentage")
    disk_usage: float = Field(..., ge=0.0, le=100.0, description="Abstract disk usage percentage")
    database_latency_ms: float = Field(..., ge=0.0, description="Database operation latency in milliseconds")
    tick_latency_ms: float = Field(..., ge=0.0, description="Market tick ingestion latency in milliseconds")
    notification_latency_ms: float = Field(..., ge=0.0, description="Notification dispatch latency in milliseconds")
    execution_latency_ms: float = Field(..., ge=0.0, description="Execution engine latency in milliseconds")
    queue_depth: int = Field(..., ge=0, description="Pending queue depth count")
    processing_time_ms: float = Field(..., ge=0.0, description="Total tick-to-order processing time in ms")
    repository_size_bytes: int = Field(..., ge=0, description="Total SQLite database file size in bytes")
    replay_throughput_eps: float = Field(..., ge=0.0, description="Deterministic replay throughput events/sec")
    event_throughput_eps: float = Field(..., ge=0.0, description="Live event throughput events/sec")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class ReliabilityAssessment(BaseModel):
    """Immutable model representing reliability metrics and uptime scores."""

    assessment_id: str = Field(
        ...,
        description="Unique reliability assessment ID formatted as RAS_<HEX16>",
        pattern=r"^RAS_[A-Fa-f0-9]{16}$",
    )
    reliability_score: float = Field(..., ge=0.0, le=100.0, description="Aggregated reliability score (0-100%)")
    uptime_percentage: float = Field(..., ge=0.0, le=100.0, description="Monitored uptime percentage")
    failure_count: int = Field(..., ge=0, description="Total detected critical failure count")
    warning_count: int = Field(..., ge=0, description="Total warning count")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class WatchdogStatus(BaseModel):
    """Immutable model representing watchdog component pulse tracking status."""

    watchdog_id: str = Field(
        ...,
        description="Unique watchdog status ID formatted as WDG_<HEX16>",
        pattern=r"^WDG_[A-Fa-f0-9]{16}$",
    )
    active_components: list[SubsystemName] = Field(default_factory=list, description="Healthy active subsystems")
    stale_components: list[SubsystemName] = Field(default_factory=list, description="Subsystems with stale heartbeats")
    dead_components: list[SubsystemName] = Field(default_factory=list, description="Subsystems with timed-out heartbeats")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class MonitoringSummary(BaseModel):
    """Immutable summary model aggregating overall operational monitoring metrics."""

    summary_id: str = Field(
        ...,
        description="Unique monitoring summary ID formatted as MSM_<HEX16>",
        pattern=r"^MSM_[A-Fa-f0-9]{16}$",
    )
    total_heartbeats: int = Field(..., ge=0, description="Total heartbeats recorded")
    total_alerts: int = Field(..., ge=0, description="Total health alerts generated")
    active_subsystems: int = Field(..., ge=0, description="Number of currently healthy subsystems")
    overall_status: HealthLevel = Field(..., description="Aggregated system health level")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")
