# PROJECT GOAT VERSION 0.9 — STRATEGIC CONSTITUTION & LIVE TRADING MANIFESTO

**Authorizing Body**: Institutional Quantitative Research Board  
**Target Release**: Project GOAT Version 0.9  
**Effective Date**: 2026-08-01  
**Status**: APPROVED & MANDATORY (AMENDED BY CONSTITUTIONAL AMENDMENT No. 001 & No. 002)  

---

## 1. Version 0.9 Mission

The mission of Project GOAT Version 0.9 is to transition from an engineering infrastructure platform into a live quantitative research and trading system.

Project GOAT's objective is **NOT**:
- High trade frequency or volume for volume's sake
- Naive point-in-time price prediction accuracy
- Impressive user interface dashboards
- Flashy demonstrations of AI/ML or probabilistic reasoning

Project GOAT's single, uncompromising objective **IS**:
> **Finding, validating, executing, and archiving statistically defensible, repeatable market edges that survive live production trading.**

---

## 2. Core Scientific Principles

1. **Every Trade is an Experiment**: Every live or backtested order submission is a hypothesis test conducted under strict statistical controls.
2. **Every Result is Evidence**: Every execution fill, slippage delta, and mark-to-market output is empirical data to be recorded without bias.
3. **Every Loss Teaches Something**: Losses are not failures; they are empirical observations detailing structural boundaries, regime shifts, or execution frictions.
4. **Every Profit Requires Explanation**: Profitable outcomes are meaningless unless grounded in a validated, explainable, and repeatable market mechanism.
5. **No Assumption Becomes Truth Without Evidence**: All quantitative hypotheses must pass rigorous statistical qualification before capital allocation.
6. **No Optimization Without Scientific Justification**: Curve-fitting and parameter tweaking without underlying market structure rationale are strictly forbidden.

---

## 3. Deriv First Strategy

Project GOAT Version 0.9 designates **Stage 1: Deriv Synthetic Indices** as the primary quantitative research and live validation environment.

### Phased Rollout Mandate:
```
[Stage 1: Deriv Synthetic Indices] ──► [Stage 2: Weltrade] ──► [Stage 3: Forex]
      (Primary Research Core)            (Secondary Expansion)    (Institutional Scale)
```

Everything in Version 0.9 must be optimized, benchmarked, and proven on **Deriv** before extending to **Weltrade**, and before extending to **Forex**. Synthetic indices provide 24/7 algorithmic continuity, deterministic tick generation, and pristine execution telemetry required for rapid quantitative feedback loops.

---

## 4. Edge Philosophy

### What IS an Edge?
A genuine quantitative edge is a statistically significant, structurally explainable asymmetry in market outcomes that yields positive long-term mathematical expectancy after accounting for spread, commission, latency, and slippage.

### What IS NOT an Edge?
- Over-fitted backtests on historical price series
- Short-term winning streaks driven by random distribution
- Strategies dependent on zero-latency execution or unachievable fill prices
- Unexplained patterns without structural or behavioral market mechanics

### Evidence Requirements & Confidence Thresholds:
- **Statistical Significance**: Minimum sample size ($N \ge 500$ trades in replay/backtest) with $p$-value $< 0.01$ across multiple market regimes.
- **Regime Robustness**: Must demonstrate positive expectancy across at least 3 distinct market regimes (e.g. `LOW_VOLATILITY_TREND`, `HIGH_VOLATILITY_EXPANSION`, `MEAN_REVERTING_RANGE`).
- **Live Validation**: Requires at least 100 live production execution cycles demonstrating consistency with historical replay before scaling capital.
- **Edge Rejection**: Any candidate strategy whose live expectancy diverges by $> 2.0\sigma$ from replay baseline is immediately halted and returned to scientific research.

---

## 5. Live Trading Philosophy

1. **Execution Discipline**: Orders are routed strictly via `goat.execution` and `goat.broker`. Manual or ad-hoc order entry is prohibited.
2. **Risk Discipline**: Capital allocation is governed entirely by `goat.risk`. Position sizing, total exposure limits, and daily loss caps cannot be overridden.
3. **Capital Preservation First**: Risk management prioritizes survival over return maximization. Preserving principal takes absolute precedence over capturing upside.
4. **Scientific Discipline**: Trading parameters are immutable during active sessions; modifications require offline scientific re-qualification.
5. **Human Override Protocol**: Human intervention is strictly restricted to emergency kill-switches (`HALT_ALL_TRADING`). Humans cannot manually place or modify individual trades.
6. **Emergency Stop Rules**: Maximum acceptable intraday portfolio drawdown is capped at **3.0%**. Exceeding this limit triggers automated order cancellation and subsystem quarantine.
7. **Maximum Acceptable Uncertainty**: If market tick latency exceeds 1,000ms or WebSocket connection stability drops below 99.0%, trading halts automatically.

---

## 6. Ranked Research Priorities

1. **Market Microstructure & Tick Latency**: Analyzing tick ingestion dynamics and execution delays.
2. **Deriv Synthetic Index Mechanics**: Mapping mathematical properties and volatility clustering of synthetic assets.
3. **Order Flow & Slippage Dynamics**: Quantifying broker execution friction and spread expansion during regime shifts.
4. **Regime Transitions & Volatility Clustering**: Detecting early signals of transition between low and high volatility regimes.
5. **Liquidity Behavior & False Breakouts**: Identifying structural traps and liquidity sweeps near key support/resistance levels.
6. **Time-of-Day & Session Effects**: Mapping cyclical patterns across trading sessions.

---

## 7. Ranked Engineering Priorities

1. **Safety & Non-Bypass Enforcement**: Absolute protection of risk boundaries and execution pipelines.
2. **Determinism & Immutable Hashing**: Ensuring 100% reproducible state computations via SHA-256 canonical digests.
3. **Replay Integrity**: Guaranteeing 1-to-1 exact chronological replay of live market feeds and event logs.
4. **Reliability & Control Room Observability**: Passive monitoring of system health, heartbeats, and telemetry snapshots.
5. **Auditability & Append-Only Archive**: Zero deletion, mutation, or compaction of historical records.
6. **Recoverability & State Reconciliation**: Seamless recovery from WebSocket disconnects with portfolio re-alignment.
7. **Explainability**: Clear mathematical traceability for every signal and execution decision.
8. **Broker Independence**: Abstract interfaces allowing seamless expansion from Deriv to Weltrade and Forex.

---

## 8. Success Metrics for Version 0.9

Version 0.9 will be evaluated strictly by scientific and institutional engineering metrics, **NOT** by short-term paper profits:

1. **Scientific Reproducibility**: 100% correlation between live execution logs and offline replay outputs.
2. **Replay Integrity**: 0 discrepancies during full replay audits.
3. **Execution Quality**: Slippage maintained within $\le 0.5$ pips of tick arrival price.
4. **Risk Consistency**: Zero violations of risk allocation or maximum drawdown boundaries.
5. **Edge Stability**: Live trade expectancy within $1.0\sigma$ of historical research estimates.
6. **Maximum Drawdown**: Intraday portfolio drawdown never exceeding 3.0%.
7. **Capital Preservation**: 100% preservation of core operating capital during volatile regimes.
8. **Live Validation Rate**: Percentage of researched hypotheses that successfully transition to live production.

---

## 9. Version 0.9 Exit Criteria (Pre-requisites for Version 1.0)

Before Project GOAT Version 1.0 (Commercial Production Deployment) can begin, Version 0.9 must satisfy all of the following exit criteria:

- [ ] **Live Deriv Deployment Proven**: Continuous, uninterrupted live trading execution on Deriv Synthetic Indices for $\ge 30$ consecutive days.
- [ ] **Institutional Execution Stable**: Zero unhandled WebSocket disconnects or un-reconciled order states.
- [ ] **Scientific Edge Validated**: At least one quantitative edge validated with positive expectancy across $\ge 200$ live trades.
- [ ] **Risk Framework Proven**: Zero risk limit breaches under real-market stress.
- [ ] **Archive Integrity Maintained**: 100% append-only audit trail verification with zero corrupted records.
- [ ] **Control Room Monitoring Proven**: 99.99% uptime of `goat.monitoring` heartbeat and telemetry collection.
- [ ] **Replay Verified**: Full round-trip replay verification matching live production logs.
- [ ] **Zero Technical Debt**: Clean code quality and complete documentation freeze.

---

## 10. Permanent Constitutional Rules

1. **Never optimize for appearance over science.**
2. **Never increase system complexity without measurable, statistically proven benefit.**
3. **Never remove explainability or black-box a trading decision.**
4. **Never bypass replay validation.**
5. **Never bypass risk sizing or drawdown limits.**
6. **Never bypass scientific qualification gates.**
7. **Never chase short-term profits at the expense of scientific integrity.**
8. **Always favor long-term structural robustness over short-term performance.**

---

## 11. Edge Retirement & Scientific Revalidation Principle (CONSTITUTIONAL AMENDMENT No. 001)

### Core Constitutional Principles:
1. **Every Edge is Provisional**: No edge is permanent. Every edge must continuously justify its existence through live evidence.
2. **Live Performance Overrides Historical Validation**: Historical validation is only the starting point. Live evidence is the highest authority and always overrides historical performance.
3. **Evidence-Based Promotion & Retirement Only**: An edge may be promoted or retired ONLY through scientific evidence. Neither promotion nor retirement may occur because of emotion, intuition, optimism, or fear.
4. **Immediate Re-classification to Research Status**: An edge showing statistically significant degradation shall immediately enter **RESEARCH STATUS** until revalidated.
5. **No Ad-Hoc Saving of Deteriorating Edges**: The system must never attempt to "save" a deteriorating edge by changing parameters, increasing risk, averaging down, curve fitting, or adding discretionary filters without a complete scientific revalidation process.
6. **Permanent Archival & Replayability**: Retired edges remain permanently archived. They are never deleted. Their complete scientific history remains replayable. Future evidence may justify their reactivation through a completely new validation process.

### Objective Retirement Triggers:
An edge shall be retired from live production trading upon meeting any of the following objective statistical triggers:
- Live mathematical expectancy falling materially below historical validated expectancy ($> 2.0\sigma$ divergence).
- Persistent performance degradation across multiple market regimes.
- Scientific confidence interval falling below constitutional thresholds ($p \ge 0.05$).
- Reproducibility failure between live execution logs and offline replay outputs.
- Walk-forward performance deterioration on out-of-sample data.
- Risk-adjusted expectancy collapse or excessive drawdown contribution.
- Structural market change invalidating the original quantitative assumptions.
- Broker execution characteristics (spread, slippage, latency) materially altering edge expectancy.

*Mandatory Condition*: No single losing trade retires an edge. No short-term drawdown alone retires an edge. Retirement requires statistically defensible evidence.

### Revalidation Requirements:
A retired edge may only return to active production after completing the full, un-shortened scientific pipeline:

```
[Scientific Review] ──► [Evidence Collection] ──► [Hypothesis Revision]
                                                         │
[Scientific Qualification] ◄── [Risk Qualification] ◄── [Walk-Forward Validation] ◄── [Simulation]
          │
          ▼
[Controlled Live Validation] ──► [Institutional Approval] ──► [Production Deployment]
```

Only after completing every stage of this pipeline may the edge return to active live production deployment.

### Immutable Constitutional Rules:
- Live evidence always overrides historical evidence.
- GOAT must never become attached to a profitable edge.
- GOAT must never protect an edge because of its history.
- Every edge must continually earn deployment.
- Scientific integrity is more important than profitability.
- Retiring an edge is a scientific success, not a failure.
- Preserving capital is preferable to preserving ego.

---

# SECTION 12
## CAPITAL-AWARE RISK MANAGEMENT & MINIMUM EXECUTABLE RISK PRINCIPLE (CONSTITUTIONAL AMENDMENT No. 002)

### 12.1 Purpose & Core Mission
Project GOAT has one long-term objective:

> **Produce statistically validated trading opportunities that are executable on accounts of every size, including very small retail accounts, while remaining scientifically defensible.**

The constitution explicitly states:
- Project GOAT is **NOT** designed only for institutional-sized accounts.
- Project GOAT is designed to intelligently adapt execution decisions according to available capital while **NEVER** compromising scientific validation.

---

### 12.2 Principle 1: Dual Requirement of Scientific and Capital Qualification
Every trading decision shall be **BOTH**:

- **Scientific**  
  AND  
- **Capital Aware**

Scientific quality alone is insufficient. Capital affordability alone is insufficient. Both conditions must simultaneously be satisfied.

---

### 12.3 Principle 2: Mandatory Broker Minimum Executable Contract Evaluation
Before any execution decision is made, GOAT **SHALL ALWAYS** determine the broker's minimum executable contract.

The following broker specifications **MUST** always be evaluated prior to trade evaluation:
- **Minimum Lot Size**
- **Lot Step**
- **Contract Size**
- **Tick Value**
- **Instrument Specifications**
- **Margin Requirements**
- **Broker Constraints**

No trade may be evaluated before these values are known.

---

### 12.4 Principle 3: Immutability of Scientific Stop Loss
The scientifically determined Stop Loss **SHALL NEVER** be modified solely because the account is small.

Stop Loss originates **ONLY** from:
- **Scientific Qualification**
- **Simulation**
- **Walk Forward Validation**
- **Risk Qualification**

Capital size **MUST NEVER** change the technical structure of the trade.

---

### 12.5 Principle 4: Definition of Minimum Executable Risk (MER)
Introduce a permanent constitutional concept named **Minimum Executable Risk (MER)**.

**Minimum Executable Risk** is formally defined as:
> *"The minimum monetary loss produced by the broker's minimum executable contract when the scientifically determined stop loss is reached."*

MER is therefore a broker-dependent quantity.

---

### 12.6 Principle 5: Mandatory Non-Bypassing Execution Eligibility Sequence
Execution eligibility shall be determined using the following sequence:

```
1 Scientific Qualification
        │
        ▼
2 Risk Qualification
        │
        ▼
3 Determine Broker Minimum Lot
        │
        ▼
4 Calculate MER
        │
        ▼
5 Compare MER against available capital
        │
        ▼
6 Apply selected Risk Profile
        │
        ▼
7 Produce Execution Decision
```

This sequence shall **NEVER** be bypassed.

---

### 12.7 Principle 6: Capital-Aware Execution Over Pure Percentage Risk
The constitution shall recognize that percentage-based risk is not universally applicable.

For extremely small accounts, broker constraints frequently dominate theoretical percentage risk.

GOAT must therefore support capital-aware execution.

---

### 12.8 Principle 7: Modular Risk Profiles Architecture
Introduce constitutional support for multiple Risk Profiles.

The constitution **SHALL** define the following architecture:
- **Conservative**
- **Balanced**
- **Aggressive Growth**
- **Custom**

Risk Profiles define execution policy.  
Risk Profiles **NEVER** alter scientific edge quality.

---

### 12.9 Principle 8: Aggressive Growth Profile & Mandatory Transparency
The **Aggressive Growth Profile** shall become an officially recognized constitutional profile.

Its purpose is: **Small account growth.**

It may intentionally tolerate significantly larger percentage exposure than institutional profiles.

However, GOAT must **ALWAYS** display:
- **Monetary Risk**
- **Monetary Reward**
- **Actual Risk Percentage**
- **Risk/Reward Ratio**
- **Minimum Executable Risk**

before execution. Nothing is hidden from the trader.

---

### 12.10 Principle 9: Categorization of Execution Decisions
Execution decisions shall be classified into constitutional categories:

- **`APPROVED`**: Trade meets all scientific, risk, and account capital thresholds under standard risk limits.
- **`HIGH_RISK_APPROVED`**: Trade is scientifically valid and within profile limits, but MER represents an elevated percentage of capital authorized by the Aggressive Growth profile.
- **`BROKER_LIMITED`**: Trade is scientifically valid, but broker minimum contracts or lot step constraints prevent optimal position sizing.
- **`INSUFFICIENT_CAPITAL`**: MER exceeds total available account capital or maximum account risk allocation limits. Trade is blocked.
- **`REJECTED`**: Trade fails scientific qualification, risk qualification, or violates constitutional rules. Trade is permanently blocked.

---

### 12.11 Principle 10: Independence of Scientific Edge Quality from Capital Size
Scientific Edge Quality **SHALL NEVER** be influenced by account size.

Example: An **A+ edge** remains **A+** whether the account is:
- **$10**
- **$100**
- **$1,000**
- or **$1,000,000**

Account size affects **execution**, **NOT** scientific validity.

---

### 12.12 Principle 11: Explicitly Forbidden Execution Behaviors
The amendment explicitly forbids the following behaviors:
- Changing stop losses merely because an account is small.
- Increasing lot size to recover losses.
- Martingale.
- Grid recovery.
- Averaging down.
- Curve fitting risk parameters.
- Ignoring broker minimum contracts.
- Ignoring monetary loss.
- Hiding actual percentage exposure.
- Any execution behaviour designed to "save" an otherwise invalid trade.

---

### 12.13 Principle 12: Permanent Capital Awareness Philosophy
Capital Awareness shall become a permanent GOAT philosophy.

> *"GOAT does not attempt to force every account into institutional risk models.  
> Instead,  
> GOAT objectively determines what is scientifically valid,  
> what is technically executable,  
> and what is financially survivable."*

---

## Final Certification

======================================================================  
**CONSTITUTIONAL AMENDMENT No. 001**  

**EDGE RETIREMENT & SCIENTIFIC REVALIDATION**  

**APPROVED**  

**THIS AMENDMENT IS NOW A PERMANENT PART OF**  
**PROJECT_GOAT_V0.9_STRATEGIC_CONSTITUTION**  
======================================================================  

======================================================================  
**CONSTITUTIONAL AMENDMENT No. 002**  

**CAPITAL-AWARE RISK MANAGEMENT &**  
**MINIMUM EXECUTABLE RISK PRINCIPLE**  

**APPROVED**  

**THIS AMENDMENT IS NOW A PERMANENT PART OF**  
**PROJECT_GOAT_V0.9_STRATEGIC_CONSTITUTION**  
======================================================================  

======================================================================  
**PROJECT GOAT VERSION 0.9**  

**STRATEGIC CONSTITUTION APPROVED**  

**READY TO BEGIN LIVE QUANTITATIVE RESEARCH**  

**DERIV SYNTHETIC INDICES DESIGNATED AS PRIMARY RESEARCH ENVIRONMENT**  
======================================================================  
