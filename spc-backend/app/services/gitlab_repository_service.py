import base64
import logging
from typing import Dict, Tuple

import httpx
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


class GitLabRepositoryService:
    """Service for managing GitLab repositories."""
    
    def __init__(self):
        self.base_url = settings.gitlab_url
        self.timeout = 30.0

    def _get_headers(self, token: str) -> Dict[str, str]:
        """Get HTTP headers for GitLab API requests."""
        return {
            "Authorization": f"Bearer {token}", 
            "Content-Type": "application/json"
        }

    async def create_repository(self, token: str, repo_data: Dict) -> Tuple[str, int]:
        """Create a new GitLab repository and return its URL and ID."""
        payload = {
            "name": repo_data.get("project_name") or repo_data.get("name"),
            "namespace_id": int(repo_data.get("group_id") or repo_data.get("groupId")),
            "visibility": "private",
            "initialize_with_readme": False,
        }

        logger.info(f"Creating GitLab repository with payload: {payload}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/projects",
                    headers=self._get_headers(token),
                    json=payload,
                )

            logger.info(f"GitLab create repository response: {response.status_code}")

            if response.status_code == 401:
                logger.error("Invalid access token for repository creation")
                raise HTTPException(401, "Your GitLab access token has expired or is invalid. Please sign out and sign in again to refresh your credentials.")
            if response.status_code == 400:
                error_msg = response.text
                if "has already been taken" in error_msg or "already exists" in error_msg:
                    project_name = payload.get('name', 'project')
                    raise HTTPException(400, f"A project named '{project_name}' already exists in this group. Please choose a different project name.")
                elif "Name is invalid" in error_msg:
                    raise HTTPException(400, "Project name contains invalid characters. Please use only letters, numbers, spaces, hyphens, and underscores.")
                else:
                    raise HTTPException(400, f"Failed to create repository. Please check your project settings and try again. Details: {error_msg}")
            if response.status_code == 403:
                logger.error("Insufficient permissions for repository creation")
                raise HTTPException(403, "You don't have permission to create repositories in this group. Please contact your GitLab administrator or choose a different group.")
            if response.status_code != 201:
                logger.error(f"Repository creation failed: {response.status_code} - {response.text}")
                raise HTTPException(500, f"Failed to create repository due to an unexpected error. Please try again later. (Error code: {response.status_code})")

            repo_data = response.json()
            return repo_data["http_url_to_repo"], repo_data["id"]

        except httpx.RequestError as e:
            logger.error(f"GitLab connection error during repo creation: {e}")
            raise HTTPException(503, f"Cannot connect to GitLab: {e}")

    async def add_files(
        self, token: str, project_id: int, files: Dict[str, str]
    ) -> None:
        """Add multiple files to a GitLab repository via commit."""
        actions = []
        for file_path, content in files.items():
            encoded_content = base64.b64encode(content.encode()).decode()
            actions.append(
                {
                    "action": "create",
                    "file_path": file_path,
                    "content": encoded_content,
                    "encoding": "base64",
                }
            )

        payload = {
            "branch": "main",
            "commit_message": "Initial project setup",
            "actions": actions,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/projects/{project_id}/repository/commits",
                headers=self._get_headers(token),
                json=payload,
            )

        if response.status_code == 401:
            raise HTTPException(401, "Your GitLab access token has expired or is invalid. Please sign out and sign in again to refresh your credentials.")
        if response.status_code == 403:
            raise HTTPException(403, "You don't have permission to add files to this repository. Please ensure you have developer or maintainer access to the project.")
        if response.status_code != 201:
            error_response = response.json() if response.headers.get('content-type') == 'application/json' else {}
            error_msg = error_response.get('message', 'Unknown error occurred')
            if "empty repository" in error_msg.lower():
                raise HTTPException(400, "Cannot initialize repository - the repository may have been created incorrectly. Please try creating the project again.")
            else:
                raise HTTPException(500, f"Failed to add files to repository: {error_msg}. Please try again or contact support.")

    async def delete_repository(self, token: str, project_id: int) -> None:
        """Delete a GitLab repository/project."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    f"{self.base_url}/projects/{project_id}",
                    headers=self._get_headers(token),
                )
            
            if response.status_code == 202:  # GitLab returns 202 for successful deletion
                logger.info(f"Successfully deleted project {project_id}")
            elif response.status_code == 404:
                logger.warning(f"Project {project_id} not found (may have been already deleted)")
            else:
                logger.error(f"Failed to delete project {project_id}: {response.status_code} - {response.text}")
                raise HTTPException(response.status_code, f"Failed to delete project: {response.text}")
                
        except httpx.RequestError as e:
            logger.error(f"Network error while deleting project {project_id}: {e}")
            raise HTTPException(500, f"Network error during project deletion: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error while deleting project {project_id}: {e}")
            raise HTTPException(500, f"Unexpected error during project deletion: {str(e)}")