import asyncio, json, time, sys

try:
    import websockets
except ImportError:
    print("websockets not installed"); sys.exit(1)

URLS = [
    "wss://project-goat.onrender.com/ws/telemetry",
    "wss://project-goat-production.up.railway.app/ws/telemetry",
]

async def test_url(url, max_frames=5, timeout_s=20.0):
    print(f"\n{'='*60}\nTARGET: {url}\n{'='*60}")
    t0 = time.time()
    frames = 0
    try:
        print(f"[{time.time()-t0:.2f}s] Connecting...")
        async with websockets.connect(url, open_timeout=15, close_timeout=5) as ws:
            print(f"[{time.time()-t0:.2f}s] CONNECTED (HTTP 101)")
            while frames < max_frames:
                left = timeout_s - (time.time() - t0)
                if left <= 0: break
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=min(left, 10.0))
                    frames += 1
                    try:
                        d = json.loads(raw)
                        print(f"[{time.time()-t0:.2f}s] FRAME #{frames}: type={d.get('type')} ticks={d.get('ticks_processed')} regime={d.get('market_state',{}).get('regime')}")
                    except: print(f"[{time.time()-t0:.2f}s] FRAME #{frames} NOT JSON: {raw[:100]}")
                except asyncio.TimeoutError:
                    print(f"[{time.time()-t0:.2f}s] TIMEOUT waiting for frame #{frames+1}"); break
                except Exception as e: print(f"[{time.time()-t0:.2f}s] RECV ERROR: {type(e).__name__}: {e}"); break
    except Exception as e:
        print(f"[{time.time()-t0:.2f}s] CONNECT FAILED: {type(e).__name__}: {e}")
    print(f"[{time.time()-t0:.2f}s] DONE: {frames} frames received")
    return frames

async def main():
    for url in URLS:
        await test_url(url)
        await asyncio.sleep(1)

asyncio.run(main())
