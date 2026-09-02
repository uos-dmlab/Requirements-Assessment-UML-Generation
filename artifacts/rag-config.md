# RAG Configuration

## Vector Store

- **Provider**: OpenAI file_search API
- **Embedding Model**: text-embedding-3-large (default)
- **Source Document**: PlantUML Language Reference Guide (~200 pages)
- **Chunking**: 1200-token segments with 400-token overlap

## Retrieval

- **Max chunks retrieved**: 15
- **Similarity**: Semantic similarity (cosine) via OpenAI embeddings
- **Context**: Retrieved chunks provide syntax patterns, relationship notations, and styling conventions

## Query Construction

At generation time, the system constructs a retrieval query from the input requirements and diagram type. Retrieved PlantUML documentation chunks are injected into the generation prompt as grounding context.

## Purpose

RAG grounds generation in official PlantUML documentation. Ablation study (Section IV-E of paper) showed minimal impact for established diagram types (class, use case) where GPT-4o already has parametric knowledge. Primary value is future-proofing for newly introduced PlantUML constructs (C4 architecture, JSON/YAML diagrams) outside model training data.

## Ablation Results

- 7 of 10 class diagram cases (70%) produced structurally similar diagrams with and without RAG
- Hallucination rate remained 0% in both conditions
- **Conclusion**: Prompt engineering (Larman's mapmaker principle) is the primary quality driver; RAG provides future-proofing
