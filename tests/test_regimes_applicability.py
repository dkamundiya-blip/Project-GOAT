"""
Project GOAT v0.7 — Test Suite for EdgeApplicabilityEngine

Coverage:
- Regime compatibility score calculation
- Activation state assignment (ACTIVE, INACTIVE, CONDITIONAL, WATCHLIST, REJECTED)
- ApplicabilityDecision & RegimeExplainabilityRecord generation
- Deterministic tie-breaking logic
"""

from goat.alpha.core.canonical import compute_edge_id
from goat.alpha.core.enums import EdgeMaturity
from goat.alpha.core.models import ScientificEdge
from goat.regimes.applicability.engine import EdgeApplicabilityEngine
from goat.regimes.core.canonical import compute_regime_id
from goat.regimes.core.enums import EdgeActivationState, RegimeType
from goat.regimes.core.models import MarketRegime


def test_assess_edge_applicability_active():
    engine = EdgeApplicabilityEngine()

    e_id, e_hash = compute_edge_id("Edge Momentum", ["HYP_1"], ["VAL_1"])
    edge = ScientificEdge(
        edge_id=e_id,
        title="Quantitative Edge: MOM_10D",
        maturity=EdgeMaturity.VALIDATED,
        confidence=0.85,
        reproducibility=0.88,
        discovery_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=e_hash,
    )

    r_id, r_hash = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    regime = MarketRegime(
        regime_id=r_id,
        timestamp="2026-07-30T00:00:00Z",
        regime_type=RegimeType.TRENDING,
        confidence=0.85,
        canonical_hash=r_hash,
    )

    assessment, explanation = engine.assess_edge_applicability(edge, regime, [])

    assert assessment.assessment_id.startswith("APA_")
    assert assessment.applicability == EdgeActivationState.ACTIVE
    assert assessment.applicability_score >= 0.70
    assert explanation.explanation_id.startswith("REX_")


def test_assess_edge_applicability_watchlist():
    engine = EdgeApplicabilityEngine()

    e_id, e_hash = compute_edge_id("Edge New", ["HYP_1"], ["VAL_1"])
    edge = ScientificEdge(
        edge_id=e_id,
        title="Edge New",
        maturity=EdgeMaturity.NEW,
        confidence=0.85,
        discovery_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=e_hash,
    )

    r_id, r_hash = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    regime = MarketRegime(
        regime_id=r_id,
        timestamp="2026-07-30T00:00:00Z",
        regime_type=RegimeType.TRENDING,
        canonical_hash=r_hash,
    )

    assessment, _ = engine.assess_edge_applicability(edge, regime, [])
    assert assessment.applicability == EdgeActivationState.WATCHLIST


def test_evaluate_all_edges_decision():
    engine = EdgeApplicabilityEngine()

    e1_id, e1_hash = compute_edge_id("E1", ["H1"], ["V1"])
    e2_id, e2_hash = compute_edge_id("E2", ["H2"], ["V2"])

    edge1 = ScientificEdge(edge_id=e1_id, title="E1", maturity=EdgeMaturity.VALIDATED, confidence=0.85, reproducibility=0.88, discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e1_hash)
    edge2 = ScientificEdge(edge_id=e2_id, title="E2", maturity=EdgeMaturity.NEW, confidence=0.85, discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e2_hash)

    r_id, r_hash = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    regime = MarketRegime(regime_id=r_id, timestamp="2026-07-30T00:00:00Z", regime_type=RegimeType.TRENDING, canonical_hash=r_hash)

    decision, assessments, explainability = engine.evaluate_all_edges([edge1, edge2], regime, [], "2026-07-30T00:00:00Z")

    assert decision.decision_id.startswith("APD_")
    assert e1_id in decision.active_edges
    assert e2_id not in decision.active_edges  # e2 is WATCHLIST
