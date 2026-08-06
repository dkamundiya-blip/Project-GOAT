# Institutional Live Market Data Architecture (`goat.market_data`)

## Overview

`goat.market_data` provides the live market data ingestion engine for Project GOAT Version 1.0. It connects directly to the Deriv WebSocket API (`wss://ws.derivws.com/websockets/v3?app_id=1089`), normalizes streaming tick payloads into canonical `LiveTick` domain models, aggregates ticks into multi-timeframe OHLCV candles (1M, 5M, 15M, 30M, 1H, 4H, 1D), persists ticks and candles asynchronously into SQLite using WAL mode, and serves real-time quotes, ticks, candles, control actions, and telemetry to the Institutional Dashboard via REST API handlers.

```
                    ┌────────────────────────────────┐
                    │      Deriv WebSocket API       │
                    │ (wss://ws.derivws.com/websockets)│
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │     DerivWebSocketClient       │
                    │   & WebSocketManager Engine    │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │       TickNormalizer           │
                    │  (Canonical SHA256 & LTK_ IDs) │
                    └───────────────┬────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐
│   LiveTickBuffer   │   │ LiveCandleBuilder  │   │ BufferedTickWriter │
│(In-Memory Ring Buf)│   │(1M,5M,15M,30M,1H..)│   │(SQLite WAL Batch)  │
└──────────┬─────────┘   └──────────┬─────────┘   └──────────┬─────────┘
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │      MarketDataAPIRouter       │
                    │   & Dashboard REST Handlers    │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │   Institutional Dashboard UX   │
                    │ (React / Zustand / Micro-UI)   │
                    └────────────────────────────────┘
```

---

## Supported Synthetic Instruments

The engine natively supports the following Deriv synthetic instruments:

| Symbol ID | Display Name | Index Type | Deriv WS Symbol | Precision |
|---|---|---|---|---|
| `VOLATILITY_10` | Volatility 10 Index | VOLATILITY | `R_10` | 3 decimals |
| `VOLATILITY_25` | Volatility 25 Index | VOLATILITY | `R_25` | 3 decimals |
| `VOLATILITY_50` | Volatility 50 Index | VOLATILITY | `R_50` | 4 decimals |
| `VOLATILITY_75` | Volatility 75 Index | VOLATILITY | `R_75` | 4 decimals |
| `VOLATILITY_100` | Volatility 100 Index | VOLATILITY | `R_100` | 2 decimals |
| `BOOM_1000` | Boom 1000 Index | SPIKE | `BOOM1000` | 3 decimals |
| `CRASH_1000` | Crash 1000 Index | SPIKE | `CRASH1000` | 3 decimals |
| `STEP_INDEX` | Step Index | STEP | `stpRNG` | 2 decimals |

---

## Multi-Timeframe Candle Aggregation Engine

`LiveCandleBuilder` aggregates incoming `LiveTick` objects into non-duplicating, replay-deterministic `MarketCandle` objects across 7 canonical timeframes:
- **1 Minute (`1M`)**
- **5 Minutes (`5M`)**
- **15 Minutes (`15M`)**
- **30 Minutes (`30M`)**
- **1 Hour (`1H`)**
- **4 Hours (`4H`)**
- **Daily (`1D`)**

Boundary floored timestamps maintain stable ISO 8601 UTC intervals. Completed candles are persisted to the `live_market_candles` table in SQLite and served through the internal Market Data REST API endpoints.

---

## Architectural Boundary for Step 1.6 (TradingView Charting)

Step 1.5 enforces a strict architectural boundary designed for Step 1.6 (TradingView Charting Library Integration):
- TradingView will obtain ALL OHLCV historical bars and live ticks **exclusively** via `goat.market_data.api`.
- TradingView will **never** communicate directly with the Deriv API.

---

## Non-Execution Governance Safety

This subsystem is **data acquisition and visualization only**. Signal generation, trade execution, machine learning models, and automated order routing are strictly omitted per Constitutional Amendments No.001 & No.002.
