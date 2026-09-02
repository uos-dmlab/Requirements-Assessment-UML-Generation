"""Generation API endpoint."""

from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.generation import GenerateRequest, GenerateResponse
from app.services.generation.generation_service import GenerationService
from app.db.models.user import User
from app.core.security import get_current_user


router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate_diagram(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate UML class diagram from requirements.

    Pipeline (10-30 seconds):
    1. Entity Registry Extraction — identify classes, attributes, relationships
    2. RAG Generation — search PlantUML docs + generate code
    3. Syntax Validation — plantuml.jar -syntax
    4. SELF-REFINE — fix errors (up to 4 iterations)
    5. Render PNG — plantuml.jar → base64

    Prerequisites:
    - Call /validate first and ensure can_generate=true
    - Vector Store must be configured with PlantUML documentation

    Returns:
    - plantuml_code: The generated PlantUML source
    - diagram_image_base64: PNG image encoded in base64
    - syntax_valid: Whether the code passed syntax check
    - entities/relationships: Extracted model elements
    - refine_iterations: How many SELF-REFINE cycles were needed
    """
    service = GenerationService()

    try:
        result = await service.generate(
            requirements=request.requirements,
            skip_validation=request.skip_validation
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )
