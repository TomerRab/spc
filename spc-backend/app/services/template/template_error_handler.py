import logging
from typing import Dict, Optional

from app.utils.exceptions import TemplateNotFoundError

logger = logging.getLogger(__name__)


class TemplateErrorHandler:
    """Handles template-related errors with user-friendly messages."""

    ERROR_MESSAGES = {
        "ci": "CI/CD pipeline template not found",
        "config": "Configuration template not found",
        "helm": "Deployment templates not available",
        "general": "Template not available"
    }

    def __init__(self, s3_bucket: str):
        self.s3_bucket = s3_bucket

    def raise_template_error(
        self,
        template_path: str,
        error_type: str = "general",
        variables: Optional[Dict] = None
    ) -> None:
        """Raise a template error with appropriate message based on type.

        Args:
            template_path: Path to the template that failed
            error_type: Type of error (ci, config, helm, general)
            variables: Optional template variables for context
        """
        base_message = self.ERROR_MESSAGES.get(error_type, self.ERROR_MESSAGES["general"])
        stack_info = self._get_stack_info(variables)

        raise TemplateNotFoundError(
            f"{base_message}{stack_info}",
            template_name=template_path,
            template_path=f"s3://{self.s3_bucket}/{template_path}"
        )

    def _get_stack_info(self, variables: Optional[Dict]) -> str:
        """Get stack information for error message."""
        if variables and variables.get('stack'):
            return f" for {variables.get('stack')}"
        return ""

    def get_error_type(self, template_path: str) -> str:
        """Determine error type based on template path.

        Args:
            template_path: Path to the template

        Returns:
            Error type string (ci, config, helm, or general)
        """
        if "/helm/templates/" in template_path:
            return "helm"
        elif ".gitlab-ci.yml" in template_path:
            return "ci"
        elif any(ext in template_path for ext in [
            '.Dockerfile', '.gitignore', '.npmrc', 'settings.xml',
            '.helmignore', 'nuget.config', 'pip.ini'
        ]):
            return "config"
        return "general"
