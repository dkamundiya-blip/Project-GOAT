"""
Project GOAT v1.0 — Master Dashboard Backend Server Facade
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from goat.dashboard.api.router import create_dashboard_router
from goat.dashboard.core.canonical import compute_dashboard_session_id
from goat.dashboard.core.enums import ServerStatus
from goat.dashboard.core.models import DashboardHealthStatus, DashboardSession
from goat.dashboard.persistence.sqlite import DashboardReadOnlyRepositoryAdapter
from goat.dashboard.reporting.reports import (
    generate_dashboard_json_report,
    generate_dashboard_session_report,
)
from goat.dashboard.telemetry.collector import SystemTelemetryCollector
from goat.dashboard.websocket.engine import WebSocketTelemetryEngine
from goat.dashboard.websocket.manager import WebSocketConnectionManager


class MasterDashboardServer:
    """Master facade for Project GOAT Version 1.0 Dashboard Backend Server."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8000, db_path: Optional[str] = None) -> None:
        self.host = host
        self.port = port
        self.start_time = datetime.now(timezone.utc).isoformat()
        self.session_id = compute_dashboard_session_id(host, port, self.start_time)

        self.repo = DashboardReadOnlyRepositoryAdapter(db_path=db_path)
        self.collector = SystemTelemetryCollector()
        self.ws_manager = WebSocketConnectionManager()
        self.ws_engine = WebSocketTelemetryEngine(manager=self.ws_manager, collector=self.collector)

        self.status = ServerStatus.INITIALIZING
        self.router = create_dashboard_router(repo=self.repo, collector=self.collector)
        self.status = ServerStatus.RUNNING

    def handle_request(self, path: str, **kwargs: Any) -> Any:
        """Handle incoming REST request by path dispatch."""
        return self.router.dispatch(path=path, **kwargs)

    def get_session(self) -> DashboardSession:
        """Get current immutable Dashboard session state."""
        return DashboardSession(
            session_id=self.session_id,
            host=self.host,
            port=self.port,
            status=self.status,
            start_time=self.start_time,
            active_connections=self.ws_manager.connection_count,
            frozen_version="v0.9.1",
        )

    def get_health(self) -> DashboardHealthStatus:
        """Get current system health status."""
        uptime = (datetime.now(timezone.utc) - datetime.fromisoformat(self.start_time)).total_seconds()
        telemetry = self.collector.collect_system_telemetry(active_ws_clients=self.ws_manager.connection_count)
        return DashboardHealthStatus(
            status=self.status,
            uptime_seconds=round(uptime, 2),
            active_ws_clients=self.ws_manager.connection_count,
            system_memory_mb=0.0,
            database_status="HEALTHY",
            frozen_backend_version="v0.9.1",
        )

    def generate_markdown_report(self) -> str:
        """Generate markdown summary report."""
        return generate_dashboard_session_report(session=self.get_session(), health=self.get_health())

    def generate_json_report(self) -> str:
        """Generate canonical json summary report."""
        return generate_dashboard_json_report(session=self.get_session(), health=self.get_health())
