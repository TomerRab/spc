import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx
from fastapi import HTTPException

from app.services.gitlab_repository_service import GitLabRepositoryService


class TestGitLabRepositoryService:
    
    def setup_method(self):
        with patch('app.services.gitlab_repository_service.settings') as mock_settings:
            mock_settings.gitlab_url = "https://gitlab.example.com/api/v4"
            self.service = GitLabRepositoryService()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_create_repository_success(self, mock_client_class):
        """Test successful repository creation."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "http_url_to_repo": "https://gitlab.example.com/group/repo.git",
            "id": 123
        }
        
        # Mock client
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        repo_data = {
            "name": "test-repo",
            "group_id": "456"
        }
        
        url, repo_id = await self.service.create_repository("test-token", repo_data)
        
        assert url == "https://gitlab.example.com/group/repo.git"
        assert repo_id == 123
        
        # Verify API call
        expected_payload = {
            "name": "test-repo",
            "namespace_id": 456,
            "visibility": "private",
            "initialize_with_readme": False
        }
        mock_client.post.assert_called_once_with(
            "https://gitlab.example.com/api/v4/projects",
            headers={"Authorization": "Bearer test-token", "Content-Type": "application/json"},
            json=expected_payload
        )

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_create_repository_name_taken(self, mock_client_class):
        """Test repository creation with name already taken."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Name has already been taken"
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        repo_data = {"name": "existing-repo", "group_id": "456"}
        
        with pytest.raises(HTTPException) as exc_info:
            await self.service.create_repository("test-token", repo_data)
        
        assert exc_info.value.status_code == 400
        assert "already exists in this group" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_create_repository_invalid_name(self, mock_client_class):
        """Test repository creation with invalid name."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Name is invalid"
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        repo_data = {"name": "invalid@repo", "group_id": "456"}
        
        with pytest.raises(HTTPException) as exc_info:
            await self.service.create_repository("test-token", repo_data)
        
        assert exc_info.value.status_code == 400
        assert "contains invalid characters" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_create_repository_permission_denied(self, mock_client_class):
        """Test repository creation with insufficient permissions."""
        mock_response = Mock()
        mock_response.status_code = 403
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        repo_data = {"name": "test-repo", "group_id": "456"}
        
        with pytest.raises(HTTPException) as exc_info:
            await self.service.create_repository("test-token", repo_data)
        
        assert exc_info.value.status_code == 403
        assert "don't have permission to create repositories" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_add_files_success(self, mock_client_class):
        """Test successful file addition to repository."""
        mock_response = Mock()
        mock_response.status_code = 201
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        files = {
            "README.md": "# Test Repository",
            "src/main.py": "print('Hello World')"
        }
        
        await self.service.add_files("test-token", 123, files)
        
        # Verify API call structure
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://gitlab.example.com/api/v4/projects/123/repository/commits"
        
        payload = call_args[1]['json']
        assert payload['branch'] == 'main'
        assert payload['commit_message'] == 'Initial project setup'
        assert len(payload['actions']) == 2

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_add_files_permission_denied(self, mock_client_class):
        """Test file addition with permission denied."""
        mock_response = Mock()
        mock_response.status_code = 403
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        files = {"README.md": "# Test"}
        
        with pytest.raises(HTTPException) as exc_info:
            await self.service.add_files("test-token", 123, files)
        
        assert exc_info.value.status_code == 403
        assert "don't have permission to add files" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_delete_repository_success(self, mock_client_class):
        """Test successful repository deletion."""
        mock_response = Mock()
        mock_response.status_code = 202
        
        mock_client = AsyncMock()
        mock_client.delete.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        await self.service.delete_repository("test-token", 123)
        
        mock_client.delete.assert_called_once_with(
            "https://gitlab.example.com/api/v4/projects/123",
            headers={"Authorization": "Bearer test-token", "Content-Type": "application/json"}
        )

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_delete_repository_not_found(self, mock_client_class):
        """Test repository deletion when repository not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        
        mock_client = AsyncMock()
        mock_client.delete.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Should not raise exception for 404
        await self.service.delete_repository("test-token", 123)

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_delete_repository_network_error(self, mock_client_class):
        """Test repository deletion with network error."""
        mock_client = AsyncMock()
        mock_client.delete.side_effect = httpx.RequestError("Connection failed")
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(HTTPException) as exc_info:
            await self.service.delete_repository("test-token", 123)
        
        assert exc_info.value.status_code == 500
        assert "Network error during project deletion" in str(exc_info.value.detail)