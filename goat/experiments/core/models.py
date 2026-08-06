"""
Project GOAT v0.9 — Core Immutable Domain Models for Scientific Experiment Subsystem
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

from goat.experiments.core.enums import (
    ExperimentPriority,
    ExperimentStatus,
    ExperimentType,
)


class ScientificExperiment(BaseModel):
    """Immutable domain model representing a scientific research experiment container."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    experiment_id: str = Field(
        ...,
        description="Unique deterministic experiment ID formatted as EXP_<HEX16>",
        pattern=r"^EXP_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(
        default="",
        description="Target ScientificHypothesis ID (HYP_<HEX16>)",
    )
    title: str = Field(default="", description="Descriptive experiment title")
    name: str = Field(default="", description="Legacy experiment name")
    objective: str = Field(default="", description="Detailed scientific purpose and scope description")
    description: str = Field(default="", description="Detailed scientific purpose and scope description")
    experiment_type: ExperimentType = Field(default=ExperimentType.SIMULATION, description="Experiment classification type")
    status: ExperimentStatus = Field(default=ExperimentStatus.PLANNED, description="Current lifecycle status")
    priority: ExperimentPriority = Field(default=ExperimentPriority.NORMAL, description="Scheduling priority rating")
    author: str = Field(default="QUANT_RESEARCHER", description="Author or registration agent")
    evidence_ids: list[str] = Field(default_factory=list, description="List of associated EvidenceRecord or Collection IDs")
    manifest_id: str = Field(default="", description="Associated ExperimentManifest ID (MAN_<HEX16>)")
    created_timestamp: str = Field(default="", description="ISO 8601 creation timestamp")
    creation_timestamp: str = Field(default="", description="Legacy ISO 8601 creation timestamp")
    updated_timestamp: str = Field(default="", description="ISO 8601 last updated timestamp")
    start_timestamp: str = Field(default="", description="ISO 8601 start timestamp")
    completion_timestamp: str = Field(default="", description="ISO 8601 completion timestamp")
    scientific_fingerprint: str = Field(default="", description="Legacy EFP fingerprint")
    semantic_version: str = Field(default="1.0.0", description="Semantic version string")
    protocol_version: str = Field(default="1.0.0", description="Protocol version string")
    pipeline_id: str = Field(default="", description="Pipeline ID")
    provenance_metadata: dict[str, Any] = Field(default_factory=dict, description="Provenance metadata")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit metadata")
    tags: list[str] = Field(default_factory=list, description="Classification tags")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    @model_validator(mode="before")
    @classmethod
    def _normalize_legacy_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            d = dict(data)
            if "name" in d and not d.get("title"):
                d["title"] = d["name"]
            elif "title" in d and not d.get("name"):
                d["name"] = d["title"]
            if "objective" in d and not d.get("description"):
                d["description"] = d["objective"]
            elif "description" in d and not d.get("objective"):
                d["objective"] = d["description"]
            if "creation_timestamp" in d and not d.get("created_timestamp"):
                d["created_timestamp"] = d["creation_timestamp"]
            elif "created_timestamp" in d and not d.get("creation_timestamp"):
                d["creation_timestamp"] = d["created_timestamp"]
            if not d.get("updated_timestamp"):
                d["updated_timestamp"] = d.get("created_timestamp", "") or d.get("creation_timestamp", "")
            return d
        return data


class ExperimentManifest(BaseModel):
    """Immutable domain model specifying execution parameters, inputs, and reproducibility specs for an experiment."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    manifest_id: str = Field(
        ...,
        description="Unique deterministic manifest ID formatted as MAN_<HEX16>",
        pattern=r"^MAN_[A-Fa-f0-9]{16,64}$",
    )
    experiment_id: str = Field(
        ...,
        description="Target ScientificExperiment ID (EXP_<HEX16>)",
        pattern=r"^EXP_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(
        ...,
        description="Target ScientificHypothesis ID (HYP_<HEX16>)",
        pattern=r"^HYP_[A-Fa-f0-9]{16,64}$",
    )
    evidence_ids: list[str] = Field(default_factory=list, description="List of associated evidence or collection IDs")
    dataset_fingerprint: str = Field(default="", description="SHA-256 digest of historical tick dataset evaluated")
    configuration_params: dict[str, Any] = Field(default_factory=dict, description="Exact configuration parameters map")
    software_version: str = Field(default="1.0.0", description="Software release version or git commit digest")
    author: str = Field(default="QUANT_RESEARCHER", description="Author or registration agent")
    created_timestamp: str = Field(..., description="ISO 8601 creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class ExperimentLifecycle(BaseModel):
    """Immutable domain model recording a state transition event for a ScientificExperiment."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    lifecycle_id: str = Field(
        ...,
        description="Unique deterministic lifecycle ID formatted as LFC_<HEX16>",
        pattern=r"^LFC_[A-Fa-f0-9]{16,64}$",
    )
    experiment_id: str = Field(
        ...,
        description="Target ScientificExperiment ID (EXP_<HEX16>)",
        pattern=r"^EXP_[A-Fa-f0-9]{16,64}$",
    )
    from_status: ExperimentStatus = Field(..., description="Origin lifecycle status")
    to_status: ExperimentStatus = Field(..., description="Target lifecycle status")
    actor: str = Field(..., description="User or system agent triggering transition")
    reason: str = Field(default="", description="Transition rationale description")
    timestamp: str = Field(..., description="ISO 8601 transition timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class ExperimentReplay(BaseModel):
    """Immutable domain model storing deterministic replay specifications and verification metadata."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_id: str = Field(
        ...,
        description="Unique deterministic replay ID formatted as RPL_<HEX16>",
        pattern=r"^RPL_[A-Fa-f0-9]{16,64}$",
    )
    experiment_id: str = Field(
        ...,
        description="Target ScientificExperiment ID (EXP_<HEX16>)",
        pattern=r"^EXP_[A-Fa-f0-9]{16,64}$",
    )
    manifest_id: str = Field(
        ...,
        description="Target ExperimentManifest ID (MAN_<HEX16>)",
        pattern=r"^MAN_[A-Fa-f0-9]{16,64}$",
    )
    dataset_hash: str = Field(..., description="SHA-256 digest of input replay dataset")
    random_seed: int = Field(default=42, description="Explicit deterministic random seed")
    expected_output_hash: str = Field(default="", description="SHA-256 digest of expected deterministic output state")
    is_verified: bool = Field(default=True, description="Boolean flag verifying replay determinism match")
    timestamp: str = Field(..., description="ISO 8601 replay record creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class ExperimentSchedule(BaseModel):
    """Immutable domain model tracking experiment scheduling and queue metadata without executing runs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schedule_id: str = Field(
        ...,
        description="Unique deterministic schedule ID formatted as SCH_<HEX16>",
        pattern=r"^SCH_[A-Fa-f0-9]{16,64}$",
    )
    experiment_id: str = Field(
        ...,
        description="Target ScientificExperiment ID (EXP_<HEX16>)",
        pattern=r"^EXP_[A-Fa-f0-9]{16,64}$",
    )
    priority: ExperimentPriority = Field(default=ExperimentPriority.NORMAL, description="Scheduling priority rating")
    scheduled_timestamp: str = Field(..., description="ISO 8601 target execution schedule timestamp")
    queue_position: int = Field(default=1, ge=1, description="Deterministic queue order position index")
    scheduler_id: str = Field(default="GOAT_SCHEDULER", description="Scheduler agent or engine identifier")
    timestamp: str = Field(..., description="ISO 8601 record creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class ExperimentSummary(BaseModel):
    """Immutable domain model summarizing aggregate experiment subsystem metrics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    summary_id: str = Field(
        ...,
        description="Unique deterministic summary ID formatted as SUM_<HEX16>",
        pattern=r"^SUM_[A-Fa-f0-9]{16,64}$",
    )
    total_experiments: int = Field(..., ge=0, description="Total count of registered experiments")
    status_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by ExperimentStatus")
    type_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by ExperimentType")
    priority_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by ExperimentPriority")
    timestamp: str = Field(..., description="ISO 8601 summary snapshot timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")
