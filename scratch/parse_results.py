import json

def parse_data():
    with open('scratch/rest_inspection_output.json', 'r') as f:
        rest = json.load(f)

    print("================ REST API DETAILED RESULTS ================")
    for ep, val in rest.items():
        print(f"Endpoint: {ep}")
        status = val.get("status_code", val.get("error"))
        lat = val.get("latency_ms")
        print(f"  HTTP Status / Error: {status} (Latency: {lat}ms)")
        if "response" in val:
            resp = val["response"]
            if isinstance(resp, dict):
                if "data" in resp:
                    print(f"  Data Summary: {json.dumps(resp['data'], indent=4)}")
                else:
                    print(f"  Full JSON: {json.dumps(resp, indent=4)}")
            else:
                print(f"  Raw: {resp}")
        print("-" * 50)

    with open('scratch/telemetry_frames_output.json', 'r') as f:
        ws = json.load(f)

    print("\n================ WEBSOCKET STREAM ANALYSIS ================")
    print(f"Total Frames Captured: {ws.get('total_frames')}")
    print("\nCheckpoints (T0, T+30, T+60, T+120):")
    for cp_name, cp in ws.get('checkpoints', {}).items():
        p = cp['payload']
        ms = p.get('market_state', {})
        print(f"--- {cp_name} (Elapsed: {cp['elapsed_sec']}s) ---")
        print(f"  ticks_processed:           {p.get('ticks_processed')}")
        print(f"  tick_rate:                 {ms.get('tick_rate')}")
        print(f"  candles_closed:            {p.get('candles_closed')}")
        print(f"  feature_vectors_generated: {p.get('feature_vectors_generated')}")
        print(f"  edges_evaluated:           {p.get('edges_evaluated')}")
        print(f"  active_edges:              {p.get('edges')}")
        print(f"  pipeline_latency_ms:       {p.get('pipeline_latency_ms')}")
        print(f"  market_regime:             {ms.get('regime')} / {ms.get('trend')} / {ms.get('volatility')} / {ms.get('momentum')}")
        print(f"  system_health:             {p.get('system_health', {}).get('overall_status')}")

    print("\n================ FIRST TELEMETRY FRAME ================")
    print(json.dumps(ws.get('first_frame', {}).get('payload', {}), indent=2))

    print("\n================ LAST TELEMETRY FRAME ================")
    print(json.dumps(ws.get('last_frame', {}).get('payload', {}), indent=2))

    print("\n================ CONSECUTIVE 10 FRAMES SUMMARY ================")
    for f in ws.get('sample_consecutive_10', []):
        idx = f.get('frame_index')
        el = f.get('elapsed_sec')
        p = f.get('payload', {})
        ms = p.get('market_state', {})
        print(f"Frame #{idx:02d} (+{el:5.2f}s) | ticks={p.get('ticks_processed'):6d} | rate={ms.get('tick_rate'):4.1f} | candles={p.get('candles_closed'):2d} | fvs={p.get('feature_vectors_generated'):2d} | edges={len(p.get('edges', []))} | latency={p.get('pipeline_latency_ms'):.3f}ms")

if __name__ == '__main__':
    parse_data()
