# Composio App Intelligence

Evidence-first research pipeline for assessing whether 100 SaaS apps can become agent toolkits.

## Setup
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add OPENAI_API_KEY. Add COMPOSIO_API_KEY only if you want to bootstrap the MCP session.
```

## Run
```bash
python agent/researcher.py --limit 5
python agent/verifier.py
python analysis/insights.py
python analysis/export_csv.py
pytest -q
```
Research can be resumed; existing app IDs are skipped. Use `--start` and `--limit` to run batches.

## Composio MCP
```bash
python agent/composio_mcp.py
```
This creates a hosted Composio session and prints the MCP endpoint and headers. Treat both as secrets. The current research pass uses the OpenAI web search tool for official documentation discovery; the Composio MCP bootstrap is a separate integration point for Composio tool discovery/execution. Do not claim MCP was used for a research action unless you actually connect and invoke it.

## Accuracy / verification
The verifier enforces schema and evidence gates; it does not establish factual correctness. Human reviewers must check the sampled rows against linked official documentation and record field-level outcomes in `data/verification.json`. Never report accuracy until that review is complete.

## Data fields
See `data/schema.json`. Unknown values are explicit, and ambiguous records are routed to human review.

## Publish dashboard
Commit the reviewed `data/research_results.json`, `data/verification.json`, and `data/insights.json` so the dashboard can load them. Enable GitHub Pages from the repository's `main` branch, `/dashboard` folder. The dashboard fetches the JSON from `../data/`.
