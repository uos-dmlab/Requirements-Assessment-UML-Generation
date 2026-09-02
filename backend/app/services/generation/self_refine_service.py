"""SELF-REFINE Service - Iterative code improvement."""

from openai import AsyncOpenAI
from app.services.generation.plantuml_service import PlantUMLService
from app.services.generation.prompts import REFINE_FEEDBACK_PROMPT, REFINE_FIX_PROMPT
from app.core.config import settings
import re


class SelfRefineService:
    """Iterative syntax refinement: check → feedback → fix → repeat."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.plantuml = PlantUMLService()
        self.max_iterations = settings.SELF_REFINE_MAX_ITERATIONS

    async def refine_loop(
        self,
        requirements: str,
        plantuml_code: str,
        entity_registry: dict
    ) -> tuple[str, int, bool]:
        """
        SELF-REFINE loop to fix syntax errors.

        Returns:
            tuple: (refined_code, iterations_used, is_valid)
        """
        current_code = plantuml_code

        for iteration in range(self.max_iterations):
            if self.plantuml.check_syntax(current_code):
                return current_code, iteration, True

            errors = self.plantuml.get_syntax_errors(current_code)
            feedback = await self._get_feedback(
                plantuml_code=current_code,
                syntax_errors=errors
            )
            current_code = await self._refine(
                requirements=requirements,
                plantuml_code=current_code,
                feedback=feedback,
                entity_registry=entity_registry
            )

        # After max_iterations, check one more time
        is_valid = self.plantuml.check_syntax(current_code)
        return current_code, self.max_iterations, is_valid

    async def _get_feedback(self, plantuml_code: str, syntax_errors: str) -> str:

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            temperature=0.0,
            messages=[
                {"role": "system", "content": REFINE_FEEDBACK_PROMPT},
                {"role": "user", "content": f"""## PLANTUML CODE

{plantuml_code}

## SYNTAX ERRORS FROM PLANTUML.JAR

{syntax_errors}

What exactly is wrong with this code?"""}
            ]
        )

        return response.choices[0].message.content

    async def _refine(
        self,
        requirements: str,
        plantuml_code: str,
        feedback: str,
        entity_registry: dict
    ) -> str:
        entities_list = [e["canonical_name"] for e in entity_registry.get("entities", [])]

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            temperature=0.0,
            messages=[
                {"role": "system", "content": REFINE_FIX_PROMPT},
                {"role": "user", "content": f"""## ORIGINAL REQUIREMENTS

{requirements}

## CURRENT (BROKEN) CODE

{plantuml_code}

## FEEDBACK (what's wrong)

{feedback}

## REQUIRED ENTITIES (must be present)

{', '.join(entities_list)}

Output the FIXED PlantUML code:"""}
            ]
        )

        text = response.choices[0].message.content

        # Extract code between @startuml and @enduml
        return self._extract_plantuml(text)

    def _extract_plantuml(self, text: str) -> str:
        text = re.sub(r'```plantuml\s*', '', text)
        text = re.sub(r'```\s*', '', text)

        match = re.search(r'(@startuml.*?@enduml)', text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)

        text = text.strip()
        if not text.lower().startswith("@startuml"):
            text = "@startuml\n" + text
        if not text.lower().endswith("@enduml"):
            text = text + "\n@enduml"

        return text
