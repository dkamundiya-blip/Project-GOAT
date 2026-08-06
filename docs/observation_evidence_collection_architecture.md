# OBSERVATION & EVIDENCE COLLECTION ENGINE ARCHITECTURE
## PROJECT GOAT VERSION 0.9 — STEP 9.2 SPECIFICATION

**Document Version**: 1.0.0  
**Authorizing Body**: Institutional Quantitative Research Board  
**Executive Authority**: Chief Scientific Officer  
**Target Subsystem**: `goat.evidence`  
**Effective Date**: 2026-08-04  
**Status**: CERTIFIED & FROZEN  

---

## 1. ARCHITECTURE SUMMARY

The **Observation & Evidence Collection Engine** (`goat.evidence`) serves as the objective measurement and evidence preservation layer for Project GOAT Version 0.9. It observes raw, uninterpreted market phenomena and structures them into immutable, append-only scientific evidence records (`EVR_`) and chronological observation collections (`COL_`).

Crucially, the evidence subsystem is strictly observation-only:
- It **DOES NOT** generate trading signals.
- It **DOES NOT** predict market direction.
- It **DOES NOT** evaluate trading strategies.
- It **DOES NOT** determine entries or exits.
- It **DOES NOT** calculate stop losses or take profits.
- It **DOES NOT** execute trades or calculate P&L.
- It **DOES NOT** perform statistical evaluation or confidence scoring.
- It **DOES NOT** judge whether evidence supports or refutes a hypothesis.

It operates as a pure, objective scientific observation and evidence linkage container governed by SHA-256 canonical digests.

---

## 2. PACKAGE STRUCTURE

```
goat/evidence/
├── __init__.py               # Top-level public API exports with strict __all__
├── engine.py                 # ScientificEvidenceEngine master facade
├── core/
│   ├── __init__.py           # Core exports
│   ├── canonical.py          # Deterministic SHA-256 serialization & ID generation
│   ├── enums.py              # ObservationStatus, ObservationSource, EvidenceCategory
│   └── models.py             # Immutable Pydantic V2 domain models
├── observation/
│   ├── __init__.py           # Observation package exports
│   └── engine.py             # ScientificObservationEngine
├── collection/
│   ├── __init__.py           # Collection package exports
│   └── engine.py             # EvidenceCollectionEngine
├── linkage/
│   ├── __init__.py           # Linkage package exports
│   └── engine.py             # EvidenceLinkageEngine
├── reporting/
│   ├── __init__.py           # Reporting package exports
│   └── reports.py            # Markdown, JSON, Observation & Summary report generators
└── persistence/
    ├── __init__.py           # Persistence package exports
    └── sqlite.py             # SQLite WAL repositories & context
```

---

## 3. DOMAIN MODEL INVENTORY

All domain models are implemented as immutable Pydantic V2 models with `frozen=True` and `extra="forbid"`:

1. **`ScientificObservation`**:
   - Primary observation entity representing an objective measured metric.
   - Identifier prefix: `OBS_<HEX16>`.
   - Fields: `metric_name`, `metric_value`, `unit_of_measure`, `timestamp`, `source`, `category`, `instrument`, `status`, `observer_id`, `tags`, `metadata`, `canonical_hash`.

2. **`EvidenceRecord`**:
   - Structured evidence compiled from one or more observation IDs.
   - Identifier prefix: `EVR_<HEX16>`.
   - Fields: `category`, `observation_ids`, `title`, `description`, `source`, `instrument`, `timestamp`, `tags`, `metadata`, `canonical_hash`.

3. **`ObservationCollection`**:
   - Chronological grouping of observations over a time window.
   - Identifier prefix: `COL_<HEX16>`.
   - Fields: `collection_name`, `observation_ids`, `start_timestamp`, `end_timestamp`, `collector_id`, `tags`, `metadata`, `canonical_hash`.

4. **`EvidenceLink`**:
   - Relational provenance link connecting a `ScientificHypothesis` (`HYP_`) to evidence or observations.
   - Identifier prefix: `LNK_<HEX16>`.
   - Fields: `hypothesis_id`, `target_id`, `link_type`, `linker_id`, `timestamp`, `metadata`, `canonical_hash`.

5. **`EvidenceSummary`**:
   - Aggregate state snapshot of subsystem counts and breakdowns.
   - Identifier prefix: `EVS_<HEX16>`.
   - Fields: `total_observations`, `total_evidence_records`, `total_collections`, `total_links`, `category_counts`, `source_counts`, `timestamp`, `metadata`, `canonical_hash`.

---

## 4. CANONICAL ID GENERATION & SHA-256 HASHING

All identifiers are computed deterministically using sorted-key canonical JSON serialization and SHA-256 hashing. Identical inputs yield identical IDs:

- **Observation ID**: `OBS_<HEX16>` derived from `instrument`, `metric_name`, `metric_value`, `source`, `timestamp`.
- **Evidence Record ID**: `EVR_<HEX16>` derived from `category`, sorted `observation_ids`, `source`, `timestamp`.
- **Collection ID**: `COL_<HEX16>` derived from `collection_name`, sorted `observation_ids`, `timestamp`.
- **Link ID**: `LNK_<HEX16>` derived from `hypothesis_id`, `link_type`, `target_id`, `timestamp`.
- **Summary ID**: `EVS_<HEX16>` derived from `total_observations`, `total_evidence_records`, `timestamp`.

---

## 5. SUB-ENGINE RESPONSIBILITIES

1. **`ScientificObservationEngine`**:
   - Creates, timestamps, and verifies raw metric observations.
   - Maintains strict chronological ordering.
   - Computes deterministic SHA-256 digests.
   - Strictly refrains from interpreting price action or market meaning.

2. **`EvidenceCollectionEngine`**:
   - Collects and groups individual observations into packaged `EvidenceRecord` (`EVR_`) and `ObservationCollection` (`COL_`) entities.
   - Prevents duplicate compilations.
   - Enforces append-only history.

3. **`EvidenceLinkageEngine`**:
   - Associates evidence (`EVR_` / `OBS_`) with hypotheses (`HYP_`).
   - Maintains relational provenance maps.
   - MUST NOT judge or score whether evidence supports or refutes a hypothesis.

---

## 6. SQLITE PERSISTENCE ARCHITECTURE

Persistence is provided by `goat.evidence.persistence.sqlite`:

- **WAL Mode & Foreign Keys**: `PRAGMA foreign_keys = ON; PRAGMA journal_mode = WAL;`
- **Repositories**:
  - `ObservationRepository`
  - `EvidenceRepository`
  - `CollectionRepository`
  - `LinkRepository`
  - `SummaryRepository`
- **Context Manager**: `EvidencePersistenceContext` managing connection lifecycle and thread safety.

---

## 7. REPORTING GENERATORS

Module `goat.evidence.reporting.reports`:
- `generate_observation_report(...)`: GFM Markdown report for observations.
- `generate_evidence_report(...)`: GFM Markdown report for evidence records.
- `generate_collection_summary_report(...)`: GFM Markdown report for collections.
- `generate_json_report(...)`: Canonical JSON serialization.
- `generate_evidence_summary_report(...)`: Aggregate metrics report.
- `generate_executive_report(...)`: Executive summary inventory.

---

## 8. NON-NEGOTIABLE COMPLIANCE AUDIT

The `goat.evidence` subsystem contains:
- ZERO broker code
- ZERO execution logic
- ZERO market prediction
- ZERO trading strategies
- ZERO technical analysis
- ZERO signal generation
- ZERO risk sizing
- ZERO portfolio logic
- ZERO statistical evaluation
- ZERO confidence scoring
- ZERO hypothesis approval

It strictly observes, records, links, and preserves scientific evidence.
