"""Centralized error handlers for the FastAPI application."""
import logging
from typing import Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.utils.exceptions import (
    SPCBaseException,
    GitLabError,
    GitLabConnectionError,
    GitLabAuthenticationError,
    GitLabRepositoryError,
    TemplateError,
    TemplateNotFoundError,
    TemplateRenderError,
    ValidationError as SPCValidationError,
    ProjectCreationError,
    ConfigurationError,
    S3Error
)
from app.schemas.response_models import create_error_response

logger = logging.getLogger(__name__)


async def spc_base_exception_handler(request: Request, exc: SPCBaseException) -> JSONResponse:
    """Handle all SPC base exceptions with user-friendly messages."""
    # Log technical details for debugging
    logger.error(f"SPC Error in {request.url.path}: {exc.message}", extra={"details": exc.details})

    # Determine status code and user-friendly message
    if isinstance(exc, SPCValidationError):
        status_code = status.HTTP_400_BAD_REQUEST
        user_message = exc.message  # Validation errors are user-friendly
    elif isinstance(exc, GitLabAuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
        user_message = "Your session has expired. Please sign in again."
    elif isinstance(exc, GitLabConnectionError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        user_message = "Unable to connect to GitLab. Please try again later."
    elif isinstance(exc, S3Error):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        user_message = "A system error occurred. Please contact SOLID Team for support."
    elif isinstance(exc, (TemplateNotFoundError, TemplateError)):
        status_code = status.HTTP_400_BAD_REQUEST
        user_message = "The selected configuration is not currently supported. Please try a different option."
    elif isinstance(exc, ConfigurationError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        user_message = "A system error occurred. Please contact SOLID Team for support."
    elif isinstance(exc, ProjectCreationError):
        status_code = status.HTTP_400_BAD_REQUEST
        user_message = exc.message  # Project errors are usually user-actionable
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        user_message = "A system error occurred. Please contact SOLID Team for support."

    return JSONResponse(
        status_code=status_code,
        content=create_error_response(
            message=user_message,
            error_code="error"
        )
    )


async def gitlab_error_handler(request: Request, exc: GitLabError) -> JSONResponse:
    """Handle GitLab-specific errors with user-friendly messages."""
    # Log technical details for debugging
    logger.error(f"GitLab Error in {request.url.path}: {exc.message}", extra={
        "operation": exc.operation,
        "status_code": exc.status_code
    })

    # Determine status code and user-friendly message
    if exc.status_code in [401, 403]:
        status_code = status.HTTP_401_UNAUTHORIZED
        user_message = "GitLab authentication failed. Please sign in again."
    elif exc.status_code == 404:
        status_code = status.HTTP_404_NOT_FOUND
        user_message = "The requested GitLab resource was not found."
    elif exc.status_code in range(500, 600):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        user_message = "GitLab service is temporarily unavailable. Please try again later."
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        # For 400-level errors, the original message is usually user-actionable
        user_message = exc.message

    return JSONResponse(
        status_code=status_code,
        content=create_error_response(
            message=user_message,
            error_code="error"
        )
    )


async def template_error_handler(request: Request, exc: TemplateError) -> JSONResponse:
    """Handle template processing errors with user-friendly messages."""
    # Log technical details for debugging
    logger.error(f"Template Error in {request.url.path}: {exc.message}", extra={
        "template_name": exc.template_name,
        "template_path": exc.template_path
    })

    # User-friendly message - hide technical template details
    if isinstance(exc, TemplateNotFoundError):
        status_code = status.HTTP_400_BAD_REQUEST
        user_message = "The selected project configuration is not available. Please try a different technology stack."
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        user_message = "A system error occurred. Please contact SOLID Team for support."

    return JSONResponse(
        status_code=status_code,
        content=create_error_response(
            message=user_message,
            error_code="error"
        )
    )


async def validation_error_handler(request: Request, exc: Union[ValidationError, SPCValidationError]) -> JSONResponse:
    """Handle validation errors from Pydantic and custom validators."""
    if isinstance(exc, ValidationError):
        # Handle Pydantic validation errors - make user-friendly
        errors = []
        for error in exc.errors():
            field_parts = [str(loc) for loc in error["loc"] if str(loc) != "body"]
            field_name = field_parts[-1] if field_parts else "input"

            # Make field names readable
            readable_field = field_name.replace("_", " ").replace("groupId", "group").replace("projectType", "project type")
            message = error["msg"]

            # Simplify technical messages
            if "field required" in message.lower():
                errors.append(f"{readable_field.capitalize()} is required")
            elif "not a valid" in message.lower():
                errors.append(f"{readable_field.capitalize()} has an invalid value")
            else:
                errors.append(f"{readable_field.capitalize()}: {message}")

        user_message = "Please check your input: " + "; ".join(errors)
        logger.warning(f"Validation Error in {request.url.path}: {user_message}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_error_response(
                message=user_message,
                error_code="validation_error"
            )
        )
    else:
        # Handle custom validation errors - these are already user-friendly
        logger.warning(f"Custom Validation Error in {request.url.path}: {exc.message}", extra={"field": exc.field})

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_error_response(
                message=exc.message,
                error_code="validation_error"
            )
        )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPExceptions with user-friendly messages."""
    # Log technical details
    logger.warning(f"HTTP Exception in {request.url.path}: {exc.detail} (status: {exc.status_code})")

    # Keep the original message for 4xx errors (usually user-actionable)
    # Simplify 5xx errors to avoid exposing internals
    if exc.status_code >= 500:
        user_message = "A system error occurred. Please contact SOLID Team for support."
    else:
        user_message = str(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            message=user_message,
            error_code="error"
        )
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions - never expose internal details to users."""
    # Log full exception with stack trace for debugging
    logger.exception(f"Unexpected error in {request.url.path}: {str(exc)}")

    # Generic user-friendly message - no technical details
    user_message = "A system error occurred. Please contact SOLID Team for support."

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            message=user_message,
            error_code="error"
        )
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    # Register in order of specificity (most specific first)
    app.add_exception_handler(GitLabError, gitlab_error_handler)
    app.add_exception_handler(TemplateError, template_error_handler)
    app.add_exception_handler(SPCValidationError, validation_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(SPCBaseException, spc_base_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)