"""
Project GOAT v1.0 — Dashboard Report Generators
"""

from typing import Any, Dict
from goat.dashboard.core.canonical import serialize_canonical_json
from goat.dashboard.core.models import DashboardHealthStatus, DashboardSession


def generate_dashboard_session_report(session: DashboardSession, health: DashboardHealthStatus) -> str:
    """Generate GitHub Flavored Markdown report for Dashboard backend session."""
    lines = [
        f"# PROJECT GOAT v1.0 — DASHBOARD BACKEND SESSION REPORT",
        "",
        f"**Session ID**: `{session.session_id}`  ",
        f"**Host**: `{session.host}:{session.port}`  ",
        f"**Status**: `{session.status.value}`  ",
        f"**Start Time**: `{session.start_time}`  ",
        f"**Frozen Backend Version**: `{session.frozen_version}`  ",
        "",
        "## System Health Summary",
        "",
        f"- **Uptime**: {health.uptime_seconds:.2f} seconds",
        f"- **Active WS Clients**: {health.active_ws_clients}",
        f"- **System Memory**: {health.system_memory_mb:.2f} MB",
        f"- **Database Status**: {health.database_status}",
        "",
        "## Connected API Subsystems",
        "",
        "- `GET /health` — System Health & Memory Telemetry",
        "- `GET /api/v1/summary` — Scientific Pipeline Overview",
        "- `GET /api/v1/hypotheses` — Active Research Hypotheses Registry",
        "- `GET /api/v1/governance` — Binding Edge Promotion & Retirement Decisions",
        "- `GET /api/v1/symbols` — Synthetic Indices Stream Status",
        "- `WS /ws` — Real-Time WebSocket Telemetry Channel Engine",
    ]
    return "\n".join(lines)


def generate_dashboard_json_report(session: DashboardSession, health: DashboardHealthStatus) -> str:
    """Generate canonical JSON report for Dashboard backend session."""
    payload: Dict[str, Any] = {
        "session": session.model_dump(),
        "health": health.model_dump(),
    }
    return serialize_canonical_json(payload)
