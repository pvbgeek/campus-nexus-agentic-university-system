"""Exercise real MCP JSON-RPC calls over a local stdio subprocess."""
from datetime import datetime, timezone
from pathlib import Path
import asyncio
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def unpack(result):
    if result.isError:
        raise RuntimeError("MCP tool returned an error")
    for block in result.content:
        if block.type == "text":
            return json.loads(block.text)
    raise RuntimeError("MCP tool returned no JSON text")


async def main():
    params = StdioServerParameters(command=sys.executable, args=["-m", "app.support_mcp"],
                                  cwd=str(ROOT), env=dict(os.environ))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]
            assert "retrieve_policy" in names and "authority_limits" in names
            limits = unpack(await session.call_tool("authority_limits", {}))
            assert limits["transaction_limit_cents"] == 10000
            assert limits["weekly_limit_cents"] == 50000
            args = dict(query="What must happen when agent refund authority is revoked?", limit=3)
            retrieved = unpack(await session.call_tool("retrieve_policy", args))
            assert any("revok" in hit["text"].lower() for hit in retrieved["matches"])
            evidence = dict(executed_at=datetime.now(timezone.utc).isoformat(), test="real-mcp-policy-retrieval", passed=True, transport="stdio",
                protocol_version=initialized.protocolVersion, available_tools=names,
                calls=[dict(tool="authority_limits", result=limits),
                       dict(tool="retrieve_policy", arguments=args, result=retrieved)])
            output = ROOT / "redteam/results/mcp-retrieval-smoke.json"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(evidence, indent=2)+"\n", encoding="utf-8")
            print("PASS: MCP discovery, authority tool, and semantic retrieval over stdio.")
            print("Evidence:", output.relative_to(ROOT))


if __name__ == "__main__":
    asyncio.run(main())
