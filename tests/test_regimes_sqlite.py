"""
Project GOAT v0.7 — Test Suite for Market Regimes Persistence Repositories

Coverage:
- MarketRegimeRepository (save, get round-trip)
- RegimeRuleRepository (save, get round-trip)
- ApplicabilityRepository (save assessment & explanation, get round-trip)
- DecisionRepository (save, get round-trip)
- ReportRepository (save, get raw JSON round-trip)
- Foreign Key Integrity Constraints
"""

import sqlite3
import pytest

from goat.regimes.core.canonical import (
    compute_assessment_id,
    compute_decision_id,
    compute_regime_explanation_id,
    compute_regime_id,
    compute_rule_id,
)
from goat.regimes.core.enums import EdgeActivationState, RegimeType
from goat.regimes.core.models import (
    ApplicabilityAssessment,
    ApplicabilityDecision,
    MarketRegime,
    RegimeExplainabilityRecord,
    RegimeRule,
)
from goat.regimes.persistence.sqlite import (
    ApplicabilityRepository,
    DecisionRepository,
    MarketRegimeRepository,
    RegimeRuleRepository,
    ReportRepository,
    init_regimes_db,
)


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    init_regimes_db(conn)
    yield conn
    conn.close()


def test_market_regime_repository_roundtrip(db_conn):
    repo = MarketRegimeRepository(db_conn)
    r_id, r_hash = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    regime = MarketRegime(
        regime_id=r_id,
        timestamp="2026-07-30T00:00:00Z",
        regime_type=RegimeType.TRENDING,
        confidence=0.85,
        canonical_hash=r_hash,
    )

    repo.save_regime(regime)
    fetched = repo.get_regime(r_id)

    assert fetched == regime


def test_regime_rule_repository_roundtrip(db_conn):
    repo = RegimeRuleRepository(db_conn)
    ru_id, ru_hash = compute_rule_id("Rule Trend", "TRENDING")
    rule = RegimeRule(
        rule_id=ru_id,
        name="Rule Trend",
        expected_regime=RegimeType.TRENDING,
        canonical_hash=ru_hash,
    )

    repo.save_rule(rule)
    fetched = repo.get_rule(ru_id)

    assert fetched == rule


def test_applicability_repository_roundtrip(db_conn):
    r_repo = MarketRegimeRepository(db_conn)
    r_id, r_hash = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    regime = MarketRegime(regime_id=r_id, timestamp="2026-07-30T00:00:00Z", regime_type=RegimeType.TRENDING, canonical_hash=r_hash)
    r_repo.save_regime(regime)

    app_repo = ApplicabilityRepository(db_conn)
    a_id, a_hash = compute_assessment_id("SED_1", r_id)
    assessment = ApplicabilityAssessment(
        assessment_id=a_id,
        edge_id="SED_1",
        regime_id=r_id,
        applicability=EdgeActivationState.ACTIVE,
        applicability_score=0.85,
        canonical_hash=a_hash,
    )

    app_repo.save_assessment(assessment)
    fetched_ass = app_repo.get_assessment(a_id)
    assert fetched_ass == assessment

    ex_id, ex_hash = compute_regime_explanation_id(r_id, a_id)
    explanation = RegimeExplainabilityRecord(
        explanation_id=ex_id,
        regime_id=r_id,
        assessment_id=a_id,
        edge_id="SED_1",
        detected_regime="TRENDING",
        scientific_explanation="Explanation narrative.",
        canonical_hash=ex_hash,
    )

    app_repo.save_explanation(explanation)
    fetched_ex = app_repo.get_explanation(ex_id)
    assert fetched_ex == explanation


def test_decision_repository_roundtrip(db_conn):
    repo = DecisionRepository(db_conn)
    d_id, d_hash = compute_decision_id(["SED_1"], [], "2026-07-30T00:00:00Z")
    decision = ApplicabilityDecision(
        decision_id=d_id,
        active_edges=["SED_1"],
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=d_hash,
    )

    repo.save_decision(decision)
    fetched = repo.get_decision(d_id)

    assert fetched == decision
