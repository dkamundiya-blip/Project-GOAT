# CONSTITUTIONAL AMENDMENT No. 002 REPORT
## Capital-Aware Risk Management & Minimum Executable Risk Principle

**Authorizing Body**: Institutional Quantitative Research Board  
**Target Release**: Project GOAT Version 0.9  
**Effective Date**: 2026-08-04  
**Status**: APPROVED & PERMANENTLY INCORPORATED  
**Target Document**: `PROJECT_GOAT_V0.9_STRATEGIC_CONSTITUTION.md`

---

## 1. PURPOSE

Project GOAT has one long-term objective:
> **Produce statistically validated trading opportunities that are executable on accounts of every size, including very small retail accounts, while remaining scientifically defensible.**

Prior to Constitutional Amendment No. 002, quantitative risk models frequently assumed institutional capital depth—where position sizes can be continuously scaled down to arbitrary fractional units to satisfy strict fixed-percentage risk rules (e.g., 0.5% or 1.0% per trade). In practice, retail accounts ranging from $10 to $500 face rigid broker physical constraints (minimum contract sizes, lot step increments, and tick values). Under institutional models, standard broker minimum contract sizes often represent 5%, 10%, or even 20% of a small account's balance, causing strict percentage-based engines to reject valid trades or forcing traders into dangerous manual overrides.

Constitutional Amendment No. 002 establishes the formal legal and quantitative foundation to bridge this gap:
- **GOAT is NOT designed only for institutional-sized accounts.**
- **GOAT is designed to intelligently adapt execution decisions according to available capital while NEVER compromising scientific validation.**

---

## 2. NEW CONSTITUTIONAL SECTIONS

Constitutional Amendment No. 002 permanently inserts **SECTION 12** into `PROJECT_GOAT_V0.9_STRATEGIC_CONSTITUTION.md`:

### Section 12 Title:
`CAPITAL-AWARE RISK MANAGEMENT & MINIMUM EXECUTABLE RISK PRINCIPLE`

### Core Principles Enacted:
1. **Principle 1 (Dual Requirement)**: Every trading decision must simultaneously satisfy both scientific qualification and capital affordability. Neither alone is sufficient.
2. **Principle 2 (Broker Minimum Contract Evaluation)**: Requires pre-execution polling and calculation of broker minimum lot size, lot step, contract size, tick value, instrument specifications, margin requirements, and broker constraints.
3. **Principle 3 (Immutability of Scientific Stop Loss)**: Stop loss originates solely from scientific research, simulation, walk-forward testing, and structural risk qualification. Capital size must NEVER alter technical stop loss levels.
4. **Principle 4 (Minimum Executable Risk - MER)**: Formalizes MER as the minimum monetary loss produced by the broker's minimum contract when the scientific stop loss is hit.
5. **Principle 5 (Non-Bypassing 7-Step Sequence)**: Enforces a 7-step sequence: Scientific Qualification → Risk Qualification → Determine Broker Minimum Lot → Calculate MER → Compare MER against Available Capital → Apply Selected Risk Profile → Produce Execution Decision.
6. **Principle 6 (Capital-Aware Execution)**: Replaces universal percentage-risk assumptions with capital-aware execution for small accounts where broker constraints dominate.
7. **Principle 7 (Modular Risk Profiles Architecture)**: Establishes Conservative, Balanced, Aggressive Growth, and Custom profiles to govern execution policy without altering scientific edge quality.
8. **Principle 8 (Aggressive Growth Mandate & Full Transparency)**: Officially recognizes Aggressive Growth for small account acceleration while mandating pre-execution display of Monetary Risk, Monetary Reward, Actual Risk Percentage, Risk/Reward Ratio, and MER.
9. **Principle 9 (Execution Decision Categorization)**: Classifies execution outcomes into `APPROVED`, `HIGH_RISK_APPROVED`, `BROKER_LIMITED`, `INSUFFICIENT_CAPITAL`, and `REJECTED`.
10. **Principle 10 (Edge Quality Independence)**: Fixes Edge Quality as invariant to account size ($10 to $1,000,000). Account size affects execution feasibility, never scientific validity.
11. **Principle 11 (Explicitly Forbidden Behaviors)**: Strictly bans modifying stop losses, revenge lot sizing, Martingale, grid recovery, averaging down, curve-fitting risk, ignoring broker minimums, ignoring monetary loss, and hiding actual risk percentage.
12. **Principle 12 (Capital Awareness Philosophy)**: Codifies the philosophy: *"GOAT does not attempt to force every account into institutional risk models. Instead, GOAT objectively determines what is scientifically valid, what is technically executable, and what is financially survivable."*

---

## 3. RATIONALE

1. **Elimination of Quantitative Blindspots**: Traditional institutional frameworks create an impasse for small accounts: either reject all trades due to percentage-cap breaches or bypass risk governance entirely. Amendment No. 002 provides a mathematically sound, transparent middle ground.
2. **Absolute Defense of Scientific Integrity**: By forbidding stop-loss manipulation or parameter curve-fitting, the amendment prevents the common pitfall of altering technical trades to force fit account size.
3. **Formalization of MER as a Fundamental Metric**: Monetary loss is the true physical reality of risk. Defining MER anchors risk assessment in absolute currency values rather than abstract percentage ratios.
4. **Radical Risk Transparency**: Requiring all 5 key risk metrics before order execution guarantees that traders using Aggressive Growth profiles make fully informed decisions with complete awareness of tail exposure.

---

## 4. LONG-TERM ARCHITECTURAL IMPACT

The passage of Constitutional Amendment No. 002 establishes explicit design contracts for GOAT's long-term architecture:

1. **Decoupling Scientific Edge from Execution Sizing**:
   - `goat.research` and `goat.edge` remain 100% agnostic of account capital. Edge qualification produces pure market-structural parameters (Entry, Stop Loss, Take Profit, Expectancy, Confidence).
   - `goat.risk` acts as the constitutional execution gatekeeper, consuming edge parameters alongside broker specifications and account balances to compute sizing and MER.

2. **Integration of Broker Metadata into Pipeline**:
   - `goat.broker` must provide deterministic, cached access to real-time broker instrument metadata (lot steps, min lots, tick values, margin requirements).

3. **Deterministic Replay Integrity for Capital Sizing**:
   - Replay logs must record broker specifications and capital snapshots alongside tick data to guarantee 100% deterministic historical replay of execution decisions across all risk profiles.

---

## 5. FUTURE SUBSYSTEM IMPLICATIONS

When future implementation steps build or extend `goat.risk`, `goat.broker`, `goat.execution`, and `goat.telemetry`, they must satisfy the following constitutional constraints:

1. **`goat.broker`**:
   - Must implement immutable data contracts for broker instrument specifications (`min_lot`, `lot_step`, `contract_size`, `tick_value`).
   - Must support pre-trade specification querying prior to any trade evaluation.

2. **`goat.risk`**:
   - Must implement the explicit MER formula:
     $$\text{MER} = \text{min\_lot} \times \text{contract\_size} \times |\text{entry\_price} - \text{stop\_loss\_price}| \times \text{tick\_value\_factor}$$
   - Must enforce the mandatory 7-step execution sequence without shortcut paths.
   - Must expose modular Risk Profile engines (`Conservative`, `Balanced`, `AggressiveGrowth`, `Custom`).
   - Must output structured execution decisions matching the 5 constitutional status categories (`APPROVED`, `HIGH_RISK_APPROVED`, `BROKER_LIMITED`, `INSUFFICIENT_CAPITAL`, `REJECTED`).

3. **`goat.telemetry` & Dashboard**:
   - Must render pre-trade execution receipts displaying all 5 mandatory transparency fields: Monetary Risk ($), Monetary Reward ($), Actual Risk Percentage (%), Risk/Reward Ratio (R:R), and Minimum Executable Risk ($).

4. **Zero Code / Schema / Subsystem Changes in Current Step**:
   - As mandated by Constitutional Amendment No. 002 directive, zero implementation code, Python packages, SQLite schemas, or test files were created or modified during this constitutional enactment step.

---

======================================================================

CONSTITUTIONAL AMENDMENT No. 002

CAPITAL-AWARE RISK MANAGEMENT &
MINIMUM EXECUTABLE RISK PRINCIPLE

APPROVED

THIS AMENDMENT IS NOW A PERMANENT PART OF

PROJECT_GOAT_V0.9_STRATEGIC_CONSTITUTION

======================================================================
