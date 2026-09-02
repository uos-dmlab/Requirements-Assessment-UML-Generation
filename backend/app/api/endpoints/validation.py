"""Validation API endpoint."""

from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.validation import (
    ValidateRequest, ValidateResponse,
    MetricScoreSchema, IssueSchema
)
from app.services.validation.validation_service import ValidationService
from app.db.models.user import User
from app.core.security import get_current_user


router = APIRouter()


@router.post("/validate", response_model=ValidateResponse)
async def validate_requirements(
    request: ValidateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    3-layer hybrid validation:
    - Layer 1: Lexical (dictionaries) — instant
    - Layer 2: Structural (spaCy) — ~100ms
    - Layer 3: Semantic (OpenAI) — ~3 sec

    Returns:
    - 8 metrics with scores 0-10
    - deterministic_score (L1+L2, weighted 60%)
    - semantic_score (L3, weighted 40%)
    - total_score (0-100)
    - can_generate: True if requirements pass quality gate
    - issues: sorted by severity (errors → warnings → info)
    """
    service = ValidationService()

    try:
        result = await service.validate(request.requirements)

        return ValidateResponse(
            metrics=[
                MetricScoreSchema(
                    name=m.name,
                    label=m.label,
                    score=m.score,
                    max_score=m.max_score,
                    source=m.source,
                    description=m.description
                ) for m in result.metrics
            ],
            deterministic_score=result.deterministic_score,
            semantic_score=result.semantic_score,
            total_score=result.total_score,
            can_generate=result.can_generate,
            issues=[
                IssueSchema(
                    layer=i.layer,
                    category=i.category,
                    severity=i.severity,
                    message=i.message,
                    sentence_index=i.sentence_index,
                    sentence_text=i.sentence_text,
                    suggestion=i.suggestion
                ) for i in result.issues
            ],
            detected_entities=result.detected_entities,
            detected_relationships=result.detected_relationships,
            feedback=result.feedback,
            readability_grade=result.readability_grade,
            total_sentences=result.total_sentences,
            total_words=result.total_words,
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
