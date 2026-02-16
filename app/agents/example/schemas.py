"""Pydantic schemas for the example agent."""

from pydantic import BaseModel, Field


class ExampleRequest(BaseModel):
    """Request to run the example agent."""

    query: str = Field(..., min_length=1, description="User query")


class ExampleResponse(BaseModel):
    """Response from the example agent."""

    agent_id: str = Field(..., description="Agent identifier")
    query: str = Field(..., description="User query")
    result: str = Field(..., description="Agent result")
    status: str = Field(default="success", description="Status")
