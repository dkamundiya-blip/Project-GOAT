# PROJECT GOAT — PHASE 1: PRODUCTION WEBSOCKET FORENSIC AUDIT REPORT

**Document ID:** `PROJECT_GOAT_PHASE_1_WEBSOCKET_FORENSIC.md`  
**Execution Timestamp:** 2026-08-30T17:38:00 UTC  
**Audit Purpose:** Deep Forensic Diagnosis of Production WebSockets, Data Routing, Symbol Pathways, and Fallback Masks  
**Audit Constraints:** Zero Code Modifications / Zero Refactoring / Pure Diagnostic Verification

---

## EXECUTIVE FORENSIC SUMMARY

Project GOAT operates **two independent WebSocket architectures**:
1. **Live Market Data WebSocket (`/api/v1/market-data/ws`)**: Streams real-time raw and normalized Deriv ticks directly to browser charting instances (`TradingViewDataFeed`).
2. **Platform Telemetry WebSocket (`/ws/telemetry`)**: Streams comprehensive 5-D market states, pipeline latency, engine metrics, discovered edges, and subsystem health matrices every 500ms to Zustand (`useTelemetryStore`).

This forensic audit identifies why live market data charts fail to establish direct WebSocket connections in production, why fallback HTTP polling masks the failure, how unsupported synthetic symbols behave across the system, and why symbol state is fragmented across multiple stores.

---

## 1. MARKET DATA WEBSOCKET FLOW

```
[User / Chart UI]
       │
       ▼
[TradingViewContainer.tsx / Symbol Selector]
       │
       ▼
[ChartStateStore (`activeSymbol`, `activeTimeframe`)]
       │
       ▼
[TradingViewDataFeed.ts (`subscribeBars`)]
       │
       ├───────────────────────────────────────────────────────┐
       ▼ (Production: Non-localhost)                           ▼ (Localhost Dev)
[wss://project-goat.onrender.com/api/v1/market-data/ws]   [ws://localhost:3000/api/v1/market-data/ws]
       │ (FAILED / CONNECTION REFUSED / TIMEOUT)               │ (Proxied by Vite to port 8000)
       ▼                                                       ▼
[Trigger `onerror` / `onclose`]                           [FastAPI `/api/v1/market-data/ws`]
       │                                                       │
       ▼                                                       ▼
[startPollingFallback() activated]                        [connected_websockets.add(ws)]
       │                                                       │
       ▼                                                       ▼
[setInterval 2000ms: GET /api/v1/market-data/candles/...] [on_tick_pipeline_wrapper broadcast]
       │                                                       │
       ▼                                                       ▼
[Netlify Proxy -> Railway Backend -> SQLite DB]           [Direct Sub-second Live OHLC Tick Stream]
```

### Forensic Details:
- **Production URL Used:** `wss://project-goat.onrender.com/api/v1/market-data/ws` (**CONFIRMED — Hardcoded in `TradingViewDataFeed.ts:465`**)
- **Hostname Validity:** `project-goat.onrender.com` is obsolete/decommissioned. The active backend is hosted on Railway (`project-goat-production.up.railway.app`). (**CONFIRMED**)
- **Backend Endpoint Existence on Railway:** The endpoint `@app.websocket("/api/v1/market-data/ws")` exists in `goat/server.py:343` and is active on Railway. (**CONFIRMED**)
- **Handler Connection Acceptance:** `websocket_stream_endpoint` executes `await websocket.accept()` and appends the connection to `connected_websockets: set[WebSocket]`. (**CONFIRMED**)
- **Frame Transmission:** When live ticks arrive via `engine.ws_manager`, `on_tick_pipeline_wrapper` in `goat/server.py:74` invokes `broadcast_tick_to_websockets(raw_payload)`. Connected clients receive the live tick frame JSON. (**CONFIRMED**)
- **Symbol Targeting:** Broadcast frames contain the tick's symbol (e.g. `{"tick": {"symbol": "R_100", "quote": 1234.56, ...}}`). `TradingViewDataFeed.handleWebSocketMessage()` normalizes the symbol and matches it against `sub.symbol`. (**CONFIRMED**)

---

## 2. TELEMETRY WEBSOCKET FLOW

```
[Dashboard Pages / TopNav / Status Bar]
       │
       ▼
[useTelemetryStore (`apps/dashboard/src/stores/telemetryStore.ts`)]
       │
       ├───────────────────────────────────────────────────────┐
       ▼ (Production: Non-localhost)                           ▼ (Localhost Dev)
[wss://project-goat-production.up.railway.app/ws/telemetry] [ws://localhost:8000/ws/telemetry]
       │                                                       │
       ▼                                                       ▼
[FastAPI @router.websocket("/ws/telemetry") in `goat/telemetry/server.py`]
       │
       ▼
[broadcaster.add_connection(websocket)]
       │
       ├────────────────────────────────────────┬───────────────────────────────────────┐
       ▼ (Task A: Send Loop)                    ▼ (Task B: Receive Loop)                ▼ (On Error / Disconnect)
[Loop every 500ms:                             [Continuous `receive_text()`:            [Remove connection from]
 get_telemetry_snapshot()                       - SWITCH_SYMBOL -> master_engine        [broadcaster active set]
 await websocket.send_json(snapshot)]           - SWITCH_TIMEFRAME -> master_engine]
       │
       ▼
[Zustand useTelemetryStore receives snapshot:
 updates `marketState`, `statistics`, `edges`, `systemHealth`, `ticksProcessed`, `liveEvents`]
```

### Forensic Details:
- **Production URL Used:** `wss://project-goat-production.up.railway.app/ws/telemetry` (**CONFIRMED — `telemetryStore.ts:169`**)
- **Backend Route:** `/ws/telemetry` defined on `create_telemetry_router(broadcaster)` and mounted via `app.include_router(...)` in `goat/server.py:142`. (**CONFIRMED**)
- **Router Mounting Match:** Matches exactly. (**CONFIRMED**)
- **Connection Acceptance:** `await websocket.accept()` followed by `broadcaster.add_connection(websocket)`. (**CONFIRMED**)
- **Frame Generation & Concurrency:** Separated `send_telemetry_loop` (500ms intervals) and `receive_command_loop` (`receive_text`) managed via `asyncio.wait(..., return_when=FIRST_COMPLETED)`. (**CONFIRMED**)
- **Exception Resilience:** `get_telemetry_snapshot()` encapsulates SQLite repository queries with try/except fallbacks (`ranked_edges_raw = []`), preventing cross-thread `ProgrammingError` from terminating the loop. If serialization errors occur, a fallback frame is sent. (**CONFIRMED**)
- **Railway Configuration Impact:** Railway supports WebSockets natively on port `${PORT:-8000}`. (**CONFIRMED**)

---

## 3. PRODUCTION URL CONFIGURATION MATRIX

| Subsystem | Development URL | Production URL (Configured) | Production URL (Actual Required) | Diagnostic Classification |
| :--- | :--- | :--- | :--- | :--- |
| **REST API Client** | `/api/v1` (via Vite proxy -> `:8000`) | `/api/v1` (via Netlify proxy -> Railway) | `https://project-goat-production.up.railway.app/api/v1` | **CONFIRMED WORKING** |
| **Telemetry WebSocket** | `ws://localhost:8000/ws/telemetry` | `wss://project-goat-production.up.railway.app/ws/telemetry` | `wss://project-goat-production.up.railway.app/ws/telemetry` | **CONFIRMED WORKING** |
| **Market Data WebSocket** | `ws://localhost:3000/api/v1/market-data/ws` | `wss://project-goat.onrender.com/api/v1/market-data/ws` | `wss://project-goat-production.up.railway.app/api/v1/market-data/ws` | **CONFIRMED BROKEN (Wrong Host)** |
| **Netlify API Redirects** | N/A (Vite handles dev) | `[[redirects]] from = "/api/*" to = "https://project-goat-production.up.railway.app/api/:splat"` | Netlify HTTP proxy (Note: Netlify cannot proxy WebSockets) | **CONFIRMED WORKING (HTTP Only)** |

---

## 4. ROUTER & MOUNTING ANALYSIS

### Backend (`goat/server.py`) Route Registration:
1. `app.include_router(create_telemetry_router(broadcaster))`
   - Path prefix: none
   - WebSocket: `/ws/telemetry` (**CONFIRMED**)
2. `app.include_router(create_validation_router(master_engine))`
   - Path prefix: `/api/v1/validation` (**CONFIRMED**)
3. `app.include_router(create_research_router(master_engine.ai_reasoning_engine))`
   - Path prefix: `/api/v1/research` (**CONFIRMED**)
   - Mounted routes: `/explain/{edge_id}`, `/report/{edge_id}`, `/evidence/{edge_id}`, `/graph/summary`, `/stats`
4. `app.include_router(create_workspace_router(workspace_repo))`
   - Path prefix: `/api/v1/workspace` (**CONFIRMED**)
5. Direct Top-Level Server Endpoints:
   - `GET /api/v1/market-data/candles/latest/{symbol_id}` (**CONFIRMED**)
   - `GET /api/v1/market-data/candles/history/{symbol_id}` (**CONFIRMED**)
   - `GET /api/v1/market-data/symbols` (**CONFIRMED**)
   - `GET /api/v1/market-data/metrics` (**CONFIRMED**)
   - `GET /api/v1/summary`, `/api/v1/health`, `/api/v1/hypotheses`, `/api/v1/governance` (**CONFIRMED**)
   - `WS /api/v1/market-data/ws` (**CONFIRMED**)

---

## 5. SYMBOL SUPPORT & PATHWAY ANALYSIS

### Supported Symbols in Backend Registry (`goat/market_data/models/symbol.py`):
Total: **8 Canonical Deriv Synthetic Instruments**
1. `VOLATILITY_10` (`R_10`)
2. `VOLATILITY_25` (`R_25`)
3. `VOLATILITY_50` (`R_50`)
4. `VOLATILITY_75` (`R_75`)
5. `VOLATILITY_100` (`R_100`)
6. `BOOM_1000` (`BOOM1000`)
7. `CRASH_1000` (`CRASH1000`)
8. `STEP_INDEX` (`stpRNG`)

### Symbols Listed in Frontend UI (`SymbolManager.ts`, `symbolStore.ts`):
Total: **15 Symbols** (8 supported + 7 unsupported):
- Supported: `VOLATILITY_10`, `VOLATILITY_25`, `VOLATILITY_50`, `VOLATILITY_75`, `VOLATILITY_100`, `BOOM_1000`, `CRASH_1000`, `STEP_INDEX`
- **Unsupported:** `BOOM_500`, `CRASH_500`, `JUMP_10`, `JUMP_25`, `JUMP_50`, `JUMP_75`, `JUMP_100`

---

## 6. DETAILED TRACE FOR TARGET SYMBOLS

### Case 1: `VOLATILITY_100` (Supported Symbol)
1. **User selects `VOLATILITY_100` in Chart Dropdown**:
   - `ChartStateStore.setSymbol('VOLATILITY_100')` is updated.
   - `TradingViewDataFeed.subscribeBars()` registers subscriber for `VOLATILITY_100`.
2. **WebSocket Attempt**:
   - Tries `wss://project-goat.onrender.com/api/v1/market-data/ws` -> **FAILS** (host unreachable).
3. **Fallback Activation**:
   - `startPollingFallback()` begins polling `GET /api/v1/market-data/candles/latest/VOLATILITY_100?timeframe=1M` every 2s.
4. **Backend Processing**:
   - Deriv feed is actively streaming `R_100` into `LiveMarketDataIngestionEngine`.
   - `LiveCandleBuilder` forms 1M candles for `VOLATILITY_100`.
   - `GET /api/v1/market-data/candles/latest/VOLATILITY_100` returns HTTP 200 with valid `MarketCandle`.
5. **Chart Outcome**:
   - **Chart renders and updates every 2 seconds via HTTP polling.**
   - **Status:** **CONFIRMED DEGRADED (WebSocket broken, HTTP fallback masking failure).**

---

### Case 2: `BOOM_500` (Unsupported Symbol)
1. **User selects `BOOM_500` in Chart Dropdown**:
   - `ChartStateStore.setSymbol('BOOM_500')` is updated.
   - `TradingViewDataFeed.subscribeBars()` registers subscriber for `BOOM_500`.
2. **WebSocket Attempt**:
   - Fails on Render URL -> falls back to HTTP polling.
3. **HTTP Polling Attempt**:
   - Polls `GET /api/v1/market-data/candles/latest/BOOM_500?timeframe=1M` every 2s.
4. **Backend Processing**:
   - `BOOM_500` is **NOT** in `SUPPORTED_SYMBOLS` and is **NOT** subscribed on Deriv WS client.
   - `candle_builder.get_latest_candle('BOOM_500')` returns `None`.
   - Backend returns HTTP 200 with `{"symbol": "BOOM_500", "timeframe": "1M", "candle": null}`.
5. **Historical Data Request**:
   - `TradingViewDataFeed.getBars()` requests `/api/v1/market-data/candles/history/BOOM_500`.
   - Backend returns HTTP 200 with `{"symbol": "BOOM_500", "candles": [], "count": 0}`.
6. **Chart Outcome**:
   - Chart receives empty history (`noData: true`) and null latest candle.
   - **Chart remains completely blank/empty with no error message to the operator.**
   - **Status:** **CONFIRMED BROKEN (Silent failure due to nonexistent backend symbol ingestion).**

---

### Case 3: `CRASH_500` (Unsupported Symbol)
- Identical failure path to `BOOM_500`.
- Not present in backend `SUPPORTED_SYMBOLS`.
- Ingestion engine never receives ticks; candle builder has no buffer; API returns `candle: null` and `candles: []`.
- **Chart remains completely blank/empty.**
- **Status:** **CONFIRMED BROKEN (Silent failure due to nonexistent backend symbol ingestion).**

---

## 7. FRONTEND FALLBACK BEHAVIOR

`TradingViewDataFeed.ts` contains an explicit HTTP polling fallback:
```typescript
private startPollingFallback(): void {
  if (this._destroyed || this.pollFallbackActive) return;
  this.pollFallbackActive = true;

  this.pollingTimerId = setInterval(async () => {
    if (this.subscribers.size === 0 || this.wsConnected) return;

    for (const [, sub] of this.subscribers.entries()) {
      try {
        const url = `/api/v1/market-data/candles/latest/${sub.symbol}?timeframe=${sub.goatTimeframe}`;
        const res = await fetch(url);
        if (!res.ok) continue;
        const payload = await res.json();
        const candle = payload.data?.candle || payload.candle;
        if (!candle) continue;
        // Construct bar and notify chart subscriber
        ...
      } catch (err) { ... }
    }
  }, 2000);
}
```

### Forensic Analysis of Fallback:
1. **Masking Effect:** For supported symbols (`VOLATILITY_100`, `BOOM_1000`, etc.), HTTP polling successfully fetches forming candles every 2 seconds. The chart updates visually, leading operators to believe WebSockets are working. (**CONFIRMED**)
2. **Performance Degradation:** Instead of push-based sub-second tick precision (e.g. 50–100ms latency), the chart operates on 2,000ms batch intervals with repetitive HTTP roundtrips. (**CONFIRMED**)
3. **Netlify Rate & Connection Pressure:** Each active chart tab fires 30 HTTP requests per minute per subscribed symbol through the Netlify proxy to Railway. (**CONFIRMED**)

---

## 8. EXACT FAILURE POINTS & EVIDENCE

### Failure Point 1: Obsolete Render URL in `TradingViewDataFeed.ts`
- **Location:** `apps/dashboard/src/charting/TradingViewDataFeed.ts:465`
- **Code:** `wsUrl = 'wss://project-goat.onrender.com/api/v1/market-data/ws';`
- **Evidence:** `grep_search` and `view_file` confirm hardcoded string pointing to `project-goat.onrender.com` instead of `project-goat-production.up.railway.app`.
- **Classification:** **CONFIRMED**

### Failure Point 2: Frontend / Backend Symbol Registry Discrepancy
- **Location:** `apps/dashboard/src/charting/SymbolManager.ts:19-200` & `apps/dashboard/src/stores/symbolStore.ts:10-26` vs `goat/market_data/models/symbol.py:39-104`
- **Evidence:** Backend only ingests 8 symbols (`VOLATILITY_10`, `VOLATILITY_25`, `VOLATILITY_50`, `VOLATILITY_75`, `VOLATILITY_100`, `BOOM_1000`, `CRASH_1000`, `STEP_INDEX`). Frontend UI lists 15 symbols including `BOOM_500`, `CRASH_500`, `JUMP_10..100`. Selecting unsupported symbols produces empty API responses and blank charts.
- **Classification:** **CONFIRMED**

### Failure Point 3: Symbol State Fragmentation Across Multiple Zustand Stores
- **Location:**
  - `apps/dashboard/src/stores/telemetryStore.ts` (`symbol`, `setSymbol`)
  - `apps/dashboard/src/stores/symbolStore.ts` (`currentSymbol`, `setSymbol`)
  - `apps/dashboard/src/charting/ChartState.ts` (`activeSymbol`, `setSymbol`)
- **Evidence:** Switching a symbol in the chart toolbar updates `ChartState`, but does not notify `telemetryStore` (which sends `SWITCH_SYMBOL` over `/ws/telemetry`). Switching in `MarketIntelligenceWorkspacePage` updates `telemetryStore`, but does not update `ChartState`.
- **Classification:** **CONFIRMED**

### Failure Point 4: Outdated Integration Test Route Assertions
- **Location:** `tests/test_production_integration.py:56` & `tests/test_fastapi_server.py:27-29`
- **Evidence:**
  - `test_production_integration.py` expects `GET /api/v1/research/edges/rankings` which does not exist on `create_research_router`.
  - `test_fastapi_server.py` expects platform title `"Project GOAT — Institutional Trading Platform API"` and version `"1.1.0"`, whereas `goat/server.py` defines `"Project GOAT — Institutional Quantitative Research Platform API"` and `"1.2.0"`.
- **Classification:** **CONFIRMED**

---

## 9. MINIMUM FIX REQUIRED

When approved to implement fixes:
1. **Fix Market Data WebSocket URL Resolution:**
   Update `TradingViewDataFeed.ts` to resolve WebSocket URL dynamically from `window.location` or `import.meta.env.VITE_WS_URL` / `project-goat-production.up.railway.app`, identical to `telemetryStore.ts`.
2. **Harmonize Supported Symbol Registry:**
   Align `SymbolManager.ts` and `symbolStore.ts` with the 8 canonical Deriv symbols supported by the backend, or flag unsupported symbols as inactive in the UI dropdown.
3. **Synchronize Symbol State Across Stores:**
   Ensure changing the active symbol in any UI component coordinates `useSymbolStore`, `useTelemetryStore`, and `useChartStateStore`.
4. **Update Integration Test Assertions:**
   Align `test_fastapi_server.py` and `test_production_integration.py` assertions with current FastAPI route names and version 1.2.0 constants.

---

## 10. FILES THAT WOULD NEED TO CHANGE (DIAGNOSTIC INVENTORY)

The following files are identified for stabilization in future phases (NO CHANGES MADE IN THIS AUDIT):
1. `apps/dashboard/src/charting/TradingViewDataFeed.ts` (WebSocket URL resolution)
2. `apps/dashboard/src/charting/SymbolManager.ts` (Supported symbol registry alignment)
3. `apps/dashboard/src/stores/symbolStore.ts` (Default symbol list alignment)
4. `apps/dashboard/src/charting/TradingViewContainer.tsx` (Symbol sync bridge)
5. `tests/test_fastapi_server.py` (Title/version string assertions)
6. `tests/test_production_integration.py` (Research route endpoint fixture)

---

**Forensic Audit Certified Complete:** 2026-08-30  
**Status:** READY FOR PHASE 1 REVIEW & STABILIZATION APPROVAL
