"""
Project GOAT v0.6 — Edge Registry Database Schema

Defines DDL specifications, versioning, indexing, and schema initialization logic for SQLite.
"""

from __future__ import annotations

from datetime import datetime, timezone
import sqlite3

from goat.research.edge.persistence.exceptions import SchemaVersionError

CURRENT_SCHEMA_VERSION = 2

CREATE_SCHEMA_MIGRATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at_utc TEXT NOT NULL
);
"""

CREATE_CANDIDATE_EDGES_TABLE = """
CREATE TABLE IF NOT EXISTS candidate_edges (
    edge_id TEXT PRIMARY KEY,
    edge_schema_version INTEGER NOT NULL,
    causal_primitive TEXT NOT NULL,
    target_feature TEXT NOT NULL,
    economic_rationale_category TEXT NOT NULL,
    base_condition_spec_json TEXT NOT NULL,
    proposition_name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    display_labels_json TEXT NOT NULL DEFAULT '[]',
    hypothesis_ids_json TEXT NOT NULL DEFAULT '[]',
    lifecycle_state TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL
);
"""

CREATE_HYPOTHESIS_VERSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS hypothesis_versions (
    hypothesis_version TEXT PRIMARY KEY,
    edge_id TEXT NOT NULL,
    condition_parameters_json TEXT NOT NULL,
    forward_outcome_metric TEXT NOT NULL,
    forward_horizon INTEGER NOT NULL,
    created_at_utc TEXT NOT NULL,
    FOREIGN KEY (edge_id) REFERENCES candidate_edges(edge_id) ON DELETE RESTRICT
);
"""

CREATE_VALIDATION_POLICIES_TABLE = """
CREATE TABLE IF NOT EXISTS validation_policies (
    policy_hash TEXT PRIMARY KEY,
    policy_id TEXT NOT NULL,
    version TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    multiplicity_strategy TEXT NOT NULL,
    meta_analysis_method TEXT NOT NULL DEFAULT 'FISHER_COMBINED_PROBABILITY',
    stage_a_alpha REAL NOT NULL,
    stage_a_effect_min REAL NOT NULL,
    stage_a_min_sample INTEGER NOT NULL,
    stage_b_min_retention_ratio REAL NOT NULL,
    stage_c_min_folds INTEGER NOT NULL,
    stage_c_min_positive_ratio REAL NOT NULL,
    stage_c_max_fold_cv REAL NOT NULL,
    stage_d_perturbation_delta REAL NOT NULL,
    stage_d_min_stable_ratio REAL NOT NULL,
    stage_d_max_allowed_drop REAL NOT NULL,
    stage_e_fail_on_contradictory_inversion INTEGER NOT NULL,
    stage_f_min_replication_pct REAL NOT NULL,
    stage_f_meta_alpha REAL NOT NULL,
    created_at_utc TEXT NOT NULL
);
"""

CREATE_VALIDATION_CONTEXT_UNIVERSES_TABLE = """
CREATE TABLE IF NOT EXISTS validation_context_universes (
    universe_id TEXT PRIMARY KEY,
    universe_schema_version INTEGER NOT NULL,
    contexts_json TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at_utc TEXT NOT NULL
);
"""

CREATE_VALIDATION_RUNS_TABLE = """
CREATE TABLE IF NOT EXISTS validation_runs (
    validation_run_id TEXT PRIMARY KEY,
    edge_id TEXT NOT NULL,
    policy_hash TEXT NOT NULL,
    dataset_fingerprint TEXT NOT NULL,
    candidate_target_scope TEXT NOT NULL,
    goat_version TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    FOREIGN KEY (edge_id) REFERENCES candidate_edges(edge_id) ON DELETE RESTRICT,
    FOREIGN KEY (policy_hash) REFERENCES validation_policies(policy_hash) ON DELETE RESTRICT
);
"""

CREATE_ATOMIC_EVIDENCE_TABLE = """
CREATE TABLE IF NOT EXISTS atomic_evidence (
    evidence_id TEXT PRIMARY KEY,
    evidence_payload_hash TEXT NOT NULL,
    validation_run_id TEXT NOT NULL,
    edge_id TEXT NOT NULL,
    dimension_type TEXT NOT NULL,
    dimension_key TEXT NOT NULL,
    partition_identity TEXT NOT NULL,
    sample_count INTEGER NOT NULL,
    effect_size REAL NOT NULL,
    effect_size_type TEXT NOT NULL,
    raw_p_value REAL NOT NULL,
    adjusted_q_value REAL,
    statistic_value REAL NOT NULL,
    confidence_interval_json TEXT,
    context_metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at_utc TEXT NOT NULL,
    FOREIGN KEY (validation_run_id) REFERENCES validation_runs(validation_run_id) ON DELETE RESTRICT,
    FOREIGN KEY (edge_id) REFERENCES candidate_edges(edge_id) ON DELETE RESTRICT
);
"""

CREATE_CONFIRMATORY_AUDITS_TABLE = """
CREATE TABLE IF NOT EXISTS confirmatory_audits (
    audit_id TEXT PRIMARY KEY,
    validation_run_id TEXT NOT NULL,
    frozen_hypothesis_version TEXT NOT NULL,
    dataset_fingerprint TEXT NOT NULL,
    policy_hash TEXT NOT NULL,
    holdout_partition_identity TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    FOREIGN KEY (validation_run_id) REFERENCES validation_runs(validation_run_id) ON DELETE RESTRICT,
    FOREIGN KEY (policy_hash) REFERENCES validation_policies(policy_hash) ON DELETE RESTRICT
);
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_candidate_edges_primitive_feature ON candidate_edges(causal_primitive, target_feature);",
    "CREATE INDEX IF NOT EXISTS idx_hypothesis_versions_edge_id ON hypothesis_versions(edge_id);",
    "CREATE INDEX IF NOT EXISTS idx_validation_runs_edge_policy ON validation_runs(edge_id, policy_hash);",
    "CREATE INDEX IF NOT EXISTS idx_validation_runs_dataset_fp ON validation_runs(dataset_fingerprint);",
    "CREATE INDEX IF NOT EXISTS idx_atomic_evidence_run_id ON atomic_evidence(validation_run_id);",
    "CREATE INDEX IF NOT EXISTS idx_atomic_evidence_edge_id ON atomic_evidence(edge_id);",
    "CREATE INDEX IF NOT EXISTS idx_atomic_evidence_payload_hash ON atomic_evidence(evidence_payload_hash);",
    "CREATE INDEX IF NOT EXISTS idx_atomic_evidence_dim_partition ON atomic_evidence(dimension_type, partition_identity);",
    "CREATE INDEX IF NOT EXISTS idx_confirmatory_audits_run_id ON confirmatory_audits(validation_run_id);",
]


def initialize_database(conn: sqlite3.Connection) -> None:
    """Initialize database schema, enable foreign keys, and enforce schema version discipline."""
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 5000;")

    with conn:
        conn.execute(CREATE_SCHEMA_MIGRATIONS_TABLE)
        conn.execute(CREATE_CANDIDATE_EDGES_TABLE)
        conn.execute(CREATE_HYPOTHESIS_VERSIONS_TABLE)
        conn.execute(CREATE_VALIDATION_POLICIES_TABLE)
        conn.execute(CREATE_VALIDATION_CONTEXT_UNIVERSES_TABLE)
        conn.execute(CREATE_VALIDATION_RUNS_TABLE)
        conn.execute(CREATE_ATOMIC_EVIDENCE_TABLE)
        conn.execute(CREATE_CONFIRMATORY_AUDITS_TABLE)

        for stmt in CREATE_INDEXES:
            conn.execute(stmt)

        cursor = conn.execute("SELECT MAX(version) FROM schema_migrations;")
        row = cursor.fetchone()
        max_version = row[0] if row and row[0] is not None else 0

        if max_version > CURRENT_SCHEMA_VERSION:
            raise SchemaVersionError(
                f"Database schema version '{max_version}' is newer than current engine version '{CURRENT_SCHEMA_VERSION}'"
            )

        if max_version == 0:
            now_iso = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "INSERT INTO schema_migrations (version, applied_at_utc) VALUES (?, ?);",
                (CURRENT_SCHEMA_VERSION, now_iso),
            )
        elif max_version < CURRENT_SCHEMA_VERSION:
            # Transactional migration from v1 -> v2
            if max_version == 1:
                cursor = conn.execute("PRAGMA table_info(validation_policies);")
                columns = [col[1] for col in cursor.fetchall()]
                if "meta_analysis_method" not in columns:
                    conn.execute(
                        "ALTER TABLE validation_policies ADD COLUMN meta_analysis_method TEXT NOT NULL DEFAULT 'FISHER_COMBINED_PROBABILITY';"
                    )
                now_iso = datetime.now(timezone.utc).isoformat()
                conn.execute(
                    "INSERT INTO schema_migrations (version, applied_at_utc) VALUES (?, ?);",
                    (CURRENT_SCHEMA_VERSION, now_iso),
                )
