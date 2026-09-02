"""Layer 2: Structural Analysis - spaCy-based NLP analysis."""

import spacy
import textstat
from dataclasses import dataclass, field
from typing import List

# Load model once at module level
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None


@dataclass
class StructuralIssue:
    category: str        # "passive_voice" | "missing_svo" | "coordination_ambiguity" | etc
    severity: str
    sentence_index: int
    sentence_text: str
    detail: str
    suggestion: str


@dataclass
class StructuralResult:
    issues: List[StructuralIssue] = field(default_factory=list)

    passive_voice_count: int = 0
    missing_svo_count: int = 0
    coordination_ambiguity_count: int = 0
    anaphoric_ambiguity_count: int = 0

    avg_sentence_length: float = 0.0
    avg_dependency_depth: float = 0.0
    flesch_kincaid_grade: float = 0.0
    gunning_fog_index: float = 0.0

    clarity_score: float = 10.0
    structure_score: float = 10.0

    total_sentences: int = 0


class StructuralAnalyzer:
    """
    Layer 2: spaCy-based structural analysis.
    CPU-only, ~100ms, free.
    """

    def analyze(self, text: str) -> StructuralResult:
        result = StructuralResult()

        if nlp is None:
            # spaCy model not available, return default scores
            result.clarity_score = 7.0
            result.structure_score = 7.0
            return result

        doc = nlp(text)

        sentences = list(doc.sents)
        result.total_sentences = len(sentences)

        if not sentences:
            return result

        dependency_depths = []
        sentence_lengths = []

        for sent_idx, sent in enumerate(sentences):
            sent_text = sent.text.strip()
            if not sent_text:
                continue

            sentence_lengths.append(len(list(sent)))

            self._check_passive_voice(sent, sent_idx, sent_text, result)
            self._check_svo_completeness(sent, sent_idx, sent_text, result)
            self._check_coordination_ambiguity(sent, sent_idx, sent_text, result)
            self._check_anaphoric_ambiguity(sent, sent_idx, sent_text, result)

            depth = self._get_max_dependency_depth(sent)
            dependency_depths.append(depth)

            if depth > 6:
                result.issues.append(StructuralIssue(
                    category="complexity",
                    severity="info",
                    sentence_index=sent_idx,
                    sentence_text=sent_text,
                    detail=f"Dependency depth: {depth} (recommended ≤ 4)",
                    suggestion="Break into shorter, simpler sentences"
                ))

        # Counts
        result.passive_voice_count = sum(1 for i in result.issues if i.category == "passive_voice")
        result.missing_svo_count = sum(1 for i in result.issues if i.category == "missing_svo")
        result.coordination_ambiguity_count = sum(1 for i in result.issues if i.category == "coordination_ambiguity")
        result.anaphoric_ambiguity_count = sum(1 for i in result.issues if i.category == "anaphoric_ambiguity")

        # Metrics
        result.avg_sentence_length = sum(sentence_lengths) / max(len(sentence_lengths), 1)
        result.avg_dependency_depth = sum(dependency_depths) / max(len(dependency_depths), 1)
        result.flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
        result.gunning_fog_index = textstat.gunning_fog(text)

        # Scores
        result.clarity_score = self._compute_clarity_score(result)
        result.structure_score = self._compute_structure_score(result)

        return result

    def _check_passive_voice(self, sent, sent_idx: int, sent_text: str, result: StructuralResult):
        """Passive voice hides the actor."""
        has_passive = any(token.dep_ in ("nsubjpass", "auxpass") for token in sent)
        if has_passive:
            passive_tokens = [t for t in sent if t.dep_ in ("nsubjpass", "auxpass")]
            passive_phrase = " ".join([t.text for t in passive_tokens[:3]])

            result.issues.append(StructuralIssue(
                category="passive_voice",
                severity="warning",
                sentence_index=sent_idx,
                sentence_text=sent_text,
                detail=f'Passive construction near "{passive_phrase}"',
                suggestion="Rewrite in active voice: specify WHO performs the action"
            ))

    def _check_svo_completeness(self, sent, sent_idx: int, sent_text: str, result: StructuralResult):
        """Check Subject-Verb-Object presence."""
        has_subject = any(token.dep_ in ("nsubj", "nsubjpass") for token in sent)
        has_verb = any(token.pos_ == "VERB" for token in sent)

        if len(list(sent)) > 3:
            if not has_subject:
                result.issues.append(StructuralIssue(
                    category="missing_svo",
                    severity="warning",
                    sentence_index=sent_idx,
                    sentence_text=sent_text,
                    detail="Missing subject — who/what performs the action?",
                    suggestion="Add explicit subject: 'The [System/User] shall...'"
                ))
            elif not has_verb:
                result.issues.append(StructuralIssue(
                    category="missing_svo",
                    severity="warning",
                    sentence_index=sent_idx,
                    sentence_text=sent_text,
                    detail="Missing verb — what action is performed?",
                    suggestion="Add a verb describing the behavior"
                ))

    def _check_coordination_ambiguity(self, sent, sent_idx: int, sent_text: str, result: StructuralResult):
        """Check for mixed AND/OR."""
        tokens_text = [t.text.lower() for t in sent]
        has_and = "and" in tokens_text
        has_or = "or" in tokens_text

        if has_and and has_or:
            result.issues.append(StructuralIssue(
                category="coordination_ambiguity",
                severity="error",
                sentence_index=sent_idx,
                sentence_text=sent_text,
                detail='Mixed "and"/"or" creates ambiguous grouping',
                suggestion="Use parentheses or split: '(A and B) or C'"
            ))

    def _check_anaphoric_ambiguity(self, sent, sent_idx: int, sent_text: str, result: StructuralResult):
        """Check pronouns without clear referent."""
        pronouns_found = []
        for token in sent:
            if (token.pos_ == "PRON"
                and token.text.lower() in {"it", "they", "them", "this", "that", "these", "those", "its", "their"}
                and token.dep_ in ("nsubj", "nsubjpass", "dobj")):
                pronouns_found.append(token.text)

        if pronouns_found:
            result.issues.append(StructuralIssue(
                category="anaphoric_ambiguity",
                severity="warning",
                sentence_index=sent_idx,
                sentence_text=sent_text,
                detail=f'Pronoun(s) {pronouns_found} may have unclear referent',
                suggestion="Replace pronouns with explicit entity names"
            ))

    def _get_max_dependency_depth(self, sent) -> int:
        """Max depth of dependency tree."""
        def depth(token, current=0):
            if list(token.children):
                return max(depth(child, current + 1) for child in token.children)
            return current

        root = [t for t in sent if t.dep_ == "ROOT"]
        if root:
            return depth(root[0])
        return 0

    def _compute_clarity_score(self, result: StructuralResult) -> float:
        total_sents = max(result.total_sentences, 1)
        problem_count = (
            result.passive_voice_count +
            result.anaphoric_ambiguity_count +
            result.coordination_ambiguity_count
        )
        problem_ratio = problem_count / total_sents
        score = max(0, 10 - problem_ratio * 10)

        if result.avg_dependency_depth > 5:
            score -= 1
        if result.flesch_kincaid_grade > 14:
            score -= 1

        return round(max(0, min(10, score)), 1)

    def _compute_structure_score(self, result: StructuralResult) -> float:
        total_sents = max(result.total_sentences, 1)
        svo_problem_ratio = result.missing_svo_count / total_sents
        score = max(0, 10 - svo_problem_ratio * 15)
        return round(max(0, min(10, score)), 1)
