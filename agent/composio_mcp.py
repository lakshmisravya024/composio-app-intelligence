"""Optional Composio MCP session bootstrap; requires a Composio project API key."""
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()
if not os.getenv("COMPOSIO_API_KEY"):
    raise SystemExit("Set COMPOSIO_API_KEY in .env")
composio = Composio()
# The Composio session exposes its tool-discovery and execution interface over MCP.
# Use the URL and headers exactly as returned; never construct the URL manually.
session = composio.create(user_id="app-research-agent", mcp=True)
print("Composio MCP session ready")
print("MCP URL:", session.mcp.url)
print("MCP headers:", session.mcp.headers)
print("Keep these values private. Do not commit them.")
