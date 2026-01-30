"""
Test Utilities - Common utilities for MCP testing.
"""
import asyncio
import sys
import logging
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_settings


class TestStatus(Enum):
    """Test result status."""
    SUCCESS = "✅ SUCCESS"
    FAILED = "❌ FAILED"
    SKIPPED = "⏭️ SKIPPED"
    WARNING = "⚠️ WARNING"


@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    status: TestStatus
    message: str
    duration_ms: float = 0
    details: Optional[str] = None


def setup_test_logging(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    Setup logging for test scripts.
    
    Args:
        name: Logger name
        level: Logging level
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Format with timestamp
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def print_header(title: str, width: int = 60):
    """Print a formatted header."""
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_section(title: str, width: int = 60):
    """Print a section divider."""
    print(f"\n{'─' * width}")
    print(f"  {title}")
    print("─" * width)


def print_config_info():
    """Print current configuration info."""
    settings = get_settings()
    
    print_section("📋 Configuration")
    print(f"  LLM Base URL:   {settings.llm_base_url}")
    print(f"  LLM Model:      {settings.llm_model}")
    print(f"  LLM API Key:    {'***' + settings.llm_api_key[-4:] if len(settings.llm_api_key) > 4 else '(not set)'}")
    print(f"  Amap MCP URL:   {settings.amap_mcp_url or '(not set)'}")
    print(f"  Weather MCP:    {settings.weather_mcp_url or '(not set)'}")
    print(f"  XHS Cookie:     {'(set)' if settings.xhs_cookie else '(not set)'}")
    print(f"  XHS MCP Dir:    {settings.xhs_mcp_dir or '(not set)'}")


def print_result(result: TestResult):
    """Print a single test result."""
    print(f"\n  {result.status.value} {result.name}")
    print(f"     Duration: {result.duration_ms:.1f}ms")
    print(f"     Message:  {result.message}")
    if result.details:
        # Truncate long details
        details = result.details[:500] + "..." if len(result.details) > 500 else result.details
        print(f"     Details:  {details}")


def print_summary(results: list[TestResult]):
    """Print summary of all test results."""
    print_section("📊 Test Summary")
    
    success = sum(1 for r in results if r.status == TestStatus.SUCCESS)
    failed = sum(1 for r in results if r.status == TestStatus.FAILED)
    skipped = sum(1 for r in results if r.status == TestStatus.SKIPPED)
    warning = sum(1 for r in results if r.status == TestStatus.WARNING)
    total = len(results)
    total_time = sum(r.duration_ms for r in results)
    
    print(f"\n  Total Tests:  {total}")
    print(f"  ✅ Passed:    {success}")
    print(f"  ❌ Failed:    {failed}")
    print(f"  ⚠️  Warning:   {warning}")
    print(f"  ⏭️  Skipped:   {skipped}")
    print(f"  ⏱️  Time:      {total_time:.1f}ms")
    
    if failed == 0:
        print("\n  🎉 All tests passed!")
    else:
        print(f"\n  ⚠️  {failed} test(s) failed!")


async def run_test(
    name: str,
    test_func: Callable,
    *args,
    **kwargs
) -> TestResult:
    """
    Run a single test with timing and error handling.
    
    Args:
        name: Test name
        test_func: Async function to run
        *args, **kwargs: Arguments to pass to test_func
    
    Returns:
        TestResult with status and details
    """
    start_time = datetime.now()
    
    try:
        result = await test_func(*args, **kwargs)
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        if isinstance(result, tuple):
            success, message, details = result
        else:
            success = bool(result)
            message = "Test completed"
            details = str(result) if result else None
        
        return TestResult(
            name=name,
            status=TestStatus.SUCCESS if success else TestStatus.FAILED,
            message=message,
            duration_ms=duration,
            details=details,
        )
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        return TestResult(
            name=name,
            status=TestStatus.FAILED,
            message=f"Exception: {type(e).__name__}",
            duration_ms=duration,
            details=str(e),
        )


def run_async(coro):
    """Run an async function in the event loop."""
    return asyncio.run(coro)
