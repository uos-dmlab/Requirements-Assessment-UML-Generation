"""Entity Extractor - Stage 2 of generation pipeline."""

from openai import AsyncOpenAI
from dataclasses import dataclass, field
from typing import List, Dict
from app.core.config import settings
import json


@dataclass
class EntityRegistry:
    """Registry of entities for consistent naming."""
    entities: List[Dict] = field(default_factory=list)
    relationships: List[Dict] = field(default_factory=list)
    entity_count: int = 0
    relationship_count: int = 0


ENTITY_EXTRACTION_PROMPT = """You are a UML class diagram entity extractor.
Extract ALL entities and relationships from the given requirements for a class diagram.

## EXTRACTION RULES

**Entities (classes):**
- Nouns → potential classes (PascalCase: User, Order, Product)
- Each entity should have:
  - canonical_name: Primary name in PascalCase
  - aliases: Alternative names found in text (lowercase)
  - attributes: Properties mentioned (camelCase with types if inferrable)
  - methods: Actions/behaviors mentioned (camelCase with parentheses)

**Important**: Only include attributes that are explicitly mentioned in the requirements for each entity. If the requirements don't mention any attributes for an entity, leave the attributes list empty. Do not infer common attributes like id, name, email unless the text specifically states them.

**Relationships:**
- "is a" / "type of" / "extends" → inheritance
- "contains" / "owns" / "is composed of" → composition (strong ownership, lifecycle dependency)
- "has" / "includes" / "consists of" → aggregation (weak ownership)
- "uses" / "references" / "associated with" → association

**Cardinality:**
- "each", "every", "a single" → "1"
- "many", "multiple", "several", "list of" → "*"
- "zero or one", "optional" → "0..1"
- "one or more", "at least one" → "1..*"

## OUTPUT FORMAT (JSON only, no markdown)

```json
{
  "entities": [
    {
      "canonical_name": "User",
      "aliases": ["user", "customer", "client"],
      "attributes": ["id: int", "name: String", "email: String", "isActive: boolean"],
      "methods": ["login()", "register()", "updateProfile()"]
    },
    {
      "canonical_name": "Order",
      "aliases": ["order", "purchase"],
      "attributes": ["id: int", "date: Date", "totalAmount: double", "status: String"],
      "methods": ["calculate()", "submit()", "cancel()"]
    }
  ],
  "relationships": [
    {
      "from": "User",
      "to": "Order",
      "type": "association",
      "label": "places",
      "cardinality_from": "1",
      "cardinality_to": "*"
    },
    {
      "from": "Order",
      "to": "OrderItem",
      "type": "composition",
      "label": "contains",
      "cardinality_from": "1",
      "cardinality_to": "1..*"
    }
  ],
  "entity_count": 2,
  "relationship_count": 2
}
```

## IMPORTANT

1. Use EXACT names consistently — if "User" is the canonical name, always use "User", not "user" or "Customer"
2. Infer types where obvious: names → String, counts → int, prices → double, flags → boolean
3. If relationship type is unclear, default to "association"
4. If cardinality is unclear, use "1" for from-side and "*" for to-side"""


class EntityExtractor:
    """
    Stage 2: Entity Registry Extraction

    Extracts entities BEFORE generation for:
    1. Consistent naming (canonical names)
    2. Pre-identified relationships
    3. Context for generation prompt
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def extract(self, requirements: str) -> EntityRegistry:
        """Extracts entity registry from requirements."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": ENTITY_EXTRACTION_PROMPT},
                    {"role": "user", "content": requirements}
                ],
                response_format={"type": "json_object"}
            )

            raw = json.loads(response.choices[0].message.content)

            return EntityRegistry(
                entities=raw.get("entities", []),
                relationships=raw.get("relationships", []),
                entity_count=len(raw.get("entities", [])),
                relationship_count=len(raw.get("relationships", []))
            )

        except Exception as e:
            # Fallback: return empty registry
            return EntityRegistry()
