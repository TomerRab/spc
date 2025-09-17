import logging
from typing import Dict

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login", response_class=RedirectResponse)
def get_oauth_login_url() -> RedirectResponse:
    """Redirect to GitLab OAuth authorization page."""
    if not settings.gitlab_client_id:
        raise HTTPException(
            status_code=500, 
            detail="GitLab OAuth not configured - missing client_id"
        )
        
    oauth_url = _build_oauth_url()
    logger.info("Redirecting to GitLab OAuth")
    return RedirectResponse(url=oauth_url, status_code=302)


@router.get("/login-url")
def get_oauth_url() -> Dict[str, str]:
    """Get GitLab OAuth authorization URL without redirect."""
    if not settings.gitlab_client_id:
        raise HTTPException(
            status_code=500, 
            detail="GitLab OAuth not configured - missing client_id"
        )
        
    oauth_url = _build_oauth_url()
    return {"login_url": oauth_url}


@router.get("/callback")
async def handle_oauth_callback(request: Request) -> RedirectResponse:
    """Handle GitLab OAuth callback and exchange code for access token."""
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    
    logger.info(f"OAuth callback received - code: {'present' if code else 'missing'}, error: {error}")
    
    # Check for OAuth errors first
    if error:
        logger.error(f"OAuth authorization failed: {error}")
        return RedirectResponse(
            url=f"{settings.frontend_url}/?error=oauth_failed&details={error}",
            status_code=302
        )
    
    # Validate authorization code
    if not code:
        logger.error("Authorization code missing from callback")
        return RedirectResponse(
            url=f"{settings.frontend_url}/?error=missing_authorization_code",
            status_code=302
        )
    
    # Validate OAuth configuration
    if not settings.gitlab_client_id or not settings.gitlab_client_secret:
        logger.error("GitLab OAuth credentials not configured")
        return RedirectResponse(
            url=f"{settings.frontend_url}/?error=oauth_not_configured",
            status_code=302
        )

    try:
        logger.info("Exchanging authorization code for access token")
        
        # Exchange code for token
        token_payload = {
            "client_id": settings.gitlab_client_id,
            "client_secret": settings.gitlab_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.gitlab_redirect_uri,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.gitlab_token_url,
                data=token_payload,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
            )

        logger.info(f"Token exchange response: {response.status_code}")
        
        if response.status_code != 200:
            error_text = response.text
            logger.error(f"Token exchange failed: {response.status_code} - {error_text}")
            return RedirectResponse(
                url=f"{settings.frontend_url}/?error=token_exchange_failed&status={response.status_code}",
                status_code=302
            )

        token_data = response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            logger.error("No access token in response")
            return RedirectResponse(
                url=f"{settings.frontend_url}/?error=invalid_token_response",
                status_code=302
            )
        
        logger.info("Successfully obtained GitLab access token")
        
        # Redirect to frontend with token
        frontend_url = (
            f"{settings.frontend_url}/"
            f"?success=true"
            f"&access_token={access_token}"
            f"&token_type={token_data.get('token_type', 'Bearer')}"
            f"&expires_in={token_data.get('expires_in', 7200)}"
        )
        
        return RedirectResponse(url=frontend_url, status_code=302)

    except httpx.RequestError as e:
        logger.error(f"Network error during token exchange: {e}")
        return RedirectResponse(
            url=f"{settings.frontend_url}/?error=network_error",
            status_code=302
        )
    except Exception as e:
        logger.error(f"Unexpected error during token exchange: {e}")
        return RedirectResponse(
            url=f"{settings.frontend_url}/?error=unexpected_error",
            status_code=302
        )


def _build_oauth_url() -> str:
    """Build GitLab OAuth authorization URL."""
    return (
        "https://gitlab.com/oauth/authorize"
        f"?client_id={settings.gitlab_client_id}"
        f"&redirect_uri={settings.gitlab_redirect_uri}"
        f"&response_type=code"
        f"&scope=api read_user read_repository write_repository"
    )