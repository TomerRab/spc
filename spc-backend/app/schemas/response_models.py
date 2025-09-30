"""Standardized response models for API consistency."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class RepositoryInfo(BaseModel):
    """Repository information."""
    id: int
    name: str
    url: str
    type: str
    description: Optional[str] = None
    files_created: Optional[int] = None


class ProjectDetails(BaseModel):
    """Project details information."""
    name: str
    type: str
    stack: Optional[str] = None
    visibility: str
    branch: str
    cluster_configs: int


class StandardResponse(BaseModel):
    """Standard API response format."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None


class ProjectCreationResponse(BaseModel):
    """Response for project creation operations."""
    success: bool = True
    message: str
    repositories: List[RepositoryInfo]
    variables_created: List[str]
    project_details: ProjectDetails
    primary_repos: Optional[List[Dict[str, Any]]] = None
    summary: Optional[Dict[str, Any]] = None
    next_steps: Optional[List[str]] = None


class GroupsResponse(BaseModel):
    """Response for groups operations."""
    success: bool = True
    message: str
    groups: List[Dict[str, Any]]
    total_count: Optional[int] = None


class ErrorResponse(BaseModel):
    """Error response format."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[str] = None
    errors: Optional[List[str]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    gitlab_url: str
    oauth_configured: bool
    version: Optional[str] = None
    timestamp: Optional[str] = None


# Response factory functions
def create_success_response(message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a standardized success response."""
    response = StandardResponse(
        success=True,
        message=message,
        data=data
    )
    return response.dict(exclude_none=True)


def create_error_response(message: str, errors: List[str] = None, error_code: str = None) -> Dict[str, Any]:
    """Create a standardized error response."""
    response = ErrorResponse(
        success=False,
        message=message,
        errors=errors,
        error_code=error_code
    )
    return response.dict(exclude_none=True)


def create_project_response(
    message: str,
    repositories: List[Dict],
    variables_created: List[str],
    project_details: Dict,
    **kwargs
) -> Dict[str, Any]:
    """Create a standardized project creation response."""
    repo_info = [RepositoryInfo(**repo) for repo in repositories]
    details = ProjectDetails(**project_details)
    
    response = ProjectCreationResponse(
        message=message,
        repositories=repo_info,
        variables_created=variables_created,
        project_details=details,
        **kwargs
    )
    return response.dict(exclude_none=True)


def create_groups_response(
    message: str,
    groups: List[Dict],
    total_count: int = None
) -> Dict[str, Any]:
    """Create a standardized groups response."""
    response = GroupsResponse(
        message=message,
        groups=groups,
        total_count=total_count or len(groups)
    )
    return response.dict(exclude_none=True)