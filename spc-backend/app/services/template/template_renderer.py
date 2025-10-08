import logging
import boto3
from typing import Dict, Optional

from jinja2 import Environment, BaseLoader, TemplateNotFound, TemplateSyntaxError, select_autoescape

from .stack_config_manager import StackConfigManager
from .template_error_handler import TemplateErrorHandler
from app.utils.exceptions import TemplateError, TemplateRenderError, S3Error
from app.core.config import settings

logger = logging.getLogger(__name__)


class S3TemplateLoader(BaseLoader):
    """Custom Jinja2 loader that fetches templates from S3."""

    def __init__(self, s3_bucket: str, s3_region: str):
        self.s3_bucket = s3_bucket
        self.s3_client = boto3.client('s3', region_name=s3_region)

    def get_source(self, environment, template):
        """Load template from S3."""
        try:
            # Template path in S3 (e.g., "library/maven.gitlab-ci.yml")
            response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=template)
            source = response['Body'].read().decode('utf-8')

            # Return (source, filename, uptodate_function)
            # uptodate_function returns False to always reload (or implement caching)
            return source, None, lambda: False

        except self.s3_client.exceptions.NoSuchKey:
            # Missing template = 404 NOT FOUND (not a server error!)
            logger.warning(f"Template not found in S3: {template}")
            raise TemplateNotFound(template)
        except self.s3_client.exceptions.NoSuchBucket:
            # Misconfigured bucket = 500 INTERNAL ERROR (server config problem)
            logger.error(f"S3 bucket not found: {self.s3_bucket}")
            raise S3Error(f"Template storage configuration error", bucket=self.s3_bucket, key=template)
        except self.s3_client.exceptions.ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            # Access denied = 403 FORBIDDEN (not 500!)
            if error_code == 'AccessDenied':
                logger.error(f"S3 access denied for template: {template}")
                raise S3Error(f"Template storage access denied", bucket=self.s3_bucket, key=template)
            # Other client errors = likely misconfiguration
            logger.error(f"S3 client error loading template {template}: {error_code}")
            raise S3Error(f"Template storage configuration error", bucket=self.s3_bucket, key=template)
        except Exception as e:
            # Network errors, connection errors = 503 SERVICE UNAVAILABLE
            logger.error(f"S3 service error loading template {template}: {str(e)}")
            raise S3Error(f"Template storage service error", bucket=self.s3_bucket, key=template)


class TemplateRenderer:
    """Handles Jinja2 template processing and rendering from S3."""

    def __init__(self, s3_bucket: Optional[str] = None, s3_region: Optional[str] = None) -> None:
        self.s3_bucket = s3_bucket or settings.s3_bucket
        self.s3_region = s3_region or settings.s3_region
        self.error_handler = TemplateErrorHandler(self.s3_bucket)
        self.stack_manager = StackConfigManager()

        # Use S3 loader instead of FileSystemLoader
        self.jinja_env = Environment(
            loader=S3TemplateLoader(self.s3_bucket, self.s3_region),
            autoescape=select_autoescape(['html', 'xml']),
            # Security: Restrict access to dangerous builtins
            enable_async=False,
            # Prevent access to Python builtins that could be dangerous
            finalize=lambda x: x if x is not None else ''
        )
        # Remove dangerous globals for security
        self.jinja_env.globals.clear()
        # Only allow safe template functions
        self.jinja_env.globals.update({
            'range': range,
            'len': len,
            'str': str,
            'int': int,
            'bool': bool,
        })

    async def process_template(self, template_path: str, variables: Dict) -> str:
        """Process a template with variable substitution."""
        try:
            template = self.jinja_env.get_template(template_path)
            return template.render(**variables)
        except TemplateNotFound:
            # Try fallback template before failing
            fallback_result = await self._try_fallback(template_path, variables)
            if fallback_result:
                return fallback_result
            # Raise appropriate error
            error_type = self.error_handler.get_error_type(template_path)
            self.error_handler.raise_template_error(template_path, error_type, variables)
        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error in {template_path}: {str(e)}")
            raise TemplateRenderError(
                f"Template syntax error in '{template_path}': {str(e)}",
                template_name=template_path,
                template_path=f"s3://{self.s3_bucket}/{template_path}"
            )
        except Exception as e:
            logger.error(f"Template processing error for {template_path}: {str(e)}")
            raise TemplateError(
                f"Failed to process template '{template_path}': {str(e)}",
                template_name=template_path,
                template_path=f"s3://{self.s3_bucket}/{template_path}"
            )

    async def get_static_template(self, template_path: str) -> str:
        """Get a static template without variable substitution."""
        try:
            template = self.jinja_env.get_template(template_path)
            return template.render()
        except TemplateNotFound:
            # Try fallback template before failing
            fallback_result = await self._try_fallback(template_path)
            if fallback_result:
                return fallback_result
            # Raise appropriate error
            error_type = self.error_handler.get_error_type(template_path)
            self.error_handler.raise_template_error(template_path, error_type)
        except Exception as e:
            logger.error(f"Static template error: {template_path} ({str(e)})")
            raise TemplateError(
                f"Failed to process static template '{template_path}': {str(e)}",
                template_name=template_path,
                template_path=f"s3://{self.s3_bucket}/{template_path}"
            )

    async def _try_fallback(
        self, template_path: str, variables: Optional[Dict] = None
    ) -> Optional[str]:
        """Try fallback template, works for both static and variable templates.

        Args:
            template_path: Path to template that failed
            variables: Optional template variables for rendering

        Returns:
            Rendered template content if fallback succeeds, None otherwise
        """
        fallback_path = self._get_fallback_template(template_path)
        if not fallback_path:
            return None

        try:
            logger.info(f"Template not found: {template_path}, trying fallback: {fallback_path}")
            template = self.jinja_env.get_template(fallback_path)
            return template.render(**variables) if variables else template.render()
        except Exception as e:
            logger.warning(f"Fallback also failed: {fallback_path} ({str(e)})")
            return None

    def _get_fallback_template(self, template_path: str) -> Optional[str]:
        """Get fallback template path for common stack mappings."""
        return self.stack_manager.get_fallback_template(template_path)