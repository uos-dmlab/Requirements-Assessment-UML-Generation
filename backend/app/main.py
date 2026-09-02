from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.api.endpoints import auth, projects, runs, artifacts, account, validation, generation, stats, ablation
from app.core.config import settings
from app.core.error_handlers import (
    AuthHTTPException,
    auth_exception_handler,
    validation_exception_handler,
)

app = FastAPI(
    title="UMLReq API",
    description="API for UML Requirements Management",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL] + settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for unified error format
app.add_exception_handler(AuthHTTPException, auth_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# API v1 routes
API_V1_PREFIX = "/api/v1"

app.include_router(
    auth.router,
    prefix=f"{API_V1_PREFIX}/auth",
    tags=["auth"]
)
app.include_router(
    projects.router,
    prefix=f"{API_V1_PREFIX}/projects",
    tags=["projects"]
)
app.include_router(
    runs.router,
    prefix=f"{API_V1_PREFIX}",
    tags=["runs"]
)
app.include_router(
    artifacts.router,
    prefix=f"{API_V1_PREFIX}/artifacts",
    tags=["artifacts"]
)
app.include_router(
    account.router,
    prefix=f"{API_V1_PREFIX}/account",
    tags=["account"]
)
app.include_router(
    validation.router,
    prefix=f"{API_V1_PREFIX}",
    tags=["validation"]
)
app.include_router(
    generation.router,
    prefix=f"{API_V1_PREFIX}",
    tags=["generation"]
)
app.include_router(
    stats.router,
    prefix=f"{API_V1_PREFIX}",
    tags=["stats"]
)
app.include_router(
    ablation.router,
    prefix=f"{API_V1_PREFIX}",
    tags=["ablation"]
)


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy"}
