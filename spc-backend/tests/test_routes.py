import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.routes import router


# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestRoutes:
    
    def test_health_check(self):
        """Test health check endpoint."""
        with patch('app.api.routes.settings') as mock_settings:
            mock_settings.gitlab_url = "https://gitlab.example.com"
            mock_settings.gitlab_client_id = "test-client-id"
            mock_settings.gitlab_client_secret = "test-secret"
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["gitlab_url"] == "https://gitlab.example.com"
            assert data["oauth_configured"] is True

    def test_health_check_oauth_not_configured(self):
        """Test health check when OAuth is not configured."""
        with patch('app.api.routes.settings') as mock_settings:
            mock_settings.gitlab_url = "https://gitlab.example.com"
            mock_settings.gitlab_client_id = None
            mock_settings.gitlab_client_secret = None
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["oauth_configured"] is False

    def test_legacy_login_redirect(self):
        """Test legacy login endpoint redirect."""
        response = client.get("/login", follow_redirects=False)
        
        assert response.status_code == 301
        assert response.headers["location"] == "/auth/login"

    def test_legacy_login_url_redirect(self):
        """Test legacy login-url endpoint redirect."""
        response = client.get("/login-url", follow_redirects=False)
        
        assert response.status_code == 301
        assert response.headers["location"] == "/auth/login-url"

    def test_legacy_callback_redirect(self):
        """Test legacy callback endpoint redirect."""
        response = client.get("/callback", follow_redirects=False)
        
        assert response.status_code == 301
        assert response.headers["location"] == "/auth/callback"

    def test_legacy_groups_redirect(self):
        """Test legacy groups endpoint redirect."""
        response = client.get("/groups", follow_redirects=False)
        
        assert response.status_code == 301
        assert response.headers["location"] == "/groups"

    def test_legacy_groups_search_redirect(self):
        """Test legacy groups search endpoint redirect."""
        response = client.get("/groups/search", follow_redirects=False)
        
        assert response.status_code == 301
        assert response.headers["location"] == "/groups/search"

    def test_legacy_generate_repo_redirect(self):
        """Test legacy generate-repo endpoint redirect."""
        response = client.post("/generate-repo", follow_redirects=False)
        
        assert response.status_code == 301
        assert response.headers["location"] == "/projects/generate-repo"