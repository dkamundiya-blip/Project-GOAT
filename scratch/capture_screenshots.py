import os
import subprocess
import time

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_DIR = r"C:\Users\The Technologist Fx\Desktop\Project Goat\scratch\screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

routes = [
    ("overview", "https://project-goat-ai.netlify.app/"),
    ("edge_discovery", "https://project-goat-ai.netlify.app/edge-discovery"),
    ("live_validation", "https://project-goat-ai.netlify.app/live-validation"),
    ("research", "https://project-goat-ai.netlify.app/research"),
    ("evidence", "https://project-goat-ai.netlify.app/evidence"),
    ("experiments", "https://project-goat-ai.netlify.app/experiments"),
    ("statistics", "https://project-goat-ai.netlify.app/statistics"),
    ("governance", "https://project-goat-ai.netlify.app/governance"),
    ("knowledge_graph", "https://project-goat-ai.netlify.app/knowledge-graph"),
    ("research_intelligence", "https://project-goat-ai.netlify.app/research-intelligence"),
    ("archive", "https://project-goat-ai.netlify.app/archive"),
    ("system_telemetry", "https://project-goat-ai.netlify.app/system-health"),
    ("markets", "https://project-goat-ai.netlify.app/markets")
]

print("=== CAPTURING SCREENSHOTS OF LIVE NETLIFY DASHBOARD ===")
for name, url in routes:
    out_file = os.path.join(OUTPUT_DIR, f"{name}.png")
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1920,1080",
        "--virtual-time-budget=8000",
        f"--screenshot={out_file}",
        url
    ]
    print(f"Capturing {name} from {url}...")
    subprocess.run(cmd, check=True)
    if os.path.exists(out_file):
        size_kb = os.path.getsize(out_file) / 1024
        print(f"  [OK] Saved {out_file} ({size_kb:.1f} KB)")
    else:
        print(f"  [ERROR] Failed to save {out_file}")

print("Screenshot capture completed.")
