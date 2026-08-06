# Project GOAT v1.0 — Dashboard Foundation & Control Room Architecture

## Subsystem Overview
The **Dashboard Foundation & Control Room Architecture** (`apps/dashboard/`) serves as the permanent, high-performance operator interface for Project GOAT Version 1.0.

The backend quantitative research platform (Versions 0.8 through 0.9.1) remains 100% frozen. The dashboard does NOT duplicate scientific business logic, generate trading signals, or route live orders. It acts purely as a visualization shell, UI state container, and FastAPI/WebSocket client abstraction layer.

---

## Directory Structure

```
apps/dashboard/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── index.html
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── theme/
│   │   ├── colors.ts
│   │   └── tokens.ts
│   ├── types/
│   │   ├── layout.ts
│   │   ├── nav.ts
│   │   └── state.ts
│   ├── stores/
│   │   ├── themeStore.ts
│   │   ├── layoutStore.ts
│   │   ├── sidebarStore.ts
│   │   ├── inspectorStore.ts
│   │   ├── workspaceStore.ts
│   │   ├── notificationStore.ts
│   │   └── symbolStore.ts
│   ├── services/
│   │   └── api/ (RESTClient, WSClient, AuthClient)
│   ├── components/
│   │   ├── ui/ (Button, Card, Input, Badge, Dialog, Table, Panel, Spinner, EmptyState, ErrorState)
│   │   └── layout/ (TopNav, LeftSidebar, RightInspector, BottomStatusBar, AppShell)
│   ├── pages/ (16 Route Pages + 404 NotFound)
│   ├── router/ (routes.ts, index.tsx)
│   └── hooks/ (useTheme, useLayout, useNotifications, useSymbol)
└── tests/
```

---

## Primary Application Shell Layout

1. **Top Navigation (`TopNav.tsx`)**: Branding, Version Tag, Workspace Selector, Symbol Selector, Inspector Toggle.
2. **Left Sidebar (`LeftSidebar.tsx`)**: Navigation groups (Operator Dashboards, Scientific Pipeline, Knowledge & Discovery, Management & System) with collapse/expand state.
3. **Main Workspace**: Responsive route renderer with lazy loading (`AppRouter.tsx`).
4. **Right Inspector Panel (`RightInspector.tsx`)**: Contextual telemetry metadata panel.
5. **Bottom Status Bar (`BottomStatusBar.tsx`)**: Live system operational status, active symbol, frozen backend version tag, and notification counters.

---

## State Management Architecture (Zustand)

- **`useThemeStore`**: Theme mode state (`dark`/`light`).
- **`useLayoutStore`**: Layout visibility flags (`topNavVisible`, `bottomStatusVisible`).
- **`useSidebarStore`**: Sidebar state (`expanded`/`collapsed`).
- **`useInspectorStore`**: Right inspector drawer state and content payload.
- **`useWorkspaceStore`**: Active workspace preset selection.
- **`useNotificationStore`**: System notifications queue.
- **`useSymbolStore`**: Selected synthetic index symbol (`VOLATILITY_100`, `BOOM_1000`, etc.).
