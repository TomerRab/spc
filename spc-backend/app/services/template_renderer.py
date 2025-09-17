import logging
from pathlib import Path
from typing import Dict

from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader

from app.services.stack_config_manager import StackConfigManager

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Handles Jinja2 template processing and rendering."""
    
    def __init__(self, templates_dir: Path = None):
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent.parent / "templates"
        
        self.templates_dir = templates_dir
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
        )

    async def process_template(self, template_path: str, variables: Dict) -> str:
        """Process a template with variable substitution."""
        try:
            template = self.jinja_env.get_template(template_path)
            return template.render(**variables)
        except Exception as e:
            logger.error(f"Template not found: {template_path} (Error: {str(e)})")
            return self._handle_template_error(template_path, variables, e)

    async def get_static_template(self, template_path: str) -> str:
        """Get a static template without variable substitution."""
        try:
            template = self.jinja_env.get_template(template_path)
            return template.render()
        except Exception as e:
            logger.error(f"Static template not found: {template_path} (Error: {str(e)})")
            return self._handle_static_template_error(template_path, e)

    def _handle_template_error(self, template_path: str, variables: Dict, error: Exception) -> str:
        """Handle template processing errors with fallbacks and user-friendly messages."""
        # Try fallback template first
        fallback_path = self._get_fallback_template(template_path)
        if fallback_path:
            try:
                logger.info(f"Trying fallback template: {fallback_path}")
                template = self.jinja_env.get_template(fallback_path)
                return template.render(**variables)
            except Exception as fallback_error:
                logger.error(f"Fallback template also failed: {fallback_path} (Error: {str(fallback_error)})")
        
        # Raise user-friendly error based on template type
        if "/helm/templates/" in template_path:
            raise HTTPException(500, f"Missing deployment template files. This appears to be a system configuration issue. Please contact support.")
        elif ".gitlab-ci.yml" in template_path:
            stack_info = f" for {variables.get('stack', 'the selected technology stack')}" if variables.get('stack') else ""
            raise HTTPException(400, f"CI/CD pipeline template not found{stack_info}. This technology stack may not be supported yet. Please try a different stack or contact support.")
        elif any(ext in template_path for ext in ['.Dockerfile', '.gitignore', '.npmrc', 'settings.xml']):
            stack_info = f" for {variables.get('stack', 'the selected technology stack')}" if variables.get('stack') else ""
            raise HTTPException(400, f"Configuration template not found{stack_info}. This technology stack may not be fully supported. Please try a different stack.")
        else:
            raise HTTPException(500, f"Required template files are missing. Please contact support. (Template: {template_path})")

    def _handle_static_template_error(self, template_path: str, error: Exception) -> str:
        """Handle static template errors with fallbacks and user-friendly messages."""
        # Try fallback template first
        fallback_path = self._get_fallback_template(template_path)
        if fallback_path:
            try:
                logger.info(f"Trying fallback static template: {fallback_path}")
                template = self.jinja_env.get_template(fallback_path)
                return template.render()
            except Exception as fallback_error:
                logger.error(f"Fallback static template also failed: {fallback_path} (Error: {str(fallback_error)})")
        
        # Raise user-friendly error based on template type
        if "/helm/templates/" in template_path:
            raise HTTPException(500, f"Missing deployment template files. This appears to be a system configuration issue. Please contact support.")
        elif any(ext in template_path for ext in ['.Dockerfile', '.gitignore', '.npmrc', 'settings.xml', '.helmignore']):
            raise HTTPException(500, f"Missing configuration files. This appears to be a system configuration issue. Please contact support.")
        else:
            raise HTTPException(500, f"Required template files are missing. Please contact support. (Template: {template_path})")
    
    def _get_fallback_template(self, template_path: str) -> str:
        """Get fallback template path for common stack mappings."""
        stack_manager = StackConfigManager()
        return stack_manager.get_fallback_template(template_path)