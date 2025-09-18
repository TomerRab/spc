import re
from typing import Optional

from .constants import PROJECT_CONSTANTS, GITLAB_CONSTANTS
from .exceptions import ValidationError

def validate_project_name(name: str) -> str:
    """Validate and sanitize project name."""
    if not name or not name.strip():
        raise ValidationError("Project name is required", "name")
    
    name = name.strip()
    
    if len(name) < PROJECT_CONSTANTS['MIN_NAME_LENGTH']:
        raise ValidationError(
            f"Project name must be at least {PROJECT_CONSTANTS['MIN_NAME_LENGTH']} characters long", 
            "name"
        )
    
    if len(name) > PROJECT_CONSTANTS['MAX_NAME_LENGTH']:
        raise ValidationError(
            f"Project name must be {PROJECT_CONSTANTS['MAX_NAME_LENGTH']} characters or fewer", 
            "name"
        )
    
    if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', name):
        raise ValidationError(
            "Project name contains invalid characters. Use only letters, numbers, spaces, hyphens, underscores, and periods", 
            "name"
        )
    
    return name

def validate_namespace(namespace: str) -> str:
    """Validate Kubernetes/OpenShift namespace."""
    if not namespace or not namespace.strip():
        raise ValidationError("Namespace is required", "namespace")
    
    namespace = namespace.strip().lower()
    
    if not re.match(r'^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$', namespace):
        raise ValidationError(
            "Namespace must contain only lowercase letters, numbers, and hyphens, and must start and end with alphanumeric characters", 
            "namespace"
        )
    
    if len(namespace) > 63:
        raise ValidationError("Namespace must be 63 characters or fewer", "namespace")
    
    return namespace

def validate_token(token: str) -> str:
    """Validate GitLab access token."""
    if not token or not token.strip():
        raise ValidationError("Access token is required", "token")
    
    token = token.strip()
    
    # Basic token format validation
    if len(token) < 20:
        raise ValidationError("Invalid access token format", "token")
    
    return token

def validate_search_query(query: str) -> str:
    """Validate search query for GitLab groups."""
    if not query or not query.strip():
        raise ValidationError("Search query is required", "query")
    
    query = query.strip()
    
    if len(query) < GITLAB_CONSTANTS['MIN_SEARCH_LENGTH']:
        raise ValidationError(
            f"Search query must be at least {GITLAB_CONSTANTS['MIN_SEARCH_LENGTH']} characters long", 
            "query"
        )
    
    return query

def validate_project_type(project_type: str) -> str:
    """Validate project type."""
    if not project_type or project_type not in PROJECT_CONSTANTS['VALID_PROJECT_TYPES']:
        raise ValidationError(
            f"Invalid project type. Must be one of: {', '.join(PROJECT_CONSTANTS['VALID_PROJECT_TYPES'])}", 
            "projectType"
        )
    
    return project_type

def validate_stack(stack: Optional[str], project_type: str) -> Optional[str]:
    """Validate technology stack for given project type."""
    if not stack:
        return None
    
    if stack not in PROJECT_CONSTANTS['VALID_STACKS']:
        raise ValidationError(
            f"Invalid technology stack. Must be one of: {', '.join(PROJECT_CONSTANTS['VALID_STACKS'])}", 
            "stack"
        )
    
    return stack