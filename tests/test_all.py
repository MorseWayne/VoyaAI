#!/usr/bin/env python3
"""
Test Script: Run All MCP and Service Tests

This script runs all available tests and provides a comprehensive report.
Use this to verify the entire system is working correctly.

Usage:
    python tests/test_all.py
    
    # Run only specific tests
    python tests/test_all.py --llm        # LLM only
    python tests/test_all.py --xhs        # Xiaohongshu only
    python tests/test_all.py --weather    # Weather only
    python tests/test_all.py --amap       # Amap only
"""
import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_utils import (
    print_header,
    print_section,
    print_config_info,
    print_summary,
    TestResult,
    TestStatus,
)


async def run_test_module(name: str, module_func, *args, **kwargs) -> list[TestResult]:
    """Run a test module and return results."""
    try:
        results = await module_func(*args, **kwargs)
        return results
    except Exception as e:
        print(f"\n❌ Error running {name}: {e}")
        return [TestResult(
            name=name,
            status=TestStatus.FAILED,
            message=f"Module error: {type(e).__name__}",
            details=str(e),
        )]


async def main():
    parser = argparse.ArgumentParser(description="VoyaAI Test Suite")
    parser.add_argument("--llm", action="store_true", help="Run LLM tests only")
    parser.add_argument("--xhs", action="store_true", help="Run Xiaohongshu tests only")
    parser.add_argument("--weather", action="store_true", help="Run Weather tests only")
    parser.add_argument("--amap", action="store_true", help="Run Amap tests only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # If no specific test selected, run all
    run_all = not (args.llm or args.xhs or args.weather or args.amap)
    
    print_header("🧭 VoyaAI Complete Test Suite")
    print(f"\n  Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_config_info()
    
    all_results = []
    
    # 1. LLM Tests
    if run_all or args.llm:
        print("\n" + "=" * 60)
        print("  Running LLM Tests...")
        print("=" * 60)
        from tests.test_llm import run_all_tests as run_llm_tests
        results = await run_test_module("LLM", run_llm_tests)
        all_results.extend(results)
    
    # 2. Xiaohongshu Tests
    if run_all or args.xhs:
        print("\n" + "=" * 60)
        print("  Running Xiaohongshu Tests...")
        print("=" * 60)
        from tests.test_xhs_mcp import run_all_tests as run_xhs_tests
        results = await run_test_module("Xiaohongshu", run_xhs_tests)
        all_results.extend(results)
    
    # 3. Weather Tests
    if run_all or args.weather:
        print("\n" + "=" * 60)
        print("  Running Weather Tests...")
        print("=" * 60)
        from tests.test_weather_mcp import run_all_tests as run_weather_tests
        results = await run_test_module("Weather", run_weather_tests)
        all_results.extend(results)
    
    # 4. Amap Tests
    if run_all or args.amap:
        print("\n" + "=" * 60)
        print("  Running Amap Tests...")
        print("=" * 60)
        from tests.test_amap_mcp import run_all_tests as run_amap_tests
        results = await run_test_module("Amap", run_amap_tests)
        all_results.extend(results)
    
    # Final Summary
    print("\n" + "=" * 60)
    print("  📊 FINAL TEST SUMMARY")
    print("=" * 60)
    
    # Group by category
    categories = {
        "LLM": [],
        "Xiaohongshu": [],
        "Weather": [],
        "Amap": [],
    }
    
    for result in all_results:
        for cat in categories:
            if cat.lower() in result.name.lower() or result.name in ["Config Check", "API Connectivity", "Simple Completion", "Tool Calling", "Streaming"]:
                if cat == "LLM" and result.name in ["Config Check", "API Connectivity", "Simple Completion", "Tool Calling", "Streaming"]:
                    categories[cat].append(result)
                    break
                elif cat != "LLM":
                    categories[cat].append(result)
                    break
        else:
            # Default to first category that matches
            for cat in categories:
                categories[cat].append(result)
                break
    
    # Print summary by category
    total_success = 0
    total_failed = 0
    total_skipped = 0
    
    for cat_name, cat_results in categories.items():
        if not cat_results:
            continue
            
        success = sum(1 for r in cat_results if r.status == TestStatus.SUCCESS)
        failed = sum(1 for r in cat_results if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in cat_results if r.status == TestStatus.SKIPPED)
        
        total_success += success
        total_failed += failed
        total_skipped += skipped
        
        status_icon = "✅" if failed == 0 else "❌"
        print(f"\n  {status_icon} {cat_name}: {success}/{len(cat_results)} passed")
        
        for result in cat_results:
            print(f"     {result.status.value} {result.name}")
    
    # Overall summary
    print(f"\n  {'─' * 40}")
    print(f"  Total: {total_success} passed, {total_failed} failed, {total_skipped} skipped")
    print(f"  End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if total_failed == 0:
        print("\n  🎉 All tests passed! System is ready.")
        return 0
    else:
        print(f"\n  ⚠️  {total_failed} test(s) failed. Check configuration and services.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
