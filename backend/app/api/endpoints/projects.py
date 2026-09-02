"""Projects API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.user import User
from app.core.security import get_current_user
from app.core.error_handlers import AuthHTTPException
from app.schemas.errors import ProjectErrorCodes
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectOut,
    ProjectListResponse,
    RequirementsDraftOut,
    RequirementsDraftUpdate,
    Score,
)
from app.crud import crud_project


router = APIRouter()


def parse_project_id(project_id: str) -> int:
    """Parse project ID from prefixed string."""
    if project_id.startswith("prj_"):
        project_id = project_id[4:]
    try:
        return int(project_id)
    except ValueError:
        raise AuthHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ProjectErrorCodes.PROJECT_NOT_FOUND,
            message="Invalid project ID format"
        )



@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List projects",
    description="Get paginated list of projects for current user.",
)
async def list_projects(
    limit: int = Query(50, ge=1, le=100),
    cursor: Optional[str] = None,
    q: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all projects for the current user."""
    cursor_int = None
    if cursor:
        try:
            cursor_int = int(cursor)
        except ValueError:
            pass

    items, next_cursor = await crud_project.list_projects(
        db,
        user_id=current_user.id,
        limit=limit,
        cursor=cursor_int,
        query=q,
        status=status_filter
    )

    project_list = []
    for project, runs_count, latest_run in items:
        latest_score = None
        latest_run_id = None
        if latest_run and latest_run.validation_score is not None:
            latest_score = Score(value=latest_run.validation_score, max=100)
            latest_run_id = latest_run.id

        project_list.append(
            ProjectOut.from_orm_with_computed(
                project,
                runs_count=runs_count,
                latest_score=latest_score,
                latest_run_id=latest_run_id
            )
        )

    return ProjectListResponse(
        items=project_list,
        next_cursor=str(next_cursor) if next_cursor else None
    )


@router.post(
    "",
    response_model=ProjectOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
    description="Create a new project.",
)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new project."""
    project = await crud_project.create_project(db, current_user.id, project_in)
    return ProjectOut.from_orm_with_computed(project, runs_count=0)


@router.get(
    "/{project_id}",
    response_model=ProjectOut,
    summary="Get project",
    description="Get a project by ID.",
)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a project by ID."""
    pid = parse_project_id(project_id)
    result = await crud_project.get_project_with_stats(db, pid, current_user.id)

    if not result:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ProjectErrorCodes.PROJECT_NOT_FOUND,
            message="Project not found"
        )

    project, runs_count, latest_run = result
    latest_score = None
    latest_run_id = None
    if latest_run and latest_run.score_value is not None:
        latest_score = Score(value=latest_run.score_value, max=latest_run.score_max or 60)
        latest_run_id = latest_run.id

    return ProjectOut.from_orm_with_computed(
        project,
        runs_count=runs_count,
        latest_score=latest_score,
        latest_run_id=latest_run_id
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectOut,
    summary="Update project",
    description="Update a project's name, description, or status.",
)
async def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a project."""
    pid = parse_project_id(project_id)
    project = await crud_project.get_project_by_id(db, pid, current_user.id)

    if not project:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ProjectErrorCodes.PROJECT_NOT_FOUND,
            message="Project not found"
        )

    project = await crud_project.update_project(db, project, project_in)
    result = await crud_project.get_project_with_stats(db, pid, current_user.id)
    project, runs_count, latest_run = result

    latest_score = None
    latest_run_id = None
    if latest_run and latest_run.score_value is not None:
        latest_score = Score(value=latest_run.score_value, max=latest_run.score_max or 60)
        latest_run_id = latest_run.id

    return ProjectOut.from_orm_with_computed(
        project,
        runs_count=runs_count,
        latest_score=latest_score,
        latest_run_id=latest_run_id
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Delete a project and all its data.",
)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a project."""
    pid = parse_project_id(project_id)
    project = await crud_project.get_project_by_id(db, pid, current_user.id)

    if not project:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ProjectErrorCodes.PROJECT_NOT_FOUND,
            message="Project not found"
        )

    await crud_project.delete_project(db, project)
    return None



@router.get(
    "/{project_id}/requirements",
    response_model=RequirementsDraftOut,
    summary="Get requirements draft",
    description="Get the current requirements draft for a project.",
)
async def get_requirements(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get requirements draft for a project."""
    pid = parse_project_id(project_id)
    project = await crud_project.get_project_by_id(db, pid, current_user.id)

    if not project:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ProjectErrorCodes.PROJECT_NOT_FOUND,
            message="Project not found"
        )

    draft = await crud_project.get_requirements_draft(db, pid)
    if not draft:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ProjectErrorCodes.PROJECT_NOT_FOUND,
            message="Requirements draft not found"
        )

    return RequirementsDraftOut.from_orm_with_prefix(draft)


@router.put(
    "/{project_id}/requirements",
    response_model=RequirementsDraftOut,
    summary="Update requirements draft",
    description="Update requirements draft with optimistic locking.",
)
async def update_requirements(
    project_id: str,
    update_in: RequirementsDraftUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update requirements draft."""
    pid = parse_project_id(project_id)
    project = await crud_project.get_project_by_id(db, pid, current_user.id)

    if not project:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ProjectErrorCodes.PROJECT_NOT_FOUND,
            message="Project not found"
        )

    draft = await crud_project.get_requirements_draft(db, pid)
    if not draft:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ProjectErrorCodes.PROJECT_NOT_FOUND,
            message="Requirements draft not found"
        )

    updated_draft, success = await crud_project.update_requirements_draft(
        db, draft, update_in.content, update_in.expected_version
    )

    if not success:
        raise AuthHTTPException(
            status_code=status.HTTP_409_CONFLICT,
            code=ProjectErrorCodes.REQUIREMENTS_VERSION_CONFLICT,
            message=f"Version conflict: expected {update_in.expected_version}, current is {draft.version}"
        )

    return RequirementsDraftOut.from_orm_with_prefix(updated_draft)
