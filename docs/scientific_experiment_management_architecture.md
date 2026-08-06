# SCIENTIFIC EXPERIMENT MANAGEMENT ENGINE ARCHITECTURE
## PROJECT GOAT VERSION 0.9 — STEP 9.3 SPECIFICATION

**Document Version**: 1.0.0  
**Authorizing Body**: Institutional Quantitative Research Board  
**Executive Authority**: Chief Scientific Officer  
**Target Subsystem**: `goat.experiments`  
**Effective Date**: 2026-08-04  
**Status**: CERTIFIED & FROZEN  

---

## 1. ARCHITECTURE SUMMARY

The **Scientific Experiment Management Engine** (`goat.experiments`) manages the complete lifecycle of scientific experiments for Project GOAT Version 0.9. It operates as a deterministic, reproducible, auditable research container linking hypotheses (`HYP_`), evidence records (`EVR_`), observation collections (`COL_`), execution manifests (`MAN_`), replay specifications (`RPL_`), and lifecycle audit logs (`LFC_`).

Crucially, the experiment subsystem is purely administrative and structural:
- It **DOES NOT** determine whether a hypothesis is true or false.
- It **DOES NOT** execute trading strategies or backtests.
- It **DOES NOT** generate trading signals.
- It **DOES NOT** compute statistical metrics or confidence scores.
- It **DOES NOT** execute live trades or manage portfolios.

It operates as an immutable container layer governed by SHA-256 canonical digests.

---

## 2. PACKAGE STRUCTURE

```
goat/experiments/
├── __init__.py               # Top-level public API exports with strict __all__
├── engine.py                 # ScientificExperimentEngine master facade
├── core/
│   ├── __init__.py           # Core package exports
│   ├── canonical.py          # Deterministic SHA-256 serialization & ID generation
│   ├── enums.py              # ExperimentStatus, ExperimentType, ExperimentPriority
│   └── models.py             # Immutable Pydantic V2 domain models
├── lifecycle/
│   ├── __init__.py           # Lifecycle package exports
│   └── engine.py             # ScientificExperimentLifecycleEngine
├── scheduling/
│   ├── __init__.py           # Scheduling package exports
│   └── engine.py             # ExperimentSchedulingEngine
├── manifests/
│   ├── __init__.py           # Manifest package exports
│   └── engine.py             # ExperimentManifestEngine
├── replay/
│   ├── __init__.py           # Replay package exports
│   └── engine.py             # ExperimentReplayEngine
├── reporting/
│   ├── __init__.py           # Reporting package exports
│   └── reports.py            # Markdown, JSON, Experiment & Replay report generators
└── persistence/
    ├── __init__.py           # Persistence package exports
    └── sqlite.py             # SQLite WAL repositories & context
```

---

## 3. DOMAIN MODEL INVENTORY

All domain models are implemented as immutable Pydantic V2 models with `frozen=True` and `extra="forbid"`:

1. **`ScientificExperiment`**:
   - Primary research container entity linking hypotheses and evidence.
   - Identifier prefix: `EXP_<HEX16>`.
   - Fields: `hypothesis_id`, `title`, `description`, `experiment_type`, `status`, `priority`, `author`, `evidence_ids`, `manifest_id`, `created_timestamp`, `updated_timestamp`, `tags`, `metadata`, `canonical_hash`.

2. **`ExperimentManifest`**:
   - Immutable specification of execution parameters, dataset hashes, and reproducibility parameters.
   - Identifier prefix: `MAN_<HEX16>`.
   - Fields: `experiment_id`, `hypothesis_id`, `evidence_ids`, `dataset_fingerprint`, `configuration_params`, `software_version`, `author`, `created_timestamp`, `metadata`, `canonical_hash`.

3. **`ExperimentLifecycle`**:
   - Immutable audit trail record of state transition events.
   - Identifier prefix: `LFC_<HEX16>`.
   - Fields: `experiment_id`, `from_status`, `to_status`, `actor`, `reason`, `timestamp`, `metadata`, `canonical_hash`.

4. **`ExperimentReplay`**:
   - Deterministic replay verification specifications.
   - Identifier prefix: `RPL_<HEX16>`.
   - Fields: `experiment_id`, `manifest_id`, `dataset_hash`, `random_seed`, `expected_output_hash`, `is_verified`, `timestamp`, `metadata`, `canonical_hash`.

5. **`ExperimentSchedule`**:
   - Priority queueing metadata tracking execution order without executing runs.
   - Identifier prefix: `SCH_<HEX16>`.
   - Fields: `experiment_id`, `priority`, `scheduled_timestamp`, `queue_position`, `scheduler_id`, `timestamp`, `metadata`, `canonical_hash`.

6. **`ExperimentSummary`**:
   - Aggregate snapshot of subsystem experiment counts and status breakdowns.
   - Identifier prefix: `SUM_<HEX16>`.
   - Fields: `total_experiments`, `status_counts`, `type_counts`, `priority_counts`, `timestamp`, `metadata`, `canonical_hash`.

---

## 4. CANONICAL ID GENERATION & SHA-256 HASHING

All identifiers are computed deterministically using sorted-key canonical JSON serialization and SHA-256 hashing. Identical inputs yield identical IDs:

- **Experiment ID**: `EXP_<HEX16>` derived from `hypothesis_id`, `title`, `experiment_type`, `author`.
- **Manifest ID**: `MAN_<HEX16>` derived from `experiment_id`, `hypothesis_id`, sorted `evidence_ids`.
- **Lifecycle ID**: `LFC_<HEX16>` derived from `experiment_id`, `from_status`, `to_status`, `timestamp`.
- **Replay ID**: `RPL_<HEX16>` derived from `experiment_id`, `manifest_id`, `dataset_hash`, `timestamp`.
- **Schedule ID**: `SCH_<HEX16>` derived from `experiment_id`, `priority`, `scheduled_timestamp`.
- **Summary ID**: `SUM_<HEX16>` derived from `total_experiments`, `timestamp`.

---

## 5. SUB-ENGINE RESPONSIBILITIES

1. **`ScientificExperimentLifecycleEngine`**:
   - Manages state transitions across `PLANNED`, `APPROVED`, `READY`, `RUNNING`, `PAUSED`, `COMPLETED`, `FAILED`, `ARCHIVED`.
   - Rejects illegal state transitions (e.g. `PLANNED` -> `COMPLETED` without running).

2. **`ExperimentSchedulingEngine`**:
   - Registers and queues experiments by priority (`CRITICAL` > `HIGH` > `NORMAL` > `LOW`) and timestamp.
   - MUST NOT execute experiments.

3. **`ExperimentManifestEngine`**:
   - Generates immutable reproducibility manifests (`MAN_`).

4. **`ExperimentReplayEngine`**:
   - Generates and verifies deterministic replay specifications (`RPL_`).

---

## 6. SQLITE PERSISTENCE ARCHITECTURE

Persistence is provided by `goat.experiments.persistence.sqlite`:

- **WAL Mode & Foreign Keys**: `PRAGMA foreign_keys = ON; PRAGMA journal_mode = WAL;`
- **Repositories**:
  - `ExperimentRepository`
  - `ManifestRepository`
  - `LifecycleRepository`
  - `ReplayRepository`
  - `ScheduleRepository`
  - `SummaryRepository`
- **Context Manager**: `ExperimentPersistenceContext` managing connection lifecycle and thread safety.

---

## 7. REPORTING GENERATORS

Module `goat.experiments.reporting.reports`:
- `generate_experiment_report(...)`: GFM Markdown report for experiments.
- `generate_lifecycle_report(...)`: Audit log for state transitions.
- `generate_manifest_report(...)`: Manifest parameters breakdown.
- `generate_replay_report(...)`: Replay specification report.
- `generate_json_report(...)`: Canonical JSON serialization.
- `generate_executive_summary(...)`: Executive inventory report.

---

## 8. NON-NEGOTIABLE COMPLIANCE AUDIT

The `goat.experiments` subsystem contains:
- ZERO broker code
- ZERO execution engine logic
- ZERO market prediction
- ZERO trading strategies
- ZERO technical indicators
- ZERO signal generation
- ZERO risk sizing
- ZERO portfolio logic
- ZERO statistical evaluation
- ZERO hypothesis scoring

It strictly manages scientific experiment containers, manifests, lifecycles, and replay specifications.
