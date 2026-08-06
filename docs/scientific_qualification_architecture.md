# Project GOAT — Scientific Signal Qualification & Decision Readiness Architecture

Version: v0.7 — Step 6.3 (Phase VI)  
Status: Active Implementation / Certified  
Package: `goat.qualification`  

---

## 1. Architecture Summary

Step 6.3 introduces the **Scientific Signal Qualification & Decision Readiness Engine** (`goat.qualification`). Even high-quality composite market edges (`CompositeEdge`) are not automatically actionable. Before any future execution phase generates a trading signal, GOAT determines whether current evidence satisfies a rigorous scientific qualification process.

Key Design Guarantees:
- **No Signal Generation / No Trade Execution**: The engine evaluates scientific evidence sufficiency and decision readiness levels. It does NOT generate trade entries or execute trades.
- **Zero AI / ML Reasoning**: Rule-based deterministic gate evaluation and readiness scoring. All decisions are 100% reproducible and auditable.
- **Immutable Pydantic Models**: Core domain models (`ScientificQualification`, `QualificationGate`, `GateEvaluation`, `DecisionReadiness`, `QualificationExplainabilityRecord`) are strictly frozen Pydantic models.
- **Deterministic Identifiers**: Prefix IDs (`SQL_<HEX16>`, `QGT_<HEX16>`, `GEV_<HEX16>`, `DCR_<HEX16>`, `QEX_<HEX16>`, `SQR_<HEX16>`) derived via canonical SHA-256 digests.
- **Complete Explainability & Traceability**: 100% scientific traceability from gate evaluations to blocking conditions to authorized readiness levels.
- **SQLite Persistence & Replay**: Full round-trip persistence with referential integrity (`PRAGMA foreign_keys = ON`) and exact state replay.

---

## 2. Qualification Pipeline

`ScientificQualificationEngine` evaluates composite edges under active market regimes:
1. `QUALIFIED`: All mandatory gates passed and overall readiness $\ge 0.70$.
2. `CONDITIONAL_QUALIFICATION`: Non-mandatory gates failed, or overall readiness between $0.50 - 0.69$.
3. `DISQUALIFIED`: Any mandatory gate failed, or overall readiness $< 0.50$.

---

## 3. Qualification Gates Framework (`QualificationGateEngine`)

Implements 10 deterministic qualification gates:
1. **Scientific Evidence Sufficiency Gate**: Evaluates supporting evidence volume ($\ge 0.60$).
2. **Knowledge Support Gate**: Evaluates originating hypothesis backing ($\ge 0.50$).
3. **Composite Stability Gate**: Evaluates composite stability score ($\ge 0.70$).
4. **Historical Reproducibility Gate**: Evaluates empirical reproducibility ($\ge 0.70$).
5. **Conflict Threshold Gate**: Evaluates conflict penalty deduction ($\le 0.25$).
6. **Regime Compatibility Gate**: Evaluates regime classification confidence ($\ge 0.60$).
7. **Explainability Completeness Gate**: Evaluates narrative explainability score ($\ge 0.70$).
8. **Scientific Confidence Gate**: Evaluates synergy confidence score ($\ge 0.70$).
9. **Composite Maturity Gate**: Evaluates participating edge count and maturity ($\ge 0.50$).
10. **Data Completeness Gate**: Verifies clean metric observations without missing data ($\ge 0.90$).

---

## 4. Decision Readiness Framework (`ReadinessLevel`)

`DecisionReadinessEngine` assigns authorized decision readiness levels:
- `NOT_READY`: Disqualified or active blocking conditions.
- `EARLY_RESEARCH`: Readiness score $< 0.50$.
- `EXPERIMENTAL`: Readiness score $0.50 - 0.64$.
- `CANDIDATE`: Readiness score $0.65 - 0.74$.
- `READY_FOR_SIMULATION`: Readiness score $0.75 - 0.84$ with zero mandatory blocking conditions.
- `READY_FOR_FORWARD_TESTING`: Readiness score $\ge 0.85$ with 100% passed mandatory gates.

> [!IMPORTANT]
> Authorized readiness levels permit progression to future simulation or forward-testing phases ONLY. They DO NOT authorize live trading.

---

## 5. Blocking Conditions Framework (`BlockingConditionType`)

Identifies active blocking conditions preventing readiness advancement:
- `INSUFFICIENT_EVIDENCE`
- `CONFLICTING_EVIDENCE`
- `WEAK_REPRODUCIBILITY`
- `INCOMPLETE_EXPLAINABILITY`
- `LOW_SCIENTIFIC_CONFIDENCE`
- `REGIME_MISMATCH`
- `COMPOSITE_INSTABILITY`
- `KNOWLEDGE_GAPS`
- `INCOMPLETE_VALIDATION`

---

## 6. Scientific Explainability Architecture

`DecisionReadinessEngine` constructs `QualificationExplainabilityRecord` objects providing 100% scientific traceability:
- Target `qualification_id`
- Participating composites and applicable market regimes
- Passed and failed gate IDs
- Active blocking condition types
- Narrative scientific rationale string

---

## 7. Persistence & Replay

Repositories:
- `QualificationRepository`: Table `scientific_qualifications`
- `GateRepository`: Table `qualification_gates`
- `GateEvaluationRepository`: Table `gate_evaluations`
- `DecisionReadinessRepository`: Tables `decision_readiness_records` & `qualification_explainability_records`
- `QualificationReportRepository`: Table `qualification_reports`

Replay support: `coordinator.replay_qualification(qualification_id)` and `coordinator.replay_readiness(readiness_id)` restore exact historical models from SQLite persistence.

---

## 8. Public API

Exposed through `goat.qualification.__all__`:

```python
from goat.qualification import (
    ScientificQualificationEngineCoordinator,
    ScientificQualificationEngine,
    QualificationGateEngine,
    DecisionReadinessEngine,
    ScientificQualification,
    QualificationGate,
    GateEvaluation,
    DecisionReadiness,
    QualificationExplainabilityRecord,
    QualificationState,
    ReadinessLevel,
    QualificationRepository,
    GateRepository,
    GateEvaluationRepository,
    DecisionReadinessRepository,
    QualificationReportRepository,
)
```

---

## 9. Code Example

```python
import sqlite3
from goat.qualification import ScientificQualificationEngineCoordinator
from goat.composite.core.models import CompositeEdge, CompositeScore
from goat.regimes.core.models import MarketRegime

conn = sqlite3.connect(":memory:")
coordinator = ScientificQualificationEngineCoordinator(conn=conn)

composite = CompositeEdge(
    composite_id="CMP_1111111111111111",
    title="Composite MOM + VOL",
    participating_edges=["SED_1", "SED_2"],
    supporting_evidence=["VAL_1", "VAL_2", "VAL_3"],
    creation_timestamp="2026-07-30T12:00:00Z",
)

score = CompositeScore(
    score_id="CSC_1111111111111111",
    composite_id="CMP_1111111111111111",
    synergy_score=0.88,
    reproducibility_score=0.90,
    stability_score=0.85,
    explainability_score=0.90,
    overall_score=0.88,
    timestamp="2026-07-30T12:00:00Z",
)

regime = MarketRegime(
    regime_id="MRG_1111111111111111",
    timestamp="2026-07-30T12:00:00Z",
    regime_type="TRENDING",
    confidence=0.85,
)

qual, readiness, report = coordinator.execute_qualification_workflow(
    composite=composite,
    score=score,
    regime=regime,
    timestamp="2026-07-30T12:00:00Z",
)

print(report.to_markdown())
```

---

## 10. Future Extension Points

- **Multi-Stage Simulation Authorizers**: Authorizing progression to paper-trading simulation environments.
- **Dynamic Gate Sensitivity Thresholds**: Tuning gate thresholds based on historical cross-asset regime volatility.
