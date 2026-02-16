"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.db import router as db_router
from app.api.v1.router import api_router
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    yield
    # Add any cleanup (e.g. close pool) here if needed


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title="AI Agents Master API",
        description="Production-grade API for multiple AI agents",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(db_router, prefix="/db")
    # Root-level health/version for probes and simplicity
    from app.api.v1.health import health_check, version as version_endpoint
    app.get("/health")(health_check)
    app.get("/version")(version_endpoint)
    return app


app = create_application()
