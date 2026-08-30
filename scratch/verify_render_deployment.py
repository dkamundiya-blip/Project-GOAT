"""
Verify Render Production Deployment after Commit 3d7aca7.
Tests:
1. HTTP GET /api/v1/health with timeout
2. WebSocket connection to wss://project-goat.onrender.com/ws/telemetry
3. Captures live telemetry frames, ticks, candles, features, latency, and edges.
"""

import asyncio
import json
import ssl
import sys
import urllib.request
import websockets


def test_http_health():
    print("--> Probing https://project-goat.onrender.com/api/v1/health ...")
    req = urllib.request.Request(
        "https://project-goat.onrender.com/api/v1/health",
        headers={"User-Agent": "Project-GOAT-Verifier/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            print("HTTP 200 OK:")
            print(json.dumps(data, indent=2))
            return data
    except Exception as exc:
        print(f"HTTP Health Check Exception: {exc}")
        return None


async def test_websocket_telemetry():
    uri = "wss://project-goat.onrender.com/ws/telemetry"
    print(f"\n--> Connecting to WebSocket: {uri} ...")
    ssl_ctx = ssl.create_default_context()

    try:
        async with websockets.connect(uri, ssl=ssl_ctx, open_timeout=15) as ws:
            print("WebSocket connected successfully! HTTP 101 Switching Protocols.")
            frames = []
            start_time = asyncio.get_event_loop().time()

            while len(frames) < 10 and (asyncio.get_event_loop().time() - start_time) < 8:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    frame = json.loads(msg)
                    frames.append(frame)
                    print(f"Frame #{len(frames)}: Symbol={frame.get('symbol')} Ticks={frame.get('ticks_processed')} Candles={frame.get('candles_closed')} FVs={frame.get('feature_vectors_generated')} Latency={frame.get('pipeline_latency_ms')}ms Edges={frame.get('edges')}")
                except asyncio.TimeoutError:
                    break

            print(f"\nTotal frames received: {len(frames)}")
            if frames:
                print("\n--- FIRST FRAME DETAIL ---")
                print(json.dumps(frames[0], indent=2))
                return True
            else:
                print("No frames received within timeout window.")
                return False
    except Exception as exc:
        print(f"WebSocket Connection Exception: {exc}")
        return False


async def main():
    health = test_http_health()
    ws_ok = await test_websocket_telemetry()
    print("\n--- SUMMARY ---")
    print(f"HTTP Health: {'PASS' if health else 'FAIL'}")
    print(f"WebSocket Telemetry: {'PASS' if ws_ok else 'FAIL'}")


if __name__ == "__main__":
    asyncio.run(main())
