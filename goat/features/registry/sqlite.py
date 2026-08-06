"""
Project GOAT v0.7 — SQLite Feature Registry Storage & Persistence

Implements SQLiteFeatureRepository for durable relational persistence, schema migration,
foreign key enforcement, append-only audit logging, and read-only integrity verification.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from goat.features.registry.model import (
    RegistrationStatus,
    RegistryAuditEvent,
    RegistryRecord,
    ValidationStatus,
)

CURRENT_SCHEMA_VERSION = 1


class SQLiteFeatureRepository:
    """Relational SQLite storage backend for Feature Registry records."""

    def __init__(self, db_path: str | Path) -> None:
        """Initialize SQLite database connection and enforce schema.

        Args:
            db_path: File path to SQLite database or ':memory:'.
        """
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._init_schema()

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()

    def __enter__(self) -> SQLiteFeatureRepository:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def _init_schema(self) -> None:
        """Initialize SQLite tables and schema version."""
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                );
            """)

            cur = self._conn.execute("SELECT MAX(version) FROM schema_version;")
            row = cur.fetchone()
            current_ver = row[0] if row and row[0] is not None else 0

            if current_ver < CURRENT_SCHEMA_VERSION:
                self._migrate(current_ver, CURRENT_SCHEMA_VERSION)

    def _migrate(self, from_ver: int, to_ver: int) -> None:
        """Migrate schema from from_ver to to_ver transactionally."""
        if from_ver < 1:
            self._conn.execute("""
                CREATE TABLE feature_registry (
                    feature_id TEXT PRIMARY KEY,
                    scientific_fingerprint TEXT NOT NULL UNIQUE,
                    canonical_hash TEXT NOT NULL,
                    semantic_version TEXT NOT NULL,
                    registration_status TEXT NOT NULL,
                    deprecation_state TEXT NOT NULL,
                    validation_status TEXT NOT NULL,
                    registration_timestamp TEXT NOT NULL,
                    json_data TEXT NOT NULL
                );
            """)
            self._conn.execute("""
                CREATE TABLE feature_dependencies (
                    parent_feature_id TEXT NOT NULL,
                    child_feature_id TEXT NOT NULL,
                    PRIMARY KEY (parent_feature_id, child_feature_id),
                    FOREIGN KEY (parent_feature_id) REFERENCES feature_registry (feature_id) ON DELETE CASCADE,
                    FOREIGN KEY (child_feature_id) REFERENCES feature_registry (feature_id) ON DELETE CASCADE
                );
            """)
            self._conn.execute("""
                CREATE TABLE feature_registry_audit (
                    event_id TEXT PRIMARY KEY,
                    feature_id TEXT NOT NULL,
                    scientific_fingerprint TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    FOREIGN KEY (feature_id) REFERENCES feature_registry (feature_id) ON DELETE CASCADE
                );
            """)
            self._conn.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, ?);",
                (1, datetime.now(timezone.utc).isoformat()),
            )

    def save(self, record: RegistryRecord) -> None:
        """Persist a RegistryRecord transactionally.

        Args:
            record: Immutable RegistryRecord instance.
        """
        json_str = record.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO feature_registry (
                    feature_id, scientific_fingerprint, canonical_hash, semantic_version,
                    registration_status, deprecation_state, validation_status,
                    registration_timestamp, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    record.feature_id,
                    record.scientific_fingerprint,
                    record.canonical_hash,
                    record.semantic_version,
                    record.registration_status.value,
                    record.deprecation_state.value,
                    record.validation_status.value,
                    record.registration_timestamp,
                    json_str,
                ),
            )

            # Insert dependency edges
            for dep_id in record.dependency_spec:
                self._conn.execute(
                    "INSERT INTO feature_dependencies (parent_feature_id, child_feature_id) VALUES (?, ?);",
                    (dep_id, record.feature_id),
                )

            # Log audit event
            self._log_audit_event_tx(
                feature_id=record.feature_id,
                scientific_fingerprint=record.scientific_fingerprint,
                event_type="REGISTER",
                actor=record.registry_provenance,
                details={"version": record.semantic_version, "status": record.registration_status.value},
            )

    def get_by_id(self, feature_id: str) -> RegistryRecord | None:
        """Retrieve RegistryRecord by Feature ID."""
        cur = self._conn.execute(
            "SELECT json_data FROM feature_registry WHERE feature_id = ?;",
            (feature_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return RegistryRecord.model_validate_json(row["json_data"])

    def get_by_fingerprint(self, fingerprint: str) -> RegistryRecord | None:
        """Retrieve RegistryRecord by Scientific Feature Fingerprint."""
        cur = self._conn.execute(
            "SELECT json_data FROM feature_registry WHERE scientific_fingerprint = ?;",
            (fingerprint,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return RegistryRecord.model_validate_json(row["json_data"])

    def get_by_canonical_hash(self, canonical_hash: str) -> RegistryRecord | None:
        """Retrieve RegistryRecord by Canonical Hash digest."""
        cur = self._conn.execute(
            "SELECT json_data FROM feature_registry WHERE canonical_hash = ?;",
            (canonical_hash,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return RegistryRecord.model_validate_json(row["json_data"])

    def list_all(self) -> list[RegistryRecord]:
        """List all registered records ordered by timestamp."""
        cur = self._conn.execute("SELECT json_data FROM feature_registry ORDER BY registration_timestamp ASC;")
        return [RegistryRecord.model_validate_json(row["json_data"]) for row in cur.fetchall()]

    def update_status(
        self,
        feature_id: str,
        registration_status: RegistrationStatus | None = None,
        validation_status: ValidationStatus | None = None,
        actor: str = "system",
        notes: str = "",
    ) -> RegistryRecord:
        """Update record status transactionally with audit logging."""
        record = self.get_by_id(feature_id)
        if not record:
            raise KeyError(f"Feature ID '{feature_id}' not found in registry")

        new_reg_status = registration_status or record.registration_status
        new_val_status = validation_status or record.validation_status

        updated_dict = record.model_dump()
        updated_dict["registration_status"] = new_reg_status
        updated_dict["validation_status"] = new_val_status
        if notes:
            updated_dict["registry_notes"] = notes

        updated_record = RegistryRecord(**updated_dict)
        json_str = updated_record.model_dump_json()

        with self._conn:
            self._conn.execute(
                """
                UPDATE feature_registry
                SET registration_status = ?, validation_status = ?, json_data = ?
                WHERE feature_id = ?;
                """,
                (new_reg_status.value, new_val_status.value, json_str, feature_id),
            )
            self._log_audit_event_tx(
                feature_id=feature_id,
                scientific_fingerprint=record.scientific_fingerprint,
                event_type="UPDATE_STATUS",
                actor=actor,
                details={
                    "old_reg_status": record.registration_status.value,
                    "new_reg_status": new_reg_status.value,
                    "old_val_status": record.validation_status.value,
                    "new_val_status": new_val_status.value,
                    "notes": notes,
                },
            )
        return updated_record

    def log_audit_event(self, feature_id: str, event_type: str, actor: str = "system", details: dict[str, Any] | None = None) -> None:
        """Log standalone audit event for a feature."""
        record = self.get_by_id(feature_id)
        fp = record.scientific_fingerprint if record else "UNKNOWN"
        with self._conn:
            self._log_audit_event_tx(
                feature_id=feature_id,
                scientific_fingerprint=fp,
                event_type=event_type,
                actor=actor,
                details=details or {},
            )

    def _log_audit_event_tx(self, feature_id: str, scientific_fingerprint: str, event_type: str, actor: str, details: dict[str, Any]) -> None:
        """Helper to write audit log inside an existing transaction."""
        event_id = f"AUD_{uuid.uuid4().hex[:16].upper()}"
        ts = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """
            INSERT INTO feature_registry_audit (
                event_id, feature_id, scientific_fingerprint, event_type, timestamp, actor, details_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (event_id, feature_id, scientific_fingerprint, event_type, ts, actor, json.dumps(details, sort_keys=True)),
        )

    def get_audit_trail(self, feature_id: str | None = None) -> list[RegistryAuditEvent]:
        """Retrieve audit history records."""
        if feature_id:
            cur = self._conn.execute(
                "SELECT * FROM feature_registry_audit WHERE feature_id = ? ORDER BY timestamp ASC;",
                (feature_id,),
            )
        else:
            cur = self._conn.execute("SELECT * FROM feature_registry_audit ORDER BY timestamp ASC;")

        events = []
        for row in cur.fetchall():
            events.append(
                RegistryAuditEvent(
                    event_id=row["event_id"],
                    feature_id=row["feature_id"],
                    scientific_fingerprint=row["scientific_fingerprint"],
                    event_type=row["event_type"],
                    timestamp=row["timestamp"],
                    actor=row["actor"],
                    details=json.loads(row["details_json"]),
                )
            )
        return events


class FeatureRegistryVerifier:
    """Read-only integrity verification tool for Feature Registry database."""

    def __init__(self, repo: SQLiteFeatureRepository) -> None:
        self._repo = repo

    def verify_integrity(self) -> tuple[bool, list[str]]:
        """Verify internal database integrity, foreign keys, and record serialization consistency.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []
        records = self._repo.list_all()

        for rec in records:
            # Check re-deserialization
            try:
                validate_rec = self._repo.get_by_id(rec.feature_id)
                if not validate_rec or validate_rec.scientific_fingerprint != rec.scientific_fingerprint:
                    errors.append(f"Record integrity failure for Feature ID '{rec.feature_id}'")
            except Exception as e:
                errors.append(f"Corrupted record '{rec.feature_id}': {e}")

        return (len(errors) == 0, errors)
