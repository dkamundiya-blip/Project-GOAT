import asyncio
import json
import time
import urllib.request
import websockets

def check_rest_endpoints():
    base_url = "https://project-goat.onrender.com"
    endpoints = [
        "/api/v1/health",
        "/api/v1/summary",
        "/api/v1/hypotheses",
        "/api/v1/governance",
        "/api/v1/market-data/status",
        "/api/v1/market-data/metrics",
        "/api/v1/market-data/symbols",
        "/api/v1/validation/status",
        "/api/v1/workspace/summary",
        "/api/v1/research/graph/summary",
        "/api/v1/research/ranking"
    ]
    results = {}
    print("=== QUERYING ALL REST ENDPOINTS ===")
    for ep in endpoints:
        url = base_url + ep
        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GOAT-Inspector/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                elapsed = (time.time() - t0) * 1000
                data = resp.read().decode("utf-8")
                parsed = json.loads(data)
                results[ep] = {
                    "status_code": resp.status,
                    "latency_ms": round(elapsed, 2),
                    "response": parsed
                }
                print(f"[SUCCESS] {ep} - Status {resp.status} ({elapsed:.1f}ms)")
        except Exception as e:
            results[ep] = {
                "error": str(e),
                "latency_ms": round((time.time() - t0) * 1000, 2)
            }
            print(f"[FAILED] {ep} - Error: {e}")
    
    with open("scratch/rest_inspection_output.json", "w") as f:
        json.dump(results, f, indent=2)
    print("REST results saved to scratch/rest_inspection_output.json")
    return results

async def capture_telemetry_long(duration_sec=130):
    uri = "wss://project-goat.onrender.com/ws/telemetry"
    print(f"\n=== CONNECTING TO WEBSOCKET: {uri} ===")
    all_frames = []
    checkpoint_frames = {}
    
    async with websockets.connect(uri) as ws:
        print("Connected to WebSocket stream successfully!")
        t_start = time.time()
        
        frame_idx = 0
        last_print = 0
        while time.time() - t_start < duration_sec:
            msg = await asyncio.wait_for(ws.recv(), timeout=10)
            t_curr = time.time()
            elapsed = t_curr - t_start
            data = json.loads(msg)
            frame_entry = {
                "frame_index": frame_idx,
                "elapsed_sec": round(elapsed, 2),
                "timestamp_recv": t_curr,
                "payload": data
            }
            all_frames.append(frame_entry)
            
            # Checkpoint at ~0, ~30, ~60, ~120
            if "T0" not in checkpoint_frames:
                checkpoint_frames["T0"] = frame_entry
                print(f"[T0 / {elapsed:.1f}s] ticks={data.get('ticks_processed')} rate={data.get('market_state',{}).get('tick_rate')} candles={data.get('candles_closed')} fvs={data.get('feature_vectors_generated')} latency={data.get('pipeline_latency_ms')}ms")
            elif elapsed >= 30 and "T+30" not in checkpoint_frames:
                checkpoint_frames["T+30"] = frame_entry
                print(f"[T+30 / {elapsed:.1f}s] ticks={data.get('ticks_processed')} rate={data.get('market_state',{}).get('tick_rate')} candles={data.get('candles_closed')} fvs={data.get('feature_vectors_generated')} latency={data.get('pipeline_latency_ms')}ms")
            elif elapsed >= 60 and "T+60" not in checkpoint_frames:
                checkpoint_frames["T+60"] = frame_entry
                print(f"[T+60 / {elapsed:.1f}s] ticks={data.get('ticks_processed')} rate={data.get('market_state',{}).get('tick_rate')} candles={data.get('candles_closed')} fvs={data.get('feature_vectors_generated')} latency={data.get('pipeline_latency_ms')}ms")
            elif elapsed >= 120 and "T+120" not in checkpoint_frames:
                checkpoint_frames["T+120"] = frame_entry
                print(f"[T+120 / {elapsed:.1f}s] ticks={data.get('ticks_processed')} rate={data.get('market_state',{}).get('tick_rate')} candles={data.get('candles_closed')} fvs={data.get('feature_vectors_generated')} latency={data.get('pipeline_latency_ms')}ms")
            
            if elapsed - last_print >= 10:
                last_print = elapsed
                print(f"  [T+{elapsed:.0f}s] frames_received={len(all_frames)} ticks={data.get('ticks_processed')} rate={data.get('market_state',{}).get('tick_rate')}")
                
            frame_idx += 1
            
    with open("scratch/telemetry_frames_output.json", "w") as f:
        json.dump({
            "total_frames": len(all_frames),
            "checkpoints": checkpoint_frames,
            "first_frame": all_frames[0] if all_frames else None,
            "last_frame": all_frames[-1] if all_frames else None,
            "sample_consecutive_10": all_frames[:10]
        }, f, indent=2)
    print("Telemetry stream results saved to scratch/telemetry_frames_output.json")

if __name__ == "__main__":
    check_rest_endpoints()
    asyncio.run(capture_telemetry_long(130))
