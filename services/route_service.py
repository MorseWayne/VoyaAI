"""
Route Service - Handles interaction with AMap MCP for geocoding, routing, and optimization.
"""
import logging
import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from mcp_services.clients import call_mcp_tool

logger = logging.getLogger(__name__)

@dataclass
class Location:
    name: str
    lat: float
    lng: float
    address: str = ""
    city: str = ""

@dataclass
class RouteSegment:
    origin: Location
    destination: Location
    distance_km: float
    duration_minutes: float
    strategy: str = "driving"

class RouteService:
    """
    Service for route planning and optimization using AMap MCP.
    """
    
    async def get_location_details(self, place_name: str, city: str = "") -> Optional[Location]:
        """
        Search for a location to get its coordinates.
        """
        try:
            # Try specific tool names known for AMap MCP
            # Based on tests/test_amap_mcp.py
            result = await call_mcp_tool("amap", "search_poi", {"keyword": place_name, "city": city})
            
            # Parse result - expecting a JSON string or dict
            # The MCP client returns a string, usually JSON representation
            if isinstance(result, str):
                # Look for JSON structure if mixed with text
                try:
                    data = json.loads(result)
                except json.JSONDecodeError:
                    # Sometimes LLM/MCP might return text description. 
                    # We rely on the MCP returning structured data for this internal call.
                    logger.error(f"Failed to parse POI search result for {place_name}: {result[:100]}")
                    return None
            else:
                data = result

            # Adapt to likely AMap API response structure
            # usually { "pois": [ ... ] }
            pois = data.get("pois", []) if isinstance(data, dict) else []
            
            if not pois and isinstance(data, list):
                pois = data

            if pois:
                top_poi = pois[0]
                location_str = top_poi.get("location", "")
                if "," in location_str:
                    lng, lat = map(float, location_str.split(","))
                    return Location(
                        name=top_poi.get("name", place_name),
                        lat=lat,
                        lng=lng,
                        address=top_poi.get("address", ""),
                        city=top_poi.get("cityname", city)
                    )
            
            logger.warning(f"No POI found for {place_name}")
            return None

        except Exception as e:
            logger.error(f"Error getting location details for {place_name}: {e}")
            return None

    async def get_travel_route(self, origin: Location, destination: Location, mode: str = "driving") -> Optional[RouteSegment]:
        """
        Get travel time and distance between two points.
        """
        try:
            # Prepare coords "lng,lat"
            origin_coords = f"{origin.lng},{origin.lat}"
            dest_coords = f"{destination.lng},{destination.lat}"
            
            # Map mode to tool
            tool_name = "direction_driving" if mode == "driving" else "direction_transit"
            
            result = await call_mcp_tool("amap", tool_name, {
                "origin": origin_coords,
                "destination": dest_coords
            })
            
            if isinstance(result, str):
                try:
                    data = json.loads(result)
                except:
                    logger.error(f"Failed to parse Route result")
                    return None
            else:
                data = result

            # Parse AMap direction response
            route = data.get("route", {})
            paths = route.get("paths", [])
            
            if paths:
                path = paths[0]
                distance = float(path.get("distance", 0)) / 1000.0 # meters to km
                duration = float(path.get("duration", 0)) / 60.0 # seconds to minutes
                
                return RouteSegment(
                    origin=origin,
                    destination=destination,
                    distance_km=distance,
                    duration_minutes=duration,
                    strategy=mode
                )
            
            return None

        except Exception as e:
            logger.error(f"Error getting route from {origin.name} to {destination.name}: {e}")
            return None

    async def optimize_route(self, locations: List[str], city: str = "") -> Dict[str, Any]:
        """
        Take a list of location names, resolve them, and reorder for optimal travel.
        Internal logic:
        1. Resolve all locations.
        2. Simple greedy nearest neighbor (start with first location provided or a central one).
        """
        # 1. Resolve Locations
        resolved_locations = []
        for loc_name in locations:
            details = await self.get_location_details(loc_name, city)
            if details:
                resolved_locations.append(details)
            else:
                logger.warning(f"Skipping unresolved location: {loc_name}")

        if not resolved_locations:
            return {"error": "No valid locations found"}

        # 2. Optimize (Greedy Nearest Neighbor)
        # Fix the first location as the starting point (User usually puts start first)
        path = [resolved_locations.pop(0)]
        total_dist = 0
        total_time = 0
        segments = []

        while resolved_locations:
            current = path[-1]
            best_next = None
            best_segment = None
            min_dist = float('inf')
            best_idx = -1

            # Find nearest neighbor
            # Note: For N locations, this makes N requests. Might be slow if N is large.
            # Optimization: Use Haversine distance for selection, then call API for final details.
            
            for i, candidate in enumerate(resolved_locations):
                # Use simple Euclidean/Haversine approx for selection to save API calls
                # or just use Euclidean on lat/lng for rough closeness
                dist_approx = ((current.lat - candidate.lat)**2 + (current.lng - candidate.lng)**2)**0.5
                
                if dist_approx < min_dist:
                    min_dist = dist_approx
                    best_next = candidate
                    best_idx = i

            # Now verify with actual API call (optional, but requested "AMap query")
            # To be fast, we might just trust the geometric sorting and then calculate route details.
            # Let's confirm the move.
            
            path.append(best_next)
            resolved_locations.pop(best_idx)

        # 3. Calculate full route details accurately
        final_route_details = []
        for i in range(len(path) - 1):
            segment = await self.get_travel_route(path[i], path[i+1])
            if segment:
                segments.append({
                    "from": path[i].name,
                    "to": path[i+1].name,
                    "distance_km": f"{segment.distance_km:.1f}",
                    "duration_m": f"{segment.duration_minutes:.0f}",
                    "mode": segment.strategy
                })
                total_dist += segment.distance_km
                total_time += segment.duration_minutes
            else:
                # Fallback if API fails
                segments.append({
                    "from": path[i].name,
                    "to": path[i+1].name,
                    "error": "Could not calculate route"
                })

        return {
            "success": True,
            "optimized_order": [p.name for p in path],
            "poi_details": [{ "name": p.name, "lat": p.lat, "lng": p.lng, "address": p.address } for p in path],
            "segments": segments,
            "total_distance_km": f"{total_dist:.1f}",
            "total_duration_hours": f"{total_time/60:.1f}"
        }
