# Project GOAT v0.8 — Notification & Distribution Platform Architecture

## 1. Subsystem Purpose

The **Notification & Distribution Platform** (`goat.notifications`) distributes already-generated, already-qualified, already-executed information downstream to external consumers (dashboards, mobile apps, webhooks, Telegram chats, etc.).

It operates strictly downstream of Steps 7.4 (Production Execution Engine), 7.5 (Portfolio Engine), and 7.6 (Trade Lifecycle Engine):

```
Execution Engine (Step 7.4)  ──┐
Portfolio Engine (Step 7.5) ───┼──► Notification Platform (Step 7.7) ──► Routing ──► Queue ──► Channel Dispatches
Trade Lifecycle (Step 7.6)  ───┘
```

The Notification Platform **MUST NEVER**:
- Generate or modify trading signals
- Change execution or portfolio states
- Calculate entry, SL, or TP prices
- Execute risk rules or size positions
- Connect directly to broker network sockets

---

## 2. Package Architecture

```
goat/notifications/
├── __init__.py                # Top-level public API exports (__all__)
├── engine.py                  # Master NotificationEngine coordinator
├── core/                      # Enums, SHA-256 ID generators, Pydantic V2 models
│   ├── __init__.py
│   ├── canonical.py
│   ├── enums.py
│   └── models.py
├── routing/                   # NotificationRoutingEngine (Recipient & priority routing, duplicate suppression)
│   ├── __init__.py
│   └── engine.py
├── channels/                  # NotificationChannelEngine (Logical channel handlers for 9 channels)
│   ├── __init__.py
│   └── engine.py
├── queue/                     # NotificationQueueEngine (Append-only FIFO & priority queue)
│   ├── __init__.py
│   └── engine.py
├── templates/                 # NotificationTemplateEngine (Markdown, Plain Text, JSON, HTML)
│   ├── __init__.py
│   └── engine.py
├── persistence/               # SQLite WAL repositories
│   ├── __init__.py
│   └── repository.py
└── reporting/                 # Markdown & Canonical JSON reporting engine
    ├── __init__.py
    └── reports.py
```

---

## 3. Deterministic SHA-256 Identifiers

All entities implement canonical SHA-256 digests across payload attributes to produce 16-character hexadecimal IDs:

| Prefix | Entity | Example ID |
|---|---|---|
| `NTF_` | `Notification` | `NTF_1A2B3C4D5E6F7890` |
| `NRC_` | `NotificationRecipient` | `NRC_2B3C4D5E6F7890A1` |
| `NCH_` | `NotificationChannel` | `NCH_3C4D5E6F7890A1B2` |
| `NPL_` | `NotificationPayload` | `NPL_4D5E6F7890A1B2C3` |
| `NDL_` | `NotificationDelivery` | `NDL_5E6F7890A1B2C3D4` |
| `NAD_` | `NotificationAudit` | `NAD_6F7890A1B2C3D4E5` |
| `NSM_` | `NotificationSummary` | `NSM_7890A1B2C3D4E5F6` |

---

## 4. Notification Routing & Duplicate Suppression

`NotificationRoutingEngine` evaluates incoming notification events against registered recipient profiles:
- **Priority Resolution**: Map event types to priority levels (`URGENT`, `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- **Duplicate Suppression**: Computes content fingerprints (`notification_type:subject:body`) to suppress identical redundant notifications within a configurable time window.
- **Recipient Channel Filtering**: Dispatches ONLY to recipient-subscribed channels.

---

## 5. Channel Abstraction Architecture

Supports 9 logical delivery channels with clean pluggable handler interfaces (`BaseNotificationChannelHandler`):
1. `DASHBOARD`: Web UI live state feed.
2. `DESKTOP`: Local OS notification alerts.
3. `MOBILE`: Push notification payloads.
4. `TELEGRAM`: Bot API MarkdownV2 formatted payloads (`chat_id`, `parse_mode`).
5. `DISCORD`: Webhook embeds format.
6. `WEBHOOK`: HTTP POST JSON payload structures.
7. `EMAIL`: Structured email templates.
8. `SMS`: Short character-constrained text alerts.
9. `FILE_EXPORT`: Disk append file logging.

*Note*: Step 7.7 implements payload serialization and dispatch planning ONLY. Zero external network connections, SDKs, or sockets are opened.

---

## 6. Queue Engine & Replay Support

`NotificationQueueEngine` maintains an append-only delivery queue:
- **Ordering**: Synchronous FIFO and priority-weighted queue processing.
- **Delivery Tracking**: Tracks delivery status (`QUEUED`, `DELIVERED`, `FAILED`, `SUPPRESSED`).
- **Replay Support**: Replays full notification history deterministically from SQLite WAL logs without re-executing actions.

---

## 7. Template Engine

`NotificationTemplateEngine` renders deterministic outputs across:
- **Markdown**: Formatted headers, code blocks, bulleted metadata lists.
- **Plain Text**: Compact single/multi-line strings for SMS and desktop toasts.
- **Canonical JSON**: Key-sorted JSON payloads for API consumers.
- **HTML**: Clean HTML5 document wrappers for email and dashboard web components.

---

## 8. Future Integration Roadmap

1. **Telegram Bot Integration**: Attach `httpx` or `python-telegram-bot` transport layer to `TelegramChannelHandler`.
2. **Mobile Push Integration**: Attach FCM (Firebase Cloud Messaging) or APNs transport to `MobileChannelHandler`.
3. **Dashboard Live Feed**: Attach Server-Sent Events (SSE) or WebSocket broadcaster to `DashboardChannelHandler`.
4. **Webhook Integration**: Attach async HTTP client worker to `WebhookChannelHandler`.
