"""Validation Service - Orchestrator for 3-layer validation."""

from app.services.validation.lexical_analyzer import LexicalAnalyzer
from app.services.validation.structural_analyzer import StructuralAnalyzer
from app.services.validation.semantic_analyzer import SemanticAnalyzer
from app.services.validation.score_aggregator import ScoreAggregator, ValidationResult


class ValidationService:
    """Orchestrates lexical, structural, and semantic validation layers."""

    def __init__(self):
        self.lexical = LexicalAnalyzer()
        self.structural = StructuralAnalyzer()
        self.semantic = SemanticAnalyzer()
        self.aggregator = ScoreAggregator()

    async def validate(self, requirements: str) -> ValidationResult:
        lexical_result = self.lexical.analyze(requirements)
        structural_result = self.structural.analyze(requirements)

        lexical_summary = self._summarize_lexical(lexical_result)
        structural_summary = self._summarize_structural(structural_result)

        semantic_result = await self.semantic.analyze(
            text=requirements,
            lexical_issues_summary=lexical_summary,
            structural_issues_summary=structural_summary,
        )

        return self.aggregator.aggregate(
            lexical=lexical_result,
            structural=structural_result,
            semantic=semantic_result,
        )

    def _summarize_lexical(self, result) -> str:
        parts = []
        if result.vague_count:
            parts.append(f"{result.vague_count} vague terms")
        if result.weak_modal_count:
            parts.append(f"{result.weak_modal_count} weak modals")
        if result.loophole_count:
            parts.append(f"{result.loophole_count} loopholes")
        if result.incomplete_count:
            parts.append(f"{result.incomplete_count} incomplete markers")
        return "; ".join(parts) if parts else "No lexical issues"

    def _summarize_structural(self, result) -> str:
        parts = []
        if result.passive_voice_count:
            parts.append(f"{result.passive_voice_count} passive voice")
        if result.missing_svo_count:
            parts.append(f"{result.missing_svo_count} missing SVO")
        if result.anaphoric_ambiguity_count:
            parts.append(f"{result.anaphoric_ambiguity_count} pronoun issues")
        return "; ".join(parts) if parts else "No structural issues"
