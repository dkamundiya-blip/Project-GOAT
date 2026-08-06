# EDGE PROMOTION & RETIREMENT GOVERNANCE ENGINE ARCHITECTURE
## PROJECT GOAT VERSION 0.9 — STEP 9.6 SPECIFICATION

**Document Version**: 1.0.0  
**Authorizing Body**: Institutional Quantitative Research Board  
**Executive Authority**: Chief Scientific Officer & Head of Quantitative Research  
**Target Subsystem**: `goat.governance`  
**Effective Date**: 2026-08-04  
**Status**: CERTIFIED & FROZEN  

---

## 1. ARCHITECTURE SUMMARY

The **Edge Promotion & Retirement Governance Engine** (`goat.governance`) is the constitutional decision-making authority responsible for determining whether a scientifically validated quantitative trading edge is:
- **Promoted** (`PROMOTE`)
- **Retained** (`RETAIN`)
- **Paused** (`PAUSE`)
- **Returned to Research** (`RETURN_TO_RESEARCH`)
- **Retired** (`RETIRE`)

The governance subsystem enforces strict constitutional principles:
- **No edge earns production status because it made money.**
- **No edge is retired because it lost money.**
- Every governance decision is based exclusively upon statistically defensible evidence accumulated throughout the complete scientific pipeline.
- Historical evidence is **NEVER** modified or deleted.
- Governance decisions are strictly append-only records (`GOV_`) linked to a complete audit trail (`AUD_`).

---

## 2. PACKAGE STRUCTURE

```
goat/governance/
├── __init__.py               # Top-level public API exports with strict __all__
├── engine.py                 # MasterGovernanceEngine facade
├── core/
│   ├── __init__.py           # Core package exports
│   ├── canonical.py          # Deterministic SHA-256 serialization & ID generation
│   ├── enums.py              # EdgeStatus, GovernanceDecisionOutcome, GovernanceReason
│   └── models.py             # Immutable Pydantic V2 domain models
├── promotion/
│   ├── __init__.py           # Promotion package exports
│   └── engine.py             # EdgePromotionEngine
├── retirement/
│   ├── __init__.py           # Retirement package exports
│   └── engine.py             # EdgeRetirementEngine
├── governance/
│   ├── __init__.py           # Governance package exports
│   └── engine.py             # EdgeGovernanceEngine
├── audit/
│   ├── __init__.py           # Audit package exports
│   └── engine.py             # GovernanceAuditEngine
├── reporting/
│   ├── __init__.py           # Reporting package exports
│   └── reports.py            # Markdown, JSON, Governance & Summary report generators
└── persistence/
    ├── __init__.py           # Persistence package exports
    └── sqlite.py             # SQLite WAL repositories & context
```

---

## 3. DOMAIN MODEL INVENTORY

All domain models are implemented as immutable Pydantic V2 models with `frozen=True` and `extra="forbid"`:

1. **`EdgeCandidate`**:
   - Submitted quantitative trading edge entity.
   - Identifier prefix: `EDG_<HEX16>`.
   - Fields: `title`, `hypothesis_id`, `evaluation_id`, `experiment_id`, `validation_session_id`, `evidence_ids`, `status`, `created_timestamp`, `metadata`, `canonical_hash`.

2. **`PromotionAssessment`**:
   - Evaluation of candidate against 7 strict promotion criteria.
   - Identifier prefix: `PRA_<HEX16>`.
   - Fields: `edge_id`, `hypothesis_id`, `is_hypothesis_passed`, `is_evidence_complete`, `is_experiment_complete`, `is_statistics_complete`, `is_live_validation_complete`, `is_constitution_satisfied`, `is_research_protocol_satisfied`, `is_promotable`, `assessment_notes`, `timestamp`, `canonical_hash`.

3. **`RetirementAssessment`**:
   - Evaluation of candidate against performance degradation and constitutional rules.
   - Identifier prefix: `RTA_<HEX16>`.
   - Fields: `edge_id`, `hypothesis_id`, `expectancy_degradation`, `confidence_decline`, `structural_shift_detected`, `amendment_001_violation`, `is_retirement_recommended`, `assessment_notes`, `timestamp`, `canonical_hash`.

4. **`GovernanceDecision`**:
   - Binding constitutional decision record.
   - Identifier prefix: `GOV_<HEX16>`.
   - Fields: `edge_id`, `hypothesis_id`, `decision`, `reason`, `rationale`, `authorizer`, `timestamp`, `metadata`, `canonical_hash`.

5. **`GovernanceAudit`**:
   - Traceability audit linking a decision back to the complete pipeline artifact chain.
   - Identifier prefix: `AUD_<HEX16>`.
   - Fields: `decision_id`, `edge_id`, `hypothesis_id`, `evidence_ids`, `experiment_id`, `evaluation_id`, `validation_session_id`, `is_explainable`, `is_replayable`, `operator`, `timestamp`, `canonical_hash`.

6. **`GovernanceSummary`**:
   - Aggregate snapshot report of candidate, decision, and rationale counts.
   - Identifier prefix: `GSM_<HEX16>`.
   - Fields: `total_edges`, `total_decisions`, `status_counts`, `decision_counts`, `reason_counts`, `timestamp`, `metadata`, `canonical_hash`.

---

## 4. CANONICAL ID GENERATION & SHA-256 HASHING

All identifiers are computed deterministically using sorted-key canonical JSON serialization and SHA-256 hashing. Identical inputs yield identical IDs:

- **Edge ID**: `EDG_<HEX16>` derived from `hypothesis_id`, `title`, `author`.
- **Promotion Assessment ID**: `PRA_<HEX16>` derived from `edge_id`, `hypothesis_id`, `evaluator`.
- **Retirement Assessment ID**: `RTA_<HEX16>` derived from `edge_id`, `hypothesis_id`, `evaluator`.
- **Decision ID**: `GOV_<HEX16>` derived from `edge_id`, `decision`, `reason`.
- **Audit ID**: `AUD_<HEX16>` derived from `decision_id`, `action`, `timestamp`, `operator`.
- **Summary ID**: `GSM_<HEX16>` derived from `total_edges`, `total_decisions`, `timestamp`.

---

## 5. SUB-ENGINE RESPONSIBILITIES

1. **`EdgePromotionEngine`**:
   - Verifies hypothesis passed, evidence complete, experiment complete, statistics supported, live validation passed, and constitutional/PRSP compliance.

2. **`EdgeRetirementEngine`**:
   - Evaluates performance degradation, expectation drift, confidence decline, and Amendment No.001 violations.

3. **`EdgeGovernanceEngine`**:
   - Derives binding governance decision outcomes (`PROMOTE`, `RETAIN`, `PAUSE`, `RETURN_TO_RESEARCH`, `RETIRE`) without human discretion.

4. **`GovernanceAuditEngine`**:
   - Verifies every decision is 100% explainable, replayable, and traceable back to `HYP_`, `EVR_`, `EXP_`, `STE_`, `VSN_`.

---

## 6. SQLITE PERSISTENCE ARCHITECTURE

Persistence is provided by `goat.governance.persistence.sqlite`:

- **WAL Mode & Foreign Keys**: `PRAGMA foreign_keys = ON; PRAGMA journal_mode = WAL;`
- **Repositories**:
  - `EdgeRepository`
  - `PromotionRepository`
  - `RetirementRepository`
  - `GovernanceRepository`
  - `AuditRepository`
  - `SummaryRepository`
- **Context Manager**: `GovernancePersistenceContext` managing connection lifecycle and thread safety.

---

## 7. REPORTING GENERATORS

Module `goat.governance.reporting.reports`:
- `generate_promotion_report(...)`: GFM Markdown report for promotion assessments.
- `generate_retirement_report(...)`: GFM Markdown report for retirement assessments.
- `generate_governance_decision_report(...)`: GFM Markdown report for binding decisions.
- `generate_audit_report(...)`: GFM Markdown report for audit verification.
- `generate_json_report(...)`: Canonical JSON serialization.
- `generate_executive_report(...)`: Executive summary inventory report.

---

## 8. NON-NEGOTIABLE COMPLIANCE AUDIT

The `goat.governance` subsystem contains:
- ZERO broker implementation
- ZERO execution engine
- ZERO strategy implementation
- ZERO hypothesis/evidence/experiment/statistical/live validation mutation
- ZERO parameter optimization or tuning
- ZERO position sizing or risk management
- ONLY appends immutable governance decisions (`GOV_`) and audit logs (`AUD_`).
