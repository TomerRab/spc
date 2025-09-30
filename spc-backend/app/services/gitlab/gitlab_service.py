from typing import Dict, List, Tuple

from .gitlab_groups_service import GitLabGroupsService
from .gitlab_repository_service import GitLabRepositoryService
from .gitlab_variables_service import GitLabVariablesService
from app.core.config import settings


class GitLabService:
    """Main orchestrator service for GitLab API operations."""

    def __init__(self):
        self.groups_service = GitLabGroupsService(settings.gitlab_url, timeout=settings.http_timeout_gitlab)
        self.repository_service = GitLabRepositoryService()
        self.variables_service = GitLabVariablesService()

    # Groups operations
    async def get_user_groups(self, token: str) -> List[Dict[str, str]]:
        """Get all GitLab groups/namespaces accessible to the authenticated user."""
        return await self.groups_service.get_user_groups(token)

    async def search_user_groups(self, token: str, search_query: str) -> List[Dict[str, str]]:
        """Search GitLab groups/namespaces with a search query."""
        return await self.groups_service.search_user_groups(token, search_query)

    # Repository operations
    async def create_repository(self, token: str, repo_data: Dict) -> Tuple[str, int]:
        """Create a new GitLab repository and return its URL and ID."""
        return await self.repository_service.create_repository(token, repo_data)

    async def add_files(self, token: str, project_id: int, files: Dict[str, str], branch: str = None) -> None:
        """Add multiple files to a GitLab repository via commit."""
        return await self.repository_service.add_files(token, project_id, files, branch)

    async def delete_repository(self, token: str, project_id: int) -> None:
        """Delete a GitLab repository/project."""
        return await self.repository_service.delete_repository(token, project_id)

    # Variables operations
    async def set_project_variables(self, token: str, project_id: int, variables: Dict[str, str]) -> None:
        """Set CI/CD variables for a GitLab project."""
        return await self.variables_service.set_project_variables(token, project_id, variables)

    async def set_environment_variables(
        self, token: str, project_id: int, environment: str, variables: Dict[str, str]
    ) -> None:
        """Set CI/CD variables for a specific GitLab environment."""
        return await self.variables_service.set_environment_variables(token, project_id, environment, variables)

