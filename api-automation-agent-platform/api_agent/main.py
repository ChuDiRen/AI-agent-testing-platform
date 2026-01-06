"""
API Automation Agent Platform - Main Application

This is the main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api_agent import settings
from api_agent.db import init_db

# Import routers
from api_agent.api.routes import (
    tasks_router,
    documents_router,
    executions_router,
    agents_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting API Automation Agent Platform...")
    init_db()
    print("Database initialized")
    yield
    # Shutdown
    print("Shutting down API Automation Agent Platform...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-driven API automation testing platform with multi-agent orchestration",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to API Automation Agent Platform",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(tasks_router)
app.include_router(documents_router)
app.include_router(executions_router)
app.include_router(agents_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_agent.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
