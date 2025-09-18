import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from fastapi import HTTPException

from app.services.template_renderer import TemplateRenderer


class TestTemplateRenderer:
    
    def setup_method(self):
        self.mock_templates_dir = Path("/mock/templates")
        self.renderer = TemplateRenderer(self.mock_templates_dir)

    @patch('app.services.template_renderer.FileSystemLoader')
    @patch('app.services.template_renderer.Environment')
    def test_init_with_custom_templates_dir(self, mock_env, mock_loader):
        """Test initialization with custom templates directory."""
        custom_dir = Path("/custom/templates")
        renderer = TemplateRenderer(custom_dir)
        
        mock_loader.assert_called_with(str(custom_dir))
        mock_env.assert_called_with(loader=mock_loader.return_value)

    @patch('app.services.template_renderer.FileSystemLoader')
    @patch('app.services.template_renderer.Environment')
    def test_init_with_default_templates_dir(self, mock_env, mock_loader):
        """Test initialization with default templates directory."""
        renderer = TemplateRenderer()
        
        mock_loader.assert_called_once()
        mock_env.assert_called_with(loader=mock_loader.return_value)

    @pytest.mark.asyncio
    async def test_process_template_success(self):
        """Test successful template processing."""
        mock_template = Mock()
        mock_template.render.return_value = "rendered content"
        self.renderer.jinja_env.get_template = Mock(return_value=mock_template)
        
        variables = {"repo_name": "test-repo", "stack": "python"}
        result = await self.renderer.process_template("test/template.j2", variables)
        
        assert result == "rendered content"
        self.renderer.jinja_env.get_template.assert_called_once_with("test/template.j2")
        mock_template.render.assert_called_once_with(**variables)

    @pytest.mark.asyncio
    async def test_get_static_template_success(self):
        """Test successful static template retrieval."""
        mock_template = Mock()
        mock_template.render.return_value = "static content"
        self.renderer.jinja_env.get_template = Mock(return_value=mock_template)
        
        result = await self.renderer.get_static_template("static/template.txt")
        
        assert result == "static content"
        self.renderer.jinja_env.get_template.assert_called_once_with("static/template.txt")
        mock_template.render.assert_called_once_with()

    @pytest.mark.asyncio
    @patch.object(TemplateRenderer, '_get_fallback_template', return_value=None)
    async def test_process_template_ci_error(self, mock_fallback):
        """Test template processing error for CI templates."""
        self.renderer.jinja_env.get_template = Mock(side_effect=Exception("Template not found"))
        
        with pytest.raises(HTTPException) as exc_info:
            await self.renderer.process_template("microservice/python.gitlab-ci.yml", {"stack": "python"})
        
        assert exc_info.value.status_code == 400
        assert "CI/CD pipeline template not found for python" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch.object(TemplateRenderer, '_get_fallback_template', return_value=None)
    async def test_process_template_helm_error(self, mock_fallback):
        """Test template processing error for Helm templates."""
        self.renderer.jinja_env.get_template = Mock(side_effect=Exception("Template not found"))
        
        with pytest.raises(HTTPException) as exc_info:
            await self.renderer.process_template("delivery/helm/templates/deployment.yaml", {})
        
        assert exc_info.value.status_code == 500
        assert "Missing deployment template files" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch.object(TemplateRenderer, '_get_fallback_template', return_value="fallback/template.j2")
    async def test_process_template_fallback_success(self, mock_fallback):
        """Test successful fallback template processing."""
        mock_template = Mock()
        mock_template.render.return_value = "fallback content"
        
        # First call fails, second (fallback) succeeds
        self.renderer.jinja_env.get_template = Mock(side_effect=[
            Exception("Original template not found"),
            mock_template
        ])
        
        result = await self.renderer.process_template("original/template.j2", {"test": "value"})
        
        assert result == "fallback content"
        assert self.renderer.jinja_env.get_template.call_count == 2
        mock_template.render.assert_called_once_with(test="value")

    @pytest.mark.asyncio
    @patch.object(TemplateRenderer, '_get_fallback_template', return_value="fallback/template.txt")
    async def test_get_static_template_fallback_success(self, mock_fallback):
        """Test successful fallback static template retrieval."""
        mock_template = Mock()
        mock_template.render.return_value = "fallback static content"
        
        # First call fails, second (fallback) succeeds
        self.renderer.jinja_env.get_template = Mock(side_effect=[
            Exception("Original template not found"),
            mock_template
        ])
        
        result = await self.renderer.get_static_template("original/template.txt")
        
        assert result == "fallback static content"
        assert self.renderer.jinja_env.get_template.call_count == 2
        mock_template.render.assert_called_once_with()

    @patch('app.services.template_renderer.StackConfigManager')
    def test_get_fallback_template(self, mock_stack_manager_class):
        """Test fallback template retrieval."""
        mock_manager = Mock()
        mock_manager.get_fallback_template.return_value = "fallback/path"
        mock_stack_manager_class.return_value = mock_manager
        
        result = self.renderer._get_fallback_template("original/path")
        
        assert result == "fallback/path"
        mock_manager.get_fallback_template.assert_called_once_with("original/path")