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

