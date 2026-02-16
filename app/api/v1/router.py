"""Aggregates all v1 API routes."""

from fastapi import APIRouter

from app.api.v1 import health
from app.agents.example.router import router as example_agent_router

api_router = APIRouter()

# Core
api_router.include_router(health.router, prefix="", tags=["health"])

# Agents (mount each agent under /agents/<name>)
api_router.include_router(
    example_agent_router,
    prefix="/agents/example",
    tags=["agents"],
)
