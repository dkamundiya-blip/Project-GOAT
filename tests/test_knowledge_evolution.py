"""
Project GOAT v0.7 — Step 5.2 Knowledge Evolution Engine Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest
from pydantic import ValidationError

from goat.evolution import (
    KnowledgeEvolution,
    KnowledgeEvolutionContext,
    KnowledgeEvolutionEngine,
    KnowledgeEvolutionReport,
    KnowledgeEvolutionType,
    KnowledgeEvolutionValidationError,
    KnowledgeLineageGraph,
    KnowledgeVersion,
    SQLiteEvolutionRepository,
    compute_evolution_fingerprint,
    compute_evolution_id,
    compute_version_id,
    generate_evolution_report,
)


@pytest.fixture
def temp_engine():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    repo = SQLiteEvolutionRepository(db_path)
    engine = KnowledgeEvolutionEngine()
    yield engine, repo, db_path

    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_evolution_and_version_identity():
    """Verify KEV_<HEX16>, EVFP_<HEX64>, KVR_<HEX16>, and EREP_<HEX16> identities."""
    vid, v_hash = compute_version_id("KNW_1111", 1)
    assert vid.startswith("KVR_")
    assert len(vid) == 20
    assert len(v_hash) == 64

    evfp = compute_evolution_fingerprint("", "KNW_1111", "created", "1.0.0")
    assert evfp.startswith("EVFP_")
    assert len(evfp) == 69

    ev_id, e_hash = compute_evolution_id(evfp, "1.0.0")
    assert ev_id.startswith("KEV_")
    assert len(ev_id) == 20


def test_lineage_graph_traversal_and_cycle_detection():
    """Verify KnowledgeLineageGraph ancestry, descendants, and cycle rejection."""
    graph = KnowledgeLineageGraph()

    v1_id, _ = compute_version_id("KNW_0001", 1)
    v2_id, _ = compute_version_id("KNW_0002", 2)
    v3_id, _ = compute_version_id("KNW_0003", 3)

    v1 = KnowledgeVersion(
        version_id=v1_id,
        knowledge_id="KNW_0001",
        version_number=1,
        creation_timestamp="2026-07-30T00:00:00Z",
        version_hash="a" * 64,
    )
    v2 = KnowledgeVersion(
        version_id=v2_id,
        knowledge_id="KNW_0002",
        version_number=2,
        parent_version_id=v1_id,
        creation_timestamp="2026-07-30T00:00:00Z",
        version_hash="b" * 64,
    )

    graph.add_version(v1)
    graph.add_version(v2)

    assert graph.get_ancestors(v2_id) == [v1_id]
    assert graph.get_descendants(v1_id) == [v2_id]
    assert graph.get_root(v2_id) == v1_id

    # Duplicate rejection test
    with pytest.raises(ValueError, match="already exists"):
        graph.add_version(v1)

    # Cycle test: v3 tries to set parent_version_id to itself
    v_cycle = KnowledgeVersion(
        version_id=v3_id,
        knowledge_id="KNW_0003",
        version_number=3,
        parent_version_id=v3_id,
        creation_timestamp="2026-07-30T00:00:00Z",
        version_hash="c" * 64,
    )
    with pytest.raises(ValueError, match="Cycle detected"):
        graph.add_version(v_cycle)


def test_knowledge_evolution_workflow_and_replay(temp_engine):
    """Verify KnowledgeEvolutionEngine version creation, superseding, and replay."""
    engine, repo, _ = temp_engine

    # Step 1: Create initial version
    v1, ev1 = engine.create_initial_version("KNW_0001", consensus_reference="CNS_001")
    assert v1.version_id.startswith("KVR_")
    assert v1.version_number == 1
    assert v1.status == "active"
    assert ev1.evolution_type == KnowledgeEvolutionType.CREATED

    # Step 2: Supersede with refined version
    v2, ev2 = engine.supersede_knowledge(
        previous_version_id=v1.version_id,
        new_knowledge_id="KNW_0002",
        evolution_type=KnowledgeEvolutionType.REFINED,
        change_summary="Refined market microstructure alpha parameters based on new consensus",
        consensus_reference="CNS_002",
    )
    assert v2.version_number == 2
    assert v2.parent_version_id == v1.version_id
    assert engine.get_version(v1.version_id).status == "superseded"
    assert ev2.evolution_type == KnowledgeEvolutionType.REFINED

    # Step 3: Replay
    replayed = engine.replay_evolution(ev2.evolution_id)
    assert replayed.evolution_id == ev2.evolution_id

    # Step 4: Persistence
    repo.save_evolution(ev2)
    repo.save_version(v2)
    loaded_ev = repo.get_evolution(ev2.evolution_id)
    assert loaded_ev is not None
    assert loaded_ev.evolution_id == ev2.evolution_id


def test_evolution_reporting(temp_engine):
    """Verify generate_evolution_report produces deterministic KnowledgeEvolutionReport."""
    engine, _, _ = temp_engine

    v1, ev1 = engine.create_initial_version("KNW_5555")
    report = generate_evolution_report(ev1, v1, ancestors_count=0)

    assert isinstance(report, KnowledgeEvolutionReport)
    assert report.report_id.startswith("EREP_")
    assert report.evolution_type == "created"
    assert report.lineage_statistics["version_number"] == 1
