# Project GOAT — Scientific Risk Management & Capital Allocation Architecture

Version: v0.7 — Step 6.5 (Phase VI)  
Status: Active Implementation / Certified  
Package: `goat.risk`  

---

## 1. Architecture Summary

Step 6.5 introduces the **Scientific Risk Management, Position Sizing & Capital Allocation Engine** (`goat.risk`). Scientifically qualified and validated market opportunities (`ScientificQualification`, `SimulationResult`) must be transformed into capital-aware opportunities before entering any signal generation pipeline. This subsystem computes position sizing, stop-loss distance, take-profit distance, monetary risk, monetary reward, recommended lot size, minimum lot size, and capital allocation without placing trades or connecting to live brokers.

Key Design Guarantees:
- **No Broker Connection / No Trade Execution**: Purely deterministic position sizing and risk exposure calculations.
- **Zero AI / ML Reasoning**: Rule-based deterministic risk calculators. All calculations are 100% reproducible and auditable.
- **Immutable Pydantic Models**: Core domain models (`RiskProfile`, `PositionSizingDecision`, `CapitalAllocation`, `ExposureAssessment`, `RiskAssessment`) are strictly frozen Pydantic models.
- **Deterministic Identifiers**: Prefix IDs (`RPF_<HEX16>`, `PSD_<HEX16>`, `CAL_<HEX16>`, `EXP_<HEX16>`, `RSA_<HEX16>`, `SRR_<HEX16>`) derived via canonical SHA-256 digests.
- **Special Required Fields**: Every decision exposes Entry Price, Stop Loss, Take Profit, Monetary Risk, Monetary Reward, Recommended Lot Size, Minimum Lot Size, and Risk Percentage for direct consumption by Step 6.6 (Signal Generation).
- **SQLite Persistence & Replay**: Full round-trip persistence with referential integrity (`PRAGMA foreign_keys = ON`) and exact state replay.

---

## 2. Risk Pipeline

`ScientificRiskEngineCoordinator` manages the risk evaluation workflow:
1. `RiskProfile` configuration (account balance, max risk %, max exposure %)
2. `PositionSizingDecision` calculation (`PositionSizingEngine`)
3. `ExposureAssessment` evaluation (`ExposureAssessmentEngine`)
4. `CapitalAllocation` reservation (`CapitalAllocationEngine`)
5. `RiskAssessment` monetary summary generation (`MonetaryRiskCalculator`)

---

## 3. Position Sizing Engine (`PositionSizingEngine`)

Calculates deterministic position units and rounded lot sizes:
- Fixed percentage risk & fixed monetary risk
- Stop-loss & take-profit distance calculation
- Risk-reward ratio computation
- Minimum lot size enforcement
- Broker lot increment rounding (e.g. down to nearest `0.01` lot)
- Instrument point value / contract unit scaling

---

## 4. Capital Allocation Engine (`CapitalAllocationEngine`)

Tracks portfolio capital allocation across concurrent opportunities:
- Reserved capital tracking
- Unallocated available capital calculation
- Portfolio utilization percentage ($0.0$ to $1.0$)
- Over-allocation prevention

---

## 5. Exposure Assessment Engine (`ExposureAssessmentEngine`)

Evaluates portfolio and asset exposure constraints:
- `ACCEPTABLE`: Exposure within limits.
- `WARNING`: Exposure at $\ge 80\%$ of maximum threshold.
- `VIOLATION_EXCEEDED`: Exposure exceeds max portfolio exposure limit.

---

## 6. Risk Rules Engine (`RiskRulesEngine`)

Evaluates deterministic rules for position eligibility (`ELIGIBLE`, `INELIGIBLE_INSUFFICIENT_CAPITAL`, `INELIGIBLE_EXPOSURE_VIOLATION`, `INELIGIBLE_REWARD_RISK_TOO_LOW`). Every rejection produces deterministic narrative explanations.

---

## 7. Monetary Calculations Framework (`MonetaryRiskCalculator`)

Computes exact monetary values:
- Monetary Stop Loss & Take Profit
- Monetary Risk Amount & Expected Reward Amount
- Expected Return % on Account Balance
- Maximum Account Loss & Remaining Capital

---

## 8. Persistence & Replay

Repositories:
- `RiskProfileRepository`: Table `risk_profiles`
- `PositionSizingRepository`: Table `position_sizing_decisions`
- `CapitalAllocationRepository`: Table `capital_allocations`
- `ExposureRepository`: Table `exposure_assessments`
- `RiskAssessmentRepository`: Table `risk_assessments`
- `RiskReportRepository`: Table `risk_reports`

Replay support: `coordinator.replay_sizing(sizing_id)` and `coordinator.replay_allocation(allocation_id)` restore exact historical models from SQLite persistence.

---

## 9. Public API

Exposed through `goat.risk.__all__`:

```python
from goat.risk import (
    ScientificRiskEngineCoordinator,
    PositionSizingEngine,
    CapitalAllocationEngine,
    ExposureAssessmentEngine,
    MonetaryRiskCalculator,
    RiskRulesEngine,
    RiskProfile,
    PositionSizingDecision,
    CapitalAllocation,
    ExposureAssessment,
    RiskAssessment,
    ExposureStatus,
    SizingMethod,
    RiskProfileRepository,
    PositionSizingRepository,
    CapitalAllocationRepository,
    ExposureRepository,
    RiskAssessmentRepository,
    RiskReportRepository,
)
```

---

## 10. Code Example

```python
import sqlite3
from goat.risk import ScientificRiskEngineCoordinator
from goat.qualification.core.models import ScientificQualification, QualificationState
from goat.simulation.core.models import SimulationResult, ValidationStatus

conn = sqlite3.connect(":memory:")
coordinator = ScientificRiskEngineCoordinator(conn=conn)

qual = ScientificQualification(
    qualification_id="SQL_1111111111111111",
    composite_id="CMP_1111111111111111",
    regime_id="MRG_1111111111111111",
    evaluation_timestamp="2026-07-30T12:00:00Z",
    qualification_state=QualificationState.QUALIFIED,
    overall_readiness=0.88,
)

sim_res = SimulationResult(
    result_id="SRS_1111111111111111",
    run_id="SRN_1111111111111111",
    validation_status=ValidationStatus.VALIDATED,
    statistical_metrics={"profit_factor": 1.6},
)

sizing, alloc, report = coordinator.execute_risk_workflow(
    qualification=qual,
    simulation_result=sim_res,
    instrument="EURUSD",
    entry_price=1.0850,
    stop_loss_price=1.0800,
    take_profit_price=1.0950,
    timestamp="2026-07-30T12:00:00Z",
    account_balance=100000.0,
    max_risk_percent=0.02,
)

print(report.to_markdown())
```

---

## 11. Future Extension Points

- **Cross-Asset Volatility Scaling**: Dynamic ATR-based stop-loss distance calculation.
- **Hierarchical Portfolio Margin Allocation**: Multi-account margin reservation across tier-1 prime brokers.
