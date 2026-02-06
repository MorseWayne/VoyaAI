"""
MCP (Model Context Protocol) client integrations.
Connects to various MCP services for travel planning.

This module implements a standard MCP client pattern:
- Dynamic tool discovery from MCP servers
- Direct tool call forwarding (no wrapper functions)
- Automatic schema conversion for OpenAI function calling
"""
import logging
import json
from typing import Any
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from config import get_settings


# Custom httpx client factory that bypasses proxy
def create_no_proxy_http_client(
    headers: dict[str, str] | None = None,
    timeout: httpx.Timeout | None = None,
    auth: httpx.Auth | None = None,
) -> httpx.AsyncClient:
    """Create an httpx client that bypasses system proxy settings."""
    return httpx.AsyncClient(
        headers=headers,
        timeout=timeout,
        auth=auth,
        trust_env=False,  # Don't read proxy from environment variables
    )

logger = logging.getLogger(__name__)


# ============== MCP Tool Schema Conversion ==============

def mcp_tool_to_openai_schema(tool) -> dict:
    """Convert MCP tool definition to OpenAI function calling schema."""
    # MCP tool has: name, description, inputSchema
    input_schema = tool.inputSchema if hasattr(tool, 'inputSchema') else {}
    
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or f"Call {tool.name} tool",
            "parameters": input_schema if input_schema else {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }


# ============== MCP Service Client ==============

@dataclass
class MCPService:
    """Generic MCP service client with dynamic tool discovery."""
    
    name: str
    url: str
    _tools_cache: list[dict] = field(default_factory=list, repr=False)
    _tools_loaded: bool = field(default=False, repr=False)
    
    async def _get_session(self):
        """Create a new MCP session."""
        return streamablehttp_client(self.url)
    
    async def list_tools(self) -> list[dict]:
        """
        Get available tools from the MCP server.
        Returns OpenAI function calling schema format.
        """
        if self._tools_loaded:
            return self._tools_cache
        
        try:
            logger.info(f"[{self.name}] 🔄 Discovering tools from {self.url}...")
            
            async with streamablehttp_client(
                self.url,
                httpx_client_factory=create_no_proxy_http_client
            ) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_result = await session.list_tools()
                    
                    self._tools_cache = [
                        mcp_tool_to_openai_schema(tool) 
                        for tool in tools_result.tools
                    ]
                    self._tools_loaded = True
                    
                    tool_names = [t["function"]["name"] for t in self._tools_cache]
                    logger.info(f"[{self.name}] ✅ Discovered {len(tool_names)} tools: {tool_names}")
                    
                    return self._tools_cache
                    
        except Exception as e:
            logger.error(f"[{self.name}] ❌ Failed to discover tools: {type(e).__name__}: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """
        Call a tool on the MCP server.
        Returns the result as a string.
        """
        logger.info(f"[{self.name}] 📤 Calling tool: {tool_name}")
        logger.debug(f"[{self.name}] Arguments: {json.dumps(arguments, ensure_ascii=False)}")
        
        try:
            async with streamablehttp_client(
                self.url,
                httpx_client_factory=create_no_proxy_http_client
            ) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    result = await session.call_tool(tool_name, arguments)
                    
                    if result.isError:
                        error_msg = str(result.content)
                        logger.error(f"[{self.name}] ❌ Tool returned error: {error_msg}")
                        return f"MCP Error: {error_msg}"
                    
                    # Extract text content from result
                    content = "\n".join([
                        c.text for c in result.content 
                        if hasattr(c, 'text')
                    ])
                    
                    logger.info(f"[{self.name}] ✅ Tool {tool_name} completed, {len(content)} chars")
                    logger.debug(f"[{self.name}] Response preview: {content[:200]}..." if len(content) > 200 else f"[{self.name}] Response: {content}")
                    
                    return content
                    
        except httpx.ConnectError as e:
            logger.error(f"[{self.name}] ❌ Connection failed: {e}")
            return f"Error connecting to {self.name}: {str(e)}"
        except httpx.TimeoutException:
            logger.error(f"[{self.name}] ❌ Request timeout")
            return f"{self.name} request timed out."
        except Exception as e:
            logger.error(f"[{self.name}] ❌ Failed to call tool: {type(e).__name__}: {e}")
            return f"Error calling {self.name}: {str(e)}"
    
    def clear_cache(self):
        """Clear the tools cache to force re-discovery."""
        self._tools_cache = []
        self._tools_loaded = False


# ============== MCP Client Manager ==============

@dataclass
class MCPClientManager:
    """Manages multiple MCP service connections."""
    
    services: dict[str, MCPService] = field(default_factory=dict)
    
    @classmethod
    def from_settings(cls) -> "MCPClientManager":
        """Create MCPClientManager from settings."""
        settings = get_settings()
        manager = cls()
        
        # Register configured MCP services
        # Temporarily disabled Xiaohongshu per user request
        # if settings.xhs_mcp_url:
        #     manager.register_service("xiaohongshu", settings.xhs_mcp_url)
        
        if settings.weather_mcp_url:
            manager.register_service("weather", settings.weather_mcp_url)
        
        if settings.amap_mcp_url:
            manager.register_service("amap", settings.amap_mcp_url)
        
        return manager
    
    def register_service(self, name: str, url: str):
        """Register a new MCP service."""
        self.services[name] = MCPService(name=name, url=url)
        logger.info(f"[MCPManager] Registered service: {name} -> {url}")
    
    def get_service(self, name: str) -> MCPService | None:
        """Get a registered MCP service."""
        return self.services.get(name)
    
    def is_available(self, name: str) -> bool:
        """Check if a service is registered."""
        return name in self.services
    
    async def list_all_tools(self) -> list[dict]:
        """Get all tools from all registered MCP services."""
        all_tools = []
        
        for name, service in self.services.items():
            try:
                tools = await service.list_tools()
                # Add service prefix to tool names to avoid conflicts
                for tool in tools:
                    # Store original name for routing
                    tool["_mcp_service"] = name
                all_tools.extend(tools)
            except Exception as e:
                logger.error(f"[MCPManager] Failed to get tools from {name}: {e}")
        
        return all_tools
    
    async def call_tool(self, service_name: str, tool_name: str, arguments: dict[str, Any]) -> str:
        """Call a tool on a specific MCP service."""
        service = self.get_service(service_name)
        if not service:
            return f"Error: MCP service '{service_name}' not found"
        
        return await service.call_tool(tool_name, arguments)


# ============== Global Manager Instance ==============

_manager: MCPClientManager | None = None


def get_mcp_manager() -> MCPClientManager:
    """Get or create the global MCP client manager."""
    global _manager
    if _manager is None:
        _manager = MCPClientManager.from_settings()
    return _manager


async def refresh_mcp_manager() -> MCPClientManager:
    """Refresh the MCP client manager with current settings."""
    global _manager
    _manager = MCPClientManager.from_settings()
    return _manager


# ============== Convenience Functions ==============

async def call_mcp_tool(service_name: str, tool_name: str, arguments: dict[str, Any]) -> str:
    """
    Call a tool on an MCP service.
    
    Args:
        service_name: Name of the MCP service (e.g., "xiaohongshu", "weather", "amap")
        tool_name: Name of the tool to call
        arguments: Arguments to pass to the tool
        
    Returns:
        Tool result as a string
    """
    manager = get_mcp_manager()
    return await manager.call_tool(service_name, tool_name, arguments)


async def get_all_mcp_tools() -> list[dict]:
    """
    Get all available tools from all MCP services.
    Returns OpenAI function calling schema format.
    """
    manager = get_mcp_manager()
    return await manager.list_all_tools()


async def get_service_tools(service_name: str) -> list[dict]:
    """
    Get available tools from a specific MCP service.
    Returns OpenAI function calling schema format.
    """
    manager = get_mcp_manager()
    service = manager.get_service(service_name)
    if not service:
        return []
    return await service.list_tools()


# ============== Backward Compatibility ==============
# These functions maintain backward compatibility with existing code

async def get_tools_schema() -> list[dict]:
    """
    Get OpenAI function calling schema for all available MCP tools.
    This function dynamically fetches tools from registered MCP services.
    """
    return await get_all_mcp_tools()


async def execute_tool(tool_name: str, arguments: dict[str, Any]) -> str:
    """
    Execute a tool by name.
    Routes the call to the appropriate MCP service.
    
    Note: This function tries to find the tool in registered services.
    For better performance, use call_mcp_tool() with explicit service name.
    """
    manager = get_mcp_manager()
    
    # Try each service to find the tool
    for service_name, service in manager.services.items():
        try:
            tools = await service.list_tools()
            tool_names = [t["function"]["name"] for t in tools]
            
            if tool_name in tool_names:
                return await service.call_tool(tool_name, arguments)
                
        except Exception as e:
            logger.debug(f"[MCPManager] Service {service_name} doesn't have tool {tool_name}: {e}")
            continue
    
    return f"Error: Tool '{tool_name}' not found in any registered MCP service"
