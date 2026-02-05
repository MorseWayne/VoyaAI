#!/usr/bin/env python3
"""
Test Script: Xiaohongshu (小红书) MCP Service

This script tests the Xiaohongshu MCP integration independently.
It verifies:
1. XHS_MCP_URL environment variable is set
2. MCP server can be connected via streamable HTTP
3. Tools can be discovered dynamically
4. Search and feed operations work correctly

Usage:
    uv run python tests/test_xhs_mcp.py
    
    # With custom query
    uv run python tests/test_xhs_mcp.py "东京旅游攻略"
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path for our modules
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

logger = setup_test_logging("test_xhs_mcp")


async def test_config_check() -> tuple[bool, str, str]:
    """Test: Check XHS configuration."""
    settings = get_settings()
    
    issues = []
    
    if not settings.xhs_mcp_url:
        issues.append("XHS_MCP_URL not set")
    else:
        # Check URL format
        if not settings.xhs_mcp_url.startswith("http"):
            issues.append("XHS_MCP_URL should start with http:// or https://")
    
    if issues:
        return False, "Configuration issues found", "\n".join(issues)
    
    return True, "Configuration valid", f"MCP URL: {settings.xhs_mcp_url}"


async def test_mcp_connection() -> tuple[bool, str, str]:
    """Test: Try to connect to XHS MCP server via streamable HTTP."""
    from mcp_services import get_mcp_manager
    
    manager = get_mcp_manager()
    service = manager.get_service("xiaohongshu")
    
    if not service:
        return False, "Skipped - service not registered", ""
    
    try:
        logger.info(f"Connecting to XHS MCP server at {service.url}...")
        
        tools = await service.list_tools()
        tool_names = [t["function"]["name"] for t in tools]
        
        logger.info(f"Connected! Available tools: {tool_names}")
        
        return True, f"Connected, {len(tool_names)} tools available", ", ".join(tool_names)
    
    except Exception as e:
        return False, f"Connection failed: {type(e).__name__}", str(e)


async def test_check_login_status() -> tuple[bool, str, str]:
    """Test: Check login status on Xiaohongshu."""
    from mcp_services import call_mcp_tool
    
    settings = get_settings()
    
    if not settings.xhs_mcp_url:
        return False, "Skipped - configuration missing", ""
    
    try:
        logger.info("Checking Xiaohongshu login status...")
        
        result = await call_mcp_tool("xiaohongshu", "check_login_status", {})
        
        if result.startswith("Error"):
            return False, "Check login failed", result
        
        logger.info(f"Login status: {result[:200]}")
        
        return True, "Login status checked", result[:500]
    
    except Exception as e:
        return False, f"Check login failed: {type(e).__name__}", str(e)


async def test_search_feeds(query: str = "日本大阪旅游攻略") -> tuple[bool, str, str]:
    """Test: Search for feeds on Xiaohongshu."""
    from mcp_services import call_mcp_tool
    
    settings = get_settings()
    
    if not settings.xhs_mcp_url:
        return False, "Skipped - configuration missing", ""
    
    try:
        logger.info(f"Searching Xiaohongshu for: {query}")
        
        result = await call_mcp_tool("xiaohongshu", "search_feeds", {"keyword": query})
        
        if result.startswith("Error"):
            return False, "Search failed", result
        
        # Check if we got meaningful results
        if not result or len(result) < 50:
            return False, "Search returned empty/minimal results", result
        
        # Count approximate number of results (rough heuristic)
        result_count = result.count("标题") or result.count("title") or "unknown"
        
        logger.info(f"Search returned {len(result)} characters of content")
        
        return True, f"Search successful ({result_count} results)", result[:500]
    
    except Exception as e:
        return False, f"Search failed: {type(e).__name__}", str(e)


async def test_list_feeds() -> tuple[bool, str, str]:
    """Test: Get homepage recommendation list."""
    from mcp_services import call_mcp_tool
    
    settings = get_settings()
    
    if not settings.xhs_mcp_url:
        return False, "Skipped - configuration missing", ""
    
    try:
        logger.info("Getting Xiaohongshu feed list...")
        
        result = await call_mcp_tool("xiaohongshu", "list_feeds", {})
        
        if result.startswith("Error"):
            return False, "List feeds failed", result
        
        if not result or len(result) < 50:
            return False, "Feed list empty/minimal", result
        
        logger.info(f"Feed list returned {len(result)} characters of content")
        
        return True, "Feed list retrieved", result[:500]
    
    except Exception as e:
        return False, f"List feeds failed: {type(e).__name__}", str(e)


async def test_get_feed_detail(feed_id: str = None, xsec_token: str = None) -> tuple[bool, str, str]:
    """Test: Get content of a specific feed."""
    from mcp_services import call_mcp_tool
    
    settings = get_settings()
    
    if not settings.xhs_mcp_url:
        return False, "Skipped - configuration missing", ""
    
    if not feed_id or not xsec_token:
        return False, "Skipped - no feed_id/xsec_token provided", "Run search first to get feed IDs and tokens"
    
    try:
        logger.info(f"Getting feed detail: {feed_id}")
        
        result = await call_mcp_tool("xiaohongshu", "get_feed_detail", {
            "feed_id": feed_id,
            "xsec_token": xsec_token
        })
        
        if result.startswith("Error"):
            return False, "Get feed detail failed", result
        
        if not result or len(result) < 50:
            return False, "Feed detail empty/minimal", result
        
        return True, "Feed detail retrieved", result[:500]
    
    except Exception as e:
        return False, f"Get feed detail failed: {type(e).__name__}", str(e)


async def run_all_tests(search_query: str = "日本大阪旅游攻略"):
    """Run all Xiaohongshu MCP tests."""
    print_header("🔴 Xiaohongshu (小红书) MCP Test")
    print_config_info()
    
    results = []
    
    # Test 1: Configuration check
    print_section("Test 1: Configuration Check")
    result = await run_test("Config Check", test_config_check)
    print_result(result)
    results.append(result)
    
    if result.status != TestStatus.SUCCESS:
        print("\n⚠️  Skipping remaining tests due to configuration issues.")
        print("\nTo configure Xiaohongshu MCP:")
        print("  1. Set XHS_MCP_URL in your .env file (e.g., http://192.168.31.121:18060/mcp)")
        print_summary(results)
        return results
    
    # Test 2: MCP Connection & Tool Discovery
    print_section("Test 2: MCP Server Connection & Tool Discovery")
    result = await run_test("MCP Connection", test_mcp_connection)
    print_result(result)
    results.append(result)
    
    if result.status != TestStatus.SUCCESS:
        print("\n⚠️  Skipping remaining tests due to connection failure.")
        print_summary(results)
        return results
    
    # Test 3: Check Login Status
    print_section("Test 3: Check Login Status")
    result = await run_test("Login Status", test_check_login_status)
    print_result(result)
    results.append(result)
    
    # Test 4: List Feeds
    print_section("Test 4: List Homepage Feeds")
    result = await run_test("List Feeds", test_list_feeds)
    print_result(result)
    results.append(result)
    
    # Test 5: Search Feeds
    print_section(f"Test 5: Search Feeds (query: '{search_query}')")
    result = await run_test("Search Feeds", test_search_feeds, search_query)
    print_result(result)
    results.append(result)
    
    # Note: We skip test_get_feed_detail as it requires valid feed_id and xsec_token from search results
    
    print_summary(results)
    return results


if __name__ == "__main__":
    # Get search query from command line if provided
    query = sys.argv[1] if len(sys.argv) > 1 else "日本大阪旅游攻略"
    
    asyncio.run(run_all_tests(query))
