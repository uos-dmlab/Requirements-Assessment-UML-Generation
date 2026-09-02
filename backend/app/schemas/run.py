"""Pydantic schemas for Runs API."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field



class RunCreate(BaseModel):
    """Request body for creating a run."""
    requirements_text: str = ""
    diagram_type: str = "class"
    detail_level: str = "domain"


class RunUpdate(BaseModel):
    """Request body for updating run requirements."""
    requirements_text: str = Field(..., min_length=1)



class DiagramArtifact(BaseModel):
    """Artifact reference for download."""
    id: str
    kind: str
    content_type: str


class DiagramOut(BaseModel):
    """Diagram section of run response."""
    available: bool = False
    plantuml_source: Optional[str] = None
    preview_artifact_id: Optional[str] = None
    download_artifacts: List[DiagramArtifact] = []


class RunOut(BaseModel):
    """Run response."""
    id: str
    project_id: str

    # Diagram type and detail level
    diagram_type: str = "class"
    detail_level: str = "domain"

    # Requirements
    requirements_text: str = ""
    requirements_updated_at: Optional[datetime] = None

    # Validation
    validation_status: Optional[str] = None
    validation_score: Optional[int] = None
    validated_at: Optional[datetime] = None

    # Generation
    generation_status: Optional[str] = None
    generated_at: Optional[datetime] = None

    # Diagram info (computed from diagram_data + artifacts)
    diagram: Optional[DiagramOut] = None

    # Performance metrics
    validation_time_ms: Optional[int] = None
    generation_time_ms: Optional[int] = None
    refine_iterations: Optional[int] = None
    syntax_valid: Optional[bool] = None
    llm_calls_count: Optional[int] = None
    tokens_used: Optional[int] = None

    # Metadata
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_prefix(cls, run, artifacts=None) -> "RunOut":
        """Create from ORM model with prefixed IDs."""
        # Build diagram info
        diagram = DiagramOut(available=False)
        if run.diagram_data:
            diagram.available = True
            diagram.plantuml_source = run.diagram_data.get("plantuml_source")

            if artifacts:
                download_arts = []
                for art in artifacts:
                    download_arts.append(DiagramArtifact(
                        id=f"art_{art.id}",
                        kind=art.kind,
                        content_type=art.content_type
                    ))
                    if art.kind == "uml_png":
                        diagram.preview_artifact_id = f"art_{art.id}"
                diagram.download_artifacts = download_arts

        return cls(
            id=f"run_{run.id}",
            project_id=f"prj_{run.project_id}",
            diagram_type=run.diagram_type or "class",
            detail_level=run.detail_level or "domain",
            requirements_text=run.requirements_text or "",
            requirements_updated_at=run.requirements_updated_at,
            validation_status=run.validation_status,
            validation_score=run.validation_score,
            validated_at=run.validated_at,
            generation_status=run.generation_status,
            generated_at=run.generated_at,
            diagram=diagram,
            validation_time_ms=run.validation_time_ms,
            generation_time_ms=run.generation_time_ms,
            refine_iterations=run.refine_iterations,
            syntax_valid=run.syntax_valid,
            llm_calls_count=run.llm_calls_count,
            tokens_used=run.tokens_used,
            created_at=run.created_at,
            updated_at=run.updated_at,
        )


class RunListResponse(BaseModel):
    """Paginated list of runs."""
    items: List[RunOut]
    next_cursor: Optional[str] = None



class MetricOut(BaseModel):
    """Single metric in validation result."""
    name: str
    label: str
    score: float
    max_score: float = 10.0
    source: str = ""
    description: str = ""


class IssueOut(BaseModel):
    """Single issue from validation."""
    layer: str = ""
    category: str
    severity: str
    message: str
    sentence_index: int = -1
    sentence_text: str = ""
    suggestion: str = ""


class ValidationResultOut(BaseModel):
    """Validation section of run result."""
    score: Optional[int] = None
    metrics: List[MetricOut] = []
    issues: List[IssueOut] = []
    feedback: str = ""
    can_generate: bool = False
    readability_grade: float = 0
    total_sentences: int = 0
    total_words: int = 0


class PerformanceMetrics(BaseModel):
    """Performance metrics section of run result."""
    validation_time_ms: Optional[int] = None
    generation_time_ms: Optional[int] = None
    total_time_ms: Optional[int] = None
    refine_iterations: int = 0
    syntax_valid: Optional[bool] = None
    llm_calls_count: Optional[int] = None
    tokens_used: Optional[int] = None


class RunResultOut(BaseModel):
    """Full run result response."""
    run_id: str
    project_id: str
    validation: Optional[ValidationResultOut] = None
    diagram: Optional[DiagramOut] = None
    performance: Optional[PerformanceMetrics] = None
