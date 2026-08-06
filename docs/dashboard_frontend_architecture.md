# Project GOAT v1.0 — Operator Dashboard Frontend Architecture Specification

**Subsystem**: Step 1.2 Operator Dashboard Frontend & Control Room UI (`apps/dashboard/`)  
**Target Release**: Project GOAT Version 1.0  
**Status**: CERTIFIED & VERIFIED  

---

## 1. Executive Summary & Overview

The **Operator Dashboard Frontend** (`apps/dashboard/`) provides the institutional workstation UI for Project GOAT Version 1.0. It connects directly to the Step 1.1 real-time REST API & WebSocket backend server (`goat.dashboard`) to surface system resource metrics, research hypotheses, evidence records, governance decisions, and live telemetry feeds.

### Strict Architectural Invariants
1. **Presentation Layer Only**: Zero trading logic, zero statistical calculation, zero signal generation, zero direct database access.
2. **Backend API Integration**: Consumes backend APIs and WebSocket streams provided by Step 1.1 (`/health`, `/api/v1/summary`, `/api/v1/hypotheses`, `/api/v1/governance`, `/api/v1/symbols`, `/ws`).
3. **Institutional Visual Design**: High data density, dark mode aesthetic, minimal clutter, responsive layout.

---

## 2. Directory Structure Inventory

```
apps/dashboard/src/
├── types/
│   ├── api.ts                 # Backend API & telemetry payload TypeScript types
│   ├── dashboard.ts           # Overview metrics & pipeline state types
│   └── layout.ts              # Nav, layout & theme types
├── stores/
│   ├── dashboardStore.ts      # Research summary & pipeline overview state
│   ├── telemetryStore.ts      # Live telemetry frames & resource metrics state
│   ├── notificationStore.ts   # System warnings & event alerts store
│   ├── healthStore.ts         # System health & database connection state store
│   ├── sessionStore.ts        # Active dashboard session & user configuration store
│   ├── settingsStore.ts       # Layout, theme & display preferences store
│   └── connectionStore.ts     # REST & WebSocket connection telemetry store
├── services/api/
│   ├── restClient.ts          # REST client wrapper connected to Step 1.1 API
│   └── wsClient.ts            # WebSocket stream client connected to Step 1.1 WS
├── components/
│   ├── layout/
│   │   ├── TopNav.tsx         # Top bar (status, connection, live/replay, notifications, menu)
│   │   ├── LeftSidebar.tsx    # Categorized research pipeline navigation (11 routes)
│   │   ├── RightInspector.tsx # Right activity panel (events, warnings, governance, validation)
│   │   ├── BottomStatusBar.tsx# Footer bar (version, build, commit, DB status, replay mode)
│   │   └── AppShell.tsx       # Institutional layout container
│   ├── widgets/
│   │   ├── SystemOverviewCards.tsx # Summary metric cards
│   │   ├── LiveTelemetryChart.tsx  # Resource utilization telemetry widget
│   │   ├── SubsystemHealthWidget.tsx# Pipeline health status matrix
│   │   └── PipelineSummaryTable.tsx # Active hypotheses & edge candidate table
│   └── ui/                    # UI primitives (Badge, Card, Button, Table, Spinner)
├── pages/
│   └── DashboardPage.tsx      # Main Operator Control Room page layout
└── router/
    └── index.tsx              # Router composition
```

---

## 3. Workstation Layout & Component Matrix

1. **Top Navigation Bar (`TopNav.tsx`)**: System health status badge, API/WS connection status, Live/Replay mode toggle, notification dropdown badge, user account menu.
2. **Left Navigation Sidebar (`LeftSidebar.tsx`)**: Categorized navigation for 11 core routes (Research, Evidence, Experiments, Statistics, Live Validation, Governance, Knowledge Graph, Research Intelligence, Archive, Monitoring, Settings).
3. **Main Dashboard Workspace (`DashboardPage.tsx`)**: System overview cards, live telemetry feed widget, subsystem health matrix, and research pipeline summary table.
4. **Right Activity Inspector Panel (`RightInspector.tsx`)**: Activity event stream, system warnings, governance decision updates, live validation status.
5. **Bottom Operational Status Bar (`BottomStatusBar.tsx`)**: System version (`v1.0.0`), build identifier, git commit hash, database status (`ONLINE_READ_ONLY`), replay status (`LIVE_STREAMING`), and frozen backend tag (`v0.9.1`).

---

## 4. Reactive State Store Topology (Zustand)

- **`useDashboardStore`**: Summary metrics, hypothesis list, governance decision records.
- **`useTelemetryStore`**: Real-time telemetry frames array, active WS client count, frame sequence tracker.
- **`useHealthStore`**: System health status (`RUNNING`, `DEGRADED`, etc.), uptime seconds, system memory MB, DB health.
- **`useSessionStore`**: Active session ID (`DSH_`), host/port config, active user role (`CHIEF_QUANTITATIVE_OFFICER`).
- **`useSettingsStore`**: Theme mode (`dark`/`light`), refresh interval ms, sound alerts, compact layout toggle.
- **`useConnectionStore`**: REST status (`CONNECTED`), WS status (`OPEN`), latency ms, reconnect count, active mode (`LIVE`/`REPLAY`).
