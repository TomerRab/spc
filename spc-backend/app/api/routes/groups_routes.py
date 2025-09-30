import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.cache import groups_cache
from app.services.gitlab import GitLabService
from app.schemas.response_models import create_groups_response
from app.utils.input_sanitizer import InputSanitizer

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
) -> Dict:
    """Get list of GitLab groups/namespaces for the authenticated user."""
    logger.info("Fetching user groups from GitLab")
    gitlab_service = GitLabService()
    groups = await gitlab_service.get_user_groups(token)
    logger.info(f"Retrieved {len(groups)} groups")
    return create_groups_response(
        message=f"Successfully retrieved {len(groups)} groups",
        groups=groups
    )


@router.get("/search")
async def search_user_groups(q: str, token: str = Depends(get_access_token)) -> Dict:
    """Search GitLab groups with a minimum 3-character query."""
    logger.info(f"Groups search endpoint called with query parameter: '{q}'")
    query = _validate_and_prepare_query(q)
    logger.info(f"Validated query: '{query}', checking cache...")
    
    cached_result = _get_cached_result(token, query)
    if cached_result is not None:
        logger.info(f"Returning cached result with {len(cached_result.get('groups', []))} groups")
        return cached_result
    
    logger.info(f"No cached result found, fetching from GitLab API...")
    result = await _fetch_and_cache_groups(token, query)
    logger.info(f"Retrieved {len(result.get('groups', []))} groups for query '{query}'")
    return result

def _validate_and_prepare_query(q: str) -> str:
    """Validate and prepare the search query."""
    if len(q.strip()) < 3:
        raise HTTPException(status_code=400, detail="Search query must be at least 3 characters long")
    
    # Sanitize the query for security
    try:
        InputSanitizer._check_for_dangerous_patterns(q)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid search query: {str(e)}")
    
    query = q.strip()
    # Additional validation - limit query length and ensure safe characters
    if len(query) > 100:
        raise HTTPException(status_code=400, detail="Search query must be 100 characters or less")
    
    # Allow only alphanumeric, spaces, hyphens, and underscores for group search
    import re
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', query):
        raise HTTPException(status_code=400, detail="Search query contains invalid characters")
    
    logger.info(f"Searching groups with query: '{query}'")
    return query

def _get_cached_result(token: str, query: str) -> Dict:
    """Get cached result if available."""
    return groups_cache.get(token, query)

async def _fetch_and_cache_groups(token: str, query: str) -> Dict:
    """Fetch groups from GitLab API and cache the result."""
    gitlab_service = GitLabService()
    groups = await gitlab_service.search_user_groups(token, query)
    result = create_groups_response(
        message=f"Found {len(groups)} groups matching '{query}'",
        groups=groups
    )
    groups_cache.set(token, query, result)
    return result