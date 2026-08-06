"""
Project GOAT v0.7 — Step 5.6 Scientific Research Execution Engine Test Suite

Comprehensive tests covering:
- Deterministic identities (SES_, EVT_, SESFP_, EREP_)
- Execution lifecycle (session create, start, complete, fail)
- Event generation and append-only history
- Execution history integrity verification
- Replay determinism
- State transition validation
- Multi-task execution workflow
- SQLite persistence roundtrip
- Reporting generation
- Validation (duplicate rejection, orphan rejection, invalid transitions)
- Public API smoke tests
- Bitwise reproducibility
- Import/export
"""

from __future__ import annotations

import os
import tempfile

import pytest
from pydantic import ValidationError

from goat.planning import (
    ScientificPlanningEngine,
)
from goat.scheduling import (
    ResearchSchedule,
    ScheduledTask,
    ScientificResearchScheduler,
)
from goat.execution import (
    EXECUTION_SCHEMA_VERSION,
    VALID_EXECUTION_TRANSITIONS,
    ExecutionEvent,
    ExecutionHistory,
    ExecutionState,
    ScientificExecutionContext,
    ScientificExecutionReport,
    ScientificExecutionSession,
    ScientificExecutionValidationError,
    ScientificResearchExecutionEngine,
    SQLiteExecutionRepository,
    compute_event_id,
    compute_session_fingerprint,
    compute_session_id,
    generate_execution_report,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def schedule_with_tasks():
    """Create a schedule with tasks ready for execution."""
    engine = ScientificPlanningEngine()
    plan, graph = engine.create_plan(
        research_objective="Investigate synthetic limit order book microstructure dynamics",
        source_priority_ids=["RPR_AAAA1111BBBB2222"],
    )
    scheduler = ScientificResearchScheduler()
    schedule, tasks = scheduler.create_schedule(plan, graph)
    return schedule, tasks


@pytest.fixture
def execution_engine():
    return ScientificResearchExecutionEngine()


@pytest.fixture
def session_with_engine(schedule_with_tasks, execution_engine):
    """Create an execution session from a schedule."""
    schedule, tasks = schedule_with_tasks
    session = execution_engine.create_session(schedule, tasks)
    return execution_engine, session, schedule, tasks


@pytest.fixture
def temp_db():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()
    repo = SQLiteExecutionRepository(db_path)
    yield repo, db_path
    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


# ---------------------------------------------------------------------------
# PART 1 — Deterministic Identity Tests
# ---------------------------------------------------------------------------


class TestDeterministicIdentities:
    """Verify SES_<HEX16>, SESFP_<HEX64>, and EVT_<HEX16> identity formats."""

    def test_session_fingerprint_format(self):
        """SESFP_ prefix + 64 hex chars = 70 total chars."""
        fp = compute_session_fingerprint(
            source_schedule_id="SCH_1111222233334444",
            executed_task_ids=["STK_AAAA1111BBBB2222"],
            version="1.0.0",
        )
        assert fp.startswith("SESFP_")
        assert len(fp) == 70  # SESFP_ (6) + 64 hex chars

    def test_session_id_format(self):
        """SES_ prefix + 16 hex chars = 20 total chars."""
        fp = compute_session_fingerprint(
            source_schedule_id="SCH_1111222233334444",
            executed_task_ids=["STK_AAAA1111BBBB2222"],
        )
        ses_id, canon_hash = compute_session_id(fp, "1.0.0")
        assert ses_id.startswith("SES_")
        assert len(ses_id) == 20
        assert len(canon_hash) == 64

    def test_event_id_format(self):
        """EVT_ prefix + 16 hex chars = 20 total chars."""
        evt_id, evt_hash = compute_event_id(
            session_id="SES_1111222233334444",
            scheduled_task_id="STK_AAAA1111BBBB2222",
            event_type="task_created_to_queued",
            event_timestamp="2026-07-30T00:00:00Z",
        )
        assert evt_id.startswith("EVT_")
        assert len(evt_id) == 20
        assert len(evt_hash) == 64

    def test_identity_determinism(self):
        """Same inputs always produce same identities."""
        fp1 = compute_session_fingerprint("SCH_ABC", ["STK_123"], "1.0.0")
        fp2 = compute_session_fingerprint("SCH_ABC", ["STK_123"], "1.0.0")
        assert fp1 == fp2

        id1, h1 = compute_session_id(fp1, "1.0.0")
        id2, h2 = compute_session_id(fp2, "1.0.0")
        assert id1 == id2
        assert h1 == h2

    def test_different_inputs_produce_different_identities(self):
        """Different inputs produce different identities."""
        fp1 = compute_session_fingerprint("SCH_A", ["STK_1"])
        fp2 = compute_session_fingerprint("SCH_B", ["STK_2"])
        assert fp1 != fp2

    def test_event_id_determinism(self):
        e1, h1 = compute_event_id("SES_A", "STK_1", "type_a", "2026-07-30T00:00:00Z")
        e2, h2 = compute_event_id("SES_A", "STK_1", "type_a", "2026-07-30T00:00:00Z")
        assert e1 == e2
        assert h1 == h2


# ---------------------------------------------------------------------------
# PART 3 — Execution State Tests
# ---------------------------------------------------------------------------


class TestExecutionStates:
    """Verify ExecutionState enum values and transitions."""

    def test_all_required_states_exist(self):
        assert ExecutionState.CREATED == "created"
        assert ExecutionState.QUEUED == "queued"
        assert ExecutionState.READY == "ready"
        assert ExecutionState.STARTED == "started"
        assert ExecutionState.RUNNING == "running"
        assert ExecutionState.PAUSED == "paused"
        assert ExecutionState.COMPLETED == "completed"
        assert ExecutionState.FAILED == "failed"
        assert ExecutionState.CANCELLED == "cancelled"

    def test_state_count(self):
        assert len(ExecutionState) == 9

    def test_valid_state_transitions(self):
        """CREATED -> QUEUED -> READY -> STARTED -> RUNNING -> COMPLETED is a valid path."""
        ScientificResearchExecutionEngine.validate_state_transition(
            ExecutionState.CREATED, ExecutionState.QUEUED,
        )
        ScientificResearchExecutionEngine.validate_state_transition(
            ExecutionState.QUEUED, ExecutionState.READY,
        )
        ScientificResearchExecutionEngine.validate_state_transition(
            ExecutionState.READY, ExecutionState.STARTED,
        )
        ScientificResearchExecutionEngine.validate_state_transition(
            ExecutionState.STARTED, ExecutionState.RUNNING,
        )
        ScientificResearchExecutionEngine.validate_state_transition(
            ExecutionState.RUNNING, ExecutionState.COMPLETED,
        )

    def test_invalid_state_transition_rejected(self):
        """CREATED -> COMPLETED is not a valid transition."""
        with pytest.raises(ScientificExecutionValidationError, match="Invalid execution state transition"):
            ScientificResearchExecutionEngine.validate_state_transition(
                ExecutionState.CREATED, ExecutionState.COMPLETED,
            )

    def test_terminal_states_have_no_transitions(self):
        """COMPLETED and CANCELLED are terminal."""
        assert VALID_EXECUTION_TRANSITIONS[ExecutionState.COMPLETED] == []
        assert VALID_EXECUTION_TRANSITIONS[ExecutionState.CANCELLED] == []

    def test_completed_to_anything_rejected(self):
        with pytest.raises(ScientificExecutionValidationError):
            ScientificResearchExecutionEngine.validate_state_transition(
                ExecutionState.COMPLETED, ExecutionState.RUNNING,
            )

    def test_pause_and_resume(self):
        """RUNNING -> PAUSED -> RUNNING is valid."""
        ScientificResearchExecutionEngine.validate_state_transition(
            ExecutionState.RUNNING, ExecutionState.PAUSED,
        )
        ScientificResearchExecutionEngine.validate_state_transition(
            ExecutionState.PAUSED, ExecutionState.RUNNING,
        )


# ---------------------------------------------------------------------------
# PART 2 — Immutable Model Tests
# ---------------------------------------------------------------------------


class TestImmutableModels:
    """Verify models are frozen (immutable)."""

    def test_session_is_frozen(self, session_with_engine):
        _, session, _, _ = session_with_engine
        with pytest.raises((ValidationError, TypeError)):
            session.session_id = "MUTATED"

    def test_event_is_frozen(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        event = engine.transition_task(
            session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED,
        )
        with pytest.raises((ValidationError, TypeError)):
            event.event_id = "MUTATED"

    def test_context_is_frozen(self):
        ctx = ScientificExecutionContext(
            session_ids=["SES_1111222233334444"],
            schedule_ids=["SCH_AAAA1111BBBB2222"],
        )
        with pytest.raises((ValidationError, TypeError)):
            ctx.session_ids = ["MUTATED"]

    def test_report_is_frozen(self, session_with_engine):
        engine, session, _, _ = session_with_engine
        events = engine.get_events_for_session(session.session_id)
        report = generate_execution_report(session, events)
        with pytest.raises((ValidationError, TypeError)):
            report.report_id = "MUTATED"


# ---------------------------------------------------------------------------
# PART 4 — Execution Engine & Lifecycle Tests
# ---------------------------------------------------------------------------


class TestExecutionLifecycle:
    """Verify session creation, task transitions, and session lifecycle."""

    def test_create_session(self, session_with_engine):
        _, session, schedule, tasks = session_with_engine
        assert session.session_id.startswith("SES_")
        assert session.source_schedule_id == schedule.schedule_id
        assert len(session.executed_task_ids) == 6
        assert session.session_status == ExecutionState.CREATED

    def test_task_initial_state(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        for task in tasks:
            state = engine.get_task_state(task.task_schedule_id)
            assert state == ExecutionState.CREATED

    def test_task_transition_generates_event(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        event = engine.transition_task(
            session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED,
        )
        assert isinstance(event, ExecutionEvent)
        assert event.event_id.startswith("EVT_")
        assert event.previous_state == ExecutionState.CREATED
        assert event.current_state == ExecutionState.QUEUED

    def test_full_task_lifecycle(self, session_with_engine):
        """CREATED -> QUEUED -> READY -> STARTED -> RUNNING -> COMPLETED."""
        engine, session, _, tasks = session_with_engine
        task_id = tasks[0].task_schedule_id
        sid = session.session_id

        e1 = engine.transition_task(sid, task_id, ExecutionState.QUEUED)
        assert e1.current_state == ExecutionState.QUEUED

        e2 = engine.transition_task(sid, task_id, ExecutionState.READY)
        assert e2.current_state == ExecutionState.READY

        e3 = engine.transition_task(sid, task_id, ExecutionState.STARTED)
        assert e3.current_state == ExecutionState.STARTED

        e4 = engine.transition_task(sid, task_id, ExecutionState.RUNNING)
        assert e4.current_state == ExecutionState.RUNNING

        e5 = engine.transition_task(sid, task_id, ExecutionState.COMPLETED)
        assert e5.current_state == ExecutionState.COMPLETED

        assert engine.get_task_state(task_id) == ExecutionState.COMPLETED

    def test_session_start_and_complete(self, session_with_engine):
        engine, session, _, _ = session_with_engine

        started = engine.start_session(session.session_id)
        assert started.session_status == ExecutionState.RUNNING
        assert started.start_timestamp != ""

        completed = engine.complete_session(session.session_id)
        assert completed.session_status == ExecutionState.COMPLETED
        assert completed.end_timestamp != ""

    def test_session_start_and_fail(self, session_with_engine):
        engine, session, _, _ = session_with_engine

        started = engine.start_session(session.session_id)
        assert started.session_status == ExecutionState.RUNNING

        failed = engine.fail_session(session.session_id)
        assert failed.session_status == ExecutionState.FAILED
        assert failed.end_timestamp != ""

    def test_cannot_start_already_running_session(self, session_with_engine):
        engine, session, _, _ = session_with_engine
        engine.start_session(session.session_id)
        with pytest.raises(ScientificExecutionValidationError, match="expected 'created'"):
            engine.start_session(session.session_id)

    def test_cannot_complete_unstarted_session(self, session_with_engine):
        engine, session, _, _ = session_with_engine
        with pytest.raises(ScientificExecutionValidationError, match="expected 'running'"):
            engine.complete_session(session.session_id)

    def test_empty_tasks_rejected(self, execution_engine, schedule_with_tasks):
        schedule, _ = schedule_with_tasks
        with pytest.raises(ScientificExecutionValidationError, match="no tasks"):
            execution_engine.create_session(schedule, [])

    def test_orphan_task_rejected(self, execution_engine, schedule_with_tasks):
        schedule, tasks = schedule_with_tasks
        # Create a task with wrong parent schedule
        from goat.scheduling.task import ScheduledTask, compute_scheduled_task_id
        stk_id, stk_hash = compute_scheduled_task_id("SCH_WRONGSCHEDULE00", "PTK_1111222233334444", 1)
        bad_task = ScheduledTask(
            task_schedule_id=stk_id,
            parent_schedule_id="SCH_WRONGSCHEDULE00",
            source_plan_task_id="PTK_1111222233334444",
            execution_position=1,
            task_schedule_hash=stk_hash,
        )
        with pytest.raises(ScientificExecutionValidationError, match="parent_schedule_id"):
            execution_engine.create_session(schedule, [bad_task])

    def test_event_metadata_preserved(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        meta = {"reason": "test_transition", "operator": "automated"}
        event = engine.transition_task(
            session.session_id, tasks[0].task_schedule_id,
            ExecutionState.QUEUED, event_metadata=meta,
        )
        assert event.event_metadata == meta


# ---------------------------------------------------------------------------
# PART 5 — Execution History Tests
# ---------------------------------------------------------------------------


class TestExecutionHistory:
    """Verify append-only execution history."""

    def test_history_append_and_count(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED)
        engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.READY)

        assert engine.history.event_count == 2

    def test_history_chronological_order(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        e1 = engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED)
        e2 = engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.READY)

        all_events = engine.history.get_all_events()
        assert all_events[0].event_id == e1.event_id
        assert all_events[1].event_id == e2.event_id

    def test_history_event_lookup(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        e1 = engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED)
        found = engine.history.get_event(e1.event_id)
        assert found.event_id == e1.event_id

    def test_history_task_events(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        tid = tasks[0].task_schedule_id
        engine.transition_task(session.session_id, tid, ExecutionState.QUEUED)
        engine.transition_task(session.session_id, tid, ExecutionState.READY)

        task_events = engine.history.get_events_for_task(tid)
        assert len(task_events) == 2

    def test_history_session_events(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED)
        engine.transition_task(session.session_id, tasks[1].task_schedule_id, ExecutionState.QUEUED)

        session_events = engine.history.get_events_for_session(session.session_id)
        assert len(session_events) == 2

    def test_history_integrity_verification(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED)
        engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.READY)

        assert engine.verify_history_integrity() is True

    def test_history_chain_hash_changes(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        h0 = engine.history.get_chain_hash()
        engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED)
        h1 = engine.history.get_chain_hash()
        assert h0 != h1

    def test_history_replay(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED)
        engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.READY)

        replayed = engine.history.replay()
        assert len(replayed) == 2

    def test_duplicate_event_rejected(self):
        """ExecutionHistory rejects duplicate event IDs."""
        history = ExecutionHistory()
        evt_id, evt_hash = compute_event_id("SES_A", "STK_1", "test", "2026-07-30T00:00:00Z")
        event = ExecutionEvent(
            event_id=evt_id,
            parent_session_id="SES_1111222233334444",
            scheduled_task_id="STK_AAAA1111BBBB2222",
            event_type="test",
            event_timestamp="2026-07-30T00:00:00Z",
            previous_state=ExecutionState.CREATED,
            current_state=ExecutionState.QUEUED,
            event_hash=evt_hash,
        )
        history.append(event)
        with pytest.raises(ValueError, match="Duplicate Event ID"):
            history.append(event)


# ---------------------------------------------------------------------------
# PART 6 — Replay & Determinism Tests
# ---------------------------------------------------------------------------


class TestReplayDeterminism:
    """Verify deterministic replay produces identical results."""

    def test_replay_returns_session_and_events(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED)

        replayed_session, replayed_events = engine.replay_session(session.session_id)
        assert replayed_session.session_id == session.session_id
        assert len(replayed_events) == 1

    def test_bitwise_reproducibility(self, schedule_with_tasks):
        """Two independent engine instances produce identical sessions for same schedule."""
        schedule, tasks = schedule_with_tasks

        eng1 = ScientificResearchExecutionEngine()
        eng2 = ScientificResearchExecutionEngine()

        s1 = eng1.create_session(schedule, tasks)
        s2 = eng2.create_session(schedule, tasks)

        assert s1.scientific_fingerprint == s2.scientific_fingerprint
        assert s1.canonical_hash == s2.canonical_hash
        assert s1.executed_task_ids == s2.executed_task_ids

    def test_session_integrity_verification(self, session_with_engine):
        engine, session, _, _ = session_with_engine
        assert engine.verify_session_integrity(session) is True


# ---------------------------------------------------------------------------
# PART 7 — Reporting Tests
# ---------------------------------------------------------------------------


class TestReporting:
    """Verify ScientificExecutionReport generation."""

    def test_report_generation(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED)
        events = engine.get_events_for_session(session.session_id)

        report = generate_execution_report(session, events)
        assert isinstance(report, ScientificExecutionReport)
        assert report.report_id.startswith("EREP_")
        assert report.session_id == session.session_id

    def test_report_determinism(self, session_with_engine):
        engine, session, _, _ = session_with_engine
        events = engine.get_events_for_session(session.session_id)

        r1 = generate_execution_report(session, events, timestamp="2026-07-30T00:00:00Z")
        r2 = generate_execution_report(session, events, timestamp="2026-07-30T00:00:00Z")
        assert r1.report_id == r2.report_id

    def test_report_task_categorization(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        tid = tasks[0].task_schedule_id
        sid = session.session_id

        # Complete one task
        engine.transition_task(sid, tid, ExecutionState.QUEUED)
        engine.transition_task(sid, tid, ExecutionState.READY)
        engine.transition_task(sid, tid, ExecutionState.STARTED)
        engine.transition_task(sid, tid, ExecutionState.RUNNING)
        engine.transition_task(sid, tid, ExecutionState.COMPLETED)

        events = engine.get_events_for_session(sid)
        report = generate_execution_report(session, events)
        assert tid in report.completed_tasks

    def test_report_failed_tasks(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        tid = tasks[0].task_schedule_id
        sid = session.session_id

        engine.transition_task(sid, tid, ExecutionState.QUEUED)
        engine.transition_task(sid, tid, ExecutionState.READY)
        engine.transition_task(sid, tid, ExecutionState.STARTED)
        engine.transition_task(sid, tid, ExecutionState.FAILED)

        events = engine.get_events_for_session(sid)
        report = generate_execution_report(session, events)
        assert tid in report.failed_tasks

    def test_report_event_statistics(self, session_with_engine):
        engine, session, _, tasks = session_with_engine
        engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED)
        engine.transition_task(session.session_id, tasks[1].task_schedule_id, ExecutionState.QUEUED)

        events = engine.get_events_for_session(session.session_id)
        report = generate_execution_report(session, events)
        assert report.event_statistics["total_events"] == 2


# ---------------------------------------------------------------------------
# PART 8 — SQLite Persistence Tests
# ---------------------------------------------------------------------------


class TestSQLitePersistence:
    """Verify persistence roundtrip for all domain objects."""

    def test_session_roundtrip(self, session_with_engine, temp_db):
        repo, _ = temp_db
        _, session, _, _ = session_with_engine

        repo.save_session(session)
        loaded = repo.get_session(session.session_id)

        assert loaded is not None
        assert loaded.session_id == session.session_id
        assert loaded.canonical_hash == session.canonical_hash
        assert loaded.scientific_fingerprint == session.scientific_fingerprint
        assert loaded.executed_task_ids == session.executed_task_ids

    def test_event_roundtrip(self, session_with_engine, temp_db):
        repo, _ = temp_db
        engine, session, _, tasks = session_with_engine

        repo.save_session(session)
        event = engine.transition_task(
            session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED,
        )
        repo.save_event(event)

        loaded = repo.get_event(event.event_id)
        assert loaded is not None
        assert loaded.event_id == event.event_id
        assert loaded.current_state == ExecutionState.QUEUED

    def test_events_for_session(self, session_with_engine, temp_db):
        repo, _ = temp_db
        engine, session, _, tasks = session_with_engine

        repo.save_session(session)
        e1 = engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED)
        e2 = engine.transition_task(session.session_id, tasks[1].task_schedule_id, ExecutionState.QUEUED)
        repo.save_event(e1)
        repo.save_event(e2)

        loaded = repo.get_events_for_session(session.session_id)
        assert len(loaded) == 2

    def test_events_for_task(self, session_with_engine, temp_db):
        repo, _ = temp_db
        engine, session, _, tasks = session_with_engine
        tid = tasks[0].task_schedule_id

        repo.save_session(session)
        e1 = engine.transition_task(session.session_id, tid, ExecutionState.QUEUED)
        e2 = engine.transition_task(session.session_id, tid, ExecutionState.READY)
        repo.save_event(e1)
        repo.save_event(e2)

        loaded = repo.get_events_for_task(tid)
        assert len(loaded) == 2

    def test_context_roundtrip(self, session_with_engine, temp_db):
        repo, _ = temp_db
        _, session, schedule, _ = session_with_engine

        repo.save_session(session)
        ctx = ScientificExecutionContext(
            session_ids=[session.session_id],
            schedule_ids=[schedule.schedule_id],
            priority_ids=["RPR_AAAA1111BBBB2222"],
        )
        repo.save_context(session.session_id, ctx)
        loaded = repo.get_context(session.session_id)

        assert loaded is not None
        assert loaded.session_ids == [session.session_id]

    def test_report_roundtrip(self, session_with_engine, temp_db):
        repo, _ = temp_db
        engine, session, _, _ = session_with_engine

        repo.save_session(session)
        events = engine.get_events_for_session(session.session_id)
        report = generate_execution_report(session, events)
        repo.save_report(report)

        loaded = repo.get_report(report.report_id)
        assert loaded is not None
        assert loaded.report_id == report.report_id

    def test_audit_events(self, session_with_engine, temp_db):
        repo, _ = temp_db
        _, session, _, _ = session_with_engine

        repo.save_session(session)
        repo.save_audit_event(
            session.session_id,
            "session_created",
            "2026-07-30T00:00:00Z",
            {"source": "test"},
        )

        events = repo.get_audit_events(session.session_id)
        assert len(events) == 1
        assert events[0]["event_type"] == "session_created"

    def test_export_import_roundtrip(self, session_with_engine, temp_db):
        repo, _ = temp_db
        engine, session, _, tasks = session_with_engine

        repo.save_session(session)
        e1 = engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED)
        repo.save_event(e1)

        exported = repo.export_session(session.session_id)
        assert exported["schema_version"] == EXECUTION_SCHEMA_VERSION

        tmp2 = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        db2_path = tmp2.name
        tmp2.close()
        repo2 = SQLiteExecutionRepository(db2_path)

        imported = repo2.import_session(exported)
        assert imported.session_id == session.session_id
        assert imported.canonical_hash == session.canonical_hash

        repo2.close()
        os.remove(db2_path)

    def test_integrity_verification(self, session_with_engine, temp_db):
        repo, _ = temp_db
        engine, session, _, tasks = session_with_engine

        repo.save_session(session)
        e1 = engine.transition_task(session.session_id, tasks[0].task_schedule_id, ExecutionState.QUEUED)
        repo.save_event(e1)

        assert repo.verify_integrity(session.session_id) is True

    def test_list_sessions(self, session_with_engine, temp_db):
        repo, _ = temp_db
        _, session, _, _ = session_with_engine

        repo.save_session(session)
        all_sessions = repo.list_sessions()
        assert len(all_sessions) == 1
        assert all_sessions[0].session_id == session.session_id

    def test_schema_version(self, temp_db):
        repo, _ = temp_db
        assert EXECUTION_SCHEMA_VERSION == 1


# ---------------------------------------------------------------------------
# PART 9 — Validation Tests
# ---------------------------------------------------------------------------


class TestValidation:
    """Verify fail-closed validation rules."""

    def test_duplicate_session_id_rejected(self, schedule_with_tasks, execution_engine):
        schedule, tasks = schedule_with_tasks
        execution_engine.create_session(schedule, tasks)
        with pytest.raises(ScientificExecutionValidationError, match="Duplicate"):
            execution_engine.create_session(schedule, tasks)

    def test_invalid_state_transition_rejected(self):
        with pytest.raises(ScientificExecutionValidationError):
            ScientificResearchExecutionEngine.validate_state_transition(
                ExecutionState.COMPLETED, ExecutionState.RUNNING,
            )

    def test_cancelled_to_anything_rejected(self):
        for state in ExecutionState:
            if state != ExecutionState.CANCELLED:
                with pytest.raises(ScientificExecutionValidationError):
                    ScientificResearchExecutionEngine.validate_state_transition(
                        ExecutionState.CANCELLED, state,
                    )

    def test_session_id_format_validation(self):
        """ScientificExecutionSession rejects invalid session_id format."""
        with pytest.raises(ValidationError):
            ScientificExecutionSession(
                session_id="INVALID",
                canonical_hash="a" * 64,
                scientific_fingerprint="SESFP_" + "a" * 64,
                creation_timestamp="2026-07-30T00:00:00Z",
                source_schedule_id="SCH_1111222233334444",
            )

    def test_event_id_format_validation(self):
        """ExecutionEvent rejects invalid event_id format."""
        with pytest.raises(ValidationError):
            ExecutionEvent(
                event_id="INVALID",
                parent_session_id="SES_1111222233334444",
                scheduled_task_id="STK_AAAA1111BBBB2222",
                event_type="test",
                event_timestamp="2026-07-30T00:00:00Z",
                previous_state=ExecutionState.CREATED,
                current_state=ExecutionState.QUEUED,
                event_hash="a" * 64,
            )

    def test_context_extra_fields_rejected(self):
        with pytest.raises(ValidationError):
            ScientificExecutionContext(
                session_ids=["SES_1111222233334444"],
                unknown_field="should_fail",
            )

    def test_import_schema_version_mismatch_rejected(self, temp_db):
        repo, _ = temp_db
        with pytest.raises(ValueError, match="Schema version mismatch"):
            repo.import_session({"schema_version": 999})

    def test_unregistered_task_transition_rejected(self, session_with_engine):
        engine, session, _, _ = session_with_engine
        with pytest.raises(ScientificExecutionValidationError, match="not registered"):
            engine.transition_task(
                session.session_id, "STK_NONEXISTENT00000", ExecutionState.QUEUED,
            )


# ---------------------------------------------------------------------------
# PART 10 — Public API Smoke Tests
# ---------------------------------------------------------------------------


class TestPublicAPI:
    """Verify all required public API symbols are importable and usable."""

    def test_all_public_symbols_importable(self):
        from goat.execution import (
            ScientificExecutionSession,
            ExecutionEvent,
            ExecutionState,
            ExecutionHistory,
            ScientificResearchExecutionEngine,
            ScientificExecutionContext,
            ScientificExecutionReport,
            ScientificExecutionValidationError,
        )
        assert ScientificExecutionSession is not None
        assert ExecutionEvent is not None
        assert ExecutionState is not None
        assert ExecutionHistory is not None
        assert ScientificResearchExecutionEngine is not None
        assert ScientificExecutionContext is not None
        assert ScientificExecutionReport is not None
        assert ScientificExecutionValidationError is not None

    def test_engine_instantiation(self):
        engine = ScientificResearchExecutionEngine()
        assert engine is not None

    def test_history_instantiation(self):
        history = ExecutionHistory()
        assert history is not None
        assert history.event_count == 0

    def test_repository_instantiation(self):
        repo = SQLiteExecutionRepository(":memory:")
        assert repo is not None
        repo.close()


# ---------------------------------------------------------------------------
# PART 11 — Regression & Edge Case Tests
# ---------------------------------------------------------------------------


class TestRegressionEdgeCases:
    """Additional edge cases and regression tests."""

    def test_get_nonexistent_session_raises(self, execution_engine):
        with pytest.raises(KeyError):
            execution_engine.get_session("SES_NONEXISTENT00000")

    def test_get_nonexistent_task_state_raises(self, execution_engine):
        with pytest.raises(KeyError):
            execution_engine.get_task_state("STK_NONEXISTENT00000")

    def test_export_nonexistent_session_raises(self, temp_db):
        repo, _ = temp_db
        with pytest.raises(KeyError):
            repo.export_session("SES_NONEXISTENT00000")

    def test_integrity_verification_nonexistent_raises(self, temp_db):
        repo, _ = temp_db
        with pytest.raises(ValueError):
            repo.verify_integrity("SES_NONEXISTENT00000")

    def test_multi_task_execution_workflow(self, session_with_engine):
        """Execute multiple tasks in a session concurrently."""
        engine, session, _, tasks = session_with_engine
        sid = session.session_id

        # Queue first 3 tasks
        for task in tasks[:3]:
            engine.transition_task(sid, task.task_schedule_id, ExecutionState.QUEUED)

        # Verify all are queued
        for task in tasks[:3]:
            assert engine.get_task_state(task.task_schedule_id) == ExecutionState.QUEUED

        # Remaining tasks still CREATED
        for task in tasks[3:]:
            assert engine.get_task_state(task.task_schedule_id) == ExecutionState.CREATED

    def test_full_workflow_integration(self):
        """End-to-end: planning -> scheduling -> execution -> reporting -> persistence."""
        from goat.planning import ScientificPlanningEngine
        from goat.scheduling import ScientificResearchScheduler

        # Planning
        planner = ScientificPlanningEngine()
        plan, graph = planner.create_plan(
            research_objective="Full integration test for execution engine",
            source_priority_ids=["RPR_INTG1111INTG2222"],
        )

        # Scheduling
        scheduler = ScientificResearchScheduler()
        schedule, sched_tasks = scheduler.create_schedule(plan, graph)

        # Execution
        exec_engine = ScientificResearchExecutionEngine()
        session = exec_engine.create_session(schedule, sched_tasks)
        started = exec_engine.start_session(session.session_id)

        # Execute first task through full lifecycle
        tid = sched_tasks[0].task_schedule_id
        exec_engine.transition_task(session.session_id, tid, ExecutionState.QUEUED)
        exec_engine.transition_task(session.session_id, tid, ExecutionState.READY)
        exec_engine.transition_task(session.session_id, tid, ExecutionState.STARTED)
        exec_engine.transition_task(session.session_id, tid, ExecutionState.RUNNING)
        exec_engine.transition_task(session.session_id, tid, ExecutionState.COMPLETED)

        # Reporting
        events = exec_engine.get_events_for_session(session.session_id)
        report = generate_execution_report(
            exec_engine.get_session(session.session_id), events,
        )

        # Persistence
        repo = SQLiteExecutionRepository(":memory:")
        final_session = exec_engine.get_session(session.session_id)
        repo.save_session(final_session)
        for event in events:
            repo.save_event(event)
        repo.save_report(report)

        # Verify
        loaded = repo.get_session(session.session_id)
        assert loaded.session_id == session.session_id
        assert repo.verify_integrity(session.session_id)

        # Replay
        replayed_session, replayed_events = exec_engine.replay_session(session.session_id)
        assert replayed_events == events

        # History integrity
        assert exec_engine.verify_history_integrity()

        repo.close()
