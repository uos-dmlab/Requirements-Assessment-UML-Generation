"""Stats API endpoint — aggregated performance statistics for thesis."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sql_func

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.run import Run
from app.core.security import get_current_user


router = APIRouter()


class TimingStats(BaseModel):
    count: int = 0
    avg_ms: float = 0
    min_ms: Optional[int] = None
    max_ms: Optional[int] = None


class GenerationStats(TimingStats):
    syntax_valid_rate: float = 0
    avg_refine_iterations: float = 0


class LLMUsageStats(BaseModel):
    total_llm_calls: int = 0
    total_tokens: int = 0
    avg_llm_calls: float = 0
    avg_tokens: float = 0


class StatsResponse(BaseModel):
    total_runs: int = 0
    runs_with_validation: int = 0
    runs_with_generation: int = 0
    validation: TimingStats = TimingStats()
    generation: GenerationStats = GenerationStats()
    llm_usage: LLMUsageStats = LLMUsageStats()


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get aggregated performance statistics",
)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregated performance statistics across all runs for the current user."""

    # Fetch all runs for user in one query
    result = await db.execute(
        select(Run).where(Run.user_id == current_user.id)
    )
    runs = list(result.scalars().all())

    if not runs:
        return StatsResponse()

    # Validation timing
    v_times = [r.validation_time_ms for r in runs if r.validation_time_ms is not None]
    validation = TimingStats()
    if v_times:
        validation = TimingStats(
            count=len(v_times),
            avg_ms=round(sum(v_times) / len(v_times), 1),
            min_ms=min(v_times),
            max_ms=max(v_times),
        )

    # Generation timing + quality
    g_times = [r.generation_time_ms for r in runs if r.generation_time_ms is not None]
    gen_runs = [r for r in runs if r.generation_time_ms is not None]
    generation = GenerationStats()
    if g_times:
        syntax_valid_count = sum(1 for r in gen_runs if r.syntax_valid)
        refine_iters = [r.refine_iterations for r in gen_runs if r.refine_iterations is not None]
        generation = GenerationStats(
            count=len(g_times),
            avg_ms=round(sum(g_times) / len(g_times), 1),
            min_ms=min(g_times),
            max_ms=max(g_times),
            syntax_valid_rate=round(syntax_valid_count / len(gen_runs), 3) if gen_runs else 0,
            avg_refine_iterations=round(sum(refine_iters) / len(refine_iters), 2) if refine_iters else 0,
        )

    # LLM usage
    llm_calls_list = [r.llm_calls_count for r in runs if r.llm_calls_count is not None]
    tokens_list = [r.tokens_used for r in runs if r.tokens_used is not None]
    llm_usage = LLMUsageStats(
        total_llm_calls=sum(llm_calls_list),
        total_tokens=sum(tokens_list),
        avg_llm_calls=round(sum(llm_calls_list) / len(llm_calls_list), 1) if llm_calls_list else 0,
        avg_tokens=round(sum(tokens_list) / len(tokens_list), 1) if tokens_list else 0,
    )

    return StatsResponse(
        total_runs=len(runs),
        runs_with_validation=len(v_times),
        runs_with_generation=len(g_times),
        validation=validation,
        generation=generation,
        llm_usage=llm_usage,
    )
