import logging
from typing import Dict

from fastapi import APIRouter

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


