"""Pydantic schemas for ablation study endpoint."""

from pydantic import BaseModel, Field


class AblationRequest(BaseModel):
    requirements: str = Field(..., min_length=10, max_length=50000)
    diagram_type: str = "class"  # "class" | "use_case"
    use_rag: bool = True


class AblationResponse(BaseModel):
    rag_enabled: bool
    plantuml_code: str
    diagram_image_base64: str | None = None
    latency_ms: int
