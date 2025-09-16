# scripts/list_mcp_tools.py
import asyncio
import os
from dotenv import load_dotenv

# Prefer new class name, but fall back if your ADK version is older
try:
    from google.adk.tools.mcp_tool.mcp_toolset import McpToolset as _Toolset, StdioServerParameters
except ImportError:
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset as _Toolset, StdioServerParameters

from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams

ROOT = os.path.dirname(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(ROOT, ".env"))

async def main():
    tools, exit_stack = await _Toolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "mongodb-mcp-server@latest"],
                env={
                    "MDB_MCP_API_CLIENT_ID": os.getenv("MDB_MCP_API_CLIENT_ID", ""),
                    "MDB_MCP_API_CLIENT_SECRET": os.getenv("MDB_MCP_API_CLIENT_SECRET", ""),
                },
            )
        )
    )
    async with exit_stack:
        print(f"Discovered {len(tools)} tool(s):")
        for t in tools:
            desc = getattr(t, "description", "") or ""
            print(f"- {t.name}{': ' + desc if desc else ''}")

if __name__ == "__main__":
    asyncio.run(main())
