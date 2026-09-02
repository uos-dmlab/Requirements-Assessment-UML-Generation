# UMLReq - UML Requirements Processing System

A FastAPI application that validates software requirements and generates UML class diagrams using AI-powered 3-layer analysis.

## Features

- **3-Layer Requirements Validation**
  - Layer 1: Lexical Analysis (dictionaries, regex) — instant
  - Layer 2: Structural Analysis (spaCy NLP) — ~100ms
  - Layer 3: Semantic Analysis (OpenAI GPT) — ~3s

- **AI-Powered Diagram Generation**
  - Entity extraction with consistent naming
  - RAG with PlantUML documentation
  - SELF-REFINE loop for syntax correction
  - PNG rendering with PlantUML

- **Complete Authentication System**
  - JWT with HttpOnly refresh tokens
  - Google OAuth integration
  - Password reset flow

- **Project Management**
  - Projects with requirements drafts
  - Version conflict handling (optimistic locking)
  - Validation/Generation runs with progress tracking

## Architecture

```
app/
├── api/endpoints/           # API endpoints
│   ├── auth.py              # Authentication
│   ├── projects.py          # Project CRUD
│   ├── runs.py              # Validation/Generation runs
│   ├── artifacts.py         # Diagram downloads
│   ├── account.py           # Account settings
│   ├── validation.py        # Requirements validation
│   └── generation.py        # Diagram generation
├── core/                    # Configuration and security
├── crud/                    # Database operations
├── db/models/               # SQLAlchemy models
├── schemas/                 # Pydantic models
└── services/
    ├── validation/          # 3-layer validation
    │   ├── lexical_analyzer.py
    │   ├── structural_analyzer.py
    │   └── semantic_analyzer.py
    └── generation/          # Diagram generation
        ├── entity_extractor.py
        ├── generation_service.py
        └── plantuml_service.py
```

## Installation

### 1. Clone and setup environment

```bash
git clone <repository-url>
cd umlreq
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Install NLP model

```bash
python -m spacy download en_core_web_sm
```

### 3. Setup PlantUML

```bash
# Download PlantUML JAR
curl -L -o resources/plantuml.jar \
  https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar

# Install Java (if needed)
sudo apt install default-jre-headless
```

### 4. Setup OpenAI Vector Store (for RAG)

```bash
# Download PlantUML documentation
curl -L -o resources/PlantUML_Language_Reference_Guide_en.pdf \
  https://pdf.plantuml.net/PlantUML_Language_Reference_Guide_en.pdf

# Run setup script
python scripts/setup_vector_store.py
```

### 5. Configure environment

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/umlreq

# Security
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
PLANTUML_VECTOR_STORE_ID=vs_...  # From setup script

# Google OAuth (optional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=...

# Frontend
FRONTEND_URL=http://localhost:5173
```

### 6. Run migrations and start

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

## API Endpoints

All endpoints under `/api/v1` prefix.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register new user |
| POST | `/auth/signin` | Login (returns access token, sets refresh cookie) |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout (clears refresh cookie) |
| GET | `/auth/me` | Get current user |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Reset password with token |
| GET | `/auth/google` | Start Google OAuth flow |
| GET | `/auth/google/callback` | Google OAuth callback |

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects` | List user's projects |
| POST | `/projects` | Create project |
| GET | `/projects/{id}` | Get project details |
| PUT | `/projects/{id}` | Update project |
| DELETE | `/projects/{id}` | Delete project |
| GET | `/projects/{id}/requirements` | Get requirements draft |
| PUT | `/projects/{id}/requirements` | Update requirements (with version check) |

### Validation & Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/validate` | Validate requirements (3-layer analysis) |
| POST | `/generate` | Generate UML diagram |

### Runs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/projects/{id}/runs` | Start validation/generation run |
| GET | `/projects/{id}/runs` | List project runs |
| GET | `/runs/{id}` | Get run status |
| GET | `/runs/{id}/result` | Get run result |

### Account

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/account/password/change` | Change password |
| POST | `/account/delete` | Delete account |

### Artifacts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/artifacts/{id}` | Download artifact (diagram image) |

## Usage Examples

### Validate Requirements

```bash
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "The system has Users who place Orders. Each Order contains OrderItems."
  }'
```

Response includes:
- 8 quality metrics (0-10 scale)
- `can_generate: true/false`
- Issues sorted by severity
- Detected entities and relationships

### Generate Diagram

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Users place Orders. Orders contain OrderItems. OrderItems reference Products."
  }'
```

Response includes:
- `plantuml_code`: Generated PlantUML source
- `diagram_image_base64`: PNG image in base64
- `syntax_valid`: Whether code passed validation
- `entities`, `relationships`: Extracted model elements

## Development

### Code Formatting

```bash
black app/
isort app/
```

### Database Migrations

```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Docker

```bash
docker-compose up --build
```

## License

MIT License
