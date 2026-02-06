import asyncio
import sys
import logging
from pathlib import Path
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.route_service import RouteService
from mcp_services.clients import refresh_mcp_manager

# Setup logging
logging.basicConfig(level=logging.INFO)

async def main():
    # Ensure MCP manager is loaded
    await refresh_mcp_manager()
    
    service = RouteService()
    locations = ["广州塔", "白云山"]
    city = "广州"
    
    # Test Transit Distance Fix
    print(f"\n=== Testing Transit (expecting distance > 0) ===")
    res_transit = await service.optimize_route(locations, city, "transit")
    print(json.dumps(res_transit, indent=2, ensure_ascii=False))
    
    # Test Smart Strategy
    print(f"\n=== Testing Smart Strategy ===")
    res_smart = await service.optimize_route(locations, city, "smart")
    print(json.dumps(res_smart, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())