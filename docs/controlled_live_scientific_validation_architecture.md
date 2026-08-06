# CONTROLLED LIVE SCIENTIFIC VALIDATION ENGINE ARCHITECTURE
## PROJECT GOAT VERSION 0.9 — STEP 9.5 SPECIFICATION

**Document Version**: 1.0.0  
**Authorizing Body**: Institutional Quantitative Research Board  
**Executive Authority**: Chief Scientific Officer & Head of Quantitative Research  
**Target Subsystem**: `goat.live_validation`  
**Effective Date**: 2026-08-04  
**Status**: CERTIFIED & FROZEN  

---

## 1. ARCHITECTURE SUMMARY

The **Controlled Live Scientific Validation Engine** (`goat.live_validation`) validates statistically supported hypotheses (`HYP_` + `STE_` Supported) under controlled live market conditions.

Crucially, every live trade executed by this subsystem is a **scientific experiment**—not a profit generation drive:
- It **DOES NOT** deploy edges to production (edge promotion is Step 9.6).
- It **DOES NOT** mutate historical evidence, experiments, or hypotheses.
- It **ONLY** records empirical live observations (`VOB_`), monitors execution quality metrics, and derives scientific recommendations (`VDC_`).
- It operates as a pure, objective scientific validation layer governed by SHA-256 canonical digests.

---

## 2. PACKAGE STRUCTURE

```
goat/live_validation/
├── __init__.py               # Top-level public API exports with strict __all__
├── engine.py                 # MasterLiveValidationEngine facade
├── core/
│   ├── __init__.py           # Core package exports
│   ├── canonical.py          # Deterministic SHA-256 serialization & ID generation
│   ├── enums.py              # ValidationStatus, ValidationDecisionOutcome, MonitoringStatus
│   └── models.py             # Immutable Pydantic V2 domain models
├── eligibility/
│   ├── __init__.py           # Eligibility package exports
│   └── engine.py             # ValidationEligibilityEngine
├── validation/
│   ├── __init__.py           # Validation package exports
│   └── engine.py             # ControlledLiveValidationEngine
├── monitoring/
│   ├── __init__.py           # Monitoring package exports
│   └── engine.py             # ValidationMonitoringEngine
├── retirement/
│   ├── __init__.py           # Retirement package exports
│   └── engine.py             # ValidationRetirementEngine
├── reporting/
│   ├── __init__.py           # Reporting package exports
│   └── reports.py            # Markdown, JSON, Validation & Summary report generators
└── persistence/
    ├── __init__.py           # Persistence package exports
    └── sqlite.py             # SQLite WAL repositories & context
```

---

## 3. DOMAIN MODEL INVENTORY

All domain models are implemented as immutable Pydantic V2 models with `frozen=True` and `extra="forbid"`:

1. **`LiveValidationCandidate`**:
   - Qualified research candidate eligible for live scientific validation.
   - Identifier prefix: `LVC_<HEX16>`.
   - Fields: `hypothesis_id`, `evaluation_id`, `experiment_id`, `evidence_ids`, `replay_id`, `status`, `eligibility_score`, `created_timestamp`, `metadata`, `canonical_hash`.

2. **`ValidationSession`**:
   - Active controlled live scientific validation session container.
   - Identifier prefix: `VSN_<HEX16>`.
   - Fields: `candidate_id`, `hypothesis_id`, `status`, `monitoring_status`, `start_timestamp`, `end_timestamp`, `total_observations`, `operator`, `metadata`, `canonical_hash`.

3. **`ValidationObservation`**:
   - Individual empirical live observation under controlled live conditions.
   - Identifier prefix: `VOB_<HEX16>`.
   - Fields: `session_id`, `timestamp`, `live_outcome`, `expected_outcome`, `slippage`, `spread`, `latency_ms`, `fill_ratio`, `metadata`, `canonical_hash`.

4. **`ValidationDecision`**:
   - Formal scientific decision outcome and recommendation derived for a live validation session.
   - Identifier prefix: `VDC_<HEX16>`.
   - Fields: `session_id`, `candidate_id`, `decision`, `rationale`, `timestamp`, `authorizer`, `metadata`, `canonical_hash`.

5. **`ValidationSummary`**:
   - Aggregate snapshot report of candidate, session, and decision counts.
   - Identifier prefix: `VSM_<HEX16>`.
   - Fields: `total_candidates`, `total_sessions`, `total_observations`, `status_counts`, `decision_counts`, `timestamp`, `metadata`, `canonical_hash`.

6. **`ValidationAudit`**:
   - Append-only audit trail event for validation session state changes.
   - Identifier prefix: `VAU_<HEX16>`.
   - Fields: `session_id`, `action`, `previous_status`, `new_status`, `operator`, `timestamp`, `notes`, `canonical_hash`.

---

## 4. CANONICAL ID GENERATION & SHA-256 HASHING

All identifiers are computed deterministically using sorted-key canonical JSON serialization and SHA-256 hashing. Identical inputs yield identical IDs:

- **Candidate ID**: `LVC_<HEX16>` derived from `hypothesis_id`, `evaluation_id`, `experiment_id`.
- **Session ID**: `VSN_<HEX16>` derived from `candidate_id`, `start_timestamp`, `operator`.
- **Observation ID**: `VOB_<HEX16>` derived from `session_id`, `timestamp`, `live_outcome`, `expected_outcome`.
- **Decision ID**: `VDC_<HEX16>` derived from `session_id`, `candidate_id`, `decision`.
- **Summary ID**: `VSM_<HEX16>` derived from `total_candidates`, `total_sessions`, `timestamp`.
- **Audit ID**: `VAU_<HEX16>` derived from `session_id`, `action`, `timestamp`, `operator`.

---

## 5. SUB-ENGINE RESPONSIBILITIES

1. **`ValidationEligibilityEngine`**:
   - Verifies hypothesis passed Step 9.4 (`STE_` with `SUPPORTED` decision).
   - Confirms evidence chain, replay integrity, and zero active duplicate sessions.

2. **`ControlledLiveValidationEngine`**:
   - Initiates validation sessions (`VSN_`) and records live empirical observations (`VOB_`).
   - Tracks execution consistency without mutating upstream scientific artifacts.

3. **`ValidationMonitoringEngine`**:
   - Monitors live execution quality: slippage, spread, latency, fill ratio.
   - Assigns health status (`NORMAL`, `WATCH`, `WARNING`, `CRITICAL`). Zero trading or optimization.

4. **`ValidationRetirementEngine`**:
   - Derives scientific conclusions (`SUPPORTED`, `INCONCLUSIVE`, `FAILED`, `PROMOTION_RECOMMENDED`, `RETIREMENT_RECOMMENDED`).
   - Appends immutable decision entities (`VDC_`). Final authority remains with Step 9.6 governance.

---

## 6. SQLITE PERSISTENCE ARCHITECTURE

Persistence is provided by `goat.live_validation.persistence.sqlite`:

- **WAL Mode & Foreign Keys**: `PRAGMA foreign_keys = ON; PRAGMA journal_mode = WAL;`
- **Repositories**:
  - `CandidateRepository`
  - `ValidationSessionRepository`
  - `ObservationRepository`
  - `DecisionRepository`
  - `AuditRepository`
  - `SummaryRepository`
- **Context Manager**: `LiveValidationPersistenceContext` managing connection lifecycle and thread safety.

---

## 7. REPORTING GENERATORS

Module `goat.live_validation.reporting.reports`:
- `generate_eligibility_report(...)`: GFM Markdown report for candidates.
- `generate_validation_report(...)`: GFM Markdown report for validation sessions.
- `generate_monitoring_report(...)`: GFM Markdown report for execution monitoring.
- `generate_decision_report(...)`: GFM Markdown report for decisions.
- `generate_json_report(...)`: Canonical JSON serialization.
- `generate_executive_report(...)`: Executive summary inventory report.

---

## 8. NON-NEGOTIABLE COMPLIANCE AUDIT

The `goat.live_validation` subsystem contains:
- ZERO broker implementation
- ZERO strategy implementation
- ZERO parameter optimization or tuning
- ZERO position sizing
- ZERO portfolio allocation logic
- ZERO automatic production deployment
- ZERO experiment/evidence/hypothesis/statistical mutation

It strictly performs controlled scientific live validation and appends immutable validation records.
