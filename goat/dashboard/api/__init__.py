"""
Project GOAT v1.0 — Dashboard API Package
"""

from goat.dashboard.api.rest import DashboardRESTHandler
from goat.dashboard.api.router import create_dashboard_router

__all__ = ["DashboardRESTHandler", "create_dashboard_router"]
