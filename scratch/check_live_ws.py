import asyncio
import json
import time
import websockets

async def timed_capture():
    uri = 'wss://project-goat.onrender.com/ws/telemetry'
    print(f"Connecting to {uri}...")
    async with websockets.connect(uri) as ws:
        print("Connected!")
        
        # Capture Frame 1 (T0)
        msg = await ws.recv()
        t0 = json.loads(msg)
        t0_time = time.time()
        print(f"\n=== T0 (Frame 1) ===")
        print(f"  ticks_processed:          {t0.get('ticks_processed')}")
        print(f"  candles_closed:            {t0.get('candles_closed')}")
        print(f"  feature_vectors_generated: {t0.get('feature_vectors_generated')}")
        print(f"  edges_evaluated:           {t0.get('edges_evaluated')}")
        print(f"  edges:                     {t0.get('edges')}")
        print(f"  pipeline_latency_ms:       {t0.get('pipeline_latency_ms')}")
        ms = t0.get('market_state', {})
        print(f"  tick_rate:                 {ms.get('tick_rate')}")
        print(f"  regime:                    {ms.get('regime')}")
        print(f"  trend:                     {ms.get('trend')}")
        print(f"  volatility:               {ms.get('volatility')}")
        print(f"  momentum:                  {ms.get('momentum')}")
        stats = t0.get('statistics', {})
        print(f"  atr:                       {stats.get('atr')}")
        print(f"  realized_volatility:       {stats.get('realized_volatility')}")
        print(f"  rolling_vwap:              {stats.get('rolling_vwap')}")
        print(f"  spread_variance:           {stats.get('spread_variance')}")
        sh = t0.get('system_health', {})
        print(f"  overall_status:            {sh.get('overall_status')}")
        components = sh.get('components', {})
        for name, comp in components.items():
            print(f"    {name}: {comp.get('status')} ({comp.get('latency_ms')}ms, errors={comp.get('error_count')})")
        
        # Capture frames for 30 seconds
        print("\n--- Waiting 30 seconds, capturing every 5 seconds ---")
        frame_count = 1
        while time.time() - t0_time < 35:
            msg = await asyncio.wait_for(ws.recv(), timeout=6)
            data = json.loads(msg)
            frame_count += 1
            elapsed = time.time() - t0_time
            if int(elapsed) % 5 < 1 or elapsed >= 29:
                print(f"  T+{elapsed:.0f}s: ticks={data.get('ticks_processed')} rate={data.get('market_state',{}).get('tick_rate')} candles={data.get('candles_closed')} fvs={data.get('feature_vectors_generated')} edges={len(data.get('edges',[]))} latency={data.get('pipeline_latency_ms')}ms")
        
        # Capture final frame
        msg = await ws.recv()
        tf = json.loads(msg)
        print(f"\n=== FINAL FRAME (#{frame_count+1}) ===")
        print(f"  ticks_processed:          {tf.get('ticks_processed')}")
        print(f"  candles_closed:            {tf.get('candles_closed')}")
        print(f"  feature_vectors_generated: {tf.get('feature_vectors_generated')}")
        print(f"  edges_evaluated:           {tf.get('edges_evaluated')}")
        print(f"  edges:                     {tf.get('edges')}")
        print(f"  pipeline_latency_ms:       {tf.get('pipeline_latency_ms')}")
        ms = tf.get('market_state', {})
        print(f"  tick_rate:                 {ms.get('tick_rate')}")
        print(f"  regime:                    {ms.get('regime')}")
        
        # Compute deltas
        delta_ticks = tf.get('ticks_processed', 0) - t0.get('ticks_processed', 0)
        print(f"\n=== DELTA ANALYSIS ===")
        print(f"  Tick delta over ~30s:      {delta_ticks}")
        print(f"  Candle delta:              {tf.get('candles_closed', 0) - t0.get('candles_closed', 0)}")
        print(f"  FV delta:                  {tf.get('feature_vectors_generated', 0) - t0.get('feature_vectors_generated', 0)}")
        print(f"  Total frames received:     {frame_count+1}")

asyncio.run(timed_capture())
