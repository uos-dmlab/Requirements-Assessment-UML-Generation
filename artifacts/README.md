## Automated Requirements Assessment and UML Generation from Natural Language

This repository accompanies the paper *"Automated Requirements Assessment and UML Generation from Natural Language"* accepted at **IEEE SERA 2026**. It contains all test cases, system prompts, evaluation protocols, generated outputs, and multi-run data needed to verify the paper's claims.

**Authors:** Amir Zhumagaliyev, Han-joon Kim
**Affiliation:** Dept. of Electrical and Computer Engineering, University of Seoul
**Deployed system:** [umlreq.com](https://umlreq.com)

### Repository Contents

| File/Directory | Description |
|---|---|
| `test-cases.md` | All 15 requirement specifications (10 class diagram, 5 use case) |
| `system-prompts.md` | Generation prompts for class and use case diagrams with design rationale |
| `evaluation-protocol.md` | SEQUAL rubrics, anti-pattern checklist, hallucination counting protocol |
| `ground-truth.json` | Expected elements per test case (derived using mapmaker principle) |
| `rag-config.md` | Vector store and retrieval parameters |
| `results/` | All generated outputs with PlantUML code and rendered diagrams |

### Results Directory Structure

| Path | Description |
|---|---|
| `results/class-diagrams/umlreq-system.md` | UMLReq system's class diagram outputs (PlantUML code + images) |
| `results/class-diagrams/chatgpt-dalle.md` | ChatGPT DALL-E class diagram outputs (images only) |
| `results/class-diagrams/chatgpt-mermaid.md` | ChatGPT Mermaid class diagram outputs (images only) |
| `results/class-diagrams/chatgpt-plantuml.md` | ChatGPT PlantUML class diagram outputs (code + images) |
| `results/use-case-diagrams/umlreq-system.md` | UMLReq system's use case diagram outputs (code + images) |
| `results/use-case-diagrams/chatgpt-dalle.md` | ChatGPT DALL-E use case outputs (images only) |
| `results/use-case-diagrams/chatgpt-mermaid.md` | Mermaid use case results (Not Supported) |
| `results/use-case-diagrams/chatgpt-plantuml.md` | ChatGPT PlantUML use case outputs (code + images) |
| `results/multi-run/multi-run-data.md` | 75 generation runs (15 TCs × 5 runs) with consistency analysis |
| `results/images/` | All extracted PNG diagrams organized by system and test case |

### Evaluation Setup

| | UMLReq System | ChatGPT Baselines |
|---|---|---|
| Model | GPT-4o (gpt-4o-2024-11-20) | GPT-5.2 Thinking |
| Interface | OpenAI API | ChatGPT web (chatgpt.com) |
| Parameters | temperature=0.3, top_p=1.0 | Default settings |
| Generation approaches | PlantUML via RAG + methodology-aware prompts | DALL-E (image), Mermaid (text), PlantUML (text) |

### Key Results (Table I)

| Metric | Ours | GPT-PlantUML | GPT-Mermaid | DALL-E |
|--------|------|-------------|-------------|--------|
| Class Overall | 100% | 87% | 85% | 55% |
| UC Overall | 96% | 72% | N/S | 74% |
| Req. Fidelity | 98% | 72% | 58% | 55% |
| Hallucinations | 0 | 11 | 8 | 5 |
| Duplications | 0 | 0 | 0 | 12 |
| Anti-Patterns | 1 | 13 | N/S | 3 |

Overall Usability is computed at the subcriteria level: 3 SEQUAL subcriteria × 10 class diagram cases = 30 total (our system: 30/30); 5 anti-pattern subcriteria × 5 use case cases = 25 total (our system: 24/25).

### Multi-Run Stability (75 runs: 15 TCs × 5 runs)

| Metric | Value | 95% Wilson CI |
|--------|-------|---------------|
| Overall structural consistency | 93.3% | [70%, 99%] |
| Class diagram consistency | 90% (9/10) | [60%, 98%] |
| Use case diagram consistency | 100% (5/5) | [57%, 100%] |
| Hallucination rate | 0% (0/75) | [0%, 4%] |

Cliff's delta effect sizes (per Kitchenham & Madeyski, 2024):
- Hallucination reduction: δ = 0.40 (Medium)
- Anti-pattern reduction: δ = 0.68 (Large)

### Reproducing Results

1. Use test case requirements from `test-cases.md` as input
2. Apply system prompts from `system-prompts.md` with GPT-4o API
3. Configure RAG per `rag-config.md`
4. Evaluate outputs against ground truth in `ground-truth.json`
5. Apply evaluation protocol from `evaluation-protocol.md`

### Citation

If you use this replication package, please cite:

> A. Zhumagaliyev and H.-J. Kim, "Automated Requirements Assessment and UML Generation from Natural Language," in *Proc. IEEE/ACIS 24th International Conference on Software Engineering Research, Management and Applications (SERA)*, 2026.

