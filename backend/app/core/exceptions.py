"""
Custom exception hierarchy for UMLReq application.

This module provides a comprehensive exception hierarchy for handling
various error conditions throughout the application.
"""

from typing import Any, Optional


class UMLReqException(Exception):
    """Base exception for all UMLReq application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# Authentication & Authorization Exceptions
class AuthenticationError(UMLReqException):
    """Base class for authentication related errors."""

    def __init__(self, message: str = "Authentication failed", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class InvalidCredentialsError(AuthenticationError):
    """Raised when user provides invalid credentials."""

    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(message)


class TokenExpiredError(AuthenticationError):
    """Raised when authentication token has expired."""

    def __init__(self, message: str = "Authentication token has expired"):
        super().__init__(message)


class InvalidTokenError(AuthenticationError):
    """Raised when authentication token is invalid."""

    def __init__(self, message: str = "Invalid authentication token"):
        super().__init__(message)


class AuthorizationError(UMLReqException):
    """Raised when user lacks permission for requested action."""

    def __init__(self, message: str = "Insufficient permissions", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


# Resource Exceptions
class ResourceNotFoundError(UMLReqException):
    """Base class for resource not found errors."""

    def __init__(self, resource_type: str, resource_id: Any):
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message, status_code=404, details={"resource_type": resource_type, "resource_id": resource_id})


class DiagramNotFoundError(ResourceNotFoundError):
    """Raised when requested diagram doesn't exist."""

    def __init__(self, diagram_id: int):
        super().__init__("Diagram", diagram_id)


class SessionNotFoundError(ResourceNotFoundError):
    """Raised when requested requirement session doesn't exist."""

    def __init__(self, session_id: int):
        super().__init__("Requirement Session", session_id)


class UserNotFoundError(ResourceNotFoundError):
    """Raised when requested user doesn't exist."""

    def __init__(self, user_id: int):
        super().__init__("User", user_id)


class ResourceAlreadyExistsError(UMLReqException):
    """Raised when attempting to create a resource that already exists."""

    def __init__(self, resource_type: str, identifier: str):
        message = f"{resource_type} with identifier '{identifier}' already exists"
        super().__init__(
            message,
            status_code=409,
            details={"resource_type": resource_type, "identifier": identifier}
        )


# Validation Exceptions
class ValidationError(UMLReqException):
    """Base class for validation errors."""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[dict[str, Any]] = None):
        validation_details = details or {}
        if field:
            validation_details["field"] = field
        super().__init__(message, status_code=422, details=validation_details)


class InvalidInputError(ValidationError):
    """Raised when input data is invalid."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, field=field)


class RequirementParsingError(ValidationError):
    """Raised when requirements text cannot be parsed."""

    def __init__(self, message: str = "Failed to parse requirements text", details: Optional[dict[str, Any]] = None):
        super().__init__(message, details=details)


# Service Layer Exceptions
class ServiceError(UMLReqException):
    """Base class for service layer errors."""

    def __init__(self, service_name: str, message: str, details: Optional[dict[str, Any]] = None):
        service_details = details or {}
        service_details["service"] = service_name
        super().__init__(message, status_code=500, details=service_details)


class NLPServiceError(ServiceError):
    """Raised when NLP service encounters an error."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__("NLP Service", message, details)


class GPTServiceError(ServiceError):
    """Raised when GPT service encounters an error."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__("GPT Service", message, details)


class PlantUMLServiceError(ServiceError):
    """Raised when PlantUML service encounters an error."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__("PlantUML Service", message, details)


class DiagramGenerationError(ServiceError):
    """Raised when diagram generation fails."""

    def __init__(self, message: str = "Failed to generate diagram", details: Optional[dict[str, Any]] = None):
        super().__init__("Diagram Generation", message, details)


# External Service Exceptions
class ExternalServiceError(UMLReqException):
    """Base class for external service errors."""

    def __init__(self, service_name: str, message: str, details: Optional[dict[str, Any]] = None):
        external_details = details or {}
        external_details["external_service"] = service_name
        super().__init__(message, status_code=503, details=external_details)


class OpenAIAPIError(ExternalServiceError):
    """Raised when OpenAI API encounters an error."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__("OpenAI API", message, details)


class PlantUMLRenderError(ExternalServiceError):
    """Raised when PlantUML rendering fails."""

    def __init__(self, message: str = "Failed to render diagram", details: Optional[dict[str, Any]] = None):
        super().__init__("PlantUML Renderer", message, details)


# Database Exceptions
class DatabaseError(UMLReqException):
    """Base class for database related errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, message: str = "Failed to connect to database"):
        super().__init__(message)


class DatabaseOperationError(DatabaseError):
    """Raised when database operation fails."""

    def __init__(self, operation: str, details: Optional[dict[str, Any]] = None):
        message = f"Database operation '{operation}' failed"
        op_details = details or {}
        op_details["operation"] = operation
        super().__init__(message, details=op_details)


# Configuration Exceptions
class ConfigurationError(UMLReqException):
    """Raised when application configuration is invalid."""

    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {"config_key": config_key} if config_key else {}
        super().__init__(message, status_code=500, details=details)


# Rate Limiting Exceptions
class RateLimitError(UMLReqException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, status_code=429, details=details)


# File Operation Exceptions
class FileOperationError(UMLReqException):
    """Base class for file operation errors."""

    def __init__(self, message: str, file_path: Optional[str] = None):
        details = {"file_path": file_path} if file_path else {}
        super().__init__(message, status_code=500, details=details)


class FileNotFoundError(FileOperationError):
    """Raised when required file is not found."""

    def __init__(self, file_path: str):
        super().__init__(f"File not found: {file_path}", file_path)


class FileReadError(FileOperationError):
    """Raised when file cannot be read."""

    def __init__(self, file_path: str, reason: Optional[str] = None):
        message = f"Failed to read file: {file_path}"
        if reason:
            message += f" - {reason}"
        super().__init__(message, file_path)


class FileWriteError(FileOperationError):
    """Raised when file cannot be written."""

    def __init__(self, file_path: str, reason: Optional[str] = None):
        message = f"Failed to write file: {file_path}"
        if reason:
            message += f" - {reason}"
        super().__init__(message, file_path)
