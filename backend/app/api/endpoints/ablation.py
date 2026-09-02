"""Ablation study endpoint — generation with RAG toggled on/off."""

from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.ablation import AblationRequest, AblationResponse
from app.services.generation.generation_service import GenerationService
from app.db.models.user import User
from app.core.security import get_current_user


router = APIRouter()


@router.post("/ablation/generate", response_model=AblationResponse)
async def ablation_generate(
    request: AblationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate UML diagram with explicit RAG toggle for ablation study.

    Use `use_rag: true` for full RAG pipeline, `use_rag: false` to skip
    PlantUML documentation retrieval. Compare latency and output quality.
    """
    service = GenerationService()

    try:
        result = await service.generate(
            requirements=request.requirements,
            diagram_type=request.diagram_type,
            use_rag=request.use_rag,
        )
        return AblationResponse(
            rag_enabled=request.use_rag,
            plantuml_code=result.plantuml_code,
            diagram_image_base64=result.diagram_image_base64 or None,
            latency_ms=result.generation_time_ms,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ablation generation failed: {str(e)}",
        )
