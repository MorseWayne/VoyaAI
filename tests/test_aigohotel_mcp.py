#!/usr/bin/env python3
"""
Test Script: AigoHotel MCP Service

测试 AigoHotel MCP 集成（Streamable HTTP + Bearer Token）。
验证：
1. AIGOHOTEL_MCP_URL、AIGOHOTEL_MCP_TOKEN 已配置
2. 能通过 streamable HTTP + Authorization 连接 MCP 服务
3. 能动态发现工具列表
4. 可选：调用一个无参或简单参数的工具验证调用链路

Usage:
    uv run python tests/test_aigohotel_mcp.py
"""
import asyncio
import sys
from pathlib import Path

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

logger = setup_test_logging("test_aigohotel_mcp")


async def test_config_check() -> tuple[bool, str, str]:
    """检查 AigoHotel MCP 配置."""
    settings = get_settings()
    issues = []
    if not settings.aigohotel_mcp_url:
        issues.append("AIGOHOTEL_MCP_URL 未设置")
    else:
        if not settings.aigohotel_mcp_url.startswith("http"):
            issues.append("AIGOHOTEL_MCP_URL 应以 http:// 或 https:// 开头")
    if not settings.aigohotel_mcp_token:
        issues.append("AIGOHOTEL_MCP_TOKEN 未设置（服务需要 Bearer 认证）")
    if issues:
        return False, "配置有问题", "\n".join(issues)
    return True, "配置有效", f"URL: {settings.aigohotel_mcp_url}, Token: ***{settings.aigohotel_mcp_token[-4:] if len(settings.aigohotel_mcp_token) > 4 else '(short)'}"


async def test_mcp_connection() -> tuple[bool, str, str]:
    """通过 Streamable HTTP + Bearer 连接 AigoHotel MCP 并拉取工具列表."""
    from mcp_services import get_mcp_manager

    manager = get_mcp_manager()
    service = manager.get_service("aigohotel")
    if not service:
        return False, "未注册 - 请先配置 AIGOHOTEL_MCP_URL 与 AIGOHOTEL_MCP_TOKEN", ""

    try:
        logger.info("正在连接 AigoHotel MCP: %s ...", service.url)
        tools = await service.list_tools()
        tool_names = [t["function"]["name"] for t in tools]
        logger.info("已连接，工具列表: %s", tool_names)
        return True, f"已连接，共 {len(tool_names)} 个工具", ", ".join(tool_names) if tool_names else "(无)"
    except Exception as e:
        return False, f"连接失败: {type(e).__name__}", str(e)


async def test_call_first_tool() -> tuple[bool, str, str]:
    """尝试调用第一个工具（无参或空参），验证调用链路."""
    from mcp_services import get_mcp_manager

    manager = get_mcp_manager()
    service = manager.get_service("aigohotel")
    if not service:
        return False, "跳过 - 服务未注册", ""

    try:
        tools = await service.list_tools()
        if not tools:
            return True, "跳过 - 无可用工具可测", ""
        first = tools[0]
        name = first["function"]["name"]
        params = first.get("function", {}).get("parameters", {}) or {}
        required = list(params.get("required", []))
        args = {}
        if required:
            for r in required:
                args[r] = ""  # 简单空串占位，部分接口可能接受
        logger.info("调用工具: %s, 参数: %s", name, args)
        result = await service.call_tool(name, args)
        if result.startswith("Error") or result.startswith("MCP Error"):
            return False, f"工具 {name} 返回错误", result[:400]
        return True, f"工具 {name} 调用成功", result[:500]
    except Exception as e:
        return False, f"调用失败: {type(e).__name__}", str(e)


async def run_all_tests():
    """运行全部 AigoHotel MCP 测试."""
    print_header("🏨 AigoHotel MCP 测试")
    print_config_info()

    results = []

    print_section("Test 1: 配置检查")
    r1 = await run_test("Config Check", test_config_check)
    print_result(r1)
    results.append(r1)

    if r1.status != TestStatus.SUCCESS:
        print("\n⚠️  因配置问题跳过后续测试。")
        print("请在 .env 中设置：")
        print("  AIGOHOTEL_MCP_URL=https://mcp.aigohotel.com/mcp")
        print("  AIGOHOTEL_MCP_TOKEN=你的 Bearer Token")
        print_summary(results)
        return results

    print_section("Test 2: MCP 连接与工具发现")
    r2 = await run_test("MCP Connection", test_mcp_connection)
    print_result(r2)
    results.append(r2)

    if r2.status != TestStatus.SUCCESS:
        print("\n⚠️  连接失败，跳过工具调用测试。")
        print_summary(results)
        return results

    print_section("Test 3: 调用第一个工具（可选）")
    r3 = await run_test("Call First Tool", test_call_first_tool)
    print_result(r3)
    results.append(r3)

    print_summary(results)
    return results


if __name__ == "__main__":
    asyncio.run(run_all_tests())
