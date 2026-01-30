#!/usr/bin/env python3
"""
Test Script: Xiaohongshu (小红书) MCP Service

This script tests the Xiaohongshu MCP integration independently.
It verifies:
1. XHS_COOKIE environment variable is set
2. XHS_MCP_DIR points to a valid directory
3. MCP server can be started via stdio
4. Search and note content retrieval work correctly

Usage:
    python tests/test_xhs_mcp.py
    
    # With custom query
    python tests/test_xhs_mcp.py "东京旅游攻略"
"""
import asyncio
import sys
import os
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

logger = setup_test_logging("test_xhs_mcp")


async def test_config_check() -> tuple[bool, str, str]:
    """Test: Check XHS configuration."""
    settings = get_settings()
    
    issues = []
    
    if not settings.xhs_cookie:
        issues.append("XHS_COOKIE not set")
    else:
        # Check cookie format (should contain key=value pairs)
        if "=" not in settings.xhs_cookie:
            issues.append("XHS_COOKIE format may be invalid (no key=value pairs found)")
    
    if not settings.xhs_mcp_dir:
        issues.append("XHS_MCP_DIR not set")
    else:
        mcp_dir = Path(settings.xhs_mcp_dir)
        if not mcp_dir.exists():
            issues.append(f"XHS_MCP_DIR does not exist: {mcp_dir}")
        else:
            # Check for main.py or expected MCP files
            main_py = mcp_dir / "main.py"
            if not main_py.exists():
                issues.append(f"main.py not found in XHS_MCP_DIR: {mcp_dir}")
    
    if issues:
        return False, "Configuration issues found", "\n".join(issues)
    
    return True, "Configuration valid", f"MCP Dir: {settings.xhs_mcp_dir}"


async def test_mcp_connection() -> tuple[bool, str, str]:
    """Test: Try to connect to XHS MCP server."""
    settings = get_settings()
    
    if not settings.xhs_cookie or not settings.xhs_mcp_dir:
        return False, "Skipped - configuration missing", ""
    
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
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
        
        logger.info("Connecting to XHS MCP server...")
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List available tools
                tools = await session.list_tools()
                tool_names = [t.name for t in tools.tools]
                
                logger.info(f"Connected! Available tools: {tool_names}")
                
                return True, f"Connected, {len(tool_names)} tools available", ", ".join(tool_names)
    
    except FileNotFoundError as e:
        return False, "uv command not found", "Please install uv: pip install uv"
    except Exception as e:
        return False, f"Connection failed: {type(e).__name__}", str(e)


async def test_search_notes(query: str = "日本大阪旅游攻略") -> tuple[bool, str, str]:
    """Test: Search for notes on Xiaohongshu."""
    settings = get_settings()
    
    if not settings.xhs_cookie or not settings.xhs_mcp_dir:
        return False, "Skipped - configuration missing", ""
    
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
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
        
        logger.info(f"Searching Xiaohongshu for: {query}")
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Call search_notes tool
                result = await session.call_tool("search_notes", {"keyword": query})
                
                if result.isError:
                    return False, "Search failed", str(result.content)
                
                # Parse result
                content = "\n".join([c.text for c in result.content if hasattr(c, 'text')])
                
                # Check if we got meaningful results
                if not content or len(content) < 50:
                    return False, "Search returned empty/minimal results", content
                
                # Count approximate number of results (rough heuristic)
                result_count = content.count("标题") or content.count("title") or "unknown"
                
                logger.info(f"Search returned {len(content)} characters of content")
                
                return True, f"Search successful ({result_count} results)", content[:500]
    
    except Exception as e:
        return False, f"Search failed: {type(e).__name__}", str(e)


async def test_get_note_content(note_id: str = None) -> tuple[bool, str, str]:
    """Test: Get content of a specific note."""
    settings = get_settings()
    
    if not settings.xhs_cookie or not settings.xhs_mcp_dir:
        return False, "Skipped - configuration missing", ""
    
    if not note_id:
        return False, "Skipped - no note_id provided", "Run search first to get note IDs"
    
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
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
        
        logger.info(f"Getting note content: {note_id}")
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                result = await session.call_tool("get_note_content", {"note_id": note_id})
                
                if result.isError:
                    return False, "Get note failed", str(result.content)
                
                content = "\n".join([c.text for c in result.content if hasattr(c, 'text')])
                
                if not content or len(content) < 50:
                    return False, "Note content empty/minimal", content
                
                return True, "Note content retrieved", content[:500]
    
    except Exception as e:
        return False, f"Get note failed: {type(e).__name__}", str(e)


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
        print("  1. Set XHS_COOKIE in your .env file")
        print("  2. Set XHS_MCP_DIR to point to jobsonlook-xhs-mcp directory")
        print_summary(results)
        return results
    
    # Test 2: MCP Connection
    print_section("Test 2: MCP Server Connection")
    result = await run_test("MCP Connection", test_mcp_connection)
    print_result(result)
    results.append(result)
    
    if result.status != TestStatus.SUCCESS:
        print("\n⚠️  Skipping remaining tests due to connection failure.")
        print_summary(results)
        return results
    
    # Test 3: Search Notes
    print_section(f"Test 3: Search Notes (query: '{search_query}')")
    result = await run_test("Search Notes", test_search_notes, search_query)
    print_result(result)
    results.append(result)
    
    # Note: We skip test_get_note_content as it requires a valid note_id from search results
    
    print_summary(results)
    return results


if __name__ == "__main__":
    # Get search query from command line if provided
    query = sys.argv[1] if len(sys.argv) > 1 else "日本大阪旅游攻略"
    
    asyncio.run(run_all_tests(query))
