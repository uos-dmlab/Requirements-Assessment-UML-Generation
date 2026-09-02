# Requirements Assessment and UML Generation

Two-stage system that assesses natural-language software requirements for quality,
then generates UML Class and Use Case diagrams under explicit modeling constraints.

**Live system:** [umlreq.com](https://umlreq.com)

Most LLM-based UML generators translate requirements directly into diagrams. When the
requirements are vague or incomplete, the model fills the gaps from its training data,
which produces diagrams that look plausible but do not represent what was actually
specified. This system separates the two concerns: requirements are scored and returned
to the user with actionable hints first, and generation runs only afterwards, constrained
by established modeling methodology.

## How it works

**Stage 1 — Requirements assessment.** Three layers score the text across eight quality
dimensions aligned with ISO/IEC/IEEE 29148:

| Layer | Technique | Dimensions |
|---|---|---|
| Lexical | Regular expressions and word lists, fully deterministic | Specificity, Completeness Markers |
| Structural | spaCy dependency parsing (`en_core_web_sm`) | Clarity, Structure, Readability |
| Semantic | GPT-4o, temperature 0, JSON-constrained output | Modelability, Completeness, Consistency |

The overall score is `0.6 x deterministic + 0.4 x semantic`, on a 0-100 scale. Assessment
is **read-only**: it never rewrites the input. The user decides whether to revise.

**Stage 2 — Constrained generation.** GPT-4o generates PlantUML under methodology-aware
prompts — Larman's mapmaker principle for class diagrams, Cockburn's goal-level taxonomy
and Jacobson's actor classification for use case diagrams. Retrieval-Augmented Generation
from the official PlantUML Language Reference Guide supplies notation context. Output is
syntax-checked with `plantuml.jar -syntax`, repaired if needed, and rendered server-side.

## Repository layout

```
backend/      FastAPI service: assessment pipeline, generation pipeline, persistence
frontend/     React + Vite single-page application, served by nginx
artifacts/    Test cases, ground truth, system prompts, evaluation protocol, results
paper/        Citation and DOI for the published conference paper
scripts/      Helper scripts (fetch third-party resources)
```

## Quick start

Requires Docker and an OpenAI API key.

```bash
git clone https://github.com/uos-dmlab/Requirements-Assessment-UML-Generation.git
cd Requirements-Assessment-UML-Generation

cp backend/.env.example backend/.env
# edit backend/.env: set OPENAI_API_KEY and SECRET_KEY at minimum
#   SECRET_KEY can be generated with: openssl rand -hex 32

./scripts/fetch-resources.sh     # downloads plantuml.jar and the PlantUML reference guide
docker compose up --build
```

Frontend on <http://localhost:3000>, API and OpenAPI docs on <http://localhost:8000/docs>.

RAG requires a one-time vector store setup, which uploads the PlantUML reference guide to
the OpenAI Files API and returns an id for `PLANTUML_VECTOR_STORE_ID`:

```bash
docker compose exec backend python scripts/setup_vector_store.py
```

Without that id the system falls back to generation without retrieval, which the ablation
study shows costs little for the diagram types evaluated here.

## Running without Docker

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env          # then edit
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend/app
npm install
npm run dev
```

PostgreSQL 16 and Java (for `plantuml.jar`) must be available locally.

## Evaluation artifacts

`artifacts/` holds everything needed to check the numbers reported in the paper:

| File | Contents |
|---|---|
| `test-cases.md` | The 15 requirement texts (TC01-TC15) |
| `ground-truth.json` | Expected classes, attributes, relationships, actors, use cases |
| `system-prompts.md` | Generation and assessment prompts as deployed |
| `evaluation-protocol.md` | Scoring procedure and criteria |
| `rag-config.md` | Vector store configuration and chunking parameters |
| `results/` | Per-case outputs, rendered diagrams, multi-run data |

Ground truth follows Larman's mapmaker principle: an element is included only when the
requirements state it. `Customer` is ground truth when the text says customers place
orders; `Customer.customerId` is a hallucination unless the text says the id is recorded.

## Configuration

Full list in `backend/.env.example`. The settings that affect results:

| Variable | Default | Meaning |
|---|---|---|
| `OPENAI_MODEL` | `gpt-4o` | Deployment pins `gpt-4o-2024-11-20` |
| `PLANTUML_VECTOR_STORE_ID` | — | Vector store for RAG; empty disables retrieval |
| `FILE_SEARCH_MAX_RESULTS` | `15` | Chunks retrieved per generation |
| `SELF_REFINE_MAX_ITERATIONS` | `4` | Syntax repair attempts before failing |
| `DETERMINISTIC_WEIGHT` / `SEMANTIC_WEIGHT` | `0.60` / `0.40` | Score aggregation weights |
| `DETERMINISTIC_FLOOR` / `TOTAL_THRESHOLD` | `40.0` / `50.0` | Gates below which generation is blocked |

Generation runs at temperature 0.3; entity extraction, the syntax repair loop and the
semantic assessment layer run at temperature 0.

## Paper

Published at IEEE/ACIS SERA 2026. Citation and DOI in [`paper/`](paper/).

## License

Code released under the MIT License — see [LICENSE](LICENSE). The PlantUML Language
Reference Guide and `plantuml.jar` are third-party artifacts fetched at setup time and
carry their own licenses; they are not redistributed here.

## Acknowledgements

Data Mining Laboratory, Department of Electrical and Computer Engineering,
University of Seoul.
