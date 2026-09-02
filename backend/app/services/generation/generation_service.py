"""Generation Service - Orchestrator for full generation pipeline."""

import time
import re
from openai import AsyncOpenAI
from app.services.generation.entity_extractor import EntityExtractor
from app.services.generation.usecase_entity_extractor import UseCaseEntityExtractor
from app.services.generation.plantuml_service import PlantUMLService
from app.services.generation.self_refine_service import SelfRefineService
from app.services.generation.prompts import build_generation_prompt, build_usecase_generation_prompt
from app.schemas.generation import GenerateResponse
from app.core.config import settings


class GenerationService:
    """Orchestrates extraction → generation → refinement → rendering pipeline."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.entity_extractor = EntityExtractor()
        self.usecase_entity_extractor = UseCaseEntityExtractor()
        self.plantuml = PlantUMLService()
        self.self_refine = SelfRefineService()
        self.vector_store_id = settings.PLANTUML_VECTOR_STORE_ID

    async def generate(
        self,
        requirements: str,
        diagram_type: str = "class",
        detail_level: str = "domain",
        skip_validation: bool = False,
        use_rag: bool | None = None,
    ) -> GenerateResponse:
        """
        Full diagram generation pipeline.

        Args:
            requirements: Requirements text
            diagram_type: "class" or "use_case"
            detail_level: "domain" or "design" (only applies to class diagrams)
            skip_validation: Skip quality check (not recommended)

        Returns:
            GenerateResponse with code, image and metadata
        """
        start_time = time.perf_counter()
        warnings = []
        llm_calls = 0
        tokens_used = 0

        if diagram_type == "use_case":
            entity_registry = await self.usecase_entity_extractor.extract(requirements)
        else:
            entity_registry = await self.entity_extractor.extract(requirements)
        llm_calls += 1

        if diagram_type == "use_case":
            system_prompt = build_usecase_generation_prompt(entity_registry.__dict__)
        else:
            system_prompt = build_generation_prompt(entity_registry.__dict__, detail_level=detail_level)

        # Determine RAG usage: explicit toggle overrides auto-detection
        do_rag = self.vector_store_id if use_rag is None else use_rag

        print(f"[RAG DEBUG] vector_store_id = {self.vector_store_id}")
        print(f"[RAG DEBUG] use_rag param = {use_rag}")
        print(f"[RAG DEBUG] do_rag final = {do_rag}")

        if do_rag:
            plantuml_code, call_tokens = await self._generate_with_rag(
                requirements=requirements,
                system_prompt=system_prompt,
                diagram_type=diagram_type,
                detail_level=detail_level,
            )
        else:
            warnings.append("Vector Store not configured - generating without PlantUML documentation RAG")
            plantuml_code, call_tokens = await self._generate_without_rag(
                requirements=requirements,
                system_prompt=system_prompt,
                diagram_type=diagram_type,
                detail_level=detail_level,
            )
        llm_calls += 1
        tokens_used += call_tokens

        syntax_valid = self.plantuml.check_syntax(plantuml_code)
        refine_iterations = 0

        if not syntax_valid:
            plantuml_code, refine_iterations, syntax_valid = \
                await self.self_refine.refine_loop(
                    requirements=requirements,
                    plantuml_code=plantuml_code,
                    entity_registry=entity_registry.__dict__
                )
            llm_calls += refine_iterations * 2  # feedback + fix per iteration

            if not syntax_valid:
                warnings.append(f"Code may contain syntax errors after {refine_iterations} refinement attempts")

        try:
            image_base64 = self.plantuml.render_to_base64(plantuml_code)
        except Exception as e:
            warnings.append(f"Render warning: {str(e)}")
            image_base64 = ""  # Empty if render fails

        generation_time = int((time.perf_counter() - start_time) * 1000)

        # Extract lists for response
        entities = [e["canonical_name"] for e in entity_registry.entities]
        relationships = [
            f"{r['from']} → {r['to']} ({r.get('type', 'association')})"
            for r in entity_registry.relationships
        ]

        return GenerateResponse(
            plantuml_code=plantuml_code,
            diagram_image_base64=image_base64,
            syntax_valid=syntax_valid,
            entities_count=entity_registry.entity_count,
            relationships_count=entity_registry.relationship_count,
            refine_iterations=refine_iterations,
            generation_time_ms=generation_time,
            llm_calls_count=llm_calls,
            tokens_used=tokens_used,
            entities=entities,
            relationships=relationships,
            warnings=warnings
        )

    def _build_user_message(self, requirements: str, diagram_type: str, detail_level: str) -> str:
        """Build the user message for the generation LLM call."""
        if diagram_type == "use_case":
            diagram_label = "use case"
        elif detail_level == "design":
            diagram_label = "Design Model class"
        else:
            diagram_label = "Domain Model class"

        cardinality_note = " with cardinalities" if diagram_type == "class" else ""

        return f"""Generate a PlantUML {diagram_label} diagram for the following requirements.

REQUIREMENTS:
{requirements}

Remember:
1. Search the PlantUML documentation first
2. Use exact entity names from the registry
3. Include all relationships{cardinality_note}
4. Output only valid PlantUML code"""

    async def _generate_with_rag(
        self,
        requirements: str,
        system_prompt: str,
        diagram_type: str = "class",
        detail_level: str = "domain",
    ) -> tuple[str, int]:
        """Stage 3: Documentation-Grounded Generation using Responses API + file_search.

        Returns (plantuml_code, tokens_used).
        """
        user_message = self._build_user_message(requirements, diagram_type, detail_level)

        print(f"[RAG DEBUG] Calling Responses API WITH file_search")

        response = await self.client.responses.create(
            model=settings.OPENAI_MODEL,
            temperature=0.3,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            tools=[{
                "type": "file_search",
                "vector_store_ids": [self.vector_store_id],
                "max_num_results": settings.FILE_SEARCH_MAX_RESULTS
            }]
        )

        print(f"[RAG DEBUG] Response output blocks: {len(response.output)}")
        for i, block in enumerate(response.output):
            print(f"[RAG DEBUG] Block {i} type: {block.type}")

        tokens = self._extract_tokens(response)
        output_text = self._extract_response_text(response)
        return self._extract_plantuml(output_text), tokens

    async def _generate_without_rag(
        self,
        requirements: str,
        system_prompt: str,
        diagram_type: str = "class",
        detail_level: str = "domain",
    ) -> tuple[str, int]:
        """Fallback generation without RAG.

        Returns (plantuml_code, tokens_used).
        """
        user_message = self._build_user_message(requirements, diagram_type, detail_level)

        print(f"[RAG DEBUG] Calling chat.completions WITHOUT RAG")

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

        tokens = 0
        if hasattr(response, 'usage') and response.usage:
            tokens = response.usage.total_tokens or 0
        output_text = response.choices[0].message.content
        return self._extract_plantuml(output_text), tokens

    def _extract_tokens(self, response) -> int:
        """Extract total token usage from Responses API output."""
        try:
            if hasattr(response, 'usage') and response.usage:
                return response.usage.total_tokens or 0
        except Exception:
            pass
        return 0

    def _extract_response_text(self, response) -> str:
        """Extract text from Responses API output."""
        # Responses API returns output as list of content blocks
        if hasattr(response, 'output'):
            for block in response.output:
                if hasattr(block, 'content'):
                    for content in block.content:
                        if hasattr(content, 'text'):
                            return content.text

        if hasattr(response, 'output_text'):
            return response.output_text

        return str(response)

    def _extract_plantuml(self, text: str) -> str:
        """Extract PlantUML code from text."""
        # Remove markdown code blocks
        text = re.sub(r'```plantuml\s*', '', text)
        text = re.sub(r'```\s*', '', text)

        # Look for @startuml ... @enduml
        match = re.search(r'(@startuml.*?@enduml)', text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)

        # If no tags, wrap text
        text = text.strip()
        if not text.lower().startswith("@startuml"):
            text = "@startuml\n" + text
        if not text.lower().endswith("@enduml"):
            text = text + "\n@enduml"

        return text
