import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx

from app.services.gitlab_variables_service import GitLabVariablesService


class TestGitLabVariablesService:
    
    def setup_method(self):
        with patch('app.services.gitlab_variables_service.settings') as mock_settings:
            mock_settings.gitlab_url = "https://gitlab.example.com/api/v4"
            self.service = GitLabVariablesService()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_set_project_variables_success(self, mock_client_class):
        """Test successful project variables setting."""
        mock_response = Mock()
        mock_response.status_code = 201
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        variables = {
            "VAR1": "value1",
            "VAR2": "value2"
        }
        
        await self.service.set_project_variables("test-token", 123, variables)
        
        # Verify two API calls were made
        assert mock_client.post.call_count == 2
        
        # Check first call
        first_call = mock_client.post.call_args_list[0]
        assert first_call[0][0] == "https://gitlab.example.com/api/v4/projects/123/variables"
        assert first_call[1]['json']['key'] == "VAR1"
        assert first_call[1]['json']['value'] == "value1"
        assert first_call[1]['json']['protected'] is False
        assert first_call[1]['json']['masked'] is False

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_set_project_variables_already_exists(self, mock_client_class):
        """Test project variables setting when variable already exists."""
        mock_response = Mock()
        mock_response.status_code = 400  # Variable already exists
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        variables = {"EXISTING_VAR": "value"}
        
        # Should not raise exception for 400 status
        await self.service.set_project_variables("test-token", 123, variables)

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_set_environment_variables_success(self, mock_client_class):
        """Test successful environment variables setting."""
        mock_response_create = Mock()
        mock_response_create.status_code = 201
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response_create
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        variables = {
            "ENV_VAR1": "env_value1",
            "ENV_VAR2": "env_value2"
        }
        
        await self.service.set_environment_variables("test-token", 123, "production", variables)
        
        # Verify two API calls were made
        assert mock_client.post.call_count == 2
        
        # Check environment scope is set correctly
        for call in mock_client.post.call_args_list:
            payload = call[1]['json']
            assert payload['environment_scope'] == "production"
            assert payload['protected'] is False
            assert payload['masked'] is False

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    @patch.object(GitLabVariablesService, '_update_environment_variable')
    async def test_set_environment_variables_update_existing(self, mock_update, mock_client_class):
        """Test environment variables setting when variable exists and needs update."""
        mock_response_create = Mock()
        mock_response_create.status_code = 400  # Variable exists
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response_create
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_update.return_value = None
        
        variables = {"EXISTING_ENV_VAR": "new_value"}
        
        await self.service.set_environment_variables("test-token", 123, "staging", variables)
        
        # Verify update was called
        mock_update.assert_called_once_with("test-token", 123, "EXISTING_ENV_VAR", "new_value", "staging")

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_update_environment_variable_success(self, mock_client_class):
        """Test successful environment variable update."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client = AsyncMock()
        mock_client.put.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        await self.service._update_environment_variable("test-token", 123, "VAR_NAME", "new_value", "production")
        
        # Verify API call
        mock_client.put.assert_called_once_with(
            "https://gitlab.example.com/api/v4/projects/123/variables/VAR_NAME",
            headers={"Authorization": "Bearer test-token", "Content-Type": "application/json"},
            json={
                "value": "new_value",
                "protected": False,
                "masked": False,
                "environment_scope": "production"
            }
        )

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_update_environment_variable_failure(self, mock_client_class):
        """Test environment variable update failure."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Variable not found"
        
        mock_client = AsyncMock()
        mock_client.put.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Should not raise exception, just log error
        await self.service._update_environment_variable("test-token", 123, "NONEXISTENT_VAR", "value", "production")

    def test_get_headers(self):
        """Test header generation."""
        headers = self.service._get_headers("test-token")
        expected = {
            "Authorization": "Bearer test-token",
            "Content-Type": "application/json"
        }
        assert headers == expected