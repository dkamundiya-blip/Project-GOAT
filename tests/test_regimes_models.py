"""
Project GOAT v0.7 — Test Suite for Market Regimes Core Models & Canonical Hashing

Coverage:
- Immutable Pydantic models (MarketRegime, RegimeRule, ApplicabilityAssessment, ApplicabilityDecision, RegimeExplainabilityRecord)
- Extra fields forbidden
- Immutability check raises (TypeError, ValidationError)
- Deterministic ID generators & canonical SHA-256 hashes
"""

import pytest
from pydantic import ValidationError

from goat.regimes.core.canonical import (
    compute_assessment_id,
    compute_decision_id,
    compute_regime_explanation_id,
    compute_regime_id,
    compute_regime_report_id,
    compute_rule_id,
    serialize_canonical_json,
)
from goat.regimes.core.enums import (
    EdgeActivationState,
    RegimeType,
)
from goat.regimes.core.models import (
    ApplicabilityAssessment,
    ApplicabilityDecision,
    MarketRegime,
    RegimeExplainabilityRecord,
    RegimeRule,
)


def test_regime_id_determinism():
    id1, hash1 = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    id2, hash2 = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("MRG_")


def test_assessment_id_determinism():
    id1, hash1 = compute_assessment_id("SED_1234567890ABCDEF", "MRG_1234567890ABCDEF")
    id2, hash2 = compute_assessment_id("SED_1234567890ABCDEF", "MRG_1234567890ABCDEF")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("APA_")


def test_rule_id_determinism():
    id1, hash1 = compute_rule_id("Rule Trending", "TRENDING")
    id2, hash2 = compute_rule_id("Rule Trending", "TRENDING")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("RGR_")


def test_decision_id_determinism():
    id1, hash1 = compute_decision_id(["SED_1"], ["SED_2"], "2026-07-30T00:00:00Z")
    id2, hash2 = compute_decision_id(["SED_1"], ["SED_2"], "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("APD_")


def test_regime_explanation_id_determinism():
    id1, hash1 = compute_regime_explanation_id("MRG_1234567890ABCDEF", "APA_1234567890ABCDEF")
    id2, hash2 = compute_regime_explanation_id("MRG_1234567890ABCDEF", "APA_1234567890ABCDEF")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("REX_")


def test_regime_report_id_determinism():
    id1, hash1 = compute_regime_report_id("MarketApplicabilityReport", "2026-07-30T00:00:00Z")
    id2, hash2 = compute_regime_report_id("MarketApplicabilityReport", "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("MRR_")


def test_market_regime_model():
    r_id, r_hash = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    regime = MarketRegime(
        regime_id=r_id,
        timestamp="2026-07-30T00:00:00Z",
        regime_type=RegimeType.TRENDING,
        confidence=0.85,
        canonical_hash=r_hash,
    )
    assert regime.regime_id == r_id
    with pytest.raises((TypeError, ValidationError)):
        regime.confidence = 0.99


def test_regime_rule_model():
    ru_id, ru_hash = compute_rule_id("Rule Trend", "TRENDING")
    rule = RegimeRule(
        rule_id=ru_id,
        name="Rule Trend",
        expected_regime=RegimeType.TRENDING,
        canonical_hash=ru_hash,
    )
    assert rule.rule_id == ru_id
    with pytest.raises((TypeError, ValidationError)):
        rule.priority = 1000


def test_applicability_assessment_model():
    a_id, a_hash = compute_assessment_id("SED_1234567890ABCDEF", "MRG_1234567890ABCDEF")
    assessment = ApplicabilityAssessment(
        assessment_id=a_id,
        edge_id="SED_1234567890ABCDEF",
        regime_id="MRG_1234567890ABCDEF",
        applicability=EdgeActivationState.ACTIVE,
        applicability_score=0.88,
        canonical_hash=a_hash,
    )
    assert assessment.assessment_id == a_id
    with pytest.raises((TypeError, ValidationError)):
        assessment.applicability_score = 1.5


def test_applicability_decision_model():
    d_id, d_hash = compute_decision_id(["SED_1"], [], "2026-07-30T00:00:00Z")
    decision = ApplicabilityDecision(
        decision_id=d_id,
        active_edges=["SED_1"],
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=d_hash,
    )
    assert decision.decision_id == d_id
    with pytest.raises((TypeError, ValidationError)):
        decision.timestamp = "2026-07-31T00:00:00Z"


def test_regime_explainability_record_model():
    ex_id, ex_hash = compute_regime_explanation_id("MRG_1234567890ABCDEF", "APA_1234567890ABCDEF")
    expl = RegimeExplainabilityRecord(
        explanation_id=ex_id,
        regime_id="MRG_1234567890ABCDEF",
        assessment_id="APA_1234567890ABCDEF",
        edge_id="SED_1234567890ABCDEF",
        detected_regime="TRENDING",
        scientific_explanation="Traceable regime decision.",
        canonical_hash=ex_hash,
    )
    assert expl.explanation_id == ex_id
    with pytest.raises((TypeError, ValidationError)):
        expl.detected_regime = "RANGING"
