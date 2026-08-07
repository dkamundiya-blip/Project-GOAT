"""
Project GOAT Phase 8 — Research Workspace REST API Router (`goat.workspace.api`)

Exposes REST API endpoints for managing bookmarks, research notes, versioned notebooks,
and workspace summary statistics.
"""

from __future__ import annotations

import datetime
from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Query
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False

from goat.workspace.models import (
    Bookmark,
    Notebook,
    ResearchNote,
    compute_bookmark_id,
    compute_note_id,
    compute_notebook_id,
)


def create_workspace_router(workspace_repository: Any) -> Any:
    """Create FastAPI router exposing Phase 8 Research Workspace endpoints."""
    if not _HAS_FASTAPI:
        raise RuntimeError("FastAPI is required to instantiate workspace REST router.")

    router = APIRouter(prefix="/api/v1/workspace", tags=["Research Workspace"])

    @router.get("/summary")
    def get_workspace_summary():
        """Retrieve count summary of bookmarks, notes, and notebooks."""
        bookmarks = workspace_repository.list_bookmarks()
        notes = workspace_repository.list_notes()
        notebooks = workspace_repository.list_notebooks()
        return {
            "bookmark_count": len(bookmarks),
            "note_count": len(notes),
            "notebook_count": len(notebooks),
            "active_workspace": "INSTITUTIONAL_RESEARCH",
        }

    # --- Bookmarks ---

    @router.get("/bookmarks")
    def list_bookmarks():
        """List all saved research bookmarks."""
        return [b.model_dump() for b in workspace_repository.list_bookmarks()]

    @router.post("/bookmarks")
    def create_bookmark(target_id: str, target_type: str, title: str):
        """Create and persist a new bookmark."""
        b_id, b_hash = compute_bookmark_id(target_id, target_type)
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        bookmark = Bookmark(
            bookmark_id=b_id,
            target_id=target_id,
            target_type=target_type,
            title=title,
            created_at=now_iso,
            metadata={},
            canonical_hash=b_hash,
        )
        workspace_repository.save_bookmark(bookmark)
        return bookmark.model_dump()

    @router.delete("/bookmarks/{bookmark_id}")
    def delete_bookmark(bookmark_id: str):
        """Delete a saved bookmark."""
        workspace_repository.delete_bookmark(bookmark_id)
        return {"status": "SUCCESS", "bookmark_id": bookmark_id}

    # --- Research Notes ---

    @router.get("/notes")
    def list_notes():
        """List all quantitative research notes."""
        return [n.model_dump() for n in workspace_repository.list_notes()]

    @router.post("/notes")
    def create_note(title: str, content: str, target_id: str | None = None, tags: str = ""):
        """Create and persist a new research note."""
        n_id, n_hash = compute_note_id(title, content)
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

        note = ResearchNote(
            note_id=n_id,
            title=title,
            content=content,
            tags=tag_list,
            target_id=target_id,
            created_at=now_iso,
            updated_at=now_iso,
            canonical_hash=n_hash,
        )
        workspace_repository.save_note(note)
        return note.model_dump()

    @router.delete("/notes/{note_id}")
    def delete_note(note_id: str):
        """Delete a research note."""
        workspace_repository.delete_note(note_id)
        return {"status": "SUCCESS", "note_id": note_id}

    # --- Notebooks ---

    @router.get("/notebooks")
    def list_notebooks():
        """List all versioned investigation notebooks."""
        return [nb.model_dump() for nb in workspace_repository.list_notebooks()]

    @router.post("/notebooks")
    def create_notebook(title: str, version: str = "1.0.0"):
        """Create and persist a new versioned notebook."""
        nb_id, nb_hash = compute_notebook_id(title, version)
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        notebook = Notebook(
            notebook_id=nb_id,
            title=title,
            version=version,
            note_ids=[],
            bookmark_ids=[],
            created_at=now_iso,
            updated_at=now_iso,
            canonical_hash=nb_hash,
        )
        workspace_repository.save_notebook(notebook)
        return notebook.model_dump()

    return router
