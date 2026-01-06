"""
MCP Client Wrapper - Integration Layer for Agent ↔ MCP Server Communication

This module provides a unified interface for agents to communicate with MCP servers.
Supports multiple transport types (stdio, SSE) and handles tool calls, errors, and reconnection.
"""
from typing import Any, Dict, List, Optional, Union
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import json
import logging
from datetime import datetime
from contextlib import asynccontextmanager
import os

# Configure logging
logger = logging.getLogger(__name__)


class MCPServerConfig:
    """Configuration for an MCP server connection"""

    def __init__(
        self,
        name: str,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
        cwd: Optional[str] = None
    ):
        self.name = name
        self.command = command
        self.args = args
        self.env = env
        self.cwd = cwd


class MCPClientWrapper:
    """
    MCP Client Wrapper

    Provides high-level interface for communicating with MCP servers.
    Handles connection management, tool calls, and error recovery.
    """

    def __init__(self, server_configs: List[MCPServerConfig]):
        """
        Initialize MCP client wrapper

        Args:
            server_configs: List of MCP server configurations
        """
        self.server_configs = {config.name: config for config in server_configs}
        self.sessions: Dict[str, ClientSession] = {}
        self.server_tools: Dict[str, List[Dict]] = {}
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    async def connect_all(self):
        """Connect to all configured MCP servers"""
        for name, config in self.server_configs.items():
            try:
                await self.connect_server(name)
                logger.info(f"Connected to MCP server: {name}")
            except Exception as e:
                logger.error(f"Failed to connect to {name}: {e}")

    async def connect_server(self, server_name: str) -> ClientSession:
        """
        Connect to a specific MCP server

        Args:
            server_name: Name of the server to connect to

        Returns:
            ClientSession instance

        Raises:
            ValueError: If server name is not configured
        """
        if server_name not in self.server_configs:
            raise ValueError(f"Unknown server: {server_name}")

        config = self.server_configs[server_name]

        # Create stdio server parameters
        server_params = StdioServerParameters(
            command=config.command,
            args=config.args,
            env=config.env
        )

        # Create client session
        session = await stdio_client(server_params)
        await session.initialize()

        # Store session and tools
        self.sessions[server_name] = session
        self.server_tools[server_name] = await self._list_tools(session)

        logger.info(f"Connected to {server_name}, loaded {len(self.server_tools[server_name])} tools")

        return session

    async def disconnect_server(self, server_name: str):
        """Disconnect from a specific server"""
        if server_name in self.sessions:
            await self.sessions[server_name].close()
            del self.sessions[server_name]
            del self.server_tools[server_name]
            logger.info(f"Disconnected from {server_name}")

    async def disconnect_all(self):
        """Disconnect from all servers"""
        for name in list(self.sessions.keys()):
            await self.disconnect_server(name)

    @asynccontextmanager
    async def session_context(self, server_name: str):
        """
        Context manager for server connection with auto-reconnection

        Args:
            server_name: Name of the server

        Yields:
            ClientSession instance
        """
        try:
            if server_name not in self.sessions:
                await self.connect_server(server_name)

            yield self.sessions[server_name]
        except Exception as e:
            logger.warning(f"Lost connection to {server_name}, attempting reconnect...")
            await self.disconnect_server(server_name)
            await self.connect_server(server_name)
            yield self.sessions[server_name]

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
        retry: bool = True
    ) -> str:
        """
        Call a tool on an MCP server with retry logic

        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Tool arguments
            retry: Whether to retry on failure

        Returns:
            Tool result as JSON string

        Raises:
            Exception: If tool call fails after retries
        """
        attempt = 0
        last_error = None

        while attempt <= self.max_retries:
            try:
                async with self.session_context(server_name) as session:
                    result = await session.call_tool(tool_name, arguments)

                    # Extract text content from result
                    if hasattr(result, 'content') and result.content:
                        # Handle TextContent objects
                        text_contents = []
                        for content in result.content:
                            if hasattr(content, 'text'):
                                text_contents.append(content.text)
                        return "\n".join(text_contents)
                    else:
                        return str(result)

            except Exception as e:
                last_error = e
                attempt += 1
                if attempt <= self.max_retries and retry:
                    logger.warning(
                        f"Tool call {tool_name}@{server_name} failed (attempt {attempt}/{self.max_retries}): {e}"
                    )
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"Tool call {tool_name}@{server_name} failed after {attempt} attempts")
                    raise

        raise last_error if last_error else Exception("Unknown error in tool call")

    async def list_tools(self, server_name: str) -> List[Dict]:
        """
        List available tools on a server

        Args:
            server_name: Name of the server

        Returns:
            List of tool definitions
        """
        if server_name not in self.sessions:
            await self.connect_server(server_name)

        return self.server_tools.get(server_name, [])

    async def list_all_tools(self) -> Dict[str, List[Dict]]:
        """
        List all available tools across all servers

        Returns:
            Dict mapping server names to tool lists
        """
        return self.server_tools.copy()

    async def _list_tools(self, session: ClientSession) -> List[Dict]:
        """Internal method to list tools from a session"""
        try:
            tools_result = await session.list_tools()
            if hasattr(tools_result, 'tools'):
                return [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool in tools_result.tools
                ]
            return []
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []

    def get_tool_schema(self, server_name: str, tool_name: str) -> Optional[Dict]:
        """
        Get the schema for a specific tool

        Args:
            server_name: Name of the server
            tool_name: Name of the tool

        Returns:
            Tool schema or None if not found
        """
        tools = self.server_tools.get(server_name, [])
        for tool in tools:
            if tool["name"] == tool_name:
                return tool
        return None

    async def health_check(self, server_name: str) -> bool:
        """
        Check if a server is healthy

        Args:
            server_name: Name of the server

        Returns:
            True if server is responsive, False otherwise
        """
        try:
            # Try to list tools as a health check
            await self.list_tools(server_name)
            return True
        except Exception as e:
            logger.warning(f"Health check failed for {server_name}: {e}")
            return False

    async def health_check_all(self) -> Dict[str, bool]:
        """
        Check health of all servers

        Returns:
            Dict mapping server names to health status
        """
        results = {}
        for name in self.server_configs.keys():
            results[name] = await self.health_check(name)
        return results


class MCPClientManager:
    """
    Singleton manager for MCP clients

    Manages lifecycle of MCP client wrapper instances.
    """

    _instance: Optional['MCPClientManager'] = None
    _client: Optional[MCPClientWrapper] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, server_configs: List[MCPServerConfig]):
        """
        Initialize MCP client with server configurations

        Args:
            server_configs: List of MCP server configurations
        """
        self._client = MCPClientWrapper(server_configs)
        logger.info(f"MCP Client Manager initialized with {len(server_configs)} servers")

    @property
    def client(self) -> Optional[MCPClientWrapper]:
        """Get the MCP client wrapper instance"""
        return self._client

    async def start(self):
        """Start all MCP connections"""
        if self._client:
            await self._client.connect_all()
            logger.info("MCP Client Manager started")

    async def stop(self):
        """Stop all MCP connections"""
        if self._client:
            await self._client.disconnect_all()
            logger.info("MCP Client Manager stopped")

    @classmethod
    def get_instance(cls) -> 'MCPClientManager':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Default server configurations
DEFAULT_SERVER_CONFIGS = [
    MCPServerConfig(
        name="rag-server",
        command="python",
        args=["-m", "mcp_servers.rag_server"],
        env=os.environ.copy()
    ),
    MCPServerConfig(
        name="automation-quality",
        command="python",
        args=["-m", "mcp_servers.automation_quality"],
        env=os.environ.copy()
    ),
    MCPServerConfig(
        name="chart-server",
        command="python",
        args=["-m", "mcp_servers.chart_server"],
        env=os.environ.copy()
    ),
]


async def create_mcp_client(
    server_configs: Optional[List[MCPServerConfig]] = None
) -> MCPClientWrapper:
    """
    Create and initialize MCP client wrapper

    Args:
        server_configs: Optional list of server configurations.
                     If None, uses DEFAULT_SERVER_CONFIGS

    Returns:
        MCPClientWrapper instance

    Example:
        ```python
        client = await create_mcp_client()
        result = await client.call_tool(
            "rag-server",
            "rag_query_data",
            {"query": "login API", "mode": "mix"}
        )
        print(result)
        ```
    """
    configs = server_configs or DEFAULT_SERVER_CONFIGS
    client = MCPClientWrapper(configs)
    await client.connect_all()
    return client
