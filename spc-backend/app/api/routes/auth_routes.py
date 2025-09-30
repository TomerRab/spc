import logging
from typing import Dict

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.utils.constants import GITLAB_CONSTANTS

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])


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
    
    validation_error = _validate_oauth_callback(code, error)
    if validation_error:
        return validation_error
    
    try:
        access_token = await _exchange_code_for_token(code)
        return _build_success_redirect(access_token)
    except httpx.RequestError as e:
        return _handle_network_error(e)
    except Exception as e:
        return _handle_unexpected_error(e)

def _validate_oauth_callback(code: str, error: str) -> RedirectResponse:
    """Validate OAuth callback parameters and configuration."""
    if error:
        return _handle_oauth_error(error)
    if not code:
        return _handle_missing_code()
    if not _is_oauth_configured():
        return _handle_oauth_not_configured()
    return None

def _handle_oauth_error(error: str) -> RedirectResponse:
    """Handle OAuth authorization errors."""
    logger.error(f"OAuth authorization failed: {error}")
    return RedirectResponse(
        url=f"{settings.frontend_url}/?error=oauth_failed&details={error}",
        status_code=302
    )

def _handle_missing_code() -> RedirectResponse:
    """Handle missing authorization code."""
    logger.error("Authorization code missing from callback")
    return RedirectResponse(
        url=f"{settings.frontend_url}/?error=missing_authorization_code",
        status_code=302
    )

def _is_oauth_configured() -> bool:
    """Check if OAuth credentials are properly configured."""
    return bool(settings.gitlab_client_id and settings.gitlab_client_secret)

def _handle_oauth_not_configured() -> RedirectResponse:
    """Handle missing OAuth configuration."""
    logger.error("GitLab OAuth credentials not configured")
    return RedirectResponse(
        url=f"{settings.frontend_url}/?error=oauth_not_configured",
        status_code=302
    )

async def _exchange_code_for_token(code: str) -> dict:
    """Exchange authorization code for access token."""
    logger.info("Exchanging authorization code for access token")
    token_payload = _build_token_payload(code)
    response = await _send_token_request(token_payload)
    return _process_token_response(response)

def _build_token_payload(code: str) -> dict:
    """Build the token exchange payload."""
    return {
        "client_id": settings.gitlab_client_id,
        "client_secret": settings.gitlab_client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.gitlab_redirect_uri,
    }

async def _send_token_request(token_payload: dict) -> httpx.Response:
    """Send token exchange request to GitLab."""
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
    return response

def _process_token_response(response: httpx.Response) -> dict:
    """Process and validate token exchange response."""
    if response.status_code != 200:
        _handle_token_exchange_failure(response)
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    
    if not access_token:
        _handle_invalid_token_response()
    
    logger.info("Successfully obtained GitLab access token")
    return token_data

def _handle_token_exchange_failure(response: httpx.Response) -> None:
    """Handle token exchange failure."""
    error_text = response.text
    logger.error(f"Token exchange failed: {response.status_code} - {error_text}")
    raise ValueError(f"Token exchange failed: {response.status_code}")

def _handle_invalid_token_response() -> None:
    """Handle invalid token response."""
    logger.error("No access token in response")
    raise ValueError("Invalid token response")

def _build_success_redirect(token_data: dict) -> RedirectResponse:
    """Build success redirect URL with token data."""
    # SECURITY: Use URL fragment instead of query parameters to prevent token leakage
    # Fragments are not sent to servers, not logged in browser history
    access_token = token_data.get("access_token")
    frontend_url = (
        f"{settings.frontend_url}/"
        f"#success=true"
        f"&access_token={access_token}"
        f"&token_type={token_data.get('token_type', 'Bearer')}"
        f"&expires_in={token_data.get('expires_in', 7200)}"
    )
    return RedirectResponse(url=frontend_url, status_code=302)

def _handle_network_error(e: httpx.RequestError) -> RedirectResponse:
    """Handle network errors during token exchange."""
    logger.error(f"Network error during token exchange: {e}")
    return RedirectResponse(
        url=f"{settings.frontend_url}/?error=network_error",
        status_code=302
    )

def _handle_unexpected_error(e: Exception) -> RedirectResponse:
    """Handle unexpected errors during token exchange."""
    logger.error(f"Unexpected error during token exchange: {e}")
    return RedirectResponse(
        url=f"{settings.frontend_url}/?error=unexpected_error",
        status_code=302
    )


def _build_oauth_url() -> str:
    """Build GitLab OAuth authorization URL."""
    return (
        GITLAB_CONSTANTS['OAUTH_AUTHORIZE_URL'] +
        f"?client_id={settings.gitlab_client_id}" +
        f"&redirect_uri={settings.gitlab_redirect_uri}" +
        f"&response_type=code" +
        f"&scope={GITLAB_CONSTANTS['DEFAULT_SCOPES']}"
    )