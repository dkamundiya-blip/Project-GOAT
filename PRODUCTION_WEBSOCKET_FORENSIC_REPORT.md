# Project GOAT — Production WebSocket Forensic Debugging Report

## 1. Executive Summary & Forensic Verdict

- **Assignment**: Forensic investigation of why the browser establishes HTTP 101 WebSocket handshake with Railway backend (`/ws/telemetry`), but receives zero continuous messages and alternates between `RECONNECTING` and `DISCONNECTED`.
- **Strict Constraint Followed**: **ZERO code modifications were made.**
- **Exact Failure Location**: `goat/telemetry/server.py:L164` inside `websocket_telemetry_endpoint()`.
- **Root Cause**: `asyncio.wait_for(websocket.receive_text(), timeout=0.01)` cancels Starlette's ASGI `receive()` channel coroutine upon timing out (10ms). In Starlette/Uvicorn, cancelling the ASGI receive task permanently corrupts the WebSocket connection state machine, causing the ASGI transport to send a close frame or causing the subsequent `send_json()` to raise `WebSocketDisconnect` / `RuntimeError: Cannot call 'send' once a close message has been sent`. The exception handler catches this, calls `broadcaster.remove_connection(websocket)`, and terminates the endpoint loop immediately after the first frame.

---

## 2. End-to-End WebSocket Lifecycle Trace

```
FastAPI ASGI Router (/ws/telemetry)
  │ [STAGE 1: EXECUTED]
  ▼
websocket.accept()
  │ [STAGE 2: EXECUTED] (HTTP 101 Switching Protocols handshake sent to browser)
  ▼
client registration (broadcaster.add_connection(websocket))
  │ [STAGE 3: EXECUTED] (Client added to _active_connections set)
  ▼
broadcast loop startup (while True)
  │ [STAGE 4: EXECUTED]
  ▼
get_telemetry_snapshot()
  │ [STAGE 5: EXECUTED] (Snapshot dict constructed from master_engine)
  ▼
websocket.send_json(snapshot)
  │ [STAGE 6: EXECUTED] (First frame sent)
  ▼
await asyncio.sleep(0.5)
  │ [STAGE 7: EXECUTED] (Sleeps for 500 ms)
  ▼
await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
  │ ✕ [STAGE 8: FATAL COROUTINE CANCELLATION] (Line 164)
  │   1. Browser is passive listener, sending no text in 10 ms.
  │   2. asyncio.wait_for raises asyncio.TimeoutError.
  │   3. asyncio.wait_for CANCELS the inner coroutine websocket.receive_text().
  │   4. Starlette's ASGI reader task is cancelled, setting socket to DISCONNECTING/CLOSED.
  ▼
Next Iteration: send_json() or Starlette Protocol Reader
  │ ✕ [STAGE 9: EXCEPTION RAISED]
  │   send_json() throws RuntimeError / WebSocketDisconnect.
  ▼
except WebSocketDisconnect / Exception:
  │ ✕ [STAGE 10: CLIENT REMOVED & LOOP TERMINATED]
  │   broadcaster.remove_connection(websocket)
  │   Endpoint coroutine terminates.
  │   Browser receives close code (1006 abnormal closure) -> RECONNECTING.
```

---

## 3. Forensic Answers to the 10 Diagnostic Questions

| # | Question | Forensic Evidence & Answer |
| :--- | :--- | :--- |
| **1** | **Is this code actually executed?** | **YES**. `websocket_telemetry_endpoint()` is entered upon client connection. `websocket.accept()` and `broadcaster.add_connection()` execute. |
| **2** | **Is it running continuously?** | **NO**. It runs for exactly one iteration (~510 ms) before terminating. |
| **3** | **If not, exactly where does execution stop?** | Execution breaks at **`goat/telemetry/server.py:L164`**: `raw_cmd = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)`. |
| **4** | **What exception is being swallowed?** | `asyncio.TimeoutError` is swallowed on line 170 (`except asyncio.TimeoutError: pass`), but the cancellation of the ASGI `receive()` channel coroutine under the hood cannot be undone by a simple `pass`. |
| **5** | **What task exits?** | The FastAPI/Starlette ASGI connection task running `websocket_telemetry_endpoint` exits. |
| **6** | **What coroutine is cancelled?** | Starlette's internal ASGI `receive()` coroutine (`WebSocket._receive()`) is cancelled by `asyncio.wait_for()`. |
| **7** | **Is the client immediately removed from the active client set?** | **YES**. Lines 176 and 179 execute `broadcaster.remove_connection(websocket)` inside `except WebSocketDisconnect` and `except Exception:`. |
| **8** | **Is `send_json()` ever reached?** | `send_json()` is reached on iteration 1, but the socket is severed within 10ms after the first frame by the receive stream cancellation, preventing continuous streaming. |
| **9** | **If reached, does it throw?** | On iteration 2, `send_json()` throws `RuntimeError: Cannot call "send" once a close message has been sent.` or `WebSocketDisconnect`. |
| **10**| **If not reached, explain exactly why.** | N/A (Reached once, throws on iteration 2). |

---

## 4. Code Citation of the Failing Block (`goat/telemetry/server.py`)

Lines 155–179 of `goat/telemetry/server.py`:
```python
# goat/telemetry/server.py:155-179
        try:
            while True:
                # 1. Publish live engine snapshot frame every 500 ms
                snapshot = broadcaster.get_telemetry_snapshot()
                await websocket.send_json(snapshot)
                await asyncio.sleep(0.5)

                # 2. Check for incoming client commands (e.g., symbol / timeframe switch)
                try:
                    # ---> FATAL DEFECT: Cancelling websocket.receive_text() breaks Starlette ASGI channel
                    raw_cmd = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                    cmd_data = json.loads(raw_cmd)
                    if cmd_data.get("action") == "SWITCH_SYMBOL" and "symbol" in cmd_data:
                        broadcaster.master_engine.switch_symbol(cmd_data["symbol"])
                    elif cmd_data.get("action") == "SWITCH_TIMEFRAME" and "timeframe" in cmd_data:
                        broadcaster.master_engine.switch_timeframe(cmd_data["timeframe"])
                except asyncio.TimeoutError:
                    pass  # Swallows the Python exception, but ASGI receive task is already cancelled!
                except Exception:
                    pass

        except WebSocketDisconnect:
            broadcaster.remove_connection(websocket)
        except Exception as exc:
            _log.warning("telemetry_ws_exception", error=str(exc))
            broadcaster.remove_connection(websocket)
```

---

## 5. Architectural Explanation: Why `asyncio.wait_for` Breaks Starlette WebSockets

In Starlette's ASGI WebSocket implementation:
1. `WebSocket.receive_text()` awaits an ASGI receive event (`type: "websocket.receive"`).
2. Uvicorn manages an internal event loop worker waiting on the raw TCP socket.
3. When `asyncio.wait_for(..., timeout=0.01)` expires, Python's `asyncio` sends a `GeneratorExit` / `CancelledError` to the `receive_text` coroutine.
4. Starlette interprets the cancelled receive future as an aborted connection or corrupted ASGI pipeline.
5. On the next call to `websocket.send_json()`, the socket is no longer in `WebSocketState.CONNECTED`, causing an immediate unrecoverable `RuntimeError` or `WebSocketDisconnect`.
6. This causes the loop to exit and the client is dropped.

---

## 6. Minimal Remediation Strategy (For Subsequent Sprint)

To make the telemetry broadcast loop 100% resilient and continuous:
- **Option A (Dedicated Push Loop)**: Separate the telemetry publisher loop from client command receiving. The broadcast loop runs continuously sending snapshots, while a separate background task listens for incoming client messages with standard `await websocket.receive_text()` (no timeout cancellation).
- **Option B (Pure Streaming Endpoint)**: Stream snapshots directly in the endpoint with `await websocket.send_json(snapshot); await asyncio.sleep(0.5)` without attempting a non-blocking `wait_for` receive on the same coroutine. Client commands (such as switching symbol or timeframe) can be routed via standard REST endpoints (`POST /api/v1/validation/symbol`) or separate dedicated command channels.
