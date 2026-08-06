"""
Project GOAT v0.7 — SQLite Persistence for Scientific Simulation Engine

Provides repositories supporting round-trip persistence and foreign-key integrity:
- SimulationScenarioRepository
- SimulationRunRepository
- SimulationResultRepository
- WalkForwardRepository
- PerformanceAttributionRepository
- SimulationReportRepository
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.simulation.core.models import (
    PerformanceAttribution,
    SimulationResult,
    SimulationRun,
    SimulationScenario,
    WalkForwardWindow,
)


def init_simulation_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and foreign key pragmas for Scientific Simulation Engine."""
    conn.execute("PRAGMA foreign_keys = ON;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS simulation_scenarios (
                scenario_id TEXT PRIMARY KEY,
                qualification_id TEXT NOT NULL,
                composite_id TEXT NOT NULL,
                regime_id TEXT NOT NULL,
                dataset_reference TEXT NOT NULL,
                simulation_window_json TEXT NOT NULL,
                configuration_json TEXT NOT NULL,
                creation_timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS simulation_runs (
                run_id TEXT PRIMARY KEY,
                scenario_id TEXT NOT NULL,
                execution_timestamp TEXT NOT NULL,
                replay_seed INTEGER NOT NULL,
                deterministic_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (scenario_id) REFERENCES simulation_scenarios(scenario_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS simulation_results (
                result_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                simulated_events_json TEXT NOT NULL,
                outcome_summary_json TEXT NOT NULL,
                validation_status TEXT NOT NULL,
                statistical_metrics_json TEXT NOT NULL,
                attribution_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES simulation_runs(run_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS walk_forward_windows (
                window_id TEXT PRIMARY KEY,
                training_period_json TEXT NOT NULL,
                validation_period_json TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS performance_attributions (
                attribution_id TEXT PRIMARY KEY,
                result_id TEXT NOT NULL,
                contributing_edges_json TEXT NOT NULL,
                contributing_regimes_json TEXT NOT NULL,
                contributing_evidence_json TEXT NOT NULL,
                contribution_breakdown_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (result_id) REFERENCES simulation_results(result_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS simulation_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                report_json TEXT NOT NULL
            );
        """)


class SimulationScenarioRepository:
    """Repository for storing and retrieving SimulationScenario models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_simulation_db(self.conn)

    def save_scenario(self, scenario: SimulationScenario) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO simulation_scenarios (
                    scenario_id, qualification_id, composite_id, regime_id,
                    dataset_reference, simulation_window_json, configuration_json,
                    creation_timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scenario.scenario_id,
                    scenario.qualification_id,
                    scenario.composite_id,
                    scenario.regime_id,
                    scenario.dataset_reference,
                    json.dumps(scenario.simulation_window, sort_keys=True),
                    json.dumps(scenario.configuration, sort_keys=True),
                    scenario.creation_timestamp,
                    json.dumps(scenario.metadata, sort_keys=True),
                    scenario.canonical_hash,
                ),
            )

    def get_scenario(self, scenario_id: str) -> SimulationScenario | None:
        cursor = self.conn.execute(
            """
            SELECT scenario_id, qualification_id, composite_id, regime_id,
                   dataset_reference, simulation_window_json, configuration_json,
                   creation_timestamp, metadata_json, canonical_hash
            FROM simulation_scenarios WHERE scenario_id = ?
            """,
            (scenario_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return SimulationScenario(
            scenario_id=row[0],
            qualification_id=row[1],
            composite_id=row[2],
            regime_id=row[3],
            dataset_reference=row[4],
            simulation_window=json.loads(row[5]),
            configuration=json.loads(row[6]),
            creation_timestamp=row[7],
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )

    def list_scenarios(self) -> list[SimulationScenario]:
        cursor = self.conn.execute("SELECT scenario_id FROM simulation_scenarios ORDER BY scenario_id ASC")
        scenarios = []
        for row in cursor.fetchall():
            s = self.get_scenario(row[0])
            if s:
                scenarios.append(s)
        return scenarios


class SimulationRunRepository:
    """Repository for storing and retrieving SimulationRun models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_simulation_db(self.conn)

    def save_run(self, run: SimulationRun) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO simulation_runs (
                    run_id, scenario_id, execution_timestamp, replay_seed,
                    deterministic_hash, status, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.scenario_id,
                    run.execution_timestamp,
                    run.replay_seed,
                    run.deterministic_hash,
                    run.status.value if hasattr(run.status, "value") else str(run.status),
                    json.dumps(run.metadata, sort_keys=True),
                    run.canonical_hash,
                ),
            )

    def get_run(self, run_id: str) -> SimulationRun | None:
        cursor = self.conn.execute(
            """
            SELECT run_id, scenario_id, execution_timestamp, replay_seed,
                   deterministic_hash, status, metadata_json, canonical_hash
            FROM simulation_runs WHERE run_id = ?
            """,
            (run_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return SimulationRun(
            run_id=row[0],
            scenario_id=row[1],
            execution_timestamp=row[2],
            replay_seed=row[3],
            deterministic_hash=row[4],
            status=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class SimulationResultRepository:
    """Repository for storing and retrieving SimulationResult models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_simulation_db(self.conn)

    def save_result(self, result: SimulationResult) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO simulation_results (
                    result_id, run_id, simulated_events_json, outcome_summary_json,
                    validation_status, statistical_metrics_json, attribution_json,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.result_id,
                    result.run_id,
                    json.dumps(result.simulated_events, sort_keys=True),
                    json.dumps(result.outcome_summary, sort_keys=True),
                    result.validation_status.value if hasattr(result.validation_status, "value") else str(result.validation_status),
                    json.dumps(result.statistical_metrics, sort_keys=True),
                    json.dumps(result.attribution, sort_keys=True),
                    json.dumps(result.metadata, sort_keys=True),
                    result.canonical_hash,
                ),
            )

    def get_result(self, result_id: str) -> SimulationResult | None:
        cursor = self.conn.execute(
            """
            SELECT result_id, run_id, simulated_events_json, outcome_summary_json,
                   validation_status, statistical_metrics_json, attribution_json,
                   metadata_json, canonical_hash
            FROM simulation_results WHERE result_id = ?
            """,
            (result_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return SimulationResult(
            result_id=row[0],
            run_id=row[1],
            simulated_events=json.loads(row[2]),
            outcome_summary=json.loads(row[3]),
            validation_status=row[4],
            statistical_metrics=json.loads(row[5]),
            attribution=json.loads(row[6]),
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class WalkForwardRepository:
    """Repository for storing and retrieving WalkForwardWindow models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_simulation_db(self.conn)

    def save_window(self, window: WalkForwardWindow) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO walk_forward_windows (
                    window_id, training_period_json, validation_period_json,
                    sequence_number, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    window.window_id,
                    json.dumps(window.training_period, sort_keys=True),
                    json.dumps(window.validation_period, sort_keys=True),
                    window.sequence_number,
                    json.dumps(window.metadata, sort_keys=True),
                    window.canonical_hash,
                ),
            )

    def get_window(self, window_id: str) -> WalkForwardWindow | None:
        cursor = self.conn.execute(
            """
            SELECT window_id, training_period_json, validation_period_json,
                   sequence_number, metadata_json, canonical_hash
            FROM walk_forward_windows WHERE window_id = ?
            """,
            (window_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return WalkForwardWindow(
            window_id=row[0],
            training_period=json.loads(row[1]),
            validation_period=json.loads(row[2]),
            sequence_number=row[3],
            metadata=json.loads(row[4]),
            canonical_hash=row[5],
        )


class PerformanceAttributionRepository:
    """Repository for storing and retrieving PerformanceAttribution models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_simulation_db(self.conn)

    def save_attribution(self, attribution: PerformanceAttribution) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO performance_attributions (
                    attribution_id, result_id, contributing_edges_json,
                    contributing_regimes_json, contributing_evidence_json,
                    contribution_breakdown_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attribution.attribution_id,
                    attribution.result_id,
                    json.dumps(attribution.contributing_edges, sort_keys=True),
                    json.dumps(attribution.contributing_regimes, sort_keys=True),
                    json.dumps(attribution.contributing_evidence, sort_keys=True),
                    json.dumps(attribution.contribution_breakdown, sort_keys=True),
                    json.dumps(attribution.metadata, sort_keys=True),
                    attribution.canonical_hash,
                ),
            )

    def get_attribution(self, attribution_id: str) -> PerformanceAttribution | None:
        cursor = self.conn.execute(
            """
            SELECT attribution_id, result_id, contributing_edges_json,
                   contributing_regimes_json, contributing_evidence_json,
                   contribution_breakdown_json, metadata_json, canonical_hash
            FROM performance_attributions WHERE attribution_id = ?
            """,
            (attribution_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return PerformanceAttribution(
            attribution_id=row[0],
            result_id=row[1],
            contributing_edges=json.loads(row[2]),
            contributing_regimes=json.loads(row[3]),
            contributing_evidence=json.loads(row[4]),
            contribution_breakdown=json.loads(row[5]),
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class SimulationReportRepository:
    """Repository for storing and retrieving report objects."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_simulation_db(self.conn)

    def save_report(self, report_id: str, report_type: str, timestamp: str, report_model: Any) -> None:
        report_json = report_model.to_json() if hasattr(report_model, "to_json") else json.dumps(report_model.dict(), sort_keys=True)
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO simulation_reports (report_id, report_type, timestamp, report_json) VALUES (?, ?, ?, ?)",
                (report_id, report_type, timestamp, report_json),
            )

    def get_report_json(self, report_id: str) -> str | None:
        cursor = self.conn.execute(
            "SELECT report_json FROM simulation_reports WHERE report_id = ?",
            (report_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
