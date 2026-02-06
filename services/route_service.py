"""
Route Service - Handles geocoding, routing, and optimization using Amap REST API.

Uses direct HTTP calls to Amap Web Service API for best performance.
Falls back to MCP only if direct API key is not configured.
"""
import logging
import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from api.models import TransportMode, Segment, Location as ApiLocation

from services import amap_service

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
    Service for route planning and optimization using Amap Direct REST API.
    """
    
    async def get_location_details(self, place_name: str, city: str = "") -> Optional[Location]:
        """
        Search for a location to get its coordinates.
        Uses Amap POI text search V5 API directly.
        """
        try:
            data = await amap_service.text_search(place_name, city=city, page_size=5)
            
            pois = data.get("pois", [])
            
            if pois:
                top_poi = pois[0]
                location_str = top_poi.get("location", "")
                
                # If location is missing but we have an address, try geocoding
                if not location_str and top_poi.get("address"):
                    address = top_poi.get("address", "")
                    if isinstance(address, list):
                        address = "".join(str(x) for x in address)
                        
                    if address:
                        logger.info(f"POI found but no location. Geocoding address: {address}")
                        try:
                            geo_data = await amap_service.geocode(address, city=city)
                            geocodes = geo_data.get("geocodes", [])
                            if geocodes:
                                location_str = geocodes[0].get("location", "")
                                if location_str:
                                    logger.info(f"Geocoding success: {location_str}")
                        except Exception as e:
                            logger.error(f"Geocoding failed during fallback: {e}")

                if location_str and "," in location_str:
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
        Uses Amap POI text search V5 API directly.
        """
        try:
            data = await amap_service.text_search(query, city=city, page_size=10)
            
            pois = data.get("pois", [])
            
            locations = []
            
            for poi in pois[:8]:  # Limit to top 8
                loc_str = poi.get("location", "")
                name = poi.get("name", query)
                address = poi.get("address", "")
                city_name = poi.get("cityname", city)
                
                # If no location, try geocoding address
                if not loc_str and address:
                    try:
                        clean_address = address.split('(')[0].split('（')[0]
                        geo_data = await amap_service.geocode(clean_address, city=city_name)
                        geocodes = geo_data.get("geocodes", [])
                        if geocodes:
                            loc_str = geocodes[0].get("location", "")
                    except Exception as e:
                        logger.warning(f"Geocoding failed for {name}: {e}")
                
                if loc_str and "," in loc_str:
                    try:
                        lng, lat = map(float, loc_str.split(","))
                        locations.append(Location(
                            name=name, lat=lat, lng=lng,
                            address=address, city=city_name
                        ))
                    except (ValueError, TypeError):
                        pass
            
            return locations
            
        except Exception as e:
            logger.error(f"Error searching locations for {query}: {e}")
            return []

    async def get_travel_route(self, origin: Location, destination: Location, mode: str = "driving") -> Optional[RouteSegment]:
        """
        Get travel time and distance between two points.
        Uses Amap direction APIs directly.
        """
        try:
            origin_coords = f"{origin.lng},{origin.lat}"
            dest_coords = f"{destination.lng},{destination.lat}"
            
            data = None
            
            if mode == "driving":
                data = await amap_service.direction_driving(origin_coords, dest_coords)
            elif mode == "transit":
                city1 = origin.city or "北京"
                city2 = destination.city or city1
                data = await amap_service.direction_transit(
                    origin_coords, dest_coords, city1=city1, city2=city2
                )
            elif mode == "walking":
                data = await amap_service.direction_walking(origin_coords, dest_coords)
            elif mode == "bicycling":
                data = await amap_service.direction_bicycling(origin_coords, dest_coords)
            else:
                # Default to driving
                data = await amap_service.direction_driving(origin_coords, dest_coords)

            if not data:
                return None

            logger.debug(f"Route API response keys: {list(data.keys())}")

            # Parse response
            # V3 driving/walking/transit: { "route": { "paths": [...] } }
            # V4 bicycling: { "data": { "paths": [...] } }
            if "data" in data and "route" not in data:
                route_data = data["data"]
            else:
                route_data = data.get("route", data)
            paths = route_data.get("paths", [])
            transits = route_data.get("transits", [])
            
            distance = 0
            duration = 0
            detailed_mode = mode
            steps = []

            if paths:
                path = paths[0]
                distance = float(path.get("distance", 0)) / 1000.0  # meters to km
                duration = float(path.get("duration", 0)) / 60.0    # seconds to minutes
                
                # Extract steps for driving/walking
                if "steps" in path:
                    for step in path["steps"]:
                        instr = step.get("instruction", "")
                        if instr:
                            steps.append(instr)
                            
            elif transits:
                path = transits[0]
                dist_val = float(path.get("distance", 0))
                if dist_val == 0:
                    dist_val = float(route_data.get("distance", 0))
                
                distance = dist_val / 1000.0
                duration = float(path.get("duration", 0)) / 60.0
                
                # Extract transit details
                segments_list = path.get("segments", [])
                modes_found = []
                for seg in segments_list:
                    if seg.get("walking", {}).get("distance"):
                        walk_dist = seg["walking"]["distance"]
                        steps.append(f"步行 {walk_dist}米")
                    
                    if seg.get("bus", {}).get("buslines"):
                        line = seg["bus"]["buslines"][0]
                        line_name = line["name"]
                        dep = line.get("departure_stop", {}).get("name", "起点")
                        arr = line.get("arrival_stop", {}).get("name", "终点")
                        
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
        1. Resolve all locations.
        2. Greedy nearest neighbor ordering.
        3. Calculate route details for final order.
        """
        # 1. Resolve Locations (parallel for speed)
        tasks = [self.get_location_details(loc_name, city) for loc_name in locations]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        resolved_locations = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to resolve location '{locations[i]}': {result}")
            elif result:
                resolved_locations.append(result)
            else:
                logger.warning(f"Skipping unresolved location: {locations[i]}")

        if not resolved_locations:
            return {"error": "No valid locations found"}

        # 2. Optimize (Greedy Nearest Neighbor)
        path = [resolved_locations.pop(0)]
        total_dist = 0
        total_time = 0
        segments = []

        while resolved_locations:
            current = path[-1]
            best_next = None
            min_dist = float('inf')
            best_idx = -1

            for i, candidate in enumerate(resolved_locations):
                dist_approx = ((current.lat - candidate.lat)**2 + (current.lng - candidate.lng)**2)**0.5
                
                if dist_approx < min_dist:
                    min_dist = dist_approx
                    best_next = candidate
                    best_idx = i

            path.append(best_next)
            resolved_locations.pop(best_idx)

        # 3. Calculate full route details
        final_route_details = []
        for i in range(len(path) - 1):
            segment = None
            if strategy in ["smart", "best", "recommend"]:
                # Compare driving and transit in parallel
                d_res, t_res = await asyncio.gather(
                    self.get_travel_route(path[i], path[i+1], mode="driving"),
                    self.get_travel_route(path[i], path[i+1], mode="transit"),
                )
                
                if d_res and t_res:
                    if preference == "distance":
                        segment = d_res if d_res.distance_km <= t_res.distance_km else t_res
                    elif preference == "transit_first":
                        segment = t_res
                    elif preference == "driving_first":
                        segment = d_res
                    else:  # Default "time"
                        segment = d_res if d_res.duration_minutes <= t_res.duration_minutes else t_res
                elif d_res:
                    segment = d_res
                elif t_res:
                    segment = t_res
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
        # 1. Resolve locations (parallel)
        origin, dest = await asyncio.gather(
            self.get_location_details(origin_name, city),
            self.get_location_details(dest_name, city),
        )
        
        if not origin or not dest:
            return {"error": "Could not resolve locations"}

        # 2. Map mode to Amap direction API
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
            cost = max(10, dist * 3.5)
        elif mode == "transit":
            if dist < 20:
                cost = 2.0 + (dist // 5) * 1
            else:
                cost = dist * 0.5
        elif mode == "flight":
            cost = 150 + dist * 0.8
        elif mode == "train":
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
