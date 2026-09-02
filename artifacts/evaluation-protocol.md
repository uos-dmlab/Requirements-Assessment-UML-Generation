# Evaluation Protocol

## Overview

Each generated diagram was evaluated by a single evaluator following the protocol below. We acknowledge single-evaluator limitation; future work includes independent second evaluation with Cohen's κ.

## Step 1: Element Enumeration

For each test case and each system output:

1. List all classes/actors in the generated diagram
2. List all attributes per class
3. List all relationships with multiplicities
4. Compare against ground truth (see `ground-truth.json`)

## Step 2: Hallucination Detection

For each generated element (class, attribute, relationship, actor, use case):

- **Element present in diagram AND in requirements** → Correct (true positive)
- **Element present in diagram but NOT in requirements** → **Hallucination** (false positive)
- **Element in requirements but NOT in diagram** → **Missing** (false negative, reduces recall)
- **Element clearly implied by requirements** → NOT hallucination (e.g., "borrows books" implies a Borrow relationship)

Count and list each hallucinated element with its source class/diagram.

## Step 3: Class Diagram Assessment (SEQUAL Framework)

Each class diagram assessed on three dimensions:

### Syntactic Validity
- Does the PlantUML code compile without errors?
- Does it render into a valid visual diagram?
- **Pass**: Code compiles and renders correctly

### Semantic Validity
- Do classes faithfully represent domain concepts stated in requirements?
- Do attributes match what requirements specify?
- Do relationships accurately reflect stated connections and multiplicities?
- **Pass**: All elements traceable to requirements, no critical misrepresentations

### Pragmatic Quality
- Is the diagram useful for understanding the domain?
- Is the layout clear and readable?
- Does it follow standard UML conventions?
- **Pass**: A stakeholder could use this diagram to verify their requirements

**Overall pass criteria**: All three SEQUAL dimensions satisfied without critical errors.

SEQUAL dimensions are operationalized as binary pass/fail per subcriterion, chosen for evaluation tractability with a single evaluator: binary criteria minimize subjective judgment.

## Step 4: Use Case Diagram Assessment

Each use case diagram checked against established methodology:

### Cockburn's Goal-Level Compliance
- Are use cases at appropriate abstraction levels (user goals)?
- Are they NOT implementation steps (function decomposition)?
- Example violation: "Validate Input" or "Query Database" instead of "Place Order"

### Jacobson's Actor Classification
- Are all actors external to the system?
- Are internal components NOT modeled as actors?
- Example violation: "Database" or "Authentication Service" as stick figures

### Anti-Pattern Checklist

- [ ] **Internal system as external actor**: System component modeled as stick figure without `<<system>>` stereotype (e.g., "Database" as actor)
- [ ] **Function decomposition**: Use cases representing implementation steps rather than user goals (e.g., "ValidateTransaction", "UpdateAccountBalances")
- [ ] **Excessive includes**: More than 3 `<<include>>` relationships suggesting procedural thinking
- [ ] **Missing system boundary**: No rectangle element enclosing use cases

**Pass criteria**: Zero anti-pattern violations AND all requirements-stated actors and goals correctly represented.

## Step 5: Overall Usability

Overall Usability is computed at the subcriteria level:

- **Class diagrams**: 3 SEQUAL subcriteria × 10 class diagram cases = 30 total subcriteria
- **Use case diagrams**: 5 anti-pattern subcriteria × 5 use case cases = 25 total subcriteria

A diagram passes Overall Usability if:

- **Class diagrams**: Passes all three SEQUAL dimensions without critical errors
- **Use case diagrams**: Zero anti-pattern violations and correct representation of all actors/goals

## Step 6: Precision / Recall / F1 Computation

For class diagrams, computed per element type:

- **Classes**: P = correct_classes / predicted_classes, R = correct_classes / expected_classes
- **Attributes**: P = correct_attrs / predicted_attrs, R = correct_attrs / expected_attrs
- **Relationships**: P = correct_rels / predicted_rels, R = correct_rels / expected_rels
- F1 = 2 × P × R / (P + R)

Ground truth derived from requirements using mapmaker principle (only explicitly stated elements).

## Statistical Methods

### Wilson Score Confidence Intervals
Used for proportions with small samples (n=10 for class, n=5 for use case). Wilson CIs have better coverage properties than Wald intervals for small n and extreme p.

Reported intervals in the paper:
- Overall multi-run consistency: 93.3%, 95% Wilson CI [70%, 99%]
- Class diagram consistency: 90% (9/10), 95% Wilson CI [60%, 98%]
- Use case diagram consistency: 100% (5/5), 95% Wilson CI [57%, 100%]
- Hallucination rate: 0% (0/75), 95% Wilson CI [0%, 4%]

### Rule of Three
For zero-event rates: when 0 events observed in n trials, 95% CI upper bound ≈ 3/n.

Applied to: hallucination rate across 75 multi-run generations (0 hallucinations in 75 runs → upper bound ≈ 3/75 = 4%).

### Cliff's Delta Effect Size
Non-parametric effect size for paired comparisons (per Kitchenham & Madeyski, 2024):

| \|δ\| Range | Effect Size |
|------------|-------------|
| < 0.147 | Negligible |
| 0.147 – 0.330 | Small |
| 0.330 – 0.474 | Medium |
| ≥ 0.474 | Large |

Results from paper:
- Hallucination reduction (class diagrams): δ = 0.40 (Medium)
- Anti-pattern reduction (use case diagrams): δ = 0.68 (Large)
