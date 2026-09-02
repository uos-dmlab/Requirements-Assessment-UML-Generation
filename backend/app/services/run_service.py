"""Service for processing validation and generation in background."""

import logging
import asyncio
import base64
import time

from app.db.session import async_session
from app.crud import crud_run
from app.services.validation.validation_service import ValidationService
from app.services.generation.generation_service import GenerationService

logger = logging.getLogger(__name__)


async def process_validation(run_id: int, user_id: int) -> None:
    """Run validation in background with its own DB session."""
    async with async_session() as db:
        try:
            run = await crud_run.get_run_by_id(db, run_id, user_id)
            if not run:
                logger.error(f"Run {run_id} not found for validation")
                return

            requirements_text = run.requirements_text or ""
            if not requirements_text.strip():
                await crud_run.set_validation_status(db, run, "failed")
                return

            service = ValidationService()
            validation_start = time.perf_counter()
            result = await service.validate(requirements_text)
            validation_time_ms = int((time.perf_counter() - validation_start) * 1000)

            validation_result = {
                "metrics": [
                    {
                        "name": m.name,
                        "label": m.label,
                        "score": m.score,
                        "max_score": m.max_score,
                        "source": m.source,
                        "description": m.description,
                    }
                    for m in result.metrics
                ],
                "issues": [
                    {
                        "layer": i.layer,
                        "category": i.category,
                        "severity": i.severity,
                        "message": i.message,
                        "sentence_index": i.sentence_index,
                        "sentence_text": i.sentence_text,
                        "suggestion": i.suggestion,
                    }
                    for i in result.issues
                ],
                "feedback": result.feedback,
                "readability_grade": result.readability_grade,
                "total_sentences": result.total_sentences,
                "total_words": result.total_words,
                "deterministic_score": result.deterministic_score,
                "semantic_score": result.semantic_score,
                "can_generate": result.can_generate,
                "detected_entities": result.detected_entities,
                "detected_relationships": result.detected_relationships,
            }

            score = int(result.total_score)

            run.validation_time_ms = validation_time_ms

            await crud_run.set_validation_status(
                db, run, "succeeded",
                score=score,
                result=validation_result
            )

        except Exception as e:
            logger.exception(f"Validation failed for run {run_id}: {e}")
            try:
                run = await crud_run.get_run_by_id(db, run_id, user_id)
                if run:
                    await crud_run.set_validation_status(db, run, "failed")
            except Exception as inner_e:
                logger.error(f"Failed to set validation failed status: {inner_e}")


async def process_generation(run_id: int, user_id: int) -> None:
    """Run generation in background with its own DB session."""
    async with async_session() as db:
        try:
            run = await crud_run.get_run_by_id(db, run_id, user_id)
            if not run:
                logger.error(f"Run {run_id} not found for generation")
                return

            requirements_text = run.requirements_text or ""
            diagram_type = run.diagram_type or "class"
            detail_level = run.detail_level or "domain"

            service = GenerationService()
            gen_result = await service.generate(
                requirements_text,
                diagram_type=diagram_type,
                detail_level=detail_level,
                skip_validation=True,
            )

            diagram_data = {
                "plantuml_source": gen_result.plantuml_code,
                "syntax_valid": gen_result.syntax_valid,
                "entities": gen_result.entities,
                "relationships": gen_result.relationships,
                "entities_count": gen_result.entities_count,
                "relationships_count": gen_result.relationships_count,
                "refine_iterations": gen_result.refine_iterations,
                "warnings": gen_result.warnings,
            }

            # Save performance metrics
            run.generation_time_ms = gen_result.generation_time_ms
            run.refine_iterations = gen_result.refine_iterations
            run.syntax_valid = gen_result.syntax_valid
            run.llm_calls_count = gen_result.llm_calls_count
            run.tokens_used = gen_result.tokens_used

            # Create PNG artifact if available
            if gen_result.diagram_image_base64:
                image_bytes = base64.b64decode(gen_result.diagram_image_base64)
                await crud_run.create_artifact(
                    db,
                    run_id=run.id,
                    project_id=run.project_id,
                    user_id=user_id,
                    kind="uml_png",
                    content_type="image/png",
                    data=image_bytes,
                    filename=f"diagram_{run.id}.png"
                )

            # Create PlantUML text artifact
            if gen_result.plantuml_code:
                await crud_run.create_artifact(
                    db,
                    run_id=run.id,
                    project_id=run.project_id,
                    user_id=user_id,
                    kind="plantuml",
                    content_type="text/plain",
                    data=gen_result.plantuml_code.encode("utf-8"),
                    filename=f"diagram_{run.id}.puml"
                )

            await crud_run.set_generation_status(
                db, run, "succeeded",
                diagram_data=diagram_data
            )

        except Exception as e:
            logger.exception(f"Generation failed for run {run_id}: {e}")
            try:
                run = await crud_run.get_run_by_id(db, run_id, user_id)
                if run:
                    await crud_run.set_generation_status(db, run, "failed")
            except Exception as inner_e:
                logger.error(f"Failed to set generation failed status: {inner_e}")


async def start_validation(run_id: int, user_id: int) -> None:
    """Start validation as background task."""
    asyncio.create_task(process_validation(run_id, user_id))


async def start_generation(run_id: int, user_id: int) -> None:
    """Start generation as background task."""
    asyncio.create_task(process_generation(run_id, user_id))
