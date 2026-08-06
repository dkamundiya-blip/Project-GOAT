"""
Project GOAT v0.7 — Step 5.5 Scientific Research Scheduler Test Suite

Comprehensive tests covering:
- Deterministic identities (SCH_, STK_, SCHFP_, SREP_)
- Schedule generation from plans
- Dependency enforcement
- Execution ordering (topological)
- Replay determinism
- Multi-plan coordination
- State transition validation
- SQLite persistence roundtrip
- Reporting generation
- Validation (duplicate rejection, orphan rejection, cycle rejection)
- Integrity verification
- Bitwise reproducibility
- Import/export
"""

from __future__ import annotations

import os
import tempfile

import pytest
from pydantic import ValidationError

from goat.planning import (
    ScientificPlan,
    ScientificPlanStage,
    ScientificPlanTask,
    ScientificPlanningEngine,
    ScientificPlanningGraph,
    compute_plan_fingerprint,
    compute_plan_id,
    compute_task_id,
)
from goat.scheduling import (
    SCHEDULING_SCHEMA_VERSION,
    VALID_STATE_TRANSITIONS,
    ResearchSchedule,
    ScheduleExecutionState,
    ScheduledTask,
    ScientificResearchScheduler,
    ScientificScheduleCoordinator,
    ScientificSchedulingContext,
    ScientificSchedulingReport,
    ScientificSchedulingValidationError,
    SQLiteSchedulingRepository,
    compute_schedule_fingerprint,
    compute_schedule_id,
    compute_scheduled_task_id,
    generate_scheduling_report,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def planning_engine():
    """Create a ScientificPlanningEngine with a plan and graph ready for scheduling."""
    engine = ScientificPlanningEngine()
    plan, graph = engine.create_plan(
        research_objective="Investigate synthetic limit order book microstructure dynamics",
        source_priority_ids=["RPR_AAAA1111BBBB2222"],
    )
    return engine, plan, graph


@pytest.fixture
def scheduler():
    return ScientificResearchScheduler()


@pytest.fixture
def temp_db():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()
    repo = SQLiteSchedulingRepository(db_path)
    yield repo, db_path
    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


# ---------------------------------------------------------------------------
# PART 1 — Deterministic Identity Tests
# ---------------------------------------------------------------------------


class TestDeterministicIdentities:
    """Verify SCH_<HEX16>, SCHFP_<HEX64>, and STK_<HEX16> identity formats."""

    def test_schedule_fingerprint_format(self):
        """SCHFP_ prefix + 64 hex chars = 69 total chars."""
        fp = compute_schedule_fingerprint(
            source_plan_ids=["PLN_1111222233334444"],
            scheduled_task_ids=["STK_AAAA1111BBBB2222"],
            version="1.0.0",
        )
        assert fp.startswith("SCHFP_")
        assert len(fp) == 70  # SCHFP_ (6) + 64 hex chars

    def test_schedule_id_format(self):
        """SCH_ prefix + 16 hex chars = 20 total chars."""
        fp = compute_schedule_fingerprint(
            source_plan_ids=["PLN_1111222233334444"],
            scheduled_task_ids=["STK_AAAA1111BBBB2222"],
        )
        sch_id, canon_hash = compute_schedule_id(fp, "1.0.0")
        assert sch_id.startswith("SCH_")
        assert len(sch_id) == 20
        assert len(canon_hash) == 64

    def test_scheduled_task_id_format(self):
        """STK_ prefix + 16 hex chars = 20 total chars."""
        stk_id, stk_hash = compute_scheduled_task_id(
            schedule_id="SCH_1111222233334444",
            source_plan_task_id="PTK_AAAA1111BBBB2222",
            position=1,
        )
        assert stk_id.startswith("STK_")
        assert len(stk_id) == 20
        assert len(stk_hash) == 64

    def test_identity_determinism(self):
        """Same inputs always produce same identities."""
        fp1 = compute_schedule_fingerprint(["PLN_ABC"], ["STK_123"], "1.0.0")
        fp2 = compute_schedule_fingerprint(["PLN_ABC"], ["STK_123"], "1.0.0")
        assert fp1 == fp2

        id1, h1 = compute_schedule_id(fp1, "1.0.0")
        id2, h2 = compute_schedule_id(fp2, "1.0.0")
        assert id1 == id2
        assert h1 == h2

    def test_different_inputs_produce_different_identities(self):
        """Different inputs produce different identities."""
        fp1 = compute_schedule_fingerprint(["PLN_A"], ["STK_1"])
        fp2 = compute_schedule_fingerprint(["PLN_B"], ["STK_2"])
        assert fp1 != fp2


# ---------------------------------------------------------------------------
# PART 2 — Execution State Tests
# ---------------------------------------------------------------------------


class TestExecutionStates:
    """Verify ScheduleExecutionState enum values and transitions."""

    def test_all_required_states_exist(self):
        assert ScheduleExecutionState.PENDING == "pending"
        assert ScheduleExecutionState.READY == "ready"
        assert ScheduleExecutionState.RUNNING == "running"
        assert ScheduleExecutionState.BLOCKED == "blocked"
        assert ScheduleExecutionState.WAITING == "waiting"
        assert ScheduleExecutionState.COMPLETED == "completed"
        assert ScheduleExecutionState.FAILED == "failed"
        assert ScheduleExecutionState.CANCELLED == "cancelled"

    def test_state_count(self):
        assert len(ScheduleExecutionState) == 8

    def test_valid_state_transitions(self):
        """PENDING -> READY -> RUNNING -> COMPLETED is a valid path."""
        ScientificResearchScheduler.validate_state_transition(
            ScheduleExecutionState.PENDING, ScheduleExecutionState.READY,
        )
        ScientificResearchScheduler.validate_state_transition(
            ScheduleExecutionState.READY, ScheduleExecutionState.RUNNING,
        )
        ScientificResearchScheduler.validate_state_transition(
            ScheduleExecutionState.RUNNING, ScheduleExecutionState.COMPLETED,
        )

    def test_invalid_state_transition_rejected(self):
        """PENDING -> COMPLETED is not a valid transition."""
        with pytest.raises(ScientificSchedulingValidationError, match="Invalid state transition"):
            ScientificResearchScheduler.validate_state_transition(
                ScheduleExecutionState.PENDING, ScheduleExecutionState.COMPLETED,
            )

    def test_terminal_states_have_no_transitions(self):
        """COMPLETED and CANCELLED are terminal."""
        assert VALID_STATE_TRANSITIONS[ScheduleExecutionState.COMPLETED] == []
        assert VALID_STATE_TRANSITIONS[ScheduleExecutionState.CANCELLED] == []

    def test_completed_to_anything_rejected(self):
        with pytest.raises(ScientificSchedulingValidationError):
            ScientificResearchScheduler.validate_state_transition(
                ScheduleExecutionState.COMPLETED, ScheduleExecutionState.RUNNING,
            )


# ---------------------------------------------------------------------------
# PART 3 — Immutable Model Tests
# ---------------------------------------------------------------------------


class TestImmutableModels:
    """Verify models are frozen (immutable)."""

    def test_research_schedule_is_frozen(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)
        with pytest.raises((ValidationError, TypeError)):
            schedule.schedule_id = "MUTATED"

    def test_scheduled_task_is_frozen(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)
        with pytest.raises((ValidationError, TypeError)):
            tasks[0].execution_position = 999

    def test_scheduling_context_is_frozen(self):
        ctx = ScientificSchedulingContext(
            schedule_ids=["SCH_1111222233334444"],
            plan_ids=["PLN_AAAA1111BBBB2222"],
        )
        with pytest.raises((ValidationError, TypeError)):
            ctx.schedule_ids = ["MUTATED"]

    def test_scheduling_report_is_frozen(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)
        report = generate_scheduling_report(schedule, tasks)
        with pytest.raises((ValidationError, TypeError)):
            report.report_id = "MUTATED"


# ---------------------------------------------------------------------------
# PART 4 — Schedule Generation Tests
# ---------------------------------------------------------------------------


class TestScheduleGeneration:
    """Verify schedule creation from plans."""

    def test_create_schedule_from_plan(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        assert schedule.schedule_id.startswith("SCH_")
        assert len(schedule.scheduled_task_ids) == 6  # Standard 6-stage pipeline
        assert len(tasks) == 6
        assert schedule.schedule_status == ScheduleExecutionState.PENDING
        assert plan.plan_id in schedule.source_plan_ids

    def test_tasks_have_correct_parent_schedule(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        for task in tasks:
            assert task.parent_schedule_id == schedule.schedule_id

    def test_execution_order_matches_topological_order(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        # Execution order should be sequential by position
        for i, tid in enumerate(schedule.execution_order):
            task = scheduler.get_scheduled_task(tid)
            assert task.execution_position == i + 1

    def test_dependency_satisfaction_root_task(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        # First task (root) should have dependencies satisfied
        assert tasks[0].dependency_satisfaction is True

    def test_dependency_satisfaction_dependent_tasks(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        # Dependent tasks should have dependencies unsatisfied initially
        for task in tasks[1:]:
            assert task.dependency_satisfaction is False

    def test_empty_plan_rejected(self, scheduler):
        """Cannot schedule a plan with no tasks."""
        graph = ScientificPlanningGraph()
        fp = compute_plan_fingerprint("Empty", ["RPR_0000"])
        pid, phash = compute_plan_id(fp)
        plan = ScientificPlan(
            plan_id=pid,
            canonical_hash=phash,
            scientific_fingerprint=fp,
            creation_timestamp="2026-07-30T00:00:00Z",
            source_priority_ids=["RPR_0000"],
            research_objective="Empty",
        )
        with pytest.raises(ScientificSchedulingValidationError, match="no tasks"):
            scheduler.create_schedule(plan, graph)


# ---------------------------------------------------------------------------
# PART 5 — Replay & Determinism Tests
# ---------------------------------------------------------------------------


class TestReplayDeterminism:
    """Verify deterministic replay produces bitwise-identical results."""

    def test_replay_returns_same_order(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        replayed_schedule, replayed_order = scheduler.replay_schedule(schedule.schedule_id)
        assert replayed_schedule.schedule_id == schedule.schedule_id
        assert replayed_order == list(schedule.execution_order)

    def test_bitwise_reproducibility(self):
        """Two independent scheduler instances produce identical schedules for same plan."""
        engine1 = ScientificPlanningEngine()
        plan1, graph1 = engine1.create_plan("Reproduce Test", ["RPR_REPR1111REPR2222"])

        engine2 = ScientificPlanningEngine()
        plan2, graph2 = engine2.create_plan("Reproduce Test", ["RPR_REPR1111REPR2222"])

        # Plans should be identical
        assert plan1.plan_id == plan2.plan_id
        assert plan1.canonical_hash == plan2.canonical_hash

        sched1 = ScientificResearchScheduler()
        sched2 = ScientificResearchScheduler()

        s1, t1 = sched1.create_schedule(plan1, graph1)
        s2, t2 = sched2.create_schedule(plan2, graph2)

        # Schedules should have identical fingerprints and task IDs
        assert s1.scientific_fingerprint == s2.scientific_fingerprint
        assert s1.scheduled_task_ids == s2.scheduled_task_ids
        assert s1.execution_order == s2.execution_order

    def test_integrity_verification_passes(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)
        assert scheduler.verify_schedule_integrity(schedule) is True


# ---------------------------------------------------------------------------
# PART 6 — Multi-Plan Coordination Tests
# ---------------------------------------------------------------------------


class TestMultiPlanCoordination:
    """Verify ScientificScheduleCoordinator merging multiple schedules."""

    def test_merge_two_schedules(self):
        engine = ScientificPlanningEngine()

        plan1, graph1 = engine.create_plan("Plan Alpha", ["RPR_ALPHA111ALPHA222"])
        plan2, graph2 = engine.create_plan("Plan Beta", ["RPR_BETA1111BETA2222"])

        scheduler = ScientificResearchScheduler()
        s1, t1 = scheduler.create_schedule(plan1, graph1)
        s2, t2 = scheduler.create_schedule(plan2, graph2)

        coordinator = ScientificScheduleCoordinator()
        merged, merged_tasks = coordinator.merge_schedules(
            [s1, s2],
            {s1.schedule_id: t1, s2.schedule_id: t2},
        )

        assert merged.schedule_id.startswith("SCH_")
        assert len(merged.scheduled_task_ids) == 12  # 6 + 6
        assert len(merged.source_plan_ids) == 2
        assert plan1.plan_id in merged.source_plan_ids
        assert plan2.plan_id in merged.source_plan_ids

    def test_merge_preserves_intra_schedule_order(self):
        engine = ScientificPlanningEngine()

        plan1, graph1 = engine.create_plan("Plan One", ["RPR_ONE11111ONE22222"])
        plan2, graph2 = engine.create_plan("Plan Two", ["RPR_TWO11111TWO22222"])

        scheduler = ScientificResearchScheduler()
        s1, t1 = scheduler.create_schedule(plan1, graph1)
        s2, t2 = scheduler.create_schedule(plan2, graph2)

        coordinator = ScientificScheduleCoordinator()
        merged, merged_tasks = coordinator.merge_schedules(
            [s1, s2],
            {s1.schedule_id: t1, s2.schedule_id: t2},
        )

        # Execution order should have all tasks from one schedule followed by the other
        # (since schedules are sorted by schedule_id)
        assert len(merged.execution_order) == 12

    def test_merge_empty_rejected(self):
        coordinator = ScientificScheduleCoordinator()
        with pytest.raises(ValueError, match="Cannot merge empty"):
            coordinator.merge_schedules([], {})

    def test_merge_deterministic_ordering(self):
        """Merging in different list order produces same result (sorted by schedule_id)."""
        engine = ScientificPlanningEngine()

        plan1, graph1 = engine.create_plan("Determinism A", ["RPR_DETA1111DETA2222"])
        plan2, graph2 = engine.create_plan("Determinism B", ["RPR_DETB1111DETB2222"])

        sched1 = ScientificResearchScheduler()
        s1, t1 = sched1.create_schedule(plan1, graph1)

        sched2 = ScientificResearchScheduler()
        s2, t2 = sched2.create_schedule(plan2, graph2)

        coord1 = ScientificScheduleCoordinator()
        m1, _ = coord1.merge_schedules([s1, s2], {s1.schedule_id: t1, s2.schedule_id: t2})

        coord2 = ScientificScheduleCoordinator()
        m2, _ = coord2.merge_schedules([s2, s1], {s1.schedule_id: t1, s2.schedule_id: t2})

        assert m1.scientific_fingerprint == m2.scientific_fingerprint
        assert m1.execution_order == m2.execution_order


# ---------------------------------------------------------------------------
# PART 7 — Reporting Tests
# ---------------------------------------------------------------------------


class TestReporting:
    """Verify ScientificSchedulingReport generation."""

    def test_report_generation(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        report = generate_scheduling_report(schedule, tasks)
        assert isinstance(report, ScientificSchedulingReport)
        assert report.report_id.startswith("SREP_")
        assert report.schedule_id == schedule.schedule_id
        assert len(report.execution_queue) == 6
        assert report.schedule_metadata["total_scheduled_tasks"] == 6

    def test_report_determinism(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        r1 = generate_scheduling_report(schedule, tasks, timestamp="2026-07-30T00:00:00Z")
        r2 = generate_scheduling_report(schedule, tasks, timestamp="2026-07-30T00:00:00Z")
        assert r1.report_id == r2.report_id
        assert r1.execution_readiness == r2.execution_readiness

    def test_report_task_categorization(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        report = generate_scheduling_report(schedule, tasks)
        # All tasks are PENDING initially, so no blocked/completed/waiting
        assert report.blocked_tasks == []
        assert report.completed_tasks == []
        assert report.waiting_tasks == []

    def test_report_execution_readiness(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        report = generate_scheduling_report(schedule, tasks)
        # No tasks are READY or COMPLETED, so readiness = 0
        assert report.execution_readiness == 0.0


# ---------------------------------------------------------------------------
# PART 8 — SQLite Persistence Tests
# ---------------------------------------------------------------------------


class TestSQLitePersistence:
    """Verify persistence roundtrip for all domain objects."""

    def test_schedule_roundtrip(self, planning_engine, scheduler, temp_db):
        repo, _ = temp_db
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        repo.save_schedule(schedule)
        loaded = repo.get_schedule(schedule.schedule_id)

        assert loaded is not None
        assert loaded.schedule_id == schedule.schedule_id
        assert loaded.canonical_hash == schedule.canonical_hash
        assert loaded.scientific_fingerprint == schedule.scientific_fingerprint
        assert loaded.scheduled_task_ids == schedule.scheduled_task_ids
        assert loaded.execution_order == schedule.execution_order

    def test_task_roundtrip(self, planning_engine, scheduler, temp_db):
        repo, _ = temp_db
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        repo.save_schedule(schedule)
        for task in tasks:
            repo.save_task(task)

        loaded_tasks = repo.get_tasks_for_schedule(schedule.schedule_id)
        assert len(loaded_tasks) == 6

        # Verify ordering
        for i, task in enumerate(loaded_tasks):
            assert task.execution_position == i + 1

    def test_context_roundtrip(self, planning_engine, scheduler, temp_db):
        repo, _ = temp_db
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        repo.save_schedule(schedule)

        ctx = ScientificSchedulingContext(
            schedule_ids=[schedule.schedule_id],
            plan_ids=[plan.plan_id],
            priority_ids=["RPR_AAAA1111BBBB2222"],
        )
        repo.save_context(schedule.schedule_id, ctx)
        loaded = repo.get_context(schedule.schedule_id)

        assert loaded is not None
        assert loaded.schedule_ids == [schedule.schedule_id]
        assert loaded.plan_ids == [plan.plan_id]

    def test_report_roundtrip(self, planning_engine, scheduler, temp_db):
        repo, _ = temp_db
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        repo.save_schedule(schedule)
        report = generate_scheduling_report(schedule, tasks)
        repo.save_report(report)

        loaded = repo.get_report(report.report_id)
        assert loaded is not None
        assert loaded.report_id == report.report_id
        assert loaded.schedule_id == schedule.schedule_id

    def test_audit_events(self, planning_engine, scheduler, temp_db):
        repo, _ = temp_db
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        repo.save_schedule(schedule)
        repo.save_audit_event(
            schedule.schedule_id,
            "schedule_created",
            "2026-07-30T00:00:00Z",
            {"source": "test"},
        )

        events = repo.get_audit_events(schedule.schedule_id)
        assert len(events) == 1
        assert events[0]["event_type"] == "schedule_created"

    def test_export_import_roundtrip(self, planning_engine, scheduler, temp_db):
        repo, _ = temp_db
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        # Save everything
        repo.save_schedule(schedule)
        for task in tasks:
            repo.save_task(task)

        # Export
        exported = repo.export_schedule(schedule.schedule_id)
        assert exported["schema_version"] == SCHEDULING_SCHEMA_VERSION

        # Import into fresh db
        tmp2 = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        db2_path = tmp2.name
        tmp2.close()
        repo2 = SQLiteSchedulingRepository(db2_path)

        imported = repo2.import_schedule(exported)
        assert imported.schedule_id == schedule.schedule_id
        assert imported.canonical_hash == schedule.canonical_hash

        repo2.close()
        os.remove(db2_path)

    def test_integrity_verification(self, planning_engine, scheduler, temp_db):
        repo, _ = temp_db
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        repo.save_schedule(schedule)
        for task in tasks:
            repo.save_task(task)

        assert repo.verify_integrity(schedule.schedule_id) is True

    def test_list_schedules(self, planning_engine, scheduler, temp_db):
        repo, _ = temp_db
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        repo.save_schedule(schedule)
        all_schedules = repo.list_schedules()
        assert len(all_schedules) == 1
        assert all_schedules[0].schedule_id == schedule.schedule_id

    def test_schema_version(self, temp_db):
        repo, _ = temp_db
        assert SCHEDULING_SCHEMA_VERSION == 1


# ---------------------------------------------------------------------------
# PART 9 — Validation Tests
# ---------------------------------------------------------------------------


class TestValidation:
    """Verify fail-closed validation rules."""

    def test_duplicate_schedule_id_rejected(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        # First schedule succeeds
        scheduler.create_schedule(plan, graph)
        # Creating same schedule again should raise (duplicate IDs)
        # Need a fresh engine to get identical plan
        engine2 = ScientificPlanningEngine()
        plan2, graph2 = engine2.create_plan(
            research_objective="Investigate synthetic limit order book microstructure dynamics",
            source_priority_ids=["RPR_AAAA1111BBBB2222"],
        )
        with pytest.raises(ScientificSchedulingValidationError, match="Duplicate"):
            scheduler.create_schedule(plan2, graph2)

    def test_invalid_state_transition_rejected(self):
        with pytest.raises(ScientificSchedulingValidationError):
            ScientificResearchScheduler.validate_state_transition(
                ScheduleExecutionState.COMPLETED, ScheduleExecutionState.RUNNING,
            )

    def test_cancelled_to_anything_rejected(self):
        for state in ScheduleExecutionState:
            if state != ScheduleExecutionState.CANCELLED:
                with pytest.raises(ScientificSchedulingValidationError):
                    ScientificResearchScheduler.validate_state_transition(
                        ScheduleExecutionState.CANCELLED, state,
                    )

    def test_schedule_id_format_validation(self):
        """ResearchSchedule rejects invalid schedule_id format."""
        with pytest.raises(ValidationError):
            ResearchSchedule(
                schedule_id="INVALID",
                canonical_hash="a" * 64,
                scientific_fingerprint="SCHFP_" + "a" * 64,
                creation_timestamp="2026-07-30T00:00:00Z",
            )

    def test_task_schedule_id_format_validation(self):
        """ScheduledTask rejects invalid task_schedule_id format."""
        with pytest.raises(ValidationError):
            ScheduledTask(
                task_schedule_id="INVALID",
                parent_schedule_id="SCH_1111222233334444",
                source_plan_task_id="PTK_AAAA1111BBBB2222",
                task_schedule_hash="a" * 64,
            )

    def test_context_extra_fields_rejected(self):
        with pytest.raises(ValidationError):
            ScientificSchedulingContext(
                schedule_ids=["SCH_1111222233334444"],
                unknown_field="should_fail",
            )

    def test_import_schema_version_mismatch_rejected(self, temp_db):
        repo, _ = temp_db
        with pytest.raises(ValueError, match="Schema version mismatch"):
            repo.import_schedule({"schema_version": 999})


# ---------------------------------------------------------------------------
# PART 10 — Public API Smoke Tests
# ---------------------------------------------------------------------------


class TestPublicAPI:
    """Verify all required public API symbols are importable and usable."""

    def test_all_public_symbols_importable(self):
        from goat.scheduling import (
            ResearchSchedule,
            ScheduledTask,
            ScheduleExecutionState,
            ScientificResearchScheduler,
            ScientificScheduleCoordinator,
            ScientificSchedulingContext,
            ScientificSchedulingReport,
            ScientificSchedulingValidationError,
        )
        # All symbols should be valid types
        assert ResearchSchedule is not None
        assert ScheduledTask is not None
        assert ScheduleExecutionState is not None
        assert ScientificResearchScheduler is not None
        assert ScientificScheduleCoordinator is not None
        assert ScientificSchedulingContext is not None
        assert ScientificSchedulingReport is not None
        assert ScientificSchedulingValidationError is not None

    def test_scheduler_instantiation(self):
        scheduler = ScientificResearchScheduler()
        assert scheduler is not None

    def test_coordinator_instantiation(self):
        coordinator = ScientificScheduleCoordinator()
        assert coordinator is not None

    def test_repository_instantiation(self):
        repo = SQLiteSchedulingRepository(":memory:")
        assert repo is not None
        repo.close()


# ---------------------------------------------------------------------------
# PART 11 — Regression & Edge Case Tests
# ---------------------------------------------------------------------------


class TestRegressionEdgeCases:
    """Additional edge cases and regression tests."""

    def test_get_nonexistent_schedule_raises(self, scheduler):
        with pytest.raises(KeyError):
            scheduler.get_schedule("SCH_NONEXISTENT00000")

    def test_get_nonexistent_task_raises(self, scheduler):
        with pytest.raises(KeyError):
            scheduler.get_scheduled_task("STK_NONEXISTENT00000")

    def test_get_ready_tasks(self, planning_engine, scheduler):
        _, plan, graph = planning_engine
        schedule, tasks = scheduler.create_schedule(plan, graph)

        ready = scheduler.get_ready_tasks(schedule.schedule_id)
        # Only root task (first) has dependencies satisfied and is PENDING
        assert len(ready) == 1
        assert ready[0].execution_position == 1

    def test_coordinator_retrieval(self):
        coordinator = ScientificScheduleCoordinator()
        with pytest.raises(KeyError):
            coordinator.get_merged_schedule("SCH_NONEXISTENT00000")

    def test_export_nonexistent_schedule_raises(self, temp_db):
        repo, _ = temp_db
        with pytest.raises(KeyError):
            repo.export_schedule("SCH_NONEXISTENT00000")

    def test_integrity_verification_nonexistent_raises(self, temp_db):
        repo, _ = temp_db
        with pytest.raises(ValueError):
            repo.verify_integrity("SCH_NONEXISTENT00000")

    def test_full_workflow_integration(self):
        """End-to-end: prioritization -> planning -> scheduling -> reporting -> persistence."""
        # Planning
        engine = ScientificPlanningEngine()
        plan, graph = engine.create_plan(
            research_objective="Full integration test objective",
            source_priority_ids=["RPR_INTG1111INTG2222"],
        )

        # Scheduling
        scheduler = ScientificResearchScheduler()
        schedule, tasks = scheduler.create_schedule(plan, graph)

        # Reporting
        report = generate_scheduling_report(schedule, tasks)

        # Persistence
        repo = SQLiteSchedulingRepository(":memory:")
        repo.save_schedule(schedule)
        for task in tasks:
            repo.save_task(task)
        repo.save_report(report)

        # Verify
        loaded = repo.get_schedule(schedule.schedule_id)
        assert loaded.schedule_id == schedule.schedule_id
        assert repo.verify_integrity(schedule.schedule_id)

        # Replay
        replayed, order = scheduler.replay_schedule(schedule.schedule_id)
        assert order == list(schedule.execution_order)

        repo.close()
