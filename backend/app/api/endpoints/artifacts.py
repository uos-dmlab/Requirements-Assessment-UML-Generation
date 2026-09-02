"""Artifacts API endpoints."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.user import User
from app.core.security import get_current_user
from app.core.error_handlers import AuthHTTPException
from app.schemas.errors import ArtifactErrorCodes
from app.crud import crud_run


router = APIRouter()


def parse_artifact_id(artifact_id: str) -> int:
    """Parse artifact ID from prefixed string."""
    if artifact_id.startswith("art_"):
        artifact_id = artifact_id[4:]
    try:
        return int(artifact_id)
    except ValueError:
        raise AuthHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ArtifactErrorCodes.ARTIFACT_NOT_FOUND,
            message="Invalid artifact ID format"
        )


@router.get(
    "/{artifact_id}",
    summary="Download artifact",
    description="Download an artifact by ID.",
    responses={
        200: {
            "description": "Artifact content",
            "content": {
                "image/png": {},
                "image/svg+xml": {},
                "text/plain": {},
            }
        },
        404: {"description": "Artifact not found"},
    },
)
async def get_artifact(
    artifact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download an artifact."""
    aid = parse_artifact_id(artifact_id)
    artifact = await crud_run.get_artifact_by_id(db, aid, current_user.id)

    if not artifact:
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ArtifactErrorCodes.ARTIFACT_NOT_FOUND,
            message="Artifact not found"
        )

    # Get content
    content = artifact.data
    if not content and artifact.storage_path:
        # TODO: Load from external storage
        raise AuthHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ArtifactErrorCodes.ARTIFACT_NOT_FOUND,
            message="Artifact content not available"
        )

    # Set content disposition for download
    headers = {}
    if artifact.filename:
        headers["Content-Disposition"] = f'attachment; filename="{artifact.filename}"'

    return Response(
        content=content,
        media_type=artifact.content_type,
        headers=headers
    )
