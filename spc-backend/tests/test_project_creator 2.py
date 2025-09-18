import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from app.services.project_creator import ProjectCreator
from app.schemas.repo_models import RepoRequest


class TestProjectCreator:
    
    def setup_method(self):
        with patch('app.services.project_creator.settings'):
            self.creator = ProjectCreator()

    @pytest.mark.asyncio
    @patch.object(ProjectCreator, '_handle_microservice_creation')
    async def test_create_project_microservice(self, mock_handle_microservice):
        """Test project creation for microservice type."""
        mock_handle_microservice.return_value = {"status": "success"}
        
        # Create a mock RepoRequest
        repo_request = Mock(spec=RepoRequest)
        repo_request.project_type = "microservice"
        repo_request.validate_requirements.return_value = None
        
        result = await self.creator.create_project("test-token", repo_request)
        
        assert result == {"status": "success"}
        mock_handle_microservice.assert_called_once_with("test-token", repo_request)

    @pytest.mark.asyncio
    async def test_create_project_standalone_microservice(self):
        """Test project creation for standalone microservice type."""
        self.creator.microservice_creator.create_standalone = AsyncMock(return_value={"status": "success"})
        
        repo_request = Mock(spec=RepoRequest)
        repo_request.project_type = "standalone-microservice"
        repo_request.validate_requirements.return_value = None
        
        result = await self.creator.create_project("test-token", repo_request)
        
        assert result == {"status": "success"}
        self.creator.microservice_creator.create_standalone.assert_called_once_with("test-token", repo_request)

    @pytest.mark.asyncio
    async def test_create_project_library(self):
        """Test project creation for library type."""
        self.creator.single_creator.create = AsyncMock(return_value={"status": "success"})
        
        repo_request = Mock(spec=RepoRequest)
        repo_request.project_type = "library"
        repo_request.validate_requirements.return_value = None
        
        result = await self.creator.create_project("test-token", repo_request)
        
        assert result == {"status": "success"}
        self.creator.single_creator.create.assert_called_once_with("test-token", repo_request)

    @pytest.mark.asyncio
    async def test_create_project_validation_error(self):
        """Test project creation with validation error."""
        repo_request = Mock(spec=RepoRequest)
        repo_request.validate_requirements.side_effect = ValueError("Invalid project configuration")
        
        with pytest.raises(HTTPException) as exc_info:
            await self.creator.create_project("test-token", repo_request)
        
        assert exc_info.value.status_code == 400
        assert "Invalid project configuration" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch.object(ProjectCreator, '_handle_unexpected_error')
    async def test_create_project_unexpected_error(self, mock_handle_error):
        """Test project creation with unexpected error."""
        mock_handle_error.side_effect = HTTPException(500, "Unexpected error")
        
        self.creator.single_creator.create = AsyncMock(side_effect=Exception("Database error"))
        
        repo_request = Mock(spec=RepoRequest)
        repo_request.project_type = "library"
        repo_request.validate_requirements.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await self.creator.create_project("test-token", repo_request)
        
        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_handle_microservice_creation_with_delivery(self):
        """Test microservice creation with delivery configuration."""
        self.creator.microservice_creator.create_with_delivery = AsyncMock(return_value={"status": "success"})
        
        repo_request = Mock(spec=RepoRequest)
        repo_request.deliveryConfig = {"createDelivery": True}
        
        result = await self.creator._handle_microservice_creation("test-token", repo_request)
        
        assert result == {"status": "success"}
        self.creator.microservice_creator.create_with_delivery.assert_called_once_with("test-token", repo_request)

    @pytest.mark.asyncio
    async def test_handle_microservice_creation_without_delivery(self):
        """Test microservice creation without delivery configuration."""
        self.creator.single_creator.create = AsyncMock(return_value={"status": "success"})
        
        repo_request = Mock(spec=RepoRequest)
        repo_request.deliveryConfig = {"createDelivery": False}
        
        result = await self.creator._handle_microservice_creation("test-token", repo_request)
        
        assert result == {"status": "success"}
        self.creator.single_creator.create.assert_called_once_with("test-token", repo_request)

    @pytest.mark.asyncio
    async def test_handle_microservice_creation_no_delivery_config(self):
        """Test microservice creation with no delivery configuration."""
        self.creator.single_creator.create = AsyncMock(return_value={"status": "success"})
        
        repo_request = Mock(spec=RepoRequest)
        repo_request.deliveryConfig = None
        
        result = await self.creator._handle_microservice_creation("test-token", repo_request)
        
        assert result == {"status": "success"}
        self.creator.single_creator.create.assert_called_once_with("test-token", repo_request)

    def test_handle_unexpected_error_template_not_found(self):
        """Test unexpected error handling for template not found."""
        repo_request = Mock(spec=RepoRequest)
        repo_request.stack = "python"
        repo_request.project_type = "microservice"
        
        error = Exception("Template not found for python")
        
        with pytest.raises(HTTPException) as exc_info:
            self.creator._handle_unexpected_error(error, repo_request)
        
        assert exc_info.value.status_code == 400
        assert "not supported for microservice projects" in str(exc_info.value.detail)

    def test_handle_unexpected_error_permission_denied(self):
        """Test unexpected error handling for permission denied."""
        repo_request = Mock(spec=RepoRequest)
        
        error = Exception("Permission denied")
        
        with pytest.raises(HTTPException) as exc_info:
            self.creator._handle_unexpected_error(error, repo_request)
        
        assert exc_info.value.status_code == 403
        assert "don't have permission" in str(exc_info.value.detail)

    def test_handle_unexpected_error_generic(self):
        """Test unexpected error handling for generic errors."""
        repo_request = Mock(spec=RepoRequest)
        
        error = Exception("Database connection failed")
        
        with pytest.raises(HTTPException) as exc_info:
            self.creator._handle_unexpected_error(error, repo_request)
        
        assert exc_info.value.status_code == 500
        assert "unexpected error occurred" in str(exc_info.value.detail)