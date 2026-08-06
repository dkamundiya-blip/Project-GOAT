# Institutional TradingView Charting Engine Architecture (`apps/dashboard/src/charting/`)

## 1. Overview & Architectural Boundaries

`apps/dashboard/src/charting/` embeds the **Professional TradingView Charting Engine** into Project GOAT Version 1.0.

### MANDATORY NON-NEGOTIABLE ARCHITECTURE:
TradingView Datafeed **MUST NEVER** communicate directly with the Deriv WebSocket endpoint.

```
                    ┌────────────────────────────────┐
                    │      Deriv WebSocket API       │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │   GOAT Market Data Engine      │
                    │   (WebSocket / Normalizer)     │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │     Canonical LiveTicks        │
                    │   & Multi-Timeframe Candles    │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │     SQLite WAL Persistence     │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │   GOAT Market Data REST API    │
                    │ (/api/v1/market-data/candles/*)│
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │  TradingView DataFeed Adapter  │
                    │    (TradingViewDataFeed.ts)    │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │  TradingView Charting Library  │
                    │  (Canvas/SVG 60 FPS Engine)    │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │  GOAT Dashboard Workspace UI   │
                    └────────────────────────────────┘
```

---

## 2. Component Structure

- **`SymbolManager.ts`**: Symbol metadata registry & resolution for 15 synthetic index instruments (Volatility 10, 25, 50, 75, 100; Boom 500, 1000; Crash 500, 1000; Step Index; Jump 10, 25, 50, 75, 100).
- **`TimeframeManager.ts`**: Timeframe resolution mapping (`Tick`, `1M`, `5M`, `15M`, `30M`, `1H`, `4H`, `1D`).
- **`TradingViewDataFeed.ts`**: TradingView JS DataFeed API adapter implementation consuming data EXCLUSIVELY from GOAT REST API endpoints (`onReady`, `searchSymbols`, `resolveSymbol`, `getBars`, `subscribeBars`, `unsubscribeBars`).
- **`TradingViewAdapter.ts`**: Event and stream bridge.
- **`ChartState.ts`**: Zustand store for active symbol, timeframe, style (`candlestick`, `line`, `area`, `heikin_ashi`, `renko`), layout mode, crosshair, and Bloomberg dark theme.
- **`ChartEvents.ts`**: Event bus for chart interaction events.
- **`DrawingManager.ts`**: Interactive drawing tool manager supporting trendlines, horizontal/vertical rays, rectangles, ellipses, text labels, Fibonacci retracements, pitchforks, measure tool, and magnet mode.
- **`LayoutManager.ts`**: Multi-chart grid layouts (`single`, `split_h`, `split_v`, `grid_2x2`).
- **`CrosshairManager.ts`**: Synchronized crosshairs across multi-chart grid instances.
- **`ChartPersistence.ts`**: Local storage preference persistence.
- **`ReplayHooks.ts`**: Interfaces and controller preparation for future market replay mode.
- **`TradingViewWidget.tsx`**: High-performance Canvas/SVG 60 FPS chart component with volume histograms, price scale badges, and legends.
- **`TradingViewContainer.tsx`**: Complete Charting Workspace shell including top main toolbar, left drawing toolbar, and multi-chart grid.
- **`TradingViewProvider.tsx`**: React Context Provider.

---

## 3. Real-Time Streaming Performance

- **Target Streaming Latency**: `< 250 ms`
- **Frame Rate**: Smooth 60 FPS Canvas rendering
- **Continuous Polling & Push Callback**: Updates latest forming candle bar without full page refreshes.

---

## 4. Preparation for Step 1.7 (Research Overlay Attachments)

`DrawingManager.ts` and `ChartDrawingObject` are engineered with non-breaking extension interfaces (`researchOverlayRef`) to support Step 1.7:
- Future research artifacts (Hypotheses, Evidence, Experiments, Governance decisions, Journal entries, Voice notes, AI Observations) will attach directly onto TradingView chart objects without altering Step 1.6 architecture.

---

## 5. Non-Execution Safety Compliance

Strict compliance with Constitutional Amendments No.001 & No.002 is maintained:
- Data acquisition and visualization ONLY.
- Zero trade execution, zero broker order routing, zero automated risk or position sizing.
