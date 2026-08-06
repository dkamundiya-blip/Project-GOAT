"""
Project GOAT v0.9 — Core Immutable Domain Models for Observation & Evidence Subsystem
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.evidence.core.enums import (
    EvidenceCategory,
    ObservationSource,
    ObservationStatus,
)


class ScientificObservation(BaseModel):
    """Immutable domain model representing an objective, uninterpreted market observation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    observation_id: str = Field(
        ...,
        description="Unique deterministic observation ID formatted as OBS_<HEX16>",
        pattern=r"^OBS_[A-Fa-f0-9]{16,64}$",
    )
    metric_name: str = Field(..., min_length=2, description="Objective metric name measured")
    metric_value: Any = Field(..., description="Observed value (float, int, str, dict, list)")
    unit_of_measure: str = Field(default="", description="Unit of measurement (e.g. pips, ms, ratio, USD)")
    timestamp: str = Field(..., description="ISO 8601 observation timestamp")
    source: ObservationSource = Field(default=ObservationSource.LIVE_MARKET, description="Observation source origin")
    category: EvidenceCategory = Field(default=EvidenceCategory.PRICE, description="Evidence category classification")
    instrument: str = Field(default="", description="Financial instrument or synthetic index symbol")
    status: ObservationStatus = Field(default=ObservationStatus.CREATED, description="Lifecycle status")
    observer_id: str = Field(default="GOAT_OBSERVER", description="Observer agent or module identifier")
    tags: list[str] = Field(default_factory=list, description="Classification tags")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class EvidenceRecord(BaseModel):
    """Immutable domain model representing structured evidence compiled from one or more observations."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence_id: str = Field(
        ...,
        description="Unique deterministic evidence ID formatted as EVR_<HEX16>",
        pattern=r"^EVR_[A-Fa-f0-9]{16,64}$",
    )
    category: EvidenceCategory = Field(..., description="Evidence category classification")
    observation_ids: list[str] = Field(..., min_length=1, description="List of component ScientificObservation IDs")
    title: str = Field(..., min_length=3, description="Descriptive title of the evidence record")
    description: str = Field(default="", description="Detailed narrative description of evidence facts")
    source: ObservationSource = Field(default=ObservationSource.LIVE_MARKET, description="Primary observation source")
    instrument: str = Field(default="", description="Target financial instrument ticker symbol")
    timestamp: str = Field(..., description="ISO 8601 compilation timestamp")
    tags: list[str] = Field(default_factory=list, description="Classification tags")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class ObservationCollection(BaseModel):
    """Immutable domain model representing a chronological grouping of observations."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    collection_id: str = Field(
        ...,
        description="Unique deterministic collection ID formatted as COL_<HEX16>",
        pattern=r"^COL_[A-Fa-f0-9]{16,64}$",
    )
    collection_name: str = Field(..., min_length=3, description="Descriptive collection name")
    observation_ids: list[str] = Field(default_factory=list, description="Ordered list of included observation IDs")
    start_timestamp: str = Field(..., description="ISO 8601 start timestamp of collection window")
    end_timestamp: str = Field(..., description="ISO 8601 end timestamp of collection window")
    collector_id: str = Field(default="GOAT_COLLECTOR", description="Collector agent or engine identifier")
    tags: list[str] = Field(default_factory=list, description="Classification tags")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class EvidenceLink(BaseModel):
    """Immutable domain model linking evidence or observations to a ScientificHypothesis without evaluation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    link_id: str = Field(
        ...,
        description="Unique deterministic link ID formatted as LNK_<HEX16>",
        pattern=r"^LNK_[A-Fa-f0-9]{16,64}$",
    )
    hypothesis_id: str = Field(
        ...,
        description="Target ScientificHypothesis ID (HYP_<HEX16>)",
        pattern=r"^HYP_[A-Fa-f0-9]{16,64}$",
    )
    target_id: str = Field(
        ...,
        description="Target EvidenceRecord ID (EVR_<HEX16>) or ScientificObservation ID (OBS_<HEX16>)",
    )
    link_type: str = Field(default="HYPOTHESIS_EVIDENCE_LINK", description="Link type classification string")
    linker_id: str = Field(default="GOAT_LINKER", description="Linker agent or engine identifier")
    timestamp: str = Field(..., description="ISO 8601 link creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")


class EvidenceSummary(BaseModel):
    """Immutable domain model summarizing aggregate evidence collection metrics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    summary_id: str = Field(
        ...,
        description="Unique deterministic summary ID formatted as EVS_<HEX16>",
        pattern=r"^EVS_[A-Fa-f0-9]{16,64}$",
    )
    total_observations: int = Field(..., ge=0, description="Total count of observed metrics")
    total_evidence_records: int = Field(..., ge=0, description="Total count of compiled evidence records")
    total_collections: int = Field(..., ge=0, description="Total count of observation collections")
    total_links: int = Field(..., ge=0, description="Total count of hypothesis evidence links")
    category_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by EvidenceCategory")
    source_counts: dict[str, int] = Field(default_factory=dict, description="Count breakdown by ObservationSource")
    timestamp: str = Field(..., description="ISO 8601 summary snapshot timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")
