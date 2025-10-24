"""
Freelancer Feedback Assistant - Main Application Entry Point
FastAPI application with AI-powered feedback parsing
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.session import engine, Base

# Set up logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan events
    Handles startup and shutdown tasks
    """
    # Startup
    logger.info("Starting Freelancer Feedback Assistant API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Create database tables (in production, use Alembic migrations)
    if settings.DEBUG:
        # Note: Use Alembic migrations in production
        # Base.metadata.create_all(bind=engine)
        pass
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Freelancer Feedback Assistant API")
    engine.dispose()
    logger.info("Application shutdown complete")


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered tool to translate creative feedback into actionable tasks",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page", "X-Per-Page"],
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add trusted host middleware (production only)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Mount Prometheus metrics endpoint
if settings.METRICS_ENABLED:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    Root endpoint - API information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-powered feedback parsing for freelancers",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
        "health": "/health",
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint
    Returns the health status of the application
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
    }


# Database health check
@app.get("/health/db", tags=["Health"])
async def database_health_check() -> dict:
    """
    Database health check endpoint
    Verifies database connectivity
    """
    try:
        from sqlalchemy import text
        from app.db.session import SessionLocal
        
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
            },
        )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler
    Catches all unhandled exceptions and returns a JSON response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests
    """
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None,
        },
    )
    
    response = await call_next(request)
    
    logger.info(
        f"Response: {response.status_code}",
        extra={
            "status_code": response.status_code,
            "method": request.method,
            "path": request.url.path,
        },
    )
    
    return response


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
