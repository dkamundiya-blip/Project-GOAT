"""
Project GOAT v0.8 — Operational Monitoring Persistence Repositories

Implements transactional SQLite persistence for:
- SystemHealthRepository
- HeartbeatRepository
- TelemetryRepository
- DiagnosticsRepository
- MonitoringReportRepository

Enforces WAL journal mode, foreign key constraints, replayability, ON CONFLICT DO UPDATE, and deterministic serialization.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from goat.monitoring.core.models import (
    HealthAlert,
    HeartbeatRecord,
    MonitoringSummary,
    ReliabilityAssessment,
    SubsystemHealth,
    SystemHealth,
    TelemetrySnapshot,
    WatchdogStatus,
)

MONITORING_SCHEMA_VERSION = 1


class SQLiteMonitoringRepository:
    """Transactional SQLite WAL repository managing operational monitoring entities."""

    def __init__(self, db_path: str | Path):
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._create_tables()

    def _create_tables(self) -> None:
        """Initialize database schema with versioning."""
        with self._conn:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS monitoring_schema_version (
                    version INTEGER PRIMARY KEY
                );

                INSERT OR IGNORE INTO monitoring_schema_version (version) VALUES (1);

                CREATE TABLE IF NOT EXISTS system_health_records (
                    health_id TEXT PRIMARY KEY,
                    overall_health TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL UNIQUE,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS subsystem_health_records (
                    subsystem_health_id TEXT PRIMARY KEY,
                    subsystem_name TEXT NOT NULL,
                    health_level TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL UNIQUE,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS heartbeats (
                    heartbeat_id TEXT PRIMARY KEY,
                    subsystem_name TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS health_alerts (
                    alert_id TEXT PRIMARY KEY,
                    subsystem_name TEXT NOT NULL,
                    alert_level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS telemetry_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    cpu_usage REAL NOT NULL,
                    memory_usage REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    canonical_hash TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS monitoring_reports (
                    report_id TEXT PRIMARY KEY,
                    report_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    content TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );
            """)

    def close(self) -> None:
        self._conn.close()

    # ------------------------------------------------------------------
    # Health Operations
    # ------------------------------------------------------------------

    def save_system_health(self, health: SystemHealth) -> None:
        json_str = health.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO system_health_records (
                    health_id, overall_health, timestamp, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(health_id) DO UPDATE SET
                    overall_health=excluded.overall_health,
                    json_data=excluded.json_data
                """,
                (
                    health.health_id,
                    health.overall_health.value if hasattr(health.overall_health, "value") else str(health.overall_health),
                    health.timestamp,
                    health.canonical_hash,
                    json_str,
                ),
            )

    def get_system_health(self, health_id: str) -> SystemHealth | None:
        cursor = self._conn.execute(
            "SELECT json_data FROM system_health_records WHERE health_id = ?",
            (health_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return SystemHealth.model_validate_json(row["json_data"])

    def save_subsystem_health(self, health: SubsystemHealth) -> None:
        json_str = health.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO subsystem_health_records (
                    subsystem_health_id, subsystem_name, health_level, timestamp, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(subsystem_health_id) DO UPDATE SET
                    health_level=excluded.health_level,
                    json_data=excluded.json_data
                """,
                (
                    health.subsystem_health_id,
                    health.subsystem_name.value if hasattr(health.subsystem_name, "value") else str(health.subsystem_name),
                    health.health_level.value if hasattr(health.health_level, "value") else str(health.health_level),
                    health.timestamp,
                    health.canonical_hash,
                    json_str,
                ),
            )

    # ------------------------------------------------------------------
    # Heartbeat Operations
    # ------------------------------------------------------------------

    def save_heartbeat(self, heartbeat: HeartbeatRecord) -> None:
        json_str = heartbeat.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO heartbeats (
                    heartbeat_id, subsystem_name, sequence, timestamp, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    heartbeat.heartbeat_id,
                    heartbeat.subsystem_name.value if hasattr(heartbeat.subsystem_name, "value") else str(heartbeat.subsystem_name),
                    heartbeat.sequence,
                    heartbeat.timestamp,
                    heartbeat.canonical_hash,
                    json_str,
                ),
            )

    def get_heartbeats(self, subsystem_name: str) -> list[HeartbeatRecord]:
        cursor = self._conn.execute(
            "SELECT json_data FROM heartbeats WHERE subsystem_name = ? ORDER BY sequence ASC",
            (subsystem_name,),
        )
        return [HeartbeatRecord.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Alert & Telemetry Operations
    # ------------------------------------------------------------------

    def save_alert(self, alert: HealthAlert) -> None:
        json_str = alert.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO health_alerts (
                    alert_id, subsystem_name, alert_level, message, timestamp, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alert.alert_id,
                    alert.subsystem_name.value if hasattr(alert.subsystem_name, "value") else str(alert.subsystem_name),
                    alert.alert_level.value if hasattr(alert.alert_level, "value") else str(alert.alert_level),
                    alert.message,
                    alert.timestamp,
                    alert.canonical_hash,
                    json_str,
                ),
            )

    def get_alerts(self, subsystem_name: str = "") -> list[HealthAlert]:
        if subsystem_name:
            cursor = self._conn.execute(
                "SELECT json_data FROM health_alerts WHERE subsystem_name = ? ORDER BY timestamp ASC",
                (subsystem_name,),
            )
        else:
            cursor = self._conn.execute("SELECT json_data FROM health_alerts ORDER BY timestamp ASC")
        return [HealthAlert.model_validate_json(row["json_data"]) for row in cursor.fetchall()]

    def save_telemetry(self, telemetry: TelemetrySnapshot) -> None:
        json_str = telemetry.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO telemetry_snapshots (
                    snapshot_id, cpu_usage, memory_usage, timestamp, canonical_hash, json_data
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    telemetry.snapshot_id,
                    telemetry.cpu_usage,
                    telemetry.memory_usage,
                    telemetry.timestamp,
                    telemetry.canonical_hash,
                    json_str,
                ),
            )

    def save_report(self, report_id: str, report_type: str, timestamp: str, content: str, json_data: dict[str, Any]) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO monitoring_reports (
                    report_id, report_type, timestamp, content, json_data
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    report_type,
                    timestamp,
                    content,
                    json.dumps(json_data, sort_keys=True),
                ),
            )


# Mapped repository export classes
class SystemHealthRepository(SQLiteMonitoringRepository):
    pass

class HeartbeatRepository(SQLiteMonitoringRepository):
    pass

class TelemetryRepository(SQLiteMonitoringRepository):
    pass

class DiagnosticsRepository(SQLiteMonitoringRepository):
    pass

class MonitoringReportRepository(SQLiteMonitoringRepository):
    pass
