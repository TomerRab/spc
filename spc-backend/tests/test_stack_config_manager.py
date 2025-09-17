import pytest
from app.services.stack_config_manager import StackConfigManager


class TestStackConfigManager:
    
    def setup_method(self):
        self.manager = StackConfigManager()

    def test_get_config_file_valid_stack(self):
        """Test getting config file for valid stacks."""
        assert self.manager.get_config_file("maven") == "settings.xml"
        assert self.manager.get_config_file("spring") == "settings.xml"
        assert self.manager.get_config_file("node") == ".npmrc"
        assert self.manager.get_config_file("react") == ".npmrc"
        assert self.manager.get_config_file("python") == "pip.ini"
        assert self.manager.get_config_file("dotnet") == "nuget.config"

    def test_get_config_file_invalid_stack(self):
        """Test getting config file for invalid stack returns None."""
        assert self.manager.get_config_file("invalid") is None
        assert self.manager.get_config_file("") is None
        assert self.manager.get_config_file(None) is None

    def test_get_fallback_template_valid_fallbacks(self):
        """Test fallback template paths for stacks with fallbacks."""
        assert self.manager.get_fallback_template("microservice/spring.gitlab-ci.yml") == "microservice/maven.gitlab-ci.yml"
        assert self.manager.get_fallback_template("library/react.gitlab-ci.yml") == "library/node.gitlab-ci.yml"
        assert self.manager.get_fallback_template("common/typescript.gitignore") == "common/node.gitignore"
        assert self.manager.get_fallback_template("microservice/csharp.gitlab-ci.yml") == "microservice/dotnet.gitlab-ci.yml"

    def test_get_fallback_template_no_fallback(self):
        """Test fallback template for stacks without fallbacks returns None."""
        assert self.manager.get_fallback_template("microservice/maven.gitlab-ci.yml") is None
        assert self.manager.get_fallback_template("library/python.gitlab-ci.yml") is None
        assert self.manager.get_fallback_template("invalid/path") is None

    def test_requires_docker_valid_combinations(self):
        """Test Docker requirements for different project type and stack combinations."""
        assert self.manager.requires_docker("microservice", "python") is True
        assert self.manager.requires_docker("monorepo", "node") is True
        assert self.manager.requires_docker("library", "java") is False  # libraries don't need Docker
        assert self.manager.requires_docker("microservice", "") is False  # no stack
        assert self.manager.requires_docker("microservice", None) is False  # no stack

    def test_requires_helm_valid_project_types(self):
        """Test Helm requirements for different project types."""
        assert self.manager.requires_helm("monorepo") is True
        assert self.manager.requires_helm("delivery") is True
        assert self.manager.requires_helm("microservice") is False
        assert self.manager.requires_helm("library") is False
        assert self.manager.requires_helm("") is False
        assert self.manager.requires_helm("invalid") is False