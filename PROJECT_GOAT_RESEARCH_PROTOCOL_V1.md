# PROJECT GOAT — PRE-IMPLEMENTATION SCIENTIFIC RESEARCH PROTOCOL (PRSP v1.0)
## INSTITUTIONAL QUANTITATIVE RESEARCH OPERATING MANUAL

**Document Version**: 1.0.0  
**Authorizing Body**: Institutional Quantitative Research Board  
**Executive Authority**: Chief Scientific Officer  
**Target Release**: Project GOAT Version 0.9  
**Effective Date**: 2026-08-04  
**Status**: APPROVED, MANDATORY & FROZEN  

---

## SECTION 1: RESEARCH PHILOSOPHY

1. **Every Hypothesis Begins as Unproven**: No quantitative idea possesses inherent truth. Every trading hypothesis is presumed false until proven valid through rigorous empirical testing under controlled conditions.
2. **Evidence is Superior to Opinion**: Subjective intuition, market commentary, personal beliefs, and discretionary biases hold zero legal or quantitative authority in GOAT. Only empirical data and mathematical proofs constitute evidence.
3. **Statistical Evidence is Superior to Historical Belief**: Traditional trading lore, unvalidated technical patterns, and historical anecdotes are invalid unless backed by statistically qualified out-of-sample data distributions ($p < 0.01$).
4. **Every Experiment Must Be Reproducible**: A scientific result is meaningless unless an independent researcher or automated replay engine can reproduce identical outputs from identical input datasets.
5. **No Edge is Permanent**: Financial and synthetic markets evolve continuous regime shifts. Every quantitative edge is provisional and must continuously justify its deployment through live production evidence.
6. **No Edge is Protected from Retirement**: Historical profitability creates zero immunity. An edge showing statistically significant performance degradation is immediately retired, regardless of past success or emotional attachment.

---

## SECTION 2: RESEARCH STANDARDS

Every research subsystem, experiment, and quantitative worker in Project GOAT must strictly enforce the following eight mandatory standards:

1. **Objective Definitions**: All market phenomena, indicators, entry/exit triggers, and regime classifications must be defined using unambiguous mathematical equations. Discretionary terms (e.g., "looks bullish" or "strong support") are strictly illegal.
2. **Deterministic Rules**: System execution must produce 100% identical state outputs for identical chronological input tick streams. Random seeds must be explicitly recorded and reproducible.
3. **Replayability**: Every research session, experiment run, and live trade must be 100% replayable from append-only tick logs and event streams.
4. **Explainability**: Every candidate edge must possess a clear, testable market-structural mechanism (e.g., volatility clustering, order flow imbalance, structural shock distribution). Statistical correlations without explainable underlying mechanics are rejected.
5. **Reproducibility**: Experiments must undergo full cross-validation and independent replay checks prior to advancing to higher evidence tiers.
6. **Append-Only Evidence**: Data ingestion, tick recordings, experiment logs, and research observations are append-only. Mutation, deletion, or retro-active editing of historical research data is forbidden.
7. **Immutable Records**: Once a hypothesis or experiment is registered, its parameter definitions, execution code, and baseline hashes are locked against mutation.
8. **SHA-256 Cryptographic Integrity**: Every research artifact, dataset, experiment manifest, and evidence package is cryptographically signed with a SHA-256 canonical hash digest to guarantee tamper-proof audit trails.

---

## SECTION 3: HYPOTHESIS REQUIREMENTS

No quantitative research may commence without a formally registered Hypothesis. Every hypothesis document must contain the following 12 mandatory fields:

1. **Title**: Concise, descriptive identifier (e.g., `HYP_CRASH_1000_SPIKE_RECOVERY_VOLATILITY_EXPANSION`).
2. **Research Question**: Clear, single-objective scientific question being investigated.
3. **Null Hypothesis ($H_0$)**: Formal mathematical statement assuming no market edge, zero excess expectancy, or random price distribution.
4. **Alternative Hypothesis ($H_1$)**: Formal mathematical statement defining the expected non-random edge or statistical asymmetry.
5. **Expected Behaviour**: Detailed structural breakdown of market mechanism driving the phenomenon.
6. **Variables**:
   - **Independent Variables**: Input factors, lookback windows, regime indicators, and volatility thresholds.
   - **Dependent Variables**: Trade outcome distributions, trade expectancy ($\mathbb{E}[R]$), Sharpe ratio, Max Adverse Excursion (MAE), and holding duration.
7. **Assumptions**: Explicit market conditions required for hypothesis validity (e.g., maximum spread caps, liquidity requirements, continuous tick stream).
8. **Risk Statement**: Tail-risk analysis detailing potential failure modes during adverse regime shifts.
9. **Success Criteria**: Quantitative statistical bounds required to reject $H_0$ ($p < 0.01$, sample size $N \ge 500$, positive expectancy $\mathbb{E}[R] > 0$).
10. **Failure Criteria**: Explicit statistical thresholds triggering immediate hypothesis rejection.
11. **Research Metadata**: Author, timestamp, version tag, target instrument class.
12. **Cryptographic Digest**: Canonical SHA-256 hash of the hypothesis registration object.

---

## SECTION 4: EXPERIMENT REQUIREMENTS

Every quantitative experiment executed under Version 0.9 must register an immutable Experiment Manifest specifying:

1. **Purpose**: Specific scientific goal of the experiment run.
2. **Dataset**: Canonical identifier and SHA-256 fingerprint of the historical or live tick dataset utilized.
3. **Observation Window**: Precise start and end timestamps (`ISO-8601` format) defining the data evaluation range.
4. **Sample Size ($N$)**: Total count of evaluated trade setups, price ticks, or regime instances (minimum $N \ge 500$ for backtest qualification; $N \ge 100$ for live micro-validation).
5. **Instrument**: Target asset symbol (e.g., Deriv `Volatility 100 Index`, `Crash 500 Index`, `Step Index`).
6. **Market Regime**: Primary regime classification under which the experiment runs (e.g., `HIGH_VOLATILITY_EXPANSION`, `MEAN_REVERTING_RANGE`, `STRUCTURAL_SHOCK_SPIKE`).
7. **Time Period**: Granularity and session window evaluated (e.g., continuous 24/7 synthetic tick stream).
8. **Research Notes**: Detailed quantitative log of observations, parameter constraints, and anomalies encountered.
9. **Research Version**: Git commit hash and software release version executing the experiment.
10. **Scientific Reviewer**: Assigned quantitative researcher or automated governance agent certifying experiment execution.

---

## SECTION 5: STATISTICAL REQUIREMENTS

Scientific qualification requires strict compliance with statistical governance standards:

1. **Sample Size Requirements**:
   - Backtest & Simulation Qualification: Minimum $N \ge 500$ trade execution events across at least 3 distinct market regimes.
   - Live Micro-Validation: Minimum $N \ge 100$ live production trades on small account sizes.
2. **Confidence Levels & Significance**:
   - Statistical significance testing must achieve $p$-value $< 0.01$ (99% confidence level) to reject the null hypothesis $H_0$.
   - $t$-statistic verification must exceed $+2.58$ for directional expectancy claims.
3. **Confidence Intervals**:
   - 95% and 99% bootstrap confidence intervals must be calculated for trade expectancy ($\mathbb{E}[R]$), Profit Factor, and Sharpe Ratio. Lower confidence bounds must remain strictly positive.
4. **Expected Value ($\mathbb{E}[R]$)**:
   - Expectancy must account for full transaction costs: spread, broker commissions, swap rates, tick slippage, and latency friction.
5. **Drawdown & Max Adverse Excursion (MAE)**:
   - Maximum portfolio drawdown must not exceed constitutional safety limits ($\le 3.0\%$). MAE distribution must demonstrate tight containment without fat-tail catastrophe risk.
6. **Walk-Forward Out-of-Sample Validation**:
   - Rolling out-of-sample testing must prove performance stability across unseen market data windows. Parameter degradation from in-sample to out-of-sample must not exceed 20%.
7. **False Discovery Rate (FDR) Protection**:
   - When evaluating multi-hypothesis families or parameter spaces, Benjamini-Hochberg or Bonferroni adjustments must be applied to prevent false discoveries from multiple hypothesis testing.
8. **Reproducibility Verification**:
   - Replaying identical input tick data through historical experiment parameters must yield identical statistical summary vectors.

---

## SECTION 6: RESEARCH EVIDENCE LEVELS

Project GOAT establishes a formal 6-tier Evidence Hierarchy. A hypothesis advances through tiers strictly upon satisfying objective criteria:

```
[ Level 0: Idea ]
       │
       ▼
[ Level 1: Observed ]
       │
       ▼
[ Level 2: Tested ]
       │
       ▼
[ Level 3: Validated ]
       │
       ▼
[ Level 4: Live Validated ]
       │
       ▼
[ Level 5: Institutionally Approved ]
```

### Level Definitions & Graduation Requirements:
- **Level 0 (Idea)**: Initial theoretical hypothesis formulated in registry (`HYP_`). No empirical testing performed.
- **Level 1 (Observed)**: Market structural pattern observed and fingerprinted in tick data (`OBS_`). Qualitative evidence collected.
- **Level 2 (Tested)**: Initial backtest simulation executed ($N \ge 100$). Preliminary positive expectancy demonstrated.
- **Level 3 (Validated)**: Full scientific qualification completed ($N \ge 500$, $p < 0.01$, walk-forward out-of-sample stability verified, tail risk contained).
- **Level 4 (Live Validated)**: Micro-lot live production execution completed ($N \ge 100$ live trades) on Deriv server, demonstrating live expectancy within $1.0\sigma$ of historical model prediction.
- **Level 5 (Institutionally Approved)**: Final sign-off by Quantitative Research Board. Edge promoted to active live production sizing pipeline under authorized Risk Profile.

---

## SECTION 7: EDGE PROMOTION RULES

An edge advances from initial research to live production strictly via the following non-bypassable 6-step promotion sequence:

```
1. Research Formulation
          │
          ▼
2. Simulation & Friction Testing
          │
          ▼
3. Walk-Forward Out-of-Sample Validation
          │
          ▼
4. Risk Qualification & MER Sizing Assessment
          │
          ▼
5. Controlled Live Micro-Validation (N >= 100)
          │
          ▼
6. Production Deployment Authorization
```

### Promotion Governance Rules:
- **Zero Shortcut Execution**: No trade setup may bypass any stage in this sequence.
- **Non-Discretionary Gate Checks**: Advancement requires automated certification signatures at every gate.
- **Capital Alignment**: Step 4 must verify Minimum Executable Risk (MER) and match the trade against an active, authorized Risk Profile before step 5 can commence.

---

## SECTION 8: EDGE RETIREMENT RULES

In accordance with **Constitutional Amendment No. 001 (Edge Retirement & Scientific Revalidation)**:

1. **Every Edge is Provisional**: Live evidence is the supreme authority. No past backtest or historical track record overrides live performance degradation.
2. **Objective Retirement Triggers**: An edge is automatically demoted from production status if any of the following occur:
   - Live trade expectancy diverges from historical baseline by $> 2.0\sigma$.
   - Statistical confidence interval degrades ($p \ge 0.05$).
   - Sustained regime shift invalidates underlying market-structural assumptions.
   - Real-world broker execution friction (spread/slippage) reduces net expectancy below zero.
3. **No Ad-Hoc Saving of Edge**: Modifying parameters, expanding stop losses, doubling lot sizes, or adding discretionary filters to "save" a failing edge is strictly illegal.
4. **Immediate Re-classification**: Failing edges are demoted immediately to `RESEARCH` status and quarantine.
5. **Permanent Append-Only Archive**: Retired edges are stored permanently in the research archive (`ARC_`). They are never erased.
6. **Revalidation Requirements**: A retired edge may return to active deployment ONLY by completing the entire 6-stage scientific promotion sequence from scratch.

---

## SECTION 9: CAPITAL AWARENESS

In accordance with **Constitutional Amendment No. 002 (Capital-Aware Risk Management & Minimum Executable Risk Principle)**:

1. **Dual Qualification Mandate**: Every trade execution decision must simultaneously satisfy both Scientific Qualification and Capital Affordability.
2. **Minimum Executable Risk (MER)**: MER is the minimum monetary loss produced by the broker's minimum contract when the scientific stop loss is reached:
   $$\text{MER} = \text{min\_lot} \times \text{contract\_size} \times |\text{entry\_price} - \text{stop\_loss\_price}| \times \text{tick\_value\_factor}$$
3. **Independence of Scientific Edge**: Account balance affects **execution sizing and eligibility**, NEVER scientific edge qualification or stop loss placement. Altering stop loss to fit small capital is illegal.
4. **Modular Risk Profiles**: GOAT supports Conservative, Balanced, Aggressive Growth, and Custom profiles.
5. **Aggressive Growth Profile Governance**: Officially recognized for small retail account growth ($10 - $500). Tolerates higher percentage risk when MER dominates theoretical percentage caps, provided absolute monetary loss is survivable.
6. **Mandatory Pre-Execution Transparency**: Before order execution, GOAT must display and log:
   - Monetary Risk ($)
   - Monetary Reward ($)
   - Actual Risk Percentage (%)
   - Risk/Reward Ratio (R:R)
   - Minimum Executable Risk ($)

---

## SECTION 10: RESEARCH ETHICS

Project GOAT enforces an uncompromising scientific code of ethics. The following practices are strictly illegal and trigger immediate system quarantine:

1. **No Curve Fitting**: Fitting parameters to random noise or over-optimizing historical indicators without structural rationale.
2. **No Cherry-Picking**: Selecting favorable time windows or excluding losing trades from reporting.
3. **No Ignoring Failed Experiments**: Every failed backtest, discarded hypothesis, and losing trade must be recorded in full.
4. **No Deleting Bad Results**: Append-only storage forbids removing negative data.
5. **No Selective Reporting**: Omitting drawdown statistics, adverse excursion, or execution friction from research reports.
6. **No Post-Hoc Parameter Manipulation**: Tweaking parameters after viewing test outcomes without restarting full out-of-sample validation.
7. **No Hidden Optimization**: Running unrecorded grid searches or genetic algorithm optimizations.
8. **No Confirmation Bias**: Seeking data that confirms a hypothesis while ignoring counter-evidence.
9. **No Survivorship Bias**: Evaluating strategies on survivor assets while ignoring delisted or changed instruments.

---

## SECTION 11: DOCUMENTATION REQUIREMENTS

Every completed quantitative experiment must generate an immutable, standardized Markdown documentation package containing:

1. **Experiment Report (`EXR_`)**: Full technical summary of experiment objectives, execution details, and outcome state.
2. **Evidence Summary (`EVS_`)**: Dataset fingerprints, sample size breakdown, and regime distribution matrices.
3. **Statistical Summary (`STS_`)**: Expectancy ($\mathbb{E}[R]$), $p$-values, $t$-statistics, confidence intervals, drawdown curves, and MAE distributions.
4. **Replay Manifest (`RPM_`)**: Step-by-step canonical log of replay digests enabling 100% verification.
5. **Research Notes (`RSN_`)**: Quantitative observations, anomaly logs, and structural insights recorded during execution.
6. **Executive Summary (`EXS_`)**: Concise high-level overview detailing key takeaways and business impact.
7. **Approval Decision Certificate (`ADC_`)**: Formal governance decision (`QUALIFIED`, `REJECTED`, `RETIRED`) signed by reviewing authorities.

---

## SECTION 12: VERSION 0.9 GOVERNANCE

Governance responsibilities during Version 0.9 execution are strictly partitioned across six authority roles:

1. **Chief Quantitative Research Director**: Overall authority over scientific roadmap, hypothesis prioritization, and research direction.
2. **Scientific Reviewer**: Responsible for auditing mathematical soundness, statistical validity, and hypothesis formulations.
3. **Risk Reviewer**: Responsible for enforcing MER bounds, Risk Profile compliance, drawdown caps, and capital awareness rules.
4. **Architecture Reviewer**: Responsible for auditing system determinism, SHA-256 state hashing, zero-leakage boundaries, and module interfaces.
5. **Release Reviewer**: Responsible for certifying step completion reports, regression suite passes, public API exports, and version freeze criteria.
6. **Independent Auditor**: External auditing authority conducting unbiased reviews of architecture, code quality, and trading safety.

---

## SECTION 13: FUTURE COMPATIBILITY

While Project GOAT Version 0.9 operates exclusively on **Deriv Synthetic Indices**, this Scientific Research Protocol is designed for long-term multi-venue expansion.

The research methodology, evidence hierarchy, statistical qualification standards, and capital awareness framework defined in this document shall remain **100% valid and immutable** when GOAT expands to future stages:
- **Stage 2**: Weltrade CFD Execution
- **Stage 3**: Traditional Forex & Institutional FX
- **Stage 4**: Multi-Asset Classes (Commodities, Cryptocurrencies, Global Equities, Futures)

The underlying scientific method never changes regardless of broker, venue, or financial instrument.

---

## SECTION 14: PROTOCOL AMENDMENT PROCESS

This protocol is a frozen constitutional document. Future modifications must follow the formal Constitutional Amendment Process:

1. **Proposal**: A formal Amendment Proposal document detailing the rationale, proposed section edits, and architectural impact must be submitted.
2. **Scientific Review**: The Quantitative Research Board conducts a mandatory review of statistical and scientific implications.
3. **Impact Assessment**: System architects verify that zero backward compatibility or replay integrity issues are introduced.
4. **Board Approval**: Unanimous formal sign-off by the Research Board and Chief Scientific Officer is required.
5. **Enactment & Freeze**: The amendment is permanently inserted into the protocol, a dedicated Amendment Report is generated, and the document is re-frozen.

---

## SECTION 15: FINAL SCIENTIFIC DECLARATION

======================================================================  
**PROJECT GOAT SCIENTIFIC DECLARATION**  

> **Project GOAT is a scientific research institution first and a quantitative trading system second.**  
>  
> **Live production trading exists solely as an empirical measurement mechanism to test, validate, or falsify quantitative market hypotheses under real-world physical frictions.**  
>  
> **Profits are not the primary goal; profits are the empirical byproduct of validated scientific truth.**  
======================================================================  
