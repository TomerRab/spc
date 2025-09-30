"""Configuration validation for the SPC application."""
import logging
from typing import List

from app.utils.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates application configuration and environment variables."""
    
    REQUIRED_CONFIG_KEYS = [
        'gitlab_client_id',
        'gitlab_client_secret',
        's3_bucket',
        'aws_access_key_id', 
        'aws_secret_access_key'
    ]
    
    @staticmethod
    def validate_settings(settings) -> None:
        """Validate that all required configuration is present."""
        missing_configs = ConfigValidator._find_missing_configs(settings)
        ConfigValidator._raise_if_missing_configs(missing_configs)
        ConfigValidator._validate_specific_configs(settings)
    
    @staticmethod
    def _find_missing_configs(settings) -> List[str]:
        """Find all missing required configuration keys."""
        missing_configs = []
        for key in ConfigValidator.REQUIRED_CONFIG_KEYS:
            if ConfigValidator._is_config_missing(settings, key):
                missing_configs.append(key.upper())
        return missing_configs
    
    @staticmethod
    def _is_config_missing(settings, key: str) -> bool:
        """Check if a configuration key is missing or empty."""
        value = getattr(settings, key, None)
        return not value or (isinstance(value, str) and value.strip() == "")
    
    @staticmethod
    def _raise_if_missing_configs(missing_configs: List[str]) -> None:
        """Raise error if any required configs are missing."""
        if not missing_configs:
            return
        raise ConfigurationError(
            f"Missing required environment variables: {', '.join(missing_configs)}. "
            f"Please set these in your .env file or environment.",
            config_key=', '.join(missing_configs)
        )
    
    @staticmethod
    def _validate_specific_configs(settings) -> None:
        """Validate GitLab, S3, and CORS specific configurations."""
        ConfigValidator._validate_gitlab_config(settings)
        ConfigValidator._validate_s3_config(settings)
        ConfigValidator._validate_cors_config(settings)
    
    @staticmethod
    def _validate_gitlab_config(settings) -> None:
        """Validate GitLab-specific configuration."""
        ConfigValidator._validate_gitlab_url(settings.gitlab_url)
        ConfigValidator._validate_gitlab_redirect_uri(settings.gitlab_redirect_uri)
    
    @staticmethod
    def _validate_gitlab_url(gitlab_url: str) -> None:
        """Validate GitLab URL format."""
        if not gitlab_url.startswith(('http://', 'https://')):
            raise ConfigurationError(
                "GitLab URL must be a valid HTTP/HTTPS URL",
                config_key='GITLAB_URL'
            )
    
    @staticmethod
    def _validate_gitlab_redirect_uri(redirect_uri: str) -> None:
        """Validate GitLab redirect URI format."""
        if not redirect_uri.startswith(('http://', 'https://')):
            raise ConfigurationError(
                "GitLab redirect URI must be a valid HTTP/HTTPS URL",
                config_key='GITLAB_REDIRECT_URI'
            )
    
    @staticmethod 
    def _validate_s3_config(settings) -> None:
        """Validate S3-specific configuration."""
        if settings.s3_bucket == "your-bucket":
            raise ConfigurationError(
                "S3 bucket must be configured with a real bucket name",
                config_key='S3_BUCKET'
            )
    
    @staticmethod
    def _validate_cors_config(settings) -> None:
        """Validate CORS configuration for security."""
        cors_origins = settings.get_cors_origins()
        
        if not cors_origins:
            raise ConfigurationError(
                "CORS origins must be configured",
                config_key='CORS_ORIGINS'
            )
        
        # Validate each origin
        for origin in cors_origins:
            if not origin.startswith(('http://', 'https://')):
                raise ConfigurationError(
                    f"CORS origin '{origin}' must be a valid HTTP/HTTPS URL",
                    config_key='CORS_ORIGINS'
                )
            
            # Warn about wildcard origins in production
            if origin == "*":
                logger.warning("Wildcard (*) CORS origin detected - this is insecure for production")

    @staticmethod
    def get_warnings(settings) -> List[str]:
        """Get list of configuration warnings (non-critical issues)."""
        warnings = []
        ConfigValidator._add_openshift_warning(settings, warnings)
        ConfigValidator._add_log_level_warning(settings, warnings)
        ConfigValidator._add_cors_warnings(settings, warnings)
        return warnings
    
    @staticmethod
    def _add_openshift_warning(settings, warnings: List[str]) -> None:
        """Add OpenShift configuration warning if needed."""
        if not settings.openshift_production_a_token:
            warnings.append("OpenShift Production A token not configured - some features may not work")
    
    @staticmethod
    def _add_log_level_warning(settings, warnings: List[str]) -> None:
        """Add log level warning if invalid."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if settings.log_level not in valid_levels:
            warnings.append(f"Invalid log level '{settings.log_level}' - defaulting to INFO")
    
    @staticmethod
    def _add_cors_warnings(settings, warnings: List[str]) -> None:
        """Add CORS configuration warnings."""
        cors_origins = settings.get_cors_origins()
        
        # Warn about localhost origins in production
        for origin in cors_origins:
            if 'localhost' in origin or '127.0.0.1' in origin:
                warnings.append(f"Localhost CORS origin '{origin}' should not be used in production")
                
            # Warn about HTTP origins (should use HTTPS in production)
            if origin.startswith('http://') and not ('localhost' in origin or '127.0.0.1' in origin):
                warnings.append(f"HTTP CORS origin '{origin}' is insecure - use HTTPS in production")