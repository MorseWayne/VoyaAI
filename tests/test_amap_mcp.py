#!/usr/bin/env python3
"""
Test Script: Amap (高德地图) MCP Service

This script tests the Amap MCP integration independently.
It verifies:
1. AMAP_MCP_URL environment variable is set
2. SSE connection to Amap MCP service works
3. Route planning and POI search work correctly

Usage:
    uv run python tests/test_amap_mcp.py
    
    # With custom origin and destination
    uv run python tests/test_amap_mcp.py "北京天安门" "北京故宫"
"""
import asyncio
import sys
import json
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
    
    # Check for key parameter (Amap usually requires API key)
    if "key=" not in url.lower():
        return False, "API key may be missing", f"Expected key= parameter in URL: {url}"
    
    return True, "Configuration valid", f"URL: {url[:50]}..."


async def test_sse_connection() -> tuple[bool, str, str]:
    """Test: Connect to Amap MCP SSE endpoint."""
    settings = get_settings()
    
    if not settings.amap_mcp_url:
        return False, "Skipped - configuration missing", ""
    
    try:
        import httpx
        from httpx_sse import aconnect_sse
        
        logger.info(f"Connecting to Amap MCP: {settings.amap_mcp_url[:50]}...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with aconnect_sse(client, "GET", settings.amap_mcp_url) as event_source:
                events_received = []
                endpoint_url = None
                
                async for event in event_source.aiter_sse():
                    events_received.append({
                        "event": event.event,
                        "data": event.data[:200] if event.data else None
                    })
                    logger.info(f"Received SSE event: {event.event}")
                    
                    # Check for endpoint event (MCP protocol)
                    if event.event == "endpoint":
                        endpoint_url = event.data
                        logger.info(f"Got MCP endpoint: {endpoint_url}")
                    
                    if len(events_received) >= 2:
                        break
                
                if endpoint_url:
                    return True, "SSE connected with MCP endpoint", f"Endpoint: {endpoint_url}"
                elif events_received:
                    return True, f"SSE connected, {len(events_received)} event(s)", str(events_received[0])
                else:
                    return False, "SSE connected but no events", ""
    
    except httpx.ConnectError as e:
        return False, "Connection refused", f"Cannot connect to Amap MCP: {e}"
    except httpx.TimeoutException:
        return False, "Connection timeout", "Server did not respond within 30 seconds"
    except Exception as e:
        return False, f"Connection failed: {type(e).__name__}", str(e)


async def test_list_tools() -> tuple[bool, str, str]:
    """Test: List available tools from Amap MCP."""
    settings = get_settings()
    
    if not settings.amap_mcp_url:
        return False, "Skipped - configuration missing", ""
    
    try:
        import httpx
        from httpx_sse import aconnect_sse
        
        logger.info("Listing available Amap MCP tools...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with aconnect_sse(client, "GET", settings.amap_mcp_url) as event_source:
                endpoint_url = None
                
                async for event in event_source.aiter_sse():
                    if event.event == "endpoint":
                        endpoint_url = event.data
                        break
                
                if not endpoint_url:
                    return False, "No MCP endpoint received", "Cannot list tools without endpoint"
                
                # Call tools/list on the MCP endpoint
                list_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                }
                
                response = await client.post(endpoint_url, json=list_request, timeout=15.0)
                
                if response.status_code != 200:
                    return False, f"HTTP {response.status_code}", response.text[:200]
                
                data = response.json()
                
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    tool_names = [t.get("name", "unknown") for t in tools]
                    logger.info(f"Available tools: {tool_names}")
                    return True, f"{len(tools)} tools available", ", ".join(tool_names)
                elif "error" in data:
                    return False, "MCP error", str(data["error"])
                else:
                    return False, "Unexpected response", str(data)[:200]
    
    except Exception as e:
        return False, f"Failed: {type(e).__name__}", str(e)


async def test_route_planning(origin: str = "北京天安门", destination: str = "北京故宫") -> tuple[bool, str, str]:
    """Test: Plan a route using Amap MCP."""
    settings = get_settings()
    
    if not settings.amap_mcp_url:
        return False, "Skipped - configuration missing", ""
    
    try:
        import httpx
        from httpx_sse import aconnect_sse
        
        logger.info(f"Planning route: {origin} → {destination}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with aconnect_sse(client, "GET", settings.amap_mcp_url) as event_source:
                endpoint_url = None
                
                async for event in event_source.aiter_sse():
                    if event.event == "endpoint":
                        endpoint_url = event.data
                        break
                
                if not endpoint_url:
                    return False, "No MCP endpoint received", ""
                
                # Try common Amap tool names for route planning
                tool_names_to_try = [
                    "maps_direction_transit",
                    "maps_direction_driving", 
                    "direction_transit",
                    "direction",
                    "route",
                    "plan_route",
                ]
                
                for tool_name in tool_names_to_try:
                    try:
                        call_request = {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "tools/call",
                            "params": {
                                "name": tool_name,
                                "arguments": {
                                    "origin": origin,
                                    "destination": destination,
                                }
                            }
                        }
                        
                        logger.debug(f"Trying tool: {tool_name}")
                        response = await client.post(endpoint_url, json=call_request, timeout=30.0)
                        data = response.json()
                        
                        if "result" in data:
                            result_content = str(data["result"])[:500]
                            logger.info(f"Tool {tool_name} succeeded")
                            return True, f"Route planned via {tool_name}", result_content
                        elif "error" in data:
                            error_msg = str(data["error"])
                            if "unknown tool" not in error_msg.lower() and "not found" not in error_msg.lower():
                                return False, f"Tool error: {tool_name}", error_msg[:200]
                    except Exception as e:
                        logger.debug(f"Tool {tool_name} failed: {e}")
                        continue
                
                return False, "No route planning tool found", f"Tried: {', '.join(tool_names_to_try)}"
    
    except Exception as e:
        return False, f"Failed: {type(e).__name__}", str(e)


async def test_poi_search(keyword: str = "餐厅", city: str = "北京") -> tuple[bool, str, str]:
    """Test: Search for POI using Amap MCP."""
    settings = get_settings()
    
    if not settings.amap_mcp_url:
        return False, "Skipped - configuration missing", ""
    
    try:
        import httpx
        from httpx_sse import aconnect_sse
        
        logger.info(f"Searching POI: {keyword} in {city}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with aconnect_sse(client, "GET", settings.amap_mcp_url) as event_source:
                endpoint_url = None
                
                async for event in event_source.aiter_sse():
                    if event.event == "endpoint":
                        endpoint_url = event.data
                        break
                
                if not endpoint_url:
                    return False, "No MCP endpoint received", ""
                
                # Try common Amap tool names for POI search
                tool_names_to_try = [
                    "maps_search_poi",
                    "search_poi",
                    "poi_search",
                    "places_search",
                    "search",
                ]
                
                for tool_name in tool_names_to_try:
                    try:
                        call_request = {
                            "jsonrpc": "2.0",
                            "id": 3,
                            "method": "tools/call",
                            "params": {
                                "name": tool_name,
                                "arguments": {
                                    "keyword": keyword,
                                    "city": city,
                                }
                            }
                        }
                        
                        logger.debug(f"Trying tool: {tool_name}")
                        response = await client.post(endpoint_url, json=call_request, timeout=30.0)
                        data = response.json()
                        
                        if "result" in data:
                            result_content = str(data["result"])[:500]
                            logger.info(f"Tool {tool_name} succeeded")
                            return True, f"POI search via {tool_name}", result_content
                        elif "error" in data:
                            error_msg = str(data["error"])
                            if "unknown tool" not in error_msg.lower() and "not found" not in error_msg.lower():
                                return False, f"Tool error: {tool_name}", error_msg[:200]
                    except Exception as e:
                        logger.debug(f"Tool {tool_name} failed: {e}")
                        continue
                
                return False, "No POI search tool found", f"Tried: {', '.join(tool_names_to_try)}"
    
    except Exception as e:
        return False, f"Failed: {type(e).__name__}", str(e)


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
        print("\nTo configure Amap MCP:")
        print("  1. Get an API key from https://console.amap.com/")
        print("  2. Set AMAP_MCP_URL in your .env file")
        print("     Example: https://mcp.amap.com/sse?key=YOUR_API_KEY")
        print_summary(results)
        return results
    
    # Test 2: SSE Connection
    print_section("Test 2: SSE Connection")
    result = await run_test("SSE Connection", test_sse_connection)
    print_result(result)
    results.append(result)
    
    if result.status != TestStatus.SUCCESS:
        print("\n⚠️  Skipping remaining tests due to connection failure.")
        print_summary(results)
        return results
    
    # Test 3: List Tools
    print_section("Test 3: List Available Tools")
    result = await run_test("List Tools", test_list_tools)
    print_result(result)
    results.append(result)
    
    # Test 4: Route Planning
    print_section(f"Test 4: Route Planning ({origin} → {destination})")
    result = await run_test("Route Planning", test_route_planning, origin, destination)
    print_result(result)
    results.append(result)
    
    # Test 5: POI Search
    print_section("Test 5: POI Search (餐厅 in 北京)")
    result = await run_test("POI Search", test_poi_search, "餐厅", "北京")
    print_result(result)
    results.append(result)
    
    print_summary(results)
    return results


if __name__ == "__main__":
    # Get origin and destination from command line if provided
    origin = sys.argv[1] if len(sys.argv) > 1 else "北京天安门"
    destination = sys.argv[2] if len(sys.argv) > 2 else "北京故宫"
    
    asyncio.run(run_all_tests(origin, destination))
