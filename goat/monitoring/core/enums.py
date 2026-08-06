"""
Project GOAT v0.8 — Operational Monitoring Core Enumerations
"""

from enum import Enum


class HealthLevel(str, Enum):
    """Subsystem and overall health state level enumeration."""
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    OFFLINE = "OFFLINE"


class AlertLevel(str, Enum):
    """Operational alert severity classification enumeration."""
    INFO = "INFO"
    NOTICE = "NOTICE"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SubsystemName(str, Enum):
    """Monitored production subsystem enumeration."""
    LIVE_MARKET_DATA = "LIVE_MARKET_DATA"
    MARKET_STATE = "MARKET_STATE"
    BROKER_ADAPTER = "BROKER_ADAPTER"
    EXECUTION_ENGINE = "EXECUTION_ENGINE"
    PORTFOLIO_ENGINE = "PORTFOLIO_ENGINE"
    LIFECYCLE_ENGINE = "LIFECYCLE_ENGINE"
    NOTIFICATION_PLATFORM = "NOTIFICATION_PLATFORM"


class DiagnosticCategory(str, Enum):
    """Operational anomaly diagnostic category classification."""
    STALE_MARKET_FEED = "STALE_MARKET_FEED"
    DATABASE_DEGRADATION = "DATABASE_DEGRADATION"
    QUEUE_CONGESTION = "QUEUE_CONGESTION"
    HEARTBEAT_FAILURE = "HEARTBEAT_FAILURE"
    MISSING_NOTIFICATIONS = "MISSING_NOTIFICATIONS"
    EXECUTION_BOTTLENECK = "EXECUTION_BOTTLENECK"
    RECONCILIATION_FAILURE = "RECONCILIATION_FAILURE"
    STORAGE_GROWTH = "STORAGE_GROWTH"
    HIGH_LATENCY = "HIGH_LATENCY"
    COMPONENT_DEGRADATION = "COMPONENT_DEGRADATION"


class MonitoringAuditEventType(str, Enum):
    """Monitoring audit event classification enumeration."""
    HEALTH_CHECK_PERFORMED = "HEALTH_CHECK_PERFORMED"
    HEALTH_LEVEL_CHANGED = "HEALTH_LEVEL_CHANGED"
    HEARTBEAT_REGISTERED = "HEARTBEAT_REGISTERED"
    WATCHDOG_ALERT = "WATCHDOG_ALERT"
    TELEMETRY_RECORDED = "TELEMETRY_RECORDED"
    DIAGNOSTIC_COMPLETED = "DIAGNOSTIC_COMPLETED"
