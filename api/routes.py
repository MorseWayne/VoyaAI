"""
API Routes for VoyaAI Travel Planning Service.
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
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
    from services.llm_factory import create_llm
    
    try:
        llm = create_llm(for_tools=False)
        response = await llm.ainvoke(content)
        
        return {
            "input": content,
            "response": response.content,
        }
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
