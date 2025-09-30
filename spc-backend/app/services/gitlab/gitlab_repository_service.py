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
        self.timeout = settings.http_timeout_gitlab

    def _get_headers(self, token: str) -> Dict[str, str]:
        """Get HTTP headers for GitLab API requests."""
        return {
            "Authorization": f"Bearer {token}", 
            "Content-Type": "application/json"
        }

    async def create_repository(self, token: str, repo_data: Dict) -> Tuple[str, int]:
        """Create a new GitLab repository and return its URL and ID."""
        payload = self._prepare_repository_payload(repo_data)
        logger.info(f"Creating GitLab repository with payload: {payload}")
        try:
            response = await self._send_create_request(token, payload)
            self._validate_create_response(response, payload)
            repo_data = response.json()
            return repo_data["http_url_to_repo"], repo_data["id"]
        except httpx.RequestError as e:
            logger.error(f"GitLab connection error during repo creation: {e}")
            raise HTTPException(503, f"Cannot connect to GitLab: {e}")

    def _prepare_repository_payload(self, repo_data: Dict) -> Dict:
        """Prepare the payload for repository creation."""
        return {
            "name": repo_data.get("project_name") or repo_data.get("name"),
            "namespace_id": int(repo_data.get("group_id") or repo_data.get("groupId")),
            "visibility": "private",
            "initialize_with_readme": False,
        }

    async def _send_create_request(self, token: str, payload: Dict) -> httpx.Response:
        """Send the repository creation request to GitLab."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/projects",
                headers=self._get_headers(token),
                json=payload,
            )
        logger.info(f"GitLab create repository response: {response.status_code}")
        return response

    def _validate_create_response(self, response: httpx.Response, payload: Dict) -> None:
        """Validate the repository creation response."""
        if response.status_code == 401:
            self._handle_auth_error()
        elif response.status_code == 400:
            self._handle_bad_request_error(response.text, payload)
        elif response.status_code == 403:
            self._handle_permission_error()
        elif response.status_code != 201:
            self._handle_unexpected_error(response)

    def _handle_auth_error(self) -> None:
        """Handle authentication errors."""
        logger.error("Invalid access token for repository creation")
        raise HTTPException(401, "Your GitLab access token has expired or is invalid. Please sign out and sign in again to refresh your credentials.")

    def _handle_bad_request_error(self, error_msg: str, payload: Dict) -> None:
        """Handle bad request errors with specific messages."""
        if "has already been taken" in error_msg or "already exists" in error_msg:
            project_name = payload.get('name', 'project')
            raise HTTPException(400, f"A project named '{project_name}' already exists in this group. Please choose a different project name.")
        elif "Name is invalid" in error_msg:
            raise HTTPException(400, "Project name contains invalid characters. Please use only letters, numbers, spaces, hyphens, and underscores.")
        else:
            logger.error(f"Repository creation failed with details: {error_msg}")
            raise HTTPException(400, "Failed to create repository. Please check your project settings and try again.")

    def _handle_permission_error(self) -> None:
        """Handle permission errors."""
        logger.error("Insufficient permissions for repository creation")
        raise HTTPException(403, "You don't have permission to create repositories in this group. Please contact your GitLab administrator or choose a different group.")

    def _handle_unexpected_error(self, response: httpx.Response) -> None:
        """Handle unexpected errors."""
        logger.error(f"Repository creation failed: {response.status_code} - {response.text}")
        raise HTTPException(500, f"Failed to create repository due to an unexpected error. Please try again later. (Error code: {response.status_code})")

    async def add_files(self, token: str, project_id: int, files: Dict[str, str], branch: str = None) -> None:
        """Add multiple files to a GitLab repository via commit."""
        actions = self._prepare_file_actions(files)
        payload = self._build_commit_payload(actions, branch)
        response = await self._send_commit_request(token, project_id, payload)
        self._validate_add_files_response(response)

    def _prepare_file_actions(self, files: Dict[str, str]) -> list:
        """Prepare file actions for GitLab commit."""
        actions = []
        for file_path, content in files.items():
            encoded_content = base64.b64encode(content.encode()).decode()
            actions.append({
                "action": "create",
                "file_path": file_path,
                "content": encoded_content,
                "encoding": "base64",
            })
        return actions

    def _build_commit_payload(self, actions: list, branch: str = None) -> dict:
        """Build commit payload for GitLab API."""
        return {
            "branch": branch or settings.default_branch,
            "commit_message": settings.commit_message,
            "actions": actions,
        }

    async def _send_commit_request(self, token: str, project_id: int, payload: dict) -> httpx.Response:
        """Send commit request to GitLab."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.post(
                f"{self.base_url}/projects/{project_id}/repository/commits",
                headers=self._get_headers(token),
                json=payload,
            )

    def _validate_add_files_response(self, response: httpx.Response) -> None:
        """Validate the add files response."""
        if response.status_code == 401:
            raise HTTPException(401, "Your GitLab access token has expired or is invalid. Please sign out and sign in again to refresh your credentials.")
        elif response.status_code == 403:
            raise HTTPException(403, "You don't have permission to add files to this repository. Please ensure you have developer or maintainer access to the project.")
        elif response.status_code != 201:
            self._handle_add_files_error(response)

    def _handle_add_files_error(self, response: httpx.Response) -> None:
        """Handle add files error responses."""
        error_response = response.json() if response.headers.get('content-type') == 'application/json' else {}
        error_msg = error_response.get('message', 'Unknown error occurred')
        if "empty repository" in error_msg.lower():
            raise HTTPException(400, "Cannot initialize repository - the repository may have been created incorrectly. Please try creating the project again.")
        else:
            raise HTTPException(500, f"Failed to add files to repository: {error_msg}. Please try again or contact support.")

    async def delete_repository(self, token: str, project_id: int) -> None:
        """Delete a GitLab repository/project."""
        try:
            response = await self._send_delete_request(token, project_id)
            self._handle_delete_response(response, project_id)
        except httpx.RequestError as e:
            self._handle_delete_network_error(e, project_id)
        except Exception as e:
            self._handle_delete_unexpected_error(e, project_id)

    async def _send_delete_request(self, token: str, project_id: int) -> httpx.Response:
        """Send delete request to GitLab."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.delete(
                f"{self.base_url}/projects/{project_id}",
                headers=self._get_headers(token),
            )

    def _handle_delete_response(self, response: httpx.Response, project_id: int) -> None:
        """Handle delete response from GitLab."""
        if response.status_code == 202:
            logger.info(f"Successfully deleted project {project_id}")
        elif response.status_code == 404:
            logger.warning(f"Project {project_id} not found (may have been already deleted)")
        else:
            logger.error(f"Failed to delete project {project_id}: {response.status_code} - {response.text}")
            raise HTTPException(response.status_code, f"Failed to delete project: {response.text}")

    def _handle_delete_network_error(self, e: httpx.RequestError, project_id: int) -> None:
        """Handle network error during deletion."""
        logger.error(f"Network error while deleting project {project_id}: {e}")
        raise HTTPException(500, f"Network error during project deletion: {str(e)}")

    def _handle_delete_unexpected_error(self, e: Exception, project_id: int) -> None:
        """Handle unexpected error during deletion."""
        logger.error(f"Unexpected error while deleting project {project_id}: {e}")
        raise HTTPException(500, f"Unexpected error during project deletion: {str(e)}")