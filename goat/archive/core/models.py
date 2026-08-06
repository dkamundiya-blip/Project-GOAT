"""
Project GOAT v0.8 — Core Immutable Domain Models for Institutional Research Archive Vault

Defines immutable Pydantic V2 models using ConfigDict(frozen=True, extra="forbid"):
- ArchiveRecord (ARC_<HEX16>)
- ArchiveBatch (ABT_<HEX16>)
- ReplayRequest (RRQ_<HEX16>)
- ReplaySession (RPS_<HEX16>)
- ReplayCheckpoint (RCP_<HEX16>)
- SnapshotManifest (SNP_<HEX16>)
- ArchiveStatistics (AST_<HEX16>)
- ArchiveSummary (ASM_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.archive.core.enums import (
    ArchiveEntityType,
    ArchiveSubsystemOrigin,
    ReplayStatus,
    SnapshotType,
)


class ArchiveRecord(BaseModel):
    """Immutable model representing an archived event record."""

    archive_id: str = Field(
        ...,
        description="Unique archive record ID formatted as ARC_<HEX16>",
        pattern=r"^ARC_[A-Fa-f0-9]{16}$",
    )
    source_subsystem: ArchiveSubsystemOrigin = Field(..., description="Originating subsystem enum")
    entity_type: ArchiveEntityType = Field(..., description="Entity category classification enum")
    entity_id: str = Field(..., description="Primary entity ID string from source subsystem")
    payload: dict[str, Any] = Field(default_factory=dict, description="Immutable event payload dictionary")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of creation")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class ArchiveBatch(BaseModel):
    """Immutable model representing an ingestion batch of archive records."""

    batch_id: str = Field(
        ...,
        description="Unique batch ID formatted as ABT_<HEX16>",
        pattern=r"^ABT_[A-Fa-f0-9]{16}$",
    )
    record_ids: list[str] = Field(default_factory=list, description="Contained ArchiveRecord IDs")
    record_count: int = Field(..., ge=0, description="Total record count in batch")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class ReplayRequest(BaseModel):
    """Immutable model representing a deterministic replay query request."""

    request_id: str = Field(
        ...,
        description="Unique replay request ID formatted as RRQ_<HEX16>",
        pattern=r"^RRQ_[A-Fa-f0-9]{16}$",
    )
    start_time: str = Field(..., description="Replay window start ISO 8601 UTC timestamp")
    end_time: str = Field(..., description="Replay window end ISO 8601 UTC timestamp")
    subsystems: list[ArchiveSubsystemOrigin] = Field(default_factory=list, description="Subsystem filter list")
    entity_types: list[ArchiveEntityType] = Field(default_factory=list, description="Entity type filter list")
    instrument: str = Field(default="", description="Target instrument filter")
    session_id: str = Field(default="", description="Target trading session filter")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class ReplaySession(BaseModel):
    """Immutable model representing an executed replay session."""

    session_id: str = Field(
        ...,
        description="Unique replay session ID formatted as RPS_<HEX16>",
        pattern=r"^RPS_[A-Fa-f0-9]{16}$",
    )
    request_id: str = Field(..., description="Associated ReplayRequest ID")
    records_replayed: int = Field(..., ge=0, description="Total records replayed")
    start_time: str = Field(..., description="Execution start timestamp")
    end_time: str = Field(..., description="Execution end timestamp")
    status: ReplayStatus = Field(default=ReplayStatus.COMPLETED, description="Replay execution status enum")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class ReplayCheckpoint(BaseModel):
    """Immutable model representing a sequence checkpoint during replay stream."""

    checkpoint_id: str = Field(
        ...,
        description="Unique replay checkpoint ID formatted as RCP_<HEX16>",
        pattern=r"^RCP_[A-Fa-f0-9]{16}$",
    )
    sequence: int = Field(..., ge=0, description="Sequential checkpoint counter")
    record_id: str = Field(..., description="ArchiveRecord ID at checkpoint")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class SnapshotManifest(BaseModel):
    """Immutable model representing a deterministic state snapshot manifest."""

    manifest_id: str = Field(
        ...,
        description="Unique snapshot manifest ID formatted as SNP_<HEX16>",
        pattern=r"^SNP_[A-Fa-f0-9]{16}$",
    )
    snapshot_type: SnapshotType = Field(..., description="Snapshot category classification enum")
    state_data: dict[str, Any] = Field(default_factory=dict, description="State data dictionary")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class ArchiveStatistics(BaseModel):
    """Immutable model representing operational storage statistics."""

    stat_id: str = Field(
        ...,
        description="Unique statistics ID formatted as AST_<HEX16>",
        pattern=r"^AST_[A-Fa-f0-9]{16}$",
    )
    total_records: int = Field(..., ge=0, description="Total archived record count")
    total_batches: int = Field(..., ge=0, description="Total ingestion batch count")
    subsystem_counts: dict[str, int] = Field(default_factory=dict, description="Subsystem -> record count map")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")


class ArchiveSummary(BaseModel):
    """Immutable summary model aggregating overall archive metrics."""

    summary_id: str = Field(
        ...,
        description="Unique summary ID formatted as ASM_<HEX16>",
        pattern=r"^ASM_[A-Fa-f0-9]{16}$",
    )
    total_records: int = Field(..., ge=0, description="Total archived record count")
    total_sessions: int = Field(..., ge=0, description="Total replay sessions executed")
    integrity_status: str = Field(default="VERIFIED", description="Vault integrity status string")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    model_config = ConfigDict(frozen=True, extra="forbid")
