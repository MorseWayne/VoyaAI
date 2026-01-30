"""
API Routes for VoyaAI Travel Planning Service.
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from services import TravelService

logger = logging.getLogger(__name__)
router = APIRouter()

# Service instance
travel_service = TravelService()


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


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "VoyaAI",
        "description": "AI-powered travel planning assistant",
        "version": "1.0.0",
        "endpoints": {
            "POST /travel/plan": "Generate a travel plan (JSON response)",
            "GET /travel/chat": "Generate a travel plan (simple query)",
            "GET /travel/html": "Get the latest generated HTML",
        }
    }


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


@router.get("/travel/chat")
async def travel_chat(content: str):
    """
    Simple GET endpoint for travel planning.
    
    Compatible with the original Java API:
    GET /travel/chat?content=your_travel_requirements
    """
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
    xhs_mcp_dir = Path(settings.xhs_mcp_dir) if settings.xhs_mcp_dir else None
    xhs_status = {
        "configured": bool(settings.xhs_cookie and settings.xhs_mcp_dir),
        "cookie_set": bool(settings.xhs_cookie),
        "mcp_dir": settings.xhs_mcp_dir or "(not set)",
        "mcp_dir_exists": xhs_mcp_dir.exists() if xhs_mcp_dir else False,
    }
    
    # Check Weather MCP
    weather_status = {
        "configured": bool(settings.weather_mcp_url),
        "url": settings.weather_mcp_url or "(not set)",
    }
    
    # Check Amap MCP
    amap_status = {
        "configured": bool(settings.amap_mcp_url),
        "url": settings.amap_mcp_url[:50] + "..." if settings.amap_mcp_url and len(settings.amap_mcp_url) > 50 else settings.amap_mcp_url or "(not set)",
        "has_key": "key=" in (settings.amap_mcp_url or "").lower(),
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
            "test_llm": "python tests/test_llm.py",
            "test_xhs": "python tests/test_xhs_mcp.py",
            "test_weather": "python tests/test_weather_mcp.py",
            "test_amap": "python tests/test_amap_mcp.py",
            "test_all": "python tests/test_all.py",
        }
    }
