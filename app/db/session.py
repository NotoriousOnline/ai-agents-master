"""Async SQLAlchemy session factory. Engine is created lazily so the app starts without a running DB."""

import socket
import ssl

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine

from app.config import get_settings
from app.db.base import Base

_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None

# Prefer IPv4 for DB connections (avoids getaddrinfo failed on networks where IPv6 is broken)
_original_getaddrinfo = socket.getaddrinfo


def _getaddrinfo_ipv4_first(host, port, family=0, type=0, proto=0, flags=0):
    if family == 0:
        try:
            return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
        except OSError:
            pass
    return _original_getaddrinfo(host, port, family, type, proto, flags)


socket.getaddrinfo = _getaddrinfo_ipv4_first


def _ssl_context_no_verify() -> ssl.SSLContext:
    """SSL context for Supabase/remote Postgres that skips cert verification (avoids CERTIFICATE_VERIFY_FAILED)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def get_engine() -> AsyncEngine:
    """Create or return the async engine. Lazy so app starts even if Postgres is down."""
    global _engine
    if _engine is None:
        settings = get_settings()
        connect_args: dict = {}
        if settings.database_use_ssl:
            connect_args["ssl"] = _ssl_context_no_verify()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.app_debug,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args=connect_args,
        )
    return _engine


def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    """Create or return the async session maker. Depends on engine (lazy)."""
    global _session_maker
    if _session_maker is None:
        _session_maker = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _session_maker


def __getattr__(name: str):
    """Lazy attributes so 'from app.db.session import engine' and async_session_maker still work."""
    if name == "engine":
        return get_engine()
    if name == "async_session_maker":
        return get_async_session_maker()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


async def init_db() -> None:
    """Create tables (use Alembic in production)."""
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
