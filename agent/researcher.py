"""
Evidence-first app research agent.
Uses OpenAI Responses API web_search for official documentation discovery.
Optional Composio MCP session bootstrap is provided separately in composio_mcp.py.
"""
import os, json, argparse, time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

SYSTEM = """You are a cautious SaaS API product researcher. Research only the named app.
Prioritize official developer docs, official pricing/access docs, and official GitHub repos.
Never infer that a feature does not exist merely because you cannot find it.
Use 'unknown' or 'none_found' when evidence is insufficient. Distinguish no public API
from no evidence found. Cite exact URLs for each material claim. Avoid guessing auth
and self-serve requirements. Access model definitions:
self-serve_free = developer can obtain usable credentials without paying;
self-serve_trial = trial/free trial can obtain credentials;
paid_required = paid subscription is needed for API access;
admin_approval = workspace/org admin must approve or install;
partner_or_sales_gated = sales/partner approval or contract is required;
unknown = docs do not establish it.
MCP status: official, community, none_found, unknown. 'none_found' means search was
performed but no credible server listing was found; do not claim absolute nonexistence.
API breadth: broad (many core resources), moderate (several domains), narrow (few endpoints).
Buildability considers API surface, auth accessibility, scopes/limits, terms and stability.
Return JSON only, matching the requested schema. Use confidence low if access details unclear."""

def research_one(client, app):
    prompt = f"""Research this app for an agent-toolkit buildability assessment.
App: {app['app']}
Category: {app['category']}
Official website: {app['website']}
Documentation starting point: {app['docs_hint']}
Return one JSON object with keys:
id, app, category, what_it_does, auth_methods, access_model, api_type, api_breadth,
mcp_status, buildability, main_blocker, evidence, confidence,
human_review_required, notes.
Evidence must be a list of objects: url, claim_supported, source_type.
For access/auth/API/MCP claims, use direct official evidence wherever possible.
Set human_review_required true if pricing/access or API status is ambiguous.
Do not invent evidence or claim you tested an API unless you actually did."""
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.4"),
        tools=[{"type":"web_search"}],
        input=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}],
        text={"format":{"type":"json_object"}}
    )
    raw = response.output_text
    result = json.loads(raw)
    result["id"] = app["id"]
    result["app"] = app["app"]
    result["category"] = app["category"]
    result["docs_hint"] = app["docs_hint"]
    result["research_run_id"] = getattr(response, "id", None)
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--limit",type=int,default=100)
    parser.add_argument("--start",type=int,default=1)
    parser.add_argument("--delay",type=float,default=1.0)
    args=parser.parse_args()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY in .env before running.")
    client=OpenAI()
    apps=json.loads((ROOT/"data/apps.json").read_text())
    out_path=ROOT/"data/research_results.json"
    existing=json.loads(out_path.read_text()) if out_path.exists() else []
    done={x.get("id") for x in existing}
    selected=[a for a in apps if a["id"]>=args.start and a["id"] not in done][:args.limit]
    for app in selected:
        try:
            item=research_one(client,app)
            existing.append(item)
            print(f"[OK] {app['id']:03} {app['app']} | {item.get('confidence')}")
        except Exception as e:
            existing.append({"id":app["id"],"app":app["app"],"category":app["category"],
                "docs_hint":app["docs_hint"],"error":str(e),"confidence":"low",
                "human_review_required":True})
            print(f"[ERR] {app['id']:03} {app['app']}: {e}")
        out_path.write_text(json.dumps(sorted(existing,key=lambda x:x["id"]),indent=2),encoding="utf-8")
        time.sleep(args.delay)
    print(f"Saved {len(existing)} records to {out_path}")

if __name__=="__main__":
    main()
