import csv, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/"data/research_results.json").read_text())
fields=["id","app","category","what_it_does","auth_methods","access_model","api_type",
        "api_breadth","mcp_status","buildability","main_blocker","confidence",
        "human_review_required","notes","evidence"]
with (ROOT/"data/research_results.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
    w.writeheader()
    for row in rows:
        item=row.copy()
        for key in ["auth_methods","evidence"]:
            item[key]=json.dumps(item.get(key,[]),ensure_ascii=False)
        w.writerow(item)
print(f"Exported {len(rows)} records.")
