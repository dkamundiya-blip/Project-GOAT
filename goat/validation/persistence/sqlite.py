"""
Project GOAT v0.7 — SQLite Validation Repository

Implements transactional SQLite persistence for Hypotheses, Validation Runs,
Evidence, Decisions, Reports, and Audit Events.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from goat.validation.core.hypothesis import ScientificHypothesis
from goat.validation.core.run import ValidationRun
from goat.validation.decisions.models import ValidationDecision
from goat.validation.evidence.models import ValidationEvidence
from goat.validation.reporting.models import ValidationReport

VALIDATION_SCHEMA_VERSION = 1


class SQLiteValidationRepository:
    """Transactional SQLite repository for scientific hypothesis validation persistence."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()

    def _create_tables(self) -> None:
        """Enforce Schema v1 tables."""
        with self._conn:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS validation_schema_version (
                    version INTEGER PRIMARY KEY
                );

                INSERT OR IGNORE INTO validation_schema_version (version) VALUES (1);

                CREATE TABLE IF NOT EXISTS validation_hypotheses (
                    hypothesis_id TEXT PRIMARY KEY,
                    canonical_hash TEXT NOT NULL,
                    scientific_fingerprint TEXT NOT NULL,
                    hypothesis_version TEXT NOT NULL,
                    title TEXT NOT NULL,
                    validation_state TEXT NOT NULL,
                    creation_time TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS validation_runs (
                    validation_id TEXT PRIMARY KEY,
                    canonical_hash TEXT NOT NULL,
                    scientific_fingerprint TEXT NOT NULL,
                    hypothesis_id TEXT NOT NULL,
                    validation_state TEXT NOT NULL,
                    creation_timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (hypothesis_id) REFERENCES validation_hypotheses(hypothesis_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS validation_evidence (
                    evidence_id TEXT PRIMARY KEY,
                    evidence_hash TEXT NOT NULL,
                    validation_run_id TEXT NOT NULL,
                    evidence_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS validation_decisions (
                    decision_id TEXT PRIMARY KEY,
                    decision_hash TEXT NOT NULL,
                    validation_run_id TEXT NOT NULL,
                    decision_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS validation_reports (
                    report_id TEXT PRIMARY KEY,
                    validation_run_id TEXT NOT NULL,
                    hypothesis_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS validation_audit_events (
                    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_timestamp TEXT NOT NULL,
                    event_data TEXT NOT NULL
                );
            """)

    # ------------------------------------------------------------------
    # Schema Version
    # ------------------------------------------------------------------

    def get_schema_version(self) -> int:
        """Retrieve current schema version."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT version FROM validation_schema_version;")
        row = cursor.fetchone()
        return row["version"] if row else 0

    # ------------------------------------------------------------------
    # Hypothesis CRUD
    # ------------------------------------------------------------------

    def save_hypothesis(self, hypothesis: ScientificHypothesis) -> None:
        """Persist a ScientificHypothesis transactionally."""
        json_str = hypothesis.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO validation_hypotheses (
                    hypothesis_id, canonical_hash, scientific_fingerprint, hypothesis_version,
                    title, validation_state, creation_time, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(hypothesis_id) DO UPDATE SET
                    validation_state = excluded.validation_state,
                    json_data = excluded.json_data;
                """,
                (
                    hypothesis.hypothesis_id,
                    hypothesis.canonical_hash,
                    hypothesis.scientific_fingerprint,
                    hypothesis.hypothesis_version,
                    hypothesis.title,
                    hypothesis.validation_state.value,
                    hypothesis.creation_time,
                    json_str,
                ),
            )

    def get_hypothesis(self, hypothesis_id: str) -> ScientificHypothesis | None:
        """Retrieve ScientificHypothesis by Hypothesis ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM validation_hypotheses WHERE hypothesis_id = ?;", (hypothesis_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ScientificHypothesis(**json.loads(row["json_data"]))

    def list_hypotheses(self) -> list[ScientificHypothesis]:
        """List all persisted hypotheses."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM validation_hypotheses ORDER BY creation_time;")
        return [ScientificHypothesis(**json.loads(row["json_data"])) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Validation Run CRUD
    # ------------------------------------------------------------------

    def save_run(self, run: ValidationRun) -> None:
        """Persist a ValidationRun transactionally."""
        json_str = run.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO validation_runs (
                    validation_id, canonical_hash, scientific_fingerprint,
                    hypothesis_id, validation_state, creation_timestamp, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(validation_id) DO UPDATE SET
                    validation_state = excluded.validation_state,
                    json_data = excluded.json_data;
                """,
                (
                    run.validation_id,
                    run.canonical_hash,
                    run.scientific_fingerprint,
                    run.hypothesis_id,
                    run.validation_state.value,
                    run.creation_timestamp,
                    json_str,
                ),
            )

    def get_run(self, validation_id: str) -> ValidationRun | None:
        """Retrieve ValidationRun by Validation Run ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM validation_runs WHERE validation_id = ?;", (validation_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ValidationRun(**json.loads(row["json_data"]))

    def list_runs(self) -> list[ValidationRun]:
        """List all persisted validation runs."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM validation_runs ORDER BY creation_timestamp;")
        return [ValidationRun(**json.loads(row["json_data"])) for row in cursor.fetchall()]

    def get_runs_for_hypothesis(self, hypothesis_id: str) -> list[ValidationRun]:
        """Retrieve all runs for a hypothesis."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT json_data FROM validation_runs WHERE hypothesis_id = ? ORDER BY creation_timestamp;",
            (hypothesis_id,),
        )
        return [ValidationRun(**json.loads(row["json_data"])) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Evidence CRUD
    # ------------------------------------------------------------------

    def save_evidence(self, evidence: ValidationEvidence) -> None:
        """Persist a ValidationEvidence record."""
        json_str = evidence.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO validation_evidence (
                    evidence_id, evidence_hash, validation_run_id,
                    evidence_type, timestamp, json_data
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(evidence_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (
                    evidence.evidence_id,
                    evidence.evidence_hash,
                    evidence.validation_run_id,
                    evidence.evidence_type,
                    evidence.timestamp,
                    json_str,
                ),
            )

    def get_evidence(self, evidence_id: str) -> ValidationEvidence | None:
        """Retrieve ValidationEvidence by Evidence ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM validation_evidence WHERE evidence_id = ?;", (evidence_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ValidationEvidence(**json.loads(row["json_data"]))

    def get_evidence_for_run(self, validation_run_id: str) -> list[ValidationEvidence]:
        """Retrieve all evidence for a validation run."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT json_data FROM validation_evidence WHERE validation_run_id = ? ORDER BY timestamp;",
            (validation_run_id,),
        )
        return [ValidationEvidence(**json.loads(row["json_data"])) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Decision CRUD
    # ------------------------------------------------------------------

    def save_decision(self, decision: ValidationDecision) -> None:
        """Persist a ValidationDecision."""
        json_str = decision.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO validation_decisions (
                    decision_id, decision_hash, validation_run_id,
                    decision_type, timestamp, json_data
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(decision_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (
                    decision.decision_id,
                    decision.decision_hash,
                    decision.validation_run_id,
                    decision.decision_type.value,
                    decision.timestamp,
                    json_str,
                ),
            )

    def get_decision(self, decision_id: str) -> ValidationDecision | None:
        """Retrieve ValidationDecision by Decision ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM validation_decisions WHERE decision_id = ?;", (decision_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ValidationDecision(**json.loads(row["json_data"]))

    def get_decision_for_run(self, validation_run_id: str) -> ValidationDecision | None:
        """Retrieve decision for a specific validation run."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT json_data FROM validation_decisions WHERE validation_run_id = ?;",
            (validation_run_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return ValidationDecision(**json.loads(row["json_data"]))

    # ------------------------------------------------------------------
    # Report CRUD
    # ------------------------------------------------------------------

    def save_report(self, report: ValidationReport) -> None:
        """Persist a ValidationReport."""
        json_str = report.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO validation_reports (
                    report_id, validation_run_id, hypothesis_id, timestamp, json_data
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(report_id) DO UPDATE SET json_data = excluded.json_data;
                """,
                (
                    report.report_id,
                    report.validation_run_id,
                    report.hypothesis_id,
                    report.timestamp,
                    json_str,
                ),
            )

    def get_report(self, report_id: str) -> ValidationReport | None:
        """Retrieve ValidationReport by Report ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT json_data FROM validation_reports WHERE report_id = ?;", (report_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return ValidationReport(**json.loads(row["json_data"]))

    # ------------------------------------------------------------------
    # Audit Events
    # ------------------------------------------------------------------

    def save_audit_event(
        self,
        entity_id: str,
        event_type: str,
        event_timestamp: str,
        event_data: dict[str, Any],
    ) -> None:
        """Persist an audit event."""
        json_str = json.dumps(event_data, sort_keys=True, separators=(",", ":"))
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO validation_audit_events (entity_id, event_type, event_timestamp, event_data)
                VALUES (?, ?, ?, ?);
                """,
                (entity_id, event_type, event_timestamp, json_str),
            )

    def get_audit_events(self, entity_id: str) -> list[dict[str, Any]]:
        """Retrieve all audit events for an entity."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT event_type, event_timestamp, event_data FROM validation_audit_events WHERE entity_id = ? ORDER BY audit_id;",
            (entity_id,),
        )
        return [
            {
                "event_type": row["event_type"],
                "event_timestamp": row["event_timestamp"],
                "event_data": json.loads(row["event_data"]),
            }
            for row in cursor.fetchall()
        ]

    # ------------------------------------------------------------------
    # Export / Import
    # ------------------------------------------------------------------

    def export_validation_run(self, validation_id: str) -> dict[str, Any]:
        """Export a complete validation run with all related artifacts."""
        run = self.get_run(validation_id)
        if run is None:
            raise KeyError(f"Validation Run '{validation_id}' not found for export")

        evidence = self.get_evidence_for_run(validation_id)
        decision = self.get_decision_for_run(validation_id)
        audit_events = self.get_audit_events(validation_id)

        return {
            "schema_version": VALIDATION_SCHEMA_VERSION,
            "run": json.loads(run.model_dump_json()),
            "evidence": [json.loads(e.model_dump_json()) for e in evidence],
            "decision": json.loads(decision.model_dump_json()) if decision else None,
            "audit_events": audit_events,
        }

    def import_validation_run(self, data: dict[str, Any]) -> ValidationRun:
        """Import a complete validation run from exported data.

        Raises:
            ValueError: If schema version mismatch.
        """
        if data.get("schema_version") != VALIDATION_SCHEMA_VERSION:
            raise ValueError(
                f"Schema version mismatch: expected {VALIDATION_SCHEMA_VERSION}, "
                f"got {data.get('schema_version')}"
            )

        run = ValidationRun(**data["run"])
        self.save_run(run)

        for ev_data in data.get("evidence", []):
            evidence = ValidationEvidence(**ev_data)
            self.save_evidence(evidence)

        if data.get("decision"):
            decision = ValidationDecision(**data["decision"])
            self.save_decision(decision)

        return run

    # ------------------------------------------------------------------
    # Integrity Verification
    # ------------------------------------------------------------------

    def verify_integrity(self, validation_id: str) -> bool:
        """Verify persistence integrity for a validation run.

        Returns:
            True if integrity check passes.

        Raises:
            ValueError: If validation run not found or integrity fails.
        """
        run = self.get_run(validation_id)
        if run is None:
            raise ValueError(f"Validation Run '{validation_id}' not found")

        evidence = self.get_evidence_for_run(validation_id)
        for ev in evidence:
            if ev.validation_run_id != validation_id:
                raise ValueError(
                    f"Evidence '{ev.evidence_id}' has validation_run_id "
                    f"'{ev.validation_run_id}', expected '{validation_id}'"
                )

        decision = self.get_decision_for_run(validation_id)
        if decision and decision.validation_run_id != validation_id:
            raise ValueError(
                f"Decision '{decision.decision_id}' has validation_run_id "
                f"'{decision.validation_run_id}', expected '{validation_id}'"
            )

        return True

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
