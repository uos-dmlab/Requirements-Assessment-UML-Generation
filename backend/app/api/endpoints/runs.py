"""Runs API endpoints — iterative workspace for requirements."""

import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.user import User
from app.core.security import get_current_user
from app.core.error_handlers import AuthHTTPException
from app.schemas.errors import ProjectErrorCodes, RunErrorCodes
from app.schemas.run import (
    RunCreate,
    RunUpdate,
    RunOut,
    RunListResponse,
    RunResultOut,
    ValidationResultOut,
    MetricOut,
    IssueOut,
    DiagramOut,
    DiagramArtifact,
    PerformanceMetrics,
)
from app.crud import crud_project, crud_run
from app.services.run_service import start_validation, start_generation


router = APIRouter()


def parse_project_id(project_id: str) -> int:
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


def parse_run_id(run_id: str) -> int:
    if run_id.startswith("run_"):
        run_id = run_id[4:]
    try:
        return int(run_id)
    except ValueError:
        raise AuthHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=RunErrorCodes.RUN_NOT_FOUND,
            message="Invalid run ID format"
        )



@router.get(
    "/projects/{project_id}/runs",
    response_model=RunListResponse,
    summary="List runs",
)
async def list_runs(
    project_id: str,
    limit: int = Query(50, ge=1, le=100),
    cursor: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pid = parse_project_id(project_id)
    project = await crud_project.get_project_by_id(db, pid, current_user.id)
    if not project:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ProjectErrorCodes.PROJECT_NOT_FOUND,
            message="Project not found"
        )

    cursor_int = None
    if cursor:
        try:
            cursor_int = int(cursor)
        except ValueError:
            pass

    runs, next_cursor = await crud_run.list_runs(
        db, project_id=pid, user_id=current_user.id,
        limit=limit, cursor=cursor_int
    )

    return RunListResponse(
        items=[RunOut.from_orm_with_prefix(run) for run in runs],
        next_cursor=str(next_cursor) if next_cursor else None
    )


@router.post(
    "/projects/{project_id}/runs",
    response_model=RunOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create run",
)
async def create_run(
    project_id: str,
    run_in: RunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pid = parse_project_id(project_id)
    project = await crud_project.get_project_by_id(db, pid, current_user.id)
    if not project:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ProjectErrorCodes.PROJECT_NOT_FOUND,
            message="Project not found"
        )

    run = await crud_run.create_run(
        db, project_id=pid, user_id=current_user.id,
        requirements_text=run_in.requirements_text,
        diagram_type=run_in.diagram_type,
        detail_level=run_in.detail_level
    )
    return RunOut.from_orm_with_prefix(run)



@router.get(
    "/runs/{run_id}",
    response_model=RunOut,
    summary="Get run",
)
async def get_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rid = parse_run_id(run_id)
    run = await crud_run.get_run_with_artifacts(db, rid, current_user.id)
    if not run:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=RunErrorCodes.RUN_NOT_FOUND,
            message="Run not found"
        )
    return RunOut.from_orm_with_prefix(run, artifacts=run.artifacts)


@router.patch(
    "/runs/{run_id}",
    response_model=RunOut,
    summary="Update requirements",
)
async def update_run(
    run_id: str,
    run_in: RunUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rid = parse_run_id(run_id)
    run = await crud_run.get_run_by_id(db, rid, current_user.id)
    if not run:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=RunErrorCodes.RUN_NOT_FOUND,
            message="Run not found"
        )

    # Can't update while validation or generation is running
    if run.validation_status == "running" or run.generation_status == "running":
        raise AuthHTTPException(
            status_code=status.HTTP_409_CONFLICT,
            code=RunErrorCodes.RUN_NOT_FINISHED,
            message="Cannot update requirements while processing is running"
        )

    run = await crud_run.update_requirements(db, run, run_in.requirements_text)
    return RunOut.from_orm_with_prefix(run)


@router.delete(
    "/runs/{run_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete run",
)
async def delete_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rid = parse_run_id(run_id)
    run = await crud_run.get_run_by_id(db, rid, current_user.id)
    if not run:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=RunErrorCodes.RUN_NOT_FOUND,
            message="Run not found"
        )
    await crud_run.delete_run(db, run)
    return None



@router.post(
    "/runs/{run_id}/validate",
    response_model=RunOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start validation",
)
async def validate_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rid = parse_run_id(run_id)
    run = await crud_run.get_run_by_id(db, rid, current_user.id)
    if not run:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=RunErrorCodes.RUN_NOT_FOUND,
            message="Run not found"
        )

    if not run.requirements_text or not run.requirements_text.strip():
        raise AuthHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=RunErrorCodes.INVALID_RUN_KIND,
            message="Requirements text is empty"
        )

    if run.validation_status == "running":
        raise AuthHTTPException(
            status_code=status.HTTP_409_CONFLICT,
            code=RunErrorCodes.RUN_NOT_FINISHED,
            message="Validation is already running"
        )

    # Set status to running
    run = await crud_run.set_validation_status(db, run, "running")

    # Start background processing
    await start_validation(run.id, current_user.id)

    return RunOut.from_orm_with_prefix(run)


@router.post(
    "/runs/{run_id}/generate",
    response_model=RunOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start generation",
)
async def generate_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rid = parse_run_id(run_id)
    run = await crud_run.get_run_by_id(db, rid, current_user.id)
    if not run:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=RunErrorCodes.RUN_NOT_FOUND,
            message="Run not found"
        )

    # Must validate first
    if run.validation_status != "succeeded":
        raise AuthHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=RunErrorCodes.INVALID_RUN_KIND,
            message="Validate first before generating"
        )

    if run.generation_status == "running":
        raise AuthHTTPException(
            status_code=status.HTTP_409_CONFLICT,
            code=RunErrorCodes.RUN_NOT_FINISHED,
            message="Generation is already running"
        )

    # Set status to running
    run = await crud_run.set_generation_status(db, run, "running")

    # Start background processing
    await start_generation(run.id, current_user.id)

    return RunOut.from_orm_with_prefix(run)



@router.get(
    "/runs/{run_id}/result",
    response_model=RunResultOut,
    summary="Get run result",
)
async def get_run_result(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rid = parse_run_id(run_id)
    run = await crud_run.get_run_with_artifacts(db, rid, current_user.id)
    if not run:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=RunErrorCodes.RUN_NOT_FOUND,
            message="Run not found"
        )

    # Build validation result
    validation = None
    if run.validation_result:
        vr = run.validation_result
        validation = ValidationResultOut(
            score=run.validation_score,
            metrics=[MetricOut(**m) for m in vr.get("metrics", [])],
            issues=[IssueOut(**i) for i in vr.get("issues", [])],
            feedback=vr.get("feedback", ""),
            can_generate=run.validation_status == "succeeded",
            readability_grade=vr.get("readability_grade", 0),
            total_sentences=vr.get("total_sentences", 0),
            total_words=vr.get("total_words", 0),
        )

    # Build diagram result
    diagram = None
    if run.diagram_data:
        diagram = DiagramOut(
            available=True,
            plantuml_source=run.diagram_data.get("plantuml_source"),
        )
        if run.artifacts:
            download_arts = []
            for art in run.artifacts:
                download_arts.append(DiagramArtifact(
                    id=f"art_{art.id}",
                    kind=art.kind,
                    content_type=art.content_type
                ))
                if art.kind == "uml_png":
                    diagram.preview_artifact_id = f"art_{art.id}"
            diagram.download_artifacts = download_arts

    # Build performance metrics
    performance = None
    v_time = run.validation_time_ms
    g_time = run.generation_time_ms
    if v_time is not None or g_time is not None:
        total_time = None
        if v_time is not None and g_time is not None:
            total_time = v_time + g_time
        elif v_time is not None:
            total_time = v_time
        elif g_time is not None:
            total_time = g_time
        performance = PerformanceMetrics(
            validation_time_ms=v_time,
            generation_time_ms=g_time,
            total_time_ms=total_time,
            refine_iterations=run.refine_iterations or 0,
            syntax_valid=run.syntax_valid,
            llm_calls_count=run.llm_calls_count,
            tokens_used=run.tokens_used,
        )

    return RunResultOut(
        run_id=f"run_{run.id}",
        project_id=f"prj_{run.project_id}",
        validation=validation,
        diagram=diagram,
        performance=performance,
    )
