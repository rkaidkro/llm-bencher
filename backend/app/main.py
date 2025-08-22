"""
Main FastAPI application for llm-bencher.

This module sets up the FastAPI application with all necessary middleware,
CORS configuration, and route registration.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import structlog
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from .utils.config import get_settings, is_development, is_debug
from .models.database import init_db, close_db, get_db
from .services.llm_service import LLMService, LLMServiceError

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Get logger
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting llm-bencher")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down llm-bencher")
    try:
        close_db()
        logger.info("Database closed successfully")
    except Exception as e:
        logger.error(f"Failed to close database: {e}")


# Create FastAPI application
app = FastAPI(
    title="llm-bencher",
    description="A comprehensive interface for testing and benchmarking LLM models",
    version="1.0.0",
    docs_url="/docs" if is_development() else None,
    redoc_url="/redoc" if is_development() else None,
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.exception_handler(LLMServiceError)
async def llm_service_exception_handler(request, exc: LLMServiceError):
    """Handle LLM service errors."""
    logger.error(f"LLM service error: {exc}")
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc), "type": "llm_service_error"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "internal_error"}
    )


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "llm-bencher API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if is_development() else None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": structlog.processors.TimeStamper(fmt="iso")(),
        "environment": settings.environment,
        "debug": is_debug()
    }


@app.get("/health/llm")
async def llm_health_check():
    """Check health of all configured LLM services."""
    services = ["ollama", "lm_studio"]
    results = {}
    
    async with LLMService() as llm_service:
        for service in services:
            try:
                health = await llm_service.check_service_health(service)
                results[service] = health
            except Exception as e:
                logger.error(f"Health check failed for {service}: {e}")
                results[service] = {
                    "status": "error",
                    "error": str(e),
                    "response_time_ms": 0
                }
    
    return {
        "services": results,
        "timestamp": structlog.processors.TimeStamper(fmt="iso")()
    }


@app.get("/api/v1/models")
async def get_models():
    """Get available models from all services."""
    services = ["ollama", "lm_studio"]
    models = {}
    
    async with LLMService() as llm_service:
        for service in services:
            try:
                service_models = await llm_service.get_available_models(service)
                models[service] = service_models
            except Exception as e:
                logger.error(f"Failed to get models for {service}: {e}")
                models[service] = []
    
    return {"models": models}


# Import and include routers
from .routers import llm, conversations, monitoring

app.include_router(llm.router, prefix="/api/v1/llm", tags=["LLM"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["Conversations"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=is_development(),
        log_level=settings.log_level.lower()
    )
