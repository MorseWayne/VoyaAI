"""
Route Service - Handles geocoding, routing, and optimization using Amap REST API.

Uses direct HTTP calls to Amap Web Service API for best performance.
Falls back to MCP only if direct API key is not configured.
Uses 12306 MCP for real train/rail schedule data when available.
"""
import logging
import json
import re
import math
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from api.models import TransportMode, Segment, Location as ApiLocation

from services import amap_service
from mcp_services.clients import get_mcp_manager

logger = logging.getLogger(__name__)

# 出行方式的最小合理距离（单位：公里），留空表示不限制，用户可自由选择高铁/飞机等
MODE_MIN_DISTANCE_KM = {}

# 出行方式的中文名称映射
MODE_DISPLAY_NAME = {
    "flight": "飞机",
    "train": "火车/高铁",
    "driving": "驾车",
    "transit": "公交/地铁",
    "walking": "步行",
    "cycling": "骑行",
    "bicycling": "骑行",
}


def _as_dict(val) -> dict:
    """Safely return val as a dict. Amap API sometimes returns [] instead of {} for empty objects."""
    return val if isinstance(val, dict) else {}


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth (Haversine formula).
    Returns distance in kilometers.
    """
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


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
                duration = float(path.get("duration", 0)) / 60.0
                
                # Extract transit details and accumulate real distance
                # Note: Amap v3 API `transits[].distance` is walking distance only,
                # NOT the total travel distance. We must sum up distances from all
                # segment components (walking + bus/subway + railway) for accuracy.
                segments_list = path.get("segments", [])
                modes_found = []
                accumulated_dist_m = 0.0  # Total distance in meters

                for seg in segments_list:
                    walking = _as_dict(seg.get("walking"))
                    bus = _as_dict(seg.get("bus"))
                    railway = _as_dict(seg.get("railway"))
                    
                    if walking.get("distance"):
                        walk_dist = float(walking["distance"])
                        accumulated_dist_m += walk_dist
                        steps.append(f"步行 {int(walk_dist)}米")
                    
                    buslines = bus.get("buslines")
                    if buslines:
                        line = buslines[0]
                        line_dist = float(line.get("distance", 0))
                        accumulated_dist_m += line_dist
                        line_name = line.get("name", "")
                        dep = _as_dict(line.get("departure_stop")).get("name", "起点")
                        arr = _as_dict(line.get("arrival_stop")).get("name", "终点")
                        
                        simple_name = line_name.split("(")[0].strip()
                        if simple_name not in modes_found:
                            modes_found.append(simple_name)
                        steps.append(f"乘坐 {simple_name} ({dep} 上车, {arr} 下车)")
                            
                    elif railway.get("name"):
                        r_name = railway["name"]
                        rail_dist = float(railway.get("distance", 0))
                        accumulated_dist_m += rail_dist
                        dep = _as_dict(railway.get("departure_stop")).get("name", "")
                        arr = _as_dict(railway.get("arrival_stop")).get("name", "")
                        
                        if r_name not in modes_found:
                            modes_found.append(r_name)
                        steps.append(f"乘坐 {r_name} ({dep} -> {arr})")
                
                # Use accumulated segment distance; fall back to route-level distance
                if accumulated_dist_m > 0:
                    distance = accumulated_dist_m / 1000.0
                else:
                    dist_val = float(path.get("distance", 0))
                    if dist_val == 0:
                        dist_val = float(route_data.get("distance", 0))
                    distance = dist_val / 1000.0

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

    # ==================== 12306 MCP Integration ====================

    def _generate_station_candidates(self, name: str, city: str = "") -> List[str]:
        """
        Generate candidate 12306 station names from a POI name.
        E.g. "珠海金湾机场" → ["珠海金湾机场", "珠海机场"]
             "珠海站"       → ["珠海站", "珠海"]
             "广州南站"     → ["广州南站", "广州南"]
        """
        candidates = []
        name = name.strip()
        candidates.append(name)

        # Remove common station suffixes
        for suffix in ["火车站", "高铁站", "动车站", "站"]:
            if name.endswith(suffix) and len(name) > len(suffix):
                candidates.append(name[:-len(suffix)])
                break

        # For airports: "珠海金湾机场" → "珠海机场"
        if "机场" in name:
            city_short = city.rstrip("市省区县") if city else ""
            if city_short:
                airport_candidate = f"{city_short}机场"
                if airport_candidate not in candidates:
                    candidates.append(airport_candidate)

        # Deduplicate while preserving order
        seen = set()
        result = []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                result.append(c)
        return result

    async def _resolve_12306_station(self, name: str, city: str = "") -> Optional[Tuple[str, str]]:
        """
        Resolve a location name to a 12306 station (code, name).
        Tries multiple candidate names. Returns (station_code, station_name) or None.
        """
        manager = get_mcp_manager()
        if not manager.is_available("train_12306"):
            return None

        candidates = self._generate_station_candidates(name, city)
        names_query = "|".join(candidates)

        try:
            result_str = await manager.call_tool(
                "train_12306", "get-station-code-by-names",
                {"stationNames": names_query}
            )
            result = json.loads(result_str)

            # Return the first candidate that was found
            for cand in candidates:
                info = result.get(cand)
                if info and info.get("station_code"):
                    return (info["station_code"], info["station_name"])
        except Exception as e:
            logger.debug(f"12306 station lookup failed for '{name}': {e}")

        # Fallback: search all stations in the city
        if city:
            try:
                city_short = city.rstrip("市省区县")
                result_str = await manager.call_tool(
                    "train_12306", "get-stations-code-in-city",
                    {"city": city_short}
                )
                stations = json.loads(result_str)
                if isinstance(stations, list):
                    # Try substring matching
                    for s in stations:
                        s_name = s.get("station_name", "")
                        if s_name and (s_name in name or name in s_name):
                            return (s["station_code"], s_name)
            except Exception as e:
                logger.debug(f"12306 city station lookup failed for '{city}': {e}")

        return None

    async def _query_train_12306(self, origin: 'Location', destination: 'Location') -> Optional[Dict[str, Any]]:
        """
        Query 12306 MCP for real train schedule data between two locations.
        Returns dict with train info or None if unavailable.
        """
        manager = get_mcp_manager()
        if not manager.is_available("train_12306"):
            return None

        try:
            # 1. Resolve station codes (parallel)
            origin_task = self._resolve_12306_station(origin.name, origin.city)
            dest_task = self._resolve_12306_station(destination.name, destination.city)
            origin_station, dest_station = await asyncio.gather(origin_task, dest_task)

            if not origin_station or not dest_station:
                logger.info(f"12306: Could not resolve stations for '{origin.name}' -> '{destination.name}'")
                return None

            origin_code, origin_sname = origin_station
            dest_code, dest_sname = dest_station

            # 2. Get tomorrow's date (today's trains may have already departed)
            tz_cn = timezone(timedelta(hours=8))
            tomorrow = (datetime.now(tz_cn) + timedelta(days=1)).strftime("%Y-%m-%d")

            # 3. Query tickets
            result_str = await manager.call_tool("train_12306", "get-tickets", {
                "date": tomorrow,
                "fromStation": origin_code,
                "toStation": dest_code,
                "format": "json",
                "limitedNum": 5,
            })
            tickets = json.loads(result_str)

            if not tickets or not isinstance(tickets, list):
                logger.info(f"12306: No trains found {origin_sname} -> {dest_sname}")
                return None

            # 4. Pick the best (shortest duration) train
            best = min(tickets, key=lambda t: t.get("lishi", "99:99"))
            duration_str = best.get("lishi", "")  # e.g. "00:35"
            duration_min = 0
            if duration_str and ":" in duration_str:
                parts = duration_str.split(":")
                duration_min = int(parts[0]) * 60 + int(parts[1])

            # Extract price from the first available seat type
            price = 0
            for p in best.get("prices", []):
                if p.get("price"):
                    price = int(p["price"])
                    break

            # Calculate approximate distance using haversine
            distance_km = _haversine_km(origin.lat, origin.lng, destination.lat, destination.lng)

            return {
                "duration_minutes": duration_min,
                "distance_km": round(distance_km, 1),
                "cost_estimate": price,
                "train_no": best.get("start_train_code", ""),
                "from_station": best.get("from_station", origin_sname),
                "to_station": best.get("to_station", dest_sname),
                "departure_time": best.get("start_time", ""),
                "arrival_time": best.get("arrive_time", ""),
                "total_trains": len(tickets),
            }

        except Exception as e:
            logger.warning(f"12306 query failed ({origin.name} -> {destination.name}): {e}")
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
        # 1. Resolve locations (串行 + 间隔，避免高德 QPS 超限 CUQPS_HAS_EXCEEDED_THE_LIMIT)
        origin = await self.get_location_details(origin_name, city)
        await asyncio.sleep(0.4)
        dest = await self.get_location_details(dest_name, city)
        
        if not origin or not dest:
            return {"error": "Could not resolve locations"}

        # 2. Check if the transport mode is reasonable for the distance
        straight_line_km = _haversine_km(origin.lat, origin.lng, dest.lat, dest.lng)
        min_km = MODE_MIN_DISTANCE_KM.get(mode)
        if min_km is not None and straight_line_km < min_km:
            mode_name = MODE_DISPLAY_NAME.get(mode, mode)
            suggested = []
            if straight_line_km < 3:
                suggested = ["步行", "骑行", "驾车"]
            elif straight_line_km < 30:
                suggested = ["驾车", "公交/地铁"]
            else:
                suggested = ["驾车", "公交/地铁"]
            suggest_text = "、".join(suggested)
            return {
                "error": f"两地直线距离仅 {straight_line_km:.1f} 公里，不适合使用「{mode_name}」出行。建议选择：{suggest_text}",
                "error_type": "mode_not_suitable",
                "straight_line_km": round(straight_line_km, 1),
                "mode_requested": mode,
            }

        # 3. For train mode, try 12306 MCP first for real rail data
        if mode == "train":
            train_data = await self._query_train_12306(origin, dest)
            if train_data:
                logger.info(f"12306: Found train {train_data['train_no']} "
                            f"{train_data['from_station']} -> {train_data['to_station']} "
                            f"{train_data['duration_minutes']}min")
                return {
                    "origin": {"name": origin.name, "lat": origin.lat, "lng": origin.lng, "address": origin.address, "city": origin.city},
                    "destination": {"name": dest.name, "lat": dest.lat, "lng": dest.lng, "address": dest.address, "city": dest.city},
                    "distance_km": train_data["distance_km"],
                    "duration_minutes": train_data["duration_minutes"],
                    "cost_estimate": train_data["cost_estimate"],
                    "mode": "train",
                    "details": {
                        "train_no": train_data["train_no"],
                        "from_station": train_data["from_station"],
                        "to_station": train_data["to_station"],
                        "departure_time": train_data.get("departure_time"),
                        "arrival_time": train_data.get("arrival_time"),
                        "total_trains": train_data.get("total_trains", 0),
                        "transit_steps": [
                            f"乘坐 {train_data['train_no']} ({train_data['from_station']} -> {train_data['to_station']})"
                        ],
                    }
                }
            else:
                logger.info("12306: No train data, falling back to Amap transit API")

        # 4. Map mode to Amap direction API (fallback for train, or primary for other modes)
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
            
        # 5. Estimate cost (Heuristics)
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
