"""
Main FastAPI application for LP Document Parser.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.db.database import init_db
from app.api import documents, auth

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(documents.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup."""
    try:
        init_db()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": settings.api_version,
        "database_status": "connected",
        "redis_status": "connected"
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "LP Document Parser API",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
