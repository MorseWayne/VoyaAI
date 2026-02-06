"""
VoyaAI - AI-powered Travel Planning Assistant

An intelligent travel planning assistant that integrates multiple information
sources including social media travel guides, real-time weather forecasts,
and map routing to generate comprehensive travel itineraries.
"""
import logging
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_settings
from api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application."""
    settings = get_settings()
    logger.info("=" * 50)
    logger.info("🧭 VoyaAI Starting (Route Planner Mode)...")
    logger.info(f"   Mode: Route Planner Only")
    logger.info(f"   Server: http://{settings.host}:{settings.port}")
    logger.info(f"   Docs: http://{settings.host}:{settings.port}/docs")
    logger.info("=" * 50)
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="VoyaAI",
        lifespan=lifespan,
        description="""
        🧭 **VoyaAI** - AI-powered Travel Planning Assistant
        
        An intelligent travel planning assistant that integrates multiple 
        information sources to generate comprehensive travel itineraries:
        
        - 📱 **Xiaohongshu** - Trending travel guides and tips
        - 🌤️ **Weather** - Real-time weather forecasts
        - 🗺️ **Amap** - Route planning and POI search
        
        ## Quick Start
        
        ```bash
        curl -X POST "http://localhost:8182/travel/plan" \\
             -H "Content-Type: application/json" \\
             -d '{"content": "帮我规划日本大阪5天游"}'
        ```
        
        Or use the simple GET endpoint:
        
        ```bash
        curl "http://localhost:8182/travel/chat?content=日本大阪5天游攻略"
        ```
        """,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(router)
    
    # Mount static files
    if Path("static").exists():
        app.mount("/static", StaticFiles(directory="static"), name="static")

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info",
    )
