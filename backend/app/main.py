"""
Quant Trading System API
FastAPI entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import regime, models, screening, sector, reports, auth, data

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: DB Init on startup"""
    try:
        from app.db.init_db import init_db
        from app.db.base import SessionLocal
        db = SessionLocal()
        init_db(db)
        db.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed (non-critical if using external migration): {e}")
    yield

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Renaissance-style Quantitative Trading System for Thai SET100",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(
    regime.router, 
    prefix=f"{settings.api_prefix}/regime", 
    tags=["Regime"]
)
app.include_router(
    models.router, 
    prefix=f"{settings.api_prefix}/models", 
    tags=["Models"]
)
app.include_router(
    screening.router, 
    prefix=f"{settings.api_prefix}/screen", 
    tags=["Screening"]
)
app.include_router(
    sector.router,
    prefix=f"{settings.api_prefix}/sector",
    tags=["Sector Rotation"]
)
app.include_router(
    reports.router,
    prefix=f"{settings.api_prefix}/reports",
    tags=["Reports"]
)
app.include_router(
    auth.router,
    prefix=f"{settings.api_prefix}/auth",
    tags=["Authentication"]
)
app.include_router(
    data.router,
    prefix=f"{settings.api_prefix}/data",
    tags=["Market Data"]
)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
