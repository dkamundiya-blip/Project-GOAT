"""
Project GOAT v1.0 — Dashboard REST Endpoints & Handlers
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from goat.dashboard.core.canonical import compute_api_payload_id
from goat.dashboard.core.enums import ServerStatus
from goat.dashboard.core.models import APIResponsePayload, DashboardHealthStatus
from goat.dashboard.persistence.sqlite import DashboardReadOnlyRepositoryAdapter
from goat.dashboard.telemetry.collector import SystemTelemetryCollector


class DashboardRESTHandler:
    """REST endpoint business logic handlers."""

    def __init__(
        self,
        repo: DashboardReadOnlyRepositoryAdapter,
        collector: SystemTelemetryCollector,
    ) -> None:
        self.repo = repo
        self.collector = collector
        self.start_time = datetime.now(timezone.utc)

    def get_health(self) -> DashboardHealthStatus:
        """System health endpoint handler."""
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        telemetry = self.collector.collect_system_telemetry()
        return DashboardHealthStatus(
            status=ServerStatus.RUNNING,
            uptime_seconds=round(uptime, 2),
            active_ws_clients=0,
            system_memory_mb=telemetry.payload.get("memory_used_mb", 0.0),
            database_status="HEALTHY",
            frozen_backend_version="v0.9.1",
        )

    def get_summary(self) -> APIResponsePayload:
        now = datetime.now(timezone.utc).isoformat()
        data = self.repo.get_dashboard_summary_metrics()
        payload_id = compute_api_payload_id("/api/v1/summary", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route="/api/v1/summary",
            status_code=200,
            timestamp=now,
            data=data,
            meta={"frozen_backend": "v0.9.1"},
        )

    def get_hypotheses(self, limit: int = 50) -> APIResponsePayload:
        now = datetime.now(timezone.utc).isoformat()
        items = self.repo.get_active_hypotheses(limit=limit)
        payload_id = compute_api_payload_id("/api/v1/hypotheses", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route="/api/v1/hypotheses",
            status_code=200,
            timestamp=now,
            data={"hypotheses": items, "count": len(items)},
            meta={"frozen_backend": "v0.9.1"},
        )

    def get_governance(self, limit: int = 50) -> APIResponsePayload:
        now = datetime.now(timezone.utc).isoformat()
        items = self.repo.get_governance_decisions(limit=limit)
        payload_id = compute_api_payload_id("/api/v1/governance", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route="/api/v1/governance",
            status_code=200,
            timestamp=now,
            data={"decisions": items, "count": len(items)},
            meta={"frozen_backend": "v0.9.1"},
        )

    def get_symbols(self) -> APIResponsePayload:
        now = datetime.now(timezone.utc).isoformat()
        symbols = self.repo.get_market_symbols_status()
        payload_id = compute_api_payload_id("/api/v1/symbols", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route="/api/v1/symbols",
            status_code=200,
            timestamp=now,
            data={"symbols": symbols, "count": len(symbols)},
            meta={"frozen_backend": "v0.9.1"},
        )
