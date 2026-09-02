"""Use Case Entity Extractor - Extracts actors, use cases, and relationships."""

from openai import AsyncOpenAI
from dataclasses import dataclass, field
from typing import List, Dict
from app.core.config import settings
from app.services.generation.entity_extractor import EntityRegistry
import json


USECASE_EXTRACTION_PROMPT = """You are an expert requirements analyst extracting Use Case diagram elements.

## STEP 1: IDENTIFY THE SYSTEM BOUNDARY

The "System Under Development" is the software being built. It is NEVER an actor.

**Detection patterns:**
- "[SystemName] shall..." → SystemName is the system boundary
- "[SystemName] must..." → SystemName is the system boundary
- "[SystemName] will..." → SystemName is the system boundary
- "The system shall..." → "System" is the system boundary

**Examples:**
- "CRM shall update profile" → system_boundary: "CRM"
- "ERP shall process order" → system_boundary: "ERP"
- "The application shall send email" → system_boundary: "Application"
- "LMS shall track progress" → system_boundary: "LMS"

## STEP 2: IDENTIFY ACTORS

Actors are entities EXTERNAL to the system that interact WITH it.

**Human actors:**
- Users, Operators, Administrators, Managers, Customers, Clients
- Pattern: "[Person] asks...", "[Role] clicks...", "[User] wants..."

**External system actors:**
- Other systems that integrate with the main system
- Pattern: "[ExternalSystem] sends data to [MainSystem]"
- Examples: "Payment Gateway", "Email Service", "External API"

**NOT actors:**
- The system boundary itself (detected in Step 1)
- Internal components of the system

**Indirect interaction rule:**
- "Client asks Manager" + "Manager uses CRM" → Only Manager is actor
- The person who DIRECTLY interacts with system is the actor

## STEP 3: EXTRACT USE CASES

**Preserve specificity from requirements:**
- Include entity identifiers: "Delete Client B profile" not "Delete profile"
- Include values: "Update phone (777 → 888)" not "Update phone"
- Include context: "Reject order #123" not "Reject order"

**Use case levels:**
- user-goal: Complete valuable outcome for actor
- subfunction: Supporting step, linked via <<include>>

## STEP 4: EXTRACT RELATIONSHIPS

**Types:**
- association: Actor → UseCase (actor initiates)
- include: MainUC → SubUC (always happens)
- extend: ExtendingUC → BaseUC (conditional)
- generalization: SpecificActor → GeneralActor

## OUTPUT FORMAT (JSON only, no markdown)

{
  "system_boundary": "<detected system name>",
  "actors": [
    {"name": "<actor name>", "type": "human|system", "description": "<role>"}
  ],
  "use_cases": [
    {"name": "<specific name with details>", "level": "user-goal|subfunction"}
  ],
  "relationships": [
    {"from": "<source>", "to": "<target>", "type": "<relationship type>"}
  ]
}

## EXAMPLES

### Example 1: CRM
Input: "Hunter shall press button in CRM. CRM shall delete Client B's profile."
Output:
{
  "system_boundary": "CRM",
  "actors": [{"name": "Hunter", "type": "human", "description": "CRM operator"}],
  "use_cases": [{"name": "Delete Client B profile", "level": "user-goal"}],
  "relationships": [{"from": "Hunter", "to": "Delete Client B profile", "type": "association"}]
}

### Example 2: ERP
Input: "Manager approves order. ERP shall update inventory. ERP shall notify warehouse."
Output:
{
  "system_boundary": "ERP",
  "actors": [{"name": "Manager", "type": "human", "description": "Order approver"}],
  "use_cases": [
    {"name": "Approve order", "level": "user-goal"},
    {"name": "Update inventory", "level": "subfunction"},
    {"name": "Notify warehouse", "level": "subfunction"}
  ],
  "relationships": [
    {"from": "Manager", "to": "Approve order", "type": "association"},
    {"from": "Approve order", "to": "Update inventory", "type": "include"},
    {"from": "Approve order", "to": "Notify warehouse", "type": "include"}
  ]
}

### Example 3: E-commerce with external system
Input: "Customer places order. System shall process payment via PayPal. System shall send confirmation."
Output:
{
  "system_boundary": "System",
  "actors": [
    {"name": "Customer", "type": "human", "description": "Online shopper"},
    {"name": "PayPal", "type": "system", "description": "External payment gateway"}
  ],
  "use_cases": [
    {"name": "Place order", "level": "user-goal"},
    {"name": "Process payment", "level": "subfunction"},
    {"name": "Send confirmation", "level": "subfunction"}
  ],
  "relationships": [
    {"from": "Customer", "to": "Place order", "type": "association"},
    {"from": "Place order", "to": "Process payment", "type": "include"},
    {"from": "Place order", "to": "Send confirmation", "type": "include"},
    {"from": "PayPal", "to": "Process payment", "type": "association"}
  ]
}
"""


class UseCaseEntityExtractor:
    """
    Entity extractor specialized for use case diagrams.

    Detects system boundary, actors, use cases, and relationships.
    Returns EntityRegistry with extra fields for use case generation.
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def extract(self, requirements: str) -> EntityRegistry:
        """Extracts use case entity registry from requirements."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": USECASE_EXTRACTION_PROMPT},
                    {"role": "user", "content": requirements}
                ],
                response_format={"type": "json_object"}
            )

            raw = json.loads(response.choices[0].message.content)

            # Build EntityRegistry with new fields stored alongside
            # standard fields for backward compatibility
            actors = raw.get("actors", [])
            use_cases = raw.get("use_cases", [])
            relationships = raw.get("relationships", [])

            # Convert actors + use_cases to entities list
            # (for compatibility with self-refine and response building)
            entities = []
            for a in actors:
                entities.append({
                    "canonical_name": a["name"],
                    "actor_type": a.get("type", "human"),
                })
            for uc in use_cases:
                entities.append({
                    "canonical_name": uc["name"],
                    "actor_type": "use_case",
                })

            registry = EntityRegistry(
                entities=entities,
                relationships=relationships,
                entity_count=len(entities),
                relationship_count=len(relationships),
            )

            # Store new fields for build_usecase_generation_prompt
            registry.system_boundary = raw.get("system_boundary", "System")
            registry.actors = actors
            registry.use_cases = use_cases

            return registry

        except Exception:
            return EntityRegistry()
