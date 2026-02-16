"""Example agent HTTP API."""

from fastapi import APIRouter

from app.agents.example.schemas import ExampleRequest, ExampleResponse
from app.agents.example.service import run_example_agent

router = APIRouter()


@router.post("/run", response_model=ExampleResponse)
async def run_agent(body: ExampleRequest) -> ExampleResponse:
    """Run the example agent with the given query."""
    return await run_example_agent(query=body.query)
