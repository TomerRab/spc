import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx
from fastapi import HTTPException

from app.services.gitlab_groups_service import GitLabGroupsService


class TestGitLabGroupsService:
    
    def setup_method(self):
        self.service = GitLabGroupsService("https://gitlab.example.com/api/v4")

    def test_init(self):
        """Test service initialization."""
        assert self.service.base_url == "https://gitlab.example.com/api/v4"
        assert self.service.timeout == 30.0

    def test_get_headers(self):
        """Test header generation."""
        headers = self.service._get_headers("test-token")
        expected = {
            "Authorization": "Bearer test-token",
            "Content-Type": "application/json"
        }
        assert headers == expected

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_get_user_groups_success(self, mock_client_class):
        """Test successful user groups retrieval."""
        # Mock response data
        mock_groups_data = [
            {"id": 1, "name": "Group 1", "full_path": "group1", "visibility": "private"},
            {"id": 2, "name": "Group 2", "full_path": "group2", "visibility": "public"}
        ]
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_groups_data
        
        # Mock client
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await self.service.get_user_groups("test-token")
        
        expected = [
            {"id": 1, "name": "Group 1", "full_path": "group1", "visibility": "private"},
            {"id": 2, "name": "Group 2", "full_path": "group2", "visibility": "public"}
        ]
        assert result == expected
        
        # Verify API call
        mock_client.get.assert_called_once_with(
            "https://gitlab.example.com/api/v4/groups",
            headers={"Authorization": "Bearer test-token", "Content-Type": "application/json"},
            params={"page": 1, "per_page": 100}
        )

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_get_user_groups_pagination(self, mock_client_class):
        """Test user groups retrieval with pagination."""
        # Mock responses for pagination
        page1_data = [{"id": i, "name": f"Group {i}", "full_path": f"group{i}", "visibility": "private"} for i in range(1, 101)]  # 100 items
        page2_data = [{"id": 101, "name": "Group 101", "full_path": "group101", "visibility": "private"}]  # 1 item
        
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = page1_data
        
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = page2_data
        
        # Mock client to return different responses for different calls
        mock_client = AsyncMock()
        mock_client.get.side_effect = [mock_response1, mock_response2]
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await self.service.get_user_groups("test-token")
        
        assert len(result) == 101
        assert result[0]["id"] == 1
        assert result[100]["id"] == 101
        
        # Verify both API calls
        assert mock_client.get.call_count == 2

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_get_user_groups_401_error(self, mock_client_class):
        """Test 401 error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(HTTPException) as exc_info:
            await self.service.get_user_groups("invalid-token")
        
        assert exc_info.value.status_code == 401
        assert "expired or is invalid" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_get_user_groups_403_error(self, mock_client_class):
        """Test 403 error handling."""
        mock_response = Mock()
        mock_response.status_code = 403
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(HTTPException) as exc_info:
            await self.service.get_user_groups("test-token")
        
        assert exc_info.value.status_code == 403
        assert "don't have permission" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_get_user_groups_network_error(self, mock_client_class):
        """Test network error handling."""
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.RequestError("Connection failed")
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(HTTPException) as exc_info:
            await self.service.get_user_groups("test-token")
        
        assert exc_info.value.status_code == 503
        assert "Cannot connect to GitLab" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_search_user_groups_success(self, mock_client_class):
        """Test successful group search."""
        mock_groups_data = [
            {"id": 1, "name": "Search Result", "full_path": "search-result", "visibility": "private"}
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_groups_data
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await self.service.search_user_groups("test-token", "search")
        
        expected = [
            {"id": 1, "name": "Search Result", "full_path": "search-result", "visibility": "private"}
        ]
        assert result == expected
        
        # Verify search API call
        mock_client.get.assert_called_once_with(
            "https://gitlab.example.com/api/v4/groups",
            headers={"Authorization": "Bearer test-token", "Content-Type": "application/json"},
            params={"page": 1, "per_page": 100, "search": "search"}
        )

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_search_user_groups_empty_result(self, mock_client_class):
        """Test search with empty results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await self.service.search_user_groups("test-token", "nonexistent")
        
        assert result == []