"""
Project GOAT v0.7 — Scientific Risk Reports

Provides immutable, deterministic report models and renderers:
- RiskProfileReport
- PositionSizingReport
- CapitalAllocationReport
- ExposureAssessmentReport
- RiskAssessmentReport
- RiskExecutiveReport
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.integration.core.canonical import serialize_canonical_json
from goat.risk.core.models import (
    CapitalAllocation,
    ExposureAssessment,
    PositionSizingDecision,
    RiskAssessment,
    RiskProfile,
)


class RiskProfileReport(BaseModel):
    """Report detailing RiskProfile configurations."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    profiles: list[RiskProfile] = Field(default_factory=list, description="List of risk profiles")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Risk Profile Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Profiles**: {len(self.profiles)}",
            "",
            "| Profile ID | Qualification ID | Account Balance | Currency | Max Risk % | Max Portfolio Exposure % |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for p in sorted(self.profiles, key=lambda x: x.risk_profile_id):
            lines.append(
                f"| `{p.risk_profile_id}` | `{p.qualification_id}` | `${p.account_balance:,.2f}` | `{p.account_currency}` | `{p.maximum_risk_percent*100:.1f}%` | `{p.maximum_portfolio_exposure*100:.1f}%` |"
            )
        return "\n".join(lines)


class PositionSizingReport(BaseModel):
    """Report detailing PositionSizingDecision outcomes."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    sizing_decisions: list[PositionSizingDecision] = Field(default_factory=list, description="List of sizing decisions")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Position Sizing & Target Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Sizing Decisions**: {len(self.sizing_decisions)}",
            "",
            "| Sizing ID | Instrument | Entry | Stop Loss | Take Profit | R:R Ratio | Recommended Lots |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for s in sorted(self.sizing_decisions, key=lambda x: x.sizing_id):
            lines.append(
                f"| `{s.sizing_id}` | `{s.instrument}` | `{s.entry_price:.5f}` | `{s.stop_loss_price:.5f}` | `{s.take_profit_price:.5f}` | `{s.risk_reward_ratio:.2f}` | `{s.recommended_lot_size:.2f}` |"
            )
        return "\n".join(lines)


class CapitalAllocationReport(BaseModel):
    """Report detailing CapitalAllocation models."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    allocations: list[CapitalAllocation] = Field(default_factory=list, description="List of capital allocations")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Capital Allocation Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Allocations**: {len(self.allocations)}",
            "",
            "| Allocation ID | Qualification ID | Allocated Capital | Reserved Capital | Utilization % |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for a in sorted(self.allocations, key=lambda x: x.allocation_id):
            lines.append(
                f"| `{a.allocation_id}` | `{a.qualification_id}` | `${a.allocated_capital:,.2f}` | `${a.reserved_capital:,.2f}` | `{a.utilization_percent*100:.1f}%` |"
            )
        return "\n".join(lines)


class ExposureAssessmentReport(BaseModel):
    """Report detailing ExposureAssessment models."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    assessments: list[ExposureAssessment] = Field(default_factory=list, description="List of exposure assessments")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Exposure Assessment Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Assessments**: {len(self.assessments)}",
            "",
            "| Exposure ID | Active Positions | Portfolio Exposure | Instrument Exposure | Status |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for e in sorted(self.assessments, key=lambda x: x.exposure_id):
            st = e.exposure_status.value if hasattr(e.exposure_status, "value") else str(e.exposure_status)
            lines.append(
                f"| `{e.exposure_id}` | {len(e.active_positions)} | `${e.portfolio_exposure:,.2f}` | `${e.instrument_exposure:,.2f}` | `{st}` |"
            )
        return "\n".join(lines)


class RiskAssessmentReport(BaseModel):
    """Report detailing RiskAssessment summary outcomes."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    risk_assessments: list[RiskAssessment] = Field(default_factory=list, description="List of risk assessments")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Risk Assessment Outcome Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Risk Assessments**: {len(self.risk_assessments)}",
            "",
            "| Assessment ID | Sizing ID | Monetary Risk | Expected Reward | Expected Return % | Impact |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for r in sorted(self.risk_assessments, key=lambda x: x.assessment_id):
            lines.append(
                f"| `{r.assessment_id}` | `{r.sizing_id}` | `${r.monetary_risk:,.2f}` | `${r.expected_reward:,.2f}` | `{r.expected_return_percent:.2f}%` | `{r.drawdown_impact:.2%}` |"
            )
        return "\n".join(lines)


class RiskExecutiveReport(BaseModel):
    """Executive root report for Scientific Risk Management Engine."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    total_opportunities_evaluated: int = Field(..., ge=0)
    total_capital_reserved: float = Field(..., ge=0.0)
    top_recommended_lots: float = Field(default=0.0, ge=0.0)
    top_monetary_risk: float = Field(default=0.0, ge=0.0)
    top_monetary_reward: float = Field(default=0.0, ge=0.0)
    summary_notes: str = Field(default="")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Scientific Risk Management Executive Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Evaluated Opportunities**: {self.total_opportunities_evaluated}",
            f"- **Total Reserved Capital**: `${self.total_capital_reserved:,.2f}`",
            f"- **Top Recommended Lots**: `{self.top_recommended_lots:.2f}`",
            f"- **Top Monetary Risk**: `${self.top_monetary_risk:,.2f}`",
            f"- **Top Monetary Reward**: `${self.top_monetary_reward:,.2f}`",
            "",
            "## Summary Rationale",
            self.summary_notes or "Scientific risk management and capital allocation completed deterministically without AI or optimization.",
        ]
        return "\n".join(lines)
