
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

apps_file = ROOT / "data" / "apps.json"
output_file = ROOT / "data" / "manual_research.csv"

with open(apps_file, "r", encoding="utf-8") as file:
    apps = json.load(file)

if isinstance(apps, dict):
    apps = apps.get("apps", [])

fields = [
    "id",
    "app",
    "category",
    "what_it_does",
    "auth_methods",
    "access_model",
    "api_type",
    "api_breadth",
    "mcp_status",
    "buildability",
    "main_blocker",
    "evidence",
    "confidence",
    "human_review_required",
    "notes"
]

with open(output_file, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()

    for app in apps:
        writer.writerow({
            "id": app.get("id", ""),
            "app": app.get("app", ""),
            "category": app.get("category", ""),
            "confidence": "low",
            "human_review_required": "true",
            "notes": f"Starting documentation: {app.get('docs_hint', '')}"
        })

print(f"Created research template: {output_file}")
print(f"Apps included: {len(apps)}")
