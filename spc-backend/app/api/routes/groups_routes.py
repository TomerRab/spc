import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.cache import groups_cache
from app.services.gitlab_service import GitLabService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/groups", tags=["groups"])
bearer_scheme = HTTPBearer()


def get_access_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    return credentials.credentials


@router.get("")
async def get_user_groups(
    token: str = Depends(get_access_token),
) -> Dict[str, List[Dict]]:
    """Get list of GitLab groups/namespaces for the authenticated user."""
    logger.info("Fetching user groups from GitLab")
    gitlab_service = GitLabService()
    groups = await gitlab_service.get_user_groups(token)
    logger.info(f"Retrieved {len(groups)} groups")
    return {"groups": groups}


@router.get("/search")
async def search_user_groups(
    q: str,
    token: str = Depends(get_access_token),
) -> Dict[str, List[Dict]]:
    """Search GitLab groups with a minimum 3-character query."""
    # Validate minimum query length
    if len(q.strip()) < 3:
        raise HTTPException(
            status_code=400, 
            detail="Search query must be at least 3 characters long"
        )
    
    query = q.strip()
    logger.info(f"Searching groups with query: '{query}'")
    
    # Check cache first
    cached_result = groups_cache.get(token, query)
    if cached_result is not None:
        return cached_result
    
    # Fetch from GitLab API
    gitlab_service = GitLabService()
    groups = await gitlab_service.search_user_groups(token, query)
    
    result = {"groups": groups}
    
    # Cache the result
    groups_cache.set(token, query, result)
    
    logger.info(f"Retrieved {len(groups)} groups for query '{query}'")
    return result