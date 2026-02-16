"""Example agent business logic. Replace with real agent calls (e.g. LLM, tools)."""

from app.agents.example.schemas import ExampleResponse


async def run_example_agent(query: str) -> ExampleResponse:
    """Run the example agent. Placeholder for actual agent logic."""
    # In production: call LLM, tools, Supabase, etc.
    return ExampleResponse(
        agent_id="example",
        query=query,
        result=f"Echo: {query}",
        status="success",
    )
