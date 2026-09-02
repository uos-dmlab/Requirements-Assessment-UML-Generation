"""Pydantic schemas for generation endpoint."""

from pydantic import BaseModel, Field
from typing import List


class GenerateRequest(BaseModel):
    requirements: str = Field(..., min_length=10, max_length=50000)
    skip_validation: bool = False  # Usually False — check before generating


class GenerateResponse(BaseModel):
    # Main result
    plantuml_code: str
    diagram_image_base64: str  # PNG in base64

    # Validation
    syntax_valid: bool

    # Metadata
    entities_count: int
    relationships_count: int
    refine_iterations: int      # How many SELF-REFINE cycles
    generation_time_ms: int     # Total generation time

    # LLM usage metrics
    llm_calls_count: int = 0
    tokens_used: int = 0

    # Extracted entities (for display)
    entities: List[str] = []
    relationships: List[str] = []

    # Warnings (if any)
    warnings: List[str] = []
