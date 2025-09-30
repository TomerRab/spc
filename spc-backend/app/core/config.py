from typing import Optional, List
from pydantic_settings import BaseSettings

from app.utils.constants import GITLAB_CONSTANTS, ENVIRONMENT_NAMES


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    
    # Core service configuration (constants that never change)
    gitlab_url: str = GITLAB_CONSTANTS['BASE_URL']
    gitlab_token_url: str = GITLAB_CONSTANTS['OAUTH_TOKEN_URL']
    
    # Server configuration (from env)
    host: str
    port: int
    log_level: str
    
    # Frontend and OAuth configuration (from env)
    frontend_url: str
    gitlab_client_id: str
    gitlab_client_secret: str
    gitlab_redirect_uri: str
    cors_origins: str
    
    # Storage configuration (from env)
    s3_bucket: str
    s3_region: str
    s3_endpoint_url: Optional[str] = None
    aws_access_key_id: str
    aws_secret_access_key: str
    
    # OpenShift configuration (optional, defaults to empty)
    openshift_production_a_token: str = ""
    openshift_production_a_server: str = ""
    openshift_production_b_token: str = ""
    openshift_production_b_server: str = ""
    openshift_test_c_token: str = ""
    openshift_test_c_server: str = ""
    openshift_test_d_token: str = ""
    openshift_test_d_server: str = ""

    # HTTP timeout configuration (in seconds)
    http_timeout_default: float = 30.0
    http_timeout_gitlab: float = 45.0
    http_timeout_s3: float = 60.0

    # Default branch configuration
    default_branch: str = "main"
    commit_message: str = "Initial project setup"

    # Cache configuration (in seconds)
    cache_ttl_groups: int = 900      # 15 minutes
    cache_ttl_projects: int = 300    # 5 minutes
    cache_ttl_templates: int = 3600  # 1 hour
    cache_max_size_groups: int = 500
    cache_max_size_projects: int = 100
    cache_max_size_templates: int = 50

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"


# Environment configuration mapping
ENVIRONMENT_CONFIG = {
    env_id: {
        "name": name,
        "environment": env_id
    }
    for env_id, name in ENVIRONMENT_NAMES.items()
}

settings = Settings()
