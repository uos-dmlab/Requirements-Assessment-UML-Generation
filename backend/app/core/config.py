"""
Application configuration management with validation and environment support.
"""

import secrets
from typing import Optional, List
from pydantic import field_validator, computed_field, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with validation and environment variable support.

    All settings can be configured via environment variables or .env file.
    """

    # Application Settings
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment name (development/staging/production)")

    # Database Configuration
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: int = Field(default=5432, description="Database port", ge=1, le=65535)
    DB_USER: str = Field(default="postgres", description="Database username")
    DB_PASS: str = Field(default="postgres", description="Database password")
    DB_NAME: str = Field(default="umlreq", description="Database name")

    # Alternative: Full database URL (overrides individual settings if provided)
    DATABASE_URL: Optional[str] = Field(default=None, description="Full database connection URL")

    # Security & Authentication
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT token generation"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, description="Access token expiration in minutes", ge=1)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration in days", ge=1)
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Password reset token expiration in minutes", ge=1)

    # Cookie Settings
    COOKIE_SECURE: bool = Field(default=True, description="Set Secure flag on cookies (disable for local dev)")
    COOKIE_SAMESITE: str = Field(default="lax", description="SameSite cookie attribute (lax/strict/none)")

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, description="Google OAuth client ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None, description="Google OAuth client secret")
    GOOGLE_REDIRECT_URI: Optional[str] = Field(default=None, description="Google OAuth redirect URI")
    FRONTEND_AUTH_CALLBACK_URL: str = Field(default="http://localhost:5173/auth/callback", description="Frontend auth callback URL")

    # CORS Configuration
    FRONTEND_URL: str = Field(default="http://localhost:5173", description="Frontend application URL")
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins"
    )
    ALLOWED_HOSTS: str = Field(default="*", description="Comma-separated list of allowed hosts")

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key (required)")
    OPENAI_MODEL: str = Field(default="gpt-4o-2024-11-20", description="OpenAI model for validation/generation")
    ASSISTANT_ID: Optional[str] = Field(default=None, description="OpenAI Assistant ID")

    # Validation Thresholds
    DETERMINISTIC_WEIGHT: float = Field(default=0.60, description="Weight for deterministic (L1+L2) score", ge=0.0, le=1.0)
    SEMANTIC_WEIGHT: float = Field(default=0.40, description="Weight for semantic (L3) score", ge=0.0, le=1.0)
    DETERMINISTIC_FLOOR: float = Field(default=40.0, description="Minimum deterministic score to allow generation", ge=0.0, le=100.0)
    TOTAL_THRESHOLD: float = Field(default=50.0, description="Minimum total score to allow generation", ge=0.0, le=100.0)

    # Vector Store for RAG (generation)
    PLANTUML_VECTOR_STORE_ID: Optional[str] = Field(default=None, description="OpenAI Vector Store ID for PlantUML docs")

    # Generation settings
    SELF_REFINE_MAX_ITERATIONS: int = Field(default=4, description="Max SELF-REFINE iterations", ge=1, le=10)
    FILE_SEARCH_MAX_RESULTS: int = Field(default=15, description="Max results from file_search", ge=1, le=50)

    # PlantUML
    PLANTUML_JAR_PATH: str = Field(default="resources/plantuml.jar", description="Path to plantuml.jar")

    # Redis Configuration (for caching)
    REDIS_URL: Optional[str] = Field(default=None, description="Redis connection URL")
    REDIS_PORT: int = Field(default=6379, description="Redis port", ge=1, le=65535)
    CACHE_ENABLED: bool = Field(default=False, description="Enable caching")
    CACHE_TTL: int = Field(default=300, description="Cache TTL in seconds", ge=0)

    # Application Server
    APP_PORT: int = Field(default=8000, description="Application server port", ge=1, le=65535)
    APP_HOST: str = Field(default="0.0.0.0", description="Application server host")

    # File Upload Settings
    MAX_UPLOAD_SIZE: int = Field(default=10485760, description="Max upload size in bytes (default 10MB)", ge=0)
    UPLOAD_DIR: str = Field(default="uploads", description="Upload directory path")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit requests per minute", ge=1)

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )

    # Model Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra environment variables
        validate_default=True
    )

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v: str) -> str:
        """Validate OpenAI API key format."""
        if not v:
            raise ValueError("OPENAI_API_KEY is required")
        if not v.startswith("sk-"):
            raise ValueError("OPENAI_API_KEY must start with 'sk-'")
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key length."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"LOG_LEVEL must be one of {allowed_levels}")
        return v_upper

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment name."""
        allowed_envs = ["development", "staging", "production", "test"]
        v_lower = v.lower()
        if v_lower not in allowed_envs:
            raise ValueError(f"ENVIRONMENT must be one of {allowed_envs}")
        return v_lower

    @field_validator("COOKIE_SAMESITE")
    @classmethod
    def validate_cookie_samesite(cls, v: str) -> str:
        """Validate SameSite cookie attribute."""
        allowed = ["lax", "strict", "none"]
        v_lower = v.lower()
        if v_lower not in allowed:
            raise ValueError(f"COOKIE_SAMESITE must be one of {allowed}")
        return v_lower

    @computed_field
    @property
    def database_url(self) -> str:
        """
        Construct database URL from individual components or use provided URL.

        Returns:
            Database connection URL
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @computed_field
    @property
    def cors_origins_list(self) -> List[str]:
        """
        Parse CORS origins from comma-separated string to list.

        Returns:
            List of allowed CORS origins
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @computed_field
    @property
    def allowed_hosts_list(self) -> List[str]:
        """
        Parse allowed hosts from comma-separated string to list.

        Returns:
            List of allowed hosts
        """
        if self.ALLOWED_HOSTS == "*":
            return ["*"]
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]

    @computed_field
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @computed_field
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    @computed_field
    @property
    def google_oauth_enabled(self) -> bool:
        """Check if Google OAuth is configured."""
        return bool(self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET and self.GOOGLE_REDIRECT_URI)

    def get_redis_url(self) -> Optional[str]:
        """
        Get Redis connection URL.

        Returns:
            Redis URL if caching is enabled, None otherwise
        """
        if not self.CACHE_ENABLED:
            return None
        return self.REDIS_URL or f"redis://localhost:{self.REDIS_PORT}/0"


# Global settings instance
settings = Settings()


# Validate critical settings on startup
def validate_settings():
    """
    Validate critical settings on application startup.

    Raises:
        ValueError: If critical settings are invalid
    """
    errors = []

    # Check OpenAI API key
    if not settings.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required")

    # Check secret key in production
    if settings.is_production and len(settings.SECRET_KEY) < 32:
        errors.append("SECRET_KEY must be at least 32 characters in production")

    # Check database configuration
    if not settings.DATABASE_URL and not all([
        settings.DB_HOST,
        settings.DB_PORT,
        settings.DB_USER,
        settings.DB_NAME
    ]):
        errors.append("Database configuration is incomplete")

    if errors:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))


# Validate on import (can be disabled for testing)
try:
    validate_settings()
except Exception as e:
    # Log warning but don't fail on import during testing
    import logging
    logging.warning(f"Settings validation warning: {e}")