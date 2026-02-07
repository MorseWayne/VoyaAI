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
from fastapi.responses import FileResponse
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
    
    # Include API routes
    app.include_router(router)

    # SPA catch-all: serve static files or fall back to index.html
    static_dir = Path("static")
    index_file = static_dir / "index.html"

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Serve static files; fall back to index.html for SPA client-side routing."""
        if full_path:
            file_path = (static_dir / full_path).resolve()
            # Security: ensure the resolved path stays within static/
            if file_path.is_file() and str(file_path).startswith(str(static_dir.resolve())):
                return FileResponse(file_path)
        return FileResponse(index_file)

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
