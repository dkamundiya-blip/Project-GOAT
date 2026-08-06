"""
Project GOAT v1.0 — Dashboard Reporting Package
"""

from goat.dashboard.reporting.reports import (
    generate_dashboard_json_report,
    generate_dashboard_session_report,
)

__all__ = ["generate_dashboard_session_report", "generate_dashboard_json_report"]
