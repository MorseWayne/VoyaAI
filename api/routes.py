"""
API Routes for VoyaAI Travel Planning Service.
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field

from config import get_settings
from services import TravelService, RouteService
from services.storage_service import StorageService
from api.models import Itinerary, Segment, TransportMode

logger = logging.getLogger(__name__)
router = APIRouter()

# Service instances
travel_service = TravelService()
route_service = RouteService()
storage_service = StorageService()


class TravelRequest(BaseModel):
    """Travel planning request model."""
    content: str = Field(
        ...,
        description="Travel requirements and preferences",
        examples=[
            "请帮我规划一份日本大阪5天的旅游攻略，预算5000-6000，主要想去环球影城和购物"
        ]
    )


class TravelResponse(BaseModel):
    """Travel planning response model."""
    success: bool
    message: str
    guide_text: Optional[str] = None
    html_content: Optional[str] = None


class RouteRequest(BaseModel):
    """Route optimization request model."""
    locations: list[str] = Field(
        ...,
        description="List of location names to visit",
        min_items=2,
        example=["Guangzhou Tower", "Baiyun Mountain", "Chimelong Safari Park"]
    )
    city: str = Field("", description="City context for resolving location names")
    strategy: str = Field("driving", description="Travel strategy: driving, walking, transit")
    preference: str = Field("time", description="Optimization preference: time, distance, transit_first, driving_first")



@router.get("/")
async def root():
    """Root endpoint redirects to Landing Page."""
    return RedirectResponse(url="/static/index.html")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@router.post("/travel/plan", response_model=TravelResponse)
async def create_travel_plan(request: TravelRequest):
    """
    Generate a comprehensive travel plan.
    
    This endpoint accepts travel requirements and returns a complete
    travel itinerary with both text and HTML formats.
    """
    # Temporarily disabled per user request
    raise HTTPException(
        status_code=503,
        detail="AI Travel Planning feature is temporarily disabled. Please use the Route Planner."
    )

    try:
        logger.info(f"Received travel plan request: {request.content[:100]}...")
        
        plan = await travel_service.generate_travel_guide(request.content)
        
        return TravelResponse(
            success=True,
            message="Travel plan generated successfully",
            guide_text=plan.guide_text,
            html_content=plan.html_content,
        )
        
    except Exception as e:
        logger.error(f"Error generating travel plan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate travel plan: {str(e)}"
        )


@router.post("/travel/optimize")
async def optimize_route(request: RouteRequest):
    """
    Optimize travel route for a list of locations.
    Returns optimized order, travel times, and map data.
    """
    try:
        logger.info(f"Optimizing route for {len(request.locations)} locations in {request.city} with strategy {request.strategy}, preference {request.preference}")
        
        result = await route_service.optimize_route(request.locations, request.city, request.strategy, request.preference)
        
        if "error" in result:
             raise HTTPException(status_code=400, detail=result["error"])
             
        return result
        
    except Exception as e:
        logger.error(f"Error optimizing route: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize route: {str(e)}"
        )


@router.get("/travel/chat")
async def travel_chat(content: str):
    """
    Simple GET endpoint for travel planning.
    
    Compatible with the original Java API:
    GET /travel/chat?content=your_travel_requirements
    """
    # Temporarily disabled per user request
    raise HTTPException(
        status_code=503,
        detail="AI Travel Planning feature is temporarily disabled. Please use the Route Planner."
    )

    try:
        logger.info(f"Received travel chat request: {content[:100]}...")
        
        plan = await travel_service.generate_travel_guide(content)
        
        return {
            "success": True,
            "message": "Travel plan generated and saved to output/travel.html",
            "guide_preview": plan.guide_text[:500] + "..." if len(plan.guide_text) > 500 else plan.guide_text,
        }
        
    except Exception as e:
        logger.error(f"Error in travel chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate travel plan: {str(e)}"
        )


@router.get("/travel/html", response_class=HTMLResponse)
async def get_travel_html():
    """
    Get the latest generated travel HTML page.
    """
    from pathlib import Path
    
    html_path = Path("output/travel.html")
    
    if not html_path.exists():
        raise HTTPException(
            status_code=404,
            detail="No travel plan has been generated yet. Use /travel/plan first."
        )
    
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)


@router.get("/test")
async def test_endpoint(content: str):
    """
    Test endpoint for simple chat without full travel planning.
    """
    from services.llm_factory import simple_chat
    
    try:
        response = await simple_chat(content)
        
        return {
            "input": content,
            "response": response,
        }
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/status")
async def get_service_status():
    """
    Get status of all MCP services and LLM connection.
    
    This endpoint provides a quick overview of which services are configured
    and available without actually calling them.
    """
    from config import get_settings
    from pathlib import Path
    
    settings = get_settings()
    
    # Check LLM configuration
    llm_status = {
        "configured": bool(settings.llm_base_url and settings.llm_api_key),
        "base_url": settings.llm_base_url,
        "model": settings.llm_model,
        "api_key": "***" + settings.llm_api_key[-4:] if len(settings.llm_api_key) > 4 else "(not set)",
    }
    
    # Check Xiaohongshu MCP
    xhs_status = {
        "configured": bool(settings.xhs_mcp_url),
        "url": settings.xhs_mcp_url or "(not set)",
    }
    
    # Check Weather MCP
    weather_status = {
        "configured": bool(settings.weather_mcp_url),
        "url": settings.weather_mcp_url or "(not set)",
    }
    
    # Check Amap API (direct REST API, no longer MCP)
    amap_status = {
        "configured": bool(settings.amap_api_key),
        "mode": "direct_api" if settings.amap_api_key else ("mcp_legacy" if settings.amap_mcp_url else "not_configured"),
        "api_key": "***" + settings.amap_api_key[-4:] if len(settings.amap_api_key) > 4 else "(not set)",
    }
    
    # Summary
    services_configured = sum([
        llm_status["configured"],
        xhs_status["configured"],
        weather_status["configured"],
        amap_status["configured"],
    ])
    
    return {
        "status": "healthy",
        "services_configured": f"{services_configured}/4",
        "llm": llm_status,
        "xiaohongshu_mcp": xhs_status,
        "weather_mcp": weather_status,
        "amap_mcp": amap_status,
        "tips": {
            "test_llm": "uv run python tests/test_llm.py",
            "test_xhs": "uv run python tests/test_xhs_mcp.py",
            "test_weather": "uv run python tests/test_weather_mcp.py",
            "test_amap": "uv run python tests/test_amap_mcp.py",
            "test_all": "uv run python tests/test_all.py",
        }
    }


# --- Itinerary / Plan Management Endpoints ---

@router.post("/travel/plans", response_model=Itinerary)
async def save_plan(plan: Itinerary):
    """Save or update a travel plan."""
    try:
        return storage_service.save_plan(plan)
    except Exception as e:
        logger.error(f"Error saving plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/travel/plans", response_model=list[Itinerary])
async def list_plans():
    """List all saved plans."""
    try:
        return storage_service.list_plans()
    except Exception as e:
        logger.error(f"Error listing plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/travel/plans/{plan_id}", response_model=Itinerary)
async def get_plan(plan_id: str):
    """Get a specific plan by ID."""
    try:
        plan = storage_service.get_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/travel/plans/{plan_id}")
async def delete_plan(plan_id: str):
    """Delete a plan by ID."""
    try:
        success = storage_service.delete_plan(plan_id)
        if not success:
            raise HTTPException(status_code=404, detail="Plan not found")
        return {"success": True, "message": "Plan deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class SegmentCalculationRequest(BaseModel):
    origin: str
    destination: str
    mode: str = "driving"
    city: str = ""

@router.post("/travel/calculate-segment")
async def calculate_segment(request: SegmentCalculationRequest):
    """
    Calculate distance, duration, and cost for a segment.
    Used when user edits a card and selects transport.
    """
    try:
        result = await route_service.calculate_segment(
            request.origin, 
            request.destination, 
            request.mode, 
            request.city
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"Error calculating segment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class LocationSearchRequest(BaseModel):
    query: str
    city: str = ""

@router.post("/travel/locations/search")
async def search_locations_endpoint(request: LocationSearchRequest):
    """
    Search for locations matching a query.
    Returns a list of candidates using Amap POI text search.
    """
    try:
        locations = await route_service.search_locations(request.query, request.city)
        return [
            {
                "name": loc.name,
                "lat": loc.lat,
                "lng": loc.lng,
                "address": loc.address,
                "city": loc.city
            }
            for loc in locations
        ]
    except Exception as e:
        logger.error(f"Error searching locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/travel/locations/tips")
async def location_input_tips(keywords: str, city: str = ""):
    """
    Fast input tips / autocomplete for location search.
    Uses Amap Input Tips API (V3) - very fast, ideal for search-as-you-type.
    """
    from services import amap_service
    try:
        data = await amap_service.input_tips(keywords, city=city, city_limit=bool(city))
        tips = data.get("tips", [])
        return [
            {
                "name": tip.get("name", ""),
                "address": tip.get("address", ""),
                "location": tip.get("location", ""),
                "district": tip.get("district", ""),
                "city": city,
            }
            for tip in tips
            if tip.get("name") and tip.get("location")
        ]
    except Exception as e:
        logger.error(f"Error getting input tips: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/travel/locations/resolve")
async def resolve_location(request: LocationSearchRequest):
    """
    Resolve a location name to coordinates and address.
    """
    try:
        result = await route_service.get_location_details(request.query, request.city)
        if not result:
            raise HTTPException(status_code=404, detail="Location not found")
            
        return {
            "name": result.name,
            "lat": result.lat,
            "lng": result.lng,
            "address": result.address,
            "city": result.city
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving location: {e}")
        raise HTTPException(status_code=500, detail=str(e))
