"""Layer 1: Lexical Analysis - 100% deterministic, dictionary-based."""

import re
from dataclasses import dataclass, field
from typing import List
from app.services.validation.dictionaries import (
    VAGUE_WORDS, WEAK_MODALS, LOOPHOLE_PHRASES,
    INCOMPLETE_MARKERS, SUPERLATIVES, COMPARATIVES
)


@dataclass
class LexicalIssue:
    """A specific finding with exact position."""
    category: str        # "vagueness" | "weakness" | "loophole" | "incomplete" | "superlative"
    severity: str        # "error" | "warning" | "info"
    word: str            # Found word/phrase
    position: int        # Character position in text
    sentence_index: int  # Sentence number (0-based)
    sentence_text: str   # Sentence text for context
    suggestion: str      # Specific recommendation


@dataclass
class LexicalResult:
    """Result of lexical analysis."""
    issues: List[LexicalIssue] = field(default_factory=list)

    # Counts by category
    vague_count: int = 0
    weak_modal_count: int = 0
    loophole_count: int = 0
    incomplete_count: int = 0
    superlative_count: int = 0

    # Scores (0-10, 10 = excellent = no problems)
    vagueness_score: float = 10.0
    weakness_score: float = 10.0

    total_words: int = 0
    total_sentences: int = 0


class LexicalAnalyzer:
    """
    Layer 1: 100% deterministic lexical analysis.
    Works instantly, no API calls, no ML.
    """

    def analyze(self, text: str) -> LexicalResult:
        result = LexicalResult()

        sentences = self._split_sentences(text)
        result.total_sentences = len(sentences)
        result.total_words = len(text.split())

        for sent_idx, sentence in enumerate(sentences):
            sentence_lower = sentence.lower().strip()

            self._check_word_set(
                sentence, sentence_lower, sent_idx,
                VAGUE_WORDS, "vagueness", "warning",
                "Replace with a specific, measurable term",
                result
            )
            self._check_word_set(
                sentence, sentence_lower, sent_idx,
                WEAK_MODALS, "weakness", "warning",
                "Use 'shall' for mandatory requirements or 'will' for facts",
                result
            )
            self._check_word_set(
                sentence, sentence_lower, sent_idx,
                SUPERLATIVES, "superlative", "info",
                "Specify a concrete threshold instead",
                result
            )
            self._check_word_set(
                sentence, sentence_lower, sent_idx,
                COMPARATIVES, "superlative", "info",
                "Specify what this is compared to and by how much",
                result
            )
            self._check_phrases(
                sentence, sentence_lower, sent_idx,
                LOOPHOLE_PHRASES, "loophole", "error",
                "Remove escape clause — requirement should be unconditional",
                result
            )
            self._check_phrases(
                sentence, sentence_lower, sent_idx,
                INCOMPLETE_MARKERS, "incomplete", "error",
                "Replace with actual content",
                result
            )

        # Counts
        result.vague_count = sum(1 for i in result.issues if i.category == "vagueness")
        result.weak_modal_count = sum(1 for i in result.issues if i.category == "weakness")
        result.loophole_count = sum(1 for i in result.issues if i.category == "loophole")
        result.incomplete_count = sum(1 for i in result.issues if i.category == "incomplete")
        result.superlative_count = sum(1 for i in result.issues if i.category == "superlative")

        # Scores
        total_critical = result.vague_count + result.weak_modal_count + result.loophole_count
        total_words = max(result.total_words, 1)

        density = (total_critical / total_words) * 100
        result.vagueness_score = round(max(0, min(10, 10 - density * 2)), 1)

        incomplete_density = (result.incomplete_count / total_words) * 100
        result.weakness_score = round(max(0, min(10, 10 - incomplete_density * 5)), 1)

        return result

    def _check_word_set(
        self, sentence: str, sentence_lower: str, sent_idx: int,
        word_set: set, category: str, severity: str, suggestion: str,
        result: LexicalResult
    ):
        """Check individual words."""
        words = re.findall(r'\b\w+(?:-\w+)*\b', sentence_lower)
        for word in words:
            if word in word_set:
                pos = sentence_lower.find(word)
                result.issues.append(LexicalIssue(
                    category=category,
                    severity=severity,
                    word=word,
                    position=pos,
                    sentence_index=sent_idx,
                    sentence_text=sentence.strip(),
                    suggestion=f'"{word}" → {suggestion}'
                ))

    def _check_phrases(
        self, sentence: str, sentence_lower: str, sent_idx: int,
        phrases: list, category: str, severity: str, suggestion: str,
        result: LexicalResult
    ):
        """Check multi-word phrases."""
        for phrase in phrases:
            if phrase.lower() in sentence_lower:
                pos = sentence_lower.find(phrase.lower())
                result.issues.append(LexicalIssue(
                    category=category,
                    severity=severity,
                    word=phrase,
                    position=pos,
                    sentence_index=sent_idx,
                    sentence_text=sentence.strip(),
                    suggestion=f'"{phrase}" → {suggestion}'
                ))

    def _split_sentences(self, text: str) -> list:
        """Split text into sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        expanded = []
        for s in sentences:
            expanded.extend(s.split('\n'))
        return [s.strip() for s in expanded if s.strip()]
