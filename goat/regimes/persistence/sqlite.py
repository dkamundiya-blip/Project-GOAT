"""
Project GOAT v0.7 — SQLite Persistence for Market Regime Engine

Provides repositories supporting round-trip persistence and foreign-key integrity:
- MarketRegimeRepository
- RegimeRuleRepository
- ApplicabilityRepository
- DecisionRepository
- ReportRepository
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.regimes.core.models import (
    ApplicabilityAssessment,
    ApplicabilityDecision,
    MarketRegime,
    RegimeExplainabilityRecord,
    RegimeRule,
)


def init_regimes_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and foreign key pragmas for Market Regime Engine."""
    conn.execute("PRAGMA foreign_keys = ON;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS market_regimes (
                regime_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                regime_type TEXT NOT NULL,
                volatility_state TEXT NOT NULL,
                liquidity_state TEXT NOT NULL,
                participation_state TEXT NOT NULL,
                trend_state TEXT NOT NULL,
                momentum_state TEXT NOT NULL,
                structural_state TEXT NOT NULL,
                confidence REAL NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS regime_rules (
                rule_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                priority INTEGER NOT NULL,
                deterministic_conditions_json TEXT NOT NULL,
                expected_regime TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applicability_assessments (
                assessment_id TEXT PRIMARY KEY,
                edge_id TEXT NOT NULL,
                regime_id TEXT NOT NULL,
                applicability TEXT NOT NULL,
                applicability_score REAL NOT NULL,
                activation_reason TEXT NOT NULL,
                suppression_reason TEXT NOT NULL,
                supporting_rules_json TEXT NOT NULL,
                supporting_evidence_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (regime_id) REFERENCES market_regimes(regime_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applicability_decisions (
                decision_id TEXT PRIMARY KEY,
                active_edges_json TEXT NOT NULL,
                suppressed_edges_json TEXT NOT NULL,
                explanations_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS regime_explainability_records (
                explanation_id TEXT PRIMARY KEY,
                regime_id TEXT NOT NULL,
                assessment_id TEXT NOT NULL,
                edge_id TEXT NOT NULL,
                detected_regime TEXT NOT NULL,
                supporting_rules_json TEXT NOT NULL,
                supporting_observations_json TEXT NOT NULL,
                supporting_evidence_json TEXT NOT NULL,
                scientific_explanation TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (regime_id) REFERENCES market_regimes(regime_id) ON DELETE CASCADE,
                FOREIGN KEY (assessment_id) REFERENCES applicability_assessments(assessment_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS regime_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                report_json TEXT NOT NULL
            );
        """)


class MarketRegimeRepository:
    """Repository for storing and retrieving MarketRegime models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_regimes_db(self.conn)

    def save_regime(self, regime: MarketRegime) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO market_regimes (
                    regime_id, timestamp, regime_type, volatility_state,
                    liquidity_state, participation_state, trend_state,
                    momentum_state, structural_state, confidence,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    regime.regime_id,
                    regime.timestamp,
                    regime.regime_type.value if hasattr(regime.regime_type, "value") else str(regime.regime_type),
                    regime.volatility_state.value if hasattr(regime.volatility_state, "value") else str(regime.volatility_state),
                    regime.liquidity_state.value if hasattr(regime.liquidity_state, "value") else str(regime.liquidity_state),
                    regime.participation_state.value if hasattr(regime.participation_state, "value") else str(regime.participation_state),
                    regime.trend_state.value if hasattr(regime.trend_state, "value") else str(regime.trend_state),
                    regime.momentum_state,
                    regime.structural_state.value if hasattr(regime.structural_state, "value") else str(regime.structural_state),
                    regime.confidence,
                    json.dumps(regime.metadata, sort_keys=True),
                    regime.canonical_hash,
                ),
            )

    def get_regime(self, regime_id: str) -> MarketRegime | None:
        cursor = self.conn.execute(
            """
            SELECT regime_id, timestamp, regime_type, volatility_state,
                   liquidity_state, participation_state, trend_state,
                   momentum_state, structural_state, confidence,
                   metadata_json, canonical_hash
            FROM market_regimes WHERE regime_id = ?
            """,
            (regime_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return MarketRegime(
            regime_id=row[0],
            timestamp=row[1],
            regime_type=row[2],
            volatility_state=row[3],
            liquidity_state=row[4],
            participation_state=row[5],
            trend_state=row[6],
            momentum_state=row[7],
            structural_state=row[8],
            confidence=row[9],
            metadata=json.loads(row[10]),
            canonical_hash=row[11],
        )


class RegimeRuleRepository:
    """Repository for storing and retrieving RegimeRule models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_regimes_db(self.conn)

    def save_rule(self, rule: RegimeRule) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO regime_rules (
                    rule_id, name, description, priority,
                    deterministic_conditions_json, expected_regime, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rule.rule_id,
                    rule.name,
                    rule.description,
                    rule.priority,
                    json.dumps(rule.deterministic_conditions, sort_keys=True),
                    rule.expected_regime.value if hasattr(rule.expected_regime, "value") else str(rule.expected_regime),
                    rule.canonical_hash,
                ),
            )

    def get_rule(self, rule_id: str) -> RegimeRule | None:
        cursor = self.conn.execute(
            """
            SELECT rule_id, name, description, priority,
                   deterministic_conditions_json, expected_regime, canonical_hash
            FROM regime_rules WHERE rule_id = ?
            """,
            (rule_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return RegimeRule(
            rule_id=row[0],
            name=row[1],
            description=row[2],
            priority=row[3],
            deterministic_conditions=json.loads(row[4]),
            expected_regime=row[5],
            canonical_hash=row[6],
        )


class ApplicabilityRepository:
    """Repository for storing and retrieving ApplicabilityAssessment and RegimeExplainabilityRecord models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_regimes_db(self.conn)

    def save_assessment(self, assessment: ApplicabilityAssessment) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO applicability_assessments (
                    assessment_id, edge_id, regime_id, applicability,
                    applicability_score, activation_reason, suppression_reason,
                    supporting_rules_json, supporting_evidence_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment.assessment_id,
                    assessment.edge_id,
                    assessment.regime_id,
                    assessment.applicability.value if hasattr(assessment.applicability, "value") else str(assessment.applicability),
                    assessment.applicability_score,
                    assessment.activation_reason,
                    assessment.suppression_reason,
                    json.dumps(assessment.supporting_rules, sort_keys=True),
                    json.dumps(assessment.supporting_evidence, sort_keys=True),
                    assessment.canonical_hash,
                ),
            )

    def get_assessment(self, assessment_id: str) -> ApplicabilityAssessment | None:
        cursor = self.conn.execute(
            """
            SELECT assessment_id, edge_id, regime_id, applicability,
                   applicability_score, activation_reason, suppression_reason,
                   supporting_rules_json, supporting_evidence_json, canonical_hash
            FROM applicability_assessments WHERE assessment_id = ?
            """,
            (assessment_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return ApplicabilityAssessment(
            assessment_id=row[0],
            edge_id=row[1],
            regime_id=row[2],
            applicability=row[3],
            applicability_score=row[4],
            activation_reason=row[5],
            suppression_reason=row[6],
            supporting_rules=json.loads(row[7]),
            supporting_evidence=json.loads(row[8]),
            canonical_hash=row[9],
        )

    def save_explanation(self, record: RegimeExplainabilityRecord) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO regime_explainability_records (
                    explanation_id, regime_id, assessment_id, edge_id,
                    detected_regime, supporting_rules_json, supporting_observations_json,
                    supporting_evidence_json, scientific_explanation, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.explanation_id,
                    record.regime_id,
                    record.assessment_id,
                    record.edge_id,
                    record.detected_regime,
                    json.dumps(record.supporting_rules, sort_keys=True),
                    json.dumps(record.supporting_observations, sort_keys=True),
                    json.dumps(record.supporting_evidence, sort_keys=True),
                    record.scientific_explanation,
                    record.canonical_hash,
                ),
            )

    def get_explanation(self, explanation_id: str) -> RegimeExplainabilityRecord | None:
        cursor = self.conn.execute(
            """
            SELECT explanation_id, regime_id, assessment_id, edge_id,
                   detected_regime, supporting_rules_json, supporting_observations_json,
                   supporting_evidence_json, scientific_explanation, canonical_hash
            FROM regime_explainability_records WHERE explanation_id = ?
            """,
            (explanation_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return RegimeExplainabilityRecord(
            explanation_id=row[0],
            regime_id=row[1],
            assessment_id=row[2],
            edge_id=row[3],
            detected_regime=row[4],
            supporting_rules=json.loads(row[5]),
            supporting_observations=json.loads(row[6]),
            supporting_evidence=json.loads(row[7]),
            scientific_explanation=row[8],
            canonical_hash=row[9],
        )


class DecisionRepository:
    """Repository for storing and retrieving ApplicabilityDecision models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_regimes_db(self.conn)

    def save_decision(self, decision: ApplicabilityDecision) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO applicability_decisions (
                    decision_id, active_edges_json, suppressed_edges_json,
                    explanations_json, timestamp, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.decision_id,
                    json.dumps(decision.active_edges, sort_keys=False),
                    json.dumps(decision.suppressed_edges, sort_keys=False),
                    json.dumps(decision.explanations, sort_keys=True),
                    decision.timestamp,
                    decision.canonical_hash,
                ),
            )

    def get_decision(self, decision_id: str) -> ApplicabilityDecision | None:
        cursor = self.conn.execute(
            """
            SELECT decision_id, active_edges_json, suppressed_edges_json,
                   explanations_json, timestamp, canonical_hash
            FROM applicability_decisions WHERE decision_id = ?
            """,
            (decision_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return ApplicabilityDecision(
            decision_id=row[0],
            active_edges=json.loads(row[1]),
            suppressed_edges=json.loads(row[2]),
            explanations=json.loads(row[3]),
            timestamp=row[4],
            canonical_hash=row[5],
        )


class ReportRepository:
    """Repository for storing and retrieving report objects."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_regimes_db(self.conn)

    def save_report(self, report_id: str, report_type: str, timestamp: str, report_model: Any) -> None:
        report_json = report_model.to_json() if hasattr(report_model, "to_json") else json.dumps(report_model.dict(), sort_keys=True)
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO regime_reports (report_id, report_type, timestamp, report_json) VALUES (?, ?, ?, ?)",
                (report_id, report_type, timestamp, report_json),
            )

    def get_report_json(self, report_id: str) -> str | None:
        cursor = self.conn.execute(
            "SELECT report_json FROM regime_reports WHERE report_id = ?",
            (report_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
