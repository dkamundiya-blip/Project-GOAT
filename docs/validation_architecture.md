# Scientific Hypothesis Validation Engine Architecture

## Overview

The `goat.validation` subsystem is responsible for transforming scientific trading hypotheses into statistically validated research outcomes.

The engine does **NOT** generate trading signals.

It validates whether a hypothesis has sufficient scientific evidence to become an accepted research result.

All components are deterministic, immutable, replayable, auditable, and SQLite-backed.

---

## Subsystem Architecture

```
goat/validation/
├── __init__.py           # Unified public API exports (__all__)
├── engine.py             # ScientificHypothesisValidationEngine
├── core/                 # Core models & state machine
│   ├── __init__.py
│   ├── context.py        # ValidationContext
│   ├── enums.py          # ValidationState, DecisionType
│   ├── hypothesis.py     # ScientificHypothesis (HYP_<HEX16>)
│   └── run.py            # ValidationRun (VRN_<HEX16>)
├── evidence/             # Evidence collection & aggregation
│   ├── __init__.py
│   ├── aggregator.py     # EvidenceAggregator
│   ├── collector.py      # EvidenceCollector
│   └── models.py         # ValidationEvidence (VEV_<HEX16>)
├── statistics/           # Pure deterministic scoring
│   ├── __init__.py
│   ├── calculator.py     # StatisticalCalculator
│   └── scores.py         # ValidationScores (8 score components)
├── decisions/            # Rule engine & decision generation
│   ├── __init__.py
│   ├── generator.py      # DecisionGenerator
│   ├── models.py         # ValidationDecision (VDC_<HEX16>)
│   └── rules.py          # ValidationRuleEngine & ValidationThresholds
├── reporting/            # Report generation & formatting
│   ├── __init__.py
│   ├── generator.py      # Report generators & serializers
│   └── models.py         # ValidationReport, Audit, Evidence, Stats reports
└── persistence/          # SQLite transactional storage
    ├── __init__.py
    └── sqlite.py         # SQLiteValidationRepository (Schema v1)
```

---

## Validation Pipeline

```
Receive ScientificHypothesis
         │
         ▼
  Submit Evidence (Experiment, Study, Consensus, Execution)
         │
         ▼
  Aggregate Evidence (Weights, Confidences, Breakdown)
         │
         ▼
  Compute Statistical Scores (8 Deterministic Scores)
         │
         ▼
  Evaluate Validation Rules (Configurable Thresholds)
         │
         ▼
  Generate ValidationDecision (ACCEPTED / REJECTED / etc.)
         │
         ▼
  Create & Persist ValidationRun (VRN_<HEX16>)
         │
         ▼
  Generate Reports (ValidationReport, Evidence, Audit, Stats)
```

---

## Statistical Framework

All 8 statistical scores are computed purely deterministically without random sampling or probabilistic simulations:

1. **Confidence Score**: Ratio of validated evidence count to total evidence count, scaled by evidence saturation.
2. **Evidence Score**: Normalized total evidence weight.
3. **Agreement Score**: Ratio of supporting evidence count to total evidence count.
4. **Reproducibility Score**: Independent replication count relative to required replication threshold.
5. **Robustness Score**: Cross-context verification count relative to required context threshold.
6. **Stability Score**: Ratio of temporally consistent evaluation periods to total periods.
7. **Validation Score**: Pass rate across all configured rule thresholds.
8. **Overall Scientific Confidence**: Weighted linear combination of the 7 component scores.

---

## Rule Engine & Decision Outcomes

The `ValidationRuleEngine` evaluates validation scores against configurable `ValidationThresholds`:

- **ACCEPTED**: Overall confidence $\ge$ `acceptance_threshold` AND $\ge 66\%$ threshold pass rate.
- **REJECTED**: Overall confidence $<$ `rejection_threshold`.
- **INCONCLUSIVE**: Overall confidence between rejection and acceptance thresholds.
- **NEEDS_MORE_DATA**: Total evidence count $<$ `min_evidence_count`.
- **INVALID_HYPOTHESIS**: Zero evidence submitted.

---

## SQLite Persistence (Schema v1)

All validation entities are persisted using foreign-key-enforced transactional SQLite tables:

- `validation_hypotheses` (HYP_)
- `validation_runs` (VRN_)
- `validation_evidence` (VEV_)
- `validation_decisions` (VDC_)
- `validation_reports` (VRPT_)
- `validation_audit_events`

Supports full export, import, schema version checking, and integrity verification.

---

## Determinism & Replay

Every validation run can be replayed deterministically. The engine recomputes canonical SHA-256 hashes of all payloads to verify replay integrity matching `VRN.replay_hash`.
