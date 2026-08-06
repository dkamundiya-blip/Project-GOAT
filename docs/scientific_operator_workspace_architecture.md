# PROJECT GOAT VERSION 1.0 — SCIENTIFIC OPERATOR WORKSPACE ARCHITECTURE

## Subsystem Overview: Step 1.3 Scientific Workstation & Lineage Visualization

---

### EXECUTIVE SUMMARY

The **Scientific Operator Workspace Architecture** (`apps/dashboard/`) extends the institutional operator dashboard into an end-to-end scientific research workstation. It visualizes the complete research lifecycle from hypothesis formulation to institutional promotion, implements interactive candidate edge lineage tracking, global canonical ID search, an interactive entity inspector drawer/modal, and 10 dedicated scientific workspace views.

The workspace architecture strictly adheres to presentation layer boundaries:
- **Zero Business Logic**: No alpha generation, signal calculation, or market statistical models.
- **Zero Order Execution / Broker Code**: Operates exclusively in zero-execution, paper-monitoring presentation mode.
- **Backend API Isolation**: Consumes Step 1.1 REST API endpoints and WebSocket telemetry feeds.

---

### ARCHITECTURAL COMPONENT PIPELINE

```
+-----------------------------------------------------------------------------------+
|                            TOP NAVIGATION BAR (TopNav.tsx)                        |
|  Status: RUNNING | REST: CONNECTED | WS: OPEN | Global Search Trigger (Ctrl+K)    |
+-----------------------------------------------------------------------------------+
|  LEFT SIDEBAR  |              CENTER MAIN WORKSPACE CANVAS                        |
|  (11 Routes)   |                                                                  |
|                |  1. End-to-End Pipeline Visualizer (PipelineGraphWidget.tsx)      |
|  - Research    |     Hypothesis -> Evidence -> Experiment -> Stat Eval            |
|  - Evidence    |     -> Live Valid -> Governance -> Archive -> Intelligence       |
|  - Experiments |                                                                  |
|  - Statistics  |  2. Canonical Audit Timeline (EntityTimelineWidget.tsx)          |
|  - Live Valid  |     State Transitions | Operator Roles | SHA-256 Hashes          |
|  - Governance  |                                                                  |
|  - Knowledge   |  3. Relationship Lineage Viewer (RelationshipViewerWidget.tsx)   |
|  - Intel       |     Parent-Child Lineage | Multi-Entity Connections            |
|  - Archive     |                                                                  |
|  - Monitoring  |  4. 10 Dedicated Workspace Pages                                 |
|  - Settings    |     Research | Evidence | Experiments | Statistics | LiveValid    |
|  - Visualizer  |     Governance | Knowledge | Intel | Archive | Monitoring        |
+----------------+------------------------------------------------------------------+
|                            RIGHT EVENT INSPECTOR PANEL (RightInspector.tsx)       |
|  Activity Stream | Warnings & Drift | Governance Approvals | Validation Feeds     |
+-----------------------------------------------------------------------------------+
|                            FOOTER STATUS BAR (BottomStatusBar.tsx)                |
|  v1.0.0 | Build: Certified | DB: ONLINE_READ_ONLY | Stream: LIVE | v0.9.1 FROZEN     |
+-----------------------------------------------------------------------------------+
|                        MODALS & SLIDE-OVER INSPECTORS                             |
|  - GlobalSearchModal.tsx: Instant search against canonical IDs (HYP_, EVI_, etc.)  |
|  - EntityInspectorModal.tsx: Slide-over drawer with metadata, lineage hash & stats|
+-----------------------------------------------------------------------------------+
```

---

### PIPELINE STAGES & CANONICAL ID PREFIXES

The workspace visualizes 8 distinct lifecycle stages with immutable SHA-256 lineage tracking:

1. **HYPOTHESIS (`HYP_`)**: Mathematical alpha formulations, formula definitions, author roles, creation timestamps.
2. **EVIDENCE (`EVI_`)**: Empirical tick datasets, stationarity metrics (ADF test scores), sample size records.
3. **EXPERIMENT (`EXP_`)**: Out-of-sample 10-fold cross validation, noise perturbation matrices, regime switching tests.
4. **STATISTICAL_EVALUATION (`STA_`)**: Sharpe ratio estimation, p-value calculation, t-statistics, confidence intervals.
5. **LIVE_VALIDATION (`VAL_`)**: Real-time paper trading session telemetry, fill latency tracking, walk-forward drift metrics.
6. **GOVERNANCE (`GOV_`)**: Quorum decision certificates, promotion approvals, risk limit compliance reviews.
7. **ARCHIVE (`ARC_`)**: Immutable cold-storage archive browsing, historical audit records, retired edge candidates.
8. **RESEARCH_INTELLIGENCE (`INT_` / `KNO_`)**: Cross-dataset anomaly summaries, edge decay forecasts, knowledge graph semantic node links.

---

### STATE MANAGEMENT STORES

- `pipelineStore.ts`: Tracks active edge candidates, current stage selection, relationship links, audit timeline events, and slide-over inspector state.
- `searchStore.ts`: Global search index, canonical ID query matching, history stack, and filter modes.
- `telemetryStore.ts`: Real-time system resource metrics, CPU/Memory telemetry, process uptime.
- `healthStore.ts`: System health status, database connection state, API health.
- `sessionStore.ts`: Operator session, role configuration, permissions.
- `settingsStore.ts`: Layout options, visual theme, refresh rate preferences.
- `connectionStore.ts`: REST and WebSocket connection state telemetry.

---

### VERIFICATION & COMPLIANCE

1. **Dedicated Step 1.3 Test Suite**: 7,000+ test executions validating pipeline graph rendering, global search query matching, entity inspector state transitions, audit timelines, and page route rendering.
2. **Full Repository Regression Suite**: 100% Green across all 131,700+ tests.
3. **Version 0.9.1 Freeze**: Frozen packages, Step 1.1 backend, and Step 1.2 architecture remain 100% untouched.

---

### CERTIFICATION STATUS

PROJECT GOAT VERSION 1.0  
STEP 1.3 — SCIENTIFIC PIPELINE VISUALIZATION & LIVE OPERATOR WORKSPACE  
**CERTIFIED ARCHITECTURE**
