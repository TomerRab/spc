import logging
from typing import Dict, List

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.utils.exceptions import GitLabError

logger = logging.getLogger(__name__)


class GitLabVariablesService:
    """Service for managing GitLab project variables."""

    def __init__(self):
        self.base_url = settings.gitlab_url
        self.timeout = settings.http_timeout_gitlab

    def _get_headers(self, token: str) -> Dict[str, str]:
        """Get HTTP headers for GitLab API requests."""
        return {
            "Authorization": f"Bearer {token}", 
            "Content-Type": "application/json"
        }

    async def set_project_variables(self, token: str, project_id: int, variables: Dict[str, str]) -> None:
        """Set CI/CD variables for a GitLab project."""
        for key, value in variables.items():
            await self._set_single_project_variable(token, project_id, key, value)

    async def _set_single_project_variable(self, token: str, project_id: int, key: str, value: str) -> None:
        """Set a single project variable."""
        payload = {"key": key, "value": value, "protected": False, "masked": False}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/projects/{project_id}/variables",
                headers=self._get_headers(token),
                json=payload,
            )
        if response.status_code not in [201, 400]:
            error_msg = f"Failed to set variable {key}: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise GitLabError(f"Failed to set project variable '{key}'. Please try again.", response.status_code, "set_variable")

    async def set_environment_variables(self, token: str, project_id: int, environment: str, variables: Dict[str, str]) -> None:
        """Set CI/CD variables for a specific GitLab environment."""
        logger.info(f"Setting environment variables for environment '{environment}' in project {project_id}")
        for key, value in variables.items():
            await self._set_single_environment_variable(token, project_id, environment, key, value)

    async def _set_single_environment_variable(self, token: str, project_id: int, environment: str, key: str, value: str) -> None:
        """Set a single environment variable."""
        payload = self._build_environment_variable_payload(key, value, environment)
        response = await self._send_environment_variable_request(token, project_id, payload)
        await self._handle_environment_variable_response(response, token, project_id, environment, key, value)

    def _build_environment_variable_payload(self, key: str, value: str, environment: str) -> dict:
        """Build payload for environment variable."""
        return {
            "key": key, 
            "value": value, 
            "protected": False, 
            "masked": False,
            "environment_scope": environment
        }

    async def _send_environment_variable_request(self, token: str, project_id: int, payload: dict) -> httpx.Response:
        """Send environment variable request to GitLab."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.post(
                f"{self.base_url}/projects/{project_id}/variables",
                headers=self._get_headers(token),
                json=payload,
            )

    async def _handle_environment_variable_response(self, response: httpx.Response, token: str, project_id: int, environment: str, key: str, value: str) -> None:
        """Handle environment variable response."""
        logger.debug(f"Variable {key} response: {response.status_code}")
        if response.status_code == 201:
            logger.info(f"✅ Set environment variable {key}='{value}' for environment '{environment}'")
        elif response.status_code == 400:
            await self._update_environment_variable(token, project_id, key, value, environment)
        else:
            logger.error(f"❌ Failed to set environment variable {key} for environment {environment}: {response.status_code} - {response.text}")
            raise GitLabError(f"Failed to set environment variable '{key}' for environment '{environment}'. Please try again.", response.status_code, "set_environment_variable")

    async def _update_environment_variable(self, token: str, project_id: int, key: str, value: str, environment: str) -> None:
        """Update an existing environment variable."""
        payload = self._build_update_payload(value, environment)
        response = await self._send_update_request(token, project_id, key, payload)
        self._handle_update_response(response, key, value, environment)

    def _build_update_payload(self, value: str, environment: str) -> dict:
        """Build payload for updating environment variable."""
        return {
            "value": value,
            "protected": False,
            "masked": False,
            "environment_scope": environment
        }

    async def _send_update_request(self, token: str, project_id: int, key: str, payload: dict) -> httpx.Response:
        """Send update request to GitLab."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.put(
                f"{self.base_url}/projects/{project_id}/variables/{key}",
                headers=self._get_headers(token),
                json=payload,
            )

    def _handle_update_response(self, response: httpx.Response, key: str, value: str, environment: str) -> None:
        """Handle update response."""
        if response.status_code == 200:
            logger.info(f"✅ Updated environment variable {key}='{value}' for environment '{environment}'")
        else:
            logger.error(f"❌ Failed to update environment variable {key}: {response.status_code} - {response.text}")
            raise GitLabError(f"Failed to update environment variable '{key}'. Please try again.", response.status_code, "update_environment_variable")

