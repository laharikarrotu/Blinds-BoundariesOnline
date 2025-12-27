"""Main FastAPI application with elite architecture."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import config
from app.core.logger import logger
from app.api.routes import router

# Create FastAPI app
app = FastAPI(
    title="Blinds & Boundaries API",
    version="2.0.0",
    description="Elite-level virtual try-on API with optimized architecture"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, tags=["api"])

# Static file serving
for dir_name, mount_path in [
    (config.BLINDS_DIR, "/blinds"),
    (config.RESULTS_DIR, "/results")
]:
    dir_path = Path(dir_name)
    if dir_path.exists() and any(dir_path.iterdir()):
        app.mount(mount_path, StaticFiles(directory=dir_name), name=dir_name)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Blinds & Boundaries API - Elite Architecture",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "Optimized algorithms",
            "LRU caching",
            "Repository pattern",
            "Service layer",
            "Async processing"
        ]
    }


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("Starting elite architecture...")
    logger.info(f"Cache enabled: {config.ENABLE_CACHING}")
    logger.info(f"Async enabled: {config.ENABLE_ASYNC}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down...")
    cache.cleanup_expired()

