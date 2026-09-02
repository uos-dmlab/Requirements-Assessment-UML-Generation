"""Pydantic schemas for validation endpoint."""

from pydantic import BaseModel, Field
from typing import List


class ValidateRequest(BaseModel):
    requirements: str = Field(..., min_length=10, max_length=50000)


class MetricScoreSchema(BaseModel):
    name: str
    label: str
    score: float = Field(..., ge=0, le=10)
    max_score: float = 10.0
    source: str
    description: str


class IssueSchema(BaseModel):
    layer: str
    category: str
    severity: str
    message: str
    sentence_index: int = -1
    sentence_text: str = ""
    suggestion: str = ""


class ValidateResponse(BaseModel):
    metrics: List[MetricScoreSchema]

    deterministic_score: float
    semantic_score: float
    total_score: float

    can_generate: bool

    issues: List[IssueSchema]

    detected_entities: List[str]
    detected_relationships: List[str]

    feedback: str
    readability_grade: float
    total_sentences: int
    total_words: int
