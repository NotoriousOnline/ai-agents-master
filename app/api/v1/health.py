"""Health check and version endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Liveness/readiness probe."""
    return {"status": "ok"}


@router.get("/version")
async def version() -> dict[str, str]:
    """API version (for deployments and clients)."""
    return {"version": "0.1.0"}
