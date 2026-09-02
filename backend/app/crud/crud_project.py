"""CRUD operations for Projects."""

from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from app.db.models.project import Project
from app.db.models.requirements_draft import RequirementsDraft
from app.db.models.run import Run
from app.schemas.project import ProjectCreate, ProjectUpdate


async def get_project_by_id(
    db: AsyncSession,
    project_id: int,
    user_id: int
) -> Optional[Project]:
    """Get a project by ID if owned by user."""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id, Project.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_project_with_stats(
    db: AsyncSession,
    project_id: int,
    user_id: int
) -> Optional[Tuple[Project, int, Optional[Run]]]:
    """Get project with runs count and latest run."""
    project = await get_project_by_id(db, project_id, user_id)
    if not project:
        return None

    # Get runs count
    count_result = await db.execute(
        select(func.count(Run.id)).where(Run.project_id == project_id)
    )
    runs_count = count_result.scalar() or 0

    # Get latest run
    latest_run_result = await db.execute(
        select(Run)
        .where(Run.project_id == project_id)
        .order_by(Run.created_at.desc())
        .limit(1)
    )
    latest_run = latest_run_result.scalar_one_or_none()

    return project, runs_count, latest_run


async def list_projects(
    db: AsyncSession,
    user_id: int,
    limit: int = 50,
    cursor: Optional[int] = None,
    query: Optional[str] = None,
    status: Optional[str] = None
) -> Tuple[List[Tuple[Project, int, Optional[Run]]], Optional[int]]:
    """List projects with stats for a user."""
    stmt = select(Project).where(Project.user_id == user_id)

    if query:
        stmt = stmt.where(Project.name.ilike(f"%{query}%"))
    if status:
        stmt = stmt.where(Project.status == status)
    if cursor:
        stmt = stmt.where(Project.id < cursor)

    stmt = stmt.order_by(Project.updated_at.desc()).limit(limit + 1)

    result = await db.execute(stmt)
    projects = list(result.scalars().all())

    # Check if there's a next page
    next_cursor = None
    if len(projects) > limit:
        projects = projects[:limit]
        next_cursor = projects[-1].id

    # Get stats for each project
    items = []
    for project in projects:
        # Runs count
        count_result = await db.execute(
            select(func.count(Run.id)).where(Run.project_id == project.id)
        )
        runs_count = count_result.scalar() or 0

        # Latest run
        latest_run_result = await db.execute(
            select(Run)
            .where(Run.project_id == project.id)
            .order_by(Run.created_at.desc())
            .limit(1)
        )
        latest_run = latest_run_result.scalar_one_or_none()

        items.append((project, runs_count, latest_run))

    return items, next_cursor


async def create_project(
    db: AsyncSession,
    user_id: int,
    project_in: ProjectCreate
) -> Project:
    """Create a new project with empty requirements draft."""
    project = Project(
        user_id=user_id,
        name=project_in.name,
        description=project_in.description
    )
    db.add(project)
    await db.flush()

    # Create empty requirements draft
    draft = RequirementsDraft(
        project_id=project.id,
        content="",
        version=1
    )
    db.add(draft)

    await db.commit()
    await db.refresh(project)
    return project


async def update_project(
    db: AsyncSession,
    project: Project,
    project_in: ProjectUpdate
) -> Project:
    """Update a project."""
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project: Project) -> None:
    """Delete a project and all related data."""
    await db.delete(project)
    await db.commit()



async def get_requirements_draft(
    db: AsyncSession,
    project_id: int
) -> Optional[RequirementsDraft]:
    """Get requirements draft for a project."""
    result = await db.execute(
        select(RequirementsDraft).where(RequirementsDraft.project_id == project_id)
    )
    return result.scalar_one_or_none()


async def update_requirements_draft(
    db: AsyncSession,
    draft: RequirementsDraft,
    content: str,
    expected_version: int
) -> Tuple[Optional[RequirementsDraft], bool]:
    """
    Update requirements draft with optimistic locking.

    Returns:
        Tuple of (updated_draft, success)
        If version conflict, returns (None, False)
    """
    if draft.version != expected_version:
        return None, False

    draft.content = content
    draft.version = draft.version + 1

    await db.commit()
    await db.refresh(draft)
    return draft, True
