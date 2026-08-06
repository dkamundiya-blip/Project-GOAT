# Scientific Research Scheduler — Architecture Documentation

## Overview

The Scientific Research Scheduler (Step 5.5) implements a deterministic scheduling layer
that coordinates executable scientific work while respecting dependency graphs, execution
state, resource constraints, and reproducibility requirements.

**The scheduler SHALL coordinate execution. It SHALL NOT perform scientific reasoning.**

## Architectural Position

```
Research Prioritization (Step 5.3)
        ↓
Scientific Planning (Step 5.4)
        ↓
Scientific Research Scheduler (Step 5.5)    ← THIS MODULE
        ↓
Research Orchestration (Future)
        ↓
Scientific Experiment Engine (Future)
```

The scheduler consumes immutable Scientific Plans produced by the planning engine and
generates immutable execution schedules that downstream orchestration layers can execute.

## Core Principles

### 1. Determinism
Every scheduling operation is deterministic. Given the same inputs, the scheduler
always produces the same outputs. This is enforced through:
- Canonical JSON serialization with sorted keys
- SHA-256 content-addressed identity computation
- Deterministic topological sorting with tiebreaking by execution order then task ID
- Sorted merging in multi-plan coordination

### 2. Immutability
All domain models are frozen Pydantic models. State changes create new schedule
snapshots rather than mutating existing ones. This preserves the complete audit trail
and enables temporal queries over schedule evolution.

### 3. Reproducibility
Schedules can be replayed by retracing the execution order. The deterministic
identity system ensures bitwise-identical schedules when given identical plan inputs.

### 4. Separation of Concerns
The scheduler:
- ✅ Generates execution queues from plan DAGs
- ✅ Validates dependency satisfaction
- ✅ Detects state transition violations
- ✅ Coordinates multiple plans
- ✅ Persists schedule state
- ❌ Does NOT execute experiments
- ❌ Does NOT generate hypotheses
- ❌ Does NOT perform ML or optimization
- ❌ Does NOT modify plans or priorities

## Domain Models

### ResearchSchedule (`SCH_<HEX16>`)
Top-level schedule containing:
- Deterministic identity (`schedule_id`, `canonical_hash`, `scientific_fingerprint`)
- Source plan references
- Ordered task IDs
- Execution order
- Schedule-level status

### ScheduledTask (`STK_<HEX16>`)
Individual executable unit within a schedule:
- Deterministic identity derived from schedule + plan task + position
- Parent schedule reference
- Source plan task reference
- Execution position
- Dependency satisfaction status
- Planned start/finish sequence ticks

### ScheduleExecutionState
Eight deterministic states with validated transitions:

```
PENDING → READY → RUNNING → COMPLETED (terminal)
                         ↘ FAILED → CANCELLED (terminal)
                         ↘ BLOCKED → READY
                                   ↘ WAITING → READY
```

All transitions are explicitly enumerated. Invalid transitions raise
`ScientificSchedulingValidationError`.

### ScientificSchedulingContext
Immutable artifact reference container carrying active IDs across scheduling operations:
schedule IDs, plan IDs, priority IDs, portfolio IDs, program IDs, study IDs,
experiment IDs, registry versions, and configuration IDs.

### ScientificSchedulingReport (`SREP_<HEX16>`)
Deterministic reporting artifact containing:
- Schedule metadata
- Execution queue
- Dependency statistics
- Task state breakdown (blocked, completed, waiting)
- Execution readiness percentage
- Audit summary

## Execution Ordering

### Topological Sort
The scheduler consumes the planning DAG's topological order to produce execution order.
Tasks are scheduled in dependency-respecting sequence with deterministic tiebreaking:
1. By execution order (lower first)
2. By task ID (lexicographic, for stability)

### Multi-Plan Coordination
When merging multiple schedules:
1. Schedules are sorted deterministically by `schedule_id`
2. Tasks within each schedule preserve their original execution order
3. A global position counter prevents execution position conflicts
4. The merged schedule receives a new deterministic identity

## Dependency Enforcement

- Root tasks (no dependencies) have `dependency_satisfaction = True`
- Dependent tasks start with `dependency_satisfaction = False`
- The `get_ready_tasks()` method identifies tasks eligible for execution
- Cyclic dependencies are rejected at the planning DAG level

## Replay

Schedule replay is a first-class operation:
```python
schedule, order = scheduler.replay_schedule(schedule_id)
# order == original execution order (bitwise identical)
```

Replay guarantees:
- Same `schedule_id` → same execution order
- No side effects
- No external state dependencies

## Persistence

### SQLite Schema (v1)
Six tables with foreign key enforcement:

| Table | Purpose |
|-------|---------|
| `research_schedules` | Schedule metadata with unique canonical hash |
| `scheduled_tasks` | Task instances with FK to parent schedule |
| `scheduling_contexts` | Artifact reference contexts |
| `scheduling_reports` | Deterministic scheduling reports |
| `coordinator_state` | Multi-plan merge state |
| `audit_events` | Chronological audit trail |

### Integrity Verification
The repository supports integrity verification ensuring all persisted task IDs
match the schedule's `scheduled_task_ids` list.

### Import/Export
Complete schedule artifacts (schedule + tasks + context + audit events) can be
exported as JSON and imported into fresh databases with schema version validation.

## Validation Rules (Fail-Closed)

The following conditions are rejected with `ScientificSchedulingValidationError`:

1. **Duplicate Schedule IDs** — Schedule ID already registered
2. **Duplicate Hashes** — Canonical hash already exists (via UNIQUE constraint)
3. **Orphan Plan References** — Source plan not provided
4. **Orphan Plan Task References** — Plan task ID not in DAG
5. **Duplicate Execution Positions** — Position already assigned
6. **Dependency Violations** — Task scheduled before its dependencies
7. **Cyclic Scheduling** — Detected via topological sort failure
8. **Invalid State Transitions** — Transition not in VALID_STATE_TRANSITIONS
9. **Hash Mismatches** — Recomputed fingerprint/hash doesn't match stored values
10. **Schema Version Mismatches** — Import with wrong schema version

## Future Integration Points

The Scientific Research Scheduler is designed to integrate with:

- **Research Executor** — Consumes ready tasks and executes them
- **Experiment Runtime** — Manages individual experiment execution contexts
- **Laboratory Runtime** — Provides execution environments and resource allocation
- **Autonomous Scientist** — High-level orchestration agent consuming schedule state
- **Live Execution Coordinator** — Real-time schedule monitoring and adaptation
