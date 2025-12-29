"""Main FastAPI application with elite architecture."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import config
from app.core.logger import logger
from app.api.routes import router
from app.cache.lru_cache import cache

# Create FastAPI app
app = FastAPI(
    title="Blinds & Boundaries API",
    version="2.0.0",
    description="Elite-level virtual try-on API with optimized architecture"
)

# CORS middleware
# Get allowed origins from config or environment
allowed_origins = ["*"]  # Default: allow all (for development)
if config.FRONTEND_URL:
    # Production: use configured frontend URL
    allowed_origins = [
        config.FRONTEND_URL,
        "http://localhost:5173",  # Local development
        "http://localhost:3000",  # Alternative local port
    ]
    # Remove trailing slash if present
    allowed_origins = [origin.rstrip('/') for origin in allowed_origins]
    logger.info(f"CORS configured for frontend: {config.FRONTEND_URL}")
else:
    logger.warning("FRONTEND_URL not set - CORS allowing all origins (not recommended for production)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (optional, only if slowapi is available)
# Note: Rate limiting can be added per-route using @limiter.limit() decorator
# For now, Azure App Service provides built-in rate limiting and DDoS protection
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("Rate limiting enabled (slowapi)")
except ImportError:
    logger.info("Rate limiting library not installed - Azure App Service provides DDoS protection")
    limiter = None

# Include routers
app.include_router(router, tags=["api"], prefix="")  # Explicitly no prefix

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
    # List all registered routes for debugging
    routes = [r.path for r in app.routes if hasattr(r, 'path')]
    return {
        "message": "Blinds & Boundaries API - Elite Architecture",
        "version": "2.0.0",
        "status": "operational",
        "mode": "elite",
        "routes": routes,
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

