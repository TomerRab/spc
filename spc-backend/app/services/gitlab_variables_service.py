import logging
from typing import Dict, List

import httpx
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


class GitLabVariablesService:
    """Service for managing GitLab project variables."""
    
    def __init__(self):
        self.base_url = settings.gitlab_url
        self.timeout = 30.0

    def _get_headers(self, token: str) -> Dict[str, str]:
        """Get HTTP headers for GitLab API requests."""
        return {
            "Authorization": f"Bearer {token}", 
            "Content-Type": "application/json"
        }

    async def set_project_variables(
        self, token: str, project_id: int, variables: Dict[str, str]
    ) -> None:
        """Set CI/CD variables for a GitLab project."""
        for key, value in variables.items():
            payload = {"key": key, "value": value, "protected": False, "masked": False}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/projects/{project_id}/variables",
                    headers=self._get_headers(token),
                    json=payload,
                )

            if response.status_code not in [201, 400]:  # 400 = already exists
                logger.warning(f"Failed to set variable {key}")

    async def set_environment_variables(
        self, token: str, project_id: int, environment: str, variables: Dict[str, str]
    ) -> None:
        """Set CI/CD variables for a specific GitLab environment."""
        logger.info(f"Setting environment variables for environment '{environment}' in project {project_id}")
        
        # Set variables for that environment
        for key, value in variables.items():
            payload = {
                "key": key, 
                "value": value, 
                "protected": False, 
                "masked": False,
                "environment_scope": environment
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/projects/{project_id}/variables",
                    headers=self._get_headers(token),
                    json=payload,
                )

            logger.info(f"Variable {key} response: {response.status_code} - {response.text}")
            
            if response.status_code == 201:
                logger.info(f"✅ Set environment variable {key}='{value}' for environment '{environment}'")
            elif response.status_code == 400:
                # Variable already exists, try to update it
                await self._update_environment_variable(token, project_id, key, value, environment)
            else:
                logger.error(f"❌ Failed to set environment variable {key} for environment {environment}: {response.status_code} - {response.text}")

    async def _update_environment_variable(
        self, token: str, project_id: int, key: str, value: str, environment: str
    ) -> None:
        """Update an existing environment variable."""
        payload = {
            "value": value,
            "protected": False,
            "masked": False,
            "environment_scope": environment
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(
                f"{self.base_url}/projects/{project_id}/variables/{key}",
                headers=self._get_headers(token),
                json=payload,
            )

        if response.status_code == 200:
            logger.info(f"✅ Updated environment variable {key}='{value}' for environment '{environment}'")
        else:
            logger.error(f"❌ Failed to update environment variable {key}: {response.status_code} - {response.text}")

