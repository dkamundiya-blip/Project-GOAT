"""
Project GOAT v0.6 — Edge Persistence Schema Tests

Verifies schema creation, initialization idempotency, migration tracking, and version enforcement.
"""

from __future__ import annotations

import sqlite3
import pytest

from goat.research.edge.persistence import (
    CURRENT_SCHEMA_VERSION,
    SchemaVersionError,
    SQLiteEdgeRepository,
    initialize_database,
)


def test_fresh_database_initialization():
    """Verify fresh database initializes schema and migrations table."""
    conn = sqlite3.connect(":memory:")
    initialize_database(conn)

    cursor = conn.execute("SELECT version, applied_at_utc FROM schema_migrations;")
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == CURRENT_SCHEMA_VERSION


def test_repeated_initialization_is_idempotent():
    """Verify initializing an existing database multiple times is idempotent."""
    conn = sqlite3.connect(":memory:")
    initialize_database(conn)
    initialize_database(conn)

    cursor = conn.execute("SELECT COUNT(*) FROM schema_migrations;")
    count = cursor.fetchone()[0]
    assert count == 1


def test_unsupported_schema_version_rejected():
    """Verify database with a schema version newer than engine is rejected with SchemaVersionError."""
    conn = sqlite3.connect(":memory:")
    initialize_database(conn)

    # Insert a future schema version
    conn.execute("INSERT INTO schema_migrations (version, applied_at_utc) VALUES (999, '2099-01-01T00:00:00Z');")

    with pytest.raises(SchemaVersionError, match="newer than current engine version"):
        initialize_database(conn)


def test_repository_context_manager_close():
    """Verify repository context manager opens and closes connections cleanly."""
    with SQLiteEdgeRepository(":memory:") as repo:
        assert repo.conn is not None
        repo.conn.execute("SELECT 1;")
