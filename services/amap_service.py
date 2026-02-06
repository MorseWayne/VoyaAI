"""
Amap (高德地图) Direct REST API Service.

Replaces MCP-based calls with direct HTTP requests for significantly better performance.
Each call is a single HTTP GET instead of MCP session init + tool discovery + JSON-RPC call.
"""
import logging
import httpx
from typing import Optional, Any

from config import get_settings

logger = logging.getLogger(__name__)

# Base URLs for Amap REST APIs
_BASE_V3 = "https://restapi.amap.com/v3"
_BASE_V4 = "https://restapi.amap.com/v4"
_BASE_V5 = "https://restapi.amap.com/v5"

# Reusable async HTTP client (created lazily)
_http_client: Optional[httpx.AsyncClient] = None


def _get_client() -> httpx.AsyncClient:
    """Get or create a reusable async HTTP client."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(15.0, connect=5.0),
            trust_env=False,  # Bypass proxy
        )
    return _http_client


def _get_key() -> str:
    """Get the Amap API key from settings."""
    settings = get_settings()
    key = settings.amap_api_key
    if not key:
        # Fallback: try to extract from MCP URL
        mcp_url = settings.amap_mcp_url or ""
        if "key=" in mcp_url:
            key = mcp_url.split("key=")[-1].split("&")[0]
    if not key:
        raise ValueError("AMAP_API_KEY is not configured. Set it in .env file.")
    return key


async def _get(url: str, params: dict[str, Any]) -> dict:
    """Make a GET request and return parsed JSON."""
    client = _get_client()
    params["key"] = _get_key()

    logger.debug(f"[Amap API] GET {url} params={params}")
    resp = await client.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    # Check for API-level errors
    # V3/V5: status="1" for success, status="0" for error
    # V4 (bicycling): errcode=0 for success, no "status" field
    status = data.get("status")
    if status is not None and str(status) == "0":
        info = data.get("info", "Unknown error")
        infocode = data.get("infocode", "")
        logger.error(f"[Amap API] Error: {info} (code={infocode})")
        raise ValueError(f"Amap API error: {info} (code={infocode})")
    
    errcode = data.get("errcode")
    if errcode is not None and int(errcode) != 0:
        errmsg = data.get("errmsg", "Unknown error")
        logger.error(f"[Amap API] Error: {errmsg} (errcode={errcode})")
        raise ValueError(f"Amap API error: {errmsg} (errcode={errcode})")

    return data


# ======================== POI Search ========================

async def text_search(keywords: str, city: str = "", page_size: int = 10) -> dict:
    """
    POI 关键字搜索 (V5).
    
    Returns: { "pois": [...], "count": "N", ... }
    """
    params = {"keywords": keywords}
    if city:
        params["region"] = city
    if page_size != 10:
        params["page_size"] = str(page_size)
    params["show_fields"] = "business"

    return await _get(f"{_BASE_V5}/place/text", params)


async def around_search(location: str, keywords: str = "", types: str = "",
                        radius: int = 5000, page_size: int = 10) -> dict:
    """
    POI 周边搜索 (V5).
    
    Args:
        location: "lng,lat" format
        keywords: search keywords
        types: POI type codes
        radius: search radius in meters (0-50000)
    """
    params = {"location": location, "radius": str(radius)}
    if keywords:
        params["keywords"] = keywords
    if types:
        params["types"] = types
    if page_size != 10:
        params["page_size"] = str(page_size)

    return await _get(f"{_BASE_V5}/place/around", params)


async def input_tips(keywords: str, city: str = "", city_limit: bool = False, type_code: str = "") -> dict:
    """
    输入提示 / 自动补全 (V3).
    Very fast, ideal for search-as-you-type.
    
    Returns: { "tips": [{"name": ..., "address": ..., "location": "lng,lat", ...}] }
    """
    params = {"keywords": keywords}
    
    # If explicitly searching for cities, restrict by POI type code for administrative regions
    # 190100: Place Name (地名地址信息)
    if type_code:
        params["type"] = type_code
        
    if city:
        params["city"] = city
    if city_limit:
        params["citylimit"] = "true"

    return await _get(f"{_BASE_V3}/assistant/inputtips", params)


# ======================== Geocoding ========================

async def geocode(address: str, city: str = "") -> dict:
    """
    地理编码 - 地址转坐标 (V3).
    
    Returns: { "geocodes": [{"location": "lng,lat", ...}] }
    """
    params = {"address": address}
    if city:
        params["city"] = city

    return await _get(f"{_BASE_V3}/geocode/geo", params)


# ======================== Route Planning (V3) ========================
# Note: V5 direction APIs require separate authorization.
# V3 is universally available and matches what AMap MCP uses internally.

async def direction_driving(origin: str, destination: str,
                            strategy: int = 0,
                            extensions: str = "all") -> dict:
    """
    驾车路径规划 V3.
    
    Args:
        origin: "lng,lat"
        destination: "lng,lat"
        strategy: 0=速度优先, 1=费用优先, 2=距离优先,
                  4=躲避拥堵, 5=多策略(躲避拥堵+速度优先),
                  6=不走高速, 7=不走高速且避免收费,
                  8=躲避拥堵且不走高速, 9=躲避拥堵且不走高速且避免收费
        extensions: "base" or "all" (all includes step details)
    """
    params = {
        "origin": origin,
        "destination": destination,
        "strategy": str(strategy),
        "extensions": extensions,
    }
    return await _get(f"{_BASE_V3}/direction/driving", params)


async def direction_walking(origin: str, destination: str,
                            extensions: str = "all") -> dict:
    """
    步行路径规划 V3.
    """
    params = {
        "origin": origin,
        "destination": destination,
        "extensions": extensions,
    }
    return await _get(f"{_BASE_V3}/direction/walking", params)


async def direction_transit(origin: str, destination: str,
                            city1: str, city2: str = "",
                            strategy: int = 0,
                            extensions: str = "all") -> dict:
    """
    公交路径规划 V3.
    
    Args:
        city1: 起点城市 (citycode or city name)
        city2: 终点城市 (defaults to city1 if empty)
        strategy: 0=最快, 1=最经济, 2=最少换乘, 3=最少步行, 5=不乘地铁
    """
    params = {
        "origin": origin,
        "destination": destination,
        "city": city1,
        "cityd": city2 or city1,
        "strategy": str(strategy),
        "extensions": extensions,
    }
    return await _get(f"{_BASE_V3}/direction/transit/integrated", params)


async def direction_bicycling(origin: str, destination: str) -> dict:
    """
    骑行路径规划 V4.
    """
    params = {
        "origin": origin,
        "destination": destination,
    }
    return await _get(f"{_BASE_V4}/direction/bicycling", params)


async def distance_measure(origins: str, destination: str, type: int = 1) -> dict:
    """
    距离测量 V3.
    
    Args:
        origins: "lng1,lat1|lng2,lat2|..." (up to 100)
        destination: "lng,lat"
        type: 0=直线, 1=驾车, 3=步行(5km内)
    """
    params = {
        "origins": origins,
        "destination": destination,
        "type": str(type),
    }
    return await _get(f"{_BASE_V3}/distance", params)


# ======================== Cleanup ========================

async def close():
    """Close the HTTP client."""
    global _http_client
    if _http_client and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None
