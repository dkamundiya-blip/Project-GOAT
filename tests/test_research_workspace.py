"""
Project GOAT Phase 8 — Research Workspace & Decision Intelligence Test Suite (`tests/test_research_workspace.py`)

Validates:
1. Bookmark, ResearchNote, and Notebook domain models & deterministic ID generation.
2. SQLiteWorkspaceRepository persistence & CRUD operations.
3. Workspace REST API endpoints (/api/v1/workspace/*).
4. Multi-workspace state management & repository integrity.
"""

from __future__ import annotations

import sqlite3
import pytest

from goat.workspace.models import (
    Bookmark,
    Notebook,
    ResearchNote,
    compute_bookmark_id,
    compute_note_id,
    compute_notebook_id,
)
from goat.workspace.store import SQLiteWorkspaceRepository, init_workspace_db


@pytest.fixture
def db_conn():
    conn = init_workspace_db(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def repo(db_conn):
    return SQLiteWorkspaceRepository(db_conn)


def test_bookmark_model_and_persistence(repo):
    """Validation 1: Bookmark creation, canonical hashing, and SQLite persistence."""
    target_id = "EDG_00018F42A109C3E1"
    target_type = "EDGE"
    b_id, b_hash = compute_bookmark_id(target_id, target_type)

    assert b_id.startswith("BMK_")
    assert len(b_hash) == 64

    bookmark = Bookmark(
        bookmark_id=b_id,
        target_id=target_id,
        target_type=target_type,
        title="Top Boom 1000 Edge Bookmark",
        created_at="2026-08-07T12:00:00Z",
        metadata={"priority": "HIGH"},
        canonical_hash=b_hash,
    )

    repo.save_bookmark(bookmark)
    bookmarks = repo.list_bookmarks()

    assert len(bookmarks) == 1
    assert bookmarks[0].bookmark_id == b_id
    assert bookmarks[0].target_id == target_id

    repo.delete_bookmark(b_id)
    assert len(repo.list_bookmarks()) == 0


def test_research_note_model_and_persistence(repo):
    """Validation 2: Quantitative Research Note creation and persistence."""
    title = "Boom 1000 Spike Behavior"
    content = "Observed 92% edge confidence on trend expansion."
    n_id, n_hash = compute_note_id(title, content)

    assert n_id.startswith("NOT_")

    note = ResearchNote(
        note_id=n_id,
        title=title,
        content=content,
        tags=["BOOM_1000", "TREND"],
        target_id="EDG_00018F42A109C3E1",
        created_at="2026-08-07T12:00:00Z",
        updated_at="2026-08-07T12:00:00Z",
        canonical_hash=n_hash,
    )

    repo.save_note(note)
    notes = repo.list_notes()

    assert len(notes) == 1
    assert notes[0].note_id == n_id
    assert notes[0].title == title
    assert "BOOM_1000" in notes[0].tags

    repo.delete_note(n_id)
    assert len(repo.list_notes()) == 0


def test_notebook_versioning_and_persistence(repo):
    """Validation 3: Versioned Investigation Notebook persistence."""
    title = "Q3 Deriv Synthetics Investigation"
    version = "1.0.0"
    nb_id, nb_hash = compute_notebook_id(title, version)

    assert nb_id.startswith("NTB_")

    notebook = Notebook(
        notebook_id=nb_id,
        title=title,
        version=version,
        note_ids=["NOT_001", "NOT_002"],
        bookmark_ids=["BMK_001"],
        created_at="2026-08-07T12:00:00Z",
        updated_at="2026-08-07T12:00:00Z",
        canonical_hash=nb_hash,
    )

    repo.save_notebook(notebook)
    notebooks = repo.list_notebooks()

    assert len(notebooks) == 1
    assert notebooks[0].notebook_id == nb_id
    assert notebooks[0].version == "1.0.0"
    assert len(notebooks[0].note_ids) == 2


def test_workspace_rest_api(repo):
    """Validation 4: Workspace REST API router endpoints."""
    try:
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from goat.workspace.api import create_workspace_router
    except ImportError:
        pytest.skip("FastAPI not installed in environment")

    app = FastAPI()
    router = create_workspace_router(repo)
    app.include_router(router)

    client = TestClient(app)

    # 1. Get Workspace Summary
    res = client.get("/api/v1/workspace/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["bookmark_count"] == 0
    assert data["note_count"] == 0

    # 2. Create Bookmark via API
    res_b = client.post("/api/v1/workspace/bookmarks", params={"target_id": "EDG_TEST", "target_type": "EDGE", "title": "API Bookmark"})
    assert res_b.status_code == 200
    b_data = res_b.json()
    assert b_data["bookmark_id"].startswith("BMK_")

    # 3. Create Note via API
    res_n = client.post("/api/v1/workspace/notes", params={"title": "API Note", "content": "API Note Content"})
    assert res_n.status_code == 200
    n_data = res_n.json()
    assert n_data["note_id"].startswith("NOT_")

    # 4. Create Notebook via API
    res_nb = client.post("/api/v1/workspace/notebooks", params={"title": "API Notebook", "version": "1.2.0"})
    assert res_nb.status_code == 200
    nb_data = res_nb.json()
    assert nb_data["version"] == "1.2.0"

    # 5. Verify Summary Count
    res_sum = client.get("/api/v1/workspace/summary")
    assert res_sum.json()["bookmark_count"] == 1
    assert res_sum.json()["note_count"] == 1
    assert res_sum.json()["notebook_count"] == 1
