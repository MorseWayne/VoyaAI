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
    
    print(f"\n=== Testing Smart Strategy (Time First - Default) ===")
    res_time = await service.optimize_route(locations, city, "smart", "time")
    if "segments" in res_time and res_time["segments"]:
        print(f"Mode: {res_time['segments'][0]['mode']}, Duration: {res_time['segments'][0]['duration_m']}m, Distance: {res_time['segments'][0]['distance_km']}km")

    print(f"\n=== Testing Smart Strategy (Distance First) ===")
    res_dist = await service.optimize_route(locations, city, "smart", "distance")
    if "segments" in res_dist and res_dist["segments"]:
        print(f"Mode: {res_dist['segments'][0]['mode']}, Duration: {res_dist['segments'][0]['duration_m']}m, Distance: {res_dist['segments'][0]['distance_km']}km")

    print(f"\n=== Testing Smart Strategy (Transit First) ===")
    res_transit = await service.optimize_route(locations, city, "smart", "transit_first")
    if "segments" in res_transit and res_transit["segments"]:
        print(f"Mode: {res_transit['segments'][0]['mode']}, Duration: {res_transit['segments'][0]['duration_m']}m, Distance: {res_transit['segments'][0]['distance_km']}km")

if __name__ == "__main__":
    asyncio.run(main())
