"""
Project GOAT v0.7 — Step 5.1 Scientific Consensus Engine Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest
from pydantic import ValidationError

from goat.consensus import (
    ConsensusConflict,
    ConsensusContext,
    ConsensusEngine,
    ConsensusReport,
    ConsensusRuleEngine,
    ConsensusStatus,
    ConsensusValidationError,
    SQLiteConsensusRepository,
    ScientificConsensus,
    compute_conflict_id,
    compute_consensus_fingerprint,
    compute_consensus_id,
    generate_consensus_report,
)


@pytest.fixture
def temp_engine():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    repo = SQLiteConsensusRepository(db_path)
    engine = ConsensusEngine()
    yield engine, repo, db_path

    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_consensus_and_conflict_identity():
    """Verify CNS_<HEX16>, CNFP_<HEX64>, CCF_<HEX16>, and CREP_<HEX16> identities."""
    cid, c_hash = compute_conflict_id(["EVD_1111", "EVD_2222"], "high")
    assert cid.startswith("CCF_")
    assert len(cid) == 20
    assert len(c_hash) == 64

    cnfp = compute_consensus_fingerprint(["SYN_1111"], ["KNW_1111"], "1.0.0")
    assert cnfp.startswith("CNFP_")
    assert len(cnfp) == 69

    cns_id, s_hash = compute_consensus_id(cnfp, "1.0.0")
    assert cns_id.startswith("CNS_")
    assert len(cns_id) == 20


def test_consensus_rule_engine_evaluations():
    """Verify ConsensusRuleEngine deterministic status evaluations."""
    rule_engine = ConsensusRuleEngine()

    # Test Insufficient Evidence
    r1 = rule_engine.evaluate_synthesis_summary({"confidence_summary": {"total_evidence_count": 1}})
    assert r1["status"] == ConsensusStatus.INSUFFICIENT_EVIDENCE

    # Test Conflict State
    r2 = rule_engine.evaluate_synthesis_summary({
        "confidence_summary": {"total_evidence_count": 5},
        "conflict_summary": {"high_severity_count": 1},
    })
    assert r2["status"] == ConsensusStatus.CONFLICTED

    # Test Strong Consensus State
    r3 = rule_engine.evaluate_synthesis_summary({
        "confidence_summary": {"total_evidence_count": 6, "validated_count": 5},
        "replication_summary": {"exact_replications": 2, "total_replications": 2},
        "conflict_summary": {"high_severity_count": 0, "total_contradictions": 0},
    })
    assert r3["status"] == ConsensusStatus.CONSENSUS
    assert r3["confidence"] == 0.95
    assert r3["maturity"] == "mature"


def test_consensus_engine_workflow_and_replay(temp_engine):
    """Verify ConsensusEngine consensus evaluation and replay."""
    engine, repo, _ = temp_engine

    # Register a conflict
    conflict = engine.register_conflict(["EVD_1001", "EVD_1002"], synthesis_references=["SYN_100"])
    assert conflict.conflict_id.startswith("CCF_")

    synthesis_summary = {
        "confidence_summary": {"total_evidence_count": 4, "validated_count": 3},
        "replication_summary": {"total_replications": 1},
        "conflict_summary": {"high_severity_count": 0},
    }

    consensus = engine.evaluate_consensus(["SYN_100"], synthesis_summary, knowledge_ids=["KNW_200"])
    assert consensus.consensus_id.startswith("CNS_")
    assert consensus.consensus_status == ConsensusStatus.STRONG
    assert consensus.confidence_level == 0.8

    # Replay consensus
    replayed = engine.replay_consensus(consensus.consensus_id)
    assert replayed.consensus_id == consensus.consensus_id

    # SQLite Persistence
    repo.save_consensus(consensus)
    loaded = repo.get_consensus(consensus.consensus_id)
    assert loaded is not None
    assert loaded.consensus_id == consensus.consensus_id


def test_consensus_reporting(temp_engine):
    """Verify generate_consensus_report produces deterministic ConsensusReport."""
    engine, _, _ = temp_engine

    synthesis_summary = {
        "confidence_summary": {"total_evidence_count": 6, "validated_count": 5},
        "replication_summary": {"exact_replications": 2},
        "conflict_summary": {"total_contradictions": 0},
    }
    consensus = engine.evaluate_consensus(["SYN_300"], synthesis_summary)

    report = generate_consensus_report(consensus, unresolved_conflicts=["CCF_9999"])
    assert isinstance(report, ConsensusReport)
    assert report.report_id.startswith("CREP_")
    assert report.status_summary == "consensus"
    assert report.maturity_assessment == "mature"
