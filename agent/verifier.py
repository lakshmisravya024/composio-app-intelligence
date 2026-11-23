"""Deterministic quality gates plus a human-review queue."""
import json, argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=["id","app","category","what_it_does","auth_methods","access_model","api_type",
          "api_breadth","mcp_status","buildability","main_blocker","evidence","confidence"]
ENUMS={
"access_model":{"self-serve_free","self-serve_trial","paid_required","admin_approval","partner_or_sales_gated","unknown"},
"api_type":{"REST","GraphQL","REST+GraphQL","SDK_only","CLI_only","No_public_API","unknown"},
"api_breadth":{"broad","moderate","narrow","unknown"},
"mcp_status":{"official","community","none_found","unknown"},
"buildability":{"ready","buildable_with_constraints","outreach_required","not_buildable","unknown"},
"confidence":{"high","medium","low"}}
def validate(record):
    errors=[]
    for k in REQUIRED:
        if k not in record: errors.append(f"missing:{k}")
    for k, allowed in ENUMS.items():
        if record.get(k) not in allowed: errors.append(f"invalid:{k}")
    ev=record.get("evidence",[])
    if not isinstance(ev,list) or not ev: errors.append("no_evidence")
    else:
        for e in ev:
            if not str(e.get("url","")).startswith("http"): errors.append("invalid_evidence_url")
    if record.get("confidence")=="high" and len(ev)<2:
        errors.append("high_confidence_requires_two_sources")
    if record.get("access_model")=="unknown" or record.get("mcp_status")=="unknown":
        record["human_review_required"]=True
    if errors: record["human_review_required"]=True
    return errors
def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",default="data/research_results.json"); a=p.parse_args()
    records=json.loads((ROOT/a.input).read_text())
    report=[]
    for r in records:
        errs=validate(r)
        report.append({"id":r.get("id"),"app":r.get("app"),"errors":errs,
                       "human_review_required":r.get("human_review_required",True)})
    (ROOT/"data/validation_report.json").write_text(json.dumps(report,indent=2))
    print(f"Validated {len(records)} records; {sum(bool(x['errors']) for x in report)} have schema/evidence issues.")
if __name__=="__main__": main()
