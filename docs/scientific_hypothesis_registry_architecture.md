# SCIENTIFIC HYPOTHESIS REGISTRY ENGINE ARCHITECTURE
## PROJECT GOAT VERSION 0.9 — STEP 9.1 SPECIFICATION

**Document Version**: 1.0.0  
**Authorizing Body**: Institutional Quantitative Research Board  
**Executive Authority**: Chief Scientific Officer  
**Target Subsystem**: `goat.research`  
**Effective Date**: 2026-08-04  
**Status**: CERTIFIED & FROZEN  

---

## 1. ARCHITECTURE SUMMARY

The **Scientific Hypothesis Registry Engine** (`goat.research`) serves as the foundational quantitative research subsystem for Project GOAT Version 0.9. It manages the complete lifecycle of scientific research hypotheses—from initial draft formulation through mathematical validation, revision tracking, status transitions, reporting, and immutable SQLite persistence.

Crucially, the registry is strategy-agnostic: it contains zero references to specific technical patterns, market strategies, indicators, brokers, or execution logic. It treats all quantitative hypotheses as generic, immutable scientific models governed by SHA-256 canonical digests.

---

## 2. PACKAGE STRUCTURE

```
goat/research/
├── __init__.py               # Top-level public API exports
├── engine.py                 # ScientificResearchEngine facade
├── core/
│   ├── __init__.py           # Core package exports
│   ├── canonical.py          # Deterministic SHA-256 canonical ID generators
│   ├── enums.py              # HypothesisStatus, HypothesisPriority, EvidenceLevel
│   └── models.py             # Immutable Pydantic V2 domain models
├── registry/
│   ├── __init__.py           # Registry package exports
│   └── engine.py             # ScientificHypothesisRegistry engine
├── validation/
│   ├── __init__.py           # Validation package exports
│   └── engine.py             # HypothesisValidationEngine
├── reporting/
│   ├── __init__.py           # Reporting package exports
│   └── reports.py            # Markdown, JSON, Executive & Summary generators
└── persistence/
    ├── __init__.py           # Persistence package exports
    └── sqlite.py             # SQLite WAL repositories & context
```

---

## 3. DOMAIN MODEL INVENTORY

All domain models are implemented as immutable Pydantic V2 models with `frozen=True` and `extra="forbid"`:

1. **`ScientificHypothesis`**:
   - Primary domain entity representing a registered hypothesis.
   - Identifier prefix: `HYP_<HEX16>`.
   - Includes title, research question, null hypothesis ($H_0$), alternative hypothesis ($H_1$), expected behaviour, independent/dependent variables, assumptions, tail risk statement, success/failure criteria, status, priority, evidence level, revision number, tags, metadata, and canonical SHA-256 hash digest.

2. **`HypothesisRevision`**:
   - Audit trail entity logging every revision and change event.
   - Identifier prefix: `REV_<HEX16>`.
   - Tracks hypothesis ID, revision number, previous hash, change summary, author, and timestamp.

3. **`HypothesisValidation`**:
   - Evaluation record produced by `HypothesisValidationEngine`.
   - Identifier prefix: `HVL_<HEX16>`.
   - Tracks validation outcome boolean, rule evaluation results, errors, warnings, reviewer, and timestamp.

4. **`HypothesisApproval`**:
   - Status transition and approval record.
   - Identifier prefix: `HAP_<HEX16>`.
   - Tracks approver, resulting target status, approval notes, and timestamp.

5. **`HypothesisRegistrySummary`**:
   - Aggregate state snapshot of the registry.
   - Identifier prefix: `HRS_<HEX16>`.
   - Tracks total count, status breakdown, priority breakdown, and evidence level breakdown.

---

## 4. CANONICAL ID GENERATION & SHA-256 HASHING

All identifiers are generated deterministically using sorted-key canonical JSON serialization and SHA-256 hashing. Identical inputs produce 100% identical IDs across restarts:

- **Hypothesis ID**: `HYP_<HEX16>` derived from `title`, `null_hypothesis`, `alternative_hypothesis`, `author`, `version`.
- **Revision ID**: `REV_<HEX16>` derived from `hypothesis_id`, `revision_number`, `previous_hash`, `timestamp`.
- **Validation ID**: `HVL_<HEX16>` derived from `hypothesis_id`, `is_valid`, `reviewer`, `timestamp`.
- **Approval ID**: `HAP_<HEX16>` derived from `hypothesis_id`, `approver`, `status`, `timestamp`.
- **Summary ID**: `HRS_<HEX16>` derived from `total_hypotheses`, `timestamp`.

---

## 5. VALIDATION ENGINE RULES

The `HypothesisValidationEngine` enforces five non-bypassable validation rules:

1. **`VAL_001_FIELD_INTEGRITY`**: Validates that all required text fields meet minimum character lengths.
2. **`VAL_002_PROTOCOL_COMPLIANCE`**: Enforces PRSP v1.0 requirements (must specify quantitative criteria and valid author).
3. **`VAL_003_CONSTITUTION_COMPLIANCE`**: Bans forbidden discretionary or subjective terms ("magic indicator", "guaranteed profit", etc.).
4. **`VAL_004_UNIQUENESS`**: Prevents duplicate hypothesis registration or duplicate title/$H_0$ content combinations.
5. **`VAL_005_IDENTIFIER_FORMAT`**: Ensures correct `HYP_` prefix and hex formatting.

---

## 6. SQLITE PERSISTENCE ARCHITECTURE

Persistence is managed by `goat.research.persistence.sqlite`:

- **WAL Mode & Foreign Keys**: `PRAGMA foreign_keys = ON; PRAGMA journal_mode = WAL;`
- **Repositories**:
  - `HypothesisRepository`
  - `RevisionRepository`
  - `ValidationRepository`
  - `ApprovalRepository`
  - `SummaryRepository`
- **Context Manager**: `ResearchPersistenceContext` provides seamless thread-safe interaction with memory or disk-backed SQLite databases.

---

## 7. REPORTING GENERATORS

Reporting functions in `goat.research.reporting.reports`:
- `generate_markdown_report(hypothesis)`: Comprehensive GFM Markdown report.
- `generate_json_report(hypothesis)`: Canonical JSON dump.
- `generate_validation_report(validation)`: Detailed rule result matrix and errors.
- `generate_registry_summary_report(summary)`: Tabular summary breakdown.
- `generate_executive_report(registry)`: High-level executive inventory.

---

## 8. NON-NEGOTIABLE COMPLIANCE STATEMENT

The `goat.research` subsystem contains:
- ZERO broker code
- ZERO execution logic
- ZERO market data
- ZERO trading strategies
- ZERO technical analysis
- ZERO price prediction
- ZERO signal generation
- ZERO risk sizing
- ZERO portfolio logic

It is a pure scientific hypothesis management framework.
