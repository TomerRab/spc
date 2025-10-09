import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.services.variable_manager import VariableManager, ENVIRONMENT_CONFIG


class TestVariableManager:
    
    def setup_method(self):
        self.manager = VariableManager()

    def test_should_create_cluster_variables_true_cases(self):
        """Test cases where cluster variables should be created."""
        assert self.manager.should_create_cluster_variables("delivery", {"cluster1": {}}) is True
        assert self.manager.should_create_cluster_variables("standalone-microservice", {"cluster1": {}}) is True
        assert self.manager.should_create_cluster_variables("other", {"cluster1": {}}) is True

    def test_should_create_cluster_variables_false_cases(self):
        """Test cases where cluster variables should not be created."""
        assert self.manager.should_create_cluster_variables("delivery", {}) is False
        assert self.manager.should_create_cluster_variables("delivery", None) is False
        assert self.manager.should_create_cluster_variables("standalone-microservice", {}) is False

    def test_create_cluster_variables(self):
        """Test creating cluster variables."""
        clusters = {
            "dev": {"name": "dev-cluster", "url": "https://dev.example.com"},
            "prod": {"name": "prod-cluster", "url": "https://prod.example.com"}
        }
        
        result = self.manager.create_cluster_variables(clusters)
        
        expected = {
            "dev_cluster_name": "dev-cluster",
            "dev_cluster_url": "https://dev.example.com",
            "prod_cluster_name": "prod-cluster",
            "prod_cluster_url": "https://prod.example.com"
        }
        
        assert result == expected

    def test_create_cluster_variables_empty(self):
        """Test creating cluster variables with empty input."""
        result = self.manager.create_cluster_variables({})
        assert result == {}
        
        result = self.manager.create_cluster_variables(None)
        assert result == {}

    def test_create_deployment_variables(self):
        """Test creating deployment variables."""
        servers = {
            "a": {"namespace": "test-ns-a"},
            "b": {"namespace": "test-ns-b", "other": "value"}
        }
        
        result = self.manager.create_deployment_variables(servers)
        
        expected = {
            "OS_PROJECT_NAME_A": "test-ns-a",
            "OS_PROJECT_NAME_B": "test-ns-b"
        }
        
        assert result == expected

    def test_create_deployment_variables_no_namespace(self):
        """Test creating deployment variables when namespace is missing."""
        servers = {
            "a": {"other": "value"},  # no namespace
            "b": {"namespace": "test-ns-b"}
        }
        
        result = self.manager.create_deployment_variables(servers)
        
        expected = {
            "OS_PROJECT_NAME_B": "test-ns-b"
        }
        
        assert result == expected

    @pytest.mark.asyncio
    @patch('app.services.variable_manager.settings')
    async def test_set_environment_variables_success(self, mock_settings):
        """Test successful environment variable setting."""
        # Mock settings attributes
        mock_settings.os_env_a_token = "token-a"
        mock_settings.os_env_a_server = "server-a"
        mock_settings.os_env_b_token = "token-b"
        mock_settings.os_env_b_server = "server-b"
        
        # Mock GitLab service
        mock_gitlab_service = Mock()
        mock_gitlab_service.set_environment_variables = AsyncMock()
        
        servers = {
            "a": {"namespace": "test-ns-a"},
            "b": {"namespace": "test-ns-b"}
        }
        
        result = await self.manager.set_environment_variables(
            mock_gitlab_service, "token", 123, servers
        )
        
        # Verify the service was called correctly
        assert mock_gitlab_service.set_environment_variables.call_count == 2
        
        # Verify return value
        expected_variables = [
            "os_project_name (env: a)",
            "os_token (env: a)", 
            "os_server (env: a)",
            "os_project_name (env: b)",
            "os_token (env: b)",
            "os_server (env: b)"
        ]
        assert all(var in result for var in expected_variables)

    @pytest.mark.asyncio
    @patch('app.services.variable_manager.settings')
    async def test_set_environment_variables_missing_namespace(self, mock_settings):
        """Test environment variable setting with missing namespace."""
        # Mock settings attributes
        mock_settings.os_env_a_token = "token-a"
        mock_settings.os_env_a_server = "server-a"
        
        # Mock GitLab service
        mock_gitlab_service = Mock()
        mock_gitlab_service.set_environment_variables = AsyncMock()
        
        servers = {
            "a": {},  # no namespace
            "invalid": {"namespace": "test"}  # invalid environment ID
        }
        
        result = await self.manager.set_environment_variables(
            mock_gitlab_service, "token", 123, servers
        )
        
        # Service should not be called for missing namespace or invalid env
        mock_gitlab_service.set_environment_variables.assert_not_called()
        assert result == []

    @pytest.mark.asyncio
    @patch('app.services.variable_manager.settings')
    async def test_set_environment_variables_invalid_env_id(self, mock_settings):
        """Test environment variable setting with invalid environment ID."""
        mock_gitlab_service = Mock()
        mock_gitlab_service.set_environment_variables = AsyncMock()
        
        servers = {
            "invalid_env": {"namespace": "test-ns"}
        }
        
        result = await self.manager.set_environment_variables(
            mock_gitlab_service, "token", 123, servers
        )
        
        # Service should not be called for invalid environment ID
        mock_gitlab_service.set_environment_variables.assert_not_called()
        assert result == []

    def test_environment_config_constants(self):
        """Test that environment configuration constants are properly defined."""
        assert "a" in ENVIRONMENT_CONFIG
        assert "b" in ENVIRONMENT_CONFIG
        assert "c" in ENVIRONMENT_CONFIG
        assert "d" in ENVIRONMENT_CONFIG
        
        for env_id, config in ENVIRONMENT_CONFIG.items():
            assert "name" in config
            assert "environment" in config
            assert isinstance(config["name"], str)
            assert isinstance(config["environment"], str)