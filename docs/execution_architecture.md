# Scientific Research Execution Engine — Architecture Documentation

## Overview

The Scientific Research Execution Engine (Step 5.6) implements a deterministic execution
layer that coordinates the lifecycle of scheduled scientific work, producing immutable
execution sessions and append-only execution events.

**The engine SHALL coordinate execution. It SHALL NOT perform scientific reasoning.**

## Architectural Position

```
Research Prioritization (Step 5.3)
        ↓
Scientific Planning (Step 5.4)
        ↓
Scientific Research Scheduling (Step 5.5)
        ↓
Scientific Research Execution (Step 5.6)    ← THIS MODULE
        ↓
Scientific Experiment Engine (Future)
```

The execution engine consumes immutable Research Schedules produced by the scheduling
engine and coordinates task execution through a deterministic lifecycle, recording
every state transition as an immutable event.

## Core Principles

### 1. Event Sourcing
Every state change is recorded as an immutable `ExecutionEvent`. The complete execution
history can be reconstructed from the event log alone. Events are append-only — they
can never be modified or deleted.

### 2. Determinism
All operations are deterministic:
- Session identity is computed from schedule content via SHA-256
- Event identity is computed from session + task + type + timestamp
- State transitions follow an explicit whitelist
- History chain hashing provides tamper detection

### 3. Immutability
All domain models are frozen Pydantic models. Session status changes produce new
session snapshots rather than mutating existing ones. Events are append-only and
never rewritten.

### 4. Separation of Concerns
The engine:
- ✅ Coordinates task execution lifecycle
- ✅ Records state transitions as events
- ✅ Maintains execution history
- ✅ Supports deterministic replay
- ❌ Does NOT execute actual experiments
- ❌ Does NOT perform scientific computation
- ❌ Does NOT modify schedules, plans, or priorities

## Domain Models

### ScientificExecutionSession (`SES_<HEX16>`)
Top-level execution session containing:
- Deterministic identity (`session_id`, `canonical_hash`, `scientific_fingerprint`)
- Source schedule reference
- Executed task IDs
- Session lifecycle status
- Start/end timestamps
- Audit metadata

### ExecutionEvent (`EVT_<HEX16>`)
Immutable append-only event recording:
- Deterministic identity derived from session + task + type + timestamp
- Parent session reference
- Scheduled task reference
- Event type classification
- Previous and current execution states
- Event-specific metadata

### ExecutionState
Nine deterministic lifecycle states with validated transitions:

```
CREATED → QUEUED → READY → STARTED → RUNNING → COMPLETED (terminal)
                                        ↕
                                      PAUSED
                                        ↓
                              FAILED → CANCELLED (terminal)
```

All transitions are explicitly enumerated in `VALID_EXECUTION_TRANSITIONS`.
Invalid transitions raise `ScientificExecutionValidationError`.

### ExecutionHistory
Append-only chronological event log:
- Events indexed by ID, task, and session
- Rolling chain hash for integrity verification
- Replay support via ordered traversal
- Duplicate event rejection

### ScientificExecutionContext
Immutable artifact reference container: session IDs, schedule IDs, plan IDs,
priority IDs, study IDs, experiment IDs, portfolio IDs, registry versions,
and configuration IDs.

### ScientificExecutionReport (`EREP_<HEX16>`)
Deterministic reporting artifact containing:
- Session metadata
- Executed task list
- Execution timeline (chronological event log)
- Event type statistics
- Execution duration
- Completed/failed task breakdowns
- Replay verification status
- Audit summary

## Execution Lifecycle

### Session Lifecycle
```
create_session() → CREATED
start_session()  → RUNNING (sets start_timestamp)
complete_session() → COMPLETED (sets end_timestamp)
fail_session()   → FAILED (sets end_timestamp)
```

### Task Lifecycle
```
transition_task(CREATED → QUEUED)    → EVT_ event generated
transition_task(QUEUED → READY)      → EVT_ event generated
transition_task(READY → STARTED)     → EVT_ event generated
transition_task(STARTED → RUNNING)   → EVT_ event generated
transition_task(RUNNING → COMPLETED) → EVT_ event generated
```

Every transition produces an immutable `ExecutionEvent` that is appended to the
`ExecutionHistory`.

## Event Sourcing

The execution engine follows an event-sourcing pattern:

1. **Commands** → `transition_task()` requests state changes
2. **Validation** → State transition is validated against the whitelist
3. **Events** → An `ExecutionEvent` is generated with deterministic identity
4. **History** → The event is appended to the `ExecutionHistory`
5. **Chain Hash** → The rolling chain hash is updated for integrity

This means:
- The complete execution state can be reconstructed from events alone
- The history is tamper-evident via chain hashing
- Replay produces identical results

## Replay

Session replay is a first-class operation:
```python
session, events = engine.replay_session(session_id)
# events == original chronological event sequence
```

History replay returns all events:
```python
all_events = engine.history.replay()
```

## Persistence

### SQLite Schema (v1)
Five tables with foreign key enforcement:

| Table | Purpose |
|-------|---------|
| `execution_sessions` | Session metadata with unique canonical hash |
| `execution_events` | Append-only events with FK to parent session |
| `execution_contexts` | Artifact reference contexts |
| `execution_reports` | Deterministic execution reports |
| `execution_audit_events` | Chronological audit trail |

### Integrity Verification
The repository verifies that all persisted events reference the correct session.
The `ExecutionHistory` verifies chain hash integrity.

### Import/Export
Complete session artifacts (session + events + context + audit events) can be
exported as JSON and imported into fresh databases with schema version validation.

## Validation Rules (Fail-Closed)

1. **Duplicate Session IDs** — Session ID already registered
2. **Duplicate Event IDs** — Event ID already in history
3. **Orphan Schedule References** — Tasks reference wrong schedule
4. **Orphan Task References** — Task not registered in engine
5. **Invalid State Transitions** — Transition not in VALID_EXECUTION_TRANSITIONS
6. **Invalid Event Ordering** — Enforced by append-only history
7. **Replay Inconsistencies** — Detected via chain hash verification
8. **Hash Mismatches** — Recomputed hash doesn't match stored values
9. **Schema Version Mismatches** — Import with wrong schema version

## Future Integration Points

The Scientific Research Execution Engine is designed to integrate with:

- **Scientific Experiment Runtime** — Actual experiment execution within sessions
- **Feature Evaluation Runtime** — Feature computation orchestration
- **Edge Validation Runtime** — Multi-stage edge validation execution
- **Autonomous Scientist** — High-level agent consuming execution state
- **Live Trading Runtime** — Production execution monitoring
