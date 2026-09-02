"""Layer 3: Semantic Analysis - OpenAI-based assessment."""

from openai import AsyncOpenAI
from dataclasses import dataclass, field
from typing import List
from app.core.config import settings
import json


@dataclass
class SemanticIssue:
    category: str        # "modelability" | "completeness" | "consistency"
    severity: str
    detail: str
    suggestion: str


@dataclass
class SemanticResult:
    issues: List[SemanticIssue] = field(default_factory=list)

    modelability_score: float = 0.0
    completeness_score: float = 0.0
    consistency_score: float = 0.0

    detected_entities: List[str] = field(default_factory=list)
    detected_relationships: List[str] = field(default_factory=list)

    feedback: str = ""



SEMANTIC_VALIDATION_PROMPT = """You are a UML class diagram modelability assessor for a requirements validation system.

## YOUR ROLE

Evaluate requirements ONLY on dimensions that rule-based NLP cannot assess:
1. **Modelability** — can these requirements become a UML class diagram?
2. **Completeness** — are all entities and relationships fully defined?
3. **Consistency** — are there logical contradictions?

DO NOT evaluate:
- Vague words (already detected by lexical analyzer)
- Passive voice, pronouns (already detected by structural analyzer)
- Grammar or spelling

## SCORING RUBRIC

### 1. MODELABILITY (0-10)
Can these requirements be transformed into a UML class diagram?

| Score | Criteria |
|-------|----------|
| 9-10  | Clear classes with attributes, methods, and explicit relationships |
| 7-8   | Main entities identifiable, most relationships stated or strongly implied |
| 5-6   | Core entities present but relationships vague, or mixed structural/behavioral |
| 3-4   | Primarily behavioral/procedural with few structural elements |
| 1-2   | Pure workflow, UI descriptions, or non-structural content |

**Positive indicators (increases score):**
- Nouns that clearly map to classes
- Properties/characteristics that map to attributes
- Actions with clear actors that map to methods
- "is-a", "has-a", "belongs to", "contains" patterns for relationships
- Explicit cardinalities ("each User has many Orders")

**Negative indicators (decreases score):**
- Step-by-step procedures without actors
- UI layout descriptions ("button on the left")
- Pure data flow without entities
- System behaviors without classes

### 2. COMPLETENESS (0-10)
Are all structural elements fully defined?

| Score | Criteria |
|-------|----------|
| 9-10  | Every entity has attributes AND relationships with cardinalities |
| 7-8   | Main entities complete, peripheral entities underspecified |
| 5-6   | Entity names present but few attributes or relationships |
| 3-4   | Only high-level entity mentions, no details |
| 1-2   | Vague domain description, almost no extractable elements |

### 3. CONSISTENCY (0-10)
Are requirements logically compatible?

| Score | Criteria |
|-------|----------|
| 9-10  | No contradictions, clear and coherent hierarchy |
| 7-8   | Minor ambiguities but no logical conflicts |
| 5-6   | Some potentially conflicting statements (cardinality mismatches) |
| 3-4   | Several contradictory requirements |
| 1-2   | Major contradictions making modeling impossible |

## ENTITY & RELATIONSHIP EXTRACTION

Extract for preview (helps user understand what was found):

**Entities**: Class names found in requirements (PascalCase)
**Relationships**: In format "Entity1 → Entity2 (relationship-type, cardinality)"

Relationship types: inheritance, composition, aggregation, association

## OUTPUT FORMAT

Return ONLY valid JSON (no markdown, no explanation):

```json
{
  "modelability_score": 7,
  "completeness_score": 5,
  "consistency_score": 9,
  "detected_entities": ["User", "Order", "Product", "Payment"],
  "detected_relationships": [
    "User → Order (association, one-to-many)",
    "Order → Product (association, many-to-many)",
    "Order → Payment (composition, one-to-one)"
  ],
  "feedback": "2-3 sentence summary of overall assessment",
  "issues": [
    {
      "category": "completeness",
      "severity": "warning",
      "detail": "Product class has no attributes specified",
      "suggestion": "Add attributes: name, price, description, stockQuantity"
    },
    {
      "category": "modelability",
      "severity": "info",
      "detail": "'User authentication flow' describes behavior, not structure",
      "suggestion": "For class diagram, describe User's auth-related attributes instead of flow"
    }
  ]
}
```

## IMPORTANT RULES

1. Scores must be integers 0-10
2. Always extract at least 1 entity if text mentions any nouns
3. Issues array can be empty if no semantic problems found
4. feedback should be actionable, not just restate scores
5. DO NOT mention lexical/structural issues — those are handled separately"""


class SemanticAnalyzer:
    """
    Layer 3: OpenAI-based semantic analysis.
    Evaluates only what rule-based cannot.
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def analyze(
        self,
        text: str,
        lexical_issues_summary: str = "",
        structural_issues_summary: str = ""
    ) -> SemanticResult:
        """
        Accepts text + summaries from Layers 1-2 to avoid duplication.
        """

        user_message = self._build_user_message(
            text, lexical_issues_summary, structural_issues_summary
        )

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.0,  # Deterministic for consistency
                messages=[
                    {"role": "system", "content": SEMANTIC_VALIDATION_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"}
            )

            raw = json.loads(response.choices[0].message.content)

            result = SemanticResult(
                modelability_score=float(raw.get("modelability_score", 5)),
                completeness_score=float(raw.get("completeness_score", 5)),
                consistency_score=float(raw.get("consistency_score", 5)),
                detected_entities=raw.get("detected_entities", []),
                detected_relationships=raw.get("detected_relationships", []),
                feedback=raw.get("feedback", ""),
            )

            for issue in raw.get("issues", []):
                result.issues.append(SemanticIssue(
                    category=issue.get("category", ""),
                    severity=issue.get("severity", "warning"),
                    detail=issue.get("detail", ""),
                    suggestion=issue.get("suggestion", ""),
                ))

            return result

        except Exception as e:
            return SemanticResult(
                modelability_score=5.0,
                completeness_score=5.0,
                consistency_score=5.0,
                feedback=f"Semantic analysis unavailable: {str(e)}"
            )

    def _build_user_message(self, text: str, lexical_summary: str, structural_summary: str) -> str:
        msg = f"""## REQUIREMENTS TEXT

{text}

"""

        if lexical_summary:
            msg += f"""## ALREADY DETECTED BY LEXICAL ANALYSIS (do NOT repeat)

{lexical_summary}

"""

        if structural_summary:
            msg += f"""## ALREADY DETECTED BY STRUCTURAL ANALYSIS (do NOT repeat)

{structural_summary}

"""

        msg += "Analyze for modelability, completeness, and consistency. Return JSON only."
        return msg
