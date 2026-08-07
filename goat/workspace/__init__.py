"""
Project GOAT Phase 8 — Research Workspace Subsystem (`goat.workspace`)
"""

from goat.workspace.api import create_workspace_router
from goat.workspace.models import (
    Bookmark,
    Notebook,
    ResearchNote,
    compute_bookmark_id,
    compute_note_id,
    compute_notebook_id,
)
from goat.workspace.store import (
    SQLiteWorkspaceRepository,
    init_workspace_db,
)

__all__ = [
    "Bookmark",
    "ResearchNote",
    "Notebook",
    "compute_bookmark_id",
    "compute_note_id",
    "compute_notebook_id",
    "SQLiteWorkspaceRepository",
    "init_workspace_db",
    "create_workspace_router",
]
