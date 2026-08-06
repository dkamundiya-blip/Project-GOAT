"""
Project GOAT v0.7 — Edge Applicability Engine

Evaluates compatibility between candidate quantitative market edges and active market regimes:
- Calculates applicability scores deterministically
- Assigns activation states (ACTIVE, INACTIVE, CONDITIONAL, WATCHLIST, REJECTED)
- Produces ApplicabilityAssessment, ApplicabilityDecision, and RegimeExplainabilityRecord models
- Implements deterministic, stable tie-breaking
"""

from __future__ import annotations

from typing import Any

from goat.alpha.core.models import ScientificEdge
from goat.regimes.core.canonical import (
    compute_assessment_id,
    compute_canonical_sha256,
    compute_decision_id,
    compute_regime_explanation_id,
)
from goat.regimes.core.enums import EdgeActivationState, RegimeType
from goat.regimes.core.models import (
    ApplicabilityAssessment,
    ApplicabilityDecision,
    MarketRegime,
    RegimeExplainabilityRecord,
    RegimeRule,
)


class EdgeApplicabilityEngine:
    """Engine for deterministic edge applicability assessment and activation state assignment."""

    def compute_compatibility_score(
        self,
        edge: ScientificEdge,
        regime: MarketRegime,
    ) -> float:
        """Compute regime compatibility score (0.0 to 1.0) deterministically."""
        base_score = float(edge.confidence) * 0.5 + float(edge.reproducibility) * 0.5

        r_type = regime.regime_type
        if hasattr(r_type, "value"):
            r_type_val = r_type.value
        else:
            r_type_val = str(r_type)

        # Regime affinity adjustments
        affinity_bonus = 0.0
        if r_type_val in ("TRENDING", "BREAKOUT") and "MOM" in edge.title.upper():
            affinity_bonus = 0.15
        elif r_type_val in ("RANGING", "REVERSAL") and "REV" in edge.title.upper():
            affinity_bonus = 0.15
        elif r_type_val == "HIGH_VOLATILITY" and float(edge.robustness) < 0.70:
            affinity_bonus = -0.20

        comp_score = round(max(0.0, min(1.0, base_score + affinity_bonus)), 4)
        return comp_score

    def assess_edge_applicability(
        self,
        edge: ScientificEdge,
        regime: MarketRegime,
        matching_rules: list[RegimeRule],
    ) -> tuple[ApplicabilityAssessment, RegimeExplainabilityRecord]:
        """Assess edge applicability for a single edge under a given market regime deterministically."""
        comp_score = self.compute_compatibility_score(edge, regime)

        mat_str = edge.maturity.value if hasattr(edge.maturity, "value") else str(edge.maturity)
        rule_ids = sorted([r.rule_id for r in matching_rules])

        state: EdgeActivationState
        act_reason: str = ""
        supp_reason: str = ""

        if mat_str in ("NEW", "EXPERIMENTAL"):
            state = EdgeActivationState.WATCHLIST
            act_reason = f"Edge maturity '{mat_str}' requires watchlist observation period."
        elif comp_score >= 0.70 and float(edge.confidence) >= 0.70:
            state = EdgeActivationState.ACTIVE
            act_reason = f"High regime compatibility score ({comp_score:.2f}) under {regime.regime_type} regime."
        elif comp_score >= 0.45:
            state = EdgeActivationState.CONDITIONAL
            act_reason = f"Moderate regime compatibility score ({comp_score:.2f}) under {regime.regime_type} regime."
        else:
            state = EdgeActivationState.INACTIVE
            supp_reason = f"Low regime compatibility score ({comp_score:.2f}) under {regime.regime_type} regime."

        ass_id, _ = compute_assessment_id(edge.edge_id, regime.regime_id)

        payload_ass = {
            "assessment_id": ass_id,
            "edge_id": edge.edge_id,
            "regime_id": regime.regime_id,
            "state": state.value,
        }
        hash_ass = compute_canonical_sha256(payload_ass).upper()

        assessment = ApplicabilityAssessment(
            assessment_id=ass_id,
            edge_id=edge.edge_id,
            regime_id=regime.regime_id,
            applicability=state,
            applicability_score=comp_score,
            activation_reason=act_reason,
            suppression_reason=supp_reason,
            supporting_rules=rule_ids,
            supporting_evidence=edge.supporting_evidence,
            canonical_hash=hash_ass,
        )

        # Generate Explainability Record
        exp_id, _ = compute_regime_explanation_id(regime.regime_id, ass_id)

        explanation_text = (
            f"Edge '{edge.title}' ({edge.edge_id}) evaluated under Market Regime '{regime.regime_type.value if hasattr(regime.regime_type, 'value') else regime.regime_type}' ({regime.regime_id}). "
            f"Assigned state '{state.value}' with compatibility score {comp_score:.4f}. "
            f"{act_reason or supp_reason}"
        )

        payload_exp = {
            "assessment_id": ass_id,
            "explanation_id": exp_id,
            "regime_id": regime.regime_id,
        }
        hash_exp = compute_canonical_sha256(payload_exp).upper()

        explainability = RegimeExplainabilityRecord(
            explanation_id=exp_id,
            regime_id=regime.regime_id,
            assessment_id=ass_id,
            edge_id=edge.edge_id,
            detected_regime=regime.regime_type.value if hasattr(regime.regime_type, "value") else str(regime.regime_type),
            supporting_rules=rule_ids,
            supporting_observations={"regime_confidence": regime.confidence},
            supporting_evidence=edge.supporting_evidence,
            scientific_explanation=explanation_text,
            canonical_hash=hash_exp,
        )

        return assessment, explainability

    def evaluate_all_edges(
        self,
        edges: list[ScientificEdge],
        regime: MarketRegime,
        matching_rules: list[RegimeRule],
        timestamp: str,
    ) -> tuple[ApplicabilityDecision, list[ApplicabilityAssessment], list[RegimeExplainabilityRecord]]:
        """Evaluate applicability across all candidate edges and construct ApplicabilityDecision."""
        assessments: list[ApplicabilityAssessment] = []
        explainability_records: list[RegimeExplainabilityRecord] = []

        for e in sorted(edges, key=lambda x: x.edge_id):
            ass, exp = self.assess_edge_applicability(e, regime, matching_rules)
            assessments.append(ass)
            explainability_records.append(exp)

        # Active vs Suppressed Lists
        active_list = [a.edge_id for a in assessments if a.applicability == EdgeActivationState.ACTIVE]
        suppressed_list = [a.edge_id for a in assessments if a.applicability != EdgeActivationState.ACTIVE]

        # Stable tie-breaking sort for active edges
        edge_map = {e.edge_id: e for e in edges}
        ass_map = {a.edge_id: a for a in assessments}

        def _sort_key(edge_id: str) -> tuple[float, float, str]:
            e = edge_map.get(edge_id)
            a = ass_map.get(edge_id)
            score = a.applicability_score if a else 0.0
            repr_sc = float(e.reproducibility) if e else 0.0
            return (-score, -repr_sc, edge_id)

        sorted_active = sorted(active_list, key=_sort_key)
        sorted_suppressed = sorted(suppressed_list)

        explanations_map = {exp.edge_id: exp.scientific_explanation for exp in explainability_records}

        dec_id, _ = compute_decision_id(sorted_active, sorted_suppressed, timestamp)

        payload_dec = {
            "decision_id": dec_id,
            "timestamp": timestamp,
        }
        hash_dec = compute_canonical_sha256(payload_dec).upper()

        decision = ApplicabilityDecision(
            decision_id=dec_id,
            active_edges=sorted_active,
            suppressed_edges=sorted_suppressed,
            explanations=explanations_map,
            timestamp=timestamp,
            canonical_hash=hash_dec,
        )

        return decision, assessments, explainability_records
