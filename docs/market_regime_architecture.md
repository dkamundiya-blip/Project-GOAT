# Project GOAT — Market Regime Classification & Edge Applicability Architecture

Version: v0.7 — Step 6.1 (Phase VI)  
Status: Active Implementation / Certified  
Package: `goat.regimes`  

---

## 1. Architecture Summary

Step 6.1 introduces the **Market Regime Classification & Edge Applicability Engine** (`goat.regimes`). Scientific candidate edges discovered in Step 6.0 are not universally valid across all market environments. This engine deterministically classifies current market conditions into 12 supported regimes and evaluates edge applicability, determining which edges should be active, conditional, watchlist, or suppressed without producing trading signals or relying on non-deterministic AI/ML inference.

Key Design Guarantees:
- **No Signal Generation**: The engine evaluates regime compatibility and edge applicability. It does NOT produce buy/sell trading signals.
- **Zero AI / ML Reasoning**: Rule-based deterministic classification. All decisions are 100% reproducible and auditable.
- **Immutable Pydantic Models**: Core domain models (`MarketRegime`, `RegimeRule`, `ApplicabilityAssessment`, `ApplicabilityDecision`, `RegimeExplainabilityRecord`) are strictly frozen Pydantic models.
- **Deterministic Identifiers**: Prefix IDs (`MRG_<HEX16>`, `RGR_<HEX16>`, `APA_<HEX16>`, `APD_<HEX16>`, `REX_<HEX16>`, `MRR_<HEX16>`) derived via canonical SHA-256 digests.
- **Complete Explainability**: 100% scientific traceability from observations to rule evaluations to activation state rationale.
- **SQLite Persistence & Replay**: Full round-trip persistence with referential integrity (`PRAGMA foreign_keys = ON`) and exact state replay.

---

## 2. Supported Market Regimes (`RegimeType`)

The classification engine supports 12 deterministic market regimes:
1. `TRENDING`
2. `RANGING`
3. `BREAKOUT`
4. `REVERSAL`
5. `ACCUMULATION`
6. `DISTRIBUTION`
7. `HIGH_VOLATILITY`
8. `LOW_VOLATILITY`
9. `LIQUIDITY_EXPANSION`
10. `LIQUIDITY_CONTRACTION`
11. `TRANSITIONAL`
12. `UNDEFINED`

---

## 3. Rule Engine & Classification Pipeline

`RegimeRuleEngine` evaluates deterministic conditions across market observation metrics (trend strength, volatility z-score, volume ratio, breakout flags, momentum states, participation states).

`MarketRegimeClassificationEngine` evaluates all registered rules against market observations and assigns primary regime classifications and confidence scores.

---

## 4. Edge Applicability & Activation States (`EdgeActivationState`)

`EdgeApplicabilityEngine` evaluates compatibility between candidate `ScientificEdge` objects and the active `MarketRegime`:
- `ACTIVE`: High compatibility score ($\ge 0.70$) and edge confidence ($\ge 0.70$).
- `CONDITIONAL`: Moderate compatibility score ($0.45 - 0.69$) or conditional regime requirements.
- `WATCHLIST`: Newly discovered edge (`NEW` or `EXPERIMENTAL` maturity).
- `INACTIVE`: Low regime compatibility ($< 0.45$) or suppressed by rule.
- `REJECTED`: High conflict penalty ($> 0.30$) or blacklisted under active regime.

### Deterministic Tie-Breaking
For equal applicability scores, active edges are sorted by:
1. `overall_edge_score` (descending)
2. `reproducibility` (descending)
3. `edge_id` (alphabetically ascending)

---

## 5. Scientific Explainability Architecture

`EdgeApplicabilityEngine` constructs `RegimeExplainabilityRecord` objects providing complete traceability:
- Target `regime_id` and `assessment_id`
- Target `edge_id`
- Detected regime classification
- Supporting rule IDs and market observations
- Narrative scientific explanation string

---

## 6. Persistence & Replay

Repositories:
- `MarketRegimeRepository`: Table `market_regimes`
- `RegimeRuleRepository`: Table `regime_rules`
- `ApplicabilityRepository`: Tables `applicability_assessments` & `regime_explainability_records`
- `DecisionRepository`: Table `applicability_decisions`
- `ReportRepository`: Table `regime_reports`

Replay support: `coordinator.replay_decision(decision_id)` and `coordinator.replay_regime(regime_id)` restore exact historical models from SQLite persistence.

---

## 7. Public API

Exposed through `goat.regimes.__all__`:

```python
from goat.regimes import (
    MarketRegimeEngineCoordinator,
    MarketRegimeClassificationEngine,
    RegimeRuleEngine,
    EdgeApplicabilityEngine,
    MarketRegime,
    RegimeRule,
    ApplicabilityAssessment,
    ApplicabilityDecision,
    RegimeExplainabilityRecord,
    RegimeType,
    EdgeActivationState,
    MarketRegimeRepository,
    RegimeRuleRepository,
    ApplicabilityRepository,
    DecisionRepository,
    ReportRepository,
)
```

---

## 8. Code Example

```python
import sqlite3
from goat.regimes import MarketRegimeEngineCoordinator
from goat.alpha import ScientificEdge

conn = sqlite3.connect(":memory:")
coordinator = MarketRegimeEngineCoordinator(conn=conn)

observations = {
    "trend_strength": 0.85,
    "volatility_zscore": 0.2,
    "volume_ratio": 1.5,
    "trend_direction": "BULLISH",
}

edge = ScientificEdge(
    edge_id="SED_1234567890ABCDEF",
    title="Quantitative Edge: MOM_10D",
    confidence=0.88,
    reproducibility=0.90,
    discovery_timestamp="2026-07-30T12:00:00Z",
)

regime, decision, report = coordinator.execute_regime_applicability_workflow(
    observations=observations,
    candidate_edges=[edge],
    timestamp="2026-07-30T12:00:00Z",
)

print(report.to_markdown())
```

---

## 9. Future Extension Points

- **Multi-Regime Transition Dynamics**: Modeling smooth transitional probability bounds between adjacent regime states.
- **Cross-Asset Regime Correlation**: Evaluating synchronized regime transitions across correlated asset classes.
