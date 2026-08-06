"""
Project GOAT v0.7 — Market Regime Reports

Provides immutable, deterministic report models and renderers:
- MarketRegimeReport
- ApplicabilityAssessmentReport
- ApplicabilityDecisionReport
- RuleEvaluationReport
- MarketApplicabilityReport
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.integration.core.canonical import serialize_canonical_json
from goat.regimes.core.models import (
    ApplicabilityAssessment,
    ApplicabilityDecision,
    MarketRegime,
    RegimeExplainabilityRecord,
    RegimeRule,
)


class MarketRegimeReport(BaseModel):
    """Report detailing MarketRegime classification."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    regime: MarketRegime = Field(..., description="Target MarketRegime model")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        r = self.regime
        rt_str = r.regime_type.value if hasattr(r.regime_type, "value") else str(r.regime_type)
        lines = [
            f"# Market Regime Classification Report ({self.report_id})",
            "",
            f"- **Regime ID**: `{r.regime_id}`",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Primary Regime Type**: `{rt_str}`",
            f"- **Classification Confidence**: `{r.confidence:.4f}`",
            "",
            "## Sub-State Indicators",
            f"- **Volatility State**: `{r.volatility_state}`",
            f"- **Liquidity State**: `{r.liquidity_state}`",
            f"- **Participation State**: `{r.participation_state}`",
            f"- **Trend State**: `{r.trend_state}`",
            f"- **Momentum State**: `{r.momentum_state}`",
            f"- **Structural State**: `{r.structural_state}`",
        ]
        return "\n".join(lines)


class ApplicabilityAssessmentReport(BaseModel):
    """Report detailing ApplicabilityAssessment objects across edges."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    assessments: list[ApplicabilityAssessment] = Field(default_factory=list, description="List of assessments")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Edge Applicability Assessment Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Assessed Edges**: {len(self.assessments)}",
            "",
            "| Assessment ID | Edge ID | Regime ID | State | Score | Rationale |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for a in sorted(self.assessments, key=lambda x: x.assessment_id):
            st = a.applicability.value if hasattr(a.applicability, "value") else str(a.applicability)
            rat = a.activation_reason or a.suppression_reason
            lines.append(
                f"| `{a.assessment_id}` | `{a.edge_id}` | `{a.regime_id}` | `{st}` | `{a.applicability_score:.2f}` | {rat} |"
            )
        return "\n".join(lines)


class ApplicabilityDecisionReport(BaseModel):
    """Report detailing ApplicabilityDecision results."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    decision: ApplicabilityDecision = Field(..., description="Target ApplicabilityDecision model")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        d = self.decision
        lines = [
            f"# Applicability Decision Executive Report ({self.report_id})",
            "",
            f"- **Decision ID**: `{d.decision_id}`",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Active Edges Count**: {len(d.active_edges)}",
            f"- **Suppressed Edges Count**: {len(d.suppressed_edges)}",
            "",
            "## Active Edges",
        ]
        for e in d.active_edges:
            lines.append(f"- `{e}`")

        lines.extend(["", "## Suppressed Edges"])
        for e in d.suppressed_edges:
            lines.append(f"- `{e}`")

        return "\n".join(lines)


class RuleEvaluationReport(BaseModel):
    """Report detailing RegimeRule evaluation results."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    evaluated_rules: list[RegimeRule] = Field(default_factory=list, description="List of evaluated rules")
    matched_rules: list[RegimeRule] = Field(default_factory=list, description="List of matched rules")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Regime Rule Evaluation Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Evaluated Rules**: {len(self.evaluated_rules)}",
            f"- **Matched Rules**: {len(self.matched_rules)}",
            "",
            "## Matched Rules",
            "| Rule ID | Priority | Name | Expected Regime |",
            "| :--- | :--- | :--- | :--- |",
        ]
        for r in sorted(self.matched_rules, key=lambda x: (-x.priority, x.rule_id)):
            er = r.expected_regime.value if hasattr(r.expected_regime, "value") else str(r.expected_regime)
            lines.append(f"| `{r.rule_id}` | {r.priority} | {r.name} | `{er}` |")
        return "\n".join(lines)


class MarketApplicabilityReport(BaseModel):
    """Executive root report for Market Regime Engine classification & applicability."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    detected_regime_type: str = Field(..., description="Name of detected regime")
    total_edges_evaluated: int = Field(..., ge=0)
    active_edges_count: int = Field(..., ge=0)
    suppressed_edges_count: int = Field(..., ge=0)
    summary_notes: str = Field(default="")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Market Regime & Edge Applicability Executive Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Detected Regime**: `{self.detected_regime_type}`",
            f"- **Total Evaluated Edges**: {self.total_edges_evaluated}",
            f"- **Active Edges**: {self.active_edges_count}",
            f"- **Suppressed Edges**: {self.suppressed_edges_count}",
            "",
            "## Summary Rationale",
            self.summary_notes or "Market regime classification and edge applicability evaluation completed deterministically without ML.",
        ]
        return "\n".join(lines)
