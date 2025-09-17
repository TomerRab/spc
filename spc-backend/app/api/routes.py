import logging
from typing import Dict

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.api.routes.auth_routes import router as auth_router
from app.api.routes.groups_routes import router as groups_router
from app.api.routes.projects_routes import router as projects_router

logger = logging.getLogger(__name__)
router = APIRouter()

# Include all route modules
router.include_router(auth_router)
router.include_router(groups_router)
router.include_router(projects_router)


@router.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint to verify service status and configuration."""
    return {
        "status": "healthy",
        "gitlab_url": settings.gitlab_url,
        "oauth_configured": bool(settings.gitlab_client_id and settings.gitlab_client_secret)
    }


# Legacy endpoints for backward compatibility
@router.get("/login")
def legacy_login_redirect():
    """Legacy endpoint - redirect to new auth endpoint."""
    return RedirectResponse(url="/auth/login", status_code=301)


@router.get("/login-url") 
def legacy_login_url():
    """Legacy endpoint - redirect to new auth endpoint."""
    return RedirectResponse(url="/auth/login-url", status_code=301)


@router.get("/callback")
def legacy_callback():
    """Legacy endpoint - redirect to new auth endpoint."""
    return RedirectResponse(url="/auth/callback", status_code=301)


@router.get("/groups")
def legacy_groups():
    """Legacy endpoint - redirect to new groups endpoint."""
    return RedirectResponse(url="/groups", status_code=301)


@router.get("/groups/search")
def legacy_groups_search():
    """Legacy endpoint - redirect to new groups endpoint."""
    return RedirectResponse(url="/groups/search", status_code=301)


@router.post("/generate-repo")
def legacy_generate_repo():
    """Legacy endpoint - redirect to new projects endpoint."""
    return RedirectResponse(url="/projects/generate-repo", status_code=301)