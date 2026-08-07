"""
Project GOAT Phase 7 — Research Report Generator (`goat.ai_reasoning.reporting`)

Compiles structured, evidence-backed quantitative ResearchReport objects.
"""

from __future__ import annotations

import datetime

from goat.ai_reasoning.evidence.engine import EvidenceEngine
from goat.ai_reasoning.models.report import (
    ExplanationLevel,
    ResearchReport,
    compute_report_id,
)
from goat.ai_reasoning.reasoning.engine import ReasoningEngine
from goat.edge_discovery.models.edge import DiscoveredEdge
from goat.research.edge.canonical import compute_canonical_sha256


class ResearchReportGenerator:
    """Quantitative Research Report Generator assembling comprehensive research documentation."""

    def __init__(
        self,
        evidence_engine: EvidenceEngine | None = None,
        reasoning_engine: ReasoningEngine | None = None,
    ):
        self.evidence_engine = evidence_engine or EvidenceEngine()
        self.reasoning_engine = reasoning_engine or ReasoningEngine(evidence_engine=self.evidence_engine)

    def generate_report(
        self,
        edge: DiscoveredEdge,
        explanation_level: ExplanationLevel = ExplanationLevel.PROFESSIONAL_QUANT,
    ) -> ResearchReport:
        """Generate a complete, evidence-backed ResearchReport for a DiscoveredEdge."""
        bundle = self.evidence_engine.build_evidence_bundle(edge)
        conclusion = self.reasoning_engine.deduce_edge_status_conclusion(edge)
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        m = edge.metrics

        title = f"Quantitative Research Report — Edge {edge.edge_id} ({', '.join(edge.supported_symbols)})"

        exec_summary = (
            f"Edge {edge.edge_id} evaluated across {m.sample_size} historical observations for symbols "
            f"{', '.join(edge.supported_symbols)}. Expected Value = {m.expected_value:.6f}, Sharpe Ratio = {m.sharpe_ratio:.2f}, "
            f"P-value = {edge.p_value:.6f}. Status: {edge.status.value}."
        )

        stats = {
            "expected_value": m.expected_value,
            "sharpe_ratio": m.sharpe_ratio,
            "sortino_ratio": m.sortino_ratio,
            "win_rate": m.win_rate,
            "max_drawdown": m.max_drawdown,
            "p_value": edge.p_value,
            "composite_score": edge.composite_score,
            "sample_size": float(m.sample_size),
        }

        risks = [
            f"Maximum peak-to-trough drawdown observed: {m.max_drawdown:.2%}.",
            "Regime sensitivity in sideways markets requires continuous volatility tracking.",
            f"Performance drift could degrade status from {edge.status.value} if EV drops below hurdle.",
        ]

        limitations = [
            f"Evaluation constrained to {m.sample_size} historical observations.",
            "Assumes continuous liquidity during synthetic index window ticks.",
            "Walk-forward window degradation requires periodic re-validation.",
        ]

        next_steps = [
            "Submit edge to Research Governance for candidate strategy allocation.",
            "Monitor daily p-value stability and confidence interval drift.",
            "Perform multi-timeframe correlation check against existing active portfolio edges.",
        ]

        r_id, r_hash = compute_report_id(title, now_iso, edge.edge_id)

        checksum = compute_canonical_sha256(
            {
                "composite_score": edge.composite_score,
                "edge_id": edge.edge_id,
                "report_id": r_id,
                "title": title,
            }
        )

        return ResearchReport(
            report_id=r_id,
            title=title,
            timestamp=now_iso,
            explanation_level=explanation_level,
            executive_summary=exec_summary,
            conclusions=[conclusion],
            evidence_bundle=bundle,
            supporting_statistics=stats,
            risk_factors=risks,
            limitations=limitations,
            recommended_next_steps=next_steps,
            checksum=checksum,
            metadata={"chart_metadata": {"timeframe": edge.supported_timeframes[0], "symbol": edge.supported_symbols[0]}},
            canonical_hash=r_hash,
        )
