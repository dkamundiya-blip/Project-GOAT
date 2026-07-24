"""
Project GOAT v0.5 — Campaign Lifecycle, Enums, Schemas & Failure Taxonomy

Defines the strongly typed status enums, frozen QueueSnapshot data contract,
Failure Exception hierarchy, CampaignDefinition, and 6-section CampaignManifest.
"""

from __future__ import annotations

from datetime import datetime, timezone
import enum
from typing import Any

from pydantic import BaseModel, Field


class ExperimentStatus(str, enum.Enum):
    """Lifecycle status of an individual experiment task."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


class CampaignStatus(str, enum.Enum):
    """Lifecycle status of a campaign execution."""
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PAUSING = "PAUSING"
    PAUSED = "PAUSED"
    RESUMING = "RESUMING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# -----------------------------------------------------------------------------
# Failure Taxonomy Exception Hierarchy
# -----------------------------------------------------------------------------

class OrchestrationError(Exception):
    """Base exception for all v0.5 orchestration failures."""


class ValidationFailure(OrchestrationError):
    """Pre-flight integrity verification failure (provenance, dataset, configuration)."""


class ProvenanceMismatchError(ValidationFailure):
    """Specific error when dataset fingerprint, version, or hypothesis version mismatches."""


class ExperimentFailure(OrchestrationError):
    """Individual experiment evaluation exception or numerical instability."""


class InfrastructureFailure(OrchestrationError):
    """Disk I/O failure, corrupt serialization, or atomic write failure."""


class WorkerFailure(OrchestrationError):
    """Worker process crash, unexpected thread termination, or timeout."""


class CampaignFailure(OrchestrationError):
    """Fatal unrecoverable orchestration logic error."""


# -----------------------------------------------------------------------------
# Data Contracts & Schemas
# -----------------------------------------------------------------------------

class QueueSnapshot(BaseModel):
    """Frozen, immutable point-in-time snapshot of ExperimentQueue state."""
    model_config = {"frozen": True}

    campaign_id: str
    configuration_hash: str
    completed_task_ids: tuple[str, ...] = Field(default_factory=tuple)
    failed_task_ids: tuple[str, ...] = Field(default_factory=tuple)
    in_progress_task_ids: tuple[str, ...] = Field(default_factory=tuple)
    pending_task_ids: tuple[str, ...] = Field(default_factory=tuple)
    task_results: dict[str, dict[str, Any]] = Field(default_factory=dict)
    last_event_sequence: int = 0
    snapshot_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CampaignLifecycleLogEntry(BaseModel):
    """Immutable record of a campaign state transition."""
    utc_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    previous_state: CampaignStatus
    new_state: CampaignStatus
    reason: str
    triggering_component: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class CampaignDefinition(BaseModel):
    """Formal specification defining a batch campaign."""
    campaign_id: str
    configuration_hash: str
    name: str
    description: str = ""
    hypothesis_families: list[dict[str, Any]] = Field(default_factory=list)
    symbol_scope: list[str] = Field(default_factory=lambda: ["R_10"])
    timeframe_scope: list[str] = Field(default_factory=lambda: ["M1"])
    master_seed: int = 42
    max_workers: int = 4
    fdr_alpha: float = 0.05
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CampaignManifest(BaseModel):
    """Authoritative 6-section campaign manifest output."""
    manifest_schema_version: int = 1
    provenance_schema_version: int = 1
    campaign: dict[str, Any] = Field(default_factory=dict)
    configuration: dict[str, Any] = Field(default_factory=dict)
    environment: dict[str, Any] = Field(default_factory=dict)
    research_provenance: dict[str, Any] = Field(default_factory=dict)
    execution_configuration: dict[str, Any] = Field(default_factory=dict)
    validation: dict[str, Any] = Field(default_factory=dict)
    lifecycle_history: list[CampaignLifecycleLogEntry] = Field(default_factory=list)
