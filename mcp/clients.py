"""
MCP (Model Context Protocol) client integrations.
Connects to various MCP services for travel planning.

Tools are defined as async functions with OpenAI function calling schema.
"""
import logging
import json
import os
from typing import Callable, Any
from dataclasses import dataclass

import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class MCPClientManager:
    """Manages MCP client connections."""
    
    amap_url: str = ""
    weather_url: str = ""
    xhs_key: str = ""
    xhs_profile: str = ""
    
    @classmethod
    def from_settings(cls) -> "MCPClientManager":
        """Create MCPClientManager from settings."""
        settings = get_settings()
        return cls(
            amap_url=settings.amap_mcp_url,
            weather_url=settings.weather_mcp_url,
            xhs_key=settings.xhs_cookie,
            xhs_profile=settings.xhs_mcp_dir,
        )
    
    def is_amap_available(self) -> bool:
        return bool(self.amap_url)
    
    def is_weather_available(self) -> bool:
        return bool(self.weather_url)
    
    def is_xhs_available(self) -> bool:
        return bool(self.xhs_key)


# ============== MCP Stdio Helper ==============

async def run_xhs_mcp_tool(tool_name: str, arguments: dict[str, Any]) -> str:
    """Run a tool from the Xiaohongshu MCP server via stdio."""
    settings = get_settings()
    
    if not settings.xhs_cookie:
        return "Xiaohongshu Cookie not configured. Please set XHS_COOKIE in .env."
    
    if not settings.xhs_mcp_dir:
        return "Xiaohongshu MCP directory not configured. Please set XHS_MCP_DIR in .env."

    # Prepare server parameters
    # The server is run via 'uv --directory <dir> run main.py'
    server_params = StdioServerParameters(
        command="uv",
        args=[
            "--directory",
            settings.xhs_mcp_dir,
            "run",
            "main.py"
        ],
        env={
            **os.environ,
            "XHS_COOKIE": settings.xhs_cookie,
        }
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Call the tool
                result = await session.call_tool(tool_name, arguments)
                
                if result.isError:
                    return f"MCP Error: {result.content}"
                
                # Assume content is a list of TextContent or similar
                return "\n".join([c.text for c in result.content if hasattr(c, 'text')])
                
    except Exception as e:
        logger.error(f"Failed to call Xiaohongshu MCP: {e}")
        return f"Error connecting to Xiaohongshu MCP: {str(e)}"


# ============== Tool Implementations ==============

async def search_xiaohongshu(query: str) -> str:
    """
    Search Xiaohongshu (Little Red Book) for travel guides and tips.
    """
    logger.info(f"Searching Xiaohongshu for: {query}")
    
    # Map to 'search_notes' tool in jobsonlook-xhs-mcp
    return await run_xhs_mcp_tool("search_notes", {"keyword": query})


async def get_xhs_note_content(note_id: str) -> str:
    """
    Get detailed content of a specific Xiaohongshu note.
    """
    logger.info(f"Getting Xiaohongshu note content: {note_id}")
    
    return await run_xhs_mcp_tool("get_note_content", {"note_id": note_id})


async def get_weather_forecast(city: str, date: str) -> str:
    """
    Get weather forecast for a city on a specific date.
    """
    settings = get_settings()
    
    if not settings.weather_mcp_url:
        return "Weather MCP service not configured. Please set WEATHER_MCP_URL."
    
    try:
        logger.info(f"Getting weather for {city} on {date}")
        
        # In production, this would call the Weather MCP SSE service
        async with httpx.AsyncClient(timeout=30.0) as client:
            # SSE connection would be established here
            return f"[Weather Forecast] {city} on {date} - MCP service would return weather data here."
            
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        return f"Error getting weather forecast: {str(e)}"


async def plan_route(origin: str, destination: str, mode: str = "transit") -> str:
    """
    Plan a route between two locations using Amap (Gaode Maps).
    """
    settings = get_settings()
    
    if not settings.amap_mcp_url:
        return "Amap MCP service not configured. Please set AMAP_MCP_URL."
    
    try:
        logger.info(f"Planning route from {origin} to {destination} via {mode}")
        
        # In production, this would call the Amap MCP SSE service
        async with httpx.AsyncClient(timeout=30.0) as client:
            return f"[Route Planning] {origin} → {destination} ({mode}) - MCP service would return route here."
            
    except Exception as e:
        logger.error(f"Error planning route: {e}")
        return f"Error planning route: {str(e)}"


async def search_poi(keyword: str, city: str, category: str = "") -> str:
    """
    Search for points of interest using Amap.
    """
    settings = get_settings()
    
    if not settings.amap_mcp_url:
        return "Amap MCP service not configured. Please set AMAP_MCP_URL."
    
    try:
        logger.info(f"Searching POI: {keyword} in {city}")
        
        return f"[POI Search] {keyword} in {city} - MCP service would return locations here."
            
    except Exception as e:
        logger.error(f"Error searching POI: {e}")
        return f"Error searching POI: {str(e)}"


# ============== OpenAI Function Calling Schema ==============

TOOLS_SCHEMA: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "search_xiaohongshu",
            "description": "Search Xiaohongshu (Little Red Book) for travel guides and tips.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for travel content (e.g., '日本大阪旅游攻略')"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_xhs_note_content",
            "description": "Get detailed content of a specific Xiaohongshu note using its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "string",
                        "description": "The ID of the Xiaohongshu note"
                    }
                },
                "required": ["note_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "Get weather forecast for a city on a specific date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g., '大阪', 'Tokyo')"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date for forecast (e.g., '2025-06-20')"
                    }
                },
                "required": ["city", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "plan_route",
            "description": "Plan a route between two locations using Amap (Gaode Maps).",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Starting location (e.g., '大阪城')"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination location (e.g., '环球影城')"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["transit", "driving", "walking"],
                        "description": "Transportation mode",
                        "default": "transit"
                    }
                },
                "required": ["origin", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_poi",
            "description": "Search for points of interest using Amap.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Search keyword (e.g., '拉面', '酒店')"
                    },
                    "city": {
                        "type": "string",
                        "description": "City to search in (e.g., '大阪')"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter (e.g., '餐饮', '住宿')"
                    }
                },
                "required": ["keyword", "city"]
            }
        }
    }
]


# Map function names to actual functions
TOOL_FUNCTIONS: dict[str, Callable] = {
    "search_xiaohongshu": search_xiaohongshu,
    "get_xhs_note_content": get_xhs_note_content,
    "get_weather_forecast": get_weather_forecast,
    "plan_route": plan_route,
    "search_poi": search_poi,
}


def get_tools_schema() -> list[dict]:
    """Get OpenAI function calling schema for all tools."""
    return TOOLS_SCHEMA


def get_tool_functions() -> dict[str, Callable]:
    """Get mapping of tool names to functions."""
    return TOOL_FUNCTIONS
