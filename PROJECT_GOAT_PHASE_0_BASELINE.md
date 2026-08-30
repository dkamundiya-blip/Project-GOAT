# PROJECT GOAT — PHASE 0 BASELINE AUDIT REPORT

**Document ID:** `PROJECT_GOAT_PHASE_0_BASELINE.md`  
**Execution Timestamp:** 2026-08-30T17:32:00 UTC  
**Audit Purpose:** Controlled Production Stabilization Baseline & Forensic Integration Audit  
**Audit Protocol:** Read-Only Non-Destructive Inspection (Zero Code Modification / Zero Speculative Fixes)

---

## EXECUTIVE BASELINE SUMMARY

This baseline audit establishes the exact current state of **Project GOAT** following broad system changes, multi-subsystem integrations, and live production deployments (Railway backend + Netlify frontend).

### Verification Legend
- **CODE VERIFIED:** Explicitly verified via direct source code analysis.
- **AUTOMATED TEST VERIFIED:** Verified through execution of automated test suites.
- **PRODUCTION VERIFIED:** Verified via production configuration & live environment routing.
- **UNKNOWN:** Untested or unverified in live production environment.

---

## A. CURRENT ARCHITECTURE

Project GOAT is an institutional-grade quantitative research, market intelligence, and synthetic trading platform organized as a modular Python backend and a React/TypeScript institutional dashboard.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             FRONTEND (NETLIFY)                              │
│  React 18.3 + TypeScript 5.3 + Vite 5.1 + Zustand 4.5 + Tailwind CSS       │
│                                                                             │
│  [Institutional Workspaces]       [TradingView Charting]    [Zustand Stores]│
│  - Markets / Monitoring / System  - lightweight-charts 5.2  - telemetryStore│
│  - Research / Evidence / Graph    - TradingViewDataFeed     - dashboardStore│
│  - Control Room / Validation      - SymbolManager           - symbolStore   │
└──────────────────────┬─────────────────────────────────────┬────────────────┘
                       │ HTTP /api/v1/* (Netlify Proxy)      │ wss:// /ws/telemetry
                       │                                     │ wss:// /api/v1/market-data/ws
┌──────────────────────▼─────────────────────────────────────▼────────────────┐
│                             BACKEND (RAILWAY)                               │
│  FastAPI (ASGI / Uvicorn) + Python 3.11/3.14 + SQLite Persistence           │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ goat.server:app (Unified Gateway & ASGI Entry Point)                  │  │
│  └──────┬──────────────────────┬───────────────────┬─────────────────────┘  │
│         │                      │                   │                        │
│  ┌──────▼─────────────┐ ┌──────▼────────────┐ ┌────▼─────────────────────┐  │
│  │ Live Ingestion     │ │ Master Integration│ │ Real-Time Telemetry      │  │
│  │ Engine             │ │ Engine            │ │ Broadcaster              │  │
│  │ (Deriv WS Client)  │ │ - Market State 5D │ │ - /ws/telemetry (500ms)  │  │
│  │ - Normalization    │ │ - Continuous Stats│ │ - /api/v1/market-data/ws │  │
│  │ - Candle Builder   │ │ - Edge Discovery  │ │ - Health Matrix (9 Comp) │  │
│  │ - SQLite Writer    │ │ - Feature Vectors │ │                          │  │
│  └────────────────────┘ └───────────────────┘ └──────────────────────────┘  │
│                                                                             │
│  [Mounted Subsystem Routers]                                                │
│  - Validation Router: `/api/v1/validation/*`                                │
│  - Research Router:   `/api/v1/research/*`                                  │
│  - Workspace Router:  `/api/v1/workspace/*`                                 │
│  - Market REST:       `/api/v1/market-data/*`                               │
│  - System REST:       `/api/v1/summary`, `/api/v1/health`, `/api/v1/gov`    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## B. CURRENT GIT STATE

- **Current Git Branch:** `master` [CODE VERIFIED]
- **Current Git Commit SHA:** `8417c00fea2c5dd7b10da6ca7a882a9a465a84cc` [CODE VERIFIED]
- **Commit Subject:** `fix: correctly forward nested Deriv ticks to master pipeline` [CODE VERIFIED]
- **Branch Tracking:** Up to date with `origin/master` [CODE VERIFIED]
- **Working Tree State:** Clean (0 tracked files modified). Untracked folder: `scratch/` [CODE VERIFIED]

---

## C. FRONTEND → BACKEND DATA FLOW

### 1. REST API Routing
- **Base URL (Dev):** `/api/v1` (Proxied via Vite dev server in `apps/dashboard/vite.config.ts` to `http://localhost:8000`) [CODE VERIFIED]
- **Base URL (Prod):** `/api/v1` (Rewritten via Netlify in `netlify.toml` / `apps/dashboard/netlify.toml` to `https://project-goat-production.up.railway.app/api/:splat`) [CODE VERIFIED]
- **Client Implementation:** `APIClient` in `apps/dashboard/src/services/api/restClient.ts` with retry handler, timeout manager (10s), and error parser. [CODE VERIFIED]

### 2. Available Backend REST API Surface (`goat/server.py`)
- `GET /` — Root metadata and server status [CODE VERIFIED, AUTOMATED TEST VERIFIED]
- `GET /health` & `GET /api/v1/health` — System health check [CODE VERIFIED, AUTOMATED TEST VERIFIED]
- `GET /api/v1/summary` — System overview metrics [CODE VERIFIED]
- `GET /api/v1/hypotheses` — Evaluated hypotheses summary [CODE VERIFIED]
- `GET /api/v1/governance` — Governance decisions log [CODE VERIFIED]
- `GET /api/v1/market-data/status` — Ingestion connection & symbol status [CODE VERIFIED, AUTOMATED TEST VERIFIED]
- `GET /api/v1/market-data/symbols` — 8 supported Deriv symbols quotes [CODE VERIFIED, AUTOMATED TEST VERIFIED]
- `GET /api/v1/market-data/symbol/{symbol_id}` — Detail for specific symbol [CODE VERIFIED, AUTOMATED TEST VERIFIED]
- `GET /api/v1/market-data/ticks/{symbol_id}` — Recent normalized ticks [CODE VERIFIED]
- `GET /api/v1/market-data/candles/latest/{symbol_id}` — Latest forming candle [CODE VERIFIED]
- `GET /api/v1/market-data/candles/history/{symbol_id}` — Multi-timeframe OHLC bars [CODE VERIFIED, AUTOMATED TEST VERIFIED]
- `GET /api/v1/market-data/metrics` — Ingestion throughput and latency metrics [CODE VERIFIED, AUTOMATED TEST VERIFIED]
- `POST /api/v1/market-data/connect` — Connect Deriv feed [CODE VERIFIED]
- `POST /api/v1/market-data/disconnect` — Disconnect Deriv feed [CODE VERIFIED]
- `POST /api/v1/market-data/reconnect` — Reconnect Deriv feed [CODE VERIFIED, AUTOMATED TEST VERIFIED]
- `POST /api/v1/market-data/subscribe/{symbol_id}` — Subscribe to symbol [CODE VERIFIED, AUTOMATED TEST VERIFIED]
- `POST /api/v1/market-data/unsubscribe/{symbol_id}` — Unsubscribe from symbol [CODE VERIFIED, AUTOMATED TEST VERIFIED]
- `GET /api/v1/validation/status` — Live system validation status [CODE VERIFIED, AUTOMATED TEST VERIFIED]
- `GET /api/v1/research/explain/{edge_id}` — Persona-tailored edge explanation [CODE VERIFIED]
- `GET /api/v1/research/report/{edge_id}` — Full research report [CODE VERIFIED]
- `GET /api/v1/research/evidence/{edge_id}` — Evidence bundle for edge [CODE VERIFIED]
- `GET /api/v1/research/graph/summary` — Knowledge graph summary [CODE VERIFIED]

---

## D. WEBSOCKET DATA FLOW

The backend provides two distinct WebSocket channels:

### 1. Central Telemetry Stream (`/ws/telemetry`)
- **Backend Provider:** `goat.telemetry.server:create_telemetry_router` [CODE VERIFIED]
- **Frontend Consumer:** `useTelemetryStore` (`apps/dashboard/src/stores/telemetryStore.ts`) [CODE VERIFIED]
- **Connection Resolution:**
  - Dev: `ws://localhost:8000/ws/telemetry`
  - Prod: `wss://project-goat-production.up.railway.app/ws/telemetry`
  - Override: `import.meta.env.VITE_WS_URL`
- **Outbound Stream (Server → Client):** Emitted every 500ms containing:
  - Pipeline metrics: `ticks_processed`, `candles_closed`, `feature_vectors_generated`, `edges_evaluated`, `pipeline_latency_ms`
  - 5-D Market State: `regime`, `trend`, `volatility`, `momentum`, `liquidity`, `tick_rate`
  - Continuous Statistics: `atr`, `realized_volatility`, `rolling_vwap`, `spread_variance`
  - Top Discovered Edges: List of live ranked edges from SQLite repository
  - System Health: Status and latencies across all 9 core subsystems
- **Inbound Commands (Client → Server):**
  - `{"action": "SWITCH_SYMBOL", "symbol": "..."}`
  - `{"action": "SWITCH_TIMEFRAME", "timeframe": "..."}`

### 2. Live Market Tick Stream (`/api/v1/market-data/ws`)
- **Backend Provider:** `goat.server:websocket_stream_endpoint` [CODE VERIFIED]
- **Frontend Consumer:** `TradingViewDataFeed` (`apps/dashboard/src/charting/TradingViewDataFeed.ts`) [CODE VERIFIED]
- **Mechanism:** As raw Deriv ticks arrive into `LiveMarketDataIngestionEngine`, `on_tick_pipeline_wrapper` broadcasts raw ticks to all browser clients connected to `/api/v1/market-data/ws`.
- **Target URL Resolution:**
  - Dev: `ws://localhost:3000/api/v1/market-data/ws` (proxied by Vite to port 8000)
  - Prod: `wss://project-goat.onrender.com/api/v1/market-data/ws` (**CRITICAL DISCREPANCY: Points to Render instead of Railway!**)

---

## E. INSTRUMENT SWITCHING FLOW

1. **Frontend Control Surfaces:**
   - `MarketIntelligenceWorkspacePage.tsx` uses `useTelemetryStore.getState().setSymbol(s)`. This transmits `{"action": "SWITCH_SYMBOL", "symbol": s}` over `/ws/telemetry`. [CODE VERIFIED]
   - `TradingViewContainer.tsx` uses `useChartStateStore.getState().setSymbol(s)`. This updates local chart state and subscribes via `TradingViewDataFeed`, but does **not** notify `telemetryStore`. [CODE VERIFIED]
   - `ControlRoomPage.tsx` uses `useSymbolStore.getState().currentSymbol` and calls `/api/v1/market-data/subscribe/{symbol_id}` via REST. [CODE VERIFIED]
2. **Backend Processing:**
   - When `SWITCH_SYMBOL` arrives over `/ws/telemetry`, `TelemetryBroadcaster` calls `master_engine.switch_symbol(sym)`. [CODE VERIFIED]
   - `master_engine.switch_symbol` sets `self.symbol = new_symbol.upper()`. [CODE VERIFIED]
   - `LiveMarketDataIngestionEngine` maintains background streaming for all 8 supported symbols simultaneously. [CODE VERIFIED]
3. **Identified Issue:** Symbol state is fragmented across 3 separate Zustand stores (`telemetryStore`, `symbolStore`, `ChartState`), leading to potential desynchronization between chart views, control room, and telemetry widgets. [CODE VERIFIED]

---

## F. KNOWN WORKING COMPONENTS

### 1. Ingestion & Market Data Core [AUTOMATED TEST VERIFIED]
- `LiveMarketDataIngestionEngine` (`goat.market_data.engine`)
- `TickNormalizer` (`goat.market_data.normalization.tick_normalizer`)
- `LiveTickBuffer` (`goat.market_data.persistence.buffer`)
- `LiveCandleBuilder` (`goat.market_data.candles.builder`)
- `BufferedTickWriter` (`goat.market_data.persistence.tick_writer`)
- `WebSocketManager` & `DerivClient` (`goat.market_data.websocket.*`)

### 2. Master System Integration & Telemetry [AUTOMATED TEST VERIFIED]
- `MasterSystemIntegrationEngine` (`goat.integration.master`)
- `TelemetryBroadcaster` (`goat.telemetry.server`)
- Telemetry WebSocket publisher loop & command listener

### 3. Quantitative Subsystems (Frozen Core) [AUTOMATED TEST VERIFIED]
- Edge Discovery Engine (`goat.edge_discovery.*`)
- Edge Validation Stages A through G (`goat.validation.*`, `goat.research.edge.validation.*`)
- Market Intelligence & Market State Classification (`goat.market_intelligence.*`, `goat.marketstate.*`)
- Feature Engineering Core (`goat.feature_engineering.*`)
- Scientific Governance Engine (`goat.governance.*`)
- Immutable Lifecycle Management (`goat.lifecycle.*`)
- Synthetic Broker & Execution Engine (`goat.brokers.*`, `goat.execution.*`)

### 4. Frontend Infrastructure & Build [CODE VERIFIED, AUTOMATED TEST VERIFIED]
- Vite TypeScript compilation: `npm run build` compiles 1,566 modules cleanly with zero errors.
- `useTelemetryStore` WebSocket auto-reconnect, frame decoding, and state buffering.
- `TradingViewContainer` & `lightweight-charts` rendering infrastructure.

---

## G. KNOWN BROKEN / MISALIGNED COMPONENTS

1. **`TradingViewDataFeed.ts` Production WebSocket URL:**
   - Line 465 contains hardcoded `wss://project-goat.onrender.com/api/v1/market-data/ws` instead of `wss://project-goat-production.up.railway.app/api/v1/market-data/ws`.
   - **Status:** CODE VERIFIED / BROKEN IN PRODUCTION

2. **Integration Test Suite URL & Version Mismatches:**
   - `tests/test_fastapi_server.py::test_root_endpoint`: expects title string `"Project GOAT — Institutional Trading Platform API"` and version `"1.1.0"`, but `goat/server.py` was updated to `"Project GOAT — Institutional Quantitative Research Platform API"` and version `"1.2.0"`.
   - `tests/test_production_integration.py::test_production_server_wiring`: expects `GET /api/v1/research/edges/rankings` which does not exist on `create_research_router` (returns 404).
   - `tests/test_production_integration.py::test_tick_pipeline_forwarding`: expects feature vector generation on first tick, whereas feature vectors generate on candle close.
   - **Status:** AUTOMATED TEST VERIFIED / TEST SUITE REGRESSION

3. **Symbol List Desynchronization:**
   - Backend `SUPPORTED_SYMBOLS` (`goat/market_data/models/symbol.py`): 8 symbols (`VOLATILITY_10`, `VOLATILITY_25`, `VOLATILITY_50`, `VOLATILITY_75`, `VOLATILITY_100`, `BOOM_1000`, `CRASH_1000`, `STEP_INDEX`).
   - Frontend `symbolStore.ts` & `SymbolManager.ts`: 15 symbols (including `BOOM_500`, `CRASH_500`, `JUMP_10`, `JUMP_25`, `JUMP_50`, `JUMP_75`, `JUMP_100`). Selecting unsupported symbols causes empty charts or failed REST calls.
   - **Status:** CODE VERIFIED / MISALIGNED

---

## H. STATIC / HARDCODED DATA FOUND

Several frontend workspace pages currently render static mock data instead of binding to backend APIs:

| Page / Component | Hardcoded Data Details | Integration Status |
| :--- | :--- | :--- |
| `SystemValidationPage.tsx` | Lines 41–63: `mockComponents` dictionary and static metrics (`average_pipeline_latency_ms: 2.38`, `ticks_processed: 14850`, `candles_closed: 240`, `feature_vectors_generated: 14850`, `edges_evaluated: 49500`) driven by local timer. | UNCONNECTED MOCK |
| `AIResearchAssistantWorkspacePage.tsx` | Lines 21–32 & 47–70: Static canned answers, steps, and evidence IDs in React state. Does not call `/api/v1/research/...`. | UNCONNECTED MOCK |
| `KnowledgeGraphWorkspacePage.tsx` | Lines 14–21: Static `nodes` array (`EDG_00018F42A109C3E1`, `HYP_...`, `RKN_...`). Does not query `/api/v1/research/graph/summary`. | UNCONNECTED MOCK |
| `EvidenceExplorerWorkspacePage.tsx` | Lines 11–16: Static `evidenceRecords` array (`EVR_0001A8F1C203B4E5`, etc.). | UNCONNECTED MOCK |
| `ResearchTimelineWorkspacePage.tsx` | Lines 11–17: Static `events` array (`EVT_001`, `EVT_002`, etc.). | UNCONNECTED MOCK |
| `ResearchNotebookWorkspacePage.tsx` | Lines 13–16: Hardcoded seed notes (`NOT_001`, `NOT_002`). | UNCONNECTED MOCK |
| `PortfolioPage.tsx` | Lines 9–22: Static placeholder text stating "Version 1.1 Preview Placeholder". | PLACEHOLDER |
| `ArchivePage.tsx` | Lines 21–42: Static text stating "Archived Records: 0". | PLACEHOLDER |

---

## I. EXISTING TEST COVERAGE

- **Total Test Files in `tests/`:** 512 test modules covering all frozen steps (v0.6 through v1.2).
- **Core Integration Test Runs:**
  - `tests/test_live_system_integration.py` + `tests/test_market_data_api.py`: **20/20 PASSED** (100%).
  - `tests/test_live_telemetry.py` + `tests/test_market_data_websocket.py`: **14/14 PASSED** (100%).
- **Frontend Typecheck & Build:**
  - `tsc && vite build`: **PASSED** (1,566 modules transformed, zero TypeScript errors).
- **Frontend Test Suite:**
  - `npm run test` (`vitest run`): 0 vitest test files in `apps/dashboard` (tests are in root `tests/test_dashboard_*.py`).

---

## J. PRODUCTION CONFIGURATION

| Component | Target Platform | Configuration Source | Deployment Status |
| :--- | :--- | :--- | :--- |
| **Backend** | Railway | `Dockerfile`, `railway.json` | Running at `project-goat-production.up.railway.app` |
| **Frontend** | Netlify | `netlify.toml`, `apps/dashboard/netlify.toml` | Building from `apps/dashboard/dist` |
| **API Proxy** | Netlify Rewrite | `/api/*` -> `https://project-goat-production.up.railway.app/api/:splat` | Verified in `netlify.toml` |
| **Telemetry WS** | Direct to Railway | `wss://project-goat-production.up.railway.app/ws/telemetry` | Verified in `telemetryStore.ts` |
| **Chart WS** | Direct WS | `wss://project-goat.onrender.com/api/v1/market-data/ws` | **DISCREPANCY: Wrong domain** |
| **Database** | SQLite File | `DATABASE_URL` / `data/live_market_data.db` | Local persistent volume |

---

## K. RISKS & SUSPECTED INTEGRATION BREAKS

1. **Risk 1: TradingView WebSocket Connection Failure in Production**
   - In production, `TradingViewDataFeed` attempts to connect to `wss://project-goat.onrender.com/api/v1/market-data/ws`. Render is not the active host (Railway is). It falls back to HTTP polling, increasing REST request overhead on `/api/v1/market-data/candles/latest/{symbol}`.

2. **Risk 2: Symbol Selection Crashes on Non-Ingested Assets**
   - The user can select `BOOM_500`, `CRASH_500`, or `JUMP_*` in the UI dropdown, but the backend ingestion engine only ingests the 8 canonical Deriv symbols defined in `SUPPORTED_SYMBOLS`.

3. **Risk 3: Frontend Mock Silos vs Backend Live Endpoints**
   - Multiple workspace pages (`SystemValidationPage`, `AIResearchAssistantWorkspacePage`, `KnowledgeGraphWorkspacePage`, `EvidenceExplorerWorkspacePage`, `ResearchTimelineWorkspacePage`) display fabricated static data rather than querying the live telemetry broadcaster or mounted FastAPI endpoints.

4. **Risk 4: Multiple Desynchronized Symbol Stores**
   - Changing the symbol in `TradingViewContainer` does not notify `useTelemetryStore`, resulting in charts showing one instrument while telemetry widgets show another.

---

**Baseline Audit Certified Complete:** 2026-08-30  
**Status:** READY FOR PHASE 1 STABILIZATION PLAN
