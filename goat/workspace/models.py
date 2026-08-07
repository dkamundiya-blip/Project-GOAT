"""
Project GOAT Phase 8 — Research Workspace Domain Models (`goat.workspace.models`)

Defines Pydantic models for Bookmarks, Research Notes, Versioned Notebooks, and Workspace Preferences.
"""

from __future__ import annotations

import datetime
from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class Bookmark(BaseModel):
    """Immutable bookmark model for saving edges, reports, and hypotheses."""

    bookmark_id: str = Field(..., description="Unique bookmark ID formatted as BMK_<HEX16>", pattern=r"^BMK_[A-Fa-f0-9]{16}$")
    target_id: str = Field(..., description="Target object ID (e.g. EDG_..., REP_..., HYP_...)")
    target_type: str = Field(..., description="Target type (EDGE, REPORT, HYPOTHESIS, FEATURE)")
    title: str = Field(..., description="Human-readable bookmark title")
    created_at: str = Field(..., description="ISO 8601 UTC creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ResearchNote(BaseModel):
    """Domain model representing a quantitative research note."""

    note_id: str = Field(..., description="Unique note ID formatted as NOT_<HEX16>", pattern=r"^NOT_[A-Fa-f0-9]{16}$")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Markdown note body content")
    tags: list[str] = Field(default_factory=list, description="Categorization tags")
    target_id: str | None = Field(default=None, description="Optional linked target ID")
    created_at: str = Field(..., description="ISO 8601 UTC creation timestamp")
    updated_at: str = Field(..., description="ISO 8601 UTC last edit timestamp")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class Notebook(BaseModel):
    """Domain model representing a versioned investigation notebook."""

    notebook_id: str = Field(..., description="Unique notebook ID formatted as NTB_<HEX16>", pattern=r"^NTB_[A-Fa-f0-9]{16}$")
    title: str = Field(..., description="Notebook title")
    version: str = Field(default="1.0.0", description="Notebook version string")
    note_ids: list[str] = Field(default_factory=list, description="Ordered note IDs")
    bookmark_ids: list[str] = Field(default_factory=list, description="Ordered bookmark IDs")
    created_at: str = Field(..., description="ISO 8601 UTC creation timestamp")
    updated_at: str = Field(..., description="ISO 8601 UTC last edit timestamp")
    canonical_hash: str = Field(..., description="SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


def compute_bookmark_id(target_id: str, target_type: str) -> tuple[str, str]:
    """Compute deterministic bookmark_id and canonical_hash."""
    payload = {"target_id": target_id.strip(), "target_type": target_type.strip()}
    digest = compute_canonical_sha256(payload)
    return f"BMK_{digest[:16].upper()}", digest.upper()


def compute_note_id(title: str, content: str) -> tuple[str, str]:
    """Compute deterministic note_id and canonical_hash."""
    payload = {"content": content.strip(), "title": title.strip()}
    digest = compute_canonical_sha256(payload)
    return f"NOT_{digest[:16].upper()}", digest.upper()


def compute_notebook_id(title: str, version: str) -> tuple[str, str]:
    """Compute deterministic notebook_id and canonical_hash."""
    payload = {"title": title.strip(), "version": version.strip()}
    digest = compute_canonical_sha256(payload)
    return f"NTB_{digest[:16].upper()}", digest.upper()
