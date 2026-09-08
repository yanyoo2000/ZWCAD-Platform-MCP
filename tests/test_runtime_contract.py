import asyncio
import unittest

from fastmcp import Client

import zwcad2d.server as server


class Zwcad2DServerRuntimeTests(unittest.TestCase):
    def test_local_tool_discovery_without_cad(self):
        async def run():
            async with Client(server.mcp) as client:
                tools = await client.list_tools()
                return {tool.name for tool in tools}

        tools = asyncio.run(run())
        self.assertEqual(39, len(tools))
        self.assertIn("zwcad_get_capabilities", tools)
        self.assertIn("zwcad_draw_entity", tools)
        self.assertIn("zwcad_mech_diagnose", tools)


if __name__ == "__main__":
    unittest.main()
