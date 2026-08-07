"""
Project GOAT Phase 8 — Workspace Persistence Store (`goat.workspace.store`)

SQLite & In-Memory repositories for managing Bookmarks, Research Notes, and Notebooks.
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import threading
from typing import Sequence

from goat.workspace.models import (
    Bookmark,
    Notebook,
    ResearchNote,
    compute_bookmark_id,
    compute_note_id,
    compute_notebook_id,
)


def init_workspace_db(conn_or_path: sqlite3.Connection | str | Path) -> sqlite3.Connection:
    """Initialize SQLite tables for Phase 8 workspace subsystems."""
    if isinstance(conn_or_path, (str, Path)):
        path_str = str(conn_or_path)
        if path_str != ":memory:":
            Path(path_str).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path_str, check_same_thread=False)
    else:
        conn = conn_or_path

    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
    except Exception:
        pass

    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                bookmark_id TEXT PRIMARY KEY,
                target_id TEXT NOT NULL,
                target_type TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS research_notes (
                note_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags_json TEXT NOT NULL,
                target_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notebooks (
                notebook_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                version TEXT NOT NULL,
                note_ids_json TEXT NOT NULL,
                bookmark_ids_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
    return conn


class SQLiteWorkspaceRepository:
    """SQLite workspace repository implementation."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._lock = threading.RLock()

    # --- Bookmarks CRUD ---

    def save_bookmark(self, bookmark: Bookmark) -> None:
        with self._lock, self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO bookmarks (
                    bookmark_id, target_id, target_type, title, created_at, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    bookmark.bookmark_id,
                    bookmark.target_id,
                    bookmark.target_type,
                    bookmark.title,
                    bookmark.created_at,
                    json.dumps(bookmark.metadata),
                    bookmark.canonical_hash,
                ),
            )

    def list_bookmarks(self) -> list[Bookmark]:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM bookmarks ORDER BY created_at DESC;")
            rows = cursor.fetchall()
            return [
                Bookmark(
                    bookmark_id=r[0],
                    target_id=r[1],
                    target_type=r[2],
                    title=r[3],
                    created_at=r[4],
                    metadata=json.loads(r[5]),
                    canonical_hash=r[6],
                )
                for r in rows
            ]

    def delete_bookmark(self, bookmark_id: str) -> None:
        with self._lock, self.conn:
            self.conn.execute("DELETE FROM bookmarks WHERE bookmark_id = ?;", (bookmark_id,))

    # --- Notes CRUD ---

    def save_note(self, note: ResearchNote) -> None:
        with self._lock, self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO research_notes (
                    note_id, title, content, tags_json, target_id, created_at, updated_at, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    note.note_id,
                    note.title,
                    note.content,
                    json.dumps(note.tags),
                    note.target_id,
                    note.created_at,
                    note.updated_at,
                    note.canonical_hash,
                ),
            )

    def list_notes(self) -> list[ResearchNote]:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM research_notes ORDER BY updated_at DESC;")
            rows = cursor.fetchall()
            return [
                ResearchNote(
                    note_id=r[0],
                    title=r[1],
                    content=r[2],
                    tags=json.loads(r[3]),
                    target_id=r[4],
                    created_at=r[5],
                    updated_at=r[6],
                    canonical_hash=r[7],
                )
                for r in rows
            ]

    def delete_note(self, note_id: str) -> None:
        with self._lock, self.conn:
            self.conn.execute("DELETE FROM research_notes WHERE note_id = ?;", (note_id,))

    # --- Notebooks CRUD ---

    def save_notebook(self, notebook: Notebook) -> None:
        with self._lock, self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO notebooks (
                    notebook_id, title, version, note_ids_json, bookmark_ids_json, created_at, updated_at, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    notebook.notebook_id,
                    notebook.title,
                    notebook.version,
                    json.dumps(notebook.note_ids),
                    json.dumps(notebook.bookmark_ids),
                    notebook.created_at,
                    notebook.updated_at,
                    notebook.canonical_hash,
                ),
            )

    def list_notebooks(self) -> list[Notebook]:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM notebooks ORDER BY updated_at DESC;")
            rows = cursor.fetchall()
            return [
                Notebook(
                    notebook_id=r[0],
                    title=r[1],
                    version=r[2],
                    note_ids=json.loads(r[3]),
                    bookmark_ids=json.loads(r[4]),
                    created_at=r[5],
                    updated_at=r[6],
                    canonical_hash=r[7],
                )
                for r in rows
            ]
