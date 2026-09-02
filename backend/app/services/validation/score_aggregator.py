"""Score Aggregator - Combines results from all 3 validation layers."""

from dataclasses import dataclass, field
from typing import List
from app.services.validation.lexical_analyzer import LexicalResult
from app.services.validation.structural_analyzer import StructuralResult
from app.services.validation.semantic_analyzer import SemanticResult
from app.core.config import settings


@dataclass
class MetricScore:
    name: str
    label: str
    score: float
    max_score: float = 10.0
    source: str = ""       # "lexical" | "structural" | "semantic"
    description: str = ""


@dataclass
class AggregatedIssue:
    layer: str
    category: str
    severity: str
    message: str
    sentence_index: int = -1
    sentence_text: str = ""
    suggestion: str = ""


@dataclass
class ValidationResult:
    """Final result — sent to frontend."""

    metrics: List[MetricScore] = field(default_factory=list)

    deterministic_score: float = 0.0
    semantic_score: float = 0.0
    total_score: float = 0.0

    can_generate: bool = False

    issues: List[AggregatedIssue] = field(default_factory=list)

    detected_entities: List[str] = field(default_factory=list)
    detected_relationships: List[str] = field(default_factory=list)

    feedback: str = ""

    readability_grade: float = 0.0
    total_sentences: int = 0
    total_words: int = 0


class ScoreAggregator:
    """
    Combines results from 3 layers.

    Weights:
      Deterministic (L1 + L2): 60%
      Semantic (L3): 40%

    Gate:
      - deterministic < 40% → can_generate = False
      - total < 50% → can_generate = False
      - modelability < 4 → can_generate = False
    """

    def aggregate(
        self,
        lexical: LexicalResult,
        structural: StructuralResult,
        semantic: SemanticResult
    ) -> ValidationResult:

        result = ValidationResult()
        result.total_sentences = lexical.total_sentences
        result.total_words = lexical.total_words
        result.readability_grade = structural.flesch_kincaid_grade
        result.detected_entities = semantic.detected_entities
        result.detected_relationships = semantic.detected_relationships
        result.feedback = semantic.feedback

        # ─────────────────────────────────────
        # Build 8 metrics
        # ─────────────────────────────────────

        # Layer 1
        result.metrics.append(MetricScore(
            name="vagueness",
            label="Vagueness",
            score=lexical.vagueness_score,
            source="lexical",
            description=f"{lexical.vague_count} vague terms, {lexical.weak_modal_count} weak modals"
        ))

        result.metrics.append(MetricScore(
            name="completeness_markers",
            label="Completeness Markers",
            score=lexical.weakness_score,
            source="lexical",
            description=f"{lexical.incomplete_count} incomplete markers (TBD, etc.)"
        ))

        # Layer 2
        result.metrics.append(MetricScore(
            name="clarity",
            label="Clarity",
            score=structural.clarity_score,
            source="structural",
            description=f"Passive: {structural.passive_voice_count}, Pronouns: {structural.anaphoric_ambiguity_count}"
        ))

        result.metrics.append(MetricScore(
            name="structure",
            label="Structure (SVO)",
            score=structural.structure_score,
            source="structural",
            description=f"Missing SVO: {structural.missing_svo_count}/{structural.total_sentences}"
        ))

        result.metrics.append(MetricScore(
            name="readability",
            label="Readability",
            score=self._readability_to_score(structural.flesch_kincaid_grade),
            source="structural",
            description=f"Flesch-Kincaid: {structural.flesch_kincaid_grade:.1f}"
        ))

        # Layer 3
        result.metrics.append(MetricScore(
            name="modelability",
            label="Modelability",
            score=semantic.modelability_score,
            source="semantic",
            description="Can be represented as UML class diagram"
        ))

        result.metrics.append(MetricScore(
            name="completeness",
            label="Completeness",
            score=semantic.completeness_score,
            source="semantic",
            description="All entities and relationships defined"
        ))

        result.metrics.append(MetricScore(
            name="consistency",
            label="Consistency",
            score=semantic.consistency_score,
            source="semantic",
            description="No logical contradictions"
        ))

        # ─────────────────────────────────────
        # Aggregate scores
        # ─────────────────────────────────────

        det_metrics = [m.score for m in result.metrics if m.source in ("lexical", "structural")]
        result.deterministic_score = round((sum(det_metrics) / len(det_metrics)) * 10, 1)

        sem_metrics = [m.score for m in result.metrics if m.source == "semantic"]
        result.semantic_score = round((sum(sem_metrics) / len(sem_metrics)) * 10, 1)

        result.total_score = round(
            result.deterministic_score * settings.DETERMINISTIC_WEIGHT +
            result.semantic_score * settings.SEMANTIC_WEIGHT,
            1
        )

        # ─────────────────────────────────────
        # Gate logic
        # ─────────────────────────────────────

        if result.deterministic_score < settings.DETERMINISTIC_FLOOR:
            result.can_generate = False
        elif result.total_score < settings.TOTAL_THRESHOLD:
            result.can_generate = False
        elif semantic.modelability_score < 4:
            result.can_generate = False
        else:
            result.can_generate = True

        # ─────────────────────────────────────
        # Collect issues
        # ─────────────────────────────────────

        for issue in lexical.issues:
            result.issues.append(AggregatedIssue(
                layer="lexical",
                category=issue.category,
                severity=issue.severity,
                message=issue.suggestion,
                sentence_index=issue.sentence_index,
                sentence_text=issue.sentence_text,
                suggestion=issue.suggestion,
            ))

        for issue in structural.issues:
            result.issues.append(AggregatedIssue(
                layer="structural",
                category=issue.category,
                severity=issue.severity,
                message=issue.detail,
                sentence_index=issue.sentence_index,
                sentence_text=issue.sentence_text,
                suggestion=issue.suggestion,
            ))

        for issue in semantic.issues:
            result.issues.append(AggregatedIssue(
                layer="semantic",
                category=issue.category,
                severity=issue.severity,
                message=issue.detail,
                suggestion=issue.suggestion,
            ))

        # Sort: errors first
        severity_order = {"error": 0, "warning": 1, "info": 2}
        result.issues.sort(key=lambda i: severity_order.get(i.severity, 3))

        return result

    def _readability_to_score(self, fk_grade: float) -> float:
        if 8 <= fk_grade <= 12:
            return 10.0
        elif 6 <= fk_grade < 8 or 12 < fk_grade <= 14:
            return 8.0
        elif 4 <= fk_grade < 6 or 14 < fk_grade <= 16:
            return 6.0
        else:
            return 4.0
