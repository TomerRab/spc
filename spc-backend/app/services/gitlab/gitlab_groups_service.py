from typing import Dict, List
import httpx
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class GitLabGroupsService:
    """Service for managing GitLab groups."""
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout

    def _get_headers(self, token: str) -> Dict[str, str]:
        """Get HTTP headers for GitLab API requests."""
        return {
            "Authorization": f"Bearer {token}", 
            "Content-Type": "application/json"
        }

    async def get_user_groups(self, token: str) -> List[Dict[str, str]]:
        """Get all GitLab groups/namespaces accessible to the authenticated user."""
        all_groups = []
        page = 1

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while True:
                try:
                    response = await client.get(
                        f"{self.base_url}/groups",
                        headers=self._get_headers(token),
                        params={"page": page, "per_page": 100},
                    )

                    logger.info(f"GitLab groups API response: {response.status_code}")

                    if response.status_code == 401:
                        logger.error("Invalid access token for GitLab API")
                        raise HTTPException(401, "Your GitLab access token has expired or is invalid. Please sign out and sign in again to refresh your credentials.")
                    if response.status_code == 403:
                        logger.error("Insufficient permissions for GitLab API")
                        raise HTTPException(403, "You don't have permission to access GitLab groups. Please ensure your GitLab account has the necessary permissions.")
                    if response.status_code != 200:
                        logger.error(f"GitLab API error: {response.status_code} - {response.text}")
                        raise HTTPException(502, f"Unable to connect to GitLab. Please try again later. (Error: {response.status_code})")

                    groups_data = response.json()
                    if not groups_data:
                        break

                    all_groups.extend([
                        {
                            "id": g["id"], 
                            "name": g["name"],
                            "full_path": g["full_path"],
                            "visibility": g.get("visibility", "private")
                        } for g in groups_data
                    ])

                    if len(groups_data) < 100:
                        break

                    page += 1

                except httpx.RequestError as e:
                    logger.error(f"GitLab connection error: {e}")
                    raise HTTPException(503, f"Cannot connect to GitLab: {e}")

        return all_groups

    async def search_user_groups(self, token: str, search_query: str) -> List[Dict[str, str]]:
        """Search GitLab groups/namespaces with a search query."""
        all_groups = []
        page = 1

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while True:
                try:
                    response = await client.get(
                        f"{self.base_url}/groups",
                        headers=self._get_headers(token),
                        params={"page": page, "per_page": 100, "search": search_query},
                    )

                    logger.info(f"GitLab groups search API response: {response.status_code} for query '{search_query}'")

                    if response.status_code == 401:
                        logger.error("Invalid access token for GitLab API")
                        raise HTTPException(401, "Your GitLab access token has expired or is invalid. Please sign out and sign in again to refresh your credentials.")
                    if response.status_code == 403:
                        logger.error("Insufficient permissions for GitLab API")
                        raise HTTPException(403, "You don't have permission to access GitLab groups. Please ensure your GitLab account has the necessary permissions.")
                    if response.status_code != 200:
                        logger.error(f"GitLab API error: {response.status_code} - {response.text}")
                        raise HTTPException(502, f"Unable to connect to GitLab. Please try again later. (Error: {response.status_code})")

                    groups_data = response.json()
                    if not groups_data:
                        break

                    all_groups.extend([
                        {
                            "id": g["id"], 
                            "name": g["name"],
                            "full_path": g["full_path"],
                            "visibility": g.get("visibility", "private")
                        } for g in groups_data
                    ])

                    # GitLab API returns fewer results when using search, so we might get all results in first page
                    if len(groups_data) < 100:
                        break

                    page += 1

                except httpx.RequestError as e:
                    logger.error(f"GitLab connection error during search: {e}")
                    raise HTTPException(503, f"Cannot connect to GitLab: {e}")

        logger.info(f"Found {len(all_groups)} groups matching query '{search_query}'")
        return all_groups