import json, collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"data/research_results.json"
rows=json.loads(p.read_text()) if p.exists() else []
def counts(key):
    c=collections.Counter(str(r.get(key,"unknown")) for r in rows)
    return dict(c.most_common())
out={"records":len(rows),"auth_methods":counts("auth_methods"),
     "access_model":counts("access_model"),"api_type":counts("api_type"),
     "api_breadth":counts("api_breadth"),"mcp_status":counts("mcp_status"),
     "buildability":counts("buildability"),
     "human_review_required":sum(bool(r.get("human_review_required",True)) for r in rows)}
(ROOT/"data/insights.json").write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
