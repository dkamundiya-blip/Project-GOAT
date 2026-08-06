"""
Project GOAT v0.7 — Research Orchestration Enums

Defines PipelineState, PipelineStageType, and ArtifactType enums for research workflow orchestration.
"""

from __future__ import annotations

from enum import Enum


class PipelineState(str, Enum):
    """Immutable state machine states for a ResearchPipeline."""

    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    ARCHIVED = "archived"


class PipelineStageType(str, Enum):
    """Supported scientific research pipeline stages (1 to 11)."""

    FEATURE_CONSTRUCTION = "feature_construction"
    FEATURE_REGISTRATION = "feature_registration"
    FEATURE_GRAPH_VALIDATION = "feature_graph_validation"
    QUALITY_GATES = "quality_gates"
    FEATURE_EXPLORATION = "feature_exploration"
    EXPLORATION_DECISION = "exploration_decision"
    SCIENTIFIC_VALIDATION = "scientific_validation"
    EVIDENCE_COLLECTION = "evidence_collection"
    KNOWLEDGE_REGISTRATION = "knowledge_registration"
    KNOWLEDGE_GRAPH_UPDATE = "knowledge_graph_update"
    SCIENTIFIC_MEMORY_UPDATE = "scientific_memory_update"


class ArtifactType(str, Enum):
    """Classification of scientific artifacts generated during pipeline execution."""

    FEATURE = "feature"
    CANDIDATE = "candidate"
    DECISION = "decision"
    VALIDATION = "validation"
    EVIDENCE = "evidence"
    KNOWLEDGE = "knowledge"
    REPORT = "report"
