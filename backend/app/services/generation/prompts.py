"""
Prompts for PlantUML diagram generation.
Uses SCoT (Structured Chain-of-Thought) from Research Report.
"""


def build_generation_prompt(entity_registry: dict, detail_level: str = "domain") -> str:
    """
    Builds system prompt for generation with entity registry context.

    SCoT (Structured Chain-of-Thought) improves pass@1 by 13.79%
    compared to regular chain-of-thought (ACM TOSEM 2024).

    Args:
        entity_registry: Extracted entities and relationships dict
        detail_level: "domain" (no methods/visibility) or "design" (with methods/visibility)
    """
    is_design = detail_level == "design"

    # Format entities
    entities_str = ""
    for e in entity_registry.get("entities", []):
        attrs = ", ".join(e.get("attributes", [])[:5])  # Max 5 for brevity
        entities_str += f"  - {e['canonical_name']}"
        if attrs:
            entities_str += f" [attrs: {attrs}]"
        if is_design:
            methods = ", ".join(e.get("methods", [])[:3])   # Max 3
            if methods:
                entities_str += f" [methods: {methods}]"
        entities_str += "\n"

    if not entities_str:
        entities_str = "  (no entities extracted yet — extract from requirements)\n"

    # Format relationships
    relationships_str = ""
    for r in entity_registry.get("relationships", []):
        rel_type = r.get("type", "association")
        label = r.get("label", "")
        card_from = r.get("cardinality_from", "1")
        card_to = r.get("cardinality_to", "*")
        relationships_str += f"  - {r['from']} → {r['to']} ({rel_type}"
        if label:
            relationships_str += f", '{label}'"
        relationships_str += f", {card_from}..{card_to})\n"

    if not relationships_str:
        relationships_str = "  (no relationships extracted yet — infer from requirements)\n"

    # Detail-level-specific sections
    if is_design:
        model_type = "Design Model"
        model_rule = "5. Include **methods** and **visibility modifiers** (+, -, #)"
        step2 = """### STEP 2 — ENTITY MAPPING (sequence)
For each entity in the registry:
```
→ Define class with name from canonical_name
→ Add attributes with visibility and types (e.g. +name: String, -id: int)
→ Add methods with visibility and parentheses (e.g. +login(), -validate())
```"""
        output_example = """```
@startuml

class ClassName {{
  +attribute: Type
  -privateAttr: Type
  +method(): ReturnType
}}

ClassA "1" -- "*" ClassB : relationship

@enduml
```"""
        syntax_extra = """
- Visibility: + public, - private, # protected, ~ package
- Static: {{static}} or underline
- Abstract: {{abstract}} or italics"""
    else:
        model_type = "Domain Model"
        model_rule = "5. Do **NOT** include methods or visibility modifiers (+, -, #) — domain model only"
        step2 = """### STEP 2 — ENTITY MAPPING (sequence)
For each entity in the registry:
```
→ Define class with name from canonical_name
→ Add attributes with types (use : notation, NO visibility prefixes)
→ Do NOT add methods — this is a Domain Model
```"""
        output_example = """```
@startuml

class ClassName {{
  attribute: Type
  anotherAttr: Type
}}

ClassA "1" -- "*" ClassB : relationship

@enduml
```"""
        syntax_extra = ""

    return f"""You are an expert PlantUML {model_type} class diagram generator.
You have access to the official PlantUML Reference Guide through file_search — USE IT.

## CRITICAL RULES

1. **ALWAYS search the PlantUML documentation** before generating code
2. Use **ONLY** syntax patterns found in the reference guide
3. Output **MUST** compile without errors via `plantuml.jar -syntax`
4. Use the **EXACT** entity names from the ENTITY REGISTRY below
{model_rule}

## ENTITY REGISTRY (use these exact names)

{entities_str}
## DISCOVERED RELATIONSHIPS

{relationships_str}
## ANALYSIS FRAMEWORK (SCoT — execute step by step)

### STEP 1 — SEARCH DOCUMENTATION
Before writing any code, search the PlantUML Reference for:
- Class definition syntax
- Relationship arrow syntax (--|>, --*, --o, --)
- Cardinality/multiplicity syntax
- Attribute notation

{step2}

### STEP 3 — RELATIONSHIP MAPPING (branch)
For each relationship:
```
IF type == "inheritance" → Child --|> Parent
IF type == "composition" → Whole *-- Part  (or Whole *--> Part)
IF type == "aggregation" → Whole o-- Part  (or Whole o--> Part)
IF type == "association" → A -- B  (or A --> B for directed)
```

### STEP 4 — CARDINALITY (loop)
For each association/aggregation/composition:
```
→ Add multiplicity using quotes: "1" -- "*"
→ PlantUML syntax: A "1" -- "*" B : label
```

### STEP 5 — OUTPUT
```
→ Valid PlantUML between @startuml and @enduml
→ Include ALL entities from registry
→ Include ALL relationships with cardinalities
→ NO notes, NO comments, ONLY diagram code
```

## OUTPUT FORMAT

Return ONLY the PlantUML code. No explanations, no markdown.

{output_example}

## PLANTUML SYNTAX REMINDERS (from documentation)
{syntax_extra}
- Arrows: --|> inheritance, *-- composition, o-- aggregation, -- association
- Direction: --> or <-- for directed, -- for bidirectional
- Cardinality: "1" "*" "0..1" "1..*" placed before/after arrow
- Labels: A -- B : label"""


def build_usecase_generation_prompt(entity_registry: dict) -> str:
    """
    Builds system prompt for use case diagram generation with entity registry context.

    SCoT (Structured Chain-of-Thought) adapted for use case diagrams.
    """

    # Format actors and use cases
    actors_str = ""
    usecases_str = ""
    for e in entity_registry.get("entities", []):
        actor_type = e.get("actor_type", "")
        if actor_type in ("human", "system"):
            actors_str += f"  - {e['canonical_name']} ({actor_type})\n"
        elif actor_type == "use_case":
            aliases = ", ".join(e.get("aliases", [])[:3])
            usecases_str += f"  - {e['canonical_name']}"
            if aliases:
                usecases_str += f" [aliases: {aliases}]"
            usecases_str += "\n"

    if not actors_str:
        actors_str = "  (no actors extracted yet — extract from requirements)\n"
    if not usecases_str:
        usecases_str = "  (no use cases extracted yet — extract from requirements)\n"

    # Format relationships
    relationships_str = ""
    for r in entity_registry.get("relationships", []):
        rel_type = r.get("type", "association")
        label = r.get("label", "")
        relationships_str += f"  - {r['from']} -> {r['to']} ({rel_type}"
        if label:
            relationships_str += f", '{label}'"
        relationships_str += ")\n"

    if not relationships_str:
        relationships_str = "  (no relationships extracted yet — infer from requirements)\n"

    return f"""You are an expert PlantUML use case diagram generator.
You have access to the official PlantUML Reference Guide through file_search — USE IT.

## CRITICAL RULES

1. **ALWAYS search the PlantUML documentation** before generating code
2. Use **ONLY** syntax patterns found in the reference guide
3. Output **MUST** compile without errors via `plantuml.jar -syntax`
4. Use the **EXACT** entity names from the ENTITY REGISTRY below

## ACTORS

{actors_str}
## USE CASES

{usecases_str}
## DISCOVERED RELATIONSHIPS

{relationships_str}
## ANALYSIS FRAMEWORK (SCoT — execute step by step)

### STEP 1 — SEARCH DOCUMENTATION
Before writing any code, search the PlantUML Reference for:
- Use case diagram syntax
- Actor definition syntax
- Use case definition syntax
- Relationship arrows: -->, ..>, --|>
- Rectangle (system boundary) syntax

### STEP 2 — ACTOR DEFINITION (sequence)
For each actor in the registry:
```
-> Define actor: actor "Name" as alias
-> Human actors use default actor icon
-> System actors use :SystemName: or actor "SystemName" <<system>>
```

### STEP 3 — USE CASE DEFINITION (sequence)
For each use case in the registry:
```
-> Define use case: usecase "Action Name" as UC_alias
-> Group related use cases inside rectangle (system boundary)
```

### STEP 4 — RELATIONSHIP MAPPING (branch)
For each relationship:
```
IF type == "association" -> Actor --> UseCase
IF type == "include" -> BaseUC ..> IncludedUC : <<include>>
IF type == "extend" -> ExtendingUC ..> BaseUC : <<extend>>
IF type == "generalization" -> Child --|> Parent
```

### STEP 5 — OUTPUT
```
-> Valid PlantUML between @startuml and @enduml
-> Include ALL actors from registry
-> Include ALL use cases from registry
-> Include ALL relationships
-> Use rectangle for system boundary where appropriate
-> NO notes, NO comments, ONLY diagram code
```

## OUTPUT FORMAT

Return ONLY the PlantUML code. No explanations, no markdown.

```
@startuml

left to right direction

actor Customer
actor Admin

rectangle "System" {{
  usecase "Place Order" as UC1
  usecase "Process Payment" as UC2
  usecase "View Report" as UC3
}}

Customer --> UC1
UC1 ..> UC2 : <<include>>
Admin --> UC3

@enduml
```

## PLANTUML USE CASE SYNTAX REMINDERS (from documentation)

- Actor: actor "Name" or :Name:
- Use case: usecase "Name" as alias
- System boundary: rectangle "System Name" {{ ... }}
- Association: Actor --> UseCase (solid arrow)
- Include: BaseUC ..> IncludedUC : <<include>> (dashed arrow)
- Extend: ExtendingUC ..> BaseUC : <<extend>> (dashed arrow)
- Generalization: Child --|> Parent (solid triangle arrow)
- Direction: left to right direction (or top to bottom direction)"""


REFINE_FEEDBACK_PROMPT = """You are a PlantUML syntax expert analyzing code that failed validation.

## YOUR TASK

Analyze the given PlantUML code and its syntax errors.
Identify EXACTLY what is wrong and why.

## OUTPUT FORMAT

List specific issues:
1. Line number (if identifiable)
2. What's wrong (incorrect token, missing element, invalid syntax)
3. What it should be (correct syntax from PlantUML spec)

Be concise and specific. No general advice — only concrete fixes."""


REFINE_FIX_PROMPT = """You are a PlantUML code fixer.

## YOUR TASK

Fix the given PlantUML code based on the feedback provided.

## RULES

1. Fix ONLY the issues mentioned in feedback
2. Preserve all correct parts of the code
3. Use EXACT syntax from PlantUML documentation
4. Output ONLY the corrected code between @startuml and @enduml
5. NO explanations, NO markdown — just the code

## OUTPUT

Return ONLY the fixed PlantUML code."""
