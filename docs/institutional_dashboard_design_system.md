# PROJECT GOAT VERSION 1.0 — INSTITUTIONAL DASHBOARD DESIGN SYSTEM & PRESENTATION SPECIFICATION

## Overview & Objective
This document defines the comprehensive presentation layer design system and component architecture for **Project GOAT Version 1.0 — Step 1.4: Institutional Dashboard UI/UX & Data Visualization Engine**.

Designed to match world-class institutional quantitative terminals (such as Bloomberg Terminal, TradingView Desktop, and modern high-frequency research workstations), this presentation layer provides extreme precision, clarity, dark glass aesthetic, and high-density quantitative visualization without modifying any backend scientific logic, REST/WS contracts, or SQLite persistence models.

---

## 1. Architecture & Technology Stack
- **Framework**: React 18 with TypeScript 5 (Vite bundler)
- **Styling Engine**: Custom Institutional Design System & Tokens with Tailwind CSS & CSS Variables
- **Theme Support**: Professional Dark Obsidian Theme + High Contrast Accessibility Mode
- **State Management**: Reactive Zustand Stores (`pipelineStore`, `searchStore`, `dashboardStore`, `telemetryStore`, `notificationStore`, `healthStore`, `sessionStore`, `settingsStore`, `connectionStore`)
- **Routing & Code-Splitting**: React Router 6 with `React.lazy` and `Suspense`
- **Location**: `apps/dashboard/src/`

---

## 2. Design Tokens (`apps/dashboard/src/theme/`)

### Colors (`colors.ts`)
- **Obsidian Primary Background**: `#06090e`
- **Institutional Surface**: `#0b101b`
- **Elevated Glass Container**: `#121a2d`
- **Subtle Panels & Borders**: `#1b253b` / `#273552`
- **Cyan Accent (Primary Indicator)**: `#00f0ff`
- **Emerald Accent (Nominal / High Confidence)**: `#10b981`
- **Amber Accent (Elevated Attention)**: `#f59e0b`
- **Rose Accent (Critical Status / Warning)**: `#f43f5e`
- **Violet Accent (Statistical Evaluation)**: `#a855f7`

### Typography (`typography.ts`)
- **Primary Body Font**: Inter (`sans-serif`)
- **Code, Hashes & Metrics Font**: JetBrains Mono (`monospace`)
- **Scale**: `3xs` (10px) to `4xl` (36px)

### Glassmorphism & Shadows (`glass.ts`, `shadows.ts`)
- **Panel Backdrop Filter**: `blur(12px)` / `blur(16px)`
- **Glass Borders**: `1px solid rgba(39, 53, 82, 0.6)`
- **Neon Glow Shadows**: `0 0 15px rgba(0, 240, 255, 0.35)`

---

## 3. Application Shell & Navigation Layout
1. **TopNav**: Workspace title, active server status, REST/WS connection indicators, global search trigger (`Ctrl+K`), notification alert toggle, user session role, and theme toggle.
2. **LeftSidebar**: Collapsible 4-section navigation tree (`Operator Workstation`, `Scientific Pipeline`, `Knowledge & Intelligence`, `System Operations`) with active indicators and stage badges.
3. **WorkspaceHeader**: Hierarchical route breadcrumbs, active entity counts, workspace title, and stage health status badges.
4. **NotificationCenter**: Slide-over drawer panel for real-time audit notifications filtered by severity (`INFO`, `WARN`, `CRITICAL`).
5. **RightInspector**: Tabbed slide-over drawer displaying canonical entity metadata, audit event stream, and real-time telemetry metrics.
6. **BottomStatusBar**: Real-time operational bar displaying REST, WS, DB, Telemetry stream status, version (`v1.0.0-institutional`), build ID, git commit hash, user, and real-time UTC clock.

---

## 4. Institutional Metric Cards & Data Grids

### KPI Metric Cards (`KPICard.tsx`)
- Supports icon, title, main value, sub-value, trend (+/- %, direction, sparkline preview), hover tooltip, shimmer skeleton loading state, and status badges (`NOMINAL`, `ELEVATED`, `CRITICAL`, `ACTIVE`).

### High-Performance Data Grid (`DataGridWidget.tsx`)
- Multi-column sorting, column filtering, search filter, page size selector (10, 25, 50, 100), canonical ID copy buttons, hover quick actions, multi-row checkbox selection, and right-click context menu.

---

## 5. Specialized Visualization Engines

### 8-Stage Research Pipeline Visualizer (`PipelineGraphWidget.tsx`)
- Interactive progress flow across `HYPOTHESIS` → `EVIDENCE` → `EXPERIMENT` → `STATISTICAL_EVALUATION` → `LIVE_VALIDATION` → `GOVERNANCE` → `ARCHIVE` → `RESEARCH_INTELLIGENCE`.
- Animated flow indicators, stage count badges, health metrics, and filter toggle.

### Master Scientific Chart Engine (`ChartsWidget.tsx`)
- Confidence distribution histogram, validation progress timeline SVG, research velocity bar chart, and governance outcome breakdown.

### Knowledge Graph & Relationship Viewer (`RelationshipViewerWidget.tsx`)
- SVG canvas node graph with zoom (+ / - / fit), pan, hover relationship highlighting, and direct entity inspector linkage.

### Chronological Audit Timeline (`EntityTimelineWidget.tsx`)
- Expandable event cards, severity color dots, step replay markers, and SHA-256 lineage signatures.

---

## 6. Accessibility & Performance
- **WCAG AA Compliance**: High contrast ratios and visible focus rings (`ring-2 ring-cyan-500`).
- **Keyboard Shortcuts**: `Ctrl+K` for global canonical search, `Esc` for modals and drawers, arrow keys for navigation.
- **Reduced Motion**: Respects `@media (prefers-reduced-motion: reduce)`.
- **Performance**: Virtualized grid rows, memoized chart components, lazy loading of workspace routes.
