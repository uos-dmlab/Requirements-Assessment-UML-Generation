"""CRUD operations for Runs."""

from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models.run import Run
from app.db.models.artifact import Artifact



async def get_run_by_id(
    db: AsyncSession,
    run_id: int,
    user_id: int
) -> Optional[Run]:
    """Get a run by ID if owned by user."""
    result = await db.execute(
        select(Run).where(Run.id == run_id, Run.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_run_with_artifacts(
    db: AsyncSession,
    run_id: int,
    user_id: int
) -> Optional[Run]:
    """Get run with artifacts loaded."""
    result = await db.execute(
        select(Run)
        .options(selectinload(Run.artifacts))
        .where(Run.id == run_id, Run.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def list_runs(
    db: AsyncSession,
    project_id: int,
    user_id: int,
    limit: int = 50,
    cursor: Optional[int] = None
) -> Tuple[List[Run], Optional[int]]:
    """List runs for a project."""
    stmt = (
        select(Run)
        .where(Run.project_id == project_id, Run.user_id == user_id)
    )

    if cursor:
        stmt = stmt.where(Run.id < cursor)

    stmt = stmt.order_by(Run.created_at.desc()).limit(limit + 1)

    result = await db.execute(stmt)
    runs = list(result.scalars().all())

    next_cursor = None
    if len(runs) > limit:
        runs = runs[:limit]
        next_cursor = runs[-1].id

    return runs, next_cursor


async def create_run(
    db: AsyncSession,
    project_id: int,
    user_id: int,
    requirements_text: str = "",
    diagram_type: str = "class",
    detail_level: str = "domain"
) -> Run:
    """Create a new run."""
    now = datetime.now(timezone.utc)
    run = Run(
        project_id=project_id,
        user_id=user_id,
        requirements_text=requirements_text,
        requirements_updated_at=now if requirements_text else None,
        diagram_type=diagram_type,
        detail_level=detail_level,
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


async def update_requirements(
    db: AsyncSession,
    run: Run,
    requirements_text: str
) -> Run:
    """Update requirements and reset validation/generation results."""
    now = datetime.now(timezone.utc)
    run.requirements_text = requirements_text
    run.requirements_updated_at = now

    # Reset validation
    run.validation_status = None
    run.validation_score = None
    run.validation_result = None
    run.validated_at = None

    # Reset generation
    run.generation_status = None
    run.diagram_data = None
    run.generated_at = None

    # Reset performance metrics
    run.validation_time_ms = None
    run.generation_time_ms = None
    run.refine_iterations = None
    run.syntax_valid = None
    run.llm_calls_count = None
    run.tokens_used = None

    run.updated_at = now

    # Delete old artifacts
    for artifact in await get_artifacts_for_run(db, run.id):
        await db.delete(artifact)

    await db.commit()
    await db.refresh(run)
    return run


async def set_validation_status(
    db: AsyncSession,
    run: Run,
    status: str,
    score: Optional[int] = None,
    result: Optional[dict] = None
) -> Run:
    """Update validation status."""
    run.validation_status = status
    if score is not None:
        run.validation_score = score
    if result is not None:
        run.validation_result = result
    if status == "succeeded":
        run.validated_at = datetime.now(timezone.utc)
    run.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(run)
    return run


async def set_generation_status(
    db: AsyncSession,
    run: Run,
    status: str,
    diagram_data: Optional[dict] = None
) -> Run:
    """Update generation status."""
    run.generation_status = status
    if diagram_data is not None:
        run.diagram_data = diagram_data
    if status == "succeeded":
        run.generated_at = datetime.now(timezone.utc)
    run.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(run)
    return run


async def delete_run(db: AsyncSession, run: Run) -> None:
    """Delete a run and all its artifacts."""
    await db.delete(run)
    await db.commit()



async def create_artifact(
    db: AsyncSession,
    run_id: int,
    project_id: int,
    user_id: int,
    kind: str,
    content_type: str,
    data: bytes,
    filename: Optional[str] = None
) -> Artifact:
    """Create an artifact."""
    artifact = Artifact(
        run_id=run_id,
        project_id=project_id,
        user_id=user_id,
        kind=kind,
        content_type=content_type,
        data=data,
        filename=filename
    )
    db.add(artifact)
    await db.commit()
    await db.refresh(artifact)
    return artifact


async def get_artifact_by_id(
    db: AsyncSession,
    artifact_id: int,
    user_id: int
) -> Optional[Artifact]:
    """Get artifact by ID if owned by user."""
    result = await db.execute(
        select(Artifact).where(Artifact.id == artifact_id, Artifact.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_artifacts_for_run(
    db: AsyncSession,
    run_id: int
) -> List[Artifact]:
    """Get all artifacts for a run."""
    result = await db.execute(
        select(Artifact).where(Artifact.run_id == run_id)
    )
    return list(result.scalars().all())
