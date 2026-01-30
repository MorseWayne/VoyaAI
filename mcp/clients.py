"""
MCP (Model Context Protocol) client integrations.
Connects to various MCP services for travel planning.
"""
import asyncio
import logging
from typing import Optional
from dataclasses import dataclass

import httpx
from langchain_core.tools import BaseTool, tool

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
            xhs_key=settings.xhs_smithery_key,
            xhs_profile=settings.xhs_profile,
        )
    
    def is_amap_available(self) -> bool:
        return bool(self.amap_url)
    
    def is_weather_available(self) -> bool:
        return bool(self.weather_url)
    
    def is_xhs_available(self) -> bool:
        return bool(self.xhs_key and self.xhs_profile)


# ============== Tool Implementations ==============

@tool
async def search_xiaohongshu(query: str) -> str:
    """
    Search Xiaohongshu (Little Red Book) for travel guides and tips.
    
    Args:
        query: Search query for travel content (e.g., "日本大阪旅游攻略")
    
    Returns:
        Travel guides and tips from Xiaohongshu users.
    """
    settings = get_settings()
    
    if not settings.xhs_smithery_key:
        return "Xiaohongshu MCP service not configured. Please set XHS_SMITHERY_KEY."
    
    try:
        # This would connect to the Xiaohongshu MCP via Smithery
        # For now, return a placeholder indicating the tool is available
        logger.info(f"Searching Xiaohongshu for: {query}")
        
        # In production, this would call the actual MCP service
        # via stdio transport using npx @smithery/cli
        return f"[Xiaohongshu Search] Query: {query} - MCP service would return travel guides here."
        
    except Exception as e:
        logger.error(f"Error searching Xiaohongshu: {e}")
        return f"Error searching Xiaohongshu: {str(e)}"


@tool
async def get_weather_forecast(city: str, date: str) -> str:
    """
    Get weather forecast for a city on a specific date.
    
    Args:
        city: City name (e.g., "大阪", "Tokyo")
        date: Date for forecast (e.g., "2025-06-20")
    
    Returns:
        Weather information including temperature, conditions, and recommendations.
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


@tool
async def plan_route(origin: str, destination: str, mode: str = "transit") -> str:
    """
    Plan a route between two locations using Amap (Gaode Maps).
    
    Args:
        origin: Starting location (e.g., "大阪城")
        destination: Destination location (e.g., "环球影城")
        mode: Transportation mode - "transit", "driving", or "walking"
    
    Returns:
        Route information including directions, duration, and transportation options.
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


@tool
async def search_poi(keyword: str, city: str, category: str = "") -> str:
    """
    Search for points of interest using Amap.
    
    Args:
        keyword: Search keyword (e.g., "拉面", "酒店")
        city: City to search in (e.g., "大阪")
        category: Optional category filter (e.g., "餐饮", "住宿")
    
    Returns:
        List of matching locations with details.
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


def get_mcp_tools() -> list[BaseTool]:
    """Get all available MCP tools."""
    return [
        search_xiaohongshu,
        get_weather_forecast,
        plan_route,
        search_poi,
    ]
