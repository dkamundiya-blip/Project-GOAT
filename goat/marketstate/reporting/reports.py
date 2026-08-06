"""
Project GOAT v0.8 — Market State Reporting Models

Immutable reporting structures supporting Markdown exports and canonical JSON formatting:
- MarketStateReport
- VolatilityReport
- LiquidityReport
- StructureReport
- QualityReport
- MarketStateExecutiveReport
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.integration.core.canonical import serialize_canonical_json
from goat.marketstate.core.canonical import compute_report_id
from goat.marketstate.core.models import (
    LiquidityAssessment,
    MarketQualityAssessment,
    MarketState,
    StructureAssessment,
    VolatilityAssessment,
)


class VolatilityReport(BaseModel):
    """Immutable report summarizing volatility classification."""

    report_id: str = Field(..., description="Report ID formatted as MSR_<HEX16>")
    symbol: str = Field(..., description="Target market symbol")
    assessment: VolatilityAssessment = Field(..., description="Volatility assessment entity")
    timestamp: str = Field(..., description="ISO 8601 UTC report generation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        v = self.assessment
        return (
            f"# Volatility Assessment Report — {self.symbol}\n"
            f"**Report ID**: `{self.report_id}`  \n"
            f"**Timeframe**: `{v.timeframe}` | **Classification**: `{v.volatility_class.value}`  \n"
            f"**Realized Volatility**: `{v.realized_volatility:.6f}` | **Score**: `{v.volatility_score:.2f}/100`  \n"
            f"**Explanation**: {v.explanation}\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class LiquidityReport(BaseModel):
    """Immutable report summarizing liquidity metrics."""

    report_id: str = Field(..., description="Report ID formatted as MSR_<HEX16>")
    symbol: str = Field(..., description="Target market symbol")
    assessment: LiquidityAssessment = Field(..., description="Liquidity assessment entity")
    timestamp: str = Field(..., description="ISO 8601 UTC report generation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        l = self.assessment
        return (
            f"# Liquidity Assessment Report — {self.symbol}\n"
            f"**Report ID**: `{self.report_id}`  \n"
            f"**Liquidity State**: `{l.liquidity_state.value}` | **Spread State**: `{l.spread_quality.value}`  \n"
            f"**Spread**: `{l.spread:.5f}` | **Score**: `{l.liquidity_score:.2f}/100`  \n"
            f"**Activity**: `{l.activity_state.value}` | **Depth Proxy**: `{l.market_depth_proxy}`  \n"
            f"**Explanation**: {l.explanation}\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class StructureReport(BaseModel):
    """Immutable report summarizing price structure."""

    report_id: str = Field(..., description="Report ID formatted as MSR_<HEX16>")
    symbol: str = Field(..., description="Target market symbol")
    assessment: StructureAssessment = Field(..., description="Structure assessment entity")
    timestamp: str = Field(..., description="ISO 8601 UTC report generation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        s = self.assessment
        return (
            f"# Price Structure Report — {self.symbol}\n"
            f"**Report ID**: `{self.report_id}`  \n"
            f"**Structure**: `{s.structure_state.value}` | **Trend**: `{s.trend_state.value}`  \n"
            f"**Extrema Counts**: HH `{s.higher_highs}` | HL `{s.higher_lows}` | LH `{s.lower_highs}` | LL `{s.lower_lows}`  \n"
            f"**Trend Strength**: `{s.trend_strength:.2f}/100`  \n"
            f"**Explanation**: {s.explanation}\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class QualityReport(BaseModel):
    """Immutable report summarizing feed quality."""

    report_id: str = Field(..., description="Report ID formatted as MSR_<HEX16>")
    symbol: str = Field(..., description="Target market symbol")
    assessment: MarketQualityAssessment = Field(..., description="Quality assessment entity")
    timestamp: str = Field(..., description="ISO 8601 UTC report generation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        q = self.assessment
        return (
            f"# Market Quality Report — {self.symbol}\n"
            f"**Report ID**: `{self.report_id}`  \n"
            f"**Overall Quality**: `{q.overall_quality.value}`  \n"
            f"**Components**: Stream `{q.stream_health.value}` | Data `{q.data_quality.value}` | Latency `{q.latency_quality.value}` | Replay `{q.replay_quality.value}`  \n"
            f"**Explanation**: {q.explanation}\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class MarketStateReport(BaseModel):
    """Immutable report summarizing a single MarketState observation."""

    report_id: str = Field(..., description="Report ID formatted as MSR_<HEX16>")
    market_state: MarketState = Field(..., description="Target MarketState entity")
    timestamp: str = Field(..., description="ISO 8601 UTC report generation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        m = self.market_state
        return (
            f"# Market State Intelligence Report — {m.symbol}\n"
            f"**State ID**: `{m.state_id}` | **Report ID**: `{self.report_id}`  \n"
            f"**Timestamp**: {m.timestamp}  \n"
            f"**Trend**: `{m.trend_state.value}` | **Structure**: `{m.structure_state.value}`  \n"
            f"**Volatility**: `{m.volatility_state.value}` | **Liquidity**: `{m.liquidity_state.value}`  \n"
            f"**Spread**: `{m.spread_state.value}` | **Activity**: `{m.activity_state.value}`  \n"
            f"**Overall Quality**: `{m.overall_quality.value}` | **Confidence**: `{m.confidence:.2f}`  \n"
            f"**Explanation**: {m.explanation}\n"
        )

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"


class MarketStateExecutiveReport(BaseModel):
    """Consolidated executive report summarizing market state across all tracked symbols."""

    report_id: str = Field(..., description="Executive report ID formatted as MSR_<HEX16>")
    active_symbols_count: int = Field(default=0, ge=0, description="Total active symbols evaluated")
    states: list[MarketState] = Field(default_factory=list, description="List of active MarketState entities")
    timestamp: str = Field(..., description="ISO 8601 UTC report generation timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    def to_markdown(self) -> str:
        lines = [
            "# Step 7.1 — Market State Intelligence Executive Report",
            f"**Report ID**: `{self.report_id}`  ",
            f"**Timestamp**: {self.timestamp}  ",
            f"**Total Tracked Symbols**: `{self.active_symbols_count}`",
            "",
            "## Active Market State Overview",
        ]
        for s in self.states:
            lines.append(
                f"- **{s.symbol}**: Trend `{s.trend_state.value}`, Structure `{s.structure_state.value}`, "
                f"Vol `{s.volatility_state.value}`, Liq `{s.liquidity_state.value}`, Confidence `{s.confidence:.2f}`"
            )
        return "\n".join(lines)

    def to_json(self) -> str:
        return serialize_canonical_json(self.model_dump(mode="json"))

    class Config:
        frozen = True
        extra = "forbid"
