#!/usr/bin/env python3
"""
Test Script: Amap (高德地图) MCP Service

This script tests the Amap MCP integration independently.
It verifies:
1. AMAP_MCP_URL environment variable is set
2. MCP server can be connected via Streamable HTTP
3. Tools can be discovered dynamically
4. Route planning (with geocoding) and POI search work correctly

Usage:
    uv run python tests/test_amap_mcp.py
    
    # With custom origin and destination
    uv run python tests/test_amap_mcp.py "北京天安门" "北京故宫"
"""
import asyncio
import sys
import json
import re
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_utils import (
    setup_test_logging,
    print_header,
    print_section,
    print_config_info,
    print_result,
    print_summary,
    run_test,
    TestResult,
    TestStatus,
)
from config import get_settings

logger = setup_test_logging("test_amap_mcp")


async def test_config_check() -> tuple[bool, str, str]:
    """Test: Check Amap MCP configuration."""
    settings = get_settings()
    
    if not settings.amap_mcp_url:
        return False, "AMAP_MCP_URL not set", "Please set AMAP_MCP_URL in .env"
    
    url = settings.amap_mcp_url
    
    # Validate URL format
    if not (url.startswith("http://") or url.startswith("https://")):
        return False, "Invalid URL format", f"URL should start with http:// or https://: {url}"
    
    return True, "Configuration valid", f"URL: {url[:50]}..."


async def test_mcp_connection() -> tuple[bool, str, str]:
    """Test: Try to connect to Amap MCP server."""
    from mcp_services import get_mcp_manager
    
    manager = get_mcp_manager()
    service = manager.get_service("amap")
    
    if not service:
        return False, "Skipped - service not registered", ""
    
    try:
        logger.info(f"Connecting to Amap MCP server at {service.url[:50]}...")
        
        # Force refresh tools
        service.clear_cache()
        tools = await service.list_tools()
        tool_names = [t["function"]["name"] for t in tools]
        
        if not tools:
            return False, "Connected but no tools found", "Server returned empty tool list"
            
        logger.info(f"Connected! Available tools: {tool_names}")
        
        return True, f"Connected, {len(tool_names)} tools available", ", ".join(tool_names)
    
    except Exception as e:
        return False, f"Connection failed: {type(e).__name__}", str(e)


async def get_coordinates(address: str, city: str = "") -> str | None:
    """Helper: Get coordinates for an address using maps_geo tool."""
    from mcp_services import call_mcp_tool
    
    try:
        logger.info(f"Geocoding address: {address}")
        result = await call_mcp_tool("amap", "maps_geo", {
            "address": address,
            "city": city
        })
        
        # Try to parse JSON result
        try:
            # Clean up result if it contains non-JSON text
            json_str = result
            if "{" in result:
                start = result.find("{")
                end = result.rfind("}") + 1
                json_str = result[start:end]
                
            data = json.loads(json_str)
            if "geocodes" in data and len(data["geocodes"]) > 0:
                location = data["geocodes"][0]["location"]
                logger.info(f"Geocoded {address} -> {location}")
                return location
        except json.JSONDecodeError:
            pass
            
        # Try regex if JSON parsing fails
        match = re.search(r"(\d+\.\d+,\d+\.\d+)", result)
        if match:
            location = match.group(1)
            logger.info(f"Geocoded {address} -> {location} (via regex)")
            return location
            
        logger.warning(f"Could not parse coordinates from result: {result[:100]}...")
        return None
        
    except Exception as e:
        logger.error(f"Geocoding failed: {e}")
        return None


async def test_route_planning(origin: str = "北京天安门", destination: str = "北京故宫") -> tuple[bool, str, str]:
    """Test: Plan a route using Amap MCP (with Geocoding first)."""
    from mcp_services import call_mcp_tool
    
    settings = get_settings()
    if not settings.amap_mcp_url:
        return False, "Skipped - configuration missing", ""
    
    try:
        # Step 1: Geocode Origin and Destination
        logger.info(f"Planning route: {origin} → {destination}")
        
        origin_loc = await get_coordinates(origin, "北京")
        dest_loc = await get_coordinates(destination, "北京")
        
        if not origin_loc:
            return False, "Geocoding failed for origin", f"Could not get coordinates for {origin}"
        if not dest_loc:
            return False, "Geocoding failed for destination", f"Could not get coordinates for {destination}"
            
        # Step 2: Call Direction API
        tool_name = "maps_direction_driving"
        logger.info(f"Using tool: {tool_name} with {origin_loc} -> {dest_loc}")
        
        params = {
            "origin": origin_loc,
            "destination": dest_loc,
        }
        
        result = await call_mcp_tool("amap", tool_name, params)
        
        if result.startswith("Error") or "API 调用失败" in result:
            return False, "Route planning failed", result
            
        if len(result) < 50:
             return False, "Result too short", result
             
        return True, "Route planned successfully", result[:500]

    except Exception as e:
        return False, f"Route planning failed: {type(e).__name__}", str(e)


async def test_poi_search(keyword: str = "餐厅", city: str = "北京") -> tuple[bool, str, str]:
    """Test: Search for POI using Amap MCP."""
    from mcp_services import call_mcp_tool
    
    settings = get_settings()
    if not settings.amap_mcp_url:
        return False, "Skipped - configuration missing", ""
    
    try:
        logger.info(f"Searching POI: {keyword} in {city}")
        
        # Use maps_text_search for keyword search
        tool_name = "maps_text_search"
        logger.info(f"Using tool: {tool_name}")
        
        params = {
            "keywords": keyword, # Note: parameter is 'keywords' plural
            "city": city
        }
        
        result = await call_mcp_tool("amap", tool_name, params)
        
        if result.startswith("Error") or "API 调用失败" in result:
            return False, "POI search failed", result
            
        if len(result) < 50:
             return False, "Result too short", result
             
        return True, "POI found successfully", result[:500]

    except Exception as e:
        return False, f"POI search failed: {type(e).__name__}", str(e)


async def run_all_tests(origin: str = "北京天安门", destination: str = "北京故宫"):
    """Run all Amap MCP tests."""
    print_header("🗺️ Amap (高德地图) MCP Test")
    print_config_info()
    
    results = []
    
    # Test 1: Configuration check
    print_section("Test 1: Configuration Check")
    result = await run_test("Config Check", test_config_check)
    print_result(result)
    results.append(result)
    
    if result.status != TestStatus.SUCCESS:
        print("\n⚠️  Skipping remaining tests due to configuration issues.")
        print_summary(results)
        return results
    
    # Test 2: Connection & Discovery
    print_section("Test 2: MCP Connection & Tool Discovery")
    result = await run_test("MCP Connection", test_mcp_connection)
    print_result(result)
    results.append(result)
    
    if result.status != TestStatus.SUCCESS:
        print("\n⚠️  Skipping remaining tests due to connection failure.")
        print_summary(results)
        return results
    
    # Test 3: POI Search
    print_section("Test 3: POI Search")
    result = await run_test("POI Search", test_poi_search)
    print_result(result)
    results.append(result)
    
    # Test 4: Route Planning
    print_section("Test 4: Route Planning")
    result = await run_test("Route Planning", test_route_planning, origin, destination)
    print_result(result)
    results.append(result)
    
    print_summary(results)
    return results


if __name__ == "__main__":
    origin = sys.argv[1] if len(sys.argv) > 1 else "北京天安门"
    destination = sys.argv[2] if len(sys.argv) > 2 else "北京故宫"
    
    asyncio.run(run_all_tests(origin, destination))
