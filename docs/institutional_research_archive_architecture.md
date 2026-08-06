# Project GOAT v0.8 — Institutional Research Archive Vault Architecture

## 1. Subsystem Purpose & Archive Philosophy

The **Institutional Research Archive Vault** (`goat.archive`) forms the permanent institutional memory of Project GOAT. It preserves every scientific decision, production event, execution log, market tick observation, broker interaction, portfolio update, notification message, trade lifecycle transition, telemetry record, heartbeat pulse, and diagnostic finding across all previous subsystems.

### Core Philosophy & Absolute Constraints
1. **Append-Only Memory**: Nothing is ever deleted, mutated, overwritten, or merged.
2. **Deterministic Replay**: Reconstructs exact historical event streams in original chronological order.
3. **Cryptographic Tamper Evidence**: Every record carries a 16-character SHA-256 canonical hash digest.
4. **Passive Observation Only**: The archive **MUST NEVER** generate trading signals, modify signals/executions/broker responses/portfolio states, or execute trades.

```
Step 4.x Scientific Research    ──┐
Step 5.x Knowledge Engine       ──┤
Step 6.x Scientific Intelligence─┤
Step 7.0 Live Market Data       ──┼──► Archive Vault (Step 7.9) ──► Append-Only Log ──► Replay & Audit
Step 7.1 Market State           ──┤
Step 7.2-7.8 Production Modules ──┘
```

---

## 2. Package Architecture

```
goat/archive/
├── __init__.py                # Top-level public API exports (__all__)
├── engine.py                  # Master ArchiveEngine coordinator
├── core/                      # Enums, SHA-256 ID generators, Pydantic V2 models
│   ├── __init__.py
│   ├── canonical.py
│   ├── enums.py
│   └── models.py
├── ingestion/                 # ArchiveIngestionEngine (Validation & append-only record ingestion)
│   ├── __init__.py
│   └── engine.py
├── indexing/                  # ArchiveIndexEngine (Replay-safe multi-attribute secondary indexing)
│   ├── __init__.py
│   └── engine.py
├── replay/                    # ReplayEngine (Exact chronological sequence reconstruction)
│   ├── __init__.py
│   └── engine.py
├── snapshots/                 # SnapshotEngine (SHA-256 integrity-verified state manifests)
│   ├── __init__.py
│   └── engine.py
├── retention/                 # RetentionEngine (APPEND_ONLY rules & integrity auditing)
│   ├── __init__.py
│   └── engine.py
├── persistence/               # SQLite WAL repositories
│   ├── __init__.py
│   └── repository.py
└── reporting/                 # Markdown & Canonical JSON reporting engine
    ├── __init__.py
    └── reports.py
```

---

## 3. Deterministic SHA-256 Identifiers

All archived entities implement canonical SHA-256 digests across payload attributes to produce 16-character hexadecimal IDs:

| Prefix | Entity | Example ID |
|---|---|---|
| `ARC_` | `ArchiveRecord` | `ARC_1A2B3C4D5E6F7890` |
| `ABT_` | `ArchiveBatch` | `ABT_2B3C4D5E6F7890A1` |
| `RRQ_` | `ReplayRequest` | `RRQ_3C4D5E6F7890A1B2` |
| `RPS_` | `ReplaySession` | `RPS_4D5E6F7890A1B2C3` |
| `RCP_` | `ReplayCheckpoint` | `RCP_5E6F7890A1B2C3D4` |
| `SNP_` | `SnapshotManifest` | `SNP_6F7890A1B2C3D4E5` |
| `AST_` | `ArchiveStatistics` | `AST_7890A1B2C3D4E5F6` |
| `ASM_` | `ArchiveSummary` | `ASM_890A1B2C3D4E5F67` |

---

## 4. Ingestion Pipeline & Append-Only Rules

`ArchiveIngestionEngine` ingests records from all 11 subsystem categories:
- Validates schema structure, origin subsystem, timestamp ordering, and canonical hashes.
- Stores records in an append-only store (`ArchiveRecord`).
- Enforces strict immutable contracts (`ConfigDict(frozen=True, extra="forbid")`).
- Groups records into unalterable `ArchiveBatch` manifests.

---

## 5. Secondary Indexing

`ArchiveIndexEngine` builds replay-safe secondary index structures across:
`time`, `subsystem`, `entity_type`, `entity_id`, `signal_id`, `execution_id`, `portfolio_id`, `broker_id`, `instrument`, `market_regime`, `session`, and `date`.

---

## 6. Deterministic Replay Engine

`ReplayEngine` reconstructs historical event streams:
- Filters by time range, subsystem, entity type, instrument, and session.
- Sorts records strictly by timestamp and canonical `archive_id`.
- Reconstructs exact original sequence with zero synthetic events or inferred data.
- Generates `ReplaySession` (`RPS_<HEX16>`) and sequence `ReplayCheckpoint` (`RCP_<HEX16>`) logs.

---

## 7. State Snapshots & Retention

`SnapshotEngine` captures state snapshot manifests (`SNP_<HEX16>`) for:
- `PORTFOLIO`, `MARKET_STATE`, `BROKER_ACCOUNT`, `SYSTEM_HEALTH`, `EXECUTION_STATE`, `ARCHIVE_STATISTICS`.

`RetentionEngine` enforces `APPEND_ONLY` policy and conducts cryptographic tamper audits on demand.

---

## 8. Persistence & Reporting

All records are persisted to transactional SQLite WAL databases (`PRAGMA foreign_keys = ON;`, `PRAGMA journal_mode = WAL;`, `ON CONFLICT DO UPDATE`). `ArchiveReportEngine` outputs structured Markdown and Canonical JSON reports.
