import urllib.request
import re
import json

def inspect_bundle():
    js_url = 'https://project-goat-ai.netlify.app/assets/index-Bct2OBGA.js'
    print(f"Fetching bundle from: {js_url}")
    req = urllib.request.Request(js_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        js_text = resp.read().decode('utf-8')

    print(f"JS Bundle Size: {len(js_text)} bytes")

    prohibited = [
        "0.942",
        "EDC_VOL_CLUSTER_STABILITY_01",
        "EDG_BOOM_",
        "42 hypotheses",
        "1250 evidence",
        "18 validated",
        "Validation Session PASSED",
        "fake",
        "mock"
    ]

    print("\n=== SCIENTIFIC INTEGRITY AUDIT OF DEPLOYED BUNDLE ===")
    for p in prohibited:
        found = p in js_text
        print(f"Checking '{p}': {'FOUND (REGRESSION!)' if found else 'CLEAN (NOT FOUND)'}")

    print("\n=== WEBSOCKET & API ENDPOINTS IN BUNDLE ===")
    ws_matches = set(re.findall(r'wss?://[a-zA-Z0-9\.\-\:\/]+', js_text))
    for ws in ws_matches:
        print(f"  WebSocket URL: {ws}")

    api_matches = set(re.findall(r'/api/v1/[a-zA-Z0-9\/\-_]+', js_text))
    for api in sorted(api_matches):
        print(f"  API Endpoint: {api}")

    print("\n=== NAVIGATION & PAGE ROUTES IN BUNDLE ===")
    routes = set(re.findall(r'path:\s*["\']([^"\']+)["\']', js_text))
    print(f"  Routes: {routes}")

if __name__ == '__main__':
    inspect_bundle()
