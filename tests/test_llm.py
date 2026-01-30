#!/usr/bin/env python3
"""
Test Script: LLM Connection

This script tests the LLM (Large Language Model) connection independently.
It verifies:
1. LLM configuration (base URL, API key, model)
2. Basic API connectivity
3. Simple chat completion
4. Tool calling capability

Usage:
    python tests/test_llm.py
    
    # With custom prompt
    python tests/test_llm.py "你好，请介绍一下自己"
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

logger = setup_test_logging("test_llm")


async def test_config_check() -> tuple[bool, str, str]:
    """Test: Check LLM configuration."""
    settings = get_settings()
    
    issues = []
    
    if not settings.llm_base_url:
        issues.append("LLM_BASE_URL not set")
    elif not (settings.llm_base_url.startswith("http://") or settings.llm_base_url.startswith("https://")):
        issues.append(f"Invalid LLM_BASE_URL format: {settings.llm_base_url}")
    
    if not settings.llm_api_key:
        issues.append("LLM_API_KEY not set")
    
    if not settings.llm_model:
        issues.append("LLM_MODEL not set")
    
    if issues:
        return False, "Configuration issues", "\n".join(issues)
    
    return True, "Configuration valid", f"Model: {settings.llm_model}, URL: {settings.llm_base_url}"


async def test_api_connectivity() -> tuple[bool, str, str]:
    """Test: Check API connectivity."""
    settings = get_settings()
    
    if not settings.llm_base_url or not settings.llm_api_key:
        return False, "Skipped - configuration missing", ""
    
    try:
        import httpx
        
        # Try to hit the models endpoint (common for OpenAI-compatible APIs)
        base_url = settings.llm_base_url.rstrip("/")
        models_url = f"{base_url}/models"
        
        logger.info(f"Testing connectivity to: {models_url}")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                models_url,
                headers={"Authorization": f"Bearer {settings.llm_api_key}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    model_count = len(data["data"])
                    model_names = [m.get("id", "unknown") for m in data["data"][:5]]
                    return True, f"Connected, {model_count} models available", ", ".join(model_names)
                return True, "Connected", str(data)[:200]
            elif response.status_code == 401:
                return False, "Authentication failed", "Invalid API key"
            elif response.status_code == 404:
                # Some APIs don't have /models endpoint, try a simple completion
                return True, "Models endpoint not available (may still work)", "Will test with completion"
            else:
                return False, f"HTTP {response.status_code}", response.text[:200]
    
    except httpx.ConnectError as e:
        return False, "Connection refused", f"Cannot connect to {settings.llm_base_url}"
    except httpx.TimeoutException:
        return False, "Connection timeout", "Server did not respond within 15 seconds"
    except Exception as e:
        return False, f"Error: {type(e).__name__}", str(e)


async def test_simple_completion(prompt: str = "你好") -> tuple[bool, str, str]:
    """Test: Simple chat completion."""
    settings = get_settings()
    
    if not settings.llm_base_url or not settings.llm_api_key:
        return False, "Skipped - configuration missing", ""
    
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
        )
        
        logger.info(f"Sending test prompt: '{prompt}'")
        
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            timeout=30.0,
        )
        
        if response.choices and response.choices[0].message.content:
            content = response.choices[0].message.content
            usage = response.usage
            usage_info = f"tokens: {usage.total_tokens}" if usage else ""
            logger.info(f"Response received ({usage_info})")
            return True, f"Completion successful ({usage_info})", content[:300]
        else:
            return False, "Empty response", str(response)
    
    except Exception as e:
        error_msg = str(e)
        print(f"Error message: {error_msg}")
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            return False, "Authentication error", error_msg[:200]
        elif "model" in error_msg.lower():
            return False, "Model not found", f"Model '{settings.llm_model}' may not be available"
        else:
            return False, f"Error: {type(e).__name__}", error_msg[:200]


async def test_tool_calling() -> tuple[bool, str, str]:
    """Test: Tool calling capability."""
    settings = get_settings()
    
    if not settings.llm_base_url or not settings.llm_api_key:
        return False, "Skipped - configuration missing", ""
    
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
        )
        
        # Define a simple test tool
        test_tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the weather for a city",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city name"
                            }
                        },
                        "required": ["city"]
                    }
                }
            }
        ]
        
        logger.info("Testing tool calling capability...")
        
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": "北京今天天气怎么样？"}],
            tools=test_tools,
            tool_choice="auto",
            timeout=30.0,
        )
        
        message = response.choices[0].message
        
        # Debug: 打印完整的 message 对象
        logger.debug(f"Response message: {message}")
        logger.debug(f"Message model_dump: {message.model_dump()}")
        
        if message.tool_calls:
            tool_calls = message.tool_calls
            tool_info = [
                f"{tc.function.name}({tc.function.arguments})" 
                for tc in tool_calls
            ]
            logger.info(f"Tool calls received: {tool_info}")
            return True, f"{len(tool_calls)} tool call(s)", ", ".join(tool_info)
        elif message.content:
            # Model responded with content instead of tool call
            return True, "Model responded (no tool call)", f"Model may not support tool calling well. Response: {message.content[:100]}"
        else:
            # 返回更详细的调试信息
            msg_dump = message.model_dump()
            # 这种情况通常是代理不支持 tool calling
            return False, "Tool calling not supported", "API proxy may not support OpenAI tool calling format. This feature is optional for basic travel planning."
    
    except Exception as e:
        error_msg = str(e)
        if "tool" in error_msg.lower() or "function" in error_msg.lower():
            return False, "Tool calling not supported", error_msg[:200]
        else:
            return False, f"Error: {type(e).__name__}", error_msg[:200]


async def test_streaming() -> tuple[bool, str, str]:
    """Test: Streaming completion."""
    settings = get_settings()
    
    if not settings.llm_base_url or not settings.llm_api_key:
        return False, "Skipped - configuration missing", ""
    
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
        )
        
        logger.info("Testing streaming capability...")
        
        stream = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": "数到5"}],
            max_tokens=50,
            stream=True,
            timeout=30.0,
        )
        
        chunks = []
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                chunks.append(chunk.choices[0].delta.content)
        
        full_content = "".join(chunks)
        
        if chunks:
            return True, f"Streaming works ({len(chunks)} chunks)", full_content[:200]
        else:
            return False, "No stream chunks received", ""
    
    except Exception as e:
        error_msg = str(e)
        if "stream" in error_msg.lower():
            return False, "Streaming not supported", error_msg[:200]
        else:
            return False, f"Error: {type(e).__name__}", error_msg[:200]


async def run_all_tests(prompt: str = "你好"):
    """Run all LLM tests."""
    print_header("🤖 LLM Connection Test")
    print_config_info()
    
    results = []
    
    # Test 1: Configuration check
    print_section("Test 1: Configuration Check")
    result = await run_test("Config Check", test_config_check)
    print_result(result)
    results.append(result)
    
    if result.status != TestStatus.SUCCESS:
        print("\n⚠️  Skipping remaining tests due to configuration issues.")
        print("\nTo configure LLM:")
        print("  1. Set LLM_BASE_URL in your .env file")
        print("  2. Set LLM_API_KEY in your .env file")
        print("  3. Set LLM_MODEL in your .env file")
        print_summary(results)
        return results
    
    # Test 2: API Connectivity
    print_section("Test 2: API Connectivity")
    result = await run_test("API Connectivity", test_api_connectivity)
    print_result(result)
    results.append(result)
    
    if result.status == TestStatus.FAILED and "Connection" in result.message:
        print("\n⚠️  Skipping remaining tests due to connection failure.")
        print_summary(results)
        return results
    
    # Test 3: Simple Completion
    print_section(f"Test 3: Simple Completion (prompt: '{prompt}')")
    result = await run_test("Simple Completion", test_simple_completion, prompt)
    print_result(result)
    results.append(result)
    
    if result.status != TestStatus.SUCCESS:
        print("\n⚠️  Skipping remaining tests due to completion failure.")
        print_summary(results)
        return results
    
    # Test 4: Tool Calling
    print_section("Test 4: Tool Calling")
    result = await run_test("Tool Calling", test_tool_calling)
    print_result(result)
    results.append(result)
    
    # Test 5: Streaming
    print_section("Test 5: Streaming")
    result = await run_test("Streaming", test_streaming)
    print_result(result)
    results.append(result)
    
    print_summary(results)
    return results


if __name__ == "__main__":
    # Get prompt from command line if provided
    prompt = sys.argv[1] if len(sys.argv) > 1 else "你好"
    
    asyncio.run(run_all_tests(prompt))
