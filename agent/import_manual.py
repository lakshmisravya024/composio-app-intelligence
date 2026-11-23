
"""Convert manual research CSV into schema-compatible JSON."""
import csv
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "manual_research.csv"
OUTPUT = ROOT / "data" / "research_results.json"

VALID_ACCESS = {
    "self-serve_free", "self-serve_trial", "paid_required",
    "admin_approval", "partner_or_sales_gated", "unknown"
}
VALID_API = {
    "REST", "GraphQL", "REST+GraphQL", "SDK_only",
    "CLI_only", "No_public_API", "unknown"
}
VALID_BREADTH = {"broad", "moderate", "narrow", "unknown"}
VALID_MCP = {"official", "community", "none_found", "unknown"}
VALID_BUILD = {
    "ready", "buildable_with_constraints", "outreach_required",
    "not_buildable", "unknown"
}
VALID_CONFIDENCE = {"high", "medium", "low"}


def normalize(value, allowed, default="unknown"):
    value = (value or "").strip()
    return value if value in allowed else default


def normalize_auth(value):
    value = (value or "").lower()
    methods = []

    if "oauth" in value:
        methods.append("OAuth2")
    if "bearer" in value or "access token" in value:
        methods.append("Bearer/token")
    if "api key" in value or "apikey" in value:
        methods.append("API key")
    if "basic" in value:
        methods.append("Basic")

    return methods or ["Unknown"]


def make_evidence(value):
    evidence = []

    for url in (value or "").split(";"):
        url = url.strip()
        if not url:
            continue

        domain = urlparse(url).netloc.lower()
        source_type = "official_docs"

        if "github.com" in domain:
            source_type = "github"
        elif "pricing" in url.lower():
            source_type = "pricing"

        evidence.append({
            "url": url,
            "claim_supported": (
                "Official source supplied for this app. "
                "Manually verify the specific claim supported."
            ),
            "source_type": source_type
        })

    return evidence


def convert(row):
    access = normalize(row.get("access_model"), VALID_ACCESS)
    api_type = normalize(row.get("api_type"), VALID_API)
    breadth = normalize(row.get("api_breadth"), VALID_BREADTH)
    mcp = normalize(row.get("mcp_status"), VALID_MCP)
    buildability = normalize(row.get("buildability"), VALID_BUILD)
    confidence = normalize(row.get("confidence"), VALID_CONFIDENCE)

    evidence = make_evidence(row.get("evidence"))

    # Unrecognized or mixed descriptions must be reviewed.
    review = (
        access == "unknown"
        or api_type == "unknown"
        or mcp == "unknown"
        or buildability == "unknown"
        or not evidence
        or confidence == "low"
        or row.get("human_review_required", "").lower() == "true"
    )

    notes = (row.get("notes") or "").strip()
    original_access = (row.get("access_model") or "").strip()

    if original_access and access == "unknown":
        notes += (
            " | Original access description needs classification: "
            + original_access
        )

    return {
        "id": int(row["id"]),
        "app": row["app"].strip(),
        "category": row["category"].strip(),
        "what_it_does": row.get("what_it_does", "").strip(),
        "auth_methods": normalize_auth(row.get("auth_methods")),
        "access_model": access,
        "api_type": api_type,
        "api_breadth": breadth,
        "mcp_status": mcp,
        "buildability": buildability,
        "main_blocker": row.get("main_blocker", "").strip(),
        "evidence": evidence,
        "confidence": confidence,
        "human_review_required": review,
        "notes": notes.strip(" |")
    }


def main():
    with INPUT.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    records = [convert(row) for row in rows]

    OUTPUT.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Imported {len(records)} apps.")
    print(f"Saved JSON: {OUTPUT}")
    print(
        "Apps requiring human review:",
        sum(r["human_review_required"] for r in records)
    )


if __name__ == "__main__":
    main()
