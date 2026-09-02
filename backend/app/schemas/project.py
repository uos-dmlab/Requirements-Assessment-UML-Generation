"""Pydantic schemas for Projects API."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field



class Score(BaseModel):
    """Quality score with value and max."""
    value: int
    max: int = 60



class ProjectCreate(BaseModel):
    """Request body for creating a project."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Request body for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|in_progress|completed|archived)$")


class ProjectOut(BaseModel):
    """Project response with computed fields."""
    id: str
    name: str
    description: Optional[str] = None
    status: str
    runs_count: int = 0
    latest_score: Optional[Score] = None
    latest_run_id: Optional[str] = None
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_computed(
        cls,
        project,
        runs_count: int = 0,
        latest_score: Optional[Score] = None,
        latest_run_id: Optional[int] = None
    ) -> "ProjectOut":
        """Create ProjectOut from ORM model with computed fields."""
        return cls(
            id=f"prj_{project.id}",
            name=project.name,
            description=project.description,
            status=project.status,
            runs_count=runs_count,
            latest_score=latest_score,
            latest_run_id=f"run_{latest_run_id}" if latest_run_id else None,
            updated_at=project.updated_at,
            created_at=project.created_at
        )


class ProjectListResponse(BaseModel):
    """Paginated list of projects."""
    items: List[ProjectOut]
    next_cursor: Optional[str] = None



class RequirementsDraftOut(BaseModel):
    """Requirements draft response."""
    project_id: str
    content: str
    version: int
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_prefix(cls, draft) -> "RequirementsDraftOut":
        """Create from ORM model with prefixed project ID."""
        return cls(
            project_id=f"prj_{draft.project_id}",
            content=draft.content,
            version=draft.version,
            updated_at=draft.updated_at
        )


class RequirementsDraftUpdate(BaseModel):
    """Request body for updating requirements draft."""
    content: str
    expected_version: int = Field(..., ge=0)
