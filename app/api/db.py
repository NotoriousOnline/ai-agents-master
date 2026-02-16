"""Database connectivity check endpoint."""

from fastapi import APIRouter, HTTPException

from sqlalchemy import text

from app.db.session import engine

router = APIRouter(tags=["db"])


@router.get("/ping")
async def db_ping() -> dict[str, str]:
    """
    Lightweight DB connectivity check. Runs SELECT 1 against the resolved database.
    Use for readiness probes or to verify LOCAL_DB_URL / SUPABASE_DB_URL connectivity.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unreachable: {e!s}") from e
