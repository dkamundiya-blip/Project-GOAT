"""
Project GOAT v1.0 — Dashboard Core Enums
"""

from enum import Enum


class ServerStatus(str, Enum):
    """Dashboard backend server status states."""

    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    DEGRADED = "DEGRADED"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


class TelemetryChannel(str, Enum):
    """Dashboard real-time telemetry streaming channels."""

    SYSTEM = "SYSTEM"
    MICROSTRUCTURE = "MICROSTRUCTURE"
    HYPOTHESIS = "HYPOTHESIS"
    EVIDENCE = "EVIDENCE"
    EXPERIMENT = "EXPERIMENT"
    GOVERNANCE = "GOVERNANCE"
    INTELLIGENCE = "INTELLIGENCE"


class StreamState(str, Enum):
    """WebSocket stream connection state."""

    CONNECTING = "CONNECTING"
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"


class APIRouteGroup(str, Enum):
    """API endpoint logical route grouping."""

    SYSTEM = "SYSTEM"
    RESEARCH = "RESEARCH"
    MICROSTRUCTURE = "MICROSTRUCTURE"
    GOVERNANCE = "GOVERNANCE"
    PORTFOLIO = "PORTFOLIO"
