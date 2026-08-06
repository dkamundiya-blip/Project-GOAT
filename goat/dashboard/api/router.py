"""
Project GOAT v1.0 — Dashboard Router Specification
"""

from typing import Any, Callable, Dict, Optional

from goat.dashboard.api.rest import DashboardRESTHandler
from goat.dashboard.core.models import APIResponsePayload, DashboardHealthStatus
from goat.dashboard.persistence.sqlite import DashboardReadOnlyRepositoryAdapter
from goat.dashboard.telemetry.collector import SystemTelemetryCollector


class DashboardAPIRouter:
    """Independent API Router handling HTTP route routing."""

    def __init__(
        self,
        repo: DashboardReadOnlyRepositoryAdapter,
        collector: SystemTelemetryCollector,
        market_data_engine: Optional[Any] = None,
    ) -> None:
        self.handler = DashboardRESTHandler(repo=repo, collector=collector)
        
        # Lazy initialization to avoid circular imports between dashboard and market_data packages
        from goat.market_data.api.router import MarketDataAPIRouter
        from goat.market_data.engine import LiveMarketDataIngestionEngine

        self.market_data_engine = market_data_engine or LiveMarketDataIngestionEngine()
        self.market_data_router = MarketDataAPIRouter(self.market_data_engine)

        self.routes: Dict[str, Callable[..., Any]] = {
            "/health": self.handler.get_health,
            "/api/v1/summary": self.handler.get_summary,
            "/api/v1/hypotheses": self.handler.get_hypotheses,
            "/api/v1/governance": self.handler.get_governance,
            "/api/v1/symbols": self.handler.get_symbols,
        }

    def dispatch(self, path: str, **kwargs: Any) -> Optional[Any]:
        """Dispatch route by path."""
        if route_fn := self.routes.get(path):
            return route_fn(**kwargs) if kwargs else route_fn()

        if path.startswith("/api/v1/market-data"):
            return self.market_data_router.dispatch(path, **kwargs)

        return None

    async def dispatch_async(self, path: str, **kwargs: Any) -> Optional[Any]:
        """Dispatch async route by path."""
        if path.startswith("/api/v1/market-data"):
            return await self.market_data_router.dispatch_async(path, **kwargs)
        return None


def create_dashboard_router(
    repo: DashboardReadOnlyRepositoryAdapter,
    collector: SystemTelemetryCollector,
    market_data_engine: Optional[Any] = None,
) -> DashboardAPIRouter:
    """Build and configure DashboardAPIRouter instance."""
    return DashboardAPIRouter(repo=repo, collector=collector, market_data_engine=market_data_engine)
