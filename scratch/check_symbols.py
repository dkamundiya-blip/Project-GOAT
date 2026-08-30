import urllib.request, json
req = urllib.request.Request('https://project-goat-production.up.railway.app/api/v1/market-data/symbols', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    for s in data.get('data', {}).get('symbols', []):
        sym = s.get('symbol')
        price = s.get('live_price')
        freq = s.get('tick_frequency')
        lat = s.get('latency_ms')
        print(f'{sym}: price={price} freq={freq} lat={lat}ms')
