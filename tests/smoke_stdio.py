"""End-to-end stdio smoke test that does not connect to CAD."""

import asyncio
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


ROOT = Path(__file__).resolve().parents[1]


async def main() -> int:
    transport = StdioTransport(
        command=sys.executable,
        args=[str(ROOT / "src" / "server.py")],
        env={"PYTHONUTF8": "1"},
        cwd=str(ROOT),
    )
    async with Client(transport) as client:
        tools = await client.list_tools()
        capabilities = await client.call_tool(
            "zwcad_get_capabilities", {"probe_cad": False}
        )
    names = {tool.name for tool in tools}
    required = {"zwcad_get_capabilities", "zwcad_draw_entity", "zwcad_mech_diagnose"}
    missing = sorted(required - names)
    if len(names) != 39 or missing:
        print(f"FAIL tools={len(names)} missing={missing}")
        return 1
    if capabilities.is_error:
        print("FAIL zwcad_get_capabilities returned an MCP error")
        return 1
    print("PASS stdio tool discovery: 39 local tools")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
