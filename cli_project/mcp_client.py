import sys
import asyncio
from typing import Optional, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        _stdio, _write = stdio_transport
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(_stdio, _write)
        )
        await self._session.initialize()

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized or cache not populated. Call connect_to_server first."
            )
        return self._session

    async def list_tools(self) -> list[types.Tool]:
        """Return a list of tools defined by the MCP server"""
        response = await self.session().list_tools()
        return response.tools

    async def call_tool(
        self, tool_name: str, tool_input: dict
    ) -> types.CallToolResult | None:
        """Call a particular tool and return the result"""
        response = await self.session().call_tool(tool_name, arguments=tool_input)
        return response

    async def list_prompts(self) -> list[types.Prompt]:
        """Return a list of prompts defined by the MCP server"""
        response = await self.session().list_prompts()
        return response.prompts

    async def get_prompt(self, prompt_name, args: dict[str, str]):
        """Get a particular prompt defined by the MCP server"""
        response = await self.session().get_prompt(prompt_name, arguments=args)
        return response.messages

    async def read_resource(self, uri: str) -> Any:
        """Read a resource, parse the contents and return it"""
        response = await self.session().read_resource(uri)
        # Return the text content of the first resource
        if response.contents:
            first_content = response.contents[0]
            if hasattr(first_content, 'text'):
                return first_content.text
        return None

    async def cleanup(self):
        """Clean up resources properly to avoid Windows pipe warnings"""
        try:
            await self._exit_stack.aclose()
        except Exception:
            pass  # Ignore errors during cleanup
        finally:
            self._session = None
            # Give time for Windows to clean up pipes
            if sys.platform == "win32":
                await asyncio.sleep(0.1)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()


# For testing
async def main():
    async with MCPClient(
        # If using Python without UV, update command to 'python' and remove "run" from args.
        command="uv",
        args=["run", "mcp_server.py"],
    ) as _client:
        result = await _client.list_tools()
        print("Tools:")
        for tool in result:
            print(f"- {tool.name}: {tool.description}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # Run and properly close event loop to avoid warnings
    try:
        asyncio.run(main())
    finally:
        # Clean up any remaining tasks on Windows
        if sys.platform == "win32":
            import time
            time.sleep(0.2)  # Give Windows time to clean up pipes
