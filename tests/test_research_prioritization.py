"""
Project GOAT v0.7 — Step 5.3 Scientific Research Prioritization Engine Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest
from pydantic import ValidationError

from goat.prioritization import (
    PriorityLevel,
    ResearchOpportunityType,
    ResearchPrioritizationContext,
    ResearchPrioritizationEngine,
    ResearchPriority,
    ResearchPriorityQueue,
    ResearchPriorityReport,
    ResearchPriorityRuleEngine,
    ResearchPriorityValidationError,
    SQLitePrioritizationRepository,
    compute_priority_fingerprint,
    compute_priority_id,
    compute_queue_id,
    generate_priority_report,
)


@pytest.fixture
def temp_engine():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    repo = SQLitePrioritizationRepository(db_path)
    engine = ResearchPrioritizationEngine()
    yield engine, repo, db_path

    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_priority_and_queue_identity():
    """Verify RPR_<HEX16>, PRFP_<HEX64>, RPQ_<HEX16>, and RPREP_<HEX16> identities."""
    prfp = compute_priority_fingerprint("conflict_resolution", "Unresolved evidence conflict", "1.0.0")
    assert prfp.startswith("PRFP_")
    assert len(prfp) == 69

    pr_id, p_hash = compute_priority_id(prfp, "1.0.0")
    assert pr_id.startswith("RPR_")
    assert len(pr_id) == 20

    qid, q_hash = compute_queue_id([pr_id])
    assert qid.startswith("RPQ_")
    assert len(qid) == 20


def test_priority_rule_engine_evaluations():
    """Verify ResearchPriorityRuleEngine deterministic scoring evaluations."""
    rule_engine = ResearchPriorityRuleEngine()

    # Rule 1: Conflict Resolution (Critical)
    r1 = rule_engine.evaluate_opportunity({"conflict_ids": ["CCF_001"]})
    assert r1["level"] == PriorityLevel.CRITICAL
    assert r1["score"] == 0.95
    assert r1["opportunity_type"] == ResearchOpportunityType.CONFLICT_RESOLUTION

    # Rule 2: Replication Required (High)
    r2 = rule_engine.evaluate_opportunity({"validated_count": 2, "replication_strength": 0.0})
    assert r2["level"] == PriorityLevel.HIGH
    assert r2["score"] == 0.85

    # Rule 3: Insufficient Evidence (High)
    r3 = rule_engine.evaluate_opportunity({"consensus_status": "insufficient_evidence"})
    assert r3["level"] == PriorityLevel.HIGH
    assert r3["score"] == 0.75


def test_prioritization_engine_queue_and_replay(temp_engine):
    """Verify ResearchPrioritizationEngine queue ordering and replay."""
    engine, repo, _ = temp_engine

    opp1 = engine.prioritize_opportunity({"consensus_status": "insufficient_evidence"})  # score 0.75
    opp2 = engine.prioritize_opportunity({"conflict_ids": ["CCF_999"]})                    # score 0.95
    opp3 = engine.prioritize_opportunity({"validated_count": 1, "replication_strength": 0.0})  # score 0.85

    queue = engine.build_priority_queue([opp1.priority_id, opp2.priority_id, opp3.priority_id])
    assert queue.queue_id.startswith("RPQ_")
    # Verify ordered score descending: opp2 (0.95), opp3 (0.85), opp1 (0.75)
    assert queue.ordered_priority_ids == [opp2.priority_id, opp3.priority_id, opp1.priority_id]

    # Replay
    replayed = engine.replay_prioritization(queue.queue_id)
    assert replayed.queue_id == queue.queue_id

    # Persistence
    repo.save_priority(opp2)
    repo.save_queue(queue)
    loaded_q = repo.get_queue(queue.queue_id)
    assert loaded_q is not None
    assert loaded_q.queue_id == queue.queue_id


def test_priority_reporting(temp_engine):
    """Verify generate_priority_report produces deterministic ResearchPriorityReport."""
    engine, _, _ = temp_engine

    opp = engine.prioritize_opportunity({"conflict_ids": ["CCF_111"]})
    queue = engine.build_priority_queue([opp.priority_id])

    report = generate_priority_report(queue, justifications=[opp.scientific_justification])
    assert isinstance(report, ResearchPriorityReport)
    assert report.report_id.startswith("RPREP_")
    assert report.queue_statistics["total_prioritized_candidates"] == 1
