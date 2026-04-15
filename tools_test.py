# tools_test.py
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StdioConnection

async def main():
    mcp_client = MultiServerMCPClient(
        {
            "find_healthcare_providers": StdioConnection(
                transport="stdio",
                command="uv",
                args=["run", "mcpserver.py"],
            )
        }
    )
    tools = await mcp_client.get_tools()
    print(tools)

asyncio.run(main())