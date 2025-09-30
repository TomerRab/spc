import re
from typing import Optional

from .constants import PROJECT_CONSTANTS, GITLAB_CONSTANTS
from .exceptions import ValidationError

def validate_project_name(name: str) -> str:
    """Validate and sanitize project name."""
    _validate_name_exists(name)
    name = name.strip()
    _validate_name_length(name)
    _validate_name_characters(name)
    return name

def _validate_name_exists(name: str) -> None:
    """Check if project name exists and is not empty."""
    if not name or not name.strip():
        raise ValidationError("Project name is required", "name")

def _validate_name_length(name: str) -> None:
    """Validate project name length constraints."""
    min_length = PROJECT_CONSTANTS['MIN_NAME_LENGTH']
    max_length = PROJECT_CONSTANTS['MAX_NAME_LENGTH']
    
    if len(name) < min_length:
        raise ValidationError(f"Project name must be at least {min_length} characters long", "name")
    
    if len(name) > max_length:
        raise ValidationError(f"Project name must be {max_length} characters or fewer", "name")

def _validate_name_characters(name: str) -> None:
    """Validate project name contains only allowed characters."""
    if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', name):
        raise ValidationError(
            "Project name contains invalid characters. Use only letters, numbers, spaces, hyphens, underscores, and periods", 
            "name"
        )

def validate_namespace(namespace: str) -> str:
    """Validate Kubernetes/OpenShift namespace."""
    _validate_namespace_exists(namespace)
    namespace = namespace.strip().lower()
    _validate_namespace_format(namespace)
    _validate_namespace_length(namespace)
    return namespace

def _validate_namespace_exists(namespace: str) -> None:
    """Check if namespace exists and is not empty."""
    if not namespace or not namespace.strip():
        raise ValidationError("Namespace is required", "namespace")

def _validate_namespace_format(namespace: str) -> None:
    """Validate namespace follows Kubernetes naming rules."""
    if not re.match(r'^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$', namespace):
        raise ValidationError(
            "Namespace must contain only lowercase letters, numbers, and hyphens, and must start and end with alphanumeric characters", 
            "namespace"
        )

def _validate_namespace_length(namespace: str) -> None:
    """Validate namespace length constraint."""
    if len(namespace) > 63:
        raise ValidationError("Namespace must be 63 characters or fewer", "namespace")

def validate_token(token: str) -> str:
    """Validate GitLab access token."""
    _validate_token_exists(token)
    token = token.strip()
    _validate_token_format(token)
    return token

def _validate_token_exists(token: str) -> None:
    """Check if token exists and is not empty."""
    if not token or not token.strip():
        raise ValidationError("Access token is required", "token")

def _validate_token_format(token: str) -> None:
    """Validate token has minimum required length."""
    if len(token) < 20:
        raise ValidationError("Invalid access token format", "token")

def validate_search_query(query: str) -> str:
    """Validate search query for GitLab groups."""
    _validate_query_exists(query)
    query = query.strip()
    _validate_query_length(query)
    return query

def _validate_query_exists(query: str) -> None:
    """Check if search query exists and is not empty."""
    if not query or not query.strip():
        raise ValidationError("Search query is required", "query")

def _validate_query_length(query: str) -> None:
    """Validate search query meets minimum length requirement."""
    min_length = GITLAB_CONSTANTS['MIN_SEARCH_LENGTH']
    if len(query) < min_length:
        raise ValidationError(f"Search query must be at least {min_length} characters long", "query")

def validate_project_type(project_type: str) -> str:
    """Validate project type is supported."""
    valid_types = PROJECT_CONSTANTS['VALID_PROJECT_TYPES']
    if not project_type or project_type not in valid_types:
        raise ValidationError(f"Invalid project type. Must be one of: {', '.join(valid_types)}", "projectType")
    return project_type

def validate_stack(stack: Optional[str], project_type: str) -> Optional[str]:
    """Validate technology stack for given project type."""
    if not stack:
        return None
    _validate_stack_is_supported(stack)
    return stack

def _validate_stack_is_supported(stack: str) -> None:
    """Check if technology stack is in the supported list."""
    valid_stacks = PROJECT_CONSTANTS['VALID_STACKS']
    if stack not in valid_stacks:
        raise ValidationError(f"Invalid technology stack. Must be one of: {', '.join(valid_stacks)}", "stack")