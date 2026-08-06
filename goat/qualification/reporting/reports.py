"""
Project GOAT v0.7 — Scientific Qualification Reports

Provides immutable, deterministic report models and renderers:
- ScientificQualificationReport
- GateEvaluationReport
- DecisionReadinessReport
- QualificationSummaryReport
- ScientificReadinessReport
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.integration.core.canonical import serialize_canonical_json
from goat.qualification.core.models import (
    DecisionReadiness,
    GateEvaluation,
    QualificationExplainabilityRecord,
    ScientificQualification,
)


class ScientificQualificationReport(BaseModel):
    """Report detailing ScientificQualification objects."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    qualifications: list[ScientificQualification] = Field(default_factory=list, description="List of qualifications")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Scientific Qualification Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Qualifications**: {len(self.qualifications)}",
            "",
            "| Qualification ID | Composite ID | Regime ID | State | Overall Readiness | Confidence |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for q in sorted(self.qualifications, key=lambda x: x.qualification_id):
            st = q.qualification_state.value if hasattr(q.qualification_state, "value") else str(q.qualification_state)
            lines.append(
                f"| `{q.qualification_id}` | `{q.composite_id}` | `{q.regime_id}` | `{st}` | `{q.overall_readiness:.4f}` | `{q.scientific_confidence:.2f}` |"
            )
        return "\n".join(lines)


class GateEvaluationReport(BaseModel):
    """Report detailing GateEvaluation results across gates."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    evaluations: list[GateEvaluation] = Field(default_factory=list, description="List of GateEvaluations")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Qualification Gate Evaluation Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Evaluated Gates**: {len(self.evaluations)}",
            "",
            "| Evaluation ID | Gate ID | Passed | Score | Rationale |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for e in sorted(self.evaluations, key=lambda x: x.evaluation_id):
            pass_str = "PASS" if e.passed else "FAIL"
            lines.append(f"| `{e.evaluation_id}` | `{e.gate_id}` | `{pass_str}` | `{e.score:.2f}` | {e.explanation} |")
        return "\n".join(lines)


class DecisionReadinessReport(BaseModel):
    """Report detailing DecisionReadiness models."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    readiness_records: list[DecisionReadiness] = Field(default_factory=list, description="List of DecisionReadiness models")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Decision Readiness Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Evaluated Readiness**: {len(self.readiness_records)}",
            "",
            "| Readiness ID | Qualification ID | Readiness Level | Blocking Conditions Count | Summary |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for r in sorted(self.readiness_records, key=lambda x: x.readiness_id):
            lvl = r.readiness_level.value if hasattr(r.readiness_level, "value") else str(r.readiness_level)
            lines.append(
                f"| `{r.readiness_id}` | `{r.qualification_id}` | `{lvl}` | {len(r.blocking_conditions)} | {r.scientific_summary} |"
            )
        return "\n".join(lines)


class QualificationSummaryReport(BaseModel):
    """Report detailing qualification summary metrics."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    total_qualified: int = Field(..., ge=0)
    total_disqualified: int = Field(..., ge=0)
    total_conditional: int = Field(..., ge=0)

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Scientific Qualification Summary Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Qualified Count**: {self.total_qualified}",
            f"- **Disqualified Count**: {self.total_disqualified}",
            f"- **Conditional Count**: {self.total_conditional}",
        ]
        return "\n".join(lines)


class ScientificReadinessReport(BaseModel):
    """Executive root report for Scientific Signal Qualification & Decision Readiness Engine."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    total_composites_qualified: int = Field(..., ge=0)
    top_readiness_level: str = Field(default="")
    top_readiness_score: float = Field(default=0.0)
    active_blocking_conditions_count: int = Field(default=0, ge=0)
    summary_notes: str = Field(default="")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Scientific Qualification & Decision Readiness Executive Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Qualified Composites**: {self.total_composites_qualified}",
            f"- **Highest Authorized Readiness Level**: `{self.top_readiness_level or 'NONE'}`",
            f"- **Top Readiness Score**: `{self.top_readiness_score:.4f}`",
            f"- **Active Blocking Conditions**: {self.active_blocking_conditions_count}",
            "",
            "## Summary Rationale",
            self.summary_notes or "Scientific signal qualification and decision readiness evaluation completed deterministically without ML.",
        ]
        return "\n".join(lines)
