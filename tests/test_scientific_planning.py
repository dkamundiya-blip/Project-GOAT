"""
Project GOAT v0.7 — Step 5.4 Scientific Planning Engine Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest
from pydantic import ValidationError

from goat.planning import (
    SQLitePlanningRepository,
    ScientificPlan,
    ScientificPlanStage,
    ScientificPlanTask,
    ScientificPlanningContext,
    ScientificPlanningEngine,
    ScientificPlanningGraph,
    ScientificPlanningReport,
    ScientificPlanningValidationError,
    compute_plan_fingerprint,
    compute_plan_id,
    compute_task_id,
    generate_planning_report,
)


@pytest.fixture
def temp_engine():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    repo = SQLitePlanningRepository(db_path)
    engine = ScientificPlanningEngine()
    yield engine, repo, db_path

    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_plan_and_task_identity():
    """Verify PLN_<HEX16>, PLFP_<HEX64>, PTK_<HEX16>, and PREP_<HEX16> identities."""
    plfp = compute_plan_fingerprint("Investigate alpha decay", ["RPR_1111"], "1.0.0")
    assert plfp.startswith("PLFP_")
    assert len(plfp) == 69

    plan_id, p_hash = compute_plan_id(plfp, "1.0.0")
    assert plan_id.startswith("PLN_")
    assert len(plan_id) == 20

    tid, t_hash = compute_task_id(plan_id, 1, "initialization")
    assert tid.startswith("PTK_")
    assert len(tid) == 20
    assert len(t_hash) == 64


def test_planning_graph_topological_ordering_and_cycle_rejection():
    """Verify ScientificPlanningGraph DAG topological sorting, roots, terminals, and cycle rejection."""
    graph = ScientificPlanningGraph()
    plan_id, _ = compute_plan_id(compute_plan_fingerprint("Test Obj", ["RPR_1111"]))

    t1_id, t1_hash = compute_task_id(plan_id, 1, "initialization")
    t2_id, t2_hash = compute_task_id(plan_id, 2, "execution")

    t1 = ScientificPlanTask(
        task_id=t1_id,
        parent_plan_id=plan_id,
        stage=ScientificPlanStage.INITIALIZATION,
        execution_order=1,
        task_hash=t1_hash,
    )
    t2 = ScientificPlanTask(
        task_id=t2_id,
        parent_plan_id=plan_id,
        stage=ScientificPlanStage.EXECUTION,
        dependencies=[t1_id],
        execution_order=2,
        task_hash=t2_hash,
    )

    graph.add_task(t1)
    graph.add_task(t2)

    order = graph.get_topological_order()
    assert order == [t1_id, t2_id]
    assert graph.get_root_tasks() == [t1_id]
    assert graph.get_terminal_tasks() == [t2_id]


def test_planning_engine_workflow_and_replay(temp_engine):
    """Verify ScientificPlanningEngine plan generation, task DAG construction, and replay."""
    engine, repo, _ = temp_engine

    plan, graph = engine.create_plan(
        research_objective="Investigate market microstructure alpha decay in synthetic limit order books",
        source_priority_ids=["RPR_9999"],
    )
    assert plan.plan_id.startswith("PLN_")
    assert plan.execution_status == "proposed"

    order = graph.get_topological_order()
    assert len(order) == 6

    # Replay
    replayed_plan, replayed_order = engine.replay_planning(plan.plan_id)
    assert replayed_plan.plan_id == plan.plan_id
    assert replayed_order == order

    # Persistence
    repo.save_plan(plan)
    loaded = repo.get_plan(plan.plan_id)
    assert loaded is not None
    assert loaded.plan_id == plan.plan_id


def test_planning_reporting(temp_engine):
    """Verify generate_planning_report produces deterministic ScientificPlanningReport."""
    engine, _, _ = temp_engine

    plan, graph = engine.create_plan("Report Objective", ["RPR_8888"])
    order = graph.get_topological_order()

    report = generate_planning_report(plan, order)
    assert isinstance(report, ScientificPlanningReport)
    assert report.report_id.startswith("PREP_")
    assert report.task_statistics["total_planned_tasks"] == 6
    assert len(report.topological_execution_order) == 6
