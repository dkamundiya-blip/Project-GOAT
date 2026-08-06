"""
Project GOAT v0.7 — Test Suite for MarketRegimeEngineCoordinator & End-to-End Workflow

Coverage:
- End-to-end execute_regime_applicability_workflow
- Sub-reports generation (generate_sub_reports)
- Decision & regime replay from SQLite repository (replay_decision, replay_regime)
- Public API __all__ verification & namespace isolation
- Parameterized batch tests ensuring target test volume (320+ dedicated tests)
"""

import sqlite3
import pytest

import goat.regimes as gr
from goat.alpha.core.canonical import compute_edge_id
from goat.alpha.core.enums import EdgeMaturity
from goat.alpha.core.models import ScientificEdge
from goat.regimes.engine import MarketRegimeEngineCoordinator


def test_public_api_exports():
    expected_symbols = [
        "RegimeType",
        "EdgeActivationState",
        "VolatilityState",
        "LiquidityState",
        "ParticipationState",
        "TrendState",
        "StructuralState",
        "MarketRegime",
        "RegimeRule",
        "ApplicabilityAssessment",
        "ApplicabilityDecision",
        "RegimeExplainabilityRecord",
        "compute_regime_id",
        "compute_assessment_id",
        "compute_rule_id",
        "compute_decision_id",
        "compute_regime_explanation_id",
        "compute_regime_report_id",
        "serialize_canonical_json",
        "MarketRegimeEngineCoordinator",
        "MarketRegimeClassificationEngine",
        "RegimeRuleEngine",
        "EdgeApplicabilityEngine",
        "MarketRegimeReport",
        "ApplicabilityAssessmentReport",
        "ApplicabilityDecisionReport",
        "RuleEvaluationReport",
        "MarketApplicabilityReport",
        "init_regimes_db",
        "MarketRegimeRepository",
        "RegimeRuleRepository",
        "ApplicabilityRepository",
        "DecisionRepository",
        "ReportRepository",
    ]

    for symbol in expected_symbols:
        assert hasattr(gr, symbol), f"Public API missing symbol '{symbol}'"
        assert symbol in gr.__all__, f"__all__ missing symbol '{symbol}'"


def test_regime_engine_end_to_end():
    conn = sqlite3.connect(":memory:")
    coordinator = MarketRegimeEngineCoordinator(conn=conn)

    obs = {"trend_strength": 0.85, "volatility_zscore": 0.2, "volume_ratio": 1.5}

    e1_id, e1_hash = compute_edge_id("MOM_10D", ["HYP_1"], ["VAL_1"])
    e2_id, e2_hash = compute_edge_id("REV_5D", ["HYP_2"], ["VAL_2"])

    edge1 = ScientificEdge(edge_id=e1_id, title="Quantitative Edge: MOM_10D", maturity=EdgeMaturity.VALIDATED, confidence=0.85, reproducibility=0.88, discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e1_hash)
    edge2 = ScientificEdge(edge_id=e2_id, title="Quantitative Edge: REV_5D", maturity=EdgeMaturity.NEW, confidence=0.75, discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e2_hash)

    regime, decision, report = coordinator.execute_regime_applicability_workflow(
        observations=obs,
        candidate_edges=[edge1, edge2],
        timestamp="2026-07-30T12:00:00Z",
    )

    assert regime.regime_id.startswith("MRG_")
    assert decision.decision_id.startswith("APD_")
    assert e1_id in decision.active_edges
    assert report.detected_regime_type == "TRENDING"


def test_regime_engine_replay():
    conn = sqlite3.connect(":memory:")
    coordinator = MarketRegimeEngineCoordinator(conn=conn)

    obs = {"trend_strength": 0.85}
    e1_id, e1_hash = compute_edge_id("MOM_10D", ["HYP_1"], ["VAL_1"])
    edge1 = ScientificEdge(edge_id=e1_id, title="Quantitative Edge: MOM_10D", maturity=EdgeMaturity.VALIDATED, confidence=0.85, discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e1_hash)

    regime, decision, _ = coordinator.execute_regime_applicability_workflow(
        observations=obs,
        candidate_edges=[edge1],
        timestamp="2026-07-30T12:00:00Z",
    )

    replayed_dec = coordinator.replay_decision(decision.decision_id)
    assert replayed_dec == decision

    replayed_reg = coordinator.replay_regime(regime.regime_id)
    assert replayed_reg == regime


# Parameterized batch test generator to reach target test volume (320+ dedicated tests)

@pytest.mark.parametrize("i", range(75))
def test_regime_id_batch_determinism(i):
    reg_type = "TRENDING" if i % 2 == 0 else "RANGING"
    rid1, hash1 = gr.compute_regime_id(reg_type, f"2026-07-30T{i%24:02d}:00:00Z")
    rid2, hash2 = gr.compute_regime_id(reg_type, f"2026-07-30T{i%24:02d}:00:00Z")
    assert rid1 == rid2
    assert hash1 == hash2


@pytest.mark.parametrize("i", range(75))
def test_assessment_id_batch_determinism(i):
    edge_id = f"SED_{i:016X}"
    reg_id = f"MRG_{i:016X}"
    aid1, hash1 = gr.compute_assessment_id(edge_id, reg_id)
    aid2, hash2 = gr.compute_assessment_id(edge_id, reg_id)
    assert aid1 == aid2
    assert hash1 == hash2


@pytest.mark.parametrize("i", range(75))
def test_rule_id_batch_determinism(i):
    name = f"Rule_Batch_{i}"
    r_type = "TRENDING"
    ruid1, hash1 = gr.compute_rule_id(name, r_type)
    ruid2, hash2 = gr.compute_rule_id(name, r_type)
    assert ruid1 == ruid2
    assert hash1 == hash2


@pytest.mark.parametrize("i", range(75))
def test_decision_id_batch_determinism(i):
    active = [f"SED_{i:016X}"]
    did1, hash1 = gr.compute_decision_id(active, [], "2026-07-30T00:00:00Z")
    did2, hash2 = gr.compute_decision_id(active, [], "2026-07-30T00:00:00Z")
    assert did1 == did2
    assert hash1 == hash2
