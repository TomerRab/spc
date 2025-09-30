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
        headers = {
            "Authorization": f"Bearer {token}", 
            "Content-Type": "application/json"
        }
        logger.debug("Authorization header configured")
        return headers

    async def get_user_groups(self, token: str) -> List[Dict[str, str]]:
        """Get all GitLab groups/namespaces accessible to the authenticated user."""
        all_groups = []
        page = 1
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while True:
                groups_page = await self._fetch_groups_page(client, token, page)
                if not groups_page:
                    break
                all_groups.extend(self._format_groups_data(groups_page))
                if len(groups_page) < 100:
                    break
                page += 1
        return all_groups

    async def _fetch_groups_page(self, client: httpx.AsyncClient, token: str, page: int, search_query: str = None) -> List[Dict]:
        """Fetch a single page of groups from GitLab API."""
        try:
            params = {"page": page, "per_page": 100}
            if search_query:
                params["search"] = search_query
                logger.info(f"Searching groups with query: '{search_query}', page: {page}")
            else:
                logger.info(f"Fetching all groups, page: {page}")
            
            url = f"{self.base_url}/groups"
            headers = self._get_headers(token)
            logger.info(f"Making request to: {url} with params: {params}")
            
            response = await client.get(url, headers=headers, params=params)
            logger.info(f"GitLab groups API response: {response.status_code}, Content-Length: {len(response.content)}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Successfully parsed {len(result)} groups from response")
                return result
            else:
                logger.error(f"Error response content: {response.text[:500]}")
                self._validate_groups_response(response)
                return []
                
        except httpx.RequestError as e:
            logger.error(f"GitLab connection error: {e}")
            raise HTTPException(503, "Cannot connect to GitLab. Please check your network connection and try again.")

    def _validate_groups_response(self, response: httpx.Response) -> None:
        """Validate GitLab groups API response."""
        if response.status_code == 401:
            logger.error("Invalid access token for GitLab API")
            raise HTTPException(401, "Your GitLab access token has expired or is invalid. Please sign out and sign in again to refresh your credentials.")
        elif response.status_code == 403:
            logger.error("Insufficient permissions for GitLab API")
            raise HTTPException(403, "You don't have permission to access GitLab groups. Please ensure your GitLab account has the necessary permissions.")
        elif response.status_code != 200:
            logger.error(f"GitLab API error: {response.status_code} - {response.text}")
            raise HTTPException(502, f"Unable to connect to GitLab. Please try again later. (Error: {response.status_code})")

    def _format_groups_data(self, groups_data: List[Dict]) -> List[Dict[str, str]]:
        """Format groups data for API response."""
        return [
            {
                "id": g["id"], 
                "name": g["name"],
                "full_path": g["full_path"],
                "visibility": g.get("visibility", "private")
            } for g in groups_data
        ]

    async def search_user_groups(self, token: str, search_query: str) -> List[Dict[str, str]]:
        """Search GitLab groups/namespaces with a search query."""
        all_groups = []
        page = 1
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while True:
                groups_page = await self._fetch_groups_page(client, token, page, search_query)
                if not groups_page:
                    break
                all_groups.extend(self._format_groups_data(groups_page))
                if len(groups_page) < 100:
                    break
                page += 1
        logger.info(f"Found {len(all_groups)} groups matching query '{search_query}'")
        return all_groups