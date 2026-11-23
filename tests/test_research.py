import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent.verifier import validate
def test_unknown_flags_human():
    r={"id":1,"app":"Demo","category":"Demo","what_it_does":"Demo",
       "auth_methods":["Unknown"],"access_model":"unknown","api_type":"unknown",
       "api_breadth":"unknown","mcp_status":"unknown","buildability":"unknown",
       "main_blocker":"Unknown","evidence":[],"confidence":"low"}
    assert validate(r)
    assert r["human_review_required"] is True
