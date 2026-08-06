"""
Project GOAT v0.7 — Core Immutable Models for Scientific Qualification & Decision Readiness Engine

Defines immutable Pydantic domain models:
- ScientificQualification (SQL_<HEX16>)
- QualificationGate (QGT_<HEX16>)
- GateEvaluation (GEV_<HEX16>)
- DecisionReadiness (DCR_<HEX16>)
- QualificationExplainabilityRecord (QEX_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.qualification.core.enums import QualificationState, ReadinessLevel


class ScientificQualification(BaseModel):
    """Immutable model representing scientific qualification of a composite edge under a regime."""

    qualification_id: str = Field(
        ...,
        description="Unique qualification ID formatted as SQL_<HEX16>",
        pattern=r"^SQL_[A-Fa-f0-9]{16}$",
    )
    composite_id: str = Field(..., description="Target CompositeEdge ID (CMP_<HEX16>)")
    regime_id: str = Field(..., description="Target MarketRegime ID (MRG_<HEX16>)")
    evaluation_timestamp: str = Field(..., description="ISO 8601 UTC evaluation timestamp")
    qualification_state: QualificationState = Field(..., description="Assigned qualification state")
    overall_readiness: float = Field(default=0.0, ge=0.0, le=1.0, description="Aggregated overall decision readiness score")
    scientific_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Scientific confidence score")
    evidence_strength: float = Field(default=0.0, ge=0.0, le=1.0, description="Evidence strength rating")
    reproducibility: float = Field(default=0.0, ge=0.0, le=1.0, description="Empirical reproducibility score")
    explainability: float = Field(default=0.0, ge=0.0, le=1.0, description="Scientific explainability score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class QualificationGate(BaseModel):
    """Immutable model representing a deterministic qualification gate criteria."""

    gate_id: str = Field(
        ...,
        description="Unique gate ID formatted as QGT_<HEX16>",
        pattern=r"^QGT_[A-Fa-f0-9]{16}$",
    )
    gate_name: str = Field(..., description="Descriptive gate name")
    description: str = Field(default="", description="Detailed narrative description")
    priority: int = Field(default=50, ge=1, le=100, description="Gate priority rating (1-100)")
    evaluation_rule: str = Field(..., description="Rule expression or evaluator key")
    pass_threshold: float = Field(default=0.70, ge=0.0, le=1.0, description="Required passing threshold (0.0 to 1.0)")
    mandatory: bool = Field(default=True, description="Whether passing this gate is mandatory for qualification")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class GateEvaluation(BaseModel):
    """Immutable model representing the evaluation result of a single QualificationGate."""

    evaluation_id: str = Field(
        ...,
        description="Unique evaluation ID formatted as GEV_<HEX16>",
        pattern=r"^GEV_[A-Fa-f0-9]{16}$",
    )
    gate_id: str = Field(..., description="Target QualificationGate ID (QGT_<HEX16>)")
    qualification_id: str = Field(..., description="Target ScientificQualification ID (SQL_<HEX16>)")
    passed: bool = Field(..., description="Whether the gate passed deterministically")
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="Evaluated gate score (0.0 to 1.0)")
    explanation: str = Field(default="", description="Narrative evaluation rationale")
    supporting_evidence: list[str] = Field(default_factory=list, description="IDs of supporting evidence artifacts")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class DecisionReadiness(BaseModel):
    """Immutable model representing authorized decision readiness state."""

    readiness_id: str = Field(
        ...,
        description="Unique readiness ID formatted as DCR_<HEX16>",
        pattern=r"^DCR_[A-Fa-f0-9]{16}$",
    )
    qualification_id: str = Field(..., description="Target ScientificQualification ID (SQL_<HEX16>)")
    readiness_level: ReadinessLevel = Field(..., description="Assigned decision readiness level")
    blocking_conditions: list[str] = Field(default_factory=list, description="Active blocking condition names")
    satisfied_conditions: list[str] = Field(default_factory=list, description="Satisfied condition names")
    scientific_summary: str = Field(default="", description="Executive scientific summary rationale")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class QualificationExplainabilityRecord(BaseModel):
    """Immutable model providing 100% scientific traceability for qualification decisions."""

    explanation_id: str = Field(
        ...,
        description="Unique explanation ID formatted as QEX_<HEX16>",
        pattern=r"^QEX_[A-Fa-f0-9]{16}$",
    )
    qualification_id: str = Field(..., description="Target ScientificQualification ID (SQL_<HEX16>)")
    participating_composites: list[str] = Field(default_factory=list, description="IDs of participating CompositeEdges")
    applicable_regimes: list[str] = Field(default_factory=list, description="IDs of applicable MarketRegimes")
    passed_gates: list[str] = Field(default_factory=list, description="IDs of passed QualificationGates")
    failed_gates: list[str] = Field(default_factory=list, description="IDs of failed QualificationGates")
    blocking_conditions: list[str] = Field(default_factory=list, description="Active blocking condition names")
    supporting_evidence: list[str] = Field(default_factory=list, description="IDs of supporting evidence artifacts")
    supporting_hypotheses: list[str] = Field(default_factory=list, description="IDs of supporting hypotheses")
    supporting_validations: list[str] = Field(default_factory=list, description="IDs of supporting validation runs")
    supporting_knowledge: list[str] = Field(default_factory=list, description="IDs of supporting IntegratedKnowledge models")
    scientific_rationale: str = Field(..., description="Detailed narrative scientific rationale")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
