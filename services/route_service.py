"""
Route Service - Handles interaction with AMap MCP for geocoding, routing, and optimization.
"""
import logging
import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from api.models import TransportMode, Segment, Location as ApiLocation

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
    steps: List[str] = None

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
            # Updated to use correct tool name "maps_text_search" and parameter "keywords"
            result = await call_mcp_tool("amap", "maps_text_search", {"keywords": place_name, "city": city})
            
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
                
                # If location is missing but we have an address, try geocoding
                if not location_str and top_poi.get("address"):
                    address = top_poi.get("address")
                    # If address is a list (some APIs do this), join it
                    if isinstance(address, list):
                        address = "".join(str(x) for x in address)
                        
                    if address:
                        logger.info(f"POI found but no location. Geocoding address: {address}")
                        try:
                            geo_result = await call_mcp_tool("amap", "maps_geo", {"address": address, "city": city})
                            if isinstance(geo_result, str):
                                try:
                                    geo_data = json.loads(geo_result)
                                    # Check for 'geocodes' (standard API) or 'results' (observed in MCP)
                                    if "geocodes" in geo_data and geo_data["geocodes"]:
                                        location_str = geo_data["geocodes"][0].get("location", "")
                                    elif "results" in geo_data and geo_data["results"]:
                                        location_str = geo_data["results"][0].get("location", "")
                                        
                                    if location_str:
                                        logger.info(f"Geocoding success: {location_str}")
                                except json.JSONDecodeError:
                                    pass
                        except Exception as e:
                            logger.error(f"Geocoding failed during fallback: {e}")

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

    async def search_locations(self, query: str, city: str = "") -> List[Location]:
        """
        Search for locations matching a query and return a list of candidates.
        """
        try:
            result = await call_mcp_tool("amap", "maps_text_search", {"keywords": query, "city": city})
            
            if isinstance(result, str):
                try:
                    data = json.loads(result)
                except json.JSONDecodeError:
                    return []
            else:
                data = result
                
            pois = data.get("pois", []) if isinstance(data, dict) else []
            if not pois and isinstance(data, list):
                pois = data
                
            locations = []
            for poi in pois:
                location_str = poi.get("location", "")
                if "," in location_str:
                    lng, lat = map(float, location_str.split(","))
                    locations.append(Location(
                        name=poi.get("name", query),
                        lat=lat,
                        lng=lng,
                        address=poi.get("address", ""),
                        city=poi.get("cityname", city)
                    ))
            
            return locations
            
        except Exception as e:
            logger.error(f"Error searching locations for {query}: {e}")
            return []

    async def get_travel_route(self, origin: Location, destination: Location, mode: str = "driving") -> Optional[RouteSegment]:
        """
        Get travel time and distance between two points.
        """
        try:
            # Prepare coords "lng,lat"
            origin_coords = f"{origin.lng},{origin.lat}"
            dest_coords = f"{destination.lng},{destination.lat}"
            
            # Map mode to tool
            tool_name = "maps_direction_driving"
            if mode == "transit":
                tool_name = "maps_direction_transit_integrated"
            elif mode == "walking":
                tool_name = "maps_direction_walking"
            elif mode == "bicycling":
                tool_name = "maps_direction_bicycling"
            
            params = {
                "origin": origin_coords,
                "destination": dest_coords
            }
            if mode == "transit":
                # Transit requires city usually, but AMap might infer or we pass origin city
                params["city"] = origin.city or "北京" 
                params["cityd"] = destination.city or "北京"

            result = await call_mcp_tool("amap", tool_name, params)
            
            logger.info(f"DEBUG: MCP Tool {tool_name} Result: {result[:500] if isinstance(result, str) else str(result)[:500]}")

            if isinstance(result, str):
                try:
                    data = json.loads(result)
                except:
                    logger.error(f"Failed to parse Route result")
                    return None
            else:
                data = result

            # Parse AMap direction response
            # Sometimes 'route' is top level, sometimes inside 'route' key depending on tool
            route_data = data.get("route", data) 
            paths = route_data.get("paths", [])
            transits = route_data.get("transits", [])
            
            logger.info(f"DEBUG: Parsed Route Data - Paths: {len(paths)}, Transits: {len(transits)}")
            
            distance = 0
            duration = 0
            detailed_mode = mode
            steps = []

            if paths:
                path = paths[0]
                distance = float(path.get("distance", 0)) / 1000.0 # meters to km
                duration = float(path.get("duration", 0)) / 60.0 # seconds to minutes
                
                # Extract driving/walking steps
                if "steps" in path:
                    for step in path["steps"]:
                        instr = step.get("instruction", "")
                        if instr:
                            steps.append(instr)
                            
            elif transits:
                path = transits[0]
                # Distance might be at top level for transit
                dist_val = float(path.get("distance", 0))
                if dist_val == 0:
                    dist_val = float(data.get("distance", 0))
                
                distance = dist_val / 1000.0
                duration = float(path.get("duration", 0)) / 60.0
                
                # Extract detailed transit info
                segments_list = path.get("segments", [])
                modes_found = []
                for seg in segments_list:
                    # Walking part
                    if seg.get("walking", {}).get("distance"):
                         walk_dist = seg["walking"]["distance"]
                         steps.append(f"步行 {walk_dist}米")
                    
                    # Bus/Train part
                    if seg.get("bus", {}).get("buslines"):
                        line = seg["bus"]["buslines"][0]
                        line_name = line["name"]
                        dep = line.get("departure_stop", {}).get("name", "起点")
                        arr = line.get("arrival_stop", {}).get("name", "终点")
                        
                        # Simplify name, e.g. "Metro Line 1 (X to Y)" -> "Metro Line 1"
                        simple_name = line_name.split("(")[0].strip()
                        if simple_name not in modes_found:
                            modes_found.append(simple_name)
                            
                        steps.append(f"乘坐 {simple_name} ({dep} 上车, {arr} 下车)")
                            
                    elif seg.get("railway", {}).get("name"):
                        r_name = seg["railway"]["name"]
                        dep = seg["railway"].get("departure_stop", {}).get("name", "")
                        arr = seg["railway"].get("arrival_stop", {}).get("name", "")
                        
                        if r_name not in modes_found:
                            modes_found.append(r_name)
                        
                        steps.append(f"乘坐 {r_name} ({dep} -> {arr})")
                
                if modes_found:
                    detailed_mode = " + ".join(modes_found)
                else:
                    detailed_mode = "Transit"

            if paths or transits:
                return RouteSegment(
                    origin=origin,
                    destination=destination,
                    distance_km=distance,
                    duration_minutes=duration,
                    strategy=detailed_mode,
                    steps=steps
                )
            
            return None

        except Exception as e:
            logger.error(f"Error getting route from {origin.name} to {destination.name}: {e}")
            return None

    async def optimize_route(self, locations: List[str], city: str = "", strategy: str = "driving", preference: str = "time") -> Dict[str, Any]:
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
            segment = None
            if strategy in ["smart", "best", "recommend"]:
                # Compare driving and transit
                seg_driving_task = self.get_travel_route(path[i], path[i+1], mode="driving")
                seg_transit_task = self.get_travel_route(path[i], path[i+1], mode="transit")
                
                d_res, t_res = await asyncio.gather(seg_driving_task, seg_transit_task)
                
                # Decision logic based on preference
                if d_res and t_res:
                    if preference == "distance":
                        # Prefer shorter distance
                        if d_res.distance_km <= t_res.distance_km:
                            segment = d_res
                        else:
                            segment = t_res
                    elif preference == "transit_first":
                        # Prefer transit if available
                        segment = t_res
                    elif preference == "driving_first":
                        # Prefer driving if available
                        segment = d_res
                    else:
                        # Default "time": Prefer faster duration
                        if d_res.duration_minutes <= t_res.duration_minutes:
                            segment = d_res
                        else:
                            segment = t_res
                elif d_res:
                    segment = d_res
                elif t_res:
                    segment = t_res
                else:
                    segment = None
            else:
                segment = await self.get_travel_route(path[i], path[i+1], mode=strategy)

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

    async def calculate_segment(self, origin_name: str, dest_name: str, mode: str, city: str = "") -> Dict[str, Any]:
        """
        Calculate details for a segment (distance, duration, cost).
        """
        # 1. Resolve locations
        origin = await self.get_location_details(origin_name, city)
        dest = await self.get_location_details(dest_name, city)
        
        if not origin or not dest:
            return {"error": "Could not resolve locations"}

        # 2. Get route
        # Map mode to AMap tools
        # mode: flight, train, driving, cycling, walking, transit
        
        amap_mode = "driving"
        if mode in ["transit", "train", "flight"]:
            amap_mode = "transit"
        elif mode == "walking":
            amap_mode = "walking"
        elif mode == "cycling":
            amap_mode = "bicycling"
            
        segment = await self.get_travel_route(origin, dest, mode=amap_mode)
        
        if not segment:
            return {"error": "Could not calculate route"}
            
        # 3. Estimate cost (Heuristics)
        cost = 0.0
        dist = segment.distance_km
        
        if mode == "driving":
            # Approx Taxi ~3-4 CNY/km
            cost = max(10, dist * 3.5)
        elif mode == "transit":
             # City transit
             if dist < 20:
                 cost = 2.0 + (dist // 5) * 1 # Rough metro pricing
             else:
                 cost = dist * 0.5 # Intercity bus/slow train
        elif mode == "flight":
             # Rough: 0.8 CNY/km + 150 base
             cost = 150 + dist * 0.8
        elif mode == "train":
             # High speed: 0.5 CNY/km
             cost = dist * 0.5
        elif mode in ["walking", "cycling"]:
             cost = 0.0
             
        return {
            "origin": {"name": origin.name, "lat": origin.lat, "lng": origin.lng, "address": origin.address, "city": origin.city},
            "destination": {"name": dest.name, "lat": dest.lat, "lng": dest.lng, "address": dest.address, "city": dest.city},
            "distance_km": round(segment.distance_km, 2),
            "duration_minutes": int(segment.duration_minutes),
            "cost_estimate": int(cost),
            "mode": mode,
            "details": {
                "transit_steps": segment.steps
            }
        }
