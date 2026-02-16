"""Async SQLAlchemy session factory."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.db.base import Base

settings = get_settings()

# Supabase requires SSL; local Postgres typically does not
connect_args = {}
if settings.database_use_ssl:
    connect_args["ssl"] = True

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args=connect_args if connect_args else None,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Create tables (use Alembic in production)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
