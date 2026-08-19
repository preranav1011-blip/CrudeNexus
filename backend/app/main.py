"""Main FastAPI application entrypoint"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.database.db import init_db
from app.routes import events, analysis, optimization, data

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s | %(levelname)-6s | %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered decision-intelligence platform for India's crude-oil supply chain",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database and log startup status"""
    try:
        init_db()
        logger.info(f"Database initialized: {settings.database_url}")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Log LLM status
    if settings.llm_enabled:
        try:
            import requests
            response = requests.get(f"{settings.llm_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"✓ LLM ENABLED: {settings.llm_model} ({settings.llm_base_url})")
            else:
                logger.warning(f"⚠ LLM service returned status {response.status_code}, using fallback")
        except Exception as e:
            logger.warning(f"⚠ LLM unavailable ({settings.llm_base_url}): {e}")
            logger.info("→ Using heuristic fallback for event extraction")
    else:
        logger.info("→ LLM disabled in config, using heuristic fallback")


# Register route modules
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(optimization.router, prefix="/api/optimization", tags=["Optimization"])
app.include_router(data.router, prefix="/api/data", tags=["Data"])


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
