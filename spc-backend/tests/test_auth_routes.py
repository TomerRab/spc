import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.routes.auth_routes import router


# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestAuthRoutes:
    
    @patch('app.api.routes.auth_routes.settings')
    def test_get_oauth_login_url_success(self, mock_settings):
        """Test successful OAuth login URL generation."""
        mock_settings.gitlab_client_id = "test-client-id"
        mock_settings.gitlab_redirect_uri = "http://localhost:3000/callback"
        
        response = client.get("/auth/login", follow_redirects=False)
        
        assert response.status_code == 302
        location = response.headers["location"]
        assert "https://gitlab.com/oauth/authorize" in location
        assert "client_id=test-client-id" in location
        assert "redirect_uri=http://localhost:3000/callback" in location

    @patch('app.api.routes.auth_routes.settings')
    def test_get_oauth_login_url_missing_client_id(self, mock_settings):
        """Test OAuth login URL when client ID is missing."""
        mock_settings.gitlab_client_id = None
        
        response = client.get("/auth/login")
        
        assert response.status_code == 500
        data = response.json()
        assert "OAuth not configured" in data["detail"]

    @patch('app.api.routes.auth_routes.settings')
    def test_get_oauth_url_success(self, mock_settings):
        """Test successful OAuth URL retrieval."""
        mock_settings.gitlab_client_id = "test-client-id"
        mock_settings.gitlab_redirect_uri = "http://localhost:3000/callback"
        
        response = client.get("/auth/login-url")
        
        assert response.status_code == 200
        data = response.json()
        assert "login_url" in data
        assert "https://gitlab.com/oauth/authorize" in data["login_url"]

    @patch('app.api.routes.auth_routes.settings')
    def test_get_oauth_url_missing_client_id(self, mock_settings):
        """Test OAuth URL retrieval when client ID is missing."""
        mock_settings.gitlab_client_id = None
        
        response = client.get("/auth/login-url")
        
        assert response.status_code == 500
        data = response.json()
        assert "OAuth not configured" in data["detail"]

    @patch('app.api.routes.auth_routes.settings')
    @patch('httpx.AsyncClient')
    def test_handle_oauth_callback_success(self, mock_client_class, mock_settings):
        """Test successful OAuth callback handling."""
        # Mock settings
        mock_settings.gitlab_client_id = "test-client-id"
        mock_settings.gitlab_client_secret = "test-secret"
        mock_settings.gitlab_redirect_uri = "http://localhost:3000/callback"
        mock_settings.gitlab_token_url = "https://gitlab.com/oauth/token"
        mock_settings.frontend_url = "http://localhost:3000"
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test-access-token",
            "token_type": "Bearer",
            "expires_in": 7200
        }
        
        # Mock client
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        response = client.get("/auth/callback?code=test-auth-code", follow_redirects=False)
        
        assert response.status_code == 302
        location = response.headers["location"]
        assert "access_token=test-access-token" in location
        assert "success=true" in location

    @patch('app.api.routes.auth_routes.settings')
    def test_handle_oauth_callback_error(self, mock_settings):
        """Test OAuth callback with error parameter."""
        mock_settings.frontend_url = "http://localhost:3000"
        
        response = client.get("/auth/callback?error=access_denied", follow_redirects=False)
        
        assert response.status_code == 302
        location = response.headers["location"]
        assert "error=oauth_failed" in location
        assert "details=access_denied" in location

    @patch('app.api.routes.auth_routes.settings')
    def test_handle_oauth_callback_missing_code(self, mock_settings):
        """Test OAuth callback without authorization code."""
        mock_settings.frontend_url = "http://localhost:3000"
        
        response = client.get("/auth/callback", follow_redirects=False)
        
        assert response.status_code == 302
        location = response.headers["location"]
        assert "error=missing_authorization_code" in location

    @patch('app.api.routes.auth_routes.settings')
    def test_handle_oauth_callback_missing_credentials(self, mock_settings):
        """Test OAuth callback without client credentials."""
        mock_settings.gitlab_client_id = None
        mock_settings.gitlab_client_secret = None
        mock_settings.frontend_url = "http://localhost:3000"
        
        response = client.get("/auth/callback?code=test-code", follow_redirects=False)
        
        assert response.status_code == 302
        location = response.headers["location"]
        assert "error=oauth_not_configured" in location

    @patch('app.api.routes.auth_routes.settings')
    @patch('httpx.AsyncClient')
    def test_handle_oauth_callback_token_exchange_failure(self, mock_client_class, mock_settings):
        """Test OAuth callback when token exchange fails."""
        # Mock settings
        mock_settings.gitlab_client_id = "test-client-id"
        mock_settings.gitlab_client_secret = "test-secret"
        mock_settings.gitlab_redirect_uri = "http://localhost:3000/callback"
        mock_settings.gitlab_token_url = "https://gitlab.com/oauth/token"
        mock_settings.frontend_url = "http://localhost:3000"
        
        # Mock failed HTTP response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid grant"
        
        # Mock client
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        response = client.get("/auth/callback?code=invalid-code", follow_redirects=False)
        
        assert response.status_code == 302
        location = response.headers["location"]
        assert "error=token_exchange_failed" in location
        assert "status=400" in location

    @patch('app.api.routes.auth_routes.settings')
    @patch('httpx.AsyncClient')
    def test_handle_oauth_callback_missing_access_token(self, mock_client_class, mock_settings):
        """Test OAuth callback when access token is missing from response."""
        # Mock settings
        mock_settings.gitlab_client_id = "test-client-id"
        mock_settings.gitlab_client_secret = "test-secret"
        mock_settings.gitlab_redirect_uri = "http://localhost:3000/callback"
        mock_settings.gitlab_token_url = "https://gitlab.com/oauth/token"
        mock_settings.frontend_url = "http://localhost:3000"
        
        # Mock HTTP response without access token
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token_type": "Bearer"}  # Missing access_token
        
        # Mock client
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        response = client.get("/auth/callback?code=test-code", follow_redirects=False)
        
        assert response.status_code == 302
        location = response.headers["location"]
        assert "error=invalid_token_response" in location